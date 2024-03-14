import pandas as pd

from DBBuilder.datareader.__base_datareader import Base_DataReader

class  PhChim_continus (Base_DataReader):

    metadata = [
        {'varname': 'conductivite', 'fullname': "conductivite_continue", 'source': None, 'unit': "nb/sec"},
        {'varname': 'oxygene', 'fullname': "oxygene_continue", 'source': None, 'unit': "pct"},
        {'varname': 'ph', 'fullname': "ph_continue", 'source': None, 'unit': "nb/sec"},
        {'varname': 'phosphate', 'fullname': "phosphate_continue", 'source': None, 'unit': "pct"},
        {'varname': 'temperature', 'fullname': "temperature_continue", 'source': None, 'unit': "nb/sec"},
        {'varname': 'turbidite', 'fullname': "turbidite_continue", 'source': None, 'unit': "nb/sec"},
    ]
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df