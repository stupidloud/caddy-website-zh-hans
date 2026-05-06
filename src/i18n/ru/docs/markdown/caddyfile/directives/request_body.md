---
title: request_body (директива Caddyfile)
---

# request_body

Изменяет или задает ограничения для bodies входящих запросов.

<a id="syntax"></a>
## Синтаксис

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** — максимальный размер request body в байтах. Принимает все size values, поддерживаемые [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants). Чтение большего количества байтов вернет ошибку с HTTP status `413`.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** позволяет установить request body в конкретное содержимое. Содержимое может включать placeholders для динамической вставки данных.

<a id="examples"></a>
## Примеры

Ограничить размеры request body до 10 мегабайт:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Установить request body со структурой JSON, содержащей SQL query:

```caddy
example.com {
	handle /jazz {
		request_body {
			set `\{"statementText":"SELECT name, genre, debut_year FROM artists WHERE genre = 'Jazz'"}`
		}

		reverse_proxy localhost:8080 {
			header_up Content-Type application/json
			method POST
			rewrite /execute-sql
		}
	}
}
```
