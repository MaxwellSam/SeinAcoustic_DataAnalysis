from astral import LocationInfo, Observer, sun, moon, SunDirection
import pandas as pd
import datetime
from dateutil import tz
import numpy as np

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
    if dates[0].tzinfo == None:
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

def get_astral_infos (dates:np.ndarray, lat:float=48.866, long:float=2.333, elev:float=35,
                      dtAroundTwilightZone:float=5400.0, tzinfo=tz.gettz("Europe/Paris"), 
                      dtformat:str="%Y-%m-%d %H:%M:%S"):
    obs = Observer(latitude=lat, longitude=long, elevation=elev)
    if type(dates[0]) == str:
        dates = pd.to_datetime(dates, format=dtformat)
        dates = dates.dt.tz_localize(tzinfo)
    sun_infos = get_sun_infos(obs=obs, dates=dates, tzinfo=tzinfo)
    sun_infos = measure_distToTwilight(sun_infos)
    sun_infos = find_suncycle_type(sun_infos, dtAroundTwilightZone=dtAroundTwilightZone)
    moon_infos = get_moon_infos(obs=obs, dates=dates)
    astral_infos = sun_infos.merge(moon_infos, on="date")
    return astral_infos

def get_sun_infos (obs, dates:np.ndarray, tzinfo=tz.gettz("Europe/Paris")):
    sun_functs = {
        "sunset":sun.sunset, 
        "dusk":sun.dusk, 
        "sunrise":sun.sunrise,
        "dawn":sun.dawn,
        "noon":sun.noon,
        "midnight":sun.midnight
    }
    df, sun_infos = pd.DataFrame(), pd.DataFrame()
    df["date"] = dates
    df["day"] = df.date.floor("d")
    sun_infos["day"] = df.day.unique()
    for k,func in sun_functs.items():
        sun_infos[k] = sun_infos.day.apply(get_time(obs, func, tzinfo=tzinfo))
    df = df.merge(sun_infos, on="day")
    df = df.drop("day", axis=1)
    return df

def find_suncycle_type (sun_infos:pd.DataFrame, dtAroundTwilightZone:float=5400.0):
    """
    """
    sun_infos = measure_distToTwilight(sun_infos, dropMid=True)
    dist_tw_types = [dtw for dtw in sun_infos.columns if  dtw.startswith("dist_tw_")]
    for dtw in dist_tw_types:
        tw = dtw.replace("dist_tw_", "")
        sun_infos.loc[abs(sun_infos[dtw]) <= dtAroundTwilightZone, "suncycle"] = tw
    maskDaylight = sun_infos["suncycle"].isna() # condition 1 => outside twilight zones
    maskDaylight = maskDaylight&(sun_infos["dist_tw_rising"] > 0) # condition 2 => after twilight rising
    maskDaylight = maskDaylight&(sun_infos["dist_tw_setting"] < 0) # condition 3 => before twilight setting
    sun_infos.loc[maskDaylight, "suncycle"] = "daylight"
    sun_infos.loc[sun_infos["suncycle"].isna(), "suncycle"] = "night"
    return sun_infos

def measure_distTo (sun_infos:pd.DataFrame, colname:str, col_date:str="date"):
    new_col = f"dist_{colname}" 
    sun_infos[new_col] = sun_infos[col_date] - sun_infos[colname]
    sun_infos[new_col] = sun_infos[new_col].dt.total_seconds()
    return sun_infos

def measure_distToTwilight (sun_infos:pd.DataFrame, dropMid:bool=True):
    sunrise, dawn = [sun_infos[col] for col in ["sunrise", "dawn"]]
    sunset, dusk = [sun_infos[col] for col in ["sunset", "dusk"]]
    sun_infos["mid_tw_rising"] = dawn + (sunrise - dawn)/2
    sun_infos["mid_tw_setting"] = sunset + (dusk - sunset)/2
    mid_tw_dates = [c for c in sun_infos.columns if "mid_tw" in c]
    for mid_tw in mid_tw_dates:
        dist_tw = mid_tw.replace("mid_", "dist_")
        sun_infos[dist_tw] = sun_infos.date - sun_infos[mid_tw]
        sun_infos[dist_tw] = sun_infos[dist_tw].dt.total_seconds()
    if dropMid:
        sun_infos=sun_infos.drop(["mid_tw_rising", "mid_tw_setting"], axis=1)
    return sun_infos


def get_moon_infos (obs, dates:np.ndarray):
    df, moon_infos = pd.DataFrame(), pd.DataFrame()
    df["date"] = dates
    df["day"] = df.date.floor("d")
    moon_infos["day"] = df.day.unique()
    moon_infos["moon_phase"] = moon_infos.day.apply(moon.phase)
    df = df.merge(moon_infos, on="day")
    df = df.drop("day", axis=1)
    return df

def get_time (obs, funct:callable, dtformat=None, **kargs):
    def inner(date):
        time = funct(obs, date, **kargs)
        if dtformat:
            time.dt.strftime(dtformat)
        return time
    return inner