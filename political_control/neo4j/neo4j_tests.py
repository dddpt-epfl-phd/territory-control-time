# %%
from graph_data_model import * 

from py2neo import Graph


tgraph = Graph(user="neo4j", password="test-password")

"""
Good adresses for neo4j:
cypher:
  https://neo4j.com/developer/cypher/
  https://neo4j.com/developer/cypher/querying/
  https://neo4j.com/developer/cypher/updating/
py2neo:
  https://py2neo.org/2021.1/
  1-4:
  https://py2neo.org/v4/data.html#py2neo.data.Node
  https://py2neo.org/v4/database.html#py2neo.database.Transaction.merge
  https://py2neo.org/v4/matching.html
  https://py2neo.org/v4/ogm.html#py2neo.ogm.GraphObject.match
  example:
  https://neo4j.com/blog/py2neo-3-1-python-driver-neo4j/
"""

#%% TESTING


tabbaye = HistoricalEntity(name="L'Abbaye", category="territoire")
dtabbaye_creation = KnownDate(date=1850)
dtabbaye_dissolution = KnownDate(date=1850)
# not possible with GraphObject
#rel1 = Start(tabbaye, dtabbaye_creation) 
#rel2 = End(tabbaye, dtabbaye_dissolution)
tabbaye.start.add(dtabbaye_creation)
tabbaye.end.add(dtabbaye_dissolution)

pe_abbaye_joux = HistoricalEntity(name="Abbaye du lac de joux", category="abbaye")
#rel3 = Relationship(pe_abbaye_joux, "DIRECT_CONTROL", tabbaye, end="1536")

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

# %% DELETE ALL FROM GRAPH ============================================

da = list(tgraph.run("MATCH (t) DETACH DELETE t RETURN t"))
da

# %% ==================================================================


da = list(tgraph.run("MATCH (t) RETURN t"))

print("checking that graph is empty: ")
print("nb of nodes in graph: "+str(len(da)))

# %%

dates = [
    # dates majeures
    # -----------------------------------
    {
      "readableId": "conquete-vaud-par-berne",
      "type":"KnownDate",
      "date": "1536"
    },
    {
      "readableId": "fin-ancien-regime-suisse",
      "type":"KnownDate",
      "date": "1798"
    },
    # dates mineures
    # -----------------------------------
    {
      "readableId": "creation-principaute-neuchatel",
      "type":"UncertainAroundDate",
      "date": "1640",
      "uncertainty": "10Y"
    },
    {
      "readableId": "partage-seigneurie-grandson",
      "type":"KnownDate",
      "date": "1234"
    },
    {
      "readableId": "dissolution-seigneurie-grandson",
      "type":"KnownDate",
      "date": "1476"
    },
    {
      "readableId": "fondation-abbaye-lac-de-joux",
      "type":"UncertainBoundedDate",
      "earliest": "1126",
      "latest": "1134"
    },
    {
      #"readableId": "fin-conflit-abbayes-joux-st-claude",
      "type":"UncertainBoundedDate",
      "earliest": "1204",
      "latest": "1219",
      "bestGuess": "1204"
    }
]


ghdates = [HistoricalDate.parse_json(d) for d in dates]
for ghd in ghdates:
  tx = tgraph.begin()
  tx.create(ghd)
  tgraph.commit(tx)

ghdates

# %%
da = list(tgraph.run("MATCH (t {readableId:'conquete-vaud-par-berne'}) RETURN t"))
da

# %%

territory = {
  "type":"Territory",
  "id": "dhs-002609",
  "name": "Abbaye, L'",
  "category": "territoire",
  "start": {
    "type":"UncertainBoundedDate",
    "latest": "1850",
    "bestGuess": "1850"
  },
  "end": {
    "type":"UncertainBoundedDate",
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


goterritory = Territory.parse_json(territory)
tgraph.create(goterritory)
goterritory_pe = PoliticalEntity.parse_json(territory)
tgraph.create(goterritory_pe)




# %%

political_entity = {
    "type":"PoliticalEntity",
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
    "type":"PoliticalEntity",
    "id": "dhs-000032",
    "name": "Rheinau (commune)",
    "category": "",
    "start": {
      "type":"KnownDate",
      "date": ""
    },
    "end": {
      "type":"KnownDate",
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


