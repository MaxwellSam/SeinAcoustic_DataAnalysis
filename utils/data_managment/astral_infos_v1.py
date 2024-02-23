import pandas as pd
import numpy as np
import datetime
import pytz
from astral import Observer, sun, moon, SunDirection


def compute_astral_infos (df:pd.DataFrame, lat:float, lon:float, elevation:float=0, icol_date:int=0, dtformat:str="%Y-%m-%d %H:%M:%S", tzinfo=None):
    obs = Observer(latitude=lat, longitude=lon, elevation=elevation)
    # print(df)
    dates = pd.Series(df.iloc[:, icol_date].values)
    if type(dates[0]) == str:
        dates = pd.to_datetime(dates, format=dtformat)
    data = find_sunCycle_type(obs=obs, dates=dates, tzinfo=tzinfo)
    data.update(compute_moon_infos(obs=obs, dates=dates))
    for k, v in data.items():
        df[k]=v
    return df

def find_sunCycle_type (obs, dates, tzinfo=None, dtArountDuskDawn:datetime.timedelta=datetime.timedelta(hours=1, minutes=30), dtformat:str="%Y-%m-%d %H:%M:%S"):
    data = {}
    days = pd.to_datetime(np.unique(dates.dt.strftime("%Y-%m-%d")), format="%Y-%m-%d")
    df_sunInfo_days = pd.DataFrame(sunInfos_byDays(obs=obs, days=days, tzinfo=tzinfo, dtformat=dtformat))
    for c in df_sunInfo_days.columns:
        df_sunInfo_days[c] = pd.to_datetime(df_sunInfo_days[c])
        if c in ["dusk", "dawn"]:
            df_sunInfo_days[f"start_{c}"] = df_sunInfo_days[c] - dtArountDuskDawn
            df_sunInfo_days[f"stop_{c}"] = df_sunInfo_days[c] + dtArountDuskDawn
    return data

def sunCycle_byDays (obs:Observer, days, tzinfo=None, dtArountDuskDawn:datetime.timedelta=datetime.timedelta(hours=1, minutes=30)):
    data = {}
    df_sunInfo_days = pd.DataFrame(sunInfos_byDays(obs=obs, days=days, tzinfo=tzinfo, dtformat=dtformat))
    for c in df_sunInfo_days.columns:
        df_sunInfo_days[c] = pd.to_datetime(df_sunInfo_days[c])
        if c in ["dusk", "dawn"]:
            df_sunInfo_days[f"start_{c}"] = df_sunInfo_days[c] - dtArountDuskDawn
            df_sunInfo_days[f"stop_{c}"] = df_sunInfo_days[c] + dtArountDuskDawn
    # data["twilight_rising"] = days.apply(get_time(obs, funct=sun.twilight, tzinfo=tzinfo, direction=SunDirection.RISING))
    # data["twilight_setting"] = days.apply(get_time(obs, funct=sun.twilight, tzinfo=tzinfo, direction=SunDirection.SETTING)) 
    # data["daylight"] = days.apply(get_time(obs, funct=sun.daylight, tzinfo=tzinfo))
    # data["night"] = days.apply(get_time(obs, funct=sun.night, tzinfo=tzinfo))
    return data

def sunInfos_byDays (obs:Observer, days, tzinfo=None, dtformat:str="%Y-%m-%d %H:%M:%S"):
    data = {}
    sun_functs = {"sunset":sun.sunset, "sunrise":sun.sunrise, 
                  "dusk":sun.dusk, "dawn":sun.dawn}
    for k, funct in sun_functs.items():
        data[k] = days.apply(get_time(obs, funct=funct, tzinfo=tzinfo, dtformat=dtformat))
    return data

def compute_sun_infos(obs, dates:pd.Series):
    data = {}
    sun_functs = {"sunset":sun.sunset, "sunrise":sun.sunrise, 
                  "dusk":sun.dusk, "dawn":sun.dawn, "noon":sun.noon}
    # data["sunset"] = dates.apply(get_dt(obs, funct=sun.sunset))
    # data["sunrise"] = dates.apply(get_dt(obs, funct=sun.sunrise))
    # data["dusk"] = dates.apply(get_dt(obs, funct=sun.dusk))
    # data["dawn"] = dates.apply(get_dt(obs, funct=sun.dawn))
    # data["dist_noon"] = dates.apply(get_dt(obs, funct=sun.noon))
    for k, funct in sun_functs.items():
        data[k] = dates.apply(get_time(obs, funct=funct))
        # data[f"dist_{k}"] = abs(dates-data[k])
    data["isNight"] = dates.apply(is_night(obs))
    return data

def compute_moon_infos (obs:Observer, dates:pd.Series):
    data = {}
    data["moon_phase"] = dates.apply(moon.phase)
    # data["dist_moonset"] = dates.apply(get_dt(obs, funct=moon.moonset))
    # data["dist_moonrise"] = dates.apply(get_dt(obs, funct=moon.moonrise))
    return data

def is_night (obs):
    def inner(date):
        date = date.replace(tzinfo=pytz.UTC)
        night_start, night_stop = sun.night(observer=obs, date=date)
        return night_start < date < night_stop
    return inner
    
def get_dt (obs, funct:callable, timeUnit:str="hour"):
    def inner(date):
        date = date.replace(tzinfo=pytz.UTC)
        output_date = funct(obs, date)
        deltatime = date - output_date
        if timeUnit=="minut":
            return abs(deltatime.minut)
        elif timeUnit=="hour":
            return abs(deltatime.hour)
        else:
            return deltatime
    return inner

def get_time (obs, funct:callable, dtformat=None, **kargs):
    def inner(date):
        time = funct(obs, date, **kargs)
        if dtformat:
            time.dt.strftime(dtformat)
        return time
    return inner