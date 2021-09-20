# %%

import json
import pandas as pd
import re

from utils import orderable_dates, camel_to_snake_case

"""
Heuristics to control graph:
- if entity doesn't change name: still the same one!
- if it changes name: create new entity.
"""

colnames = []
with open("bfs_txt_colnames.json") as fcoln:
    colnames = json.load(fcoln)


# %% Municipalities


gde = pd.read_csv(
    "bfs_txt/01.2/20210701_GDEHist_GDE.txt",
    sep="\t",
    encoding="Windows 1252",
    names = colnames["municipalities"]
)

gde_short_col_names = [ camel_to_snake_case(re.sub("municipality","",c)) for c in gde.columns]
gde.columns = gde_short_col_names

# %% Districts

bez = pd.read_csv(
    "bfs_txt/01.2/20210701_GDEHist_BEZ.txt",
    sep="\t",
    encoding="Windows 1252",
    names = colnames["districts"]
)

bez_short_col_names = [ camel_to_snake_case(re.sub("district","",c)) for c in bez.columns]
bez.columns = bez_short_col_names

# %% Cantons

kt = pd.read_csv(
    "bfs_txt/01.2/20210701_GDEHist_KT.txt",
    sep="\t",
    encoding="Windows 1252",
    names = colnames["cantons"]
)


# %%


"""

How is it structured?
- mun & dis have admission & abolition number:
    -> that's how you link gde through time among them


gde admissionMode
- 21 mun creation
- 26 mun territory modification
- 23 mun name change
- 24 mun dis/kt change
- 27 mun renumerotation

gde abolitionMode:
- 26 mun territory modification
- 29 mun suppression
- 23 mun name change
- 24 mun dis/kt change
- 27 mun renumerotation

relevant gde changes:
- inclusion
    ab: 26 for main, 29 for others
    ad: 26
- fusion
    ab: 29
    ad: 21 
- exclusion
    ab: 26
    ad: 26 for main, 21 for others
- scission
    ab: 29
    ad: 21
- territory exchange:
    ab/ad: 26

irrelevant changes codes:
- name change: 23
- district/kt change: 24
- renumerotation: 27

proposition:
- abolition 29 leads to end of entity
- admission 21 leads to new entity
- admission 26 leads to change of control
- abolition 29 ad only 21 leads to no change

an event:
- date
- controller histId
- controllee histId
- ab/ad nb

"""

current_free_hist_id = gde.history_municipality_id.max()+1
def get_new_hist_id():
    global current_free_hist_id
    print(f"gfhi: {current_free_hist_id}")
    current_free_hist_id +=1
    return current_free_hist_id-1


gde_cols=[
    'history_municipality_id',
    'district_hist_id',
    'canton_abbreviation',
    'id',
    'long_name',
    'short_name',
    'entry_mode',
    'status',
    'admission_number',
    'admission_mode',
    'admission_date',
    'abolition_number',
    'abolition_mode',
    'abolition_date',
    'date_of_change',
]
gde_extra_cols = [
    'controller',
    "controlled",
    "origin",
    'join_number',
    "from_scission"
]

def create_new_controller(*args, extra_cols=True):
    cols = gde_cols.copy()
    if extra_cols:
        cols+=gde_extra_cols
    return pd.DataFrame({k:v for k,v in zip(cols, args)})

"""

algo:
-> goal:
    final_gdes is a dtf with on each line:
        start & end date
        controller & controlled
- add controller&controlled column in gdes, with municipality histId
- add AdmissionDateOrderable AbolitionDateOrderable
- func1step(gdes, final_gdes):
    - split gdes: those with earliest abolition date in
        cgdes, the other in rgdes
    - cgdes without abolition dates -> in final gdes
    - merge cgdes with rgdes on
        - cgde: abolitionNb 
        - rgde: admissionNb
    - groupby: abolitionNb, for each group:
        if more than 1 new unique histId:
            if all admission codes are 26: (territory exchange)
                -> corresponding controllers
            else:
                old controlled, controllers is both new histId
        else:
            26 in ab code: 26ab's histId is controller to all 
            21 code: controller is new municipality histId
            in the modified entities, you give:
                - controller admission fields
                - controlled abolition fields
                - name fields: 
- func1step(gdes, [])

"""

def gde_control(gde, control_relationships=None):
    gde.admission_date = orderable_dates(gde.admission_date)
    gde.abolition_date = orderable_dates(gde.abolition_date)
    madr = min_admission_date_rows = gde.admission_date==gde.admission_date.min()
    gde.loc[madr,"controller"]=gde.loc[madr,"history_municipality_id"]
    gde.loc[madr, "controlled"] = [[hid] for hid in gde.loc[madr,"history_municipality_id"]]
    gde.loc[madr,"origin"]="initialization"
    gde["join_number"] = gde["admission_number"]
    gde["from_scission"] = False

    def gde_control_from_mutation(mutation):
        # scission/exclusion
        if mutation["history_municipality_id.ad"].value_counts()>=1:
            # territory exchange/scission/exclusion
            if all(mutation["admission_mode.ad"]==26):
                # territory exchange: keep same controller
                matching_gde = mutation[mutation.id_ab==mutation.id_ad]
                matching_gde.controller_ad = matching_gde.controller_ab
                matching_gde.from_scission_ad = matching_gde.from_scission_ab
                
                return matching_gde[keep_ad_columns].copy()
            else:
                # scission/exclusion: both new territories keep
                # create new controller, keep same controlled, from_scission=True and 
                # if future fusion with gde outisde of old ones: problem :-/
                
                mutation.controller_ad = mutation.controller_ab
                mutation.controlled_ad = [mutation.controlled_ab.iloc[0].copy() for i in range(mutation.shape[0])]
                mutation.from_scission_ad = True
                new_controller_id = get_new_hist_id()
                create_new_controller(
                    new_controller_id,
                    mutation.district_hist_id_ad.iloc[0],
                    mutation.canton_abbreviation_ad.iloc[0],
                    42,
                    ", ".join(mutation.long_name_ad),
                    ", ".join(mutation.short_name_ad),
                    42, 42, 42, 21,
                    mutation.admission_date_ad.iloc[0],
                    42, 42, 42, None, "2021.09.20",
                    new_controller_id,
                    mutation.controlled_ab.iloc[0].copy(),
                    "scission/exclusion",
                    42, True
                )
    
                return mutation

    while gde.controller.isnull().values.any():
        abolished_gde = gde[gde.abolition_date==gde.abolition_date.min()].copy()
        unabolished_gde = gde[gde.abolition_date!=gde.abolition_date.min()].copy()
        abolished_gde["join_number"] = abolished_gde["abolition_number"]

        # finding the new gde
        mutations = abolished_gde.merge(gde, on="join_number", suffixes = ("_ab", "_ad"))

        mutation = mutations[mutations.admission_number_ad==3632]
        keep_ad_columns = [
            c for c in mutations.columns
            if c.endswith("ad") or c=="join_number"
        ]
        keep_ab_columns = [
            c for c in mutations.columns
            if c.endswith("ab") or c=="join_number"
        ]
        
        new_gde = [
            gde_control_from_mutation(g)
            for n,g in mutations.groupby("join_number")
        ]

    return control_relationships

gde[gde.admission_number==3632]

if False:
    gde[gde.admission_number]


    dup1 = gde[gde.admission_number!=1000][gde.admission_number[gde.admission_number!=1000].duplicated()]



# %%
