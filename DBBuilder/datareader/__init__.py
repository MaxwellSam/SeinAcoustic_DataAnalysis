"""
# DataReader package

Usefull object for specific data reading and pre-processing.

## Description

DataReader objects are used to read specific (acoustic descriptors, physico-chemical data, etc) data 
with pre-processing to generate a usable dataframe.

## Fonctionalities

This package offer the followinf set of fonctionalities to read specific data

### How to use a DataReader

1) Identify the correct dataReader to use according to input (expl: otoriver data, sensea data)
2) Initialize DataReader and specify `timefreq` variable to chose time frequency output (expl: "h", "min", "30min").
   An aggregation will be performed on input data to generate the output with time frequency needed.
3) use input fonctions to read the data, 3 input types avalable with: 
    - `datareader.from_csv` to read csv file
    - `datareader.from_xlsx` to read excel file
    - `datareader.from_dataframe` to read dataframe

### Acoustic descriptors data 

Acoustic descriptors contain informations about temporal acoustic activities (expl: bioclicks, fish, boats). 
The following objects allow to read specific acoustic data sources : 
- `Otoriver_DataReader`: To read acoustic data from Otoriver source
- `Sensea_DataReader`: To read acoustic data from Sensea source

### Other infos

#### Metadata

DataReader object can use metadata informations relative to the source (expl: "otoriver", "sensea") for different
task (update column names with relevant informations, perform specific operations on measure units, etc.)

##### Expl : Metadata for otoriver

|    | colname                     | varname                     | type       | source   | unit   |   timefreq |
|---:|:----------------------------|:----------------------------|:-----------|:---------|:-------|-----------:|
|  0 | Bioclicks                   | Bioclicks                   | acoustique | otoriver | nb/sec |        nan |
|  1 | Bioclicks séries 40K        | Bioclicks séries 40K        | acoustique | otoriver | %      |        nan |
|  2 | Bioclicks 40K               | Bioclicks 40K               | acoustique | otoriver | nb/sec |        nan |
|  3 | Blioclicks séries 2-30K     | Blioclicks séries 2-30K     | acoustique | otoriver | %      |        nan |
| ...| ...                         | ...                         | ...        | ...      | ...    |        ... |
|  8 | Dauphins sifflements        | Dauphins sifflements        | acoustique | otoriver | nb     |        nan |
|  9 | Baleines chant              | Baleines chant              | acoustique | otoriver | nb     |        nan |
| 10 | Bioclicks mammifères        | Bioclicks mammifères        | acoustique | otoriver | %      |        nan |
| 11 | Poissons 20-400 Hz          | Poissons 20-400 Hz          | acoustique | otoriver | db     |        nan |

"""

from DBBuilder.datareader.__otoriver_datareader import Otoriver_DataReader
from DBBuilder.datareader.__sensea_datareader import Sensea_DataReader