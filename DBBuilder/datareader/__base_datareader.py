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
    - Parse date informations in data to standardize date info in one colone "date" as datetime type.
    - Rename label columns according to metadata. 

    In child class

    ## Exemple   

    """
    metadata:pd.DataFrame=None
    option_rename_columns:bool=True

    def __init__(self, timefreq:str="h") -> None:
        self.timefreq = timefreq

    # ------ input methods ------ #

    def from_csv (self, filepath:str, sep:str=',', decimal:str='.', 
                  cols_label:list=None, cols_date:list=["date"], dateformat:str="%Y-%m-%d %H:%M:%S"):
        df = pd.read_csv(filepath, sep=sep, decimal=decimal)
        return self.from_dataframe(df=df, cols_label=cols_label, cols_date=cols_date, dateformat=dateformat)
        
    def from_xslx (self, filepath:str, cols_label:list=None, cols_date:list=["date"], dateformat:str="%Y-%m-%d %H:%M:%S"):
        df = pd.read_excel(filepath)
        return self.from_dataframe(df=df, cols_label=cols_label, cols_date=cols_date, dateformat=dateformat)

    def from_dataframe (self, df:pd.DataFrame, cols_label:list=None, cols_date:list=["date"], dateformat:str="%Y-%m-%d %H:%M:%S"):
        if type(cols_label) == list:
            cols_to_keep = [*cols_date, *cols_label]
            df = df[cols_to_keep]
        df = self.prepare_datetime(df, cols_date=cols_date, dateformat=dateformat)
        df = self.prepare_data(df)
        if self.option_rename_columns:
            df = self.rename_columns_with_metadata(df)
        return df

    # ------ preprocessinf method ----- #

    def prepare_data (self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Child method, not implemented in this parent class.
        """
        raise NotImplementedError("Base_DataReader: `prepare_data` not implemented in this parent class.")
    
    # ------ other ------- #

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
        return df.rename(columns=rename_columns)
    
    def prepare_datetime (self, df:pd.DataFrame, cols_date:list=["date"], dateformat:str="%Y-%m-%d %H:%M:%S"):
        if len(cols_date)>1:
            dates = df[cols_date].values.tolist()
            df = df.drop(columns=cols_date, axis=1)
            df.insert(0, "date", dates)
            df["date"] = df["date"].apply(lambda x : " ".join(x))
            dateformat = " ".join(dateformat)
        else:
            colname_date = cols_date[0]
            if colname_date != "date":
                df = df.rename(columns={cols_date[0]:"date"}) 
        if df["date"].dtype == 'object':
            df["date"] = pd.to_datetime(df["date"], format=dateformat)
        df["date"] = df["date"].dt.floor(self.timefreq)
        return df

# ----------- methods -------------- # 

def parse_date_infos_in_df (df:pd.DataFrame, cols_date:list=["date"], dateformat:str="%Y-%m-%d %H:%M:%S"):
    if len(cols_date)>1:
        dates = df[cols_date].values.tolist()
        df = df.drop(columns=cols_date, axis=1)
        df.insert(0, "date", dates)
        df["date"] = df["date"].apply(lambda x : " ".join(x))
    else:
        if cols_date[0] != "date":
            df = df.rename(columns={cols_date[0]:"date"})   
        if type(df["date"][0]) == str:
            df["date"] = pd.to_datetime(df["date"], format=dateformat)
    return df