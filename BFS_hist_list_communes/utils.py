import pandas as pd
import re
from warnings import warn

orderable_date_regex = re.compile(r"(\d{2})\.(\d{2}).(\d{4})")
def orderable_date(d):
    if isinstance(d, str) and orderable_date_regex.match(d):
        return int(orderable_date_regex.sub(r"\3\2\1",d))
    else:
        return float("nan")
orderable_dates = lambda dates: [orderable_date(d) for d in dates]

camel_to_snake_case_regex = re.compile(r"([A-Z]+)")

def camel_to_snake_case(s):
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')





def get_attributes_string(class_name, object_dict):
    return f"""{class_name}({', '.join([
        f"{str(k)}: {str(v)}"
        for k, v in object_dict.items()
    ])})"""




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
FUSION_MUTATION = "fusion"
MUTATION_TYPES = [
    DISTRICT_CHANGE_MUTATION,
    TERRITORY_EXCHANGE_MUTATION,
    INCLUSION_MUTATION,
    MULTI_INCLUSION_MUTATION,
    MULTI_EXCLUSION_MUTATION,
    EXCLUSION_MUTATION,
    SCISSION_MUTATION,
    INITIALIZATION_MUTATION,
    RENUMBERING_MUTATION,
    NAME_CHANGE_MUTATION,
    DISTRICT_NAME_CHANGE_MUTATION,
    FUSION_MUTATION
]


class HistoricizedMunicipality:
    def __init__(self, dict_municipality):
        self.hid = int(dict_municipality["history_municipality_id"])
        self.district_hist_id = int(dict_municipality["district_hist_id"])
        self.canton_abbreviation = dict_municipality["canton_abbreviation"]
        self.id = int(dict_municipality["id"])
        self.long_name = dict_municipality["long_name"]
        self.short_name = dict_municipality["short_name"]
        self.entry_mode = int(dict_municipality["entry_mode"])
        self.status = int(dict_municipality["status"])
        self.admission_number = int(dict_municipality["admission_number"])
        self.admission_mode = int(dict_municipality["admission_mode"])
        self.admission_date = orderable_date(dict_municipality["admission_date"])
        self.abolition_number = int(dict_municipality["abolition_number"]) if dict_municipality["abolition_number"] else None
        self.abolition_mode = int(dict_municipality["abolition_mode"]) if dict_municipality["abolition_mode"] else None
        self.abolition_date = orderable_date(dict_municipality["abolition_date"]) if dict_municipality["abolition_date"] else 99999999
        self.date_of_change = orderable_date(dict_municipality["date_of_change"])
        self.controller = None
        self.equivalent_territories = []
        self.admission=None
        self.abolition=None
        self.mutations_history=[]
    def successors(self):
        if self.abolition is None:
            return None
        else:
            return self.abolition.admitted
    def predessors(self):
        if self.admission is None:
            return None
        else:
            return self.admission.abolished
    def __str__(self):
        odict = self.__dict__.copy()
        del odict["admission"]
        del odict["abolition"]
        odict["admission_type"] = self.admission.type if self.admission else "?"
        odict["abolition_type"] = self.abolition.type if self.abolition else "?"
        return get_attributes_string("HistoricizedMunicipality", odict)
    def __repr__(self):
        return self.__str__()

class Mutation:
    def __init__(self, number,abolished,admitted, date, mutation_type = None):
        self.number = number
        self.abolished = abolished
        self.admitted = admitted
        self.date = date
        self.type = mutation_type
        if self.type is None:
            self.type = get_mutation_type(self)
        for ab in self.abolished:
            ab.abolition = self
        for ab in self.admitted:
            ab.admission = self
    def __str__(self):
        odict = self.__dict__.copy()
        odict["abolished"] = [f"HistMun({hm.hid}, {hm.short_name}, ab. mode: {hm.abolition_mode})" for hm in odict["abolished"]]
        odict["admitted"] = [f"HistMun({hm.hid}, {hm.short_name}, ab. mode: {hm.admission_mode})" for hm in odict["admitted"]]
        return get_attributes_string("Mutation", odict)
    def __repr__(self):
        return self.__str__()




def get_mutations(gdes):
    # for unclear reasons, admission_number and admission_date pairs are not unique
    # some admission_number have multiple dates
    # we always take the earliest admission date
    mutation_numbers = {gde.admission_number for gde in gdes}
    mutation_numbers_dates = [(mn,min(gde.admission_date for gde in gdes if gde.admission_number==mn)) for mn in mutation_numbers]
    mutations = [
        Mutation(
            mn,
            [gde for gde in gdes if gde.abolition_number==mn],
            [gde for gde in gdes if gde.admission_number==mn],
            date
        ) for mn, date in mutation_numbers_dates
    ]
    # sort by date&number
    mutations.sort(key= lambda m: 10000*m.date + m.number)
    return mutations




def get_mutation_type(mutation):
    """gets mutation type from a Mutation object"""
    abolished_gdes = mutation.abolished
    admitted_gdes = mutation.admitted
    nb_admissions = len(admitted_gdes)
    nb_abolitions = len(abolished_gdes)

    if all(gde.admission_mode==20 for gde in admitted_gdes):
        return "initialization"
    elif nb_admissions>1:
        # territory exchange/scission/exclusion/multi inclusion
        if all(gde.admission_mode==26 for gde in admitted_gdes) and nb_abolitions==nb_admissions:
            return "territory exchange"
        if all(gde.admission_mode==26 for gde in admitted_gdes):
            # multi inclusion: 1 gde is shared in 2 existing gdes
            return "multi inclusion"
        elif any(gde.admission_mode==26 for gde in admitted_gdes)  and nb_abolitions==1:
            return "exclusion"
        elif any(gde.admission_mode==26 for gde in admitted_gdes)  and nb_abolitions>1:
            # multi exclusion: 1 gde is cut out of 2 existing gdes
            return "multi exclusion"
        elif all(gde.admission_mode==21 for gde in admitted_gdes)  and nb_abolitions==1:
            return "scission"
    else:
        admitted_gde = admitted_gdes[0]
        if admitted_gde.admission_mode==27:
            return "renumbering"
        elif admitted_gde.admission_mode==23:
            return "name change"
        elif admitted_gde.admission_mode==22:
            return "district name change"
        elif admitted_gde.admission_mode==24:
            return "district/canton change"
        elif admitted_gde.admission_mode==26:
            return "inclusion"
        elif admitted_gde.admission_mode==21:
            return "fusion"
    warn(f"unknown gemeinde mutation type for number: {mutation.number}")
    return f"unknown"

# %%


def gde_control_from_mutation(mutation):
    nb_abolished = len(mutation.abolished)
    nb_admitted = len(mutation.admitted)

    # adding mutation_history
    for admitted in mutation.admitted:
        admitted.mutations_history = [mutation]+[
           m for abolished in mutation.abolished
           for m in abolished.mutations_history
        ]

    if mutation.type == INITIALIZATION_MUTATION:
        for admitted in mutation.admitted:
            admitted.controller = admitted.hid
            admitted.equivalent_territories = [admitted.hid]
        return None
    if nb_abolished == nb_admitted == 1:
        # only 1 abolished&admitted:
        abolished = mutation.abolished[0]
        admitted = mutation.admitted[0]
        if mutation.type in [
            DISTRICT_CHANGE_MUTATION,
            RENUMBERING_MUTATION,
            NAME_CHANGE_MUTATION,
            DISTRICT_NAME_CHANGE_MUTATION
        ]:
            admitted.controller = abolished.controller
            admitted.equivalent_territories = abolished.equivalent_territories.copy()
            return None
        elif mutation.type==NAME_CHANGE_MUTATION:
            admitted.controller = admitted.controller.hid
            admitted.equivalent_territories = abolished.equivalent_territories.copy()
            return None
    elif nb_admitted==1:
        admitted = mutation.admitted[0]
        if mutation.type==FUSION_MUTATION:
            admitted.controller = admitted.hid
            admitted.equivalent_territories = [et for ab in mutation.abolished for et in ab.equivalent_territories]
            return None
        elif mutation.type==INCLUSION_MUTATION:
            controller = [ab for ab in mutation.abolished if ab.abolition_mode==26]
            if len(controller)!=1:
                raise Exception(f"gde_control_from_mutation() inclusion with more than 1 abolition_mode 26 for mutation {mutation.number}")
            admitted.controller = controller[0].hid
            admitted.equivalent_territories = [et for ab in mutation.abolished for et in ab.equivalent_territories]
            return None
    else:
        # more than 1 abolished/admitted:
        if mutation.type==TERRITORY_EXCHANGE_MUTATION:
            abs = {ab.short_name: ab for ab in mutation.abolished}
            ads = {ad.short_name: ad for ad in mutation.admitted}
            for short_name, ab in abs.items():
                ads[short_name].controller = ab.controller
                ads[short_name].equivalent_territories = ab.equivalent_territories.copy()
            return None
        elif mutation.type in [
            MULTI_INCLUSION_MUTATION,
            MULTI_EXCLUSION_MUTATION,
            EXCLUSION_MUTATION,
            SCISSION_MUTATION
        ]:
            # TODO: improve scission/exclusion to finesse gde control if possible
            for admitted in mutation.admitted:
                admitted.controller = admitted.hid
                admitted.equivalent_territories = [et for ab in mutation.abolished for et in ab.equivalent_territories]
            return None
    raise Exception(f"gde_control_from_mutation() unable to match control for mutation {mutation.number}")