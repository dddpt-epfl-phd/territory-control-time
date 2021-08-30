# %%
from graph_data_model import * 

from py2neo import Graph


tgraph = Graph(user="neo4j", password="test-password")


# %% TESTS ========================================================================

tabbaye = HistoricalEntity(name="L'Abbaye", category="territoire")
dtabbaye_creation = KnownDate(date=1850)
dtabbaye_dissolution = KnownDate(date=1850)
rel1 = Start(tabbaye, dtabbaye_creation)
rel2 = End(tabbaye, dtabbaye_dissolution)

pe_abbaye_joux = HistoricalEntity(name="Abbaye du lac de joux", category="abbaye")
rel3 = Relationship(pe_abbaye_joux, "DIRECT_CONTROL", tabbaye, end="1536")



da = Node("Huha", name="hahuhua")
tx = tgraph.begin()
#tx.create(da)
tx.push(da)
tgraph.commit(tx)

# %%

da = list(tgraph.run("MATCH (t) RETURN t"))
da

# %% ========================================================================




# %%


# %%


# %%


# %%


# %%


# %%


# %%


