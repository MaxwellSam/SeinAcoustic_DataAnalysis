import pandas as pd

from DBBuilder.datareader.__base_datareader import Base_DataReader
from DBBuilder.util.metadata import metadata
from DBBuilder.util import clean_dataframe

class Otoriver_DataReader (Base_DataReader):

    """
    # Otoriver_DataReader

    DataReader object for otoriver data source.

    ## Description

    Object to read acoustic descriptors data specific to otoriver source file.
    
    ## How to use it

    ```python
    from DBBuilder.datareader import Otoriver_DataReader
    
    datareader = Otoriver_DataReader(timefreq="h") # for a hourly time frequency output
    df_otoriver = datareader.from_xlsx(filepath="PATH/TO/otoriver.xslx")
    ```
    """
    metadata = metadata[metadata["source"]=="otoriver"]

    kepp_in_duplicated_dates:str="max" 
    agg_options_byunit = {
        "nb/sec":"mean",
        "%":"mean",
        "db":"mean",
        "nb":"mean"
    } 

    def __init__(self, timefreq: str = "h", sep: str = ',', decimal: str = '.', colnames_var: list = None, colname_date: str = "date", dateformat: str = "%Y-%m-%d %H:%M:%S", renamecolumns: bool = True) -> None:
        super().__init__(timefreq, sep, decimal, colnames_var, colname_date, dateformat, renamecolumns)
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        metadata = self.metadata.set_index("colname")
        var_to_keep = [c for c in df.columns if c in metadata.index]
        df = df[["date", *var_to_keep]]
        # 1) Remove duplicated dates in data
        df = clean_dataframe.remove_duplicated_values(df=df, target_cols=["date"], keep=self.kepp_in_duplicated_dates)
        # 2) Aggregation per unit types => timestamp = self.timefreq 
        # df["date"] = df["date"].dt.floor(self.timefreq)
        # update agg_args for aggregation (see self.resample_with_timefreq)
        agg_args = {}
        for var in var_to_keep:
            unit = metadata.loc[var]["unit"]
            agg_method_to_use = "mean" if not unit in self.agg_options_byunit.keys() else self.agg_options_byunit[unit] 
            agg_args[var] = agg_method_to_use
        self.agg_args = agg_args 
        return df
        
            
        