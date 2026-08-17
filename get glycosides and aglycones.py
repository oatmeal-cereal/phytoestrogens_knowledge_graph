import pandas as pd
import json

glyc_agly = pd.read_csv('glycoside aglycone.csv', header=0)

pairs = []

for ind, row in glyc_agly.iterrows():
    glycoside = row['Glycoside']
    if pd.isna(glycoside):
        continue
    aglycone = row['Aglycone']
    if pd.isna(aglycone):
        continue
    pairs.append((glycoside, aglycone))

with open('list files\\glycoside algycone pairs.json', 'w') as f:
    json.dump(pairs, f)