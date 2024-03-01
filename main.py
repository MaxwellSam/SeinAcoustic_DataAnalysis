from DBBuilder import DBBuilder
import glob
import pandas as pd

dbbuilder = DBBuilder()
files = glob.glob("./data/bougival/acoustique/acoustique SENSEA/yolo/*.csv", recursive=True)
df = pd.read_csv(files[0])
db = dbbuilder.create(dates=df.date, labels=df.label)
