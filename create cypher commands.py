from neo4j import GraphDatabase
import json
import pandas as pd

with open('list files\\body concentrations.json', 'r') as f:
    body_concentrations = json.load(f)

with open('list files\\compounds.json', 'r') as f:
    compounds = json.load(f)

with open('list files\\glycoside aglycone pairs.json', 'r') as f:
    glyc_agly_pairs = json.load(f)

with open('go away\\passwords.json', 'r') as f:
    passwords = json.load(f)

with open('phytoestrogens list.json', 'r') as f:
    all_phytoestrogens = json.load(f)

with open('phytoprogestogens list.json', 'r') as f:
    all_phytoprogestogens = json.load(f)

with open('aromatase inhibitors list.json', 'r') as f:
    all_aromatase_inhibitors = json.load(f)

with open('list files\\food concentrations.json', 'r') as f:
    food_concentrations = json.load(f)

with open('list files\\affinities.json', 'r', encoding='utf-8') as f:
    comp_affinities = json.load(f)

with open('miscellaneous compounds.json', 'r') as f:
    misc_compounds = json.load(f)

all_compounds = all_phytoestrogens + all_phytoprogestogens + all_aromatase_inhibitors + list(misc_compounds.keys())

neo_password = passwords['neo4j']

del passwords

numbers_map = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}

def preprocess_label(label):
    if label[0].isnumeric():
        label = label.replace(label[0], numbers_map[int(label[0])])
    replace_chars = ["-", "(", ")", " ", ".", ",", "\'", "/", "\"", ";", "&", ":", ";", "|", "%", "’", "?", "!", "«", "+", "（", "）", "？", "，", "<", ">"]
    for char in replace_chars:
        label = label.replace(char, '')
    return label

def preprocess_name(name):
    replace_chars = ["'"]
    for char in replace_chars:
        name = name.replace(char, '')
    return name

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", neo_password)

driver = GraphDatabase.driver(URI, auth=AUTH, max_connection_lifetime=3600)

with driver.session() as session:

    def run_food_compound_commands():

        for compound in all_compounds:
            is_phytoestrogen = "No"
            is_phytoprogestogen = "No"
            is_aromatase = "No"
            if compound in all_phytoestrogens:
                is_phytoestrogen = "Yes"
            if compound in all_phytoprogestogens:
                is_phytoprogestogen = "Yes"
            if compound in all_aromatase_inhibitors:
                is_aromatase = "Yes"
            comp_label = preprocess_label(compound)
            comp_name = preprocess_name(compound)
            comp_command = f"MERGE ({comp_label}:COMPOUND" + r"{" + f"customId: '{comp_label}'," + f" name: '{comp_name}', is_phytoestrogen: '{is_phytoestrogen}', is_phytoprogestogen: '{is_phytoprogestogen}', is_aromatase_inhibitor: '{is_aromatase}'" + r"})"
            session.run(comp_command)

        for compound, foods in compounds.items():
            for food in foods:
                food_label = preprocess_label(food)
                food_command = f"MERGE ({food_label}:FOOD" + r"{" + f"customId: '{food_label}', name: '{food}'" + r"})"
                session.run(food_command)

                rel_command =  f"""MATCH (a) WHERE a.customId = '{food_label}'
                                    MATCH (b) WHERE b.customId = '{comp_label}'
                                    MERGE (a)-[:CONTAINS]->(b)
                                    """
                session.run(rel_command)

    def run_food_concentration_commands():

        current_food = ""
        for food, compound, low, high in food_concentrations:
            if not pd.isna(food):
                current_food = food
            food_label = preprocess_label(current_food)
            food_name = preprocess_name(current_food)

            comp_label = preprocess_label(compound)
            comp_name = preprocess_name(compound)

            food_test_command = f"MATCH (a) WHERE a.name = '{current_food}' RETURN a.name AS name"

            records, summary, keys = driver.execute_query(food_test_command)

            if not records: #if results is an empty list
                food_command = f"MERGE ({food_label}:FOOD" + r"{" + f"customId: '{food_label}', name: '{current_food}'" + r"})"
                session.run(food_command)

            rel_command =  f"""MATCH (a) WHERE a.customId = '{food_label}'
                                MATCH (b) WHERE b.customId = '{comp_label}'
                                MERGE (a)-[rel:CONTAINS]->(b)
                                SET rel.concentration_low = {low}, rel.concentration_high = {high}, rel.unit = 'mg/g'
                                """
            session.run(rel_command)

    def run_glycoside_aglycone_commands():

        for glycoside, aglycone in glyc_agly_pairs:
            glyco_label = preprocess_label(glycoside)
            agly_label = preprocess_label(aglycone)
            command1 = f"MERGE ({glyco_label}:COMPOUND" + r"{" + f"customId: '{glyco_label}'," + f" name: '{glycoside}'" + r"})"
            command2 = f"MERGE ({agly_label}:COMPOUND" + r"{" + f"customId: '{agly_label}'," + f" name: '{aglycone}'" + r"})"

            session.run(command1)
            session.run(command2)

            rel_command1 =  f"""MATCH (a) WHERE a.customId = '{glyco_label}'
                                MATCH (b) WHERE b.customId = '{agly_label}'
                                MERGE (a)-[:GLYCOSIDEOF]->(b)
                                """
            session.run(rel_command1)
            
            rel_command2 =  f"""MATCH (a) WHERE a.customId = '{agly_label}'
                                MATCH (b) WHERE b.customId = '{glyco_label}'
                                MERGE (a)-[:AGLYCONEOF]->(b)
                                """
            session.run(rel_command2)

    def run_body_concentrations_commands():

            for biomarker, others1 in body_concentrations.items():

                comp_label = preprocess_label(biomarker)
                comp_name = preprocess_name(biomarker)
                comp_command = f"MERGE ({comp_label}:COMPOUND" + r"{" + f"customId: '{comp_label}'," + f" name: '{comp_name}'" + r"})"
                session.run(comp_command)

                for biospecimen, others2 in others1.items():
                    for unit, min_max in others2.items():
                        min = min_max['min']
                        max = min_max['max']

                        conc_label = str(min) + str(max) + unit + comp_label
                        conc_label = preprocess_label(conc_label)

                        conc_command = f"MERGE ({conc_label}:BODYCONCENTRATION" + r"{" + f"customId: '{conc_label}'," + f" min: '{min}', max: '{max}', unit: '{unit}', biospecimen: '{biospecimen}'" + r"})"
                        session.run(conc_command)

                        rel_command = f"""MATCH (a) WHERE a.customId = '{comp_label}'
                                            MATCH (b) WHERE b.customId = '{conc_label}'
                                            MERGE (a)-[:FOUNDATCONCENTRATION]->(b)
                                            """
                        session.run(rel_command)

    def run_affinities_commands():

        def sort_affin(affin):
            sort_chars = [' ', '(', ')']
            for char in sort_chars:
                affin = affin.replace(char, '_')
            affin = affin.replace('/', '_PER_')
            affin = affin.replace('%', 'PERCENT')
            affin = affin.replace('__', '_')
            return affin

        for compound, affinities in comp_affinities.items():
            for affin, value in affinities.items():
                affin = sort_affin(affin)
                affin_command = f"""MATCH (a) WHERE a.name = '{compound}'
                                    SET a.{affin} = '{value}'"""

                session.run(affin_command)

    run_food_compound_commands()
    run_food_concentration_commands()
    """ run_glycoside_aglycone_commands()
    run_affinities_commands()
    run_body_concentrations_commands() """

    #MERGE (threeeightdihydrodiligustilide:COMPOUND {customId: 'threeeightdihydrodiligustilide', name: '3,8-dihydrodiligustilide', is_phytoestrogen: 'No', is_phytoprogestogen: 'Yes', is_aromatase_inhibitor: 'No'"})