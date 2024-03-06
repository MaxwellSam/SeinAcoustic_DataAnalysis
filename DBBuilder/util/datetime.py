import pandas as pd

def convert_all_dtcolumns_to_str (df:pd.DataFrame, format:str="%Y-%m-%d %H:%M:%S"):
    """
    Convert columns with datetimes to string format in dataframe
    """
    cols_to_conv = columns_with_datetime(df)
    for col in cols_to_conv:
        df[col] = df[col].dt.strftime(format)
    return df

def columns_with_datetime(df:pd.DataFrame):
    """
    Get columns with datetime in dataframe
    """
    return [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]