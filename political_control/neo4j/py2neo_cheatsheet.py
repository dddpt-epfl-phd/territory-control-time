from py2neo import Graph, Node
from py2neo.ogm import GraphObject

# Node
# ==================

node = Node("NodeLalabel", name="name property")

# subgraphs are Node, RelationShip or GraphObject
subgraph=node

# Relationship
# ==================

# Graph
# ==================

# creation:
graph = Graph(user="neo4j", password="test-password")

# operations
# -------------

# run cypher query
da = list(tgraph.run("MATCH (t) RETURN t"))
da = list(tgraph.run("MATCH (a)-[r:CONTROLS]->(b) RETURN a,b"))
da

# create only if doesn't exist
graph.create(subgraph)
# create or update (based on __primarylabel and __primarykey___)
graph.merge(subgraph)
# update
graph.push(subgraph)
# delete
graph.delete(subgraph)

# check if subraph already in graph
graph.exists(subgraph)

# get relationship starting from node
nodes=(node,) # sequence or set
graph.match(nodes, r_type="CONTROL_OVER")

# Transaction
# ==================

tx = graph.begin()
tx.push(node)
graph.commit(tx)

# GraphObject
# ==================

graph_object = GraphObject(node)


# note that graphObject.create() or
# graphObject.merge() do only match on
# __primarylabel__ and __primarykey__.
# Hence it's tricky to create & merge

