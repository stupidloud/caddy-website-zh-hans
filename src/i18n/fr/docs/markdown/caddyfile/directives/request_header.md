---
title: request_header (directive Caddyfile)
---

# request_header

Manipule les champs d'en-tête HTTP sur la requête. Elle peut définir, ajouter et supprimer des valeurs d'en-tête, ou effectuer des remplacements en utilisant des expressions régulières.

Si vous avez l'intention de manipuler des en-têtes pour du proxying, utilisez plutôt la [sous-directive `header_up`](/docs/caddyfile/directives/reverse_proxy#header_up) de `reverse_proxy`, car ces manipulations sont conscientes du proxy.

Pour manipuler les en-têtes de réponse HTTP, vous pouvez utiliser la directive [`header`](header).


## Syntaxe

```caddy-d
request_header [<matcher>] [[+|-]<champ> [<valeur>|<cherche>] [<remplace>]]
```

- **&lt;champ&gt;** est le nom du champ d'en-tête.

  Sans préfixe, le champ est défini (écrasé).

  Préfixez par `+` pour ajouter le champ au lieu de l'écraser s'il existe déjà ; les champs d'en-tête peuvent apparaître plus d'une fois dans une requête.

  Préfixez par `-` pour supprimer le champ. Le champ peut utiliser les caractères génériques `*` en préfixe ou suffixe pour supprimer tous les champs correspondants.

- **&lt;valeur&gt;** est la valeur du champ d'en-tête, lors de l'ajout ou de la définition d'un champ.

- **&lt;cherche&gt;** est la sous-chaîne ou l'expression régulière à rechercher.

- **&lt;remplace&gt;** est la valeur de remplacement ; requise lors de l'exécution d'un chercher-remplacer.


## Exemples

Supprimer l'en-tête `Referer` de la requête :

```caddy-d
request_header -Referer
```

Supprimer tous les en-têtes contenant un souligné (underscore) de la requête :

```caddy-d
request_header -*_*
```
