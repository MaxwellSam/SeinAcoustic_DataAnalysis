import pandas as pd
from dateutil import tz

def setup_datetime (df:pd.DataFrame, columns:list=["date"], dtformat:str="%Y-%m-%d %H-%M", timezone:str="UTC"):
    """
    Setup datetime columns
    """
    for col in columns:
        if df[col].dtype == object and isinstance(df.iloc[0][col], str):
            df[col] = pd.to_datetime(df[col], format=dtformat)
        if df[col].dt.tz == None:
            df[col] = df[col].dt.tz_localize(timezone)
        if df[col].dt.tz != timezone:
            df[col] = df[col].dt.tz_convert(timezone)
    return df         