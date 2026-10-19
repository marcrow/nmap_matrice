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

3. **(Optionnel) Alias multi-interfaces** `alias.csv` — pour exclure les autres pattes
   d'un meme hote qui se verrait lui-meme dans son scan :
   ```
   ip_principale;ip_secondaire
   10.0.2.1;192.168.50.1
   ```

4. **Generation** :
   ```bash
   python3 seg_matrix.py -i inventaire.csv -s ./scans/ -o ./report/ --aliases alias.csv --host-graph
   ```

## Exclusion du self
L'IP source (et ses alias eventuels) est systematiquement retiree des resultats :
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
- `o`     : ports closed / host up -> flux admis jusqu'a l'hote (cloisonnement permeable, sans service)
- `x`     : filtered / down -> bloque
- `.`     : cible absente de la sortie du scan (non vu)

## Rapport HTML
`report.html` charge mermaid.js depuis un CDN (jsdelivr) : prevoir une connexion au
premier affichage. Pour un livrable hors-ligne, bundler mermaid.min.js en local et
remplacer l'URL du `<script>`.
