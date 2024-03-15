import pandas as pd

from DBBuilder.datareader.__base_datareader import Base_DataReader
from DBBuilder.util.metadata import metadata

class PhCh_Continus_DataReader (Base_DataReader):

    """
    # PhCh_Continus_DataReader

    DataReader Object to read continus physico-chemical data. 

    # Input data structure
    """

    metadata = metadata[metadata["source"] == "phch_continue"]

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df