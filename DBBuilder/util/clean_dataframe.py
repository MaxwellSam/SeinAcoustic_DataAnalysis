import pandas as pd

def remove_duplicated_values (df:pd.DataFrame, target_cols:list=["date"], keep="max"):
    df = df.groupby(target_cols).agg(keep).reset_index()
    return df