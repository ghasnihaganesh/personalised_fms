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

    df = pd.read_csv(uploaded_file)

    # -------- SAFE COLUMN CHECK -------- #
    required_cols = ["datetime", "amount", "type"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Missing required column: {col}")
            st.stop()

    # Convert datetime safely
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])

    # -------- SPLIT DATA -------- #
    income_df = df[df["type"] == "CREDIT"]
    expense_df = df[df["type"] == "DEBIT"]

    total_income = income_df["amount"].sum()
    total_expense = expense_df["amount"].sum()

    # Use absolute for expense math
    total_expense_abs = abs(total_expense)

    savings = total_income - total_expense_abs

    # -------- KPI CARDS -------- #
    c1, c2, c3 = st.columns(3)

    c1.metric("💵 Total Income", f"₹{total_income:,.0f}")
    c2.metric("💸 Total Expense", f"₹{total_expense_abs:,.0f}")
    c3.metric("💰 Net Savings", f"₹{savings:,.0f}")

    st.divider()

    # -------- MONTHLY SUMMARY -------- #
    expense_df["month"] = expense_df["datetime"].dt.to_period("M").astype(str)

    monthly = (
        expense_df.groupby("month")["amount"]
        .sum()
        .abs()
        .reset_index()
    )

    monthly.columns = ["month", "total_expense"]

    # -------- PREDICTION -------- #
    if len(monthly) >= 2:
        prediction = predict_next_month(monthly)
        st.metric("🔮 Predicted Next Month Expense", f"₹{prediction:,.0f}")

    st.divider()

    # -------- TREND CHART -------- #
    st.subheader("📈 Monthly Expense Trend")

    fig = px.line(
        monthly,
        x="month",
        y="total_expense",
        markers=True,
        title="Monthly Expense Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------- CATEGORY DONUT -------- #
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

    # -------- TOP MERCHANTS -------- #
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
            orientation="h",
            title="Top 5 Merchants"
        )

        st.plotly_chart(fig3, use_container_width=True)

    # -------- BUDGET PLAN -------- #
    st.subheader("📊 Budget Plan")

    budget_limit = total_income * 0.7

    if budget_limit > 0:
        progress = total_expense_abs / budget_limit

        # Clamp between 0 and 1
        progress = max(0.0, min(progress, 1.0))
    else:
        progress = 0.0

    st.progress(progress)
    st.write(f"Budget Limit (70% rule): ₹{budget_limit:,.0f}")

    if total_expense_abs > budget_limit:
        st.error("⚠ Budget exceeded!")
    else:
        st.success("✅ Within budget")

    st.divider()

    # -------- INSIGHTS -------- #
    st.subheader("💡 Insights")

    if "category" in df.columns and total_income > 0:
        top_cat = cat_sum.sort_values("amount", ascending=False).iloc[0]
        percent = (top_cat["amount"] / total_income) * 100

        if percent > 35:
            st.error(
                f"⚠ High spending on {top_cat['category']} ({percent:.1f}% of income)"
            )

    if savings < 0:
        st.warning("⚠ Expenses exceed income!")

    st.info("💡 Tip: Save at least 30% of income.")

    st.divider()

    # -------- DOWNLOAD -------- #
    st.download_button(
        "📥 Download Monthly Summary",
        data=monthly.to_csv(index=False),
        file_name="monthly_summary.csv"
    )

    st.divider()

    # -------- SMART SAVINGS -------- #
    st.subheader("💡 Smart Saving Ideas & Better Utilization")

    if savings < 0:
        st.error("⚠ You are overspending. Focus on essentials.")

    st.markdown("""
### ✅ Recommendations
- Track daily expenses  
- Follow 50-30-20 rule  
- Invest via SIP/Mutual Funds  
- Reduce subscriptions  
- Set savings goals  
- Build emergency fund  
- Compare prices before buying  
- Invest extra income  

### 📈 Better Utilization
- Diversify investments  
- Automate savings  
- Use reward programs  
- Avoid high-interest debt   
- Review goals quarterly  
""")

else:
    st.info("👆 Upload a CSV file to begin analysis.")


