
# %% 

from database_population_1 import *



gpe_second_royaume_bourgogne = PoliticalEntity.from_dhsId("006620")
gpe_second_royaume_bourgogne.name="Second Royaume de Bourgogne"
dfondation_second_royaume_bourgogne = KnownDate.new(
    "fondation-second-royaume-bourgogne",
    888
)
gpe_second_royaume_bourgogne.start.add(dfondation_second_royaume_bourgogne)
dfin_second_royaume_bourgogne = KnownDate.new(
    "fin-second-royaume-bourgogne",
    1032
)
gpe_second_royaume_bourgogne.end.add(dfin_second_royaume_bourgogne)

# %% Prieuré de Romainmôtier

gpe_prieure_rmmtier = PoliticalEntity.from_dhsId(tgraph, "011867")[0]
gpe_prieure_rmmtier.name="Prieuré de Romainmôtier"

dfondation_rmmtier = UncertainAroundDate.new(
    "fondation-prieure-romainmotier",
    "450",
    "10Y"
)
dfin_prieure_rmmtier = KnownDate.new(
    "fondation-prieure-romainmotier",
    "15370127"
)
gpe_prieure_rmmtier.start.add(dfondation_rmmtier)
gpe_prieure_rmmtier.end.add(dfin_prieure_rmmtier)

# district d'orbe
gpe_district_orbe = PoliticalEntity.new(
    "District d'Orbe",
    "district",
    dfin_ancien_regime,
    dreorganisation_districts_vaud,
    DHSArticle.from_dhsId(tgraph, "007580")
)

# %% villages du prieure/baillage de  romainmotier


# %% territoire always part of rmmtier
# ===========================================================
trmmtier = PoliticalEntity.from_dhsId(tgraph, "002544")[0]
trmmtier.name="Romainmôtier"
for s in trmmtier.start:
    trmmtier.start.remove(s)
trmmtier.start.add(dfondation_rmmtier)

tcroy = Territory.from_dhsId(tgraph, "002536")[0]
tenvy = Territory.from_dhsId(tgraph, "003326")[0] # fondation <1216, fusion 1970
tenvy.set_first_mention("1216")
tbretonnieres = Territory.from_dhsId(tgraph, "002532")[0] # fondation <1154
tbretonnieres.set_first_mention("1154")
tpremier = Territory.from_dhsId(tgraph, "002542")[0]
tpremier.set_first_mention("1396")
tjuriens = Territory.from_dhsId(tgraph, "002537")[0] # fondation <1263
tjuriens.set_first_mention("1263")
tlapraz = Territory.from_dhsId(tgraph, "002541")[0]
tlapraz.set_first_mention("996")

t_of_rmmtier_tjrs = [trmmtier, tcroy, tenvy, tbretonnieres, tpremier, tjuriens, tlapraz]

# 450-1537: prieuré de romainmotier, tjrs
pc_prieure_rmmtier_tjrs = DirectControl.new(
    gpe_prieure_rmmtier,
    [t_of_rmmtier_tjrs],
    dfondation_rmmtier,
    dfin_prieure_rmmtier,
    [s for t in t_of_rmmtier_tjrs for s in t.sources]
)

# %% territoire donnation 1011 du royaume de bourgogne à rmmtier
# ===========================================================

tbofflens = Territory.from_dhsId(tgraph, "002531")[0] # fondation <1007
tbofflens.set_first_mention("1007")
tagiez = Territory.from_dhsId(tgraph, "002526")[0] # fondation <1011
tagiez.set_first_mention("1011")
t_of_rmmtier_1011 = [tbofflens, tagiez]

dbourgogne_controle_bofflens = UncertainBoundedDate.new(
    "bourgogne-controle-bofflens",
    "888",
    "1011",
    "888"
)
ddonation_bourgogne_rmmtier = KnownDate(
    "donation-roi-bourgogne-rmmtier",
    "1011"
)

pc_bourgogne_1011 = DirectControl.new(
    gpe_second_royaume_bourgogne,
    t_of_rmmtier_1011,
    dbourgogne_controle_bofflens,
    ddonation_bourgogne_rmmtier,
    [s for t in t_of_rmmtier_1011 for s in t.sources]
)

# 1011-1537: agiez+bofflens au prieuré de romainmotier
pc_prieure_rmmtier_tjrs = DirectControl.new(
    gpe_prieure_rmmtier,
    [t_of_rmmtier_1011],
    ddonation_bourgogne_rmmtier,
    dfin_prieure_rmmtier,
    [s for t in t_of_rmmtier_1011 for s in t.sources]
)

# %% Arnex: donné en 1049 à rmmtier par seigneur de grnadson
# ===========================================================

tarnex = Territory.from_dhsId(tgraph, "002527")[0] # fondation <1049
dfirst_mention_arnex = tarnex.set_first_mention("1049")

pc_grandson_arnex = DirectControl.new(
    gpe_seigneurie_grandson,
    tarnex,
    dfirst_mention_arnex,
    dfirst_mention_arnex,
    list(tarnex.sources)
)
pc_prieure_rmmtier_arnex = DirectControl.new(
    gpe_prieure_rmmtier,
    tarnex,
    dfirst_mention_arnex,
    dfin_prieure_rmmtier,
    list(tarnex.sources)
)

# %% Vaulion: à rmmtier en 1097
# ===========================================================

tvaulion = Territory.from_dhsId(tgraph, "002548")[0]

dirst_mention_vaulion = tvaulion.set_first_mention(1097)

pc_prieure_rmmtier_vaulion = DirectControl.new(
    gpe_prieure_rmmtier,
    tvaulion,
    dirst_mention_vaulion,
    dfin_prieure_rmmtier,
    list(tvaulion.sources)
)




# %% baillage de romainmotier + district d'orbe
# ===========================================================


t_of_baillage_rmmtier_district_orbe = [t for t in
    t_of_rmmtier_tjrs+
    t_of_rmmtier_1011+
    [tvaulion, tarnex]
]

# 1536-1798: baillage romainmotier
pc_baillage_rmmtier = DirectControl.new(
    gpe_baillage_rmmtier,
    t_of_baillage_rmmtier_district_orbe,
    dfin_prieure_rmmtier,
    dfin_ancien_regime,
    [s for t in t_of_baillage_rmmtier_district_orbe for s in t.sources]
)

# 1798-2006: district d'orbe
pc_district_orbe = DirectControl.new(
    gpe_district_orbe,
    t_of_baillage_rmmtier_district_orbe,
    dfin_ancien_regime,
    dreorganisation_districts_vaud,
    [s for t in t_of_baillage_rmmtier_district_orbe for s in t.sources]
)


# %% Vallorbe
# ===========================================================

"""
Vallorbe, suzerain
- 1139: rmmtier
- 1537-1543 baillage de rmmtier
- 1543: baillage de rmmtier, chatellenie
- 1798: district d'orbe
"""

tvallorbe = Territory.from_dhsId(tgraph, "002547")[0]
tvallorbe.set_first_mention("1139")

dfondation_chatellenie_vallorbe = KnownDate.new(
    "fondation-chatellenie-vallorbe"
    "1543"
)

# 1139-1537: prieuré rmmtier > vallorbe
pc_prieure_rmmtier_vallorbe = DirectControl.new(
    gpe_prieure_rmmtier,
    tvallorbe,
    list(tvallorbe.start)[0],
    dfin_prieure_rmmtier
)

# 1537-1543: baillage rmmtier > vallorbe
pc_baillage_rmmtier_vallorbe = DirectControl.new(
    gpe_baillage_rmmtier,
    tvallorbe,
    dfin_prieure_rmmtier,
    dfondation_chatellenie_vallorbe,
    tvallorbe.sources
)

gpe_chatellenie_vallorbe = PoliticalEntity.new(
    "Châtellenie de Vallorbe",
    "chatellenie",
    dfondation_chatellenie_vallorbe,
    dfin_ancien_regime,
    tvallorbe.sources,
    dhsId="dhs-002547-2"
)

# 1543-1798 chatellenie de vallorbe > vallorbe
pc_chatellenie_vallorbe = DirectControl.new(
    gpe_chatellenie_vallorbe,
    tvallorbe,
    dfondation_chatellenie_vallorbe,
    dfin_ancien_regime,
    tvallorbe.sources
)

# 1543-1798 baillage de rmmtier controle chatellenie de vallorbe
pc_baillage_rmmtier_chat_vallorbe = DirectControl.new(
    gpe_baillage_rmmtier,
    gpe_chatellenie_vallorbe,
    dfondation_chatellenie_vallorbe,
    dfin_ancien_regime,
    tvallorbe.sources
)

# %% eveche de Lausanne
# ===========================================================

gpe_eveche_lausanne = PoliticalEntity.from_dhsId("008559")
gpe_eveche_lausanne.name = "Évêché de Lausanne"
dfondation_eveche_lausanne = UncertainBoundedDate.new(
    "fondation-eveche-lausanne",
    latest="888",
    best_guess="888"
)

for d in gpe_eveche_lausanne.start:
    gpe_eveche_lausanne.start.remove(d)
gpe_eveche_lausanne.start.add(dfondation_eveche_lausanne)
gpe_eveche_lausanne.end.add(dconquete_vaud_par_berne)


# %% Abbaye de St-Maurice
# ===========================================================

gpe_abbaye_maurice = PoliticalEntity.from_dhsId("011411")
gpe_abbaye_maurice.name = "Abbaye de Saint-Maurice"
dfondation_abbaye_maurice = KnownDate.new(
    "fondation-abbaye-maurice",
    "515"
)

for d in gpe_abbaye_maurice.start:
    gpe_abbaye_maurice.start.remove(d)
gpe_abbaye_maurice.start.add(dfondation_abbaye_maurice)
gpe_abbaye_maurice.end.add(dconquete_vaud_par_berne)

# %% district cossonay
dfondation_baronnie_cossonay = UncertainBoundedDate.new(
    "fondation-baronnie-cossonay"
    "1000",
    "1100",
    "1000"
)
dsavoie_controle_cossonay = UncertainBoundedDate.new(
    "savoie-controle-cossonay"
    "1406",
    "1421",
    "1406"
)

gpe_baronnie_cossonay = PoliticalEntity.from_dhsId("007573")
gpe_baronnie_cossonay.name="Baronnie de Cossonay"
gpe_baronnie_cossonay.category="baronnie"
for d in gpe_baronnie_cossonay.start:
    gpe_baronnie_cossonay.start.remove(d)
gpe_baronnie_cossonay.start.add(dfondation_baronnie_cossonay)
gpe_baronnie_cossonay.end.add(dsavoie_controle_cossonay)

gpe_chatellenie_cossonay = PoliticalEntity.new(
    "Châtellenie de Cossonay",
    "chatellenie",
    dsavoie_controle_cossonay,
    dfin_ancien_regime,
    gpe_baronnie_cossonay.sources,
    gpe_baronnie_cossonay,
    "dhs-007573-2"
)

gpe_district_cossonay = PoliticalEntity.new(
    "District de Cossonay",
    "district",
    dfin_ancien_regime,
    dreorganisation_districts_vaud,
    gpe_baronnie_cossonay.sources,
    gpe_chatellenie_cossonay,
    "dhs-007573-3"
)

"007573"

# %% Ferreyres
# ===========================================================

"""
Ferreyres, controlé par:
- <1000, partagé entre
    église de Lausanne (évêque?)
    romainmotier
    abbaye de st-maurice
- 1000: contesté Grandson-rmmtier
- 1130: rmmtier vvvvvvvvvvvvvAAAAAAAAAA
- 1141: La Sarraz
- 1536: baillage de rmmtier
- 1798: district de cossonay

"""

tferreyres = Territory.from_dhsId("002333")
tferreyres.set_first_mention("814")


drmmtier_grandson_conteste_ferreyre = UncertainAroundDate.new(
    "rmmtier-grandson-controle-conteste-ferreyre",
    "1000",
    "20Y"
)
drmmtier_controle_ferreyre = KnownDate.new(
    "rmmtier-controle-ferreyre",
    "1130"
)
dsarraz_controle_ferreyre = KnownDate.new(
    "lasarraz-controle-ferreyre",
    "1141"
)

# <1000, evec de lausanne, abb de st-maurice & rmmtier
pc_lausanne_stmaurice_rmmtier_controle_ferreyre = SharedControl.new(
    gpe_prieure_rmmtier,
    [gpe_prieure_rmmtier, gpe_eveche_lausanne, gpe_abbaye_maurice],
    tferreyres,
    list(tferreyres.start)[0],
    drmmtier_grandson_conteste_ferreyre,
    tferreyres.sources
)

# 1000-1130: conteste grandson-rmmtier
pc_rmmtier_grandson_conteste_ferreyre = ContestedControl.new(
    gpe_prieure_rmmtier,
    [gpe_prieure_rmmtier, gpe_seigneurie_grandson],
    tferreyres,
    drmmtier_grandson_conteste_ferreyre,
    drmmtier_grandson_conteste_ferreyre,
    tferreyres.sources
)

# 1130-1141: rmmtier controle ferreyres
pc_rmmtier_controle_ferreyre = DirectControl.new(
    gpe_prieure_rmmtier,
    tferreyres,
    drmmtier_grandson_conteste_ferreyre,
    dsarraz_controle_ferreyre,
    tferreyres.sources
)

# 1141-1537: seigneurie la sarraz controle ferreyres (with baronnie transition)
pc_sarraz_controle_ferreyre = DirectControl.new(
    gpe_seigneurie_sarraz,
    tferreyres,
    dsarraz_controle_ferreyre,
    dsarraz_baronnie,
    list(tferreyres.sources)+list(gpe_seigneurie_sarraz.sources)
)
pc_sarraz_baronnie_controle_ferreyre = DirectControl.new(
    gpe_baronnie_sarraz,
    tferreyres,
    dsarraz_baronnie,
    dfin_prieure_rmmtier,
    list(tferreyres.sources)+list(gpe_seigneurie_sarraz.sources)
)

# 1537-1798 baillage rmmtier
pc_baillage_rmmtier_controle_ferreyre = DirectControl.new(
    gpe_baillage_rmmtier,
    tferreyres,
    dfin_prieure_rmmtier,
    dfin_ancien_regime,
    tferreyres.sources
)

# 1798: district cossonay
pc_district_cossonay_controle_ferreyre = DirectControl.new(
    gpe_district_cossonay,
    tferreyres,
    dfin_ancien_regime,
    dreorganisation_districts_vaud,
    tferreyres.sources
)

# %% La Sarraz (territoire)
# ===========================================================

"""
territoire de la sarraz:
- <1049: prieuré de rmmtier
- 1049-1798: seigneurie&baronnie de La sarraz
- 1798: district de cossonay
"""

tsarraz = Territory.from_dhsId("002348")
tsarraz.set_first_mention("1049")

# <1049: rmmtier controle sarraz
pc_rmmtier_controle_sarraz = DirectControl.new(
    gpe_prieure_rmmtier,
    tsarraz,
    list(tsarraz.start)[0],
    dfondation_seigneurie_sarraz,
    tsarraz.sources
)

# 1049-1461: seigneurie sarraz
pc_seigneurie_sarraz_controle_sarraz = DirectControl.new(
    gpe_seigneurie_sarraz,
    tsarraz,
    dfondation_seigneurie_sarraz,
    dsarraz_baronnie,
    tsarraz.sources
)

# 1461-1798: seigneurie sarraz
pc_baronnie_sarraz_controle_sarraz = DirectControl.new(
    gpe_baronnie_sarraz,
    tsarraz,
    dsarraz_baronnie,
    dfin_ancien_regime,
    tsarraz.sources
)

# 1798: district cossonay > sarraz
pc_district_cossonay_controle_sarraz = DirectControl.new(
    gpe_district_cossonay,
    tsarraz,
    dfin_ancien_regime,
    dreorganisation_districts_vaud,
    tsarraz.sources
)

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% 

# %% Seigneurie de Champvent


gpe_seigneurie_champvent

gpe_territoires_champvent = Territory.from_name(tgraph,
    "(Champvent|Mathod|Susc|Orges|Vugelles|Vuiteb|Sainte-Croix|Bullet)"
)

# %% Seigneuries du baillage d'Yverdon

"""
Baulmes
Belmont
Chavornay
Les Clées
Donneloye
Essertines
Saint-Martin
Sainte-Croix
Yverdon

anciennes seigneuries
Ballaigues
Bavois
Bercher
Bioley-Magnoux
Champvent
Chanéaz
Corcelles-sur-Chavornay
Correvon
Cronay
Ependes
Essert-Pittet
La Mothe
Lignerolle
Mathod
Mézery
Molondin
Orzens
Pailly
Vuarrens
"""