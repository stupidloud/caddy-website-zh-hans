---
title: request_body (directiva de Caddyfile)
---

# request_body

Manipula o establece restricciones sobre los cuerpos de las solicitudes entrantes.

## Sintaxis

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** es el tamaño máximo en bytes permitido para el cuerpo de la solicitud. Acepta todos los valores de tamaño compatibles con [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants). Leer más bytes devolverá un error con estado HTTP `413`.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** permite establecer el cuerpo de la solicitud con contenido específico. El contenido puede incluir placeholders para insertar datos dinámicamente.

## Ejemplos

Limitar el tamaño del cuerpo de la solicitud a 10 megabytes:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Establecer el cuerpo de la solicitud con una estructura JSON que contenga una consulta SQL:

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
