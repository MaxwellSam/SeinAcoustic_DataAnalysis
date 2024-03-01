from astral import Observer, moon
from DBBuilder.astral.__base_astral import BaseAstral
import datetime

class Moon (BaseAstral):

    astral_functs={
        "moon_phase":moon.phase
    }

    def __init__(self, latitude: float = 48.886, longitude: float = 2.333, elevation: float = 35, timezone: str = "UTC", **kargs) -> None:
        super().__init__(latitude, longitude, elevation, timezone, **kargs)

    def get_infos(self, date, format:str="%Y-%m-%d %H:%M:%S"):
        date = self.read_date(date, format=format)
        day_infos = self.get_day_infos(date, format=format)
        moon_infos = {
            "date":date,
            **day_infos
        }
        del moon_infos["day"]
        return moon_infos

    def _run_astral_funct(self, functKey:str, date:datetime.datetime):
        """
        run moon function
        """
        funct = self.astral_functs[functKey]
        if functKey == "moon_phase":
            return funct(date)
        else:
            return funct(date, tzinfo=self.timezone)


