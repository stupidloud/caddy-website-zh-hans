---
title: error (директива Caddyfile)
---

# error

Вызывает ошибку в цепочке HTTP handler'ов, с необязательным сообщением и рекомендуемым HTTP status code. 

Этот handler не записывает ответ. Вместо этого он предназначен для использования вместе с директивой [`handle_errors`](handle_errors), чтобы вызвать вашу пользовательскую логику обработки ошибок.


<a id="syntax"></a>
## Синтаксис

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** — HTTP status code, который нужно записать. По умолчанию `500`.
- **&lt;message&gt;** — сообщение об ошибке. По умолчанию сообщение об ошибке отсутствует.
- **message** — альтернативный способ задать сообщение об ошибке; удобен, если оно занимает несколько строк.

Для ясности: первый аргумент, не являющийся matcher, может быть либо 3-значным status code, либо строкой сообщения об ошибке. Если это сообщение об ошибке, следующим аргументом может быть status code.


<a id="examples"></a>
## Примеры

Вызвать ошибку для определенных путей запроса и использовать [`handle_errors`](handle_errors), чтобы записать ответ:

```caddy
example.com {
	root /srv

	# Вызывать ошибки для определенных путей
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Обработать ошибку, отдав HTML-страницу 
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
