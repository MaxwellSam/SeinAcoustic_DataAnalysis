import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
import datetime
from dateutil import tz

from DBBuilder.util.metadata import metadata

class OpenMeteo ():

    metadata = metadata[metadata["source"]=="openmeteo"]
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    option_rename_columns:bool=None

    def __init__(self, latitude:float=48.886, longitude:float=2.333, timezone:str="UTC", 
                 renamecolumns:bool=False, add_metadata_in_colname:bool=False) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_str, self.timezone = timezone, tz.gettz(timezone)
        self.option_rename_columns = renamecolumns
        self.option_add_metadata_in_colname = add_metadata_in_colname

    def get_meteo (self, date_start, date_end, format="%Y-%m-%d %H:%M:%S"):
        return self._request_api(date_start=date_start, date_end=date_end, format=format)

    def _request_api (self, date_start, date_end, format="%Y-%m-%d %H:%M:%S"):
        date_start = self.read_date(date_start, format=format)
        date_end = self.read_date(date_end, format=format)
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": date_start.strftime("%Y-%m-%d"),
            "end_date": date_end.strftime("%Y-%m-%d"),
            "hourly": self.metadata["colname"].values.tolist(),
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
        if self.option_rename_columns:
            hourly_dataframe = self.rename_columns_with_metadata(df=hourly_dataframe, add_metadata_infos=self.option_add_metadata_in_colname)
        return hourly_dataframe

    def read_date (self, date:any, format:str="%Y-%m-%d %H:%M:%S"):
        if type(date)==str:
            date = pd.to_datetime(date, format=format)
        else:
            date = pd.to_datetime(date)
        if date.tzinfo != self.timezone:
            date = date.replace(tzinfo=self.timezone)
        return date
    
    def rename_columns_with_metadata (self, df:pd.DataFrame, add_metadata_infos:bool=False):
        metadata = pd.DataFrame(self.metadata).set_index("colname")
        rename_columns = {}
        for i in metadata.index:
            if i in df.columns:
                new_colname = metadata.loc[i]["varname"]
                if add_metadata_infos:
                    metadata_infos = metadata.loc[i][["type", "source", "unit", "timefreq"]].values.tolist()
                    str_metadata_infos = ",".join([str(info) for info in metadata_infos])
                    new_colname += f" ({str_metadata_infos})"
                rename_columns[i] = new_colname
        # self.metadata = metadata.reset_index()
        return df.rename(columns=rename_columns)