---
title: redir (директива Caddyfile)
---

# redir

Выдает клиенту HTTP redirect.

Эта директива подразумевает, что совпавший запрос должен быть отклонен как есть, а клиент должен повторить попытку по другому URL. Поэтому ее [directive order](/docs/caddyfile/directives#directive-order) очень ранний.


<a id="syntax"></a>
## Синтаксис

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** — target location. Становится [`Location` header <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location) ответа.

- **&lt;code&gt;** — HTTP status code, используемый для redirect. Может быть:

	- Положительным integer в диапазоне `3xx` или `401`
	
	- `temporary` для временного redirect (`302`, значение по умолчанию)
	
	- `permanent` для постоянного redirect (`301`)
	
	- `html`, чтобы использовать HTML document для выполнения redirect (полезно для redirect browsers, но не API clients)
	
	- Placeholder со значением status code



<a id="examples"></a>
## Примеры

Перенаправить все запросы на `https://example.com`:

```caddy
www.example.com {
	redir https://example.com
}
```

То же самое, но сохранить существующий URI, добавив [placeholder `{uri}`](/docs/caddyfile/concepts#placeholders):

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

То же самое, но постоянно:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Перенаправить старую страницу `/about-us` на новую страницу `/about`:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
