import numpy as np
from Visu.radarVisu.utils import create_radar_mean_traces, create_multi_threshold_traces

def get_traces_RadarWithSTDThresholds (theta_values:np.ndarray, mean_values:np.ndarray, 
                                  std_values:np.ndarray, varname:str="descriptor", 
                                  std_th:list=[2, 3, 4], hexcolor:str="#3182bd", 
                                  hexcolor_th=['#ffeda0','#feb24c','#f03b20'],
                                  minimalValue:float=0.0, showlegend:bool=True):
    ths_upper = [mean_values+(std_values*i) for i in std_th]
    ths_lower = [mean_values-(std_values*i) for i in std_th]
    # 1) Trace mean and std areas
    mean_traces = create_radar_mean_traces(
        theta_values=theta_values,
        mean_values=mean_values,
        error_values=std_values,
        hexcolor=hexcolor,
        opacity=0.6,
        opacity_std=0.3,
        w=2,
        tracename=f"mean {varname}",
        errorname=f"std {varname}",
        minimalValue=minimalValue,
        legendgroup=varname,
        showlegend_line=showlegend,
        showlegend_error=showlegend
    )
    th_upper_traces = create_multi_threshold_traces(
        theta_values=theta_values, 
        limit_values=mean_values+std_values, 
        th_list_values=ths_upper,
        th_list_names=[f"upper std*{i} {varname}" for i in std_th],
        hexcolor_list=hexcolor_th,
        legendgroup=f"th-upper {varname}",
        minimalValue=minimalValue,
        showlegend=showlegend
    )
    th_lower_traces = create_multi_threshold_traces(
        theta_values=theta_values, 
        limit_values=mean_values-std_values, 
        th_list_values=ths_lower,
        th_list_names=[f"lower std*{i} {varname}" for i in std_th],
        hexcolor_list=hexcolor_th,
        legendgroup=f"th-lower {varname}",
        minimalValue=minimalValue,
        showlegend=showlegend
    )
    return [*th_upper_traces, *th_lower_traces, *mean_traces]