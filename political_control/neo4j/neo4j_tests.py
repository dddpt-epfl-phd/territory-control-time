# %%
from graph_data_model import * 

from py2neo import Graph

# %% TESTING

tgraph = Graph(user="neo4j", password="test-password")


tabbaye = HistoricalEntity(name="L'Abbaye", category="territoire")
dtabbaye_creation = KnownDate(date=1850)
dtabbaye_dissolution = KnownDate(date=1850)
rel1 = Start(tabbaye, dtabbaye_creation)
rel2 = End(tabbaye, dtabbaye_dissolution)

pe_abbaye_joux = HistoricalEntity(name="Abbaye du lac de joux", category="abbaye")
rel3 = Relationship(pe_abbaye_joux, "DIRECT_CONTROL", tabbaye, end="1536")

# %%


da = Node("Huha", name="hahuhua")
tx = tgraph.begin()
#tx.create(da)
tx.push(da)
tgraph.commit(tx)

# %%

da = list(tgraph.run("MATCH (t) RETURN t"))
da

# %%


class Entity(GraphObject):
    __primarykey__ = "name"

    name = Property()
    lordship = Label()

    controls = RelatedTo("Entity", "CONTROLS")
    controlled_by = RelatedFrom("Entity", "CONTROLS")

a = Entity()
a.name = "aaaaa"
a.lordship=True
b = Entity()
b.name = "lbbbbb"

a.controls.add(b)

tgraph.create(a)

da = list(tgraph.run("MATCH (a)-[r:CONTROLS]->(b) RETURN a,b"))

# %%

da = list(tgraph.run("MATCH (t) DETACH DELETE t RETURN t"))
da

# %% ==================================================================

territory = {
    "type": "politicalEntity",
    "id": "dhs-002609",
    "name": "Abbaye, L'",
    "category": "territoire",
    "start": {
      "type": "uncertainBoundedDate",
      "latest": "1850",
      "bestGuess": "1850"
    },
    "end": {
      "type": "uncertainBoundedDate",
      "earliest": "1850"
    },
    "tags": [
      "DHS-Commune"
    ],
    "description": "",
    "sources": [
      {
        "url": "https://hls-dhs-dss.ch/fr/articles/002609/2009-06-23/",
        "id": "dhs-002609",
        "tags": [
          {
            "tag": "Entités politiques / Commune",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.006900.007800."
          }
        ]
      }
    ]
}







# %%

political_entity = {
    "type": "politicalEntity",
    "id": "dhs-012134",
    "name": "Abbaye du Lac de Joux",
    "category": "abbaye",
    "start": "fondation-abbaye-lac-de-joux",
    "end": "conquete-vaud-par-berne",
    "tags": [
      "Entités ecclésiastiques / Abbaye, couvent, monastère, prieuré"
    ],
    "description": "",
    "sources": [
      {
        "name": "Lac de Joux",
        "url": "https://hls-dhs-dss.ch/fr/articles/012134/2009-03-10/",
        "id": "dhs-012134",
        "tags": [
          {
            "tag": "Entités ecclésiastiques / Abbaye, couvent, monastère, prieuré",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.009500.009600."
          }
        ]
      },
      {
        "url": "https://hls-dhs-dss.ch/fr/articles/002609/2009-06-23/",
        "id": "dhs-002609"
      }
    ]
}

political_entity_basis = {
    "type": "politicalEntity",
    "id": "dhs-000032",
    "name": "Rheinau (commune)",
    "category": "",
    "start": {
      "type": "exactDate",
      "date": ""
    },
    "end": {
      "type": "exactDate",
      "date": ""
    },
    "tags": [
      "Commune",
      "Ville médiévale",
      "Archéologie / Site de l'âge du Bronze",
      "Archéologie / Site de Hallstatt",
      "Archéologie / Site de La Tène"
    ],
    "description": "",
    "sources": [
      {
        "name": "Rheinau (commune)",
        "url": "https://hls-dhs-dss.ch/fr/articles/000032/2011-12-23/",
        "id": "dhs-000032",
        "tags": [
          {
            "tag": "Entités politiques / Commune",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.006900.007800."
          },
          {
            "tag": "Entités politiques / Ville médiévale",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.006900.008900."
          },
          {
            "tag": "Archéologie / Site de l'âge du Bronze",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.014300.014700."
          },
          {
            "tag": "Archéologie / Site de Hallstatt",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.014300.014800."
          },
          {
            "tag": "Archéologie / Site de La Tène",
            "url": "/fr/search/category?f_hls.lexicofacet_string=2/006800.014300.014900."
          }
        ]
      }
    ]
}


# %%


# %%


# %%


# %%


# %%


