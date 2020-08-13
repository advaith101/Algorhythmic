import datetime
import time
import random
from pprint import pprint
import asyncio
import requests
import json
import pandas as pd
import numpy as np
import decimal
import csv

filename = input('What is the file name that you wish to splice? (no need to include .csv)\n') + '.csv'
size = int(input('How many rows do you want each new CSV to be?  (number only)\n'))
df = pd.read_csv(filename, sep='\t', engine='python')
#print(str(df.iloc[1, 0]))

for i in range(0, len(df.index) - size, size):
    dfslice = df.iloc[i:(i+size)] #try loc if this doesn't work
    # firstTime = str(df.loc[i]['Time'])
    # lastTime = str(df.loc[size]['Time'])
    # CSVname = filename + ': ' + dfslice['']
    # df.to_csv(r'Path where you want to store the exported CSV file\File Name.csv', index = False)
