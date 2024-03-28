import numpy as np
import pandas as pd
import plotly.graph_objs as go

from Visu.radarVisu import TemporalRadarVis_withErrorThresholds, TemporalRadarVis


class TemporalAnalysis ():

    radarVis:TemporalRadarVis=TemporalRadarVis_withErrorThresholds()

    def __init__(self, dates:np.ndarray, values:np.ndarray, 
                 GRPper:str="%Y%U", roundEvery:str=None, name:str=None, 
                 dateformat:str='%Y-%m-%d %H:%M:%S', makeVis:bool=True,
                 hexcolor:str="#3182bd", 
                 radarVis:TemporalRadarVis=None) -> None:
        # Optionsdf
        self.makeVis=makeVis
        self.GRPper=GRPper
        self.roundEvery=roundEvery
        self.name=name 
        self.hexcolor=hexcolor
        # Visualizer
        self.radarVis = radarVis if radarVis else self.radarVis
        self.radarVis.name=name 
        self.radarVis.hexcolor=hexcolor
        # Prepare base dataframe
        self.data=pd.DataFrame({"date":dates, "values":values}).dropna()
        self.data.date=pd.to_datetime(self.data.date, format=dateformat)
        if roundEvery :
            self.data.date = self.data.date.dt.round(roundEvery)
        self.date_min, self.date_max = self.data.date.min(), self.data.date.max() 
        
    def get_visu (self, GRPper:str="%Y%U"):
        data = self.data
        data["GRP"] = data["date"].dt.strftime(GRPper)
        grp_unique = data["GRP"].unique()
        records = []
        for grp in grp_unique:
            data_selection = data[(data.GRP == grp)]
            date_min = data_selection.date.min()
            date_max = data_selection.date.max()
            # 1) Radar Visu
            radarFig = go.Figure(
                self.radarVis.get_traces(
                    dates=data_selection["date"].values,
                    values=data_selection["values"].values
                )
            )
            records.append(
                {"date_min":date_min,
                 "date_max":date_max,
                 "radarVis":radarFig})
        return pd.DataFrame(records)