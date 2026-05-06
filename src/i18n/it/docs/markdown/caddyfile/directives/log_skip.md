---
title: log_skip (direttiva del Caddyfile)
---

# log_skip

Salta il logging degli accessi per le richieste corrispondenti.

Questa direttiva deve essere utilizzata insieme alla [direttiva `log`](log) per saltare il logging delle richieste che non sono rilevanti per le vostre necessità.

Prima della v2.8.0, questa direttiva si chiamava `skip_log`, ma è stata rinominata per coerenza con le altre direttive.


## Sintassi

```caddy-d
log_skip [<matcher>]
```


## Esempi

Salta il logging degli accessi per i file statici memorizzati in un sottopercorso:

```caddy
example.com {
	root * /srv

	log
	log_skip /static*

	file_server
}
```


Salta il logging degli accessi per le richieste che corrispondono a un pattern; in questo caso, per file con estensioni particolari:

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


Il matcher non è necessario se si trova all'interno di una rotta che è già all'interno di un matcher. Per esempio, con un handle per un file server per un sottopercorso particolare:

```caddy-d
handle_path /static* {
	root * /srv/static
	log_skip
	file_server
}
```
