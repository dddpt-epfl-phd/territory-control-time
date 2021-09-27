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

def get_mutation_type(mutation):
    """returns mutation type
    
    expects gde cols with _ad _ab suffixes
    """
    nb_admissions = len(mutation.history_municipality_id_ad.unique())
    nb_abolitions = len(mutation.history_municipality_id_ab.unique())
    # scission/exclusion
    if nb_admissions>1:
        # territory exchange/scission/exclusion/multi inclusion
        if all(mutation["admission_mode_ad"]==26) and nb_abolitions==nb_admissions:
            return "territory exchange"
        if all(mutation["admission_mode_ad"]==26) and nb_admissions>1:
            # multi inclusion: 1 gde is shared in 2 existing gdes
            return "multi inclusion"
        elif any(mutation["admission_mode_ad"]==26) and nb_abolitions==1:
            return "exclusion"
        elif any(mutation["admission_mode_ad"]==26) and nb_abolitions>1:
            # multi exclusion: 1 gde is cut out of 2 existing gdes
            return "multi exclusion"
        elif all(mutation["admission_mode_ad"]==21) and nb_abolitions==1:
            return "scission"
        else:
            warn("unknown gemeinde mutation type")
            return f"unknown"
    else:
        if any(mutation["admission_mode_ad"]==20):
            return "initialization"
        if any(mutation["admission_mode_ad"]==27):
            return "renumbering"
        elif any(mutation["admission_mode_ad"]==23):
            return "name change"
        elif any(mutation["admission_mode_ad"]==22):
            return "district name change"
        elif any(mutation["admission_mode_ad"]==24):
            return "district/canton change"
        elif any(mutation["admission_mode_ad"]==26):
            return "inclusion"
        elif any(mutation["admission_mode_ad"]==21):
            return "fusion"
        else:
            warn("unknown gemeinde mutation type")
            return f"unknown"


def add_mutations_type(gde, summary_or_mutations="summary"):
    """returns mutation type
    
    expects gde cols
    """
    summary_or_mutations = summary_or_mutations=="summary"

    gde2=gde.copy()
    gde2["mutation_number"]  = gde2["admission_number"]
    gde["mutation_number"] = gde["abolition_number"]

    mutations = gde.merge(gde2, on="mutation_number", suffixes = ("_ab", "_ad"))
    if not summary_or_mutations:
        mutations["mutation_type"]=None

    rmutations = []
    hid_ab = "history_municipality_id_ab"
    colnames_ab= [
            "short_name_ab",
            "abolition_mode_ab",
    ]
    hid_ad = "history_municipality_id_ad"
    colnames_ad= [
            "short_name_ad",
            "admission_mode_ad",
    ]

    gde.loc[gde["admission_mode"]==20,"admission_type"] = "initialization"
    gde["abolition_type"] = None
    for jn,mutation in mutations.groupby("mutation_number"):
        mutation_type = get_mutation_type(mutation)
        gde.loc[gde.admission_number==jn, "admission_type"] = mutation_type
        gde.loc[gde.abolition_number==jn, "abolition_type"] = mutation_type
        gde_ab = mutation[colnames_ab+[hid_ab]].drop_duplicates()
        gde_ad = mutation[colnames_ad+[hid_ad]].drop_duplicates()
        if summary_or_mutations:
            mutation_date = mutation.admission_date_ad.iloc[0]
            rmutations.append([
                list(gde_ab.short_name_ab),
                list(gde_ab.abolition_mode_ab),
                list(gde_ad.short_name_ad),
                list(gde_ad.admission_mode_ad),
                mutation_type,
                mutation_date,
                list(gde_ab.history_municipality_id_ab),
                list(gde_ad.history_municipality_id_ad),
            ])
        else:
            mutations.loc[mutations.mutation_number==jn,["mutation_type"]]=mutation_type
    if summary_or_mutations:
        return pd.DataFrame(rmutations, columns = colnames_ab+colnames_ad+["mutation_type", "mutation_date",hid_ab, hid_ab])
    else:
        del mutations["mutation_number"]
        return mutations
