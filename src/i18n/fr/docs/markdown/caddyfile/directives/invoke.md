---
title: invoke (directive Caddyfile)
---

# invoke

<i>⚠️ Expérimental</i>

Invoque une [route nommée](/docs/caddyfile/concepts#named-routes).

Ceci est utile lorsqu'associé à des directives de gestionnaire HTTP possédant leur propre état en mémoire, ou si elles sont coûteuses à initialiser (provision) lors du chargement. Si vous avez des centaines de sites ou plus, invoquer une route nommée peut aider à réduire l'utilisation de la mémoire.

<aside class="tip">
	
Contrairement à [`import`](/docs/caddyfile/directives/import), `invoke` ne supporte pas d'arguments, mais vous pouvez utiliser [`vars`](/docs/caddyfile/directives/vars) pour définir des variables utilisables au sein de la route nommée.

</aside>

## Syntaxe

```caddy-d
invoke [<matcher>] <nom-route>
```

- **&lt;nom-route&gt;** est le nom de la route précédemment définie qui doit être invoquée. Si la route n'est pas trouvée, une erreur sera déclenchée.


## Exemples

Définit une [route nommée](/docs/caddyfile/concepts#named-routes) avec un [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) pouvant être réutilisée dans plusieurs sites, avec le même état d'équilibrage de charge en mémoire partagé pour chaque site.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Le domaine apex permet d'accéder à l'application via un sous-chemin /app
# et au site principal sinon.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# L'application est également accessible via un sous-domaine.
app.example.com {
	invoke app-proxy
}
```
