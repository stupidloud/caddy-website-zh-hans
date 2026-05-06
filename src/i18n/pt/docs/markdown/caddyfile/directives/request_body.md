---
title: request_body (diretiva do Caddyfile)
---

# request_body

Manipula ou define restrições sobre os corpos de requisições de entrada.

## Sintaxe

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** é o tamanho máximo, em bytes, permitido para o corpo da requisição. Aceita todos os valores de tamanho suportados por [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants). Leituras acima desse valor retornarão um erro com status HTTP `413`.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** permite definir o corpo da requisição para um conteúdo específico. O conteúdo pode incluir placeholders para inserir dados dinamicamente.

## Exemplos

Limitar o tamanho do corpo da requisição a 10 megabytes:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Definir o corpo da requisição com uma estrutura JSON contendo uma query SQL:

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
