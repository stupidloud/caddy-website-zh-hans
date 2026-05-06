---
title: invoke (директива Caddyfile)
---

# invoke

<i>⚠️ Experimental</i>

Вызывает [named route](/docs/caddyfile/concepts#named-routes).

Это полезно в сочетании с HTTP handler directives, у которых есть собственное in-memory state, или если их дорого provision при загрузке. Если у вас сотни sites или больше, вызов named route может помочь снизить использование памяти.

<aside class="tip">
	
В отличие от [`import`](/docs/caddyfile/directives/import), `invoke` не поддерживает аргументы, но можно использовать [`vars`](/docs/caddyfile/directives/vars), чтобы определить переменные, доступные внутри named route.

</aside>

<a id="syntax"></a>
## Синтаксис

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** — имя ранее определенного route, который должен быть вызван. Если route не найден, будет вызвана ошибка.


<a id="examples"></a>
## Примеры

Определяет [named route](/docs/caddyfile/concepts#named-routes) с [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy), который можно повторно использовать в нескольких sites, с тем же in-memory load balancing state, переиспользуемым для каждого site.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Apex domain позволяет обращаться к app через subpath /app,
# а иначе обслуживает main site.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# App также доступно через subdomain.
app.example.com {
	invoke app-proxy
}
```
