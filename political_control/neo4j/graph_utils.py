

def gnames(graph_objects):
    return [go.name for go in graph_objects]
def gdhsIds(graph_objects):
    return [go.dhsId for go in graph_objects]

def gdhsIds_and_names(graph_objects):
    return [(go.dhsId, go.name) for go in graph_objects]

def regex_name_query(go_class, graph, regex):
    return [node for node in go_class.match(graph).where(r"_.name=~'.*"+regex+r".*'")]

def greadableIds(graph_objects):
    return [go.readableId for go in graph_objects]