---
title: error (direttiva del Caddyfile)
---

# error

Innesca un errore nella catena degli handler HTTP, con un messaggio opzionale e un codice di stato HTTP raccomandato.

Questo handler non scrive una risposta. Invece, è inteso per essere accoppiato con la direttiva [`handle_errors`](handle_errors) per invocare la vostra logica personalizzata di gestione degli errori.


## Sintassi

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** è il codice di stato HTTP da scrivere. Predefinito: `500`.
- **&lt;message&gt;** è il messaggio di errore. Per impostazione predefinita, nessun messaggio di errore.
- **message** è un modo alternativo per fornire un messaggio di errore; comodo se è su più righe.

Per chiarire, il primo argomento non-matcher può essere o un codice di stato a 3 cifre, o una stringa di messaggio di errore. Se è un messaggio di errore, l'argomento successivo può essere il codice di stato.


## Esempi

Innesca un errore su determinati percorsi di richiesta, e usa [`handle_errors`](handle_errors) per scrivere una risposta:

```caddy
example.com {
	root * /srv

	# Innesca errori per determinati percorsi
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Gestisce l'errore servendo una pagina HTML
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
