from DBBuilder.__datereader import DateReader
from DBBuilder import Sun, Moon
from DBBuilder.meteo import OpenMeteo
from DBBuilder.util.datetime import convert_all_dtcolumns_to_str
import numpy as np
import pandas as pd
from dateutil import tz
from IPython.display import display

class DBBuilder (DateReader):

    timefreq_to_count_occ:str="min"
    data:dict={}

    def __init__(self, latitude:float=48.886, longitude:float=2.333, elevation:float=35, timezone:str="UTC", timefreq="min", **kargs) -> None:
        self.sun = Sun(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.moon = Moon(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.meteo = OpenMeteo(latitude=latitude, longitude=longitude, timezone=timezone)
        self.timefreq = timefreq
        super().__init__(timezone=timezone)
        
    def run (self, dates:np.ndarray, labels:np.ndarray, dfs_toMerge:list=[], on="date", format:str="%Y-%m-%d %H:%M:%S"):
        """
        """
        output = {}
        dates = pd.Series(dates).apply(self.read_date, format=format)
        # Astral infos
        astral_daily_infos = self.get_astral_daily_infos(date_start=dates.min(), date_end=dates.max(), format=format)
        sun_infos = pd.DataFrame(dates.apply(self.sun.get_infos, format=format).to_list())
        # Acoustic infos  
        labels_count = self.count_labels_occurence(dates=dates, labels=labels, timefreq=self.timefreq, format=format)
        acoustic_infos = pd.merge(labels_count)
        # 2) Aggregate by suncycle
        sun_infos = pd.DataFrame(db.date.apply(self.sun.get_infos, format=format).to_list())
        db = pd.merge(db, sun_infos, on="date")
        output[f"db_{self.timefreq_to_count_occ}"] = db.copy()
        db = self.agregate_count_by(df=db, timefreq=self.timefreq, format=format)
        # 4) add astral infos 
        tw_infos = pd.DataFrame(db.date.apply(self.sun.get_twilight_infos, format=format).to_list())
        # moon_infos = pd.DataFrame(db.suncycle_day.unique().apply(self.moon.get_infos, format=format).to_list())
        moon_infos = pd.DataFrame([self.moon.get_infos(date, format=format) for date in db.suncycle_day.unique()])
        db = pd.merge(db, tw_infos, on="date")
        db = pd.merge(db, moon_infos.rename(columns={"date":"suncycle_day"}), on="suncycle_day")
        # 5) get meteo data
        meteo_infos = self.meteo.get_meteo(
            date_start=db.date.min(), 
            date_end=db.date.max(), 
            format=format)
        db = pd.merge(db, meteo_infos, on="date")
        self.data[f"db_{self.timefreq}_meteo"] = db.copy()
        if len(dfs_toMerge) > 0:
            for df in dfs_toMerge:
                db = pd.merge(db, df, on=on)
        return db
    
    def get_astral_daily_infos (self, date_start:pd.Timestamp, date_end:pd.Timestamp, format="%Y-%m-%d %H:%M:%S"):
        """
        Get astral informations on a range of days 
        """
        date_start, date_end = [self.read_date(d) for d in [date_start, date_end]]
        dates = pd.date_range(start=date_start.floor(freq="d"), stop=date_end.floor(freq="d"), freq="d")
        df_sun_daily_infos = pd.DataFrame(dates.apply(self.sun.get_day_infos, format=format).to_list())
        df_moon_daily_infos = pd.DataFrame(dates.apply(self.moon.get_day_infos, format=format).to_list())
        df_astral_infos = pd.merge(df_sun_daily_infos, df_moon_daily_infos, on="day")
        return df_astral_infos
    
    def from_labels_occurence (self, dates, labels, format="%Y-%m-%d %H:%M:%S"):
        df_count = self.occ_to_count(dates=dates, labels=labels)
        

    def occ_to_count (self, dates, labels, prefix:str="label_", format="%Y-%m-%d %H:%M:%S"):
        df = pd.DataFrame({"date":dates, "label":labels})
        df.date = df.date.apply(self.read_date, format=format)
        df_grouped = df.groupby(['date', 'label']).size().reset_index(name='count')
        df_count = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        df_count = df_count.add_prefix(prefix).reset_index(names=["date"])
        return df_count
    
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
        aggreg.columns = ['_'.join(col) if col[1]!='' and col[1] != "sum" else col[0] for col in aggreg.columns.values]
        return aggreg

    def count_labels_occurence (self, dates:np.ndarray, labels:np.ndarray, timefreq="min", prefix:str="label_", format="%Y-%m-%d %H:%M:%S"):
        """
        Count labels occurrence in a time frequency from a list of dates and labels
        """
        df = pd.DataFrame({"date":dates, "label":labels})
        df.date = df.date.apply(self.read_date, format=format)
        df_grouped = df.groupby([pd.Grouper(key='date', freq=timefreq), 'label']).size().reset_index(name='count')
        df_count = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        # index_complet = pd.date_range(start=df_count.index.min(), end=df_count.index.max(), freq=timefreq)
        # count_freq1 = df_count.reindex(index_complet, fill_value=0)
        df_count = df_count.add_prefix(prefix).reset_index(names=["date"])
        return df_count


