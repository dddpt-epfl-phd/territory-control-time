# %%

import json
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


# %% Municipalities


gde = pd.read_csv(
    path_prefix+"bfs_txt/01.2/20210701_GDEHist_GDE.txt",
    sep="\t",
    encoding="Windows 1252",
    names = colnames["municipalities"]
)

gde_short_col_names = [ camel_to_snake_case(re.sub("municipality","",c)) for c in gde.columns]
gde.columns = gde_short_col_names

# %% Districts

bez = pd.read_csv(
    path_prefix+"bfs_txt/01.2/20210701_GDEHist_BEZ.txt",
    sep="\t",
    encoding="Windows 1252",
    names = colnames["districts"]
)

bez_short_col_names = [ camel_to_snake_case(re.sub("district","",c)) for c in bez.columns]
bez.columns = bez_short_col_names

# %% Cantons

kt = pd.read_csv(
    path_prefix+"bfs_txt/01.2/20210701_GDEHist_KT.txt",
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
    "equivalent_territories",
    "origin",
    'mutation_number',
    "from_scission"
]

def create_new_controller(*args, extra_cols=True):
    cols = gde_cols.copy()
    if extra_cols:
        cols+=gde_extra_cols
    return pd.DataFrame({k:v for k,v in zip(cols, args)})

"""

controller:
    - id
    - name
    - start_date
    - end_date
    - controlled (array)

controlled:
    - start_date
    - territory_hist_id
    - end_date (default None)
    - shared_control_id (default None)

equivalent_controller
equivalent_territories
-> for each hist_id


algo:
-> goal:
    final_gdes is a dtf with on each line:
        start & end date
        controller & equivalent_territories
- add controller, equivalent_territories, equivalence column in gdes, with municipality histId
- add AdmissionDateOrderable AbolitionDateOrderable
- func1step(gdes, final_gdes):
    - split gdes: those with earliest abolition date in
        cgdes, the other in rgdes
    - cgdes without abolition dates -> in final gdes
    - merge cgdes with rgdes on
        - cgde: abolitionNb 
        - rgde: admissionNb
    - groupby: abolitionNb, for each mutation:
        switch on abolition_type_ab:
            district/canton change    1492
                -> keep same controller
                -> keep same equivalent_territories
            renumbering                581
                -> keep same controller
                -> keep same equivalent_territories
            district name change        47
                -> keep same controller
                -> keep same equivalent_territories
            territory exchange          15
                -> keep same controller
                -> keep same equivalent_territories
            inclusion                  342
                26:
                    -> keep same controller
                    -> add new equivalent_territories
            fusion                     216
                21:
                    -> create new controller
                    -> add new equivalent_territories
            name change                206
                -> create new controller
                -> keep same equivalent_territories
            exclusion/scission/multi inclusion/multi exclusion
                easy exclusion (separable former gde):
                -> create new controllers
                -> share equivalent_territories
                hard exclusions:
                -> create new controllers
                -> shared control over equivalent_territories

        -----
        if more than 1 new unique histId:
            if all admission codes are 26: (territory exchange)
                -> corresponding controllers
            else:
                old controlled, controllers is both new histId
        else:
            26 in ab code: 26ab's controller's histId is controller to all 
            21 code: controller is new municipality histId
            in the modified entities, you give:
                - controller admission fields
                - controlled abolition fields
                - name fields: 
- func1step(gdes, [])

"""

class Controlled:
    def __init__(self, start_date, hist_id, end_date=None, shared_control_id=None):
        self.hist_id=hist_id
        self.start_date=start_date
        self.end_date=end_date
        self.shared_control_id=shared_control_id
class Controller:
    def __init__(self, start_date, hist_id, name, controlled=[], end_date=None):
        self.hist_id=hist_id
        self.name=name
        self.start_date=start_date
        self.controlled= controlled.copy()
        self.end_date=end_date
    def set_end_date(self,end_date):
        for c in controlled:
            if c.end_date is None:
                c.end_date=end_date
        self.end_date=end_date

def gde_control(gde, control_relationships=None):
    gde.admission_date = orderable_dates(gde.admission_date)
    gde.abolition_date = orderable_dates(gde.abolition_date)
    madr = min_admission_date_rows = gde.admission_date==gde.admission_date.min()
    gde.loc[madr,"controller"]= [[hid] for hid in gde.loc[madr,"history_municipality_id"]]
    gde.loc[madr, "equivalent_territories"] = [[hid] for hid in gde.loc[madr,"history_municipality_id"]]
    gde.loc[madr,"origin"]="initialization"
    gde["mutation_number"] = gde["admission_number"]
    gde["from_scission"] = False

    controllers={m.hist_id:Controller(
        m.admission_date,
        m.hist_id,
        m.short_name,
        controlled=[Controlled]
    ) for i,m in gde.iterrows()}

    def gde_control_from_mutation(mutation):
        # scission/exclusion
        if mutation["history_municipality_id_ad"].value_counts()>=1:
            # territory exchange/scission/exclusion
            if all(mutation["admission_mode.ad"]==26):
                # territory exchange: keep same controller
                matching_gde = mutation[mutation.id_ab==mutation.id_ad]
                matching_gde.controller_ad = matching_gde.controller_ab
                matching_gde.from_scission_ad = matching_gde.from_scission_ab
                
                return matching_gde[keep_ad_columns].copy()
            else:
                # scission/exclusion: both new territories keep
                # create new controller, keep same equivalent_territories, from_scission=True and 
                # if future fusion with gde outisde of old ones: problem :-/
                
                mutation.controller_ad = mutation.controller_ab
                mutation.equivalent_territories_ad = [mutation.equivalent_territories_ab.iloc[0].copy() for i in range(mutation.shape[0])]
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
                    mutation.equivalent_territories_ab.iloc[0].copy(),
                    "scission/exclusion",
                    42, True
                )
    
                return mutation

    while gde.controller.isnull().values.any():
        abolished_gde = gde[gde.abolition_date==gde.abolition_date.min()].copy()
        unabolished_gde = gde[gde.abolition_date!=gde.abolition_date.min()].copy()
        abolished_gde["mutation_number"] = abolished_gde["abolition_number"]

        # finding the new gde
        mutations = abolished_gde.merge(gde, on="mutation_number", suffixes = ("_ab", "_ad"))

        mutation = mutations[mutations.admission_number_ad==3632]
        keep_ad_columns = [
            c for c in mutations.columns
            if c.endswith("ad") or c=="mutation_number"
        ]
        keep_ab_columns = [
            c for c in mutations.columns
            if c.endswith("ab") or c=="mutation_number"
        ]
        
        new_gde = [
            gde_control_from_mutation(g)
            for n,g in mutations.groupby("mutation_number")
        ]

    return control_relationships

gde[gde.admission_number==3632]


mutations = add_mutations_type(gde)

if False:
    mutations[(mutations.mutation_type=="exclusion") |
        (mutations.mutation_type=="scission") | 
        (mutations.mutation_type=="multi exclusion") |
        (mutations.mutation_type=="multi inclusion")
    ]
    mutations["year"] = [int(re.sub(r"\d+.\d+\.","",d)) for d in mutations.mutation_date]

    # getting all gde in a given mutation
    jn = 3677
    da=gde[(gde.admission_number==jn)|(gde.abolition_number==jn)].sort_values(by="admission_date")
    da

    # getting gde with unknown mutation type
    gde.loc[gde.admission_type=="unknown","admission_number"].unique().shape
    # -> 54 mutations without multi-inclusion
    # -> 48 mutations with multi-inclusion

# %%
