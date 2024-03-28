import numpy as np
import pandas as pd
from Visu.radarVisu.utils import create_radar_mean_traces, create_multi_threshold_traces
import seaborn as sns

class RadarVis ():

    error_type:str=None
    groupeMeanError: bool = True,
    showlegend_line: bool = True,
    showlegend_error: bool = True
    
    def __init__ (self, name:str=None, minimalValue:float=None, 
                  hexcolor:str="#3182bd", opacity:float=0.6, 
                  showlegend_line:bool=True, showlegend_error:bool=True):
        self.name=name
        self.hexcolor=hexcolor
        self.opacity=opacity
        self.minimalValue=minimalValue
        self.showlegend_line=showlegend_line
        self.showlegend_error=showlegend_error

    def get_traces (self, theta:list, values:list, errors:list=None) -> list: 
        return create_radar_mean_traces(
            theta_values=theta,
            mean_values=values, 
            error_values=errors,
            minimalValue=self.minimalValue,
            hexcolor=self.hexcolor, 
            opacity=self.opacity, 
            tracename=self.name,
            errorname=self.error_type,
            legendgroup=self.name, 
            groupeMeanError=self.groupeMeanError,
            showlegend_line=self.showlegend_line,
            showlegend_error=self.showlegend_error
        )
    
class TemporalRadarVis (RadarVis):

    def __init__(self, name: str = None, MEANby:str="%H", error_type:str="std",
                 minimalValue: float = None, hexcolor: str = "#3182bd", 
                 opacity: float = 0.6, showlegend_line:bool=True, 
                 showlegend_error:bool=True):
        self.MEANby=MEANby
        self.error_type=error_type
        super().__init__(name, minimalValue, hexcolor, opacity, showlegend_line, showlegend_error)

    def compute_stats (self, dates:list, values:list):
        data = pd.DataFrame(dict(date=dates, value=values))
        data.date = pd.to_datetime(data.date)
        self.timeInterval = (data.date.min(), data.date.max())
        data["theta"] = data.date.dt.strftime(self.MEANby)
        stats = data.groupby("theta")["value"].agg(["mean", self.error_type]).reset_index()
        return stats
    
    def get_traces(self, dates:list, values:list) -> list:
        self.stats = self.compute_stats(dates=dates, values=values)
        self.theta = self.stats["theta"].values
        self.means = self.stats["mean"].values
        self.errors = self.stats[self.error_type].values
        return super().get_traces(
            theta=self.theta,
            values=self.means, 
            errors=self.errors
        )

class TemporalRadarVis_withErrorThresholds (TemporalRadarVis):

    seabornColorPalette_th:str="YlOrRd"
    th_ratios=[1.5, 1.5*2, 1.5*3]

    def __init__(self, name: str = None, MEANby: str = "%H", 
                 error_type: str = "std", minimalValue: float = None, 
                 hexcolor: str = "#3182bd", opacity: float = 0.6, 
                 showlegend_line: bool = True, showlegend_error: bool = True,
                 showlegend_th: bool = True):
        self.showlegend_th=showlegend_th
        super().__init__(name, MEANby, error_type, minimalValue, 
                         hexcolor, opacity, showlegend_line, showlegend_error)
        
    def compute_stats(self, dates: list, values: list):
        stats = super().compute_stats(dates, values)
        means, errors = [stats[c].values for c in ["mean", self.error_type]]
        th_data = self.compute_thresholds(means=means, errors=errors)
        stats = pd.merge(stats, th_data, left_index=True, right_index=True)
        return stats
        
    def compute_thresholds (self, means:np.ndarray, errors:np.ndarray):
        means = means
        errors = errors
        th_data = {}
        for ratio in self.th_ratios:
            errorname = f"{self.error_type}*{ratio}_th" 
            # upper threshold
            th_upper=means+(errors*ratio) 
            th_data[f"{errorname}_upper"]=th_upper
            # lower threshold
            th_lower=means-(errors*ratio) 
            th_data[f"{errorname}_lower"]=th_lower
        return pd.DataFrame(th_data)
    
    def get_threshold_traces (self, stats:pd.DataFrame):
        colname_ths_upper = [c for c in stats.columns if c.endswith("th_upper")]
        colname_ths_lower = [c for c in stats.columns if c.endswith("th_lower")]
        th_upper_series = [stats[c].values for c in colname_ths_upper]
        th_lower_series = [stats[c].values for c in colname_ths_lower]
        colors = sns.color_palette(
            palette=self.seabornColorPalette_th, 
            n_colors=len(self.th_ratios)).as_hex() 
        
        th_upper_traces = create_multi_threshold_traces(
            theta_values=self.theta, 
            limit_values=self.means+self.errors, 
            th_list_values=th_upper_series,
            th_list_names=colname_ths_upper,
            hexcolor_list=colors,
            legendgroup=f"th-upper {self.name}",
            minimalValue=self.minimalValue,
            showlegend=self.showlegend_th
        )
        th_lower_traces = create_multi_threshold_traces(
            theta_values=self.theta, 
            limit_values=self.means-self.errors, 
            th_list_values=th_lower_series,
            th_list_names=colname_ths_lower,
            hexcolor_list=colors,
            legendgroup=f"th-lower {self.name}",
            minimalValue=self.minimalValue,
            showlegend=self.showlegend_th
        )
        return [*th_upper_traces, *th_lower_traces]
    
    def get_traces(self, dates: list, values: list) -> list:
        mean_traces = super().get_traces(dates, values)
        th_traces = self.get_threshold_traces(stats=self.stats)
        return [*th_traces, *mean_traces]