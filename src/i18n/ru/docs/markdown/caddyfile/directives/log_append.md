---
title: log_append (директива Caddyfile)
---

# log_append

Добавляет поле в access log для текущего запроса.

Ее следует использовать вместе с [директивой `log`](log), которая изначально нужна для включения access logging.

Значение может быть статической строкой или [placeholder](/docs/caddyfile/concepts#placeholders), который во время запроса будет заменен значением placeholder.


<a id="syntax"></a>
## Синтаксис

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

По умолчанию поле log добавляется при обратном проходе вверх по middleware chain (т. е. "late"), после завершения всех последующих handlers (например, после handlers вроде [`reverse_proxy`](reverse_proxy), [`respond`](respond) или [`file_server`](file_server), которые записывают ответ), поэтому оно фиксирует финальное состояние запроса и ответа.

Если `<` используется как prefix к key, поле помечается как "early"; это означает, что поле log будет добавлено в logs *до* вызова следующего handler в цепочке, так что запрос можно прочитать до его изменения последующими handlers.

Только для отладки (не для production) handler имеет специальную обработку, когда значение является одним из этих placeholders: `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}` или `{http.response.body_base64}`. Если используется placeholder тела запроса, режим "early" включается неявно, а тело запроса будет buffered. Если используется placeholder тела ответа, включается buffering ответа, чтобы захватить тело ответа, а поле добавляется в log "late" во время записи ответа.


<a id="examples"></a>
## Примеры

Показать в logs область сайта, из которой обслуживается запрос: `static` или `dynamic`:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

Показать в logs, какой reverse proxy upstream фактически использовался (`node1`, `node2` или `node3`), а также
время проксирования к upstream в миллисекундах и то, сколько времени proxy upstream потребовалось, чтобы записать response header:

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Поле можно добавить в logs "early", поставив перед key prefix `<`. Это позволяет захватить состояние запроса до его изменения последующими handlers. Например, чтобы записать исходный request path до rewrite (хотя это искусственный пример, поскольку исходный request path и так уже записывается, но он помогает показать идею):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

Для отладки добавьте bodies запроса и ответа в logs (не используйте в production, так как это снижает производительность и делает logs очень шумными). Если ожидается, что bodies будут binary data с непечатаемыми символами, можно использовать base64-варианты placeholders (например, `{http.request.body_base64}` и `{http.response.body_base64}`), которые будет проще копировать и проверять:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
