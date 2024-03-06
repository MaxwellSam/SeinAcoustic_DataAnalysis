from datetime import datetime, timedelta
from DBBuilder.astral.__base_astral import BaseAstral
from astral import sun
import pandas as pd

class Sun (BaseAstral):
    
    astral_functs:dict={
        "sunset":sun.sunset, 
        "dusk":sun.dusk, 
        "sunrise":sun.sunrise,
        "dawn":sun.dawn,
        "noon":sun.noon,
        "midnight":sun.midnight
    }
    
    def __init__(self, latitude: float = 48.886, longitude: float = 2.333, elevation: float = 35, timeAroundTW:float=5400.0, timezone: str = "UTC", **kargs) -> None:
        super().__init__(latitude, longitude, elevation, timezone, **kargs)
        self.timeAroundTW = timeAroundTW

    def get_infos (self, date, format:str="%Y-%m-%d %H:%M:%S"):
        """
        Get suncycle informations for a given date `Y-m-d H:M:S`. 
        ## Params 

        date: str | datetime | Timestamp
        
            date input.
        
        timeAroundTW: float
            
            time around twilight zones (rising and setting) in seconds.
        
        format: str
            
            date format if to read date date if type string.
        
        ## Return
        
        suncycle_infos: dict
            
            suncycle informations which contain: 
                
                `"suncycle_type"`:str
                    suncycle category `["daylight", "night", "setting", "rising"]`
                
                `"suncycle_day"`:Timestamp
                    day of suncycle (cause suncycle night is between two days)
            
            + twightlight informations `["dist_tw_rising", "dist_tw_setting", ...]`
            + day informations [``]        
        """
        date = self.read_date(date, format=format)
        day = date.floor("d")
        suncycle_type = "night"
        # suncycle infos
        day_infos = self.get_day_infos(date=date, format=format) 
        tw_infos = self.get_twilight_infos(date=date, format=format)
        suncycle_type = self.get_suncycle_type(date=date, tw_infos=tw_infos,
                                          format=format)
        suncycle_day = day 
        if suncycle_type == "night" and tw_infos["dist_tw_setting"] < 0:
            suncycle_day -= timedelta(days=1)
        sun_infos={
            "date":date,
            "suncycle_type":suncycle_type,
            "suncycle_day":suncycle_day,
            **tw_infos
        }
        return sun_infos
        
    def get_suncycle_type (self, date, tw_infos:dict=None, format:str="%Y-%m-%d %H:%M:%S"):
        """
        Get suncycle type
        
        ## Params 
        
        date: str | datetime | Timestamp
            
            date input.

        tw_infos: dict

            twilight informations with `"dist_tw_rising"` and `"dist_tw_setting"` 
            distance to twilight zones (in seconds).
        
        timeAroundTW: float

            time around twilight zones (rising and setting) in seconds.
        
        format: str
        
            date format if to read date date if type string.
        """
        date = self.read_date(date, format=format)
        isTWinfos = type(tw_infos) == dict and not False in [k in tw_infos.keys() for k in ["dist_tw_rising", "dist_tw_setting"]]
        tw_infos = self.get_twilight_infos(date=date, format=format) if not isTWinfos else tw_infos
        dist_tw_rising, dist_tw_setting = tw_infos["dist_tw_rising"], tw_infos["dist_tw_setting"]
        suncycle="night"
        if abs(dist_tw_rising) <= self.timeAroundTW:
            suncycle="rising"
        elif abs(dist_tw_setting) <= self.timeAroundTW:
            suncycle="setting"
        elif dist_tw_rising > 0 and dist_tw_setting < 0:
            suncycle="daylight"
        return suncycle

    def get_twilight_infos (self, date:datetime, format:str="%Y-%m-%d %H:%M:%S"):
        """
        Get ditance of date to twilight zones. This zone is respectively 
        between dawn/sunrise and sunset/dusk. The distance evaluated is with 
        the middle of these zones.
        
        ## Params
        
        date: datetime
        
            input date.
        
        ## Return

        tw_infos: dict

            twilight informations which contain:

                `"mid_tw_rising"`:Timestamp
                    datetime between dawn and sunrise

                `"mid_tw_setting"`:Timestamp
                    datetime between sunset and dusk

                `"dist_tw_rising"`: float   
                    distance to twilight rising (in seconds).
        
                `"dist_tw_setting"`: float 
                    distance to twilight setting (in seconds).
        """
        date = self.read_date(date, format=format)
        day_infos = self.get_day_infos(date=date, format=format)
        keys_tw = ["sunrise", "dawn", "sunset", "dusk"]
        sunrise, dawn, sunset, dusk = [day_infos[k] for k in keys_tw]
        mid_tw_rising = dawn + (sunrise - dawn)/2
        mid_tw_setting = sunset + (dusk - sunset)/2
        dist_tw_rising = date - mid_tw_rising
        dist_tw_setting = date - mid_tw_setting
        tw_infos={
            "date":date,
            # "mid_tw_rising":mid_tw_rising,
            # "mid_tw_seting":mid_tw_setting,
            "dist_tw_rising":dist_tw_rising.total_seconds(),
            "dist_tw_setting":dist_tw_setting.total_seconds()
        }
        return tw_infos

    def _run_astral_funct(self, functKey:str, date:datetime):
        """
        run sun function
        """
        funct = self.astral_functs[functKey]
        date = funct(self.obs, date, tzinfo=self.timezone)
        date = self.read_date(date=date)
        return date