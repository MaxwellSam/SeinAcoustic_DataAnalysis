# import os
# cwd = os.getcwd()
# new_cwd = os.path.join(cwd.rsplit("SeinAcoustic_DataAnalysis")[0], "SeinAcoustic_DataAnalysis") if not cwd.endswith("SeinAcoustic_DataAnalysis") else None
# if new_cwd != None:
#     os.chdir(new_cwd)

import pandas as pd
import numpy as np
import plotly.graph_objs as go
# import seaborn as sns
# import glob
import datetime

from Visu.radar_plot.radar_traces import get_traces_RadarWithSTDThresholds

dateformat = "%Y-%m-%d %H:%M:%S"

data = "data/Data_SAM/Bougival/output/Bougival_DataSet_hourly_data_20210531-20231208.csv"
df = pd.read_csv(data)

def weekly_analysis (df:pd.DataFrame, weekFreq:int=1, target_cols:list=None,
                     filter_uncompleteWeeks:bool=True, colname_date:str="date",
                     colname_day:str="suncycle_day"):
    # Week infos
    target_cols = df.select_dtypes(include="number").columns if not target_cols else target_cols
    df["date"] = pd.to_datetime(df["date"], format=dateformat)
    df[colname_day] = pd.to_datetime(df["suncycle_day"], format=dateformat)
    df["hour"] = df[colname_date].dt.strftime("%H")
    df["week_id"] = df["suncycle_day"].dt.strftime("%Y%U")
    df_week = df.groupby(["week_id"])["suncycle_day"].agg(["min", "max", "nunique"]).reset_index()
    df_week = df_week.sort_values(by="min")
    if filter_uncompleteWeeks:
        df_week = df_week[(df_week["nunique"] == 7)]
    dfs = []
    for i in range(0, len(df_week), weekFreq):
        df_week_interval = df_week.iloc[i:i+weekFreq+1]
        week_days = df_week_interval[["min", "max"]].values.flatten()
        day_min, day_max = week_days.min(), week_days.max()
        mask = (day_min<df[colname_day])&(df[colname_day]<day_max)
        stats_weeks = df[mask].groupby(["hour"])[target_cols].agg(["mean", "std"]).reset_index()
        timeint_name = f"{pd.to_datetime(day_min).strftime("%d/%m")}-{pd.to_datetime(day_max).strftime("%d/%m %Y")}"
        stats_weeks[["start", "end"]] = day_min, day_max
        stats_weeks["timeint"] = timeint_name
        dfs.append(stats_weeks)
    return pd.concat(dfs)
# th_colors = ['#ffeda0','#feb24c','#f03b20']

stat_weeks = weekly_analysis(df=df, weekFreq=2)

fig = go.Figure()

var = "0 (acoustique,sensea,nb)"
stats_var = stat_weeks[["hour", "timeint", var]].dropna()
week_intervals = stats_var["timeint"].unique()
stats_var_weeks = stats_var[stats_var["timeint"] == week_intervals[-3]]
hours = stats_var_weeks["hour"].values
means = stats_var_weeks[var]["mean"].values
stds = stats_var_weeks[var]["std"].values

traces = get_traces_RadarWithSTDThresholds(
    theta_values=hours, 
    mean_values=means, 
    std_values=stds,
    varname=var,
    showlegend=False
)

fig.add_traces(traces)
fig.show()

