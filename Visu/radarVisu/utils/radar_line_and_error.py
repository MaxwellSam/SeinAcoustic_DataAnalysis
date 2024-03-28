from Visu.radar_plot.create_traces import create_radar_line

def get_radar_traces (theta_values:list, mean_values:list,
                      error_values:str=None, threshold_values:str=None, 
                      hexcolor:str="#3182bd", hexcolor_th:str="#d73027", 
                      opacity=0.6, opacity_std=0.3, opacity_th=0.6, w=2,
                      tracename:str="mean", errorname:str="error", thname:str="threshold", 
                      minimalValue:bool=True, legendgroup:str=None, grpErrorWith:bool=False,
                      showlegend_line:bool=True, showlegend_error:bool=True):
    traces_container = []
    # 1) Mean trace
    traces_container += create_radar_line(
        theta_values=theta_values, 
        line_values=mean_values,
        name=tracename,
        hexcolor=hexcolor,
        line_opacity=opacity,
        lines_width=w,
        legendgroup=legendgroup,
        showlegend=showlegend_line
        )
    # 2.2) Error traces
    error_traces = []
    if type(error_values) != type(None):
        error_min = mean_values - error_values
        if type(minimalValue) != type(None):
            error_min[error_min<minimalValue] = minimalValue
        error_max = mean_values + error_values
        if legendgroup:
            legendgroup_error = f"error-{legendgroup}" if not grpErrorWith else legendgroup
        else:
            legendgroup_error = legendgroup
        traces_container += create_radar_line(
            theta_values=theta_values,
            line_values=error_min,
            fill_values=mean_values,
            name=f"{errorname} lower - {tracename}",
            hexcolor=hexcolor,
            line_opacity=opacity_std,
            lines_width=w,
            fill_opacity=opacity_std,
            legendgroup=legendgroup_error,
            showlegend=showlegend_error
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
            legendgroup=legendgroup_error,
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
    return traces_container