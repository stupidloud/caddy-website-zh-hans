---
title: respond (директива Caddyfile)
---

# respond

Записывает клиенту hard-coded/static response.

Если body непустое, эта директива устанавливает header `Content-Type`, если он еще не установлен. Значение по умолчанию — `text/plain; utf-8`, если только body не является валидным JSON object или array; в этом случае устанавливается `application/json`. Для всех остальных типов содержимого явно задайте правильный Content-Type с помощью [директивы `header`](/docs/caddyfile/directives/header).


<a id="syntax"></a>
## Синтаксис

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** — HTTP status code, который нужно записать.

  Если это `103` (Early Hints), ответ будет записан без body, а handler chain продолжит выполнение. (Ответы HTTP `1xx` информационные, не финальные.)
  
  По умолчанию: `200`

- **&lt;body&gt;** — response body, которое нужно записать.

- **body** — альтернативный способ задать body; удобен, если оно занимает несколько строк.

- **close** закроет соединение клиента с сервером после записи ответа.

Для ясности: первый аргумент, не являющийся matcher, может быть либо 3-значным status code, либо строкой response body. Если это body, следующим аргументом может быть status code.

<aside class="tip">

Ответ с error status code отличается от возврата ошибки в handler chain, который внутренне вызывает error handlers.

</aside>


<a id="examples"></a>
## Примеры

Записать пустой status 200 с пустым body для всех health checks и простое response body для всех остальных запросов:

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

Записать error response и закрыть соединение:

<aside class="tip">

Возможно, лучше использовать [директиву `error`](error), которая вызывает ошибку, обрабатываемую [директивой `handle_errors`](handle_errors).

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

Записать HTML response, используя [heredoc syntax](/docs/caddyfile/concepts#heredocs) для контроля whitespace, а также установив header `Content-Type` в соответствии с response body:

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
