---
title: route (directive Caddyfile)
---

# route

Évalue un groupe de directives littéralement et comme une seule unité.

Les directives contenues dans un bloc route ne seront pas [réordonnées en interne](/docs/caddyfile/directives#directive-order). Seules les directives de gestionnaire HTTP (directives ajoutant des gestionnaires ou middlewares à la chaîne) peuvent être utilisées dans un bloc route.

Cette directive est un cas particulier dans le sens où ses sous-directives sont également des directives classiques.


## Syntaxe

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** est une liste de directives ou de blocs de directives, une par ligne, tout comme en dehors d'un bloc route ; sauf que ces directives ne seront pas réordonnées. Seules les directives de gestionnaire HTTP peuvent être utilisées.



## Utilité

La directive `route` est utile dans certains cas d'utilisation avancés ou particuliers pour prendre le contrôle absolu sur des parties de la chaîne de gestionnaires HTTP.

Parce que l'ordre d'évaluation des middlewares HTTP est significatif, le Caddyfile réordonne normalement les directives après l'analyse pour rendre le Caddyfile plus facile à utiliser ; vous n'avez pas à vous soucier de l'ordre dans lequel vous saisissez les choses.

Bien que l'[ordre intégré](/docs/caddyfile/directives#directive-order) soit compatible avec la plupart des sites, vous avez parfois besoin de prendre le contrôle manuel de l'ordre, soit pour l'ensemble du site, soit pour une partie de celui-ci. C'est à cela que sert la directive `route`.

Pour illustrer, considérons le cas de deux gestionnaires terminaux : [`redir`](redir) et [`file_server`](file_server). Tous deux écrivent la réponse au client et n'appellent pas le prochain gestionnaire de la chaîne, donc un seul d'entre eux sera exécuté pour une requête donnée. Alors, lequel passe en premier ? Normalement, `redir` est exécuté avant `file_server` car on souhaite généralement émettre une redirection uniquement dans des cas spécifiques et servir des fichiers dans le cas général.

Cependant, il peut y avoir des occasions où la première directive (`file_server`) possède un sélecteur plus précis que la seconde (`redir`). En d'autres termes, vous voulez rediriger dans le cas général, et servir uniquement un fichier spécifique.

Vous pourriez donc essayer un Caddyfile comme celui-ci (mais cela ne fonctionnera pas comme prévu !) :

```caddy
example.com {
	file_server /specifique.html
	redir https://unautresite.com{uri}
}
```

Le problème est qu'après le [tri des directives](/docs/caddyfile/directives#sorting-algorithm), `redir` se retrouve avant `file_server`.

Mais dans ce cas, le sélecteur pour `redir` (un [`*`](/docs/caddyfile/matchers#wildcard-matchers) implicite) est un sur-ensemble du sélecteur pour `file_server` (`*` est un sur-ensemble de `/specifique.html`).

Heureusement, la solution est facile : enveloppez simplement ces deux directives dans un bloc `route`, afin de garantir que `file_server` soit exécuté avant `redir` :

```caddy
example.com {
	route {
		file_server /specifique.html
		redir https://unautresite.com{uri}
	}
}
```

<aside class="tip">

Un autre moyen d'y parvenir est de rendre les deux sélecteurs mutuellement exclusifs, mais cela peut vite devenir complexe s'il y a plus d'une ou deux conditions. Avec la directive `route`, l'exclusivité mutuelle des deux gestionnaires est implicite car ils sont tous deux des gestionnaires terminaux.

</aside>

Et maintenant, `file_server` sera enchaîné avant `redir` car l'ordre est pris littéralement.



## Directives similaires

Il existe d'autres directives pouvant envelopper des directives de gestionnaire HTTP, mais chacune a son utilité selon le comportement que vous souhaitez exprimer :

- [`handle`](handle) enveloppe d'autres directives comme `route` le fait, mais avec deux distinctions : 1) les blocs handle sont mutuellement exclusifs entre eux, et 2) les directives à l'intérieur d'un handle sont [réordonnées](/docs/caddyfile/directives#directive-order) normalement.

- [`handle_path`](handle_path) fait la même chose que `handle`, mais il supprime un préfixe de la requête avant d'exécuter ses gestionnaires.

- [`handle_errors`](handle_errors) est comme `handle`, mais n'est invoqué que lorsque Caddy rencontre une erreur pendant le traitement de la requête.



## Exemples

Proxifier les requêtes vers `/api` telles quelles, et réécrire toutes les autres requêtes selon qu'elles correspondent à un fichier sur le disque, sinon vers `/index.html`. Ensuite, ce fichier est servi.

Puisque [`try_files`](try_files) possède un ordre de directive plus élevé que [`reverse_proxy`](reverse_proxy), il serait normalement trié plus haut et s'exécuterait en premier ; cela ferait en sorte que toutes les requêtes API soient réécrites vers `/index.html` et échouent à correspondre à `/api*`, donc aucune d'elles ne serait proxifiée et résulterait à la place en une erreur `404` de [`file_server`](file_server). Envelopper le tout dans une `route` garantit que `reverse_proxy` s'exécute toujours en premier, avant que la requête ne soit réécrite.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Ce n'est pas la seule solution à ce problème. Vous pourriez également utiliser une paire de blocs [`handle`](handle), le premier faisant correspondre `/api*` vers `reverse_proxy`, et le second agissant comme repli et servant les fichiers. Voir [cet exemple](/docs/caddyfile/patterns#single-page-apps-spas) d'une SPA.

</aside>
