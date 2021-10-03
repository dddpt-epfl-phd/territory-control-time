

# %% Imports
import os

import fiona
import geopandas as gpd


path_prefix = "../"
working_directory = "BFS_geometries/"
os.chdir(path_prefix+working_directory)

gde1848_gdbfile="./gde1848_geodatabase/K4_HistGde.gdb"
g0g1848_gdbfile="./gde1848_geodatabase/g0g1848.gdb"


# %% Lakes geometries

hid_lakes = [
    10241, 10243, 10244, 10245, 10246,
    10247, 10248, 10249, 10250, 10251,
    10252, 10253, 10254, 10255, 10256,
    10257, 10258, 10259, 10260, 10261,
    10262, 10263, 10264, 10265, 10266,
    10267, 10270, 10284, 10287, 10288,
    10289, 10290, 10291, 10292, 10293,
    10294, 10295, 10296, 10297, 10298,
    10299, 16584, 16585
]

# %% list layers

layers = fiona.listlayers(gde1848_gdbfile)
layers

# %%
g0glayers = fiona.listlayers(g0g1848_gdbfile)
g0glayers

# %% load layers & inspect columns

for l in layers:
    layer = gpd.read_file(gde1848_gdbfile, layer = l)
    #print("\nlayer "+l)
    #print(layer.columns)
    layer.to_file('./geojson/'+l+'.geojson', driver='GeoJSON')  

# %% gde layer is layer 1

gde1848 = gpd.read_file(gde1848_gdbfile, layer = layers[1])

gde1848.plot()
# %%


print(fiona.listlayers(g0g1848_gdbfile))
g0g1848 = gpd.read_file(g0g1848_gdbfile)
print(g0g1848.shape)
g0g1848.head()

# %% to csv

gdeVD = gde1848.loc[gde1848["GdeKT"]=="VD"]
gdeVD = gdeVD[["GDEHISTID","GDENR","GdeName"]]
gdeVD.sort_values(by="GdeName", inplace=True)
gdeVD.to_csv("BFS_communes.csv",sep=";", index=False)

# %% g0g1848_gdbfile to given epsg 
espg = 4326
for l in layers:
    layer = gpd.read_file(gde1848_gdbfile, layer = l)
    #print("\nlayer "+l)
    #print(layer.columns)
    print("\nlayer "+l+" crs:")
    print(layer.crs)
    layer = layer.to_crs(epsg=espg)
    print("layer "+l+" shape:")
    print(layer.shape)
    layer.to_file(f'./geojson/epsg{espg}_'+l+'.geojson', driver='GeoJSON')  

# %% g0g1848_gdbfile to given epsg 
espg = 4326
for l in g0glayers:
    layer = gpd.read_file(g0g1848_gdbfile, layer = l)
    print("\nlayer "+l)
    print(layer.columns)
    layer = layer.to_crs(epsg=espg)
    print("layer "+l+" shape:")
    print(layer.shape)
    layer_no_lakes = layer[~layer.histid.isin(hid_lakes)]
    print("layer "+l+" shape after removing lakes:")
    print(layer_no_lakes.shape)
    layer_no_lakes.to_file(f'./geojson/epsg{espg}_'+l+'_no_lakes.geojson', driver='GeoJSON')  



# %% g0glayers got the right histId, gde1848 got the nice geometries:
# let's get the best of both world!


