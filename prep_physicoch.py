
import glob
import pandas as pd
from functools import reduce

input_path = "./data/bougival/chimie continue"
output_path = "./data/bougival/database"


files = glob.glob(input_path+"/*.csv")

dfs = []

final_df = None
for file in files:
    df = pd.read_csv(file, sep=";", decimal=",")
    df["date"] = df["date"] + " " + df["hour"]
    df = df.drop(columns=["hour"])
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y %H:%M:%S")
    print(df)
    if type(final_df) == type(None):
        final_df = df.copy()
        pass
    else:
        final_df = pd.merge(final_df, df, on="date")
    print(final_df)

final_df["date"] = final_df["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
