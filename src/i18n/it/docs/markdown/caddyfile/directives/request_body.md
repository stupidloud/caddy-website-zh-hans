---
title: request_body (direttiva del Caddyfile)
---

# request_body

Manipola o imposta restrizioni sui corpi delle richieste in entrata.

## Sintassi

```caddy-d
request_body [<matcher>] {
	max_size &lt;valore&gt;
	set &lt;body_content&gt;
}
```

- **max_size** è la dimensione massima in byte consentita per il corpo della richiesta. Accetta tutti i valori di dimensione supportati da [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants). Letture di un numero maggiore di byte restituiranno un errore con stato HTTP `413`.

⚠️ <i>Sperimentale</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** permette di impostare il corpo della richiesta a un contenuto specifico. Il contenuto può includere placeholder per inserire dinamicamente dei dati.

## Esempi

Limita le dimensioni dei corpi delle richieste a 10 megabyte:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Imposta il corpo della richiesta con una struttura JSON contenente una query SQL:

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
