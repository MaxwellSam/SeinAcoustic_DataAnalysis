from astral import LocationInfo, Observer, sun, moon, SunDirection
import pandas as pd
import datetime
from dateutil import tz
import numpy as np

def get_sunCycle (dates:np.ndarray, lat:float=48.866, long:float=2.333, elev:float=35, dtAroundTwilightZone:datetime.timedelta=datetime.timedelta(hours=1, minutes=30), 
                  twilightZones=["dusk", "dawn"], tzinfo=tz.gettz("Europe/Paris"), dtformat:str="%Y-%m-%d %H:%M:%S"):
    """
    Get suncycle type for given dates
    """ 
    cyclezones = ["daylight", "night"]+twilightZones
    obs = Observer(latitude=lat, longitude=long, elevation=elev)
    if type(dates[0]) == str:
        dates = pd.to_datetime(dates, format=dtformat)
    df = pd.DataFrame()
    df["date"] = dates
    df["date"].dt.tz_localize(tzinfo)
    df[cyclezones] = False
    fist_date = df.date.min() - datetime.timedelta(days=1)
    last_date = df.date.max()
    first_day, last_day = [datetime.datetime.strftime(date, format="%Y-%m-%d") for date in [fist_date, last_date]]
    days = pd.date_range(start=first_day, end=last_day).to_list() 
    df_suncycles = sunCycle_byDays(obs, days, tzinfo=tzinfo, dtformat_output=dtformat)
    for i in range(len(df_suncycles)):
        cycle_infos = pd.to_datetime(df_suncycles.iloc[i], format=dtformat)
        for tw in twilightZones:
            tw_time = cycle_infos[tw]
            cycle_infos[f"{tw}_start"] = tw_time - dtAroundTwilightZone
            cycle_infos[f"{tw}_stop"] = tw_time + dtAroundTwilightZone 
        for cz in cyclezones:
            cz_start, cz_stop = [cycle_infos[f"{cz}_{k}"] for k in ["start", "stop"]]
            mask_cz = (cz_start<=dates)&(dates<=cz_stop)
            df.loc[mask_cz, cz] = True
    for cz in cyclezones:
        mask = (df[cz]==True)
        df.loc[mask, "suncycle"] = cz
    cols_toremove = [c for c in df.columns if c not in ["date", "suncycle"]]
    df = df.drop(cols_toremove, axis=1)
    df.date = pd.to_datetime(df.date, format=dtformat)
    return df

def get_suninfos (dates:np.ndarray, lat:float=48.866, long:float=2.333, elev:float=35, 
                  tzinfo=tz.gettz("Europe/Paris"), dtformat:str="%Y-%m-%d %H:%M:%S"):
    functs = {
        "sunset":sun.sunset, 
        "dusk":sun.dusk, 
        "sunrise":sun.sunrise,
        "dawn":sun
    }
    obs = Observer(latitude=lat, longitude=long, elevation=elev)
    if type(dates[0]) == str:
        dates = pd.to_datetime(dates, format=dtformat)
    df = pd.DataFrame()
    # df["date"] = dates
    # df["day"] = df.date
    # df.date = df.date.dt.tz_localize(tzinfo)
    # df["tw_rising"] = df.date.apply(get_time(obs, sun.twilight, direction=SunDirection.RISING, tzinfo=tzinfo))
    # df["tw_setting"] = df.date.apply(get_time(obs, sun.twilight, direction=SunDirection.SETTING, tzinfo=tzinfo))
    # for tw in ["tw_rising", "tw_setting"]:
    #     df[f"center_{tw}"] = df[tw].apply(lambda x: x[0] + (x[0]-x[1])/2)
    #     df[f"dist_{tw}"] = df[f"center_{tw}"] - df["date"]

    return df


def sunCycle_byDays (obs:Observer, days, tzinfo=None, dtformat_input:str="%Y-%m-%d", dtformat_output:str="%Y-%m-%d %H:%M:%S", asDataFrame:bool=True):
    """
    Generate suncycle by days
    """
    records = []
    for day in days:
        records.append(get_suncycle_forDay(obs, day, tzinfo=tzinfo, dtformat_input=dtformat_input, dtformat_output=dtformat_output))
    if asDataFrame:
        return pd.DataFrame(records)
    else:
        return records

def get_suncycle_forDay (obs, day, tzinfo=None, dtformat_input:str="%Y-%m-%d", dtformat_output:str="%Y-%m-%d %H:%M:%S"):
    """
    Generate suncycle infos for a day
    """
    if type(day) == str:
        day = datetime.datetime.strptime(day, dtformat_input)
    record = {}
    single_date_output_functs = {"sunset":sun.sunset, "sunrise":sun.sunrise, "dusk":sun.dusk, "dawn":sun.dawn}
    double_date_output_functs = {"night":sun.night, "daylight":sun.daylight}
    for k, funct in single_date_output_functs.items():
        record[k] = funct(obs, day, tzinfo=tzinfo)
    for k, funct in double_date_output_functs.items():
        record[f"{k}_start"], record[f"{k}_stop"] = funct(obs, day, tzinfo=tzinfo)
    record = {k:v.strftime(dtformat_output) for k,v in record.items()}
    return record

def get_time (obs, funct:callable, dtformat=None, **kargs):
    def inner(date):
        time = funct(obs, date, **kargs)
        if dtformat:
            time.dt.strftime(dtformat)
        return time
    return inner

# def get_midd_time (dstart, dstop):
