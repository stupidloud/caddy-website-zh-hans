---
title: invoke (Caddyfile directive)
---

# invoke

<i>⚠️ Experimental</i>

Ruft eine [benannte Route](/docs/caddyfile/concepts#named-routes) auf.

Das ist nützlich in Kombination mit HTTP-Handler-Direktiven, die eigenen In-Memory-State haben oder beim Laden teuer zu provisionieren sind. Wenn Sie hunderte Sites oder mehr haben, kann das Aufrufen einer benannten Route helfen, den Speicherverbrauch zu reduzieren.

<aside class="tip">
	
Anders als [`import`](/docs/caddyfile/directives/import) unterstützt `invoke` keine Argumente; Sie können aber [`vars`](/docs/caddyfile/directives/vars) verwenden, um Variablen zu definieren, die innerhalb der benannten Route verwendet werden können.

</aside>

<a id="syntax"></a>
## Syntax

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** ist der Name der zuvor definierten Route, die aufgerufen werden soll. Wenn die Route nicht gefunden wird, wird ein Fehler ausgelöst.


<a id="examples"></a>
## Beispiele

Definiert eine [benannte Route](/docs/caddyfile/concepts#named-routes) mit einem [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy), die in mehreren Sites wiederverwendet werden kann, wobei derselbe In-Memory-Load-Balancing-State für jede Site wiederverwendet wird.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Apex-Domain erlaubt den Zugriff auf die App über einen /app-Unterpfad
# und ansonsten auf die Hauptsite.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# Die App ist auch über eine Subdomain erreichbar.
app.example.com {
	invoke app-proxy
}
```
