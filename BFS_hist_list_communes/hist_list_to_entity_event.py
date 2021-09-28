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

debug = []

# %% Municipalities



gde = pd.read_csv(
    path_prefix+"bfs_txt/01.2/20210701_GDEHist_GDE.txt",
    sep="\t",
    encoding="Windows 1252",
    names = colnames["municipalities"]
)

gde_short_col_names = [ camel_to_snake_case(re.sub("municipality","",c)) for c in gde.columns]
gde.columns = gde_short_col_names
gde.admission_date = orderable_dates(gde.admission_date)
gde.abolition_date = orderable_dates(gde.abolition_date)

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
        for c in self.controlled:
            if c.end_date is None:
                c.end_date=end_date
        self.end_date=end_date

def copy_equivalent_territories(abolished_gde, admitted_gde):
        """
        Creates a copy of the "equivalent territories"  of abolished_gde for admitted_gde,
        matching gde by id: gde stay the same
        """
        if abolished_gde.shape[0]==1:
            return abolished_gde.equivalent_territories.copy()
        else:
            return [
                abolished_gde.equivalent_territories[abolished_gde.id==ad_id].values[0].copy()
                #for et in abolished_gde.equivalent_territories
                for ad_id in admitted_gde.id
            ]
def concat_equivalent_territories(abolished_gde, admitted_gde):
    """
    Concatenates the "equivalent territories"  of the abolished_gde for the admitted_gde:
    Control of the territories of abolished_gde is shared among admitted_gde
    """
    global debug
    debug += ["concat_equivalent_territories", abolished_gde, admitted_gde]
    equivalent_territories = abolished_gde.equivalent_territories if abolished_gde.shape[0]>1 else list(abolished_gde.equivalent_territories)
    ets = [et for ets in equivalent_territories for et in ets]
    return [ets.copy() for i in range(admitted_gde.shape[0])]

def gde_control_from_mutation(abolished_gde, admitted_gde):
    """
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
            -> controller is gde hist_id
            -> keep same equivalent_territories
        exclusion/scission/multi inclusion/multi exclusion
            easy exclusion (separable former gde):
            -> create new controllers
            -> share equivalent_territories
            hard exclusions:
            -> create new controllers
            -> shared control over equivalent_territories
    
        DISTRICT_CHANGE_MUTATION = "district/canton change"
        TERRITORY_EXCHANGE_MUTATION = "territory exchange"
        INCLUSION_MUTATION = "inclusion"
        MULTI_INCLUSION_MUTATION = "multi inclusion"
        MULTI_EXCLUSION_MUTATION = "multi exclusion"
        EXCLUSION_MUTATION = "exclusion"
        SCISSION_MUTATION = "scission"
        INITIALIZATION_MUTATION = "initialization"
        RENUMBERING_MUTATION = "renumbering"
        NAME_CHANGE_MUTATION = "name change"
        DISTRICT_NAME_CHANGE_MUTATION = "district name change"
        FUSION_MUTATION 
    """
    #print("gde_control_from_mutation() abolished_gde: ")
    #print(abolished_gde.short_name)
    global debug
    debug += ["gde_control_from_mutation", abolished_gde, admitted_gde]
    mutation_type = abolished_gde.abolition_type.unique()[0]
    if mutation_type in [
        DISTRICT_CHANGE_MUTATION,
        RENUMBERING_MUTATION,
        NAME_CHANGE_MUTATION,
        DISTRICT_NAME_CHANGE_MUTATION
    ]:
        print("renumber-dis change")
        admitted_gde.controller = abolished_gde.controller.copy()
        admitted_gde.equivalent_territories = abolished_gde.equivalent_territories.copy()
    elif mutation_type==TERRITORY_EXCHANGE_MUTATION:
        print("terr ex")
        admitted_gde.controller = [
            abolished_gde.controller[abolished_gde.id==ad_id].values[0]
            for ad_id in admitted_gde.id
        ]
        admitted_gde.equivalent_territories = copy_equivalent_territories(abolished_gde, admitted_gde)
    elif mutation_type==NAME_CHANGE_MUTATION:
        print("name change")
        admitted_gde.controller = admitted_gde.history_municipality_id
        admitted_gde.equivalent_territories = concat_equivalent_territories(abolished_gde, admitted_gde)
    elif mutation_type==FUSION_MUTATION:
        print("fusion")
        admitted_gde.controller = admitted_gde.history_municipality_id
        admitted_gde.equivalent_territories = concat_equivalent_territories(abolished_gde, admitted_gde)
    elif mutation_type==INCLUSION_MUTATION:
        print("inclusion")
        controller = abolished_gde.loc[abolished_gde.abolition_mode==26,"controller"].values[0]
        admitted_gde.controller=controller
        admitted_gde.equivalent_territories = concat_equivalent_territories(abolished_gde, admitted_gde)
    elif mutation_type in [
        MULTI_INCLUSION_MUTATION,
        MULTI_EXCLUSION_MUTATION,
        EXCLUSION_MUTATION,
        SCISSION_MUTATION
    ]:
        print("scission/exclusion/multi-...")
        # TODO: improve scission/exclusion to finesse gde control if possible
        admitted_gde.controller = admitted_gde.history_municipality_id
        admitted_gde.equivalent_territories = concat_equivalent_territories(abolished_gde, admitted_gde)
    print("admitted_gde.controller")
    print(admitted_gde.controller)
    return admitted_gde

def gde_control(gde):
    gde["controller"]=None
    gde["equivalent_territories"]=None
    gde["origin"]=None
    madr = min_admission_date_rows = gde.admission_date==gde.admission_date.min()
    gde.loc[madr,"controller"]= [[hid] for hid in gde.loc[madr,"history_municipality_id"]]
    gde.loc[madr, "equivalent_territories"] = gde.loc[madr,"history_municipality_id"].map(lambda hid: [0,hid])
    gde.loc[madr,"origin"]="initialization"
    gde["mutation_number"] = gde["admission_number"]
    gde["from_scission"] = False

    """ controllers={m.hist_id:Controller(
        m.admission_date,
        m.history_municipality_id_ad,
        m.short_name,
        controlled=[Controlled(
            m.admission_date,
            m.history_municipality_id_ad,
        )]
    ) for i,m in gde.iterrows()} """

    
    
    def gde_control_recursive(gde):
        #while still_uncontrolled_gde:
        print(f"number of 'uncontrolled' gde: {gde.controller.isnull().sum()}")
        mutation_number = gde.abolition_number.min()
        abolished_gde = gde[gde.abolition_number==mutation_number].copy()
        admitted_gde = gde[gde.admission_number==mutation_number].copy()
        changed_gde_hist_ids = list(abolished_gde.history_municipality_id) + list(admitted_gde.history_municipality_id)
        unchanged_gde = gde[[hid not in changed_gde_hist_ids for hid in gde.history_municipality_id]].copy()

        new_admitted_gde = gde_control_from_mutation(abolished_gde, admitted_gde)

        new_gde = unchanged_gde.append(new_admitted_gde)
        if False:
            adgde = admitted_gde
            abgde = abolished_gde
            abolished_gde = list(abgde.groupby(abgde.abolition_number))[0][1]
            admitted_gde = list(adgde.groupby(adgde.admission_number))[0][1]


        print(f"-- number of 'uncontrolled' new_gde: {new_gde.controller.isnull().sum()}")
        if new_gde.controller.isnull().values.any():
            abolished_gde.append(gde_control_recursive(new_gde))
        else:
            return abolished_gde.append(new_gde)
        #still_uncontrolled_gde = gde.controller.isnull().values.any()
    # END WHILE

    return gde_control_recursive(gde)

gde[gde.admission_number==3632]

print("adding mutations types...")
mutations = add_mutations_type(gde)
print("done adding mutations types")

print("adding controls...")
gde_to1960 = gde[ (gde.admission_date<19600000)].copy()
new_gde_to1960 = gde_control(gde_to1960)
#new_gde_from1960 = gde_control(gde[gde.admission_date>=19600000].copy())
print("done adding controls")

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
