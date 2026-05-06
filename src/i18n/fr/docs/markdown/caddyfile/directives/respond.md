---
title: respond (directive Caddyfile)
---

# respond

Écrit une réponse fixée (hard-coded) ou statique vers le client.

Si le corps n'est pas vide, cette directive définit l'en-tête `Content-Type` s'il n'est pas déjà défini. La valeur par défaut est `text/plain; utf-8`, sauf si le corps est un objet ou un tableau JSON valide, auquel cas elle est définie sur `application/json`. Pour tout autre type de contenu, définissez explicitement le `Content-Type` approprié en utilisant la [directive `header`](/docs/caddyfile/directives/header).


## Syntaxe

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <texte>
	close
}
```

- **&lt;status&gt;** est le code d'état HTTP à écrire.

  S'il vaut `103` (Early Hints), la réponse sera écrite sans corps et la chaîne de gestionnaires continuera. (Les réponses HTTP `1xx` sont informatives, pas finales.)
  
  Par défaut : `200`.

- **&lt;body&gt;** est le corps de la réponse à écrire.

- **body** est un autre moyen de fournir un corps ; pratique s'il s'étend sur plusieurs lignes.

- **close** fermera la connexion du client au serveur après avoir écrit la réponse.

Pour clarifier, le premier argument après le sélecteur peut être soit un code d'état à 3 chiffres, soit une chaîne de caractères de corps de réponse. S'il s'agit d'un corps, l'argument suivant peut être le code d'état.

<aside class="tip">

Répondre avec un code d'état d'erreur est différent de retourner une erreur dans la chaîne de gestionnaires, ce qui invoque les gestionnaires d'erreurs en interne.

</aside>


## Exemples

Écrire un statut 200 vide avec un corps vide pour toutes les vérifications de santé (health-checks), et un corps de réponse simple pour toutes les autres requêtes :

```caddy
example.com {
	respond /health-check 200
	respond "Bonjour le monde !"
}
```

Écrire une réponse d'erreur et fermer la connexion :

<aside class="tip">

Vous pourriez préférer utiliser la [directive `error`](error) à la place, laquelle déclenche une erreur pouvant être gérée avec la [directive `handle_errors`](handle_errors).

</aside>

```caddy
example.com {
	respond /secret/* "Accès refusé" 403 {
		close
	}
}
```

Écrire une réponse HTML, en utilisant la [syntaxe heredoc](/docs/caddyfile/concepts#heredocs) pour contrôler les espaces blancs, et en définissant également l'en-tête `Content-Type` pour correspondre au corps de la réponse :

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
