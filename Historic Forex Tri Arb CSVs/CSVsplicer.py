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

filename = input('What is the file name that you wish to splice? (no need to include .csv)\n')
file = filename + '.csv'
size = int(input('How many rows do you want each new CSV to be?  (number only)\n'))
df = pd.read_csv(file, sep='\t', engine='python')

for i in range(0, len(df.index) - size, 1):
    dfslice = df.iloc[i:(i+size)] #try loc if this doesn't work
    firstTime = str(dfslice.iloc[0,0])
    lastTime = str(dfslice.iloc[size - 1, 0])
    sliceFileName = filename.split('_') [0] + ':' + firstTime + '-' + lastTime + '.csv'
    df.to_csv(sliceFileName, sep='\t', index = False) #Path where you want to store the exported CSV file\ <- Can add this before file name in quotes
