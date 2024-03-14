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
    agg_options = {
        "nb/sec":"mean",
        "%":"mean",
        "db":"mean",
        "nb":"mean"
    } 
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        metadata = self.metadata.set_index("varname")
        # 1) Remove duplicated dates in data
        df = clean_dataframe.remove_duplicated_values(df=df, target_cols=["date"], keep=self.kepp_in_duplicated_dates)
        # 2) Aggregation per unit types => timestamp = self.timefreq 
        df["date"] = df["date"].dt.floor(self.timefreq)
        final_df = None
        for unit in metadata["unit"].unique():
            var_unit = [i for i in metadata[metadata['unit'] == unit].index.values.tolist() if i in df.columns]
            df_unit = df[["date", *var_unit]]
            agg_option = self.agg_options[unit]
            df_unit = df_unit.groupby("date").agg(agg_option).reset_index()
            if type(final_df) == type(None):
                final_df = df_unit
            else:
                final_df = pd.merge(final_df, df_unit, on="date", how="outer")
        return final_df
        
            
        