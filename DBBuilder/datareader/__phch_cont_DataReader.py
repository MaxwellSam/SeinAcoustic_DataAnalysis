import pandas as pd

from DBBuilder.datareader.__base_datareader import Base_DataReader
from DBBuilder.util.metadata import metadata
from DBBuilder.util import clean_dataframe

class PhCh_Continus_DataReader (Base_DataReader):

    """
    # PhCh_Continus_DataReader

    DataReader Object to read continus physico-chemical data. 

    # Input data structure
    """
    
    kepp_in_duplicated_dates:str="max" 
    metadata = metadata[metadata["source"] == "phch_continue"]
    interpolate_option=True
    timefreq_input:str="15min"
    

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = df["date"].dt.round(self.timefreq_input)
        df = clean_dataframe.remove_duplicated_values(df=df, target_cols=["date"], keep="max")
        return df