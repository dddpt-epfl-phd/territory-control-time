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
baseurl = "https://beta.hls-dhs-dss.ch"
# VD basic
url = "https://beta.hls-dhs-dss.ch/Search/Category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&language=fr"
# VD 100 results
url1 = "https://beta.hls-dhs-dss.ch/Search/Category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&language=fr&rows=100&firstIndex=0"
url_VD_C = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&firstIndex="
# 3: Vd AC+C
url_VD_AC_C = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.lexicofacet_string=2%2F006800.006900.007800.&f_hls.placefacet_string=1%2F00200.03000&f_hls.lexicofacet_string=2%2F006800.006900.007200.&firstIndex="
# 4: VD AC
url_VD_AC = "https://hls-dhs-dss.ch/fr/search/category?text=*&sort=hls.title_sortString&sortOrder=asc&collapsed=true&r=1&language=fr&rows=100&f_hls.placefacet_string=1%2F00200.03000&f_hls.lexicofacet_string=2%2F006800.006900.007200.&firstIndex="


def get_dhs_search_results(search_url, rows_per_page=100):
    """returns a list of DHS search results with name & URL

    search_url should end with "&firstIndex=" to browse through the search results
    """
    article_id_regex = re.compile(r"articles/(.+?)/")
    communes_list = {}
    communes_page_url = search_url+"0"
    communes_page = r.get(communes_page_url)
    tree = html.fromstring(communes_page.content)
    communes_count = int(tree.cssselect(".hls-search-header__count")[0].text_content())
    for i in range(0,math.ceil(communes_count/rows_per_page)+1):
        print("Getting communes search results, firstIndex=",rows_per_page*i, "\nurl = ",communes_page_url)
        search_results = tree.cssselect(".search-result a")
        for c in search_results:
            cname = c.text_content().strip()
            page_url = c.xpath("@href")[0]
            print("url for ",cname,": ",page_url)
            communes_list[cname] = {
                "url" : "https://hls-dhs-dss.ch"+page_url
            }
            article_id_match = article_id_regex.search(page_url)
            if article_id_match:
                communes_list[cname]["id"] = "dhs-"+article_id_match.group(1)
            else:
                print("No id for "+cname)

        communes_page_url = search_url+str(i*rows_per_page)
        communes_page = r.get(communes_page_url)
        tree = html.fromstring(communes_page.content)
    return communes_list

anciennes_communes = get_dhs_search_results(url_VD_AC)
for n,ac in anciennes_communes.items():
    ac["category"] = "ancienne commune"
communes = get_dhs_search_results(url_VD_C)
for n,c in communes.items():
    c["category"] = "commune"

print("len(anciennes_communes): ", len(anciennes_communes))
print("len(communes): ", len(communes))

communes_list = dict(anciennes_communes,**communes)

# fetching all the pages
#for n,c in communes_list.items():
#    print("Getting commune ", n)
#    if "page" not in c:
#        print(c)
#        da = r.get(baseurl+c["url"])
#        c["page"] = da

communes_to_JSON = copy.deepcopy(communes_list)
for n,c in communes_to_JSON.items():
    c["name"] = n
communes_to_JSON = [c for n,c in communes_to_JSON.items()]

#with open('./communes_VD.json', 'w') as fp:
#    json.dump(communes_to_JSON, fp)

dtf = pd.DataFrame(communes_to_JSON)
dtf = dtf[['name', 'id', 'category', 'url']]
dtf.sort_values(by="name",inplace=True)
dtf.to_csv("DHS_communes_AC_C_VD.csv", sep=";", index=False)