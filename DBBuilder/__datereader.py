import pandas as pd
from dateutil import tz

class DateReader ():

    def __init__(self, timezone:str="UTC") -> None:
        self.timezone_str, self.timezone = timezone, tz.gettz(name=timezone)
        
    def read_date (self, date:any, format:str="%Y-%m-%d %H:%M:%S"):
        if type(date)==str:
            date = pd.to_datetime(date, format=format)
        else:
            date = pd.to_datetime(date)
        if date.tzinfo != self.timezone:
            date = date.replace(tzinfo=self.timezone)
        return date