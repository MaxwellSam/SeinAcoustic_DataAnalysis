import pandas as pd
import datetime
from tqdm import tqdm
import numpy as np
from utils.data_managment.suncycle import get_sunCycle
from utils.data_managment.meteo_infos import get_meteo

def add_suncycle (df:pd.DataFrame, lat:float=48.866, long:float=2.333, elev:float=35,
                             dtAroundTwilightZone:datetime.timedelta=datetime.timedelta(hours=1, minutes=30),
                             twilightZones=["dusk", "dawn"], tzinfo=None,
                             dtformat_input:str="%Y-%m-%d %H:%M:%S", dtformat_output:str="%Y-%m-%d %H:00:00",
                             col_date:str="date"):
    """
    """
    if type(df[col_date].values[0]) == str:
        df[col_date] = pd.to_datetime(df[col_date], format=dtformat_input)
    dates = df[col_date].values 
    df_suncycle_infos = get_sunCycle(dates=dates, lat=lat, long=long, elev=elev, dtAroundTwilightZone=dtAroundTwilightZone,
                                     twilightZones=twilightZones, tzinfo=tzinfo, dtformat=dtformat_output) 
    df[col_date]=pd.to_datetime(df[col_date], format=dtformat_output)
    df = df.merge(df_suncycle_infos, on=col_date)
    return df
    
def add_open_meteo (df, lat:float=48.866, long:float=2.333, dtformat_input:str="%Y-%m-%d %H:%M:%S", 
                    dtformat_output:str="%Y-%m-%d %H:%M:%S", col_date:str="date"):
    if type(df[col_date].values[0]) == str:
        df[col_date] = pd.to_datetime(df[col_date], format=dtformat_input)
    date_start = df[col_date].min() - datetime.timedelta(days=1)
    date_stop = df[col_date].max()
    date_start, date_stop = [datetime.datetime.strftime(date, format="%Y-%m-%d") for date in [date_start, date_stop]]
    df_meteo_hourly = get_meteo(lat=lat, long=long, date_start=date_start, date_stop=date_stop)
    df_meteo_hourly.date = df_meteo_hourly.date.dt.strftime("%Y-%m-%d %H:%M:%S")
    df["date_hourly"] = df.date.dt.strftime("%Y-%m-%d %H:00:00")
    df[col_date] = df[col_date].dt.strftime(dtformat_output)
    df_meteo_hourly = df_meteo_hourly.rename(columns={"date":"date_hourly"})
    df = df.merge(df_meteo_hourly, on="date_hourly")
    df = df.drop(["date_hourly"], axis=1)
    return df
    

    

def formating_hourly_counting (df:pd.DataFrame, dt_format_input:str="%Y-%m-%d %H:%M:%S", dt_format_output:str="%Y-%m-%d %H:00:00",
                               col_date:str="date", col_label:str="label"):
    df = df.copy()
    df = df[[col_date, col_label]] 
    df[col_date] = pd.to_datetime(df[col_date], format=dt_format_input).dt.strftime(date_format=dt_format_output)
    print(df)
    labels_unique = df[col_label].unique()
    dates_unique = df[col_date].unique()
    records = []
    print("Create hourly records ...")
    for date in tqdm(dates_unique):
        for label in labels_unique:
            record = {"date":date}
            count = len(df[(df[col_date]==date)&(df[col_label]==label)])
            record["count"] = count
            record["label"] = label
            records.append(record)
    df = pd.DataFrame.from_records(data=records)
    return df