import pandas as pd
import json

food_concentrations = pd.read_csv('list files\\food concentrations.csv')

concentrations = []

for ind, row in food_concentrations.iterrows():
    food = row['Food']
    comp = row['Compound']
    low = row['Concentration low (mg/g)']
    high = row['Concentration high (mg/g)']

    concentrations.append((food, comp, low, high))

with open('list files\\food concentrations.json', 'w') as f:
    json.dump(concentrations, f)