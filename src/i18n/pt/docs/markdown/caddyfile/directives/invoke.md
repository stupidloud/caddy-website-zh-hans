---
title: invoke (diretiva do Caddyfile)
---

# invoke

<i>⚠️ Experimental</i>

Invoca uma [rota nomeada](/docs/caddyfile/concepts#named-routes).

Isso é útil quando combinado com diretivas de HTTP handler que têm seu próprio estado em memória, ou se elas são caras para provisionar no carregamento. Se você tiver centenas de sites ou mais, invocar uma rota nomeada pode ajudar a reduzir o uso de memória.

<aside class="tip">
	
Diferentemente de [`import`](/docs/caddyfile/directives/import), `invoke` não suporta argumentos, mas você pode usar [`vars`](/docs/caddyfile/directives/vars) para definir variáveis que podem ser usadas dentro da rota nomeada.

</aside>

## Sintaxe

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** é o nome da rota previamente definida que deve ser invocada. Se a rota não for encontrada, um erro será disparado.


## Exemplos

Define uma [rota nomeada](/docs/caddyfile/concepts#named-routes) com um [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) que pode ser reutilizada em vários sites, com o mesmo estado de balanceamento de carga em memória reaproveitado para cada site.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# O domínio apex permite acessar o app via um subcaminho /app
# e o site principal de outra forma.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# O app também fica acessível via um subdomínio.
app.example.com {
	invoke app-proxy
}
```
