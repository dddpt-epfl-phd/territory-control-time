# based on dhs_anciennes_communes.py from swiss-population-time-machine git repo

import requests as r
import re
from lxml import html
from functools import reduce
import math
import copy

import json
import pandas as pd

# get vufflens la ville
#da = r.get("https://beta.hls-dhs-dss.ch/Articles/007383/?language=fr")
#re.search("Signau",da.text)

# get liste of commune in vd:
baseurl = "https://hls-dhs-dss.ch"
# VD basic
url = "https://beta.hls-dhs-dss.ch/Search/Category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&language=fr"
# VD 100 results
url1 = "https://beta.hls-dhs-dss.ch/Search/Category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&language=fr&rows=100&firstIndex=0"
url_VD_C = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&firstIndex="
# 3: Vd AC+C
url_VD_AC_C = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&f_hls.lexicofacet_string=2%2F006800.006900.007200.&firstIndex="
# 4: VD AC
url_VD_AC = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.placefacet_string=1%2F00200.03000&f_hls.lexicofacet_string=2%2F006800.006900.007200.&firstIndex="
# all political entities:
# - baillage, châtellenie
# - canton
# - canton, département, république (1790-1813)
# - comté, landgraviat
# - etat (étranger): continent, partie de continent
# - état historique disparu
# - seigneurie
# - Ville médiévale
url_pe = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=score&sortOrder=desc&collapsed=true&r=1&f_hls.lexicofacet_string=2%2F006800.006900.007300.&f_hls.lexicofacet_string=2%2F006800.006900.007500.&f_hls.lexicofacet_string=2%2F006800.006900.007400.&f_hls.lexicofacet_string=2%2F006800.006900.007900.&f_hls.lexicofacet_string=2%2F006800.006900.008100.&f_hls.lexicofacet_string=2%2F006800.006900.008200.&f_hls.lexicofacet_string=2%2F006800.006900.008600.&f_hls.lexicofacet_string=2%2F006800.006900.008900.&rows=100&firstIndex="
# religious entities:
# - abbaye, couvent, monastère
# - archidiocèse
# - chapitre cathédral
# - chapitre collégial
# - commanderie
# - décanat, paroisse, pieve
# - évêché, diocèse
# - hospice
url_re = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=score&sortOrder=desc&collapsed=true&r=1&rows=100&f_hls.lexicofacet_string=2%2F006800.009500.009600.&f_hls.lexicofacet_string=2%2F006800.009500.009700.&f_hls.lexicofacet_string=2%2F006800.009500.009800.&f_hls.lexicofacet_string=2%2F006800.009500.009900.&f_hls.lexicofacet_string=2%2F006800.009500.010000.&f_hls.lexicofacet_string=2%2F006800.009500.010100.&f_hls.lexicofacet_string=2%2F006800.009500.010200.&f_hls.lexicofacet_string=2%2F006800.009500.010300.&firstIndex="

def get_dhs_search_results(search_url, rows_per_page=100):
    """returns a list of DHS search results with name & URL

    search_url should end with "&firstIndex=" to browse through the search results
    """
    article_id_regex = re.compile(r"articles/(.+?)/")
    entities_list = {}
    entities_page_url = search_url+"0"
    entities_page = r.get(entities_page_url)
    tree = html.fromstring(entities_page.content)
    entities_count = int(tree.cssselect(".hls-search-header__count")[0].text_content())
    for i in range(0,math.ceil(entities_count/rows_per_page)+1):
        print("Getting search results, firstIndex=",rows_per_page*i, "\nurl = ",entities_page_url)
        search_results = tree.cssselect(".search-result a")
        for c in search_results:
            cname = c.text_content().strip()
            page_url = c.xpath("@href")[0]
            print("url for ",cname,": ",page_url)
            entities_list[cname] = {
                "name": cname,
                "url" : "https://hls-dhs-dss.ch"+page_url
            }
            article_id_match = article_id_regex.search(page_url)
            if article_id_match:
                entities_list[cname]["id"] = "dhs-"+article_id_match.group(1)
            else:
                print("No id for "+cname)

        entities_page_url = search_url+str(i*rows_per_page)
        entities_page = r.get(entities_page_url)
        tree = html.fromstring(entities_page.content)
    return entities_list

tagged_entries = []

def add_dhs_text_and_tags(search_results, include_text=True, include_tags=True):
    counter=0
    # fetching all the pages
    for n,e in search_results.items():
        if "page" not in e:# and counter<5:
            print("Adding tags for: ", n, "counter: ", counter)
            page = r.get(e["url"])
            e["page"] = page
            pagetree = html.fromstring(e["page"].content)
            if include_text:
                e["text"] = reduce(lambda s,el: s+"\n\n"+el.text_content(), pagetree.cssselect(".hls-article-text-unit p"), "")
            if include_tags:
                e["tags"] = [{"tag":el.text_content(),"url":el.xpath("@href")[0]} for el in pagetree.cssselect(".hls-service-box-right a")]
            counter+=1
            tagged_entries.append(n)
            #search_results[n] = e
    print("done")

def format_dhs_results_to_political_entities(dhs_pe):
    for n,e in dhs_pe.items():
        if "page" in e:
            del e["page"]
    # regex to remove entité politique prefix:
    ep_regex = re.compile(r"Entités politiques / ")
    # fetching all the pages
    return [{
        "type": "PoliticalEntity",
        "dhsId": e["id"],
        "name": e["name"],
        "category": "",
        # "start": {
        #     "type":"exactDate",
        #     "date":"" 
        # },
        # "end": {
        #     "type":"exactDate",
        #     "date":""
        # },
        "dhsTags": [ep_regex.sub("", t["tag"]) for t in e["tags"]],
        "description": "",
        "sources": [e]
    } for n,e in dhs_pe.items() if n in tagged_entries]

dhs_political_entities = get_dhs_search_results(url_pe)
add_dhs_text_and_tags(dhs_political_entities, False)
formatted_political_entities = format_dhs_results_to_political_entities(dhs_political_entities)


dhs_religious_entities = get_dhs_search_results(url_re)
dhs_religious_entities = {k:v for k,v in dhs_religious_entities.items() if k not in dhs_political_entities}
# 268 to 231: 37 already are in political entities
add_dhs_text_and_tags(dhs_religious_entities, False)
formatted_religious_entities = format_dhs_results_to_political_entities(dhs_religious_entities)


with open('./DHS_political_entities_basis.json', 'w') as fp:
    json.dump(formatted_political_entities+formatted_religious_entities, fp, indent=2, ensure_ascii=False)


url_VD_AC_C = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&f_hls.lexicofacet_string=2%2F006800.006900.007200.&firstIndex="
dhs_communes_VD = get_dhs_search_results(url_VD_AC_C)
add_dhs_text_and_tags(dhs_communes_VD, False)
formatted_communes_VD = format_dhs_results_to_political_entities(dhs_communes_VD)
for c in formatted_communes_VD:
    c["start"] ={
      "type": "uncertainBoundedDate",
      "latest": "1850",
      "bestGuess": "1850"
    }
    c["end"] ={
      "type": "uncertainBoundedDate",
      "earliest": "1850"
    },
with open('./DHS_communes_VD_as_pe_basis.json', 'w') as fp:
    json.dump(formatted_communes_VD, fp, indent=2, ensure_ascii=False)


political_entity_template = {
    "type": "politicalEntity",
    "id": "",
    "name": "",
    "category": "",
    # "start": {
    #     "type":"exactDate",
    #     "date":"" 
    # },
    # "end": {
    #     "type":"exactDate",
    #     "date":""
    # },
    "tags": [],
    "description": "",
    "sources": []
}

""" 
communes_to_JSON = copy.deepcopy(communes_list)
for n,c in communes_to_JSON.items():
    c["name"] = n
communes_to_JSON = [c for n,c in communes_to_JSON.items()]

#with open('./communes_VD.json', 'w') as fp:
#    json.dump(communes_to_JSON, fp)

dtf = pd.DataFrame(communes_to_JSON)
dtf = dtf[['name', 'id', 'category', 'url']]
dtf.sort_values(by="name",inplace=True)
dtf.to_csv("DHS_communes_AC_C_VD.csv", sep=";", index=False) """