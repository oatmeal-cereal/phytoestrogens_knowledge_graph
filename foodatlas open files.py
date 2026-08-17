import pandas as pd
import pyarrow

entities = pd.read_parquet('foodatlas-v4.8/entities.parquet')
relationships = pd.read_parquet('foodatlas-v4.8/relationships.parquet')
triplets = pd.read_parquet('foodatlas-v4.8/triplets.parquet')

contains_triplets = triplets[triplets['relationship_id'] == 'r1']

relations = []

for ind, triplet in contains_triplets.iterrows():
    head_id = triplet['head_id']
    rel_id = triplet['relationship_id']
    tail_id = triplet['tail_id']

    head_entity = entities[entities['foodatlas_id'] == head_id]
    relation = relationships[relationships['foodatlas_id'] == rel_id]
    tail_entity = entities[entities['foodatlas_id'] == tail_id]
    relations.append((head_entity['common_name'], relation['name'], tail_entity['common_name']))

print(len(relations))