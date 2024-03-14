import pandas as pd
import os

metadata_files = [
    "metadata_acoustic.xlsx", 
    "metadata_meteo.xlsx", 
    "metadata_phch_continue.xlsx"
    ]

def build_metadata (metadata_files:list):
    dfs = []
    for file in metadata_files:
        filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", file)
        df = pd.read_excel(filepath)
        dfs.append(df)
    return pd.concat(dfs)

metadata = build_metadata(metadata_files)