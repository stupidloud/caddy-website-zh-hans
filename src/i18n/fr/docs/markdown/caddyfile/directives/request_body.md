---
title: request_body (directive Caddyfile)
---

# request_body

Manipule ou définit des restrictions sur les corps des requêtes entrantes.

## Syntaxe

```caddy-d
request_body [<matcher>] {
	max_size <valeur>
	set <contenu_corps>
}
```

- **max_size** est la taille maximale en octets autorisée pour le corps de la requête. Elle accepte toutes les valeurs de taille supportées par [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants). La lecture de plus d'octets retournera une erreur avec le statut HTTP `413`.

⚠️ <i>Expérimental</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** permet de définir le corps de la requête sur un contenu spécifique. Le contenu peut inclure des espaces réservés pour insérer des données de manière dynamique.

## Exemples

Limiter la taille du corps de la requête à 10 mégaoctets :

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Définir le corps de la requête avec une structure JSON contenant une requête SQL :

```caddy
example.com {
	handle /jazz {
		request_body {
			set `\{"statementText":"SELECT name, genre, debut_year FROM artists WHERE genre = 'Jazz'"}`
		}

		reverse_proxy localhost:8080 {
			header_up Content-Type application/json
			method POST
			rewrite /execute-sql
		}
	}
}
```
