# %%
import re

from graph_data_model import * 
from graph_utils import * 

tgraph = neo4j_connect()

HDate = HistoricalDate


# %%


# %% Dates



dates = [HDate.wrap(d["d"]) for d in tgraph.run("Match (d:HistoricalDate) where d.readableId=~'.+' return d")]
"""['conquete-vaud-par-berne',
 'fin-ancien-regime-suisse',
 'creation-principaute-neuchatel',
 'partage-seigneurie-grandson',
 'dissolution-seigneurie-grandson',
 'fondation-abbaye-lac-de-joux',
 'fin-conflit-abbayes-joux-st-claude']"""

dfondation_abbaye_joux = HDate.from_readable_id('fondation-abbaye-lac-de-joux', tgraph)
dfin_conflit_joux_claude = HDate.from_readable_id('fin-conflit-abbayes-joux-st-claude', tgraph)
dconquete_vaud_par_berne = HDate.from_readable_id('conquete-vaud-par-berne', tgraph)
dfin_ancien_regime = HDate.from_readable_id('fin-ancien-regime-suisse', tgraph)
dpartage_seigneurie_grandson = HDate.from_readable_id("partage-seigneurie-grandson", tgraph)


dreorganisation_districts_vaud = KnownDate(
    "reorganisation-districts-vaud",
    "2008"
)

# %% global list of objects to save in graph

# graph objects to create
goc = []
# graph objects to save
gos = []

# %% Seigneuries de Grandson, Champvent, Les Clées et La Sarraz

gpe_seigneurie_grandson = PoliticalEntity.from_name(tgraph,"Seigneurie de Grandson")[0]
gpe_baillage_grandson = PoliticalEntity.from_name(tgraph,"Baillage de Grandson")[0]
gpe_seigneurie_grandson.successors.add(gpe_baillage_grandson)

gpe_seigneurie_sarraz = PoliticalEntity.from_dhsId(tgraph, "007575")[0]
gpe_seigneurie_champvent = PoliticalEntity.from_dhsId(tgraph, "007572")[0]
gpe_seigneurie_clees = PoliticalEntity.from_dhsId(tgraph, "002534-2")[0]


gpe_baillage_yverdon = PoliticalEntity.from_name(tgraph,r"Baillage d\'Yverdon")[0]
gpe_baillage_rmmtier = PoliticalEntity.from_dhsId(tgraph,"007582")[0]

gpe_baillage_moudon = PoliticalEntity.from_dhsId(tgraph,"007578")[0]
gpe_baillage_moudon.dhsId+="-2" # châtellenie before baillage
gpe_baillage_moudon.name="Baillage de Moudon"

gos = gos +[
    gpe_seigneurie_grandson,
    gpe_baillage_grandson,
    gpe_seigneurie_sarraz,
    gpe_seigneurie_champvent,
    gpe_baillage_yverdon,
    gpe_baillage_rmmtier,
    gpe_baillage_moudon
]

# %% Communes de la Vallée de joux

"""
1 seule commune avant 16xx: le lieu

Communes de la vallée de joux:
contrôle:
-  1155-1204: contesté entre (à part l'Abbaye)
    abbaye de joux
    abbaye de Saint-Claude
- 1204-1536: abbaye de joux
- 1536-1565: baillage d'Yverdon
    - abbaye chez baillage romainmotier
- 1565-1798: baillage de Romainmôtier
"""

gpe_abbaye_joux = PoliticalEntity.from_dhsId(tgraph, "012134")[0]
gpe_abbaye_claude = PoliticalEntity.from_dhsId(tgraph, "007107")[0]

tabbaye = PoliticalEntity.from_dhsId(tgraph, "002609")[0]
tchenit = PoliticalEntity.from_dhsId(tgraph, "002610")[0]
tlieu = PoliticalEntity.from_dhsId(tgraph, "002611")[0]
gos = gos +[
    gpe_abbaye_joux,
    gpe_abbaye_claude,
    tabbaye,
    tchenit,
    tlieu
]

dhsa_vallee_joux = DHSArticle.scrape_from_dhs("007588")
dhsa_abbaye = DHSArticle.scrape_from_dhs("002609")
dhsa_lieu = DHSArticle.scrape_from_dhs("002611")
dhsa_abbaye_joux = DHSArticle.scrape_from_dhs("012134")
dhsa_clees = list(gpe_seigneurie_clees.sources)[0]

# 1155-1536 abbaye de joux controls l'abbaye
pc_abbaye_fondation = DirectControl()
pc_abbaye_fondation.controlled.add(tabbaye)
pc_abbaye_fondation.main_controller.add(gpe_abbaye_joux)
pc_abbaye_fondation.start.add(dfondation_abbaye_joux)
pc_abbaye_fondation.end.add(dconquete_vaud_par_berne)
pc_abbaye_fondation.sources.add(dhsa_abbaye)
goc.append(pc_abbaye_fondation)

# 1155-1204: contested joux vs saint-claude
pc_contested_joux_claude = ContestedControl()
pc_contested_joux_claude.controlled.add(tchenit)
pc_contested_joux_claude.controlled.add(tlieu)
pc_contested_joux_claude.controllers.add(gpe_abbaye_joux)
pc_contested_joux_claude.controllers.add(gpe_abbaye_claude)
pc_contested_joux_claude.main_controller.add(gpe_abbaye_joux)
pc_contested_joux_claude.start.add(dfondation_abbaye_joux)
pc_contested_joux_claude.end.add(dfin_conflit_joux_claude)
pc_contested_joux_claude.sources.add(dhsa_abbaye_joux)
pc_contested_joux_claude.sources.add(dhsa_vallee_joux)
goc.append(pc_contested_joux_claude)

# 1204-1536: direct joux by abbaye joux
pc_abbaye_joux = DirectControl()
pc_abbaye_joux.controlled.add(tchenit)
pc_abbaye_joux.controlled.add(tlieu)
pc_abbaye_joux.main_controller.add(gpe_abbaye_joux)
pc_abbaye_joux.start.add(dfin_conflit_joux_claude)
pc_abbaye_joux.end.add(dconquete_vaud_par_berne)
pc_abbaye_joux.sources.add(dhsa_lieu)
pc_abbaye_joux.sources.add(dhsa_abbaye_joux)
goc.append(pc_abbaye_joux)

# 1536-1566: direct abbaye by baillage de rmmtier
drmmtier_controls_joux = KnownDate()
drmmtier_controls_joux.date="1566"
drmmtier_controls_joux.readableId="baillage-romainmotier-controle-joux"
pc_rmmtier_abbaye = DirectControl()
pc_rmmtier_abbaye.controlled.add(tabbaye)
pc_rmmtier_abbaye.main_controller.add(gpe_baillage_rmmtier)
pc_rmmtier_abbaye.start.add(dconquete_vaud_par_berne)
pc_rmmtier_abbaye.end.add(dfin_ancien_regime)
pc_rmmtier_abbaye.sources.add(dhsa_abbaye)
goc.append(pc_rmmtier_abbaye)

# 1536-1566: direct lieu+chenit by clees (sous baillage d'yverdon)
pc_clees_joux = DirectControl()
pc_clees_joux.controlled.add(tchenit)
pc_clees_joux.controlled.add(tlieu)
pc_clees_joux.main_controller.add(gpe_seigneurie_clees)
pc_clees_joux.start.add(dconquete_vaud_par_berne)
pc_clees_joux.end.add(drmmtier_controls_joux)
pc_clees_joux.sources.add(dhsa_vallee_joux)
pc_clees_joux.sources.add(dhsa_clees)
goc.append(pc_clees_joux)

# 1566-1798: direct joux by baillage de romainmotier
pc_rmmtier_joux = DirectControl()
pc_rmmtier_joux.controlled.add(tabbaye)
pc_rmmtier_joux.controlled.add(tchenit)
pc_rmmtier_joux.controlled.add(tlieu)
pc_rmmtier_joux.main_controller.add(gpe_baillage_rmmtier)
pc_rmmtier_joux.start.add(drmmtier_controls_joux)
pc_rmmtier_joux.end.add(dfin_ancien_regime)
pc_rmmtier_joux.sources.add(dhsa_vallee_joux)
goc.append(pc_rmmtier_joux)


# %% Abbaye du lac de Joux

"""
Abbaye de Joux:
- 1126: grandson
- <1234: La Sarraz
- 1334/1344: chatellenie des clées (sous les savoie)
- 1536 baillage d'Yverdon
- 1566 baillage de romainmotier
"""

dfondation_seigneurie_sarraz = KnownDate.new(
        "fondation-seigneurie-la-sarraz",
        "1049"
)

dvente_joux_savoie = UncertainPossibilitiesDate.new(
    "vente-joux-savoie",
    [
        KnownDate.new("vente-joux-1334", 1334),
        KnownDate.new("vente-joux-1344", 1344)
    ]
)

# 1126: grandson
pc_grandson_abbjoux = DirectControl.new(
    gpe_seigneurie_grandson,
    gpe_abbaye_joux,
    dfondation_abbaye_joux,
    dpartage_seigneurie_grandson,
    dhsa_vallee_joux
)

# <1234: La Sarraz
pc_sarraz_abbjoux = DirectControl.new(
    gpe_seigneurie_sarraz,
    gpe_abbaye_joux,
    dpartage_seigneurie_grandson,
    dvente_joux_savoie,
    [dhsa_vallee_joux, dhsa_lieu]
)

# 1334/1344-1536: chatellenie des clées (sous les savoie)
pc_sarraz_abbjoux = DirectControl.new(
    gpe_seigneurie_clees,
    gpe_abbaye_joux,
    dvente_joux_savoie,
    dconquete_vaud_par_berne,
    [dhsa_vallee_joux, dhsa_lieu]
)

# %% seigneurie de la Sarraz

"""
seigneurie/baronnie de la sarraz:
- 1049: fondation par famille Grandson
- 1234: partage Grandson en 3: indép.
    - 13ième: famille montferrand
- 1461: seigneurie devient baronnie
- 1536: baillage de moudon
- 1542: famille Gingins
    -> seigneur de divonne+châtelard
- 1598: baillage de romainmotier
"""


dhsa_seigneurie_grandson = DHSArticle.from_dhsId(tgraph, "007574")

dhsa_seigneurie_sarraz = DHSArticle.from_dhsId(tgraph, "007575")


# seigneurie de 1049 à 1461
dsarraz_baronnie=KnownDate.new(
    "sarraz-devient-baronnie",
    "1461"
)
for d in gpe_seigneurie_sarraz.start:
    gpe_seigneurie_sarraz.start.remove(d)
for d in gpe_seigneurie_sarraz.end:
    gpe_seigneurie_sarraz.end.remove(d)
gpe_seigneurie_sarraz.start.add(dfondation_seigneurie_sarraz)
gpe_seigneurie_sarraz.end.add(dsarraz_baronnie)

# 11ième-1234: famille Grandson
pc_grandson_sarraz = DirectControl.new(
    gpe_seigneurie_grandson,
    gpe_seigneurie_sarraz,
    dfondation_seigneurie_sarraz,
    dpartage_seigneurie_grandson,
    dhsa_seigneurie_grandson
)

# 1461: devient baronnie
gpe_baronnie_sarraz = PoliticalEntity.new(
    "Baronnie de La Sarraz",
    "baronnie",
    dsarraz_baronnie,
    dfin_ancien_regime,
    dhsa_seigneurie_sarraz,
    gpe_seigneurie_sarraz,
    "007575-2",
)

drmmtier_controle_sarraz = KnownDate.new("rmmtier-controle-sarraz", "1598")

# 1536: baillage de moudon controle la sarraz
pc_grandson_sarraz = DirectControl.new(
    gpe_baillage_moudon,
    gpe_seigneurie_sarraz,
    dconquete_vaud_par_berne,
    drmmtier_controle_sarraz,
    dhsa_seigneurie_sarraz
)
# 1598: baillage de rmmtier controle la sarraz
pc_grandson_sarraz = DirectControl.new(
    gpe_baillage_rmmtier,
    gpe_seigneurie_sarraz,
    drmmtier_controle_sarraz,
    dfin_ancien_regime,
    dhsa_seigneurie_sarraz
)

# %% Comté de Genève

dhsa_dynastie_geneve = DHSArticle.scrape_from_dhs("019515")

dfondation_comte_geneve = UncertainBoundedDate.new(
    "fondation-comte-geneve",
    latest="1034"
)

dfin_comte_geneve = UncertainBoundedDate.new(
    "fin-comte-geneve",
    "1402",
    "1798",
    best_guess = "1402"
)

gpe_comte_geneve = PoliticalEntity.new(
    "Comté de Genève",
    "comté",
    dfondation_comte_geneve,
    dfin_comte_geneve,
    dhsa_dynastie_geneve,
    dhsId="dhs-019515"
)

# %% Comté et duché de Savoie


gpe_comte_savoie = PoliticalEntity.from_name(tgraph, "Savoie")[0]
gpe_comte_savoie.name="Comté de Savoie"
gpe_comte_savoie.category="comte"

dfondation_savoie = KnownDate.new(
    "fondation-comte-savoie",
    "1160"
)
dcomte_savoie_devient_duche = KnownDate.new(
    "comte-savoie-devient-duche",
    "1416"
)
dfin_duche_savoie = KnownDate.new(
    "fin-duche-savoie",
    "1860"
)
gpe_comte_savoie.start.add(dfondation_savoie)
gpe_comte_savoie.end.add(dcomte_savoie_devient_duche)

gpe_duche_savoie = PoliticalEntity.new(
    "Duché de savoie",
    "duche",
    dcomte_savoie_devient_duche,
    dfin_duche_savoie,
    list(gpe_comte_savoie.sources),
    gpe_comte_savoie,
    "dhs-006641-2"
)

# %% Seigneurie des Clées

"""
seigneurie des clées
suzerains:
- <1232: duc de Bourgogne
- 1232: comte de Genève
- 1237 ?Jean de Chalon? Comte de Genève?
- 1260: Comte de Savoie
- 1416: duc de savoie
- 1475 ou 1536: chez les bernois...
"""

gpe_duche_bourgogne = PoliticalEntity.from_dhsId(tgraph,"007281")[0]

dbourgogne_controle_clees = UncertainBoundedDate.new(
    "bourgogne-controle-clees",
    latest="1232",
    best_guess="1000"
)

dgeneve_controle_clees = KnownDate.new(
    "comte-geneve-controle-clees",
    "1232"
)

dsavoie_controle_clees = KnownDate.new(
    "comte-geneve-controle-clees",
    "1260"
)


# <1232: duc de bourgnogne controle les clées
pc_bourgnogne_clees = DirectControl.new(
    gpe_duche_bourgogne,
    gpe_seigneurie_clees,
    dbourgogne_controle_clees,
    dgeneve_controle_clees,
    dhsa_clees
)
# 1232: comte de geneve controle les clées
pc_comte_geneve_clees = DirectControl.new(
    gpe_comte_geneve,
    gpe_seigneurie_clees,
    dgeneve_controle_clees,
    dsavoie_controle_clees,
    dhsa_clees
)
# 1260: comte de savoie controle les clées
pc_comte_savoie_clees = DirectControl.new(
    gpe_comte_savoie,
    gpe_seigneurie_clees,
    dsavoie_controle_clees,
    dcomte_savoie_devient_duche,
    [dhsa_clees]+list(gpe_comte_savoie.sources)
)
# 1416: comte savoie devient duche
pc_duche_savoie_clees = DirectControl.new(
    gpe_duche_savoie,
    gpe_seigneurie_clees,
    dcomte_savoie_devient_duche,
    dconquete_vaud_par_berne,
    [dhsa_clees]+list(gpe_comte_savoie.sources)
)
# 1536: conquête bernoise
pc_baillaye_yverdon_clees = DirectControl.new(
    gpe_baillage_yverdon,
    gpe_seigneurie_clees,
    dconquete_vaud_par_berne,
    dfin_ancien_regime,
    [dhsa_clees]+list(gpe_baillage_yverdon.sources)
)





#%%