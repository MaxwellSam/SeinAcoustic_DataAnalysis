import pandas as pd
import datetime
from tqdm import tqdm
import numpy as np
from dateutil import tz
# from utils.data_managment.suncycle import get_sunCycle
from utils.data_managment.datetime import setup_datetime
from utils.data_managment.astral_infos import Observer, get_sun_infos, find_suncycle_type, get_moon_infos, measure_distTo
from utils.data_managment.meteo_infos import add_open_meteo, get_meteo

def dataset_from_report (detection_report:pd.DataFrame, lat:float=48.866, long:float=2.333, elev:float=35,
                         countBy:str="h", Qday_countBy:str="min", Qday_groupBy:str="suncycle", Qday_dtAroundTwilightZone:float=5400.0,
                         timezone="Europe/Paris", dtformat:str="%Y-%m-%d %H:%M:%S", col_date:str="date", col_label="label"):
    obs = Observer(latitude=lat, longitude=long, elevation=elev)
    print("---")
    detection_report = setup_datetime(df=detection_report, columns=[col_date], dtformat=dtformat, timezone=timezone)
    print("1) setup datetime")
    # 1) generate Qday with suninfos (dt = Qday_countBy)
    df = count_detections_fromReport(detection_report, countBy=Qday_countBy, col_date=col_date, col_label=col_label)
    print(f"2) count_detections by {Qday_countBy}")
    df["day"] = df[col_date].dt.floor("d")
    sun_infos_days = get_sun_infos(obs=obs, dates=df["day"], tzinfo=tz.gettz(timezone)).rename(columns={"date":"day"})
    moon_infos_day = get_moon_infos(obs=obs, dates=sun_infos_days["day"]).rename(columns={"date":"day"})
    print("3) get sun and moon infos by day")
    astral_infos = sun_infos_days.merge(moon_infos_day, on="day")
    df = df.merge(sun_infos_days, on="day")
    df = find_suncycle_type(sun_infos=df, dtAroundTwilightZone=Qday_dtAroundTwilightZone)
    print("4) find suncycles")
    # 2) count detection (dt = countBy)
    df[col_date] = df[col_date].dt.floor(countBy) 
    for label in [c for c in df.columns if c.startswith(col_label)]:
        df = df.groupby([col_date, Qday_groupBy], as_index=False)[[c for c in df.columns if c.startswith(col_label)]].sum()
    print(f"5) group by suncycle and count by {countBy}")
    # 3) add astral infos
    df["day"] = df[col_date].dt.floor("d")
    # df = df.merge(astral_infos, on="day")
    # print("6) add suncycle and moon infos")
    # si_dcol = [c for c in sun_infos_days.columns if c not in ["day", "date"]]
    # df = measure_distTo(sun_infos=df, colname=si_dcol, coldate=col_date)
    # df = df.drop(si_dcol, axis=1)
    # print("7) compute dist to sun points")
    # 4) add meteo infos
    dstart, dstop = [d.strftime("%Y-%m-%d") for d in [df["day"].min(), df["day"].max()]]
    meteo_info = get_meteo(lat=lat, long=long, date_start=dstart, date_stop=dstop, timezone=timezone).rename(columns={"date":col_date})
    meteo_info = setup_datetime(meteo_info, columns=[col_date], timezone=timezone)
    df = df.merge(meteo_info, on=col_date)
    print("8) add meteo data")
    print(df)
    return df

# def create_full_dataframe (detection_report:pd.DataFrame, lat:float=48.866, long:float=2.333, elev:float=35,
#                            dtAroundTwilightZone:float=5400.0, tzinfo=tz.gettz("Europe/Paris"), dtformat:str="%Y-%m-%d %H:%M:%S", 
#                            col_date:str="date", col_label="label", col_rain="rain", countBy_1="min", countBy_2="h", 
#                            groupBy="suncycle"):
#     obs = Observer(latitude=lat, longitude=long, elevation=elev)
#     df = count_detections_fromReport(detection_report, dtformat=dtformat, col_date=col_date, col_label=col_label, countBy=countBy_1)
#     df = 
#     df[col_date] = df[col_date].dt.floor(countBy_2)
#     df_detection=df.groupby([col_date, groupBy], as_index=False)[[c for c in df.columns if col_label in c]].sum()
#     df_other_infos=df.groupby([col_date, groupBy], as_index=False)[[c for c in df.columns if not col_label in df()]]
#     df=df_detection.merge(df_astral_hourly.drop(groupBy), on=col_date)
#     df=add_open_meteo(df, lat=lat, long=long, dtformat=dtformat, col_date=col_date)
#     return df

# def sum_detection (detection_count:pd.DataFrame, keycol_label:str="label", sumBy="h", col_date:str="date"):
#     detection_count[col_date] = detection_count[col_date].dt.floor(sumBy)

def count_detection_fromReport (detection_report:pd.DataFrame, dtformat:str="%Y-%m-%d %H:%M:%S", countBy="min",
                    col_date:str="date", col_label:str="label"):
    """
    Count lables detection by time intervales from detection report.
    # Params
    detection_report: pd.DataFrame
        detection report, with informations by rows of datetime and label detected 
        (`detection_report.columns = ["date", "label"]`). 
    dtformat: str
        datetime format, default `"%Y-%m-%d %H:%M:%S"`
    countBy

    """
    df = detection_report.copy()
    df = df[[col_date, col_label]] 
    if type(df[col_date].values[0]) == str:
        df[col_date] = pd.to_datetime(df[col_date], format=dtformat)
    df[col_date] = df[col_date].dt.floor(countBy)
    dates_range = pd.date_range(start=df.date.min(), end=df.date.max(), freq=countBy)
    labels_unique = df[col_label].unique()
    records = []
    for date in tqdm(dates_range):
        record = {"date":date}
        for label in labels_unique:
            count = len(df[(df[col_date]==date)&(df[col_label]==label)])
            record[f"label_{label}"] = count
        records.append(record)
    df = pd.DataFrame.from_records(data=records)
    return df

def count_detections_fromReport (detection_report:pd.DataFrame, countBy="min",
                                 col_date:str="date", col_label:str="label"):
    df = detection_report.copy()
    df = df[[col_date, col_label]] 
    df[col_date] = df[col_date].dt.floor(countBy)
    dates_range = pd.date_range(start=df.date.min(), end=df.date.max(), freq=countBy)
    df = pd.crosstab(df[col_date], df[col_label]).reindex(dates_range, fill_value=0)
    df = df.rename(columns={i:f"{df.columns.name}_{i}" for i in df.columns})
    df.columns.name = None
    df = df.reset_index(names=[col_date])
    df.sort_values(by=col_date)
    return df

    
    