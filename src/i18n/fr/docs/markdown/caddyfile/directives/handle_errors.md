---
title: handle_errors (directive Caddyfile)
---

# handle_errors

Définit les gestionnaires d'erreurs.

Lorsque les gestionnaires de requêtes HTTP normaux retournent une erreur, le traitement normal s'arrête et les gestionnaires d'erreurs sont invoqués. Les gestionnaires d'erreurs forment une route qui est identique aux routes normales, et ils peuvent faire tout ce que les routes normales peuvent faire. Cela permet un grand contrôle et une grande flexibilité lors de la gestion des erreurs pendant les requêtes HTTP. Par exemple, vous pouvez servir des pages d'erreur statiques, des pages d'erreur utilisant des modèles, ou effectuer un proxy inverse vers un autre backend pour gérer les erreurs.

La directive peut être répétée avec différents codes d'état pour gérer différentes erreurs de manières différentes. Si aucun code d'état n'est spécifié, alors elle correspondra à n'importe quelle erreur, agissant comme un repli (fallback) si aucun autre gestionnaire d'erreurs ne correspond.

Le contexte d'une requête est transporté dans les routes d'erreur, ainsi toutes les valeurs définies sur le contexte de la requête telles que la racine du site ([site root](root)) ou les variables ([vars](vars)) seront également préservées dans les gestionnaires d'erreurs. De plus, de [nouveaux espaces réservés](#placeholders) sont disponibles lors de la gestion des erreurs.

Notez que certaines directives, par exemple [`reverse_proxy`](reverse_proxy) qui peut écrire une réponse avec un statut HTTP classé comme une erreur, ne déclencheront *pas* les routes d'erreur.

Vous pouvez utiliser la directive [`error`](error) pour déclencher explicitement une erreur basée sur vos propres décisions de routage.


## Syntaxe

```caddy-d
handle_errors [<codes_etat...>] {
	<directives...>
}
```

- **<codes_etat...>** est un ou plusieurs codes d'état HTTP à faire correspondre à l'erreur traitée. Les codes d'état peuvent être des nombres à 3 chiffres, ou les cas particuliers `4xx` ou `5xx` qui correspondent respectivement à tous les codes d'état dans les plages 400-499 ou 500-599. Si aucun code d'état n'est spécifié, alors elle correspondra à n'importe quelle erreur, agissant comme un repli si aucun autre gestionnaire d'erreurs ne correspond.

- **<directives...>** est une liste de [directives](/docs/caddyfile/directives) et de [sélecteurs](/docs/caddyfile/matchers) de gestionnaire HTTP, un par ligne.


<a id="placeholders"></a>
## Espaces réservés (Placeholders)

Les espaces réservés suivants sont disponibles lors de la gestion des erreurs. Ce sont des [raccourcis Caddyfile](/docs/caddyfile/concepts#placeholders) pour les espaces réservés complets qui peuvent être trouvés dans la [documentation JSON des routes d'erreur d'un serveur HTTP](/docs/json/apps/http/servers/errors/#routes).

| Espace réservé | Description |
|---|---|
| `{err.status_code}` | Le code d'état HTTP recommandé |
| `{err.status_text}` | Le texte de statut associé au code d'état recommandé |
| `{err.message}` | Le message d'erreur |
| `{err.trace}` | L'origine de l'erreur |
| `{err.id}` | Un identifiant pour cette occurrence de l'erreur |


## Exemples

Pages d'erreur personnalisées basées sur le code d'état (ex: une page nommée `404.html` pour les erreurs `404`). Notez que [`file_server`](file_server) préserve le code d'état HTTP de l'erreur lorsqu'il est exécuté dans `handle_errors` (suppose que vous avez défini une racine de site ([site root](root)) dans votre site au préalable) :

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Une page d'erreur unique qui utilise les modèles ([`templates`](templates)) pour écrire un message d'erreur personnalisé :

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Si vous souhaitez fournir des pages d'erreur personnalisées uniquement pour certains codes d'erreur, vous pouvez vérifier l'existence des fichiers d'erreur personnalisés au préalable avec un sélecteur [`file`](/docs/caddyfile/matchers#file) :

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

Proxy inverse vers un serveur professionnel hautement qualifié pour gérer les erreurs HTTP et améliorer votre journée 😸 :

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Utiliser simplement [`respond`](respond) pour retourner le code d'erreur et son nom :

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Pour gérer spécifiquement certains codes d'erreur différemment :

```caddy-d
handle_errors 404 410 {
	respond "C'est une erreur 404 ou 410 !"
}

handle_errors 5xx {
	respond "C'est une erreur 5xx."
}

handle_errors {
	respond "C'est une autre erreur"
}
```

Le code ci-dessus se comporte de la même manière que celui ci-dessous, qui utilise un sélecteur d' [expression `expression`](/docs/caddyfile/matchers#expression) sur les codes d'état, et utilise [`handle`](handle) pour l'exclusivité mutuelle :

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "C'est une erreur 404 ou 410 !"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "C'est une erreur 5xx."
	}

	handle {
		respond "C'est une autre error"
	}
}
```
