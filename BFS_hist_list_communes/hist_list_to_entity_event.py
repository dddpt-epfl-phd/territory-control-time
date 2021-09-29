# %%

import json
import csv
import re

from utils import *#orderable_dates, camel_to_snake_case, add_mutations_type

"""
Heuristics to control graph:
- if entity doesn't change name: still the same one!
- if it changes name: create new entity.
"""
path_prefix = ""#"BFS_hist_list_communes/"

colnames = []
with open(path_prefix+"bfs_txt_colnames.json") as fcoln:
    colnames = json.load(fcoln)

gde_short_col_names = [ camel_to_snake_case(re.sub("municipality","",c)) for c in colnames["municipalities"]]


# %% Municipalities

gdes = [HistoricizedMunicipality(g) for g in csv.DictReader(open(path_prefix+"bfs_txt/01.2/20210701_GDEHist_GDE.txt", encoding="Windows 1252"), fieldnames=gde_short_col_names)]

for gde in gdes:
    # Wolfenschiessen error: admission_mode 26 as it is initialized in mutation 1000 (init!)
    if gde.hid==10357:
        gde.admission_mode=20
    if gde.hid==12556:
        gde.admission_mode=20

# %% Mutations

# mutations with multiple admission dates:
if False:
    mds = {(g.admission_number, g.admission_date) for g in gdes}
    mns = [m[0] for m in mds]
    duplicate_mutation_numbers = {(n,d) for n,d in mds if len([x for x in mns if x==n])>1}

mutations = get_mutations(gdes)

# %% Control

for m in mutations:
    gde_control_from_mutation(m)