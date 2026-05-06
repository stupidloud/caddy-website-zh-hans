---
title: Conventions
---

# Conventions

L'écosystème Caddy adhère à quelques conventions pour assurer la cohérence et l'intuitivité de la plateforme.


- [Adresses réseau](#network-addresses)
- [Espaces réservés (Placeholders)](#placeholders)
- [Emplacements des fichiers](#file-locations)
  - [Répertoire de données](#data-directory)
  - [Répertoire de configuration](#configuration-directory)
- [Durées](#durations)



<a id="network-addresses"></a>
## Adresses réseau

Lors de la spécification d'une adresse réseau pour une connexion ou une écoute, Caddy accepte une chaîne au format suivant :

```
réseau/adresse
```

La partie réseau est optionnelle (valeur par défaut : `tcp`) et correspond à tout ce que la [fonction `net.Dial` de Go](https://pkg.go.dev/net#Dial) reconnaît. Si un réseau est spécifié, un slash `/` doit séparer les portions réseau et adresse.

Le réseau peut être l'un des suivants ; ceux suffixés par `4` ou `6` sont respectivement limités à l'IPv4 ou l'IPv6 :

- TCP : `tcp`, `tcp4`, `tcp6`
- UDP : `udp`, `udp4`, `udp6`
- IP : `ip`, `ip4`, `ip6`
- Unix : `unix`, `unixgram`, `unixpacket`

La partie adresse peut prendre n'importe laquelle de ces formes :

- `hôte`
- `hôte:port`
- `:port`
- `[ipv6%zone]:port`
- `/chemin/vers/socket/unix`
- `/chemin/vers/socket/unix|0200`

L'hôte peut être n'importe quel nom d'hôte, nom de domaine résolvable ou adresse IP.

Dans le cas des adresses IPv6, l'adresse doit être entourée de crochets `[]`. L'identifiant de zone (commençant par `%`) est optionnel (souvent utilisé pour les adresses de lien local).

Le port peut être une valeur unique (`:8080`) ou une plage inclusive (`:8080-8085`). Une plage de ports sera démultipliée en adresses individuelles. Tous les champs de configuration n'acceptent pas les plages de ports. Le port spécial `:0` désigne n'importe quel port disponible.

Un chemin de socket Unix n'est acceptable que lors de l'utilisation d'un type de réseau `unix*`. Le slash séparant le réseau et l'adresse n'est pas considéré comme faisant partie du chemin.

Lorsqu'un socket Unix est utilisé comme adresse d'écoute, vous pouvez optionnellement spécifier un mode de permission de fichier après le chemin, séparé par un tube `|`. La valeur par défaut est `0200` (octal), soit `u=w,g=,o=` (symbolique). Le `0` initial est optionnel.

Exemples valides :

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Les adresses réseau de Caddy ne sont pas des URLs. Les URLs couplent les couches basses et hautes du [modèle OSI <img src="/old/resources/images/external-link.svg" class="external-link">](https://fr.wikipedia.org/wiki/Mod%C3%A8le_OSI), mais Caddy utilise souvent les adresses réseau indépendamment d'une application spécifique, leur combinaison serait donc problématique. Dans Caddy, les adresses réseau désignent précisément des ressources pouvant être contactées ou écoutées aux couches L3-L5, tandis que les URLs combinent L3-L7, ce qui est trop. Une adresse réseau exige que l'hôte+port et le chemin soient mutuellement exclusifs, ce qui n'est pas le cas des URLs. Les adresses réseau supportent parfois les plages de ports, contrairement aux URLs.

</aside>




<a id="placeholders"></a>
## Espaces réservés (Placeholders)

La configuration de Caddy supporte l'utilisation d' _espaces réservés_. C'est un moyen simple d'injecter des valeurs dynamiques dans une configuration statique.

<aside class="tip">

Les espaces réservés sont une idée similaire aux variables dans d'autres logiciels. Par exemple, [nginx possède des variables <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) comme `$uri` et `$document_root`, alors que l'équivalent de Caddy serait [`{http.request.uri}`](/docs/json/apps/http/#docs) et [`{http.vars.root}`](/docs/caddyfile/directives/root).

</aside>


Les espaces réservés sont délimités de chaque côté par des accolades `{ }` et contiennent l'identifiant à l'intérieur, par exemple : `{foo.bar}`. L'accolade ouvrante peut être échappée `\{comme.ceci}` pour empêcher le remplacement. Les identifiants sont généralement segmentés par des points pour éviter les collisions entre modules.

Les espaces réservés disponibles dépendent du contexte. Ils ne sont pas tous disponibles dans toutes les parties de la configuration. Par exemple, [l'application HTTP définit des espaces réservés](/docs/json/apps/http/#docs) qui ne sont accessibles que dans les zones de configuration liées au traitement des requêtes HTTP. Lorsqu'une requête passe par le [gestionnaire `reverse_proxy`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs), celui-ci définit plusieurs espaces réservés spécifiques au proxy. Ces derniers peuvent être référencés pendant le proxying ainsi qu'après (dans `handle_response`), par exemple pour définir des en-têtes de réponse ou enrichir les journaux d'accès.

Les espaces réservés suivants sont toujours disponibles (globaux) :

Placeholder | Description
------------|-------------
`{env.*}` | Variable d'environnement ; exemple : `{env.HOME}`
`{file.*}` | Contenu d'un fichier ; exemple : `{file./chemin/vers/secret.txt}`
`{system.hostname}` | Le nom d'hôte local du système
`{system.slash}` | Le séparateur de chemin du système
`{system.os}` | L'OS du système
`{system.arch}` | L'architecture du système
`{system.wd}` | Le répertoire de travail actuel
`{time.now}` | L'heure actuelle sous forme de structure Time de Go
`{time.now.http}` | L'heure actuelle au format utilisé dans les [en-têtes HTTP <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)
`{time.now.unix}` | L'heure actuelle sous forme de timestamp Unix (secondes)
`{time.now.unix_ms}` | L'heure actuelle sous forme de timestamp Unix (millisecondes)
`{time.now.common_log}` | L'heure actuelle au format Common Log
`{time.now.year}` | L'année actuelle au format YYYY

Tous les champs de configuration ne supportent pas les espaces réservés, mais la plupart le font là où on s'y attendrait. Le support des espaces réservés doit avoir été explicitement ajouté à ces champs. Les auteurs de plugins peuvent [lire cet article](/docs/extending-caddy/placeholders) pour apprendre comment ajouter le support des espaces réservés dans leurs propres modules.




<a id="file-locations"></a>
## Emplacements des fichiers

Cette section contient des informations sur l'emplacement de divers fichiers. Les chemins de fichiers et de répertoires décrits ici sont au mieux des valeurs par défaut ; certains peuvent être remplacés.

<a id="your-config-files"></a>
### Vos fichiers de configuration

Il n'y a pas d'emplacement conventionnel unique pour vos fichiers de configuration. Placez-les là où cela vous semble le plus logique.

<aside class="tip">

La seule exception est un fichier nommé `Caddyfile` dans le répertoire de travail actuel, que la commande caddy tente d'utiliser par commodité si aucun autre fichier n'est spécifié.

</aside>


Les distributions fournissant un fichier de configuration par défaut doivent documenter son emplacement. Pour la plupart des installations Linux, le Caddyfile se trouve dans `/etc/caddy/Caddyfile`.


<a id="data-directory"></a>
### Répertoire de données

Caddy stocke les certificats TLS et d'autres ressources importantes dans un répertoire de données, qui s'appuie sur le [module de stockage configuré](/docs/json/storage/) (par défaut : système de fichiers local).

Si la variable d'environnement `XDG_DATA_HOME` est définie, il s'agit de `$XDG_DATA_HOME/caddy`.

Sinon, son chemin varie selon la plateforme, en respectant les conventions de l'OS :

OS | Chemin du répertoire de données
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (ou `/sdcard/caddy`)

Tous les autres OS utilisent le chemin des répertoires Linux/BSD.

**Le répertoire de données ne doit pas être traité comme un cache.** Son contenu n'est **pas** éphémère. Caddy y stocke les certificats TLS, les clés privées, les agrafes OCSP et d'autres informations nécessaires. Il ne doit pas être purgé sans en comprendre les implications.

Il est crucial que ce répertoire soit persistant et accessible en écriture par Caddy.


<a id="configuration-directory"></a>
### Répertoire de configuration

C'est là que Caddy peut stocker certaines configurations sur le disque. Notamment, il y conserve (par défaut) la dernière configuration active pour une reprise facile via [`caddy run --resume`](/docs/command-line#caddy-run).

<aside class="tip">

Le répertoire de configuration n'est *pas* l'endroit où vous devez stocker [vos fichiers de configuration](#your-config-files) (bien que vous y soyez autorisé).

</aside>


Si la variable d'environnement `XDG_CONFIG_HOME` est définie, il s'agit de `$XDG_CONFIG_HOME/caddy`.

Sinon, son chemin varie selon la plateforme, en respectant les conventions de l'OS :


OS | Chemin du répertoire de configuration
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Tous les autres OS utilisent le chemin des répertoires Linux/BSD.

Il est crucial que ce répertoire soit persistant et accessible en écriture par Caddy.


<a id="durations"></a>
## Durées

Les chaînes de caractères de durée sont couramment utilisées dans la configuration de Caddy. Elles adoptent le même format que la [syntaxe `time.ParseDuration` de Go](https://golang.org/pkg/time/#ParseDuration), avec en plus le support de `d` pour jour (1 jour = 24 heures par simplicité). Les unités valides sont :

- `ns` (nanoseconde)
- `us`/`µs` (microseconde)
- `ms` (milliseconde)
- `s` (seconde)
- `m` (minute)
- `h` (heure)
- `d` (jour)

Exemples :

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

Dans la [configuration JSON](/docs/json/), les valeurs de durée peuvent également être des entiers représentant des nanosecondes.
