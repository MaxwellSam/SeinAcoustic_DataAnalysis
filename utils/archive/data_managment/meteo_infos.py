import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
import datetime
from dateutil import tz

def add_open_meteo (df, lat:float=48.866, long:float=2.333, dtformat:str="%Y-%m-%d %H:%M:%S", 
                    col_date:str="date", mininal_last_rain:float=4.0):
    if type(df[col_date].values[0]) == str:
        df[col_date] = pd.to_datetime(df[col_date], format=dtformat)
    date_start = df[col_date].min() - datetime.timedelta(days=1)
    date_stop = df[col_date].max()
    date_start, date_stop = [datetime.datetime.strftime(date, format="%Y-%m-%d") for date in [date_start, date_stop]]
    df_meteo_hourly = get_meteo(lat=lat, long=long, date_start=date_start, date_stop=date_stop)
    # df_meteo_hourly = find_last_rain(meteo_info=df_meteo_hourly, mininal_rain=mininal_last_rain, col_date="date")
    df["date_hourly"] = df[col_date].dt.floor("h")
    df_meteo_hourly = df_meteo_hourly.rename(columns={"date":"date_hourly"})
    df = df.merge(df_meteo_hourly, on="date_hourly")
    df = df.drop(["date_hourly"], axis=1)
    return df  

def find_last_rain (meteo_info:pd.DataFrame, mininal_rain:float=4.0, col_rain="rain", col_date="date"):
    dates_with_rain = meteo_info.loc[(meteo_info[col_rain]>=mininal_rain), col_date]
    meteo_info["date_last_rain"] = meteo_info[col_date].apply(find_last_date(dates_with_rain))

    #     row = meteo_info.loc[i]
    #     last_dates_with_rain = meteo_info[(meteo_info[col_date] <= row[col_date])&(meteo_info[col_rain]>=mininal_rain)]
    #     if len(last_dates_with_rain) == 0:
    #         last_rain_dists.append(pd.NA)
    #         last_rain_values.append(pd.NA)
    #     else:
    #         dates_dist = np.asarray(abs(last_dates_with_rain[col_date].values - last_dates_with_rain[col_date]))
    #         idx_last_rain = np.argmin(dates_dist)
    #         rain_val = last_dates_with_rain[col_rain].values[idx_last_rain]
    #         dist_val = dates_dist[idx_last_rain]
    #         last_rain_dists.append(pd.Timedelta(dist_val).total_seconds())
    #         last_rain_values.append(rain_val)
    # meteo_info["last_rain_dist"] = last_rain_dists
    # meteo_info["last_rain_value"] = last_rain_values
    return meteo_info

def find_last_date (dates_list):
    def inner(date):
        dates = dates_list[dates_list <= date]
        if len(dates) == 0:
            return None
        else:
            idx = np.argmin(abs(dates - date))
            return dates[idx]
    return inner


def get_meteo (lat, long, date_start, date_stop, 
               hourly_var:list=["temperature_2m", "relative_humidity_2m", "precipitation", "rain", 
                                "cloud_cover", "et0_fao_evapotranspiration", "soil_temperature_0_to_7cm", 
                                "soil_moisture_0_to_7cm"], timezone:str="UTC"):
    """
    Get meteo informations from open-meteo API
    """
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": date_start,
        "end_date": date_stop,
        # "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", 
        #            "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", 
        #            "et0_fao_evapotranspiration", "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", 
        #            "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm", 
        #            "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm", "is_day", 
        #            "sunshine_duration"]
        "hourly": hourly_var,
        "timezone": timezone
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    for i in range(len(params["hourly"])):
        hourly_data[params["hourly"][i]] = hourly.Variables(i).ValuesAsNumpy()
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe.date = pd.to_datetime(hourly_dataframe.date.dt.strftime("%Y-%m-%d %H:%M:%S"))
    return hourly_dataframe
