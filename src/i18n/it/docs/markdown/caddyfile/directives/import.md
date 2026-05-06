---
title: import (direttiva del Caddyfile)
---

# import

Include uno [snippet](/docs/caddyfile/concepts#snippet) o un file, sostituendo questa direttiva con il contenuto dello snippet o del file.

Questa direttiva è un caso speciale: viene valutata prima che la struttura venga analizzata, e può apparire ovunque nel Caddyfile.

## Sintassi

```caddy-d
import <pattern> [<argomenti...>] [{block}]
```

- **&lt;pattern&gt;** è il nome del file, il pattern glob, o il nome dello [snippet](/docs/caddyfile/concepts#snippet) da includere. Il suo contenuto sostituirà questa riga come se il contenuto di quel file fosse apparso qui fin dall'inizio.

  È un errore se un file specifico non può essere trovato, ma un pattern glob vuoto non è un errore.

  Se si importa un file specifico, verrà emesso un avviso se il file è vuoto.

  Se il pattern è un nome di file o un glob, è sempre relativo al file in cui appare `import`.

  Se si usa un pattern glob `*` come segmento finale del percorso, i file nascosti (ovvero i file che iniziano con un `.`) vengono ignorati. Per importare i file nascosti, usate `.*` come segmento finale.
- **&lt;argomenti...&gt;** è un elenco opzionale di argomenti da passare ai token importati. Questo placeholder è un caso speciale e viene valutato al momento dell'analisi del Caddyfile, non a runtime. Possono essere usati in varie forme, in modo simile alla [sintassi degli slice di Go](https://gobyexample.com/slices):
  - `{args[n]}` dove `n` è l'indice posizionale 0-based del parametro
  - `{args[:]}` dove vengono inseriti tutti gli argomenti
  - `{args[:m]}` dove vengono inseriti gli argomenti prima di `m`
  - `{args[n:]}` dove vengono inseriti gli argomenti a partire da `n`
  - `{args[n:m]}` dove vengono inseriti gli argomenti nell'intervallo tra `n` e `m`

  Per le forme che inseriscono molti token, il placeholder **deve** essere un [token](/docs/caddyfile/concepts#token-e-virgolette) a sé stante, non può far parte di un altro token. In altre parole, deve avere spazi intorno e non può essere tra virgolette.

  Si noti che prima della v2.7.0, la sintassi era `{args.N}` ma questa forma è stata deprecata in favore della sintassi più flessibile descritta sopra.

⚠️ <i>Sperimentale</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** è un blocco opzionale da passare ai token importati. Questo placeholder è un caso speciale e viene valutato ricorsivamente al momento dell'analisi del Caddyfile, non a runtime. Possono essere usati in due forme:
  - `{block}` dove il contenuto dell'intero blocco fornito verrà sostituito al placeholder
  - `{blocks.key}` dove `key` è il primo token di un parametro all'interno del blocco fornito


## Esempi

Importa tutti i file in una cartella adiacente `sites-enabled` (eccetto i file nascosti):

```caddy-d
import sites-enabled/*
```

Importa uno snippet che imposta gli header CORS usando un argomento di importazione:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Importa uno snippet che accetta un elenco di upstream proxy come argomenti:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Importa uno snippet che crea un proxy con una regola di riscrittura del prefisso come primo argomento:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Sperimentale</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Importa uno snippet che risponde con un messaggio "hello world" e un content-type configurabili:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Importa uno snippet che fornisce opzioni estensibili per un reverse proxy:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Importa uno snippet che serve qualsiasi insieme di direttive, ma con un middleware precaricato:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
