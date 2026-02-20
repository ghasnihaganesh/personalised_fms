import streamlit as st
import pandas as pd
import plotly.express as px
from finance_analysis import predict_next_month

st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

st.title("💰 Personal Finance Management System")
st.write("Upload your bank transactions CSV for insights & predictions.")

# -------- FILE UPLOAD -------- #
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:

    # ---------------- LOAD DATA ---------------- #
    df = pd.read_csv(uploaded_file)

    required_cols = ["datetime", "amount", "type"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Missing required column: {col}")
            st.stop()

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])

    df["type"] = df["type"].str.upper()

    # ---------------- SPLIT DATA ---------------- #
    income_df = df[df["type"] == "CREDIT"]
    expense_df = df[df["type"] == "DEBIT"]

    total_income = income_df["amount"].sum()
    total_expense = expense_df["amount"].sum()
    total_expense_abs = abs(total_expense)
    savings = total_income - total_expense_abs

    # ---------------- KPI CARDS ---------------- #
    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Total Income", f"₹{total_income:,.0f}")
    c2.metric("💸 Total Expense", f"₹{total_expense_abs:,.0f}")
    c3.metric("💰 Net Savings", f"₹{savings:,.0f}")

    st.divider()

    # ---------------- MONTHLY SUMMARY ---------------- #
    expense_df["month"] = expense_df["datetime"].dt.to_period("M").astype(str)

    monthly = (
        expense_df.groupby("month")["amount"]
        .sum()
        .abs()
        .reset_index()
    )

    monthly.columns = ["month", "total_expense"]

    # ---------------- PREDICTION ---------------- #
    if len(monthly) >= 2:
        prediction = predict_next_month(monthly)
        st.metric("🔮 Predicted Next Month Expense", f"₹{prediction:,.0f}")

    st.divider()

    # ---------------- TREND CHART ---------------- #
    st.subheader("📈 Monthly Expense Trend")

    fig = px.line(
        monthly,
        x="month",
        y="total_expense",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- CATEGORY CHART ---------------- #
    if "category" in df.columns:
        st.subheader("🥧 Spending by Category")

        cat_sum = (
            expense_df.groupby("category")["amount"]
            .sum()
            .abs()
            .reset_index()
        )

        fig2 = px.pie(
            cat_sum,
            names="category",
            values="amount",
            hole=0.5
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- TOP MERCHANTS ---------------- #
    if "merchant" in df.columns:
        st.subheader("🏪 Top Merchants")

        merchants = (
            expense_df.groupby("merchant")["amount"]
            .sum()
            .abs()
            .nlargest(5)
            .reset_index()
        )

        fig3 = px.bar(
            merchants,
            x="amount",
            y="merchant",
            orientation="h"
        )

        st.plotly_chart(fig3, use_container_width=True)

    # =====================================================
    # SMART FINANCIAL INTELLIGENCE MODULE
    # =====================================================

    st.divider()
    st.subheader("🧠 Smart Financial Intelligence")

    if not expense_df.empty:

        expense_df["abs_amount"] = expense_df["amount"].abs()

        # 1️⃣ Recurring Detection
        recurring = (
            expense_df.groupby(["merchant", "abs_amount"])
            .size()
            .reset_index(name="count")
        )

        recurring = recurring[recurring["count"] >= 3]

        if not recurring.empty:
            st.subheader("🔁 Recurring Payment Alerts")
            for _, row in recurring.iterrows():
                st.warning(
                    f"Recurring payment detected: ₹{row['abs_amount']:,.0f} "
                    f"paid to {row['merchant']} ({row['count']} times)"
                )

        # 2️⃣ Spending Spike
        if len(monthly) >= 2:
            last = monthly.iloc[-1]["total_expense"]
            prev = monthly.iloc[-2]["total_expense"]

            if last > prev * 1.25:
                st.error("⚠ Sudden spending spike detected.")
            elif last < prev * 0.75:
                st.success("📉 Spending reduced compared to last month.")

        # 3️⃣ Financial Health Score
        if total_income > 0:
            ratio = savings / total_income

            if ratio >= 0.3:
                score = 90
                status = "Excellent"
            elif ratio >= 0.2:
                score = 75
                status = "Good"
            elif ratio >= 0.1:
                score = 50
                status = "Average"
            else:
                score = 30
                status = "Poor"

            st.metric("💎 Financial Health Score", f"{score}/100")
            st.write(f"Financial Status: **{status}**")

    # =====================================================
    # BUDGET PLAN
    # =====================================================

    st.divider()
    st.subheader("📊 Budget Plan")

    budget_limit = total_income * 0.7

    if budget_limit > 0:
        progress = total_expense_abs / budget_limit
        progress = max(0.0, min(progress, 1.0))
    else:
        progress = 0.0

    st.progress(progress)
    st.write(f"Budget Limit (70% rule): ₹{budget_limit:,.0f}")

    if total_expense_abs > budget_limit:
        st.error("⚠ Budget exceeded!")
    else:
        st.success("✅ Within budget")

    # =====================================================
    # INSIGHTS
    # =====================================================

    st.divider()
    st.subheader("💡 Insights")

    if savings < 0:
        st.error("🚨 Negative savings trend detected.")
    elif savings > total_income * 0.3:
        st.success("🎯 Strong savings performance!")

    st.info("💡 Tip: Save at least 30% of income.")

    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.divider()
    st.download_button(
        "📥 Download Monthly Summary",
        data=monthly.to_csv(index=False),
        file_name="monthly_summary.csv"
    )

else:
    st.info("👆 Upload a CSV file to begin analysis.")


