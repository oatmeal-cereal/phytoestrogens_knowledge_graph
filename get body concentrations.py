import pandas as pd
import re
import json

with open('phytoestrogens list.json', 'r') as f:
    all_phytoestrogens = json.load(f)

with open('phytoprogestogens list.json', 'r') as f:
    all_phytoprogestogens = json.load(f)

with open('aromatase inhibitors list.json', 'r') as f:
    all_aromatase_inhibitors = json.load(f)

all_compounds = all_phytoestrogens + all_phytoprogestogens + all_aromatase_inhibitors

phytoestrogen_groups = ['Isoflavones', 'Lignans', 'Phytoestrogens']

def check_name(name, list):
    for item in list:
        if item in name:
            return True
    return False

def check_lists(name_list, list_list):
    for name in name_list:
        if name in list_list:
            return True
    return False

def find_value(row, columns):
    columns = ['Arithmetic mean', 'Median', 'Min', 'Min (detected)', 'Max']
    for col in columns:
        if not pd.isna(row[col]):
            return row[col]
    return None

compound_to_concentrations = {}

concentrations = pd.read_csv('list files\\body concentrations.csv', header=0, sep=',')

def add_bio_values(row, bio_value):
    biospec = row['Biospecimen']
    unit = row['Unit']
    #if this biomarker detail compound has not already been added to the dict
    if not compound_to_concentrations.get(bio_value):
        compound_to_concentrations[bio_value] = {}
    #we will sort by: compound -> biospecimen (urine/blood) -> unit -> min and max values
    if not compound_to_concentrations[bio_value].get(biospec):
        compound_to_concentrations[bio_value][biospec] = {}
    if not compound_to_concentrations[bio_value][biospec].get(unit):
        compound_to_concentrations[bio_value][biospec].update({unit: {}})
        compound_to_concentrations[bio_value][biospec][unit].update({'min': min_value, 'max': max_value})
    #if there already exists an entry for the unit, update values accordingly
    else:
        if compound_to_concentrations[bio_value][biospec][unit]['min'] > min_value:
            compound_to_concentrations[bio_value][biospec][unit]['min'] = min_value
        if compound_to_concentrations[bio_value][biospec][unit]['max'] > max_value:
            compound_to_concentrations[bio_value][biospec][unit]['max'] = max_value

for ind, row in concentrations.iterrows():
    #biomarker detail gives details to the types of biomarkers they are after, e.g. 'Genistein' rather than 'Isoflavones'
    if not pd.isna(row['Biomarker detail']):
        #compounds are usually separated by '+' or '/'
        bio_detail = row['Biomarker detail'].replace(' + ', '/')
        bio_detail = bio_detail.split('/')
    else:
        bio_detail = ''
    #biomarker is something like 'Polyphenols/Isoflavones', the broader grouping
    if row['Biomarker'] in all_compounds + phytoestrogen_groups or check_lists(bio_detail, all_compounds):
        if check_name(row['Biospecimen'].lower(), ['blood', 'plasma', 'serum', 'urine']):
            min_value = find_value(row, ['Min', 'Min (detected)', 'Arithmetic mean', 'Median'])
            max_value = find_value (row, ['Max', 'Arithmetic mean', 'Median'])
            #if there is no min or max value found we skip this one
            if not (min_value or max_value):
                continue
            #biomarker detail usually contains a list of compounds
            for bio in bio_detail:
                add_bio_values(row, bio)
            #if not specific biomarker compounds, use the biomarker directly
            if pd.isna(row['Biomarker detail']):
                biomarker = row['Biomarker']
                add_bio_values(row, biomarker)

print(compound_to_concentrations)

with open('list files\\body concentrations.json', 'w') as f:
    json.dump(compound_to_concentrations, f)