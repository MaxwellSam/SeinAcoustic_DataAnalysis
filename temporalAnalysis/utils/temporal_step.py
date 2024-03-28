import numpy as np
import pandas as pd

def get_date_interval (date:pd.Timestamp, freq:str="d", periods:int=6, as_string:bool=True):
    dates = pd.date_range(start=date, freq=freq, periods=periods)
    dateint = (dates.min(), dates.max())
    if as_string:
        dateint = "/".join([x.strftime("%Y-%m-%d") for x in dateint])
    return dateint

# def find_temporal_step (start:pd.Timestamp, end:pd.Timestamp, 
#                         timefreq:str="h", period:str="W", step:int=1):
#     dates = pd.date_range(start=start, end=end, freq=timefreq)