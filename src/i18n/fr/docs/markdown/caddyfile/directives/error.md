---
title: error (directive Caddyfile)
---

# error

Déclenche une erreur dans la chaîne de gestionnaires HTTP, avec un message optionnel et un code d'état HTTP recommandé. 

Ce gestionnaire n'écrit pas de réponse. Il est plutôt destiné à être associé à la directive [`handle_errors`](handle_errors) pour invoquer votre logique personnalisée de gestion des erreurs.


## Syntaxe

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <texte>
}
```

- **&lt;status&gt;** est le code d'état HTTP à utiliser. Par défaut : `500`.
- **&lt;message&gt;** est le message d'erreur. Par défaut, aucun message.
- **message** est une autre façon de fournir un message d'erreur ; pratique s'il s'étend sur plusieurs lignes.

Pour clarifier, le premier argument après le sélecteur peut être soit un code d'état à 3 chiffres, soit une chaîne de caractères de message d'erreur. S'il s'agit d'un message d'erreur, l'argument suivant peut être le code d'état.


## Exemples

Déclencher une erreur sur certains chemins de requête, et utiliser [`handle_errors`](handle_errors) pour écrire une réponse :

```caddy
example.com {
	root /srv

	# Déclencher des erreurs pour certains chemins
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Gérer l'erreur en servant une page HTML
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
