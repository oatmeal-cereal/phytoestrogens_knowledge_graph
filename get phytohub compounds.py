import pandas as pd
import json

compounds_food_dict = {}

with open('phytoestrogens list.json', 'r') as f:
    all_phytoestrogens = json.load(f)

with open('phytoprogestogens list.json', 'r') as f:
    all_phytoprogestogens = json.load(f)

with open('aromatase inhibitors list.json', 'r') as f:
    all_aromatase_inhibitors = json.load(f)

with open('miscellaneous compounds.json', 'r') as f:
    misc_compounds = json.load(f)

all_compounds = all_phytoestrogens + all_phytoprogestogens + all_aromatase_inhibitors + list(misc_compounds.keys())

def check_name(name):
    for phyto in all_compounds:
        if phyto in name:
            return phyto
    return None

comp_csv = pd.read_csv('list files\\PhytoHub Compounds.csv', header=0, sep='\t', encoding='utf-8')

for ind, row in comp_csv.iterrows():
    chem_name = row['Chemical Name'].replace(u'\xa0', u'')
    phyto = check_name(chem_name)
    if phyto:
        if not pd.isna(row['Food sources']):
            all_foods = row['Food sources'].split(' / ')
            if not compounds_food_dict.get(phyto):
                compounds_food_dict[phyto] = all_foods
            else:
                compounds_food_dict[phyto] += all_foods

print(compounds_food_dict)

with open('list files\\compounds.json', 'w') as f:
    json.dump(compounds_food_dict, f)