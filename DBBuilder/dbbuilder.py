from DBBuilder.__datereader import DateReader
from DBBuilder import Sun, Moon
from DBBuilder.meteo import OpenMeteo
from DBBuilder.util.datetime import convert_all_dtcolumns_to_str
import numpy as np
import pandas as pd
from dateutil import tz
from IPython.display import display

class DBBuilder (DateReader):

    """
    # DBBuilder

    Python object for database generation from labels detection to organise and complete time series data by :
    1) Organizing labels detection by `timefreq` (default count by minutes)
    2) Find astral informations about sun (suncycle) and moon (phase)
    3) Find meteorological informations 

    ## How to use it
    
    ### 1) Generate database

    #### From labels occurence

    ```python
        df = pd.read_csv("PATH/TO/DETECTION/OCCURENCE/file.csv")
        print(df)
        
        # Dataframe structure
        #         date                 label
        # 0       2022-05-11 00:07:00      9
        # 1       2022-05-11 00:07:00      9
        # ...                     ...    ...
        # 184973  2022-06-09 10:37:00      3
        # 184974  2022-06-09 10:38:00      0

        # 1) dbbuilder object initialisation
        dbbuilder = DBBuilder(latitude=lat, longitude=long, elevation=elev)
        # 2) get acoustic data (with label occurences)
        dfs = [pd.read_csv(file)[["date", "label"]] for file in files_sensea_yolo[:1]]
        df = pd.concat(dfs)
        # 3) use dbbuilder to create database
        output = dbbuilder.from_labels_occurence(dates=df.date, labels=df.label, prefix="label_")
    ```

    #### From labels count

    ```python
        df = pd.read_csv("PATH/TO/DETECTION/OCCURENCE/file.csv")
        print(df)
        
        #     date                          label_0   ...  label_10  
        # 0     2022-05-11 00:06:00+00:00      5.0    ...      0.0   
        # 1     2022-05-11 00:07:00+00:00      0.0    ...      0.0     
        # ...                         ...      ...    ...      ...       
        # 9551  2022-06-09 10:37:00+00:00      0.0    ...      2.0      
        # 9552  2022-06-09 10:38:00+00:00      1.0    ...      0.0

        # 1) dbbuilder object initialisation
        dbbuilder = DBBuilder(latitude=lat, longitude=long, elevation=elev)
        # 2) get acoustic data (with label occurences)
        dfs = [pd.read_csv(file)[["date", "label"]] for file in files_sensea_yolo[:1]]
        df = pd.concat(dfs)
        # 3) use dbbuilder to create database
        output = dbbuilder.from_labels_count(df=df, colnames_label=[c for c in df.columns if c.startswith("label_")])
    ```
    
    Sam MAXWELL - 2024
    """

    input_count:pd.DataFrame=None
    detection:pd.DataFrame=None
    meteo_infos_hourly:pd.DataFrame=None
    astral_infos_daily:pd.DataFrame=None

    def __init__(self, latitude:float=48.886, longitude:float=2.333, elevation:float=35, timezone:str="UTC", timefreq="min", dateformat_output:str="%Y-%m-%d %H:%M:%S",**kargs) -> None:
        self.sun = Sun(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.moon = Moon(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.meteo = OpenMeteo(latitude=latitude, longitude=longitude, timezone=timezone)
        self.timefreq = timefreq
        self.dateformat_output = dateformat_output
        self.latitude, self.longitude, self.elevation = latitude, longitude, elevation
        super().__init__(timezone=timezone)
    
    # ---- input functions ---- #
        
    def from_labels_occurence (self, dates, labels, prefix:str="label_", format="%Y-%m-%d %H:%M:%S"):
        df_count = self.occurence_to_count(dates=dates, labels=labels, prefix=prefix, format=format)
        return self.from_labels_count(df=df_count)
        
    def from_labels_count(self, df:pd.DataFrame, colnames_label:list=None, colname_date:str="date", label_prefix:str="label_", format="%Y-%m-%d %H:%M:%S"):
        self.input_count = df.copy()
        self.dateformat_input = format
        df = df.rename(columns={colname_date:"date"})
        labels_count = self.agg_detection(df=df, cols_to_sum=colnames_label, 
                                          colname_date="date", grpBy=None, timefreq=self.timefreq, 
                                          format=format, traget_prefix=label_prefix)
        self.colnames_label = colnames_label
        self.detection = labels_count
        output = self.__create_db()
        return output

    # ---- build function ---- #
        
    def __generate_output(self):
        output={
            "data":{
                f"detection_{self.timefreq}":self.detection,
                "astral_infos_d":self.astral_infos_daily,
                "meteo_infos_h":self.meteo_infos_hourly
            },
            "infos":{
                "latitude":self.latitude,
                "longitude":self.longitude,
                "elevation":self.elevation,
                "timezone":self.timezone
            }
        }
        output["data"] = {k:convert_all_dtcolumns_to_str(df, format=self.dateformat_output).to_dict(orient="records") 
                          for k,df in output["data"].items()}
        self.output = output
        return output
    
    def __create_db (self):
        """
        Create database with detection, astral and meteo informations.
        """
        dates = self.detection.date
        # Astral infos
        self.astral_infos_daily = self.get_astral_infos_daily(date_start=dates.min(), date_end=dates.max(), format=format)
        suncycle_infos = pd.DataFrame(dates.apply(self.sun.get_infos, format=format).to_list())
        # Meteo  infos
        self.meteo_infos_hourly = self.meteo.get_meteo(date_start=dates.min(), date_end=dates.max())
        # Detection infos
        self.detection = pd.merge(self.detection, suncycle_infos, on="date")
        output = self.__generate_output()
        return output
    
    # ---- data recuperation ---- # 
    
    def get_astral_infos_daily (self, date_start:pd.Timestamp, date_end:pd.Timestamp, format="%Y-%m-%d %H:%M:%S"):
        """
        Get astral informations on a range of days 
        """
        date_start, date_end = [self.read_date(d) for d in [date_start, date_end]]
        dates = pd.Series(pd.date_range(start=date_start.floor(freq="d"), end=date_end.floor(freq="d"), freq="d"))
        df_sun_daily_infos = pd.DataFrame(dates.apply(self.sun.get_day_infos, format=format).to_list())
        df_moon_daily_infos = pd.DataFrame(dates.apply(self.moon.get_day_infos, format=format).to_list())
        df_astral_infos = pd.merge(df_sun_daily_infos, df_moon_daily_infos, on="day")
        return df_astral_infos
    
    # ---- tool functions ---- #

    def occurence_to_count (self, dates, labels, prefix:str="label_", format="%Y-%m-%d %H:%M:%S"):
        df = pd.DataFrame({"date":dates, "label":labels})
        df.date = df.date.apply(self.read_date, format=format)
        df_grouped = df.groupby(['date', 'label']).size().reset_index(name='count')
        df_count = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        df_count = df_count.add_prefix(prefix).reset_index(names=["date"])
        return df_count
    
    def agg_detection (self, df:pd.DataFrame=None, cols_to_sum:list=None, colname_date:str="date", grpBy=["suncycle_type", "suncycle_day"], 
                              timefreq="h", other_agg_params:dict={}, format="%Y-%m-%d %H:%M:%S", traget_prefix:str="label"):
        """
        Agregate a set of count (expl: label counts over time) by time frequency and other (default suncycle info)
        ## Params
        df: pd.DataFrame
            dataframe with counting informations and other (suncycle info)
        cols_to_sum: list
            columns to sum during aggregation (must be a counting measure)
        colname_date: str
            column name of date values
        grpBy: list
            column name to group by (default by suncycle type and day)
        timefreq: str
            time frequency for aggregation (default hourly)
        format: str
            datetime format if str
        target_prefix: str
            prefix of target columns if target columns list is None
        # Return  
        aggreg: pd.DataFrame
            results of aggregation
        """
        df, cols_to_sum = [self.detection, self.colnames_label] if type(df) == type(None) else [df, cols_to_sum]
        df[colname_date] = df[colname_date].apply(self.read_date, format=format)
        # Define columns to aggregate
        cols_to_sum = [c for c in df.columns if c.startswith(traget_prefix)] if not cols_to_sum else cols_to_sum
        # Group by parameters
        grpby_params = [df[colname_date].dt.floor(timefreq)] 
        grpby_params += grpBy if grpBy != None else []
        # Aggregation params
        agg_params = {k:"sum" for k in cols_to_sum}
        agg_params.update({colname_date: ['min', 'max']})
        agg_params.update(other_agg_params)
        aggreg = df.groupby(grpby_params).agg(agg_params).reset_index()
        aggreg.columns = ['_'.join(col) if col[1]!='' and col[1] != "sum" else col[0] for col in aggreg.columns.values]
        return aggreg


