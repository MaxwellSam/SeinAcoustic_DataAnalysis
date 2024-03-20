import pandas as pd
import plotly.express as px


# ------------------ Object ------------------ # 

class Base_DataReader ():

    """
    # Base class DataReader

    ## Description
    
    Give common features relative to data reading and preprocessing. 
    
    ## Fonctionalities

    Because data in source files can have different structure and need some 
    preprocessing to standardize it in output, this object hollow to take different
    input types to perform different task on the input data:
    - Accept csv, exel or dataframe as inputs.
    - Preprocessing to standardize data => output with specified time frequency  
    - Rename label columns according to metadata. 
    """


    metadata:pd.DataFrame=None
    option_rename_columns:bool=True
    
    # resampling variables
    interpolate_option:bool=False
    interpolation_method="linear"
    agg_args:any="mean" 

    def __init__(self, timefreq:str="h", sep:str=',', decimal:str='.', 
                 colnames_var:list=None, colname_date:str="date", 
                 dateformat:str="%Y-%m-%d %H:%M:%S", renamecolumns:bool=True) -> None:
        self.timefreq = timefreq
        self.sep = sep
        self.decimal = decimal
        self.colnames_var = colnames_var
        self.colname_date = colname_date
        self.dateformat = dateformat
        self.option_rename_columns = renamecolumns

    # ------ input methods ------ #
        
    def from_input (self, input:any):
        output = None
        if type(input) == str:
            if input.endswith(".csv"):
                output = self.from_csv(
                    filepath=input, 
                    sep=self.sep, decimal=self.decimal, 
                    colnames_var=self.colnames_var, colname_date=self.colname_date, 
                    dateformat=self.dateformat)
            elif input.endswith(".xlsx"):
                output = self.from_xslx(
                    filepath=input, 
                    colnames_var=self.colnames_var, colname_date=self.colname_date, 
                    dateformat=self.dateformat) 
            else:
                raise ValueError("Base_DataReader: filepath not valide. Be sure to use .csv or .xlsx file as input.")
        if type(input) == pd.DataFrame:
            output = self.from_dataframe(
                df=input,
                colnames_var=self.colnames_var,
                colname_date=self.colname_date,
                dateformat=self.dateformat
            )
        return output

    def from_csv (self, filepath:str, sep:str=None, decimal:str=None, 
                  colnames_var:list=None, colname_date:str=None, dateformat:str=None):
        sep = self.sep if sep == None else sep
        decimal = self.decimal if decimal == None else decimal
        df = pd.read_csv(filepath, sep=sep, decimal=decimal)
        return self.from_dataframe(df=df, colnames_var=colnames_var, colname_date=colname_date, dateformat=dateformat)
        
    def from_xslx (self, filepath:str, colnames_var:list=None, colname_date:str=None, dateformat:str=None):
        df = pd.read_excel(filepath)
        return self.from_dataframe(df=df, colnames_var=colnames_var, colname_date=colname_date, dateformat=dateformat)

    def from_dataframe (self, df:pd.DataFrame, colnames_var:list=None, colname_date:str=None, dateformat:str=None):
        colnames_var = self.colnames_var if not colnames_var else colnames_var
        colname_date = self.colname_date if not colname_date else colname_date
        df = self.prepare_datetime(df, colname_date=colname_date, dateformat=dateformat)
        if type(colnames_var) == list:
            cols_to_keep = ["date", *colnames_var]
            df = df[cols_to_keep]
        df = self.prepare_data(df)
        df = self.resample_with_timefreq(df=df)
        if self.option_rename_columns:
            df = self.rename_columns_with_metadata(df)
        return df

    # ------ preprocessinf method ----- #

    def resample_with_timefreq (self, df:pd.DataFrame, colname_date:str="date"):
        output = None
        desired_timefreq = self.timefreq
        actual_timefreq = df[colname_date].diff().min()
        resampled_data = df.set_index(colname_date).resample(desired_timefreq)
        if desiredTimeFreq_IsLower (actual_timefreq, desired_timefreq):
            if self.interpolate_option:
                output = resampled_data.interpolate(method=self.interpolation_method)
            else:
                output = resampled_data.ffill()
        else:
            output = resampled_data.agg(self.agg_args)
        output = output.reset_index()
        return output

    def prepare_data (self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Child method, not implemented in this parent class.
        """
        raise NotImplementedError("Base_DataReader: `prepare_data` not implemented in this parent class.")
    
    # ------ other ------- #

    def rename_columns_with_metadata (self, df:pd.DataFrame):
        metadata = self.metadata.set_index("colname")
        rename_columns = {}
        for i in metadata.index:
            if i in df.columns:
                varname = metadata.loc[i]["varname"]
                metadata_infos = metadata.loc[i][["type", "source", "unit"]].values.tolist()
                str_metadata_infos = ",".join([str(info) for info in metadata_infos])
                new_colname=f"{varname} [{str_metadata_infos}]"
                rename_columns[i] = new_colname
        return df.rename(columns=rename_columns)
    
    def prepare_datetime (self, df:pd.DataFrame, colname_date:str="date", dateformat:str="%Y-%m-%d %H:%M:%S"):
        if type(colname_date) == list and len(colname_date)>1:
            dates = df[colname_date].values.tolist()
            df = df.drop(columns=colname_date, axis=1)
            df.insert(0, "date", dates)
            df["date"] = df["date"].apply(lambda x : " ".join(x))
        else:
            if colname_date != "date":
                df = df.rename(columns={colname_date:"date"}) 
        if df["date"].dtype == 'object':
            df["date"] = pd.to_datetime(df["date"], format=dateformat)
        # df["date"] = df["date"].dt.floor(self.timefreq)
        return df

# ----------- methods -------------- # 

# def parse_date_infos_in_df (df:pd.DataFrame, colname_date:str="date", dateformat:str="%Y-%m-%d %H:%M:%S"):
#     if len(cols_date)>1:
#         dates = df[cols_date].values.tolist()
#         df = df.drop(columns=cols_date, axis=1)
#         df.insert(0, "date", dates)
#         df["date"] = df["date"].apply(lambda x : " ".join(x))
#     else:
#         if cols_date[0] != "date":
#             df = df.rename(columns={cols_date[0]:"date"})   
#         if type(df["date"][0]) == str:
#             df["date"] = pd.to_datetime(df["date"], format=dateformat)
#     return df
    
def desiredTimeFreq_IsLower (timedelta:pd.Timedelta, timefreq:str="h"):
    timefreq = "1"+timefreq if timefreq in ["s", "min", "h", "d"] else timefreq
    return timedelta < pd.Timedelta(timefreq)