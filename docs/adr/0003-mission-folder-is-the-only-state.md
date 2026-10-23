# The mission folder is the only state, no database

All state lives in one mission folder of plain files (`inventory.csv`, `flow_policy.csv`, `port_groups.csv`, `scans/<src_ip>/*.xml`), and the report is regenerated from it. This holds for the future local web app too: it reads and writes those same files rather than a database. Missions run offline on client sites and get archived, copied and diffed as folders; plain files stay editable in a spreadsheet, need nothing to deploy, and keep the CLI and the app on a single source of truth.
