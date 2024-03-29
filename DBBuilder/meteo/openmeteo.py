import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
import datetime
from dateutil import tz

class OpenMeteo ():

    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    hourly = ["temperature_2m", "relative_humidity_2m", "precipitation", 
              "rain", "cloud_cover", "et0_fao_evapotranspiration", 
              "soil_temperature_0_to_7cm", "soil_moisture_0_to_7cm"]

    def __init__(self, latitude:float=48.886, longitude:float=2.333, timezone:str="UTC") -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_str, self.timezone = timezone, tz.gettz(timezone)

    def get_meteo (self, date_start, date_end, format="%Y-%m-%d %H:%M:%S"):
        return self._request_api(date_start=date_start, date_end=date_end, format=format)

    def _request_api (self, date_start, date_end, format="%Y-%m-%d %H:%M:%S"):
        date_start = self.read_date(date_start, format=format)
        date_end = self.read_date(date_end, format=format)
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": date_start.strftime("%Y-%m%d 00:00:00"),
            "end_date": date_end.strftime("%Y-%m%d 00:00:00"),
            "hourly": self.hourly,
            "timezone": self.timezone_str
        }
        responses = self.openmeteo.weather_api(self.url, params=params)
        response = responses[0]
        hourly = response.Hourly()
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s"),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left",
            tz=self.timezone
        )}
        for i in range(len(params["hourly"])):
            hourly_data[params["hourly"][i]] = hourly.Variables(i).ValuesAsNumpy()
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        return hourly_dataframe

    def read_date (self, date:any, format:str="%Y-%m-%d %H:%M:%S"):
        if type(date)==str:
            date = pd.to_datetime(date, format=format)
        else:
            date = pd.to_datetime(date)
        if date.tzinfo != self.timezone:
            date = date.replace(tzinfo=self.timezone)
        return date