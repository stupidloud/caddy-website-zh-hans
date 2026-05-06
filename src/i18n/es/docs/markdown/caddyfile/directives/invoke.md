---
title: invoke (Directiva de Caddyfile)
---

# invoke

<i>⚠️ Experimental</i>

Invoca una [ruta nombrada](/docs/caddyfile/concepts#named-routes).

Esto es útil cuando se combina con directivas de manejador HTTP que tienen su propio estado en memoria, o si son costosas de aprovisionar al cargar. Si tienes cientos de sitios o más, invocar una ruta nombrada puede ayudar a reducir el uso de memoria.

<aside class="tip">
	
A diferencia de [`import`](/docs/caddyfile/directives/import), `invoke` no admite argumentos, pero puedes usar [`vars`](/docs/caddyfile/directives/vars) para definir variables que se puedan usar dentro de la ruta nombrada.

</aside>

## Sintaxis

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** es el nombre de la ruta previamente definida que debe invocarse. Si no se encuentra la ruta, se producirá un error.


## Ejemplos

Define una [ruta nombrada](/docs/caddyfile/concepts#named-routes) con un [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) que se puede reutilizar en múltiples sitios, reutilizando el mismo estado de balanceo de carga en memoria para cada sitio.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# El dominio apex permite acceder a la app mediante la subruta /app
# y al sitio principal en cualquier otro caso.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# La app también es accesible mediante un subdominio.
app.example.com {
	invoke app-proxy
}
```
