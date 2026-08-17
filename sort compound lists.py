import json

with open('phytoestrogens list.json', 'r+', encoding='utf-8') as f:
    all_phytoestrogens = json.load(f)
    all_phytoestrogens = list(sorted(all_phytoestrogens))
    f.seek(0)
    json.dump(all_phytoestrogens, f, ensure_ascii=False)
    f.truncate()

with open('phytoprogestogens list.json', 'r+', encoding='utf-8') as f:
    all_phytoprogestogens = json.load(f)
    all_phytoprogestogens = list(sorted(all_phytoprogestogens))
    f.seek(0)
    json.dump(all_phytoprogestogens, f, ensure_ascii=False)
    f.truncate()

with open('aromatase inhibitors list.json', 'r+', encoding='utf-8') as f:
    all_aromatase_inhibitors = json.load(f)
    all_aromatase_inhibitors = list(sorted(all_aromatase_inhibitors))
    f.seek(0)
    json.dump(all_aromatase_inhibitors, f, ensure_ascii=False)
    f.truncate()