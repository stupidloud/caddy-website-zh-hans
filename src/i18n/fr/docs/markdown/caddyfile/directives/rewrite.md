---
title: rewrite (directive Caddyfile)
---

# rewrite

Réécrit l'URI de la requête de manière interne.

Une réécriture modifie tout ou partie de l'URI de la requête. Notez que l'URI n'inclut pas le schéma ou l'autorité (hôte et port), et que les clients n'envoient généralement pas de fragments. Ainsi, cette directive est principalement utilisée pour la manipulation du **chemin** (path) et de la chaîne de **requête** (query string).

La directive `rewrite` implique l'intention d'accepter la requête, mais avec des modifications.

Elle est mutuellement exclusive avec les autres directives `rewrite` du même bloc, il est donc sûr de définir des réécritures qui autrement cascaderaient les unes dans les autres, car seule la première réécriture correspondante sera exécutée.

Un [sélecteur de requête](/docs/caddyfile/matchers) qui correspond à une requête avant le `rewrite` pourrait ne plus correspondre à la même requête après le `rewrite`. Si vous voulez que votre `rewrite` partage une route avec d'autres gestionnaires, utilisez les directives [`route`](route) ou [`handle`](handle).


## Syntaxe

```caddy-d
rewrite [<matcher>] <vers>
```

- **&lt;vers&gt;** est l'URI vers laquelle réécrire la requête. Seuls les composants de l'URI (chemin ou chaîne de requête) spécifiés dans la réécriture seront modifiés. Le chemin d'URI est n'importe quelle sous-chaîne apparaissant avant `?`. Si `?` est omis, alors le jeton entier est considéré comme étant le chemin.

Avant la v2.8.0, l'argument `<vers>` pouvait être confondu par l'analyseur avec un [jeton de sélecteur](/docs/caddyfile/matchers#syntax) s'il commençait par `/`, il était donc nécessaire de spécifier un jeton de sélecteur générique (`*`).


## Directives similaires

Il existe d'autres directives effectuant des réécritures, mais elles impliquent une intention différente ou effectuent la réécriture sans remplacement complet de l'URI :

- [`uri`](uri) manipule une URI (suppression de préfixe, suffixe, ou remplacement de sous-chaîne).

- [`try_files`](try_files) réécrit la requête en fonction de l'existence de fichiers.



## Exemples

Réécrire toutes les requêtes vers `index.html`, en laissant la chaîne de requête inchangée :

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Notez qu'avant la v2.8.0, un [sélecteur générique](/docs/caddyfile/matchers#wildcard-matchers) était requis ici car le premier argument est ambigu avec un [sélecteur de chemin](/docs/caddyfile/matchers#path-matchers), ex: `rewrite * /foo`, mais cela peut désormais être simplifié en `rewrite /foo`.

</aside>

Préfixer toutes les requêtes par `/api`, en préservant le reste de l'URI, puis effectuer un proxy inverse vers une application :

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Remplacer la chaîne de requête sur les requêtes API par `a=b`, en laissant le chemin inchangé :

```caddy
example.com {
	rewrite ?a=b
}
```

Uniquement pour les requêtes vers `/api/`, préserver la chaîne de requête existante et ajouter une paire clé-valeur :

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Modifier à la fois le chemin et la chaîne de requête, en préservant la chaîne de requête originale tout en ajoutant le chemin original dans le paramètre `p` :

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
