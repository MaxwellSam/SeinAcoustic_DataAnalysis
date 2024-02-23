import pandas as pd
import datetime
from tqdm import tqdm
import numpy as np
from dateutil import tz
# from utils.data_managment.suncycle import get_sunCycle
from utils.data_managment.astral_infos import get_astral_infos
from utils.data_managment.meteo_infos import get_meteo

# def add_suncycle (df:pd.DataFrame, lat:float=48.866, long:float=2.333, elev:float=35,
#                              dtAroundTwilightZone:datetime.timedelta=datetime.timedelta(hours=1, minutes=30),
#                              twilightZones=["dusk", "dawn"], tzinfo=None,
#                              dtformat_input:str="%Y-%m-%d %H:%M:%S", dtformat_output:str="%Y-%m-%d %H:00:00",
#                              col_date:str="date"):
#     """
#     """
#     if type(df[col_date].values[0]) == str:
#         df[col_date] = pd.to_datetime(df[col_date], format=dtformat_input)
#     dates = df[col_date].values 
#     df_suncycle_infos = get_sunCycle(dates=dates, lat=lat, long=long, elev=elev, dtAroundTwilightZone=dtAroundTwilightZone,
#                                      twilightZones=twilightZones, tzinfo=tzinfo, dtformat=dtformat_output) 
#     df[col_date]=pd.to_datetime(df[col_date], format=dtformat_output)
#     df = df.merge(df_suncycle_infos, on=col_date)
#     return df

def add_astral_infos (df:pd.DataFrame, lat:float=48.866, long:float=2.333, elev:float=35,
                   dtAroundTwilightZone:float=5400.0,
                   tzinfo=tz.gettz("Europe/Paris"), dtformat:str="%Y-%m-%d %H:%M:%S", col_date:str="date"):
    """
    """
    # df = df.copy()
    dates = df["date"]
    # if type(dates) == str:
    #     dates = pd.to_datetime(dates, format=dtformat)
    if type(dates[0]) == str:
        dates = pd.to_datetime(dates, format=dtformat)
    dates = dates.dt.tz_localize(tzinfo)
    df[col_date] = dates
    # get astral informations
    astral_infos = get_astral_infos(dates=dates, lat=lat, long=long, elev=elev, 
                                    dtAroundTwilightZone=dtAroundTwilightZone, 
                                    tzinfo=tzinfo, dtformat=dtformat)
    if col_date != "date":
        astral_infos = astral_infos.rename(columns={"date", col_date})
    df = df.merge(astral_infos, on=col_date)
    return df

def find_suncycle_type (astral_infos:pd.DataFrame, dtAroundTwilightZone:datetime.timedelta=datetime.timedelta(hours=1, minutes=30)):
    dist_tw_types = [dtw for dtw in astral_infos.columns if  dtw.startswith("dist_tw_")]
    for dtw in dist_tw_types:
        tw = dtw.replace("dist_tw_", "")
        astral_infos.loc[abs(astral_infos[dtw]) <= dtAroundTwilightZone, "suncycle"] = tw
    maskDaylight = astral_infos["suncycle"].isna() # condition 1 => outside twilight zones
    maskDaylight = maskDaylight&(astral_infos["dist_tw_rising"].dt.total_seconds() > 0) # condition 2 => after twilight rising
    maskDaylight = maskDaylight&(astral_infos["dist_tw_setting"].dt.total_seconds() < 0) # condition 3 => before twilight setting
    astral_infos.loc[maskDaylight, "suncycle"] = "daylight"
    astral_infos.loc[astral_infos["suncycle"].isna(), "suncycle"] = "night"

    

    
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

def formating_labels_detection (df:pd.DataFrame, dtformat:str="%Y-%m-%d %H:%M:%S", countBy="h",
                                col_date:str="date", col_label:str="label", strftime:bool=False):
    """
    """
    df = df.copy()
    df = df[[col_date, col_label]] 
    if type(df[col_date].values[0]) == str:
        df[col_date] = pd.to_datetime(df[col_date], format=dtformat)
    df[col_date] = df[col_date].dt.floor(countBy)
    labels_unique = df[col_label].unique()
    dates_unique = df[col_date].unique()
    records = []
    for date in tqdm(dates_unique):
        record = {"date":date}
        for label in labels_unique:
            count = len(df[(df[col_date]==date)&(df[col_label]==label)])
            record[f"label_{label}"] = count
        records.append(record)
    df = pd.DataFrame.from_records(data=records)
    return df
        