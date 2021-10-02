

# %% Imports


import fiona
import geopandas as gpd


gde1848_gdbfile="./gde1848_geodatabase/K4_HistGde.gdb"
g0g1848_gdbfile="./gde1848_geodatabase/g0g1848.gdb"

# %% list layers


layers = fiona.listlayers(gde1848_gdbfile)
layers

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

# to given epsg 
espg = 4326
for l in layers:
    layer = gpd.read_file(gde1848_gdbfile, layer = l)
    #print("\nlayer "+l)
    #print(layer.columns)
    print("\nlayer "+l+" crs:")
    print(layer.crs)
    layer = layer.to_crs(epsg=espg)
    print("layer "+l+" new crs:")
    print(layer.crs)
    layer.to_file(f'./geojson/epsg{espg}_'+l+'.geojson', driver='GeoJSON')  
