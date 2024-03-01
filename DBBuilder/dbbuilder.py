from DBBuilder.__datereader import DateReader
from DBBuilder import Sun, Moon
from DBBuilder.meteo import OpenMeteo
import numpy as np
import pandas as pd
from dateutil import tz
from IPython.display import display

class DBBuilder (DateReader):

    def __init__(self, latitude:float=48.886, longitude:float=2.333, elevation:float=35, timezone:str="UTC", timefreq="min", **kargs) -> None:
        self.sun = Sun(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.moon = Moon(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, **kargs)
        self.meteo = OpenMeteo(latitude=latitude, longitude=longitude, timezone=timezone)
        self.timefreq = timefreq
        super().__init__(timezone=timezone)
        

    def create (self, dates:np.ndarray, labels:np.ndarray, format:str="%Y-%m-%d %H:%M:%S"):
        labels_occ = self.get_labels_occurrence(dates=dates, labels=labels, format=format)
        print("labels_occ")
        display(labels_occ)
        df_sun = pd.DataFrame(labels_occ.date.apply(self.sun.get_infos, format=format).to_list())
        print("df_sun")
        display(df_sun)
        df_moon = pd.DataFrame(labels_occ.date.apply(self.moon.get_infos, format=format).to_list())
        print("df_moon")
        display(df_moon)
        astral_infos = pd.merge(df_sun, df_moon, on="date")
        print("astral_infos")
        display(astral_infos)
        final_df = pd.merge(labels_occ, astral_infos, on="date")
        print("final_df")
        display(final_df)
        return final_df
        

        
    def get_labels_occurrence (self, dates:np.ndarray, labels:np.ndarray, timefreq="min", format="%Y-%m-%d %H:%M:%S"):
        """
        Count labels occurrence in a time frequency from a list of dates and labels
        """
        df = pd.DataFrame({"date":dates, "label":labels})
        df.date = df.date.apply(self.read_date, format=format)
        df.date = df.date.apply(self.read_date, format=format)
        df['date'] = pd.to_datetime(df['date'])
        df_grouped = df.groupby([pd.Grouper(key='date', freq=timefreq), 'label']).size().reset_index(name='count')
        print("df_grouped")
        display(df_grouped)
        df_pivot = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        print("df_pivot")
        display(df_pivot)
        index_complet = pd.date_range(start=df_pivot.index.min(), end=df_pivot.index.max(), freq=timefreq)
        df_final = df_pivot.reindex(index_complet, fill_value=0)
        df_final = df_final.add_prefix("label_").reset_index(names=["date"])
        # df_final.columns = [f"label_{col}" if col != 'date' else col for col in df_final.columns]
        return df_final


