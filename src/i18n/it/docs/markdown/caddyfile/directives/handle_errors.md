---
title: handle_errors (direttiva del Caddyfile)
---

# handle_errors

Configura gli handler degli errori.

Quando gli handler delle normali richieste HTTP restituiscono un errore, l'elaborazione normale si interrompe e vengono invocati gli handler degli errori. Gli handler degli errori formano una rotta che è proprio come le rotte normali, e possono fare tutto ciò che le rotte normali possono fare. Ciò consente un grande controllo e flessibilità nella gestione degli errori durante le richieste HTTP. Ad esempio, potete servire pagine di errore statiche, pagine di errore con template, o effettuare un reverse proxy verso un altro backend per gestire gli errori.

La direttiva può essere ripetuta con diversi codici di stato per gestire i vari errori in modo differente. Se non vengono specificati codici di stato, allora corrisponderà a qualsiasi errore, agendo come fallback se nessun altro handler degli errori corrisponde.

Il contesto di una richiesta viene portato nelle rotte degli errori, quindi eventuali valori impostati sul contesto della richiesta come la [root del sito](root) o le [vars](vars) saranno preservati anche negli handler degli errori. Inoltre, sono disponibili [nuovi placeholder](#placeholder) durante la gestione degli errori.

Si noti che determinate direttive, ad esempio [`reverse_proxy`](reverse_proxy) che potrebbe scrivere una risposta con uno stato HTTP classificato come errore, *non* innescheranno le rotte degli errori.

Potete usare la direttiva [`error`](error) per innescare esplicitamente un errore basandovi sulle vostre decisioni di routing.


## Sintassi

```caddy-d
handle_errors [<status_codes...>] {
	<direttive...>
}
```

- **&lt;status_codes...&gt;** è uno o più codici di stato HTTP da confrontare con l'errore gestito. I codici di stato possono essere numeri a 3 cifre, o un caso speciale di `4xx` o `5xx` che corrispondono rispettivamente a tutti i codici di stato negli intervalli 400-499 o 500-599. Se non vengono specificati codici di stato, allora corrisponderà a qualsiasi errore, agendo come fallback se nessun altro handler degli errori corrisponde.

- **&lt;direttive...&gt;** è un elenco di [direttive](/docs/caddyfile/directives) e [matcher](/docs/caddyfile/matchers) degli handler HTTP, uno per riga.


## Placeholder

I seguenti placeholder sono disponibili durante la gestione degli errori. Sono [scorciatoie del Caddyfile](/docs/caddyfile/concepts#placeholder) per i placeholder completi che possono essere trovati nella [documentazione JSON per le rotte di errore di un server HTTP](/docs/json/apps/http/servers/errors/#routes).

| Placeholder | Descrizione |
|---|---|
| `{err.status_code}` | Il codice di stato HTTP raccomandato |
| `{err.status_text}` | Il testo dello stato associato al codice di stato raccomandato |
| `{err.message}` | Il messaggio di errore |
| `{err.trace}` | L'origine dell'errore |
| `{err.id}` | Un identificativo per questa occorrenza dell'errore |


## Esempi

Pagine di errore personalizzate basate sul codice di stato (es. una pagina chiamata `404.html` per gli errori `404`). Notate che [`file_server`](file_server) preserva il codice di stato HTTP dell'errore quando viene eseguito in `handle_errors` (assume che abbiate impostato una [root del sito](root) nel vostro sito in precedenza):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Una singola pagina di errore che usa [`templates`](templates) per scrivere un messaggio di errore personalizzato:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Se volete fornire pagine di errore personalizzate solo per alcuni codici di errore, potete controllare preventivamente l'esistenza dei file di errore personalizzati con un matcher [`file`](/docs/caddyfile/matchers#file):

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

Reverse proxy verso un server professionale che è altamente qualificato per gestire gli errori HTTP e migliorare la vostra giornata 😸:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Semplicemente usate [`respond`](respond) per restituire il codice e il nome dell'errore:

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Per gestire specifici codici di errore in modo diverso:

```caddy-d
handle_errors 404 410 {
	respond "È un errore 404 o 410!"
}

handle_errors 5xx {
	respond "È un errore 5xx."
}

handle_errors {
	respond "È un altro errore"
}
```

Quanto sopra si comporta come quanto segue, che usa un matcher [`expression`](/docs/caddyfile/matchers#expression) contro i codici di stato, e utilizza [`handle`](handle) per la mutua esclusività:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "È un errore 404 o 410!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "È un errore 5xx."
	}

	handle {
		respond "È un altro errore"
	}
}
```
