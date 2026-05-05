---
title: request_body (Caddyfile directive)
---

# request_body

Manipuliert die Bodys eingehender Requests oder setzt Einschränkungen dafür.

<a id="syntax"></a>
## Syntax

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** ist die maximal erlaubte Größe des Request-Bodys in Bytes. Akzeptiert alle Größenwerte, die von [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants) unterstützt werden. Lesevorgänge über mehr Bytes geben einen Fehler mit HTTP-Status `413` zurück.

⚠️ <i>Experimentell</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** erlaubt, den Request-Body auf bestimmte Inhalte zu setzen. Der Inhalt kann Platzhalter enthalten, um Daten dynamisch einzufügen.

<a id="examples"></a>
## Beispiele

Request-Body-Größen auf 10 Megabyte begrenzen:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Den Request-Body mit einer JSON-Struktur setzen, die eine SQL-Abfrage enthält:

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
