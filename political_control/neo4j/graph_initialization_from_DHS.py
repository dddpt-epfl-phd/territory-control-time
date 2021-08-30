# %%
import json

from py2neo import Graph

from graph_data_model import * 


neo4j_pwd=None
with open('neo4j_db/.neo4j_pwd', 'r') as file:
    neo4j_pwd = file.read()

tgraph = Graph(user="neo4j", password=neo4j_pwd)
neo4j_pwd=None


# %%

da = list(tgraph.run("MATCH (t) RETURN t"))
print("nb of nodes in db: "+str(len(da)))

# %% DATES 

print("\n\n\nLoading dates...")
dates=None
with open("initialization_from_DHS/dates.json", "r") as fdates:
    dates = json.load(fdates)

gdates = [HistoricalDate.parse_json(d) for d in dates]

counter=0
for gd in gdates:
    gd_in_db = PoliticalEntity.match(tgraph).where("_.readableId='"+gd.readableId+"'")
    if not gd_in_db:
        print("neo4j creating territory: "+gd.readableId)
        tgraph.create(gd)
        counter+=1
print("done, nb dates created: "+str(counter))

# %% Territories 

print("\n\n\nLoading territories scraped from DHS...")
jterritories=None
with open("initialization_from_DHS/territories_VD.json", "r") as fterritories:
    jterritories = json.load(fterritories)

gterritories = [PoliticalEntity.parse_json(t, tgraph) for t in jterritories]

counter=0
for gt in gterritories:
    gt_in_db = PoliticalEntity.match(tgraph).where("_.dhsId='"+gt.dhsId+"'")
    if not gt_in_db:
        print("neo4j creating territory: "+gt.dhsId)
        tgraph.create(gt)
        counter+=1
print("done, nb territories created: "+str(counter))


# %% PoliticalEntities basis 

print("\n\n\nLoading political entities scraped from DHS...")
jpolitical_entities_basis=None
with open("initialization_from_DHS/DHS_political_entities_basis.json", "r") as fpolitical_entities_basis:
    jpolitical_entities_basis = json.load(fpolitical_entities_basis)

gpolitical_entities_basis = [PoliticalEntity.parse_json(pe, tgraph) for pe in jpolitical_entities_basis]


counter=0
for gpe in gpolitical_entities_basis:
    gpe_in_db = PoliticalEntity.match(tgraph).where("_.dhsId='"+gpe.dhsId+"'")
    if not gpe_in_db:
        print("neo4j creating political entity: "+gpe.dhsId)
        tgraph.create(gpe)
        counter+=1
print("done, nb political entities created: "+str(counter))


# %% PoliticalEntities already done by hand 

print("\n\n\nLoading political entities already checked by hand...")
jpolitical_entities_hand=None
with open("initialization_from_DHS/political_entities.json", "r") as fpolitical_entities_hand:
    jpolitical_entities_hand = json.load(fpolitical_entities_hand)

gpolitical_entities_hand = [PoliticalEntity.parse_json(pe, tgraph) for pe in jpolitical_entities_hand]


counter=0
for gpe in gpolitical_entities_hand:
    gpe_in_db = PoliticalEntity.match(tgraph).where("_.dhsId='"+gpe.dhsId+"'")
    if not gpe_in_db:
        print("neo4j creating political entity: "+gpe.dhsId)
        tgraph.create(gpe)
        counter+=1
print("done, nb political entities (already hand-checked) created: "+str(counter))

# %%


# %%


# %%


# %%


# %%


# %%


# %%


