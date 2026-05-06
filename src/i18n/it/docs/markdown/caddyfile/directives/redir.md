---
title: redir (direttiva del Caddyfile)
---

# redir

Invia un reindirizzamento HTTP al client.

Questa direttiva implica che una richiesta corrispondente debba essere rifiutata così com'è, e che il client debba riprovare a un URL differente. Per questa ragione, il suo [ordine della direttiva](/docs/caddyfile/directives#ordine-delle-direttive) è molto anticipato.


## Sintassi

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** è la posizione di destinazione. Diventa l'[header `Location`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location) della risposta.

- **&lt;code&gt;** è il codice di stato HTTP da usare per il reindirizzamento. Può essere:

	- Un numero intero positivo nell'intervallo `3xx`, oppure `401`
	
	- `temporary` per un reindirizzamento temporaneo (`302`, questo è il valore predefinito)
	
	- `permanent` per un reindirizzamento permanente (`301`)
	
	- `html` per usare un documento HTML per eseguire il reindirizzamento (utile per reindirizzare i browser ma non i client API)
	
	- Un placeholder con un valore di codice di stato



## Esempi

Reindirizza tutte le richieste a `https://example.com`:

```caddy
www.example.com {
	redir https://example.com
}
```

Lo stesso, ma preserva l'URI esistente aggiungendo il [placeholder `{uri}`](/docs/caddyfile/concepts#placeholder):

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

Lo stesso, ma permanente:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Reindirizza la vostra vecchia pagina `/about-us` alla nuova pagina `/about`:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
