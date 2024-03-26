

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# import seaborn as sns
# import glob
import datetime
import os
import math

from Visu.radar_plot.radar_traces import get_traces_RadarWithSTDThresholds

default_input = "data/Data_SAM/Bougival/output/Bougival_DataSet_hourly_data_20210531-20231208.csv"
default_output = "data/Data_SAM/Bougival/output/"

def read_input_file (input=None):
    input = input if type(input)==str else default_input
    df = pd.read_csv(input)
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_radar_traces_per_vars (df:pd.DataFrame, target_cols:list, GRPper:str="%Y%U", MEANby:str="%H", roundEvery:str=None):
    if roundEvery :
        df["date"] = df["date"].dt.round(roundEvery)
    df["GRP"] = df["date"].dt.strftime(GRPper)
    df["TIME"] = df["date"].dt.strftime(MEANby)
    grp_unique = df["GRP"].unique()
    radar_collection = {
        "date_start":[],
        "date_stop":[],
        **{c:[] for c in target_cols}
    }
    for grp in grp_unique:
        df_grp = df[df["GRP"]==grp]
        df_stats = df_grp.groupby("TIME")[target_cols].agg(["mean", "std"])
        radar_collection["date_start"].append(df_grp["date"].min())
        radar_collection["date_stop"].append(df_grp["date"].max())
        for c in target_cols:
            theta_values = df_stats.index.values
            mean_values = df_stats[c]["mean"].values
            std_values = df_stats[c]["std"].values
            # if not True in pd.Series(mean_values).isna():
            #     radar_collection[c].append(pd.NA)
            # else:
            radar_traces = get_traces_RadarWithSTDThresholds(
                theta_values=theta_values,
                mean_values=mean_values, 
                std_values=std_values,
                varname=c,
                showlegend=False
            )
            radar_collection[c].append(radar_traces)
    return pd.DataFrame(radar_collection)

def plot_multiRadars (radar_collection:pd.DataFrame, descripteur:str, nbrOfcols:int=4, title:str=None):
    radar_collection = radar_collection.dropna()
    radar_collection["nbr_traces"] = radar_collection[descripteur].apply(lambda x: len(x))
    nbrOfRows=math.ceil(len(radar_collection)/nbrOfcols) 
    empty_subplots = (nbrOfcols*nbrOfRows)-len(radar_collection)
    subplot_titles = radar_collection.apply(lambda row: f"{row['date_start'].strftime('%Y-%m-%d')} to {row['date_stop'].strftime('%Y-%m-%d')}", axis=1).values.tolist()
    if empty_subplots > 0:
        subplot_titles += [""]*empty_subplots
    # subplot_titles = np.reshape(subplot_titles, (nbrOfRows, nbrOfcols)).tolist()
    fig = make_subplots(
        rows=nbrOfRows, 
        cols=nbrOfcols, 
        subplot_titles=subplot_titles,
        specs=[[{"type":"polar"}]*nbrOfcols]*nbrOfRows,
        # horizontal_spacing=0.3,
        # vertical_spacing=0.3
        )
    idx_traces_to_show = radar_collection[radar_collection["nbr_traces"] == radar_collection["nbr_traces"].max()].index.values[0]
    for trace in radar_collection[descripteur].iloc[idx_traces_to_show]:
        trace["showlegend"] = True
    r,c = (1, 1)
    for idx,row in radar_collection.iterrows():
        fig.add_traces(row[descripteur], rows=r, cols=c)
        c+=1
        if c > nbrOfcols:
            c=1
            r+=1
    fig.update_layout(
        autosize=False,
        width=700*nbrOfcols,
        height=700*nbrOfRows,
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=15)
            ),
        margin=dict(t=200)
        )
    return fig

# ==== MAIN ==== #

def main (input:str=None, output_folder:str=None, target_cols=None,
          forWeeks:bool=True, forMonths:bool=True, forYears:bool=True):
    df = read_input_file(input)
    time_interval = " to ".join([
        df["date"].min().strftime("%Y-%m-%d"),
        df["date"].max().strftime("%Y-%m-%d")
        ])
    output_folder = default_output if not output_folder else output_folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    target_cols = [c for c in df.columns if "acoustique" in c] if type(target_cols)!=list else target_cols

    if forWeeks:
        # 1) Per Week visualisation
        output = os.path.join(output_folder, "radar_perWeek")
        if not os.path.exists(output):
            os.makedirs(output)
        radar_collection = get_radar_traces_per_vars(df=df, target_cols=target_cols, GRPper="%Y%U")
        for c in target_cols:
            title=f"Radar charts par semaine - {time_interval} - {c}"
            fig = plot_multiRadars(radar_collection=radar_collection, descripteur=c, title=title)
            filename=f"{c} {time_interval}.html".replace(" ", "_").replace("/", "")
            fig.write_html(os.path.join(output, filename))
            # fig.show()
            del fig
        del radar_collection
    if forMonths:
        # 2) Per Month visualisation
        output = os.path.join(output_folder, "radar_permont")
        if not os.path.exists(output):
            os.makedirs(output)
        radar_collection = get_radar_traces_per_vars(df=df, target_cols=target_cols, GRPper="%Y%m")
        for c in target_cols:
            title=f"Radar charts par mois - {time_interval} - {c}"
            fig = plot_multiRadars(radar_collection=radar_collection, descripteur=c, title=title)
            filename=f"{c} {time_interval}.html".replace(" ", "_").replace("/", "")
            fig.write_html(os.path.join(output, filename))
            # fig.show()
            del fig
        del radar_collection
    if forYears:
        # 3) Per Year visualisation
        output = os.path.join(output_folder, "radar_peryear")
        if not os.path.exists(output):
            os.makedirs(output)
        radar_collection = get_radar_traces_per_vars(df=df, target_cols=target_cols, GRPper="%Y")
        for c in target_cols:
            title=f"Radar charts par an - {time_interval} - {c}"
            fig = plot_multiRadars(radar_collection=radar_collection, descripteur=c, title=title)
            filename=f"{c} {time_interval}.html".replace(" ", "_").replace("/", "")
            fig.write_html(os.path.join(output, filename))
            # fig.show()
            del fig
        del radar_collection

    



