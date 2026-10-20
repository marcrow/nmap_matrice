# seg_matrix — matrice de cloisonnement + Mermaid + rapport HTML

## Workflow

1. **Inventaire** `inventaire.csv` (separateur `;`, en-tete optionnel), `type` en snake_case :
   ```
   ip;zone;type;nom
   10.0.2.1;interne;vm;app-01
   ```

2. **Scans** — un scan *depuis chaque source*, sortie nommee par l'IP source :
   ```bash
   nmap -Pn -p- --open -oA "$SRC_IP" <cibles>   # via proxychains/SOCKS si pivot
   ```
   `-oA` produit `<SRC_IP>.xml/.gnmap/.nmap`. Priorite de parsing : xml > gnmap > nmap.

   Machines multi-interfaces (admin, service, iLO, supervision...) : une ligne par
   interface, meme `nom`. Sans nom, la machine = l'IP. Une IP en double est une erreur.
   ```
   10.0.2.1;T1-service;vm;app-01
   10.9.0.1;T0-admin;vm;app-01
   10.8.0.1;ilo;ilo;app-01
   ```

3. **Generation** :
   ```bash
   python3 seg_matrix.py -i inventaire.csv -s ./scans/ -o ./report/ --host-graph
   ```

## Exclusion du self
Toutes les interfaces de la machine source sont systematiquement retirees des resultats :
un scan qui se voit lui-meme en local affiche typiquement de nombreux ports "open"
qui fausseraient la matrice.

## Sorties
- `report.html`         : **rapport standalone a onglets** (Vue globale / Par source / Anomalies)
- `matrix_hosts.md/.csv`: matrice consolidee hote -> hote
- `matrix_zones.md`     : matrice consolidee zone -> zone
- `exposure_targets.md` : vue orientee cible (qui accede a quoi)
- `segmentation.mmd`    : Mermaid global zone
- `mermaid/<ip>.mmd`    : Mermaid par source
- `segmentation_hosts.mmd` : Mermaid global hote (option `--host-graph`)
- `findings.md`         : expositions inter-zones + anomalies


## Mode -Pn
Tes scans en `-Pn` sont pris en charge nativement (et meme recommandes) : l'option
est auto-detectee depuis l'entete des fichiers nmap, ou forcable via `--pn`. En mode
-Pn l'etat "host up" (toujours vrai) est ignore ; le verdict repose uniquement sur
l'etat des ports (open/closed/filtered). Avantage : les cibles bloquees apparaissent
en `filtered` (-> bloque) au lieu d'etre absentes.

## Verdicts
- `OPEN`  : >=1 port open -> service joignable
- `o`     : ports closed (RST) -> flux L4 admis jusqu'a l'hote (cloisonnement permeable, sans service)
- `~`     : vivant (ping/ARP), aucun port qui passe -> hors `-Pn` uniquement
- `x`     : filtered / down -> bloque
- `.`     : cible absente de la sortie du scan (non vu)

## Graphes
La zone colore le fond de son cadre. Chaque machine multi-interfaces a sa propre
couleur de noeud, et ses interfaces sont reliees par un pointille gris ; les machines
a une seule interface restent en blanc borde de la couleur de zone.

## Rapport HTML
`report.html` charge mermaid.js depuis un CDN (jsdelivr) : prevoir une connexion au
premier affichage. Pour un livrable hors-ligne, bundler mermaid.min.js en local et
remplacer l'URL du `<script>`.
