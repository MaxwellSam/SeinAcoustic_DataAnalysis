import pandas as pd

from DBBuilder.datareader.__base_datareader import Base_DataReader
from DBBuilder.util.metadata import metadata

class Sensea_DataReader (Base_DataReader):

    source_name:str = "sensea"
    metadata = metadata[metadata["source"] == "sensea"]

    def __init__(self, timefreq: str = "h", sep: str = ',', decimal: str = '.', colnames_var: list = ["label"], colname_date: str = "date", dateformat: str = "%Y-%m-%d %H:%M:%S", renamecolumns:bool=True) -> None:
        super().__init__(timefreq, sep, decimal, colnames_var, colname_date, dateformat, renamecolumns)
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = df["date"].dt.floor(self.timefreq)
        df_grouped = df.groupby(['date', 'label']).size().reset_index(name='count')
        df_count = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        df_count = df_count.reset_index(names=["date"])
        return df_count