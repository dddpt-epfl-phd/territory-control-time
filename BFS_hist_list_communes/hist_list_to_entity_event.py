# %%

import json
import csv
import pandas as pd
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


# %%

gdes_dtf = pd.DataFrame({
    "hid": [g.hid for g in gdes],
    "name": [g.short_name for g in gdes],
    "controller": [g.controller for g in gdes],
    "nb_territories": [len(g.equivalent_territories) for g in gdes]
})

# %%

"""
needs:
- controllers: needs a name + list of date with each a list of controlled territories

algorithm for control list of gde:
- 
"""

def get_gde_control_web(gdes, get_controller=lambda g: g.controller):
    dates = list(set([gde.admission_date for gde in gdes]))
    dates.sort()

    controllers = list(set([get_controller(gde) for gde in gdes]))
     
    territories_to_controller = dict()


    def get_controls_at_date(date, gdes, previous_date_t_to_c, last_controls):
        changed_gdes = [gde for gde in gdes if gde.admission_date==date]

        territories_to_controller = previous_date_t_to_c
        # update territories to controller
        for cgde in changed_gdes:
            for t in cgde.equivalent_territories:
                territories_to_controller[t] = get_controller(cgde)
        controls = {c:set() for c in controllers}
        for t, c in territories_to_controller.items():
            controls[c].add(t)
        
        filtered_controls = {c:ts for c,ts in controls.items() if c not in last_controls or ts!=last_controls[c]}

        return filtered_controls, controls

    controls_at_dates = []
    last_controls =  dict()
    for d in dates:
        filtered_controls_at_d, controls_at_d = get_controls_at_date(d, gdes, territories_to_controller, last_controls)
        controls_at_dates.append((d, filtered_controls_at_d))
        last_controls = controls_at_d

    #controls_at_dates_only_list = [(d, [(c, list(ts)) for c,ts in c_to_ts.items()]) for d,c_to_ts in controls_at_dates]

    controls_by_controller = [(
        c,
        [
            (d, list(c_to_ts[c]))
            for d, c_to_ts
            in controls_at_dates
            if c in c_to_ts
            #if len(c_to_ts[c])>0
        ])
        for c in controllers
    ]

    #return [(d, c_to_ts) for d,c_to_ts in controls_at_dates_only_list if len(c_to_ts)>0]
    return controls_by_controller

controls_at_dates_gde = get_gde_control_web(gdes)
with open("controls_at_dates_gde.json", "w") as outfile:
    json.dump(controls_at_dates_gde, outfile, indent=2)


controls_at_dates_bez = get_gde_control_web(gdes, lambda g: g.district_hist_id)
with open("controls_at_dates_bez.json", "w") as outfile:
    json.dump(controls_at_dates_bez, outfile, indent=2)

controls_at_dates_kt = get_gde_control_web(gdes, lambda g: g.canton_abbreviation)
with open("controls_at_dates_kt.json", "w") as outfile:
    json.dump(controls_at_dates_kt, outfile, indent=2)

# %%
