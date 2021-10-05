# Political Territorial Control through Time

This project's main aim is to propose a data model to encode control of land over time and propose an interactive interface to explore and search in a given control dataset. [__Interface accessible here.__](https://dddpt-epfl-phd.github.io/territory-control-time/)



The data model should englobe the following aspects of political control:
- generic polities at all level of the control ladder (small lordships, administrative subunits, duchies, etc...)
- different modes of control relationships (simple control, shared control, contested, etc...)
- events delimitating control relationships (date, duration, description)
- sources, references and how to document polities, relationships and events
- uncertainty and ongoing discussions on polities, relationships and events in poorly documented times

As a practical case study, we will create a dataset for political territorial control relationships in Switzerland from 1000 to today based on the Historical Dictionary of Switzerland (DHS).

## folders structures

- `BFS_geometries/`: code to prepare the territories geometries from 1848 municipalities geometries from the swiss Bundesamt Für Statistik (BFS).
- `BFS_hist_list_communes/`: code to prepare the control relations in Switzerland 1848-present from the historicized list of municipalities of BFS.
- `DHS_communes/`: code to scrape DHS pages of municipalities
- `political_control/`: data model for political control
- `web/`: web interface related code
