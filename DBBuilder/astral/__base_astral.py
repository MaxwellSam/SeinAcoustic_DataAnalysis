from DBBuilder.__datereader import DateReader
from astral import Observer
import pandas as pd
import numpy as np
import datetime

class BaseAstral (DateReader): 

    astral_functs:dict 
    data=pd.DataFrame() 

    def __init__(self, latitude:float=48.886, longitude:float=2.333, elevation:float=35, timezone:str="UTC", **kargs) -> None:
        self.obs = Observer(latitude=latitude, longitude=longitude, elevation=elevation)
        super().__init__(timezone)
    
    def daily_infos_in_range (self, start, end):
        """
        Compute daily infos in date range 
        """
        start, end = [self.read_date(d).floor("d") for d in [start, end]]
        days = pd.date_range(start=start, end=end, freq="d")
        records = []
        for day in days:
            record = self.get_day_infos(date=day)
            records.append(record)
        self.add_new_records(data=records)
        return self.data
        
    def get_day_infos (self, date, format:str="%Y-%m-%d %H:%M:%S"):
        """
        Get infos of date
        """
        date = self.read_date(date, format=format)
        day = date.floor("d")
        day_infos = {"day":day}
        if day in self.data.index:
            day_infos.update(self.data.loc[day].to_dict())
        else:
            for k_funct in self.astral_functs.keys():
                day_infos[k_funct] = self._run_astral_funct(k_funct, date)
            self.add_new_records(data=[day_infos])
        return day_infos

    def _run_astral_funct(self, functKey:str, date:datetime.datetime):
        """
        run astral function
        """
        return None
    
    def read_date (self, date:any, format:str="%Y-%m-%d %H:%M:%S"):
        if type(date)==str:
            date = pd.to_datetime(date, format=format)
        else:
            date = pd.to_datetime(date)
        if date.tzinfo != self.timezone:
            date = date.replace(tzinfo=self.timezone)
        return date
    
    def add_new_records (self, data:list):
        new_data = pd.DataFrame(data)
        new_data = new_data.set_index("day")
        self.data = pd.concat([self.data, new_data])
        self.data.index.duplicated(keep="first")
        self.data = self.data.sort_index()
        
        
            

    
        
        

