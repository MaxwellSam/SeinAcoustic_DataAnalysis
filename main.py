from DBBuilder import DBBuilder
import glob
import pandas as pd
from  tqdm import tqdm
import os
from IPython.display import display
# Variables

city_name = "Bougival"
lat, long, elev = 48.865, 2.144, 23
timezone="UTC"

filepath_otoriver = "data/Data_SAM/Bougival/input/acoustique/otoriver/otoriver_2021-07-06_2023-12-08.xlsx" 
filepath_sensea = "data/Data_SAM/Bougival/input/acoustique/sensea/sensea_2021-06-16_2023-11-21.csv"

filepath_output = "data/Data_SAM/Bougival/database.xlsx"

# Program

dbbuilder = DBBuilder(input_isHourly=True, output_asdataframe=True)
output = dbbuilder.build_from_seinAcousticSourceFiles(acoustic_sensea=filepath_sensea, acoustic_otoriver=filepath_otoriver)
dbbuilder.export_to_xlsx(filepath=filepath_output)




