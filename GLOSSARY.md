# Test de cloisonnement

Mesure, à partir de scans réseau lancés depuis l'intérieur du périmètre, des flux réellement admis entre segments, pour que l'auditeur juge si le cloisonnement voulu est respecté.

## Language

### Périmètre

**Zone** :
Segment réseau déclaré par l'auditeur dans l'inventaire, représentant une intention de cloisonnement, et non un VLAN ou un sous-réseau observé. Un tier d'administration (T0, T1…) ou un environnement (admin, iLO, supervision) s'exprime comme une Zone.
_Avoid_ : VLAN, sous-réseau, segment, tier, environnement

**Machine** :
Équipement physique ou virtuel, identifié par son nom dans l'inventaire, qui porte une ou plusieurs Interfaces.
_Avoid_ : hôte, serveur, asset

**Interface** :
Une IP d'une Machine, rattachée à exactement une Zone. Une Machine dont les Interfaces sont dans plusieurs Zones enjambe ces Zones.
_Avoid_ : alias, patte, IP secondaire

**Politique de zone** :
Jugement, porté manuellement par l'auditeur à la lecture des graphes, sur les paires de zones qui doivent ou non communiquer. L'outil ne la connaît pas.
_Avoid_ : règle, matrice de flux attendue

### Scan

**Source** :
L'IP depuis laquelle un scan est lancé. Elle est en pratique confondue avec la machine, car le routage système choisit l'interface de sortie.
_Avoid_ : pivot, origine, hôte source

**Self** :
Toutes les Interfaces de la Machine qui porte la Source. Elles sont exclues de son propre scan.

### Verdict

Verdict d'un couple Source → Interface, du plus permissif au plus fermé :

**OPEN** :
Au moins un port open : un service est joignable.

**REACHABLE** :
Aucun port open mais au moins un port closed (RST reçu) : le flux L4 traverse la segmentation.

**ALIVE** :
L'Interface répond au niveau L3/L2 (ping, ARP) sans qu'aucun port TCP ne passe. N'existe pas en scan -Pn.
_Avoid_ : host up, joignable

**BLOCKED** :
Uniquement des ports filtered. En -Pn, cela ne distingue pas un filtrage d'une Interface éteinte ou inexistante.

**NON-VU** :
L'Interface est absente de la sortie du scan.

### Résultat

**Finding** :
Flux OPEN entre deux zones différentes, présenté à l'auditeur qui décide s'il s'agit d'un écart à la Politique de zone.
_Avoid_ : vulnérabilité, violation
