import pandas as pd

from DBBuilder.datareader.__base_datareader import Base_DataReader
from DBBuilder.util.metadata import metadata

class Sensea_DataReader (Base_DataReader):

    metadata = metadata[metadata["source"] == "sensea"]

    def from_csv(self, filepath: str, sep: str = ',', decimal: str = '.', cols_label: list = ["label"], cols_date: list = ["date"], dateformat: list = ["%Y-%m-%d %H:%M:%S"]):
        return super().from_csv(filepath, sep, decimal, cols_label, cols_date, dateformat)
    
    def from_xslx(self, filepath: str, cols_label: list = ["label"], cols_date: str = ["date"], dateformat: list = ["%Y-%m-%d %H:%M:%S"]):
        return super().from_xslx(filepath, cols_label, cols_date, dateformat)
    
    def from_dataframe(self, df: pd.DataFrame, cols_label: list = ["label"], cols_date: str = ["date"], dateformat: list = ["%Y-%m-%d %H:%M:%S"]):
        return super().from_dataframe(df, cols_label, cols_date, dateformat)
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = df["date"].dt.floor(self.timefreq)
        df_grouped = df.groupby(['date', 'label']).size().reset_index(name='count')
        df_count = df_grouped.pivot_table(index='date', columns='label', values='count', fill_value=0)
        df_count = df_count.reset_index(names=["date"])
        return df_count