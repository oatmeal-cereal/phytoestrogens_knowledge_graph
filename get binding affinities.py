import pandas as pd
import json

affinities = pd.read_csv('list files\\Phytoestrogen binding affinities.csv', encoding='utf-8')

affin = {}

columns = list(affinities.columns)

for ind, row in affinities.iterrows():
    comp = row['Compound']
    affin[comp] = {}
    for col in affinities.columns[1:]:
        value = str(row[col])
        if value != 'nan':
            value = value.replace('�', '–')
            affin[comp].update({col: value})

with open('list files\\affinities.json', 'w', encoding='utf-8') as f:
    json.dump(affin, f, ensure_ascii=False)