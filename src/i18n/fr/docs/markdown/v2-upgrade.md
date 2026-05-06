---
title: Passer à Caddy 2
---

Guide de mise à jour
====================

Caddy 2 est une toute nouvelle base de code, écrite à partir de zéro, pour améliorer Caddy 1. Caddy 2 n'est pas rétrocompatible avec Caddy 1. Mais ne vous inquiétez pas, pour la plupart des installations basiques, peu de choses changent. Ce guide vous aidera à effectuer la transition le plus facilement possible.

Ce guide ne s'attardera pas sur les nouvelles fonctionnalités disponibles — qui sont d'ailleurs très cool, vous devriez [les apprendre](/docs/getting-started) — le but ici est simplement de vous rendre opérationnel sur Caddy 2 rapidement.


- [Points essentiels](#high-order-bits)
- [Étapes](#steps)
- [HTTPS et ports](#https-and-ports)
- [Ligne de commande](#command-line)
- [Caddyfile](#caddyfile)
  - [Changements principaux](#primary-changes)
  - [basicauth](#basicauth)
  - [browse](#browse)
  - [errors](#errors)
  - [ext](#ext)
  - [fastcgi](#fastcgi)
  - [gzip](#gzip)
  - [header](#header)
  - [log](#log)
  - [proxy](#proxy)
  - [redir](#redir)
  - [rewrite](#rewrite)
  - [root](#root)
  - [status](#status)
  - [templates](#templates)
  - [tls](#tls)
- [Fichiers de service](#service-files)
- [Plugins](#plugins)
- [Obtenir de l'aide](#getting-help)



<a id="high-order-bits"></a>
## Points essentiels

- "Caddy 2" s'appelle toujours simplement `caddy`. Nous pouvons utiliser "Caddy 2" pour clarifier la version et rendre la transition moins confuse.
- La plupart des utilisateurs devront simplement remplacer leur binaire `caddy` et leur configuration `Caddyfile` mise à jour (après avoir testé qu'elle fonctionne).
- Il est préférable d'aborder Caddy 2 sans aucune supposition héritée de Caddy 1.
- Vous ne pourrez peut-être pas répliquer parfaitement votre configuration v1 très spécifique en v2. Généralement, il y a une bonne raison à cela.
- La ligne de commande n'est plus utilisée pour la configuration du serveur.
- Les variables d'environnement ne sont plus nécessaires pour la configuration.
- La méthode principale pour donner sa configuration à Caddy 2 est via son [API](/docs/api), mais la commande [`caddy`](/docs/command-line) peut également être utilisée.
- Sachez que le langage de configuration natif de Caddy 2 est le [JSON](/docs/json/), et le Caddyfile n'est qu'un [adaptateur de configuration](/docs/config-adapters) qui le convertit en JSON pour vous. Les cas d'utilisation extrêmement personnalisés ou avancés peuvent nécessiter du JSON, car toutes les configurations possibles ne peuvent pas être exprimées par le Caddyfile.
- Le Caddyfile est globalement le même, mais bien plus puissant ; les directives ont changé.



<a id="steps"></a>
## Étapes

1. Familiarisez-vous avec Caddy 2 en suivant notre tutoriel de [Premiers pas](/docs/getting-started).
2. Faites l'étape 1 si ce n'est pas déjà fait. Sérieusement — nous insistons sur l'importance de savoir au moins comment utiliser Caddy 2. (C'est plus amusant !)
3. Utilisez le guide ci-dessous pour adapter vos commandes `caddy`.
4. Utilisez le guide ci-dessous pour adapter votre Caddyfile.
5. Testez votre nouvelle config localement ou en pré-production (staging).
6. Testez, testez, et testez encore.
7. Déployez et profitez !



<a id="https-and-ports"></a>
## HTTPS et ports

Le port par défaut de Caddy n'est plus `:2015`. Le port par défaut de Caddy 2 est `:443` ou, si aucun nom d'hôte/IP n'est connu, le port `:80`. Vous pouvez toujours personnaliser les ports dans votre configuration.

Le protocole par défaut de Caddy 2 est [*toujours* HTTPS si un nom d'hôte ou une IP est connu](/docs/automatic-https#overview). C'est différent de Caddy 1, où seuls les domaines d'apparence publique utilisaient le HTTPS par défaut. Désormais, *chaque* site utilise le HTTPS (sauf si vous le désactivez en spécifiant explicitement le port `:80` ou `http://`).

Les adresses IP et les domaines localhost recevront des certificats d'une [CA intégrée et localement approuvée](/docs/automatic-https#local-https). Tous les autres domaines utiliseront ZeroSSL ou Let's Encrypt. (Tout cela est configurable.)

La structure de stockage des certificats et des ressources ACME a changé. Caddy 2 obtiendra probablement de nouveaux certificats pour vos sites ; mais si vous avez beaucoup de certificats, vous pouvez les migrer manuellement s'il ne le fait pas pour vous. Voir les tickets [#2955](https://github.com/caddyserver/caddy/issues/2955) et [#3124](https://github.com/caddyserver/caddy/issues/3124) pour les détails.



<a id="command-line"></a>
## Ligne de commande

La commande `caddy` est maintenant `caddy run`.

Tous les drapeaux (flags) de ligne de commande sont différents. Supprimez-les ; toute la configuration du serveur réside désormais dans le document de configuration lui-même (généralement Caddyfile ou JSON). Vous trouverez probablement ce dont vous avez besoin dans la [structure JSON](/docs/json/) ou dans les [options globales du Caddyfile](/docs/caddyfile/options) pour remplacer la plupart des drapeaux de la v1.

Une commande comme `caddy -conf ../Caddyfile` deviendrait `caddy run --config ../Caddyfile`.

Comme auparavant, si votre Caddyfile se trouve dans le dossier actuel, Caddy le trouvera et l'utilisera automatiquement ; vous n'avez pas besoin d'utiliser le drapeau `--config` dans ce cas.

Les signaux sont globalement les mêmes, sauf que USR1 et USR2 ne sont plus supportés. Utilisez plutôt la commande [`caddy reload`](/docs/command-line#caddy-reload) ou l'[API](/docs/api) pour charger une nouvelle configuration.

Lancer `caddy` sans aucune config lançait un simple serveur de fichiers. L'équivalent en Caddy 2 est [`caddy file-server`](/docs/command-line#caddy-file-server).

Les variables d'environnement ne sont plus pertinentes, sauf pour `HOME` (et, optionnellement, toutes les variables `XDG_*` que vous définissez). Le `CADDYPATH` est [remplacé par les conventions de l'OS](/docs/conventions#file-locations).



<a id="caddyfile"></a>
## Caddyfile

Le [Caddyfile v2](/docs/caddyfile/concepts) est très similaire à ce que vous connaissez déjà. La chose principale à faire est de changer vos directives.

⚠️ **Assurez-vous de bien lire la documentation des nouvelles directives !** Surtout si votre configuration est avancée, il y a de nombreuses nuances à considérer. Ces conseils vous permettront de migrer assez rapidement, mais veuillez lire la documentation complète de chaque directive pour comprendre les implications de la mise à jour. Et bien sûr, testez toujours vos configurations en profondeur avant de les mettre en production.


<a id="primary-changes"></a>
### Changements principaux

- Si vous servez des fichiers statiques, vous devrez ajouter une [directive `file_server`](/docs/caddyfile/directives/file_server), car Caddy 2 ne le suppose plus par défaut. Caddy 2 ne détecte plus le type MIME automatiquement par défaut non plus, pour des raisons de sécurité ; si un Content-Type manque, vous devrez peut-être définir l'en-tête vous-même en utilisant la directive [header](/docs/caddyfile/directives/header).

- En v1, vous ne pouviez filtrer (ou "matcher") les directives que par le chemin de la requête. En v2, le [filtrage de requête (matching)](/docs/caddyfile/matchers) est bien plus puissant. Toutes les directives v2 qui ajoutent un middleware à la chaîne de traitement HTTP ou qui manipulent la requête/réponse HTTP tirent parti de cette nouvelle fonctionnalité. [En savoir plus sur les sélecteurs (matchers) v2.](/docs/caddyfile/matchers) Vous devrez les connaître pour comprendre le Caddyfile v2.

- Bien que de nombreux [espaces réservés (placeholders)](/docs/conventions#placeholders) soient identiques, beaucoup ont changé, et il y en a maintenant de [nombreux nouveaux](/docs/modules/http#docs), incluant des [raccourcis pour le Caddyfile](/docs/caddyfile/concepts#placeholders).

- Les journaux (logs) de Caddy 2 sont tous structurés, et le format par défaut est le JSON. Tous les niveaux de journaux peuvent simplement aller dans le même log pour être traités (mais vous pouvez personnaliser cela si nécessaire).

- Là où vous filtriez les requêtes par préfixe de chemin en Caddy 1, le filtrage de chemin est désormais exact par défaut en Caddy 2. Si vous voulez filtrer un préfixe comme `/foo/`, vous aurez besoin de `/foo/*` en Caddy 2.

Nous listons ici certaines des directives v1 les plus courantes et décrivons comment les convertir pour le Caddyfile v2.

⚠️ **Ce n'est pas parce qu'une directive v1 est absente de cette page que Caddy 2 ne peut pas le faire !** Certaines directives v1 ne sont plus nécessaires, ne se traduisent pas bien, ou sont remplies d'une autre manière en v2. Pour certaines personnalisations avancées, vous devrez peut-être descendre au niveau JSON. Explorez [notre documentation](/docs/caddyfile) pour trouver ce dont vous avez besoin !


<a id="basicauth"></a>
### basicauth

L'authentification HTTP Basic se configure toujours avec la directive [`basic_auth`](/docs/caddyfile/directives/basic_auth). Cependant, la configuration de Caddy 2 n'accepte pas les mots de passe en texte clair. Vous devez les hacher, ce que la commande [`caddy hash-password`](/docs/command-line#caddy-hash-password) peut vous aider à faire.

- **v1 :**
```
basicauth /secret/ Bob hiccup
```

- **v2 :**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


<a id="browse"></a>
### browse

L'exploration de fichiers est désormais activée via la directive [`file_server`](/docs/caddyfile/directives/file_server).

- **v1 :**
```
browse /subfolder/
```
- **v2 :**
```caddy-d
file_server /subfolder/* browse
```


<a id="errors"></a>
### errors

Les pages d'erreur personnalisées peuvent être réalisées avec [`handle_errors`](/docs/caddyfile/directives/handle_errors).


- **v1 :**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2 :**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

<a id="ext"></a>
### ext

Les extensions de fichiers implicites peuvent être gérées avec [`try_files`](/docs/caddyfile/directives/try_files).

- **v1 :** `ext .html`
- **v2 :** `try_files {path}.html {path}`


<a id="fastcgi"></a>
### fastcgi

En supposant que vous serviez du PHP, l'équivalent v2 est [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1 :**
```
fastcgi / localhost:9005 php
```
- **v2 :**
```caddy-d
php_fastcgi localhost:9005
```

Notez que la directive `fastcgi` de la v1 faisait beaucoup de choses en arrière-plan, comme tester des fichiers sur le disque, réécrire des requêtes, et même rediriger. La directive `php_fastcgi` de la v2 fait également ces choses pour vous, mais la documentation donne sa [forme étendue](/docs/caddyfile/directives/php_fastcgi#expanded-form) que vous pouvez modifier si vos besoins sont différents.

Il n'y a plus besoin du préréglage `php` en v2, car la directive `php_fastcgi` suppose du PHP par défaut. Une ligne telle que `php_fastcgi 127.0.0.1:9000 php` fera croire au proxy inverse qu'il y a un second backend nommé `php`, entraînant des erreurs de connexion.

Les sous-directives sont différentes en v2 — vous n'en aurez probablement besoin d'aucune pour PHP.


<a id="gzip"></a>
### gzip

Une seule directive [`encode`](/docs/caddyfile/directives/encode) est désormais utilisée pour tous les encodages de réponse, incluant plusieurs formats de compression.

- **v1 :**
```
gzip
```
- **v2 :**
```caddy-d
encode gzip
```

Le saviez-vous ? Caddy 2 supporte également `zstd` (mais aucun navigateur ne le supporte encore).


<a id="header"></a>
### header

[Quasiment inchangée](/docs/caddyfile/directives/header), mais bien plus puissante car elle peut effectuer des remplacements de sous-chaînes en v2.

- **v1 :**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2 :**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


<a id="log"></a>
### log

Active la journalisation des accès ; la directive [`log`](/docs/caddyfile/directives/log) peut toujours être utilisée en v2, mais tous les journaux sont structurés et encodés en JSON par défaut.

La méthode recommandée pour activer les journaux d'accès est simplement :

```caddy-d
log
```

ce qui émet des journaux structurés sur stderr. (Vous pouvez aussi émettre vers un fichier ou un socket réseau ; voir la doc de la directive [`log`](/docs/caddyfile/directives/log).)

Par défaut, les journaux seront au format JSON [structuré](/docs/logging). Si vous avez toujours besoin de journaux au format Common Log Format (CLF) pour des raisons d'héritage, vous pouvez utiliser le plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder).


<a id="proxy"></a>
### proxy

L'équivalent v2 est [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

Les changements notables de sous-directives sont `header_upstream` et `header_downstream` devenus respectivement `header_up` et `header_down` ; et les sous-directives liées à l'équilibrage de charge sont préfixées par `lb_`.

Une autre différence significative est que le proxy v2 transmet tous les en-têtes entrants par défaut (incluant l'en-tête `Host`) et définit l'en-tête `X-Forwarded-For`. En d'autres termes, le mode "transparent" de la v1 est fondamentalement le défaut en v2 (but if you need other headers like X-Real-IP, you must set those yourself). Vous pouvez toujours surcharger/personnaliser l'en-tête `Host` via la sous-directive `header_up`.

Le proxying de Websocket "fonctionne tout simplement" en v2 ; il n'y a plus besoin d'activer les websockets comme en v1.

La sous-directive `without` a été supprimée car les [bidouilles de réécriture (rewrite hacks)](#rewrite) ne sont plus nécessaires en v2 grâce au support amélioré des sélecteurs (matchers).

- **v1 :**
```
proxy / localhost:9005
```
- **v2 :**
```caddy-d
reverse_proxy localhost:9005
```


<a id="redir"></a>
### redir

[Inchangée](/docs/caddyfile/directives/redir), sauf pour quelques détails concernant l'argument optionnel du code d'état. La plupart des configurations n'auront aucun changement à faire.

- **v1 :** `redir https://example.com{uri}`
- **v2 :** `redir https://example.com{uri}`


<a id="rewrite"></a>
### rewrite

La sémantique de la réécriture de requête ("redirection interne") a légèrement changé. Si vous utilisiez une bidouille de réécriture ("rewrite hack") en v1 pour filtrer des requêtes sur autre chose qu'un simple préfixe de chemin, c'est totalement inutile en v2.

La [nouvelle directive `rewrite`](/docs/caddyfile/directives/rewrite) est très simple mais très puissante, car l'essentiel de sa complexité est géré par les [sélecteurs (matchers)](/docs/caddyfile/matchers) en v2 :

- **v1 :**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2 :**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Remarquez comment nous utilisons simplement les [jetons de sélecteurs](/docs/caddyfile/matchers) habituels de Caddy 2 ; ce n'est plus un cas particulier pour cette directive.

Commencez par supprimer toutes les bidouilles de réécriture ; transformez-les plutôt en [sélecteurs nommés](/docs/caddyfile/concepts#named-matchers). Évaluez chaque `rewrite` v1 pour voir s'il est réellement nécessaire en v2. Indice : un Caddyfile v1 qui utilise `rewrite` pour ajouter un préfixe de chemin, puis `proxy` avec `without` pour supprimer ce même préfixe est une bidouille de réécriture, et peut être éliminé.

Vous pourriez trouver les nouvelles directives [`route`](/docs/caddyfile/directives/route) et [`handle`](/docs/caddyfile/directives/handle) utiles pour avoir un meilleur contrôle sur la logique de routage avancée.


<a id="root"></a>
### root

[Inchangée](/docs/caddyfile/directives/root).

N'oubliez pas d'ajouter une [directive `file_server`](/docs/caddyfile/directives/file_server) si vous servez des fichiers statiques, car Caddy 2 ne le suppose plus par défaut, contrairement à la v1 qui l'avait toujours activé.


<a id="status"></a>
### status

L'équivalent v2 est [`respond`](/docs/caddyfile/directives/respond), qui peut également écrire un corps de réponse.

- **v1 :**
```
status 404 /secrets/
```
- **v2 :**
```caddy-d
respond /secrets/* 404
```


<a id="templates"></a>
### templates

La syntaxe globale de la directive [`templates`](/docs/caddyfile/directives/templates) est inchangée, mais les actions/fonctions de modèles réelles sont d'autres et grandement améliorées. Par exemple, les modèles sont capables d'inclure des fichiers, de rendre du markdown, d'effectuer des sous-requêtes internes, d'analyser le front-matter, et plus encore !

[Voir la doc](/docs/modules/http.handlers.templates) pour les détails sur les nouvelles fonctions.

- **v1 :** `templates`
- **v2 :** `templates`


<a id="tls"></a>
### tls

Les fondamentaux de la directive [`tls`](/docs/caddyfile/directives/tls) n'ont pas changé, par exemple pour spécifier vos propres certificat et clé :

- **v1 :** `tls cert.pem key.pem`
- **v2 :** `tls cert.pem key.pem`

Mais la [logique de HTTPS automatique](/docs/automatic-https) de Caddy *a* changé, soyez-en conscient !

Les noms des suites de chiffrement (cipher suites) ont également changé.

Une configuration courante en Caddy 2 est d'utiliser `tls internal` pour lui faire servir un certificat localement approuvé pour un nom d'hôte de développement qui n'est pas `localhost` ou une adresse IP.

La plupart des sites n'auront pas besoin de cette directive du tout.


<a id="service-files"></a>
## Fichiers de service

Nous recommandons d'utiliser l'[un de nos fichiers de service systemd officiels](/docs/running#linux-service) pour les déploiements de Caddy.

Si vous avez besoin d'un fichier de service personnalisé, basez-vous sur les nôtres. Ils ont été soigneusement ajustés pour de bonnes raisons ! Veillez à personnaliser le vôtre si nécessaire.


<a id="plugins"></a>
## Plugins

Les plugins écrits pour la v1 ne sont pas automatiquement compatibles avec la v2. De nombreux plugins v1 ne sont même plus nécessaires en v2. D'un autre côté, la v2 est bien plus facilement extensible et flexible que la v1 !

Si vous voulez écrire un plugin pour Caddy 2, [apprenez comment écrire un module Caddy](/docs/extending-caddy).


### Compiler Caddy 2 avec des plugins

Caddy 2 peut être téléchargé avec des plugins sur la [page de téléchargement interactive](/download). Alternativement, vous pouvez [compiler Caddy vous-même](/docs/build) en utilisant `xcaddy` et choisir quels plugins inclure. `xcaddy` automatise les instructions contenues dans le fichier [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) de Caddy.


<a id="getting-help"></a>
## Obtenir de l'aide

Si vous avez des difficultés à faire fonctionner Caddy, veuillez d'abord consulter la documentation sur notre site web. Prenez le temps d'essayer de nouvelles choses et de comprendre ce qui se passe — la v2 est très différente de la v1 sur de nombreux points (mais elle est aussi très familière) !

Si vous avez toujours besoin d'assistance, rejoignez [notre communauté](https://caddy.community) ! Vous découvrirez peut-être qu'aider les autres est aussi le meilleur moyen de s'aider soi-même.
