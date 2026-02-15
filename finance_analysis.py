import numpy as np
from sklearn.linear_model import LinearRegression

def predict_next_month(monthly_df):

    if len(monthly_df) < 2:
        return 0

    monthly_df = monthly_df.copy()
    monthly_df["month_index"] = np.arange(len(monthly_df))

    X = monthly_df[["month_index"]]
    y = monthly_df["total_expense"]

    model = LinearRegression()
    model.fit(X,y)

    next_index = [[monthly_df["month_index"].max()+1]]

    return round(model.predict(next_index)[0],2)

