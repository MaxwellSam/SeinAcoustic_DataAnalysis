"""
file: dbbuilder.py
description: dbbuilder object to construct dataset for time series detections data.
author: Sam Maxwell
date: 2024
"""

# ------ python packages ------- # 
import numpy as np
import pandas as pd
from dateutil import tz
from IPython.display import display
# ------ DBBuilder imports ------ # 
from DBBuilder.__datereader import DateReader
from DBBuilder import Sun, Moon
from DBBuilder.meteo import OpenMeteo
from DBBuilder.datareader import Otoriver_DataReader, Sensea_DataReader, PhCh_Continus_DataReader
from DBBuilder.datareader.__base_datareader import Base_DataReader
from DBBuilder.util.datetime import convert_all_dtcolumns_to_str

from DBBuilder.util.metadata import metadata

class DBBuilder (DateReader):

    """
    # DBBuilder

    Python object for database generation from labels descriptor_infos to organise and complete time series data by :
    1) Organizing labels descriptor_infos by `timefreq` (default count by minutes)
    2) Find astral informations about sun (suncycle) and moon (phase) 
    3) Find meteorological informations (hourly) 

    ## How to use it
    
    ### 1) Generate database

    # #### From labels count

    ```python
        df = pd.read_csv("PATH/TO/descriptor_infos/OCCURENCE/file.csv")
        print(df)
        
        #     date                          label_0   ...  label_10  
        # 0     2022-05-11 00:06:00+00:00      5.0    ...      0.0   
        # 1     2022-05-11 00:07:00+00:00      0.0    ...      0.0     
        # ...                         ...      ...    ...      ...       
        # 9551  2022-06-09 10:37:00+00:00      0.0    ...      2.0      
        # 9552  2022-06-09 10:38:00+00:00      1.0    ...      0.0

        # 1) dbbuilder object initialisation
        dbbuilder = DBBuilder(latitude=lat, longitude=long, elevation=elev)
        # 2) get acoustic data (with label occurences)
        dfs = [pd.read_csv(file)[["date", "label"]] for file in files_sensea_yolo[:1]]
        df = pd.concat(dfs)
        # 3) use dbbuilder to create database
        output = dbbuilder.from_labels_count(df=df, colnames_label=[c for c in df.columns if c.startswith("label_")])
    ```
    Sam MAXWELL - 2024
    """

    input_data:any=None
    input_timefreq:str="15min"

    data:pd.DataFrame=None
    hourly_data:pd.DataFrame=None
    daily_data:pd.DataFrame=None
    
    agg_param="mean"
    metadata:pd.DataFrame=metadata

    ## Output
    output_renamecolumns:bool=None
    output_asdataframe:bool=None
    roundValuesAt:int=3
    orient:str="records"
    output_dateformat = "%Y-%m-%d %H:%M%:%S"
    output_dateformat_daily = "%Y-%m-%d"

    def __init__(self, latitude:float=48.886, longitude:float=2.333, elevation:float=35, 
                 timezone:str="UTC", colname_date:str="date", input_timefreq:str="15min",
                 dateformat:str="%Y-%m-%d %H:%M:%S", sep:str=",", decimal:str=".", 
                 output_renamecolumns:bool=True, output_asdataframe:bool=False, 
                 **kargs) -> None:
        # --- Objects initialisation --- #
        ## Astral objects
        self.sun = Sun(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, timefreq=self.input_timefreq, **kargs)
        self.moon = Moon(latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone, timefreq=self.input_timefreq, **kargs)
        ## Meteo object
        self.meteo = OpenMeteo(latitude=latitude, longitude=longitude, timezone=timezone)
        # --- Variables --- #
        self.latitude, self.longitude, self.elevation = latitude, longitude, elevation # site localization
        self.sep, self.decimal=sep, decimal # csv file informations (case input is csv)
        self.colname_date = colname_date # colname for date informations in input data
        self.dateformat = dateformat # dateformat information in input data
        # --- Options --- # 
        self.input_timefreq = input_timefreq
        self.output_renamecolumns = output_renamecolumns
        self.output_asdataframe = output_asdataframe
        # DataReaders
        self.sensea_datareader = Sensea_DataReader(timefreq=self.input_timefreq, colname_date=colname_date, dateformat=dateformat, renamecolumns=self.output_renamecolumns)
        self.otoriver_datareader = Otoriver_DataReader(timefreq=self.input_timefreq, colname_date=colname_date, dateformat=dateformat, renamecolumns=self.output_renamecolumns)
        self.phch_h_datareader = PhCh_Continus_DataReader(timefreq=self.input_timefreq, colname_date=colname_date, dateformat=dateformat, renamecolumns=self.output_renamecolumns) 
        super().__init__(timezone=timezone)
    
    # ---- input functions ---- #
        
    def clear (self):
        for k in ["data", "hourly_data", "daily_data"]:
            del self.__dict__[k]
            self.__dict__[k] = None

    # ---- build function ---- #
    
    def read_input(self, input:any):    
        df = None
        if type(input) == str:
            if input.endswith(".csv"):
                df = pd.read_csv(input, sep=self.sep, decimal=self.decimal)
            elif input.endswith(".xlsx"):
                df = pd.read_excel(input)
            else:
                raise ValueError("DBBuilder: filepath not valide. Be sure to use .csv or .xlsx file as input.")
        elif type(input) == pd.DataFrame:
            df = input
        else:
            raise ValueError("DBBuilder: Bad input type. Be sure to use filepaht (.csv or .xlsx) or dataframe.")
        return df
    
    def build_from_seinAcousticSourceFiles (self, acoustic_sensea:any=None, acoustic_otoriver:any=None, phch_hourly:any=None, phch_hebdo:any=None, timefreq:str=None):
        input_dfs = []
        # 1) read input data
        self.input_timefreq = self.input_timefreq if timefreq == None else timefreq
        if type(acoustic_sensea) != type(None):
            self.sensea_datareader.timefreq = self.input_timefreq
            acoustic_sensea = self.sensea_datareader.from_input(input=acoustic_sensea)
            input_dfs.append(acoustic_sensea)
        if type(acoustic_otoriver) != type(None):
            acoustic_otoriver = self.otoriver_datareader.from_input(input=acoustic_otoriver)
            input_dfs.append(acoustic_otoriver)
        if len(input_dfs) >= 1:
            if type(phch_hourly) != type(None):
                phch_hourly = self.phch_h_datareader.from_input(input=phch_hourly)
                input_dfs.append(phch_hourly)
            # 2) merge input data
            input_data = None
            for df in input_dfs:
                if type(input_data) == type(None):
                    input_data = df
                else:
                    input_data = pd.merge(input_data, df, on="date", how="outer")
            # 3) build dataset
            output = self.build(input=input_data)
            del input_data, input_dfs, acoustic_sensea, acoustic_otoriver, phch_hourly
            return output
        else:
            raise ValueError("DBBuilder: No acoustic data in inputs.")
        
    def build (self, input:any, colname_date:str=None, dateformat:str=None, input_timefreq:str=None):
        """
        Create data collection with following informations : suncycle informations, hourly meteo, daily astral informations.
        """
        self.input_timefreq = input_timefreq if input_timefreq != None else self.input_timefreq
        # Agg Data
        self.hourly_data = pd.DataFrame()
        self.daily_data = pd.DataFrame()
        # Input data
        df_input = self.read_input(input=input)
        colname_date = colname_date if colname_date != None else self.colname_date
        dateformat = dateformat if dateformat != None else self.dateformat
        if colname_date != "date":
            df_input.rename(columns={colname_date:"date"})
        df_input.date = df_input.date.apply(lambda x: self.read_date(x, dateformat))
        self.numerical_cols = df_input.select_dtypes(include=['number']).columns.tolist()
        # Date series
        date_min, date_max = df_input.date.min(), df_input.date.max()
        self.hourly_data["date"] = pd.date_range(start=date_min.floor("h"), end=date_max.floor("h"), freq="h").to_list()
        self.daily_data["date"] = pd.date_range(start=date_min.floor("d"), end=date_max.floor("d"), freq="d").to_list()
        # Generate data
        sun_infos = pd.DataFrame(df_input.date.apply(self.sun.get_infos).values.tolist())
        self.data = pd.merge(sun_infos, df_input, on="date")
        ### 1) Hourly data
        self.__generate_hourly_data()
        ### 2) Daily data
        self.__generate_daily_data()
        output = self.__generate_output()
        return output
    
    def __generate_hourly_data (self):
        ## Input data
        data_h = self.data.copy()
        final_data_h = self.hourly_data.copy()
        numerical_cols = data_h.select_dtypes(include=['number']).columns.tolist()
        ## 1) Add astral informations (sun)
        # sun_infos_h = pd.DataFrame(final_data_h.date.apply(self.sun.get_infos).values.tolist())
        # final_data_h = pd.merge(final_data_h, sun_infos_h, on="date", how="left")
        meteo_infos_h = self.meteo.get_meteo(date_start=data_h.date.min(), date_end=data_h.date.max())
        self.meteo_cols = meteo_infos_h.select_dtypes(include=['number']).columns.tolist()
        final_data_h = pd.merge(final_data_h, meteo_infos_h, on="date", how="left")
        if self.input_timefreq != "h":
            #### 2) Agg input data (numerical value) hourly
            data_h["date_h"] = data_h.date.dt.floor("h")
            min_max_date = data_h.groupby(["date_h", "suncycle_day", "suncycle_type"])["date"].agg(["min", "max"]).add_prefix("date_agg_").reset_index()
            data_h = data_h.groupby(["date_h", "suncycle_day", "suncycle_type"])[numerical_cols].agg(self.agg_param).reset_index()
            data_h.columns = join_multicolumns_level(columns=data_h.columns)
            data_h = pd.merge(min_max_date, data_h, on=["date_h", "suncycle_day", "suncycle_type"]).rename(columns={"date_h":"date"})
            del min_max_date
        else:
            data_h = data_h[["date", "suncycle_day", "suncycle_type", *numerical_cols]]
        final_data_h = pd.merge(final_data_h, data_h, on="date", how="outer")
        final_data_h = final_data_h.round(self.roundValuesAt)
        self.hourly_data = final_data_h.copy()
        ## Delete un-used dataframes
        del data_h, final_data_h, meteo_infos_h
        return self.hourly_data
    
    def __generate_daily_data (self):
        ## Input data
        data_d = self.hourly_data.copy()
        final_data_d = self.daily_data.copy()
        cols_to_agg = [*self.numerical_cols, *self.meteo_cols]
        #### add astral informations (sun and moon)
        sun_infos_d = pd.DataFrame(final_data_d.date.apply(self.sun.get_day_infos).values.tolist()).rename(columns={"day":"date"})
        final_data_d = pd.merge(final_data_d, sun_infos_d, on="date", how="left")
        moon_infos_d = pd.DataFrame(final_data_d.date.apply(self.moon.get_day_infos).values.tolist()).rename(columns={"day":"date"})
        final_data_d = pd.merge(final_data_d, moon_infos_d, on="date", how="left")
        #### agg input data (numerical values) by suncycle type and suncycle days
        data_d["date"] = data_d["suncycle_day"]
        data_d_gby = data_d.groupby(["date", "suncycle_type"])[cols_to_agg].agg(self.agg_param).reset_index()
        data_d_all = data_d.groupby(["date"])[cols_to_agg].agg(self.agg_param).reset_index()
        data_d_all["suncycle_type"]="all"
        data_d_all = data_d_all[data_d_gby.columns.tolist()]
        data_daily = pd.DataFrame([*data_d_gby.to_dict(orient="records"), *data_d_all.to_dict(orient="records")])
        data_daily.columns = join_multicolumns_level(data_daily.columns)
        final_data_d = pd.merge(data_daily, final_data_d, on="date", how="outer").sort_values(by=["date", "suncycle_type"])
        final_data_d = final_data_d.round(self.roundValuesAt)
        self.daily_data = final_data_d.copy()
        del data_d, data_d_gby, data_d_all, sun_infos_d, moon_infos_d, final_data_d
        return self.daily_data
    
    def __generate_output(self):
        output={
            "data":{
                "data":self.data.copy(),
                "hourly_data":self.hourly_data.copy(),
                "daily_data":self.daily_data.copy()
            },
            "infos":{
                "latitude":self.latitude,
                "longitude":self.longitude,
                "elevation":self.elevation,
                "timezone":self.timezone
            }
        }
        for k in output["data"].keys():
            df = output["data"][k]
            if self.rename_columns_with_metadata:
                df = self.rename_columns_with_metadata(df)
            if k == "daily_data":
                df["date"] = df["date"].dt.strftime(self.output_dateformat_daily)
            df = convert_all_dtcolumns_to_str(df, format=self.output_dateformat)
            if not self.output_asdataframe:
                df = df.to_dict(orient=self.orient)
            output["data"][k]=df
        output["metadata"] = self.metadata if self.output_asdataframe else self.metadata.to_dict(self.orient)
        self.output = output
        return output
    
    def export_to_xlsx (self, filepath:str):
        writer = pd.ExcelWriter(filepath)
        for k, data in self.output["data"].items():
            if not type(data) == pd.DataFrame:
                data = pd.DataFrame(data)
            data.to_excel(writer, sheet_name=k, index=False)
        infos_df = pd.DataFrame({"info":self.output["infos"].keys(), "value":self.output["infos"].values()})
        infos_df.to_excel(writer, sheet_name="infos", index=False)
        self.metadata.to_excel(writer, sheet_name="metadata", index=False)
        writer.close()

    
    def rename_columns_with_metadata (self, df:pd.DataFrame):
        metadata = pd.DataFrame(self.metadata).set_index("colname")
        rename_columns = {}
        for i in metadata.index:
            if i in df.columns:
                varname = metadata.loc[i]["varname"]
                metadata_infos = metadata.loc[i][["type", "source", "unit"]].values.tolist()
                str_metadata_infos = ",".join([str(info) for info in metadata_infos])
                new_colname=f"{varname} [{str_metadata_infos}]"
                rename_columns[i] = new_colname
        self.metadata = metadata.reset_index()
        return df.rename(columns=rename_columns)

def join_multicolumns_level (columns:list, sep:str=" "):
    new_columns = []
    for c in columns:
        if type(c) in (tuple, list):
            v_to_join = [str(v) for v in c if v != '']
            new_c = sep.join(v_to_join)
            new_columns.append(new_c)
        else:
            new_columns.append(c)
    return new_columns

