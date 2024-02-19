import pandas as pd

def change_datetime_format (df, dt_format, new_dt_format, col_date:str="date"):
    df[col_date] = pd.to_datetime(df[col_date], format=dt_format)
    df[col_date] = df[col_date].dt.strftime(new_dt_format)
    return df

    