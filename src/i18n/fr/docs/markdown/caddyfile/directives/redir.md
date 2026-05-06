---
title: redir (directive Caddyfile)
---

# redir

Émet une redirection HTTP vers le client.

Cette directive implique qu'une requête correspondante doit être rejetée telle quelle, et que le client doit réessayer à une URL différente. Pour cette raison, son [ordre de directive](/docs/caddyfile/directives#directive-order) est très précoce.


## Syntaxe

```caddy-d
redir [<matcher>] <vers> [<code>]
```

- **&lt;vers&gt;** est l'emplacement cible. Devient l' [en-tête `Location` <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location) de la réponse.

- **&lt;code&gt;** est le code d'état HTTP à utiliser pour la redirection. Peut être :

	- Un entier positif dans la plage `3xx`, ou `401`.
	
	- `temporary` pour une redirection temporaire (`302`, c'est le défaut).
	
	- `permanent` pour une redirection permanente (`301`).
	
	- `html` pour utiliser un document HTML afin d'effectuer la redirection (utile pour rediriger les navigateurs mais pas les clients API).
	
	- Un espace réservé avec une valeur de code d'état.



## Exemples

Rediriger toutes les requêtes vers `https://example.com` :

```caddy
www.example.com {
	redir https://example.com
}
```

Même chose, mais en préservant l'URI existante en ajoutant l' [espace réservé `{uri}`](/docs/caddyfile/concepts#placeholders) :

```caddy
www.example.com {
	redir https://example.com{uri}
}

```

Même chose, mais de manière permanente :

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Rediriger votre ancienne page `/a-propos` vers votre nouvelle page `/about` :

```caddy
example.com {
	redir /a-propos /about
	reverse_proxy localhost:9000
}
```
