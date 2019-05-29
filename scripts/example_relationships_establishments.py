import json
import pdb

with open("../data/outputs/categorizer_cat_output.json") as fp:
    categorizations = json.load(fp)

for cat in categorizations:
    if cat['func_call'] == 1:
        print(cat['line'])
