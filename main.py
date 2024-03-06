from DBBuilder import DBBuilder
import glob
import pandas as pd
from  tqdm import tqdm
import os

# Variables

city_name = "Bougival"
lat, long, elev = 48.865, 2.144, 23
timezone="UTC"

input_path = "./data/bougival/acoustique/acoustique SENSEA/yolo/"
output_path = "./data/bougival/database/"
db_filename = f"{city_name}_database"
date_format = "%Y-%m-%d %H:%M:%S"


# Program

def main ():
    # DBBuilder initialisation
    dbbuilder = DBBuilder(latitude=lat, longitude=long, elevation=elev, timezone=timezone)
    # Get csv files in input_path wich contain accoustic labels occurence
    files = glob.glob(input_path+"*.csv", recursive=True)
    # Concat all files in a single df
    dfs_db = []
    for file in tqdm(files):
        df = pd.read_csv(file)
        dfs_db.append(df)
    db = pd.concat(dfs_db)
    db = db.sort_values(by="date")
    # Generate database from labels occurence data
    db = dbbuilder.run(dates=db.date, labels=db.label)
    # convert datetime to string
    date_columns = [col for col in db.columns if pd.api.types.is_datetime64_any_dtype(db[col])]
    for col in date_columns:
        db[col] = db[col].dt.strftime(date_format)
    # Save database
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    db.to_csv(os.path.join(output_path, db_filename+".csv"), index=False)
    db.to_excel(os.path.join(output_path, db_filename+".xlsx"))

# Exec

main()


