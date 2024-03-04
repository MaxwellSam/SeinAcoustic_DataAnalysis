from DBBuilder.__datereader import DateReader
from DBBuilder import Sun, Moon
from DBBuilder.meteo import OpenMeteo
import numpy as np
import pandas as pd
from dateutil import tz
from IPython.display import display

class DBBuilder (DateReader):

    timefreq_to_count_occ:str="min"

    def __init__(self, latitude:float=48.886, longitude:float=2.333, elevation:float=35, timezone:str="UTC", timefreq="h", **kargs) -> None:
        self.sun = Sun(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.moon = Moon(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.meteo = OpenMeteo(latitude=latitude, longitude=longitude, timezone=timezone)
        self.timefreq = timefreq
        super().__init__(timezone=timezone)
        
    def create_acoustic_db (self, dates:np.ndarray, labels:np.ndarray, format:str="%Y-%m-%d %H:%M:%S"):
        # 1) Count labels occurence over time  
        labels_count = self.count_labels_occurence(dates=dates, labels=labels, timefreq=self.timefreq_to_count_occ, format=format)
        # 2) Find astral informations
        ## 2.1) Sun informations
        df_sun = pd.DataFrame(labels_count.date.apply(self.sun.get_infos, format=format).to_list())
        ## 2.2) Moon informations
        df_moon = pd.DataFrame(labels_count.date.apply(self.moon.get_infos, format=format).to_list())
        astral_infos = pd.merge(df_sun, df_moon, on="date")
        labels_count = pd.merge(labels_count, astral_infos, on="date")
        # 3) Agregation by suncycles
        labels_count_aggBy = self.agregate_count_by(df=labels_count, timefreq=self.timefreq, format=format)
        return labels_count_aggBy 
    
    def agregate_count_by (self, df:pd.DataFrame, traget_cols:list=None, col_date:str="date", grpBy=["suncycle_type", "suncycle_day"], 
                              timefreq="h", format="%Y-%m-%d %H:%M:%S", traget_prefix:str="label"):
        """
        Agregate a set of count (expl: label counts over time) by time frequency and other (default suncycle info)
        ## Params
        df: pd.DataFrame
            dataframe with counting informations and other (suncycle info)
        target_cols: list
            columns to aggregate (must be a counting measure)
        col_date: str
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
        df[col_date] = df[col_date].apply(self.read_date, format=format)
        traget_cols = [c for c in df.columns if c.startswith(traget_prefix)] if not traget_cols else traget_cols
        grpby_params = [df[col_date].dt.floor(timefreq)] + grpBy 

        agg_params = {k:"sum" for k in traget_cols}
        agg_params.update({col_date: ['min', 'max']})
        aggreg = df.groupby(grpby_params).agg(agg_params).reset_index()
        aggreg.columns = ['_'.join(col) for col in aggreg.columns.values]
        return aggreg

    def count_labels_occurence (self, dates:np.ndarray, labels:np.ndarray, timefreq="min", prefix:str="label_", format="%Y-%m-%d %H:%M:%S"):
        """
        Count labels occurrence in a time frequency from a list of dates and labels
        """
        df = pd.DataFrame({"date":dates, "label":labels})
        df.date = df.date.apply(self.read_date, format=format)
        df_grouped = df.groupby([pd.Grouper(key='date', freq=timefreq), 'label']).size().reset_index(name='count')
        df_pivot = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        index_complet = pd.date_range(start=df_pivot.index.min(), end=df_pivot.index.max(), freq=timefreq)
        labels_count = df_pivot.reindex(index_complet, fill_value=0)
        labels_count = labels_count.add_prefix(prefix).reset_index(names=["date"])
        # labels_count.columns = [f"label_{col}" if col != 'date' else col for col in labels_count.columns]
        return labels_count


