---
title: handle_errors (директива Caddyfile)
---

# handle_errors

Настраивает handlers ошибок.

Когда обычные HTTP request handlers возвращают ошибку, нормальная обработка останавливается и вызываются error handlers. Error handlers образуют route, похожий на обычные routes, и могут делать все, что могут обычные routes. Это дает большой контроль и гибкость при обработке ошибок во время HTTP requests. Например, можно отдавать статические страницы ошибок, шаблонные страницы ошибок или проксировать запрос в другой backend для обработки ошибок.

Директиву можно повторять с разными status codes, чтобы по-разному обрабатывать разные ошибки. Если status codes не указаны, она совпадает с любой ошибкой и работает как fallback, если другие error handlers не совпали.

Контекст запроса переносится в error routes, поэтому любые значения, установленные в request context, такие как [site root](root) или [vars](vars), также сохраняются в error handlers. Кроме того, при обработке ошибок доступны [новые placeholders](#placeholders).

Обратите внимание, что некоторые директивы, например [`reverse_proxy`](reverse_proxy), которая может записать ответ с HTTP status, классифицируемым как ошибка, *не* запускают error routes.

Можно использовать директиву [`error`](error), чтобы явно вызвать ошибку на основе собственных routing decisions.


<a id="syntax"></a>
## Синтаксис

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** — один или несколько HTTP status codes, с которыми нужно сопоставить обрабатываемую ошибку. Status codes могут быть 3-значными числами или специальными значениями `4xx` либо `5xx`, которые соответствуют всем status codes в диапазонах 400-499 или 500-599 соответственно. Если status codes не указаны, совпадает с любой ошибкой и работает как fallback, если другие error handlers не совпали.

- **<directives...>** — список HTTP handler [directives](/docs/caddyfile/directives) и [matchers](/docs/caddyfile/matchers), по одному в строке.


<a id="placeholders"></a>
## Placeholders

Следующие placeholders доступны во время обработки ошибок. Это [сокращения Caddyfile](/docs/caddyfile/concepts#placeholders) для полных placeholders, которые можно найти в [JSON-документации по error routes HTTP server](/docs/json/apps/http/servers/errors/#routes).

| Placeholder | Описание |
|---|---|
| `{err.status_code}` | Рекомендуемый HTTP status code |
| `{err.status_text}` | Текст status, связанный с рекомендуемым status code |
| `{err.message}` | Сообщение об ошибке |
| `{err.trace}` | Источник ошибки |
| `{err.id}` | Идентификатор этого возникновения ошибки |


<a id="examples"></a>
## Примеры

Пользовательские страницы ошибок на основе status code (например, страница `404.html` для ошибок `404`). Обратите внимание, что [`file_server`](file_server) сохраняет HTTP status code ошибки при запуске внутри `handle_errors` (предполагается, что вы заранее задали [site root](root) в своем site):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Единая страница ошибки, использующая [`templates`](templates), чтобы записать пользовательское сообщение об ошибке:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Если нужно предоставлять пользовательские страницы ошибок только для некоторых error codes, можно заранее проверить существование пользовательских файлов ошибок с помощью matcher [`file`](/docs/caddyfile/matchers#file):

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

Reverse proxy к профессиональному серверу, который отлично умеет обрабатывать HTTP errors и улучшать ваш день 😸:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Просто использовать [`respond`](respond), чтобы вернуть error code и name

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Чтобы по-разному обрабатывать конкретные error codes:

```caddy-d
handle_errors 404 410 {
	respond "It's a 404 or 410 error!"
}

handle_errors 5xx {
	respond "It's a 5xx error."
}

handle_errors {
	respond "It's another error"
}
```

Вариант выше ведет себя так же, как вариант ниже, который использует matcher [`expression`](/docs/caddyfile/matchers#expression) по status codes и [`handle`](handle) для взаимного исключения:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "It's a 404 or 410 error!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "It's a 5xx error."
	}

	handle {
		respond "It's another error"
	}
}
```
