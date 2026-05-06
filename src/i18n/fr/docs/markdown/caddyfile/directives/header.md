---
title: header (directive Caddyfile)
---

# header

Manipule les champs d'en-tête de réponse HTTP. Elle peut définir, ajouter et supprimer des valeurs d'en-tête, ou effectuer des remplacements en utilisant des expressions régulières.

Par défaut, les opérations d'en-tête sont effectuées immédiatement, sauf si l'un des en-têtes est supprimé (préfixe `-`) ou si une valeur par défaut est définie (préfixe `?`). Dans ces cas, les opérations d'en-tête sont automatiquement différées jusqu'au moment où elles sont écrites vers le client.

Pour manipuler les en-têtes de requête HTTP, vous pouvez utiliser la directive [`request_header`](request_header).


## Syntaxe

```caddy-d
header [<matcher>] [[+|-|?|>]<champ> [<valeur>|<cherche>] [<remplace>]] {
	# Ajouter
	+<champ> <valeur>

	# Définir
	<champ> <valeur>

	# Définir avec defer
	><champ> <valeur>

	# Supprimer
	-<champ>

	# Remplacer
	<champ> <cherche> <remplace>

	# Remplacer avec defer
	><champ> <cherche> <remplace>

	# Valeur par défaut
	?<champ> <valeur>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;champ&gt;** est le nom du champ d'en-tête.

  Sans préfixe, le champ est défini (écrasé).

  Préfixez par `+` pour ajouter le champ au lieu de l'écraser s'il existe déjà ; les champs d'en-tête peuvent apparaître plus d'une fois dans une réponse.

  Préfixez par `-` pour supprimer le champ. Le champ peut utiliser les caractères génériques `*` en préfixe ou suffixe pour supprimer tous les champs correspondants.

  Préfixez par `?` pour définir une valeur par défaut pour le champ. Le champ n'est écrit que s'il n'existe pas encore.

  Préfixez par `>` pour définir le champ et activer `defer`, comme raccourci.

- **&lt;valeur&gt;** est la valeur du champ d'en-tête, lors de l'ajout ou de la définition d'un champ.

- **&lt;cherche&gt;** est l'expression régulière à rechercher. Les espaces réservés peuvent être utilisés pour une entrée dynamique dans le motif de recherche. Le langage d'expression régulière utilisé est RE2, inclus dans Go. Voir la [référence de syntaxe RE2](https://github.com/google/re2/wiki/Syntax) et l' [aperçu de la syntaxe regexp de Go](https://pkg.go.dev/regexp/syntax).

- **&lt;remplace&gt;** est la valeur de remplacement ; requise lors de l'exécution d'un chercher-remplacer. Utilisez `$1` ou `$2` et ainsi de suite pour référencer les groupes de capture du motif de recherche. Si la valeur de remplacement est `""`, alors le texte correspondant est supprimé de la valeur. Consultez la [documentation Go](https://golang.org/pkg/regexp/#Regexp.Expand) pour les détails.

- **defer** diffère l'exécution des opérations d'en-tête jusqu'à ce que la réponse soit envoyée au client. Cette option est automatiquement activée sous les conditions suivantes :
	- Lorsqu'un champ d'en-tête est supprimé avec `-`.
	- Lors de la définition d'une valeur par défaut avec `?`.
	- Lors de l'utilisation du préfixe `>` sur une opération de définition ou de remplacement.
	- Lorsqu'une ou plusieurs conditions `match` sont présentes.

- **match** <span id="match"/> est un [sélecteur de réponse](/docs/caddyfile/response-matchers) en ligne. Les opérations d'en-tête ne s'appliquent qu'aux réponses satisfaisant les conditions spécifiées.

Pour plusieurs manipulations d'en-têtes, vous pouvez ouvrir un bloc et spécifier une manipulation par ligne de la même manière.

Lors de l'utilisation du préfixe `?` pour définir une valeur d'en-tête par défaut, celle-ci est automatiquement séparée dans son propre gestionnaire `header`, si elle se trouvait dans un bloc `header` avec plusieurs opérations d'en-tête. [Sous le capot](/docs/modules/http.handlers.headers#response/require), l'utilisation de `?` configure un [sélecteur de réponse](/docs/caddyfile/response-matchers) qui s'applique à l'intégralité du gestionnaire de la directive, lequel n'applique les opérations d'en-tête (comme `defer`) que si le champ n'est pas encore défini.


## Exemples

Définir un champ d'en-tête personnalisé sur toutes les réponses :

```caddy-d
header Custom-Header "Ma valeur"
```

Supprimer le champ d'en-tête "Hidden" :

```caddy-d
header -Hidden
```

Remplacer `http://` par `https://` dans n'importe quel en-tête Location :

```caddy-d
header Location http:// https://
```

Définir des en-têtes de sécurité et de confidentialité sur toutes les pages : (**AVERTISSEMENT :** n'utilisez ceci que si vous en comprenez les implications !)

```caddy-d
header {
	# désactiver le traçage FLoC
	Permissions-Policy interest-cohort=()

	# activer le HSTS
	Strict-Transport-Security max-age=31536000;

	# empêcher les clients de deviner le type MIME
	X-Content-Type-Options nosniff

	# protection contre le clickjacking
	X-Frame-Options DENY
}
```

Plusieurs directives header destinées à être mutuellement exclusives :

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Définir une expiration de cache par défaut si l'amont n'en définit pas :

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Marquer toutes les réponses réussies aux requêtes GET comme pouvant être mises en cache jusqu'à une heure :

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Empêcher la mise en cache des réponses d'erreur en cas d'exception sur le serveur amont :

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Marquer les réponses en mode clair comme pouvant être mises en cache séparément des réponses en mode sombre si le serveur amont supporte les client hints :
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Empêcher les en-têtes CORS trop permissifs en remplaçant les valeurs wildcard par un domaine spécifique :
```caddy-d
header >Access-Control-Allow-Origin "\*" "partenaire-autorise.com"
reverse_proxy upstream:443
```
**Note** : Dans les opérations de remplacement, la valeur `<cherche>` est interprétée comme une expression régulière. Pour faire correspondre le caractère `*`, il doit être échappé avec un antislash comme montré dans l'exemple ci-dessus.

Alternativement, vous pouvez utiliser un [sélecteur de réponse](/docs/caddyfile/response-matchers) pour faire correspondre une valeur d'en-tête littérale :
```caddy-d
header Access-Control-Allow-Origin "partenaire-autorise.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Pour surcharger l'expiration du cache qu'un proxy amont a défini pour les chemins commençant par `/no-cache` ; l'activation de `defer` est nécessaire pour garantir que l'en-tête soit défini *après* que le proxy ait écrit ses en-têtes :

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Pour effectuer une mise à jour différée d'un en-tête `Set-Cookie` afin d'ajouter `SameSite=None` ; une capture regexp est utilisée pour récupérer la valeur existante, et `$1` la réinsère au début avec l'option supplémentaire ajoutée à la fin :

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
