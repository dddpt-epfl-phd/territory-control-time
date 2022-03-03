

from s2_database_population_2 import *

for node_goc in goc:
    tx = tgraph.begin()
    tx.create(node_goc)
    tgraph.commit(tx)

for node_gos in gos:
    tx = tgraph.begin()
    tx.push(node_gos)
    tgraph.commit(tx)

