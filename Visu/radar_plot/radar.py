import pandas as pd
import seaborn as sns
import plotly.graph_objs as go
from PIL import ImageColor
import numpy as np


def get_radar_traces (theta_values:list, mean_values:list,
                      error_values:str=None, threshold_values:str=None, 
                      hexcolor:str="#3182bd", hexcolor_th:str="#d73027", 
                      opacity=0.6, opacity_std=0.3, opacity_th=0.6, w=2,
                      tracename:str="mean", errorname:str="error", thname:str="threshold", 
                      minimalValue:bool=True):
    traces_container = []
    # 1) Mean trace
    traces_mean = create_radar_line(
        theta_values=theta_values, 
        line_values=mean_values,
        name=tracename,
        hexcolor=hexcolor,
        line_opacity=opacity,
        lines_width=w,
        legendgroup=tracename
        )
    # 2.2) Error traces
    if type(error_values) != type(None):
        error_min = mean_values - error_values
        if type(minimalValue) != type(None):
            error_min[error_min<minimalValue] = minimalValue
        error_max = mean_values + error_values
        traces_container += create_radar_line(
            theta_values=theta_values,
            line_values=error_min,
            fill_values=mean_values,
            name=f"{errorname} lower - {tracename}",
            hexcolor=hexcolor,
            line_opacity=opacity_std,
            lines_width=w,
            fill_opacity=opacity_std,
            legendgroup=tracename,
            showlegend=True
        )
        traces_container += create_radar_line(
            theta_values=theta_values,
            line_values=error_max,
            fill_values=mean_values,
            name=f"{errorname} upper - {tracename}",
            hexcolor=hexcolor,
            line_opacity=opacity_std,
            lines_width=w,
            fill_opacity=opacity_std,
            legendgroup=tracename,
            showlegend=True,
        )
    # 2.3) Threshold trace
    if type(threshold_values)!=type(None):
        traces_container += create_radar_line(
            theta_values=theta_values,
            line_values=threshold_values,
            fill_values=None,
            name=f"{thname} - {tracename}",
            hexcolor=hexcolor_th,
            line_opacity=opacity_th,
            lines_width=w,
            dash="dot",
            fill_opacity=opacity_th,
            legendgroup=tracename,
            showlegend=True
        )
    # 3) Order traces
    traces_container += traces_mean
    return traces_container

def create_radar_line (theta_values:list, line_values:list, name:str="trace", 
                       mode:str="lines", hexcolor:str="#3182bd", 
                       lines_width:int=1, line_opacity:float=0.6, dash:str=None,
                       fill_values:list=None, hexcolor_fill:str=None, fill_opacity:int=None, 
                       legendgroup:str=None, showlegend=True, **kargs):
    traces_container = []
    ## Setup line variables: 
    theta_values = np.append(theta_values, theta_values[0])
    line_values = np.append(line_values, line_values[0])
    color_rgb = ImageColor.getcolor(hexcolor, mode="RGB")
    color_rgba = (*color_rgb, line_opacity)
    ## Make trace
    traces_container.append(go.Scatterpolar(
            r=line_values,
            theta=theta_values,
            mode=mode,
            line=dict(
                color=f"rgba{color_rgba}", 
                width=lines_width,
                dash=dash),
            name=name,
            legendgroup=legendgroup,
            showlegend=showlegend,
            **kargs
        ))
    if type(fill_values)!=type(None):
        ## Setup fill trace variables
        fill_values = np.append(fill_values, fill_values[0])
        color_rgb_fill = ImageColor.getcolor(hexcolor_fill, mode="RGB") if hexcolor_fill else color_rgb
        fill_opacity = fill_opacity if fill_opacity else (line_opacity/2)
        color_rgba_fill = (*color_rgb_fill, fill_opacity)
        traces_container.append(go.Scatterpolar(
            r=fill_values,
            theta=theta_values,
            mode=mode,
            line=dict(
                color=f"rgba{color_rgba_fill}", 
                width=0),
            fill='tonext',
            fillcolor=f"rgba{color_rgba_fill}",
            name=f"area {name}",
            legendgroup=legendgroup,
            showlegend=False
        ))
    return traces_container

def create_multi_threshold_traces (theta_values:list, limit_values:list, 
                                   th_list_values:list, th_list_names:list=None, 
                                   hexcolor_list:list=None, line_opacity:float=0.6, dash:str="dot",
                                   fill_option:bool=True, fill_opacity:int=0.3, 
                                   legendgroup:str=None, showlegend=True, 
                                   default_color_palette:str="hls"):
    traces_container = []
    # Setup variables
    hexcolor_list = sns.color_palette(
        palette=default_color_palette, 
        n_colors=len(th_list_values)
        ) if type(hexcolor_list)==None else hexcolor_list
    th_list_names = [
        f"threshold lev.{i}" 
        for i in range(1, len(th_list_values)+1)
        ] if type(th_list_names)==None else th_list_names

    for i in range(len(th_list_values)):
        th_values = th_list_values[i]
        if i == 0:
            traces_container += create_radar_line(
                theta_values=theta_values,
                line_values=th_values, 
                hexcolor=hexcolor_list[i], 
                name=th_list_names[i],
                dash=dash,
                line_opacity=line_opacity, 
                fill_values=limit_values if fill_option else None,
                fill_opacity=fill_opacity,
                legendgroup=legendgroup, 
                showlegend=showlegend
            )
        else:
            traces_container += create_radar_line(
                theta_values=theta_values,
                line_values=th_values, 
                hexcolor=hexcolor_list[i], 
                name=th_list_names[i],
                dash=dash,
                line_opacity=line_opacity, 
                fill_values=th_list_values[i-1] if fill_option else None,
                fill_opacity=fill_opacity,
                legendgroup=legendgroup, 
                showlegend=showlegend
            )
    return traces_container
    