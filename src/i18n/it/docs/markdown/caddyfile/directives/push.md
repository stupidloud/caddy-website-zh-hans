---
title: push (direttiva del Caddyfile)
---

# push

Configura il server per inviare preventivamente risorse al client utilizzando il server push di HTTP/2.

Le risorse possono essere collegate per il server push specificando gli header `Link` della risposta. Questa direttiva invierà automaticamente le risorse descritte dagli header `Link` dell'upstream in questi formati:

- `<risorsa>; as=script`
- `<risorsa>; as=script,<risorsa>; as=style`
- `<risorsa>; nopush`
- `<risorsa>;<risorsa2>;...`

dove `<risorsa>` inizia con una barra in avanti `/` (ovvero è un percorso URI con lo stesso host). Solo le risorse dello stesso host possono essere inviate tramite push. Se una risorsa collegata è esterna o se ha l'attributo `nopush`, non verrà inviata.

Per impostazione predefinita, le richieste push includeranno alcuni header ritenuti sicuri da copiare dalla richiesta originale:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

poiché si assume che molte richieste fallirebbero senza questi header; questi non devono essere configurati manualmente.

Le richieste push sono virtualizzate internamente, quindi sono molto leggere.


## Sintassi

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** è il percorso URI di destinazione da inviare tramite push. Se usato all'interno del blocco, può essere opzionalmente preceduto dal metodo (GET o HEAD; GET è l'impostazione predefinita).
- **&lt;headers&gt;** manipola gli header della richiesta push utilizzando la stessa sintassi della [direttiva `header`](/docs/caddyfile/directives/header). Alcuni header vengono portati per impostazione predefinita e non devono essere configurati esplicitamente (vedi sopra).



## Esempi

Invia tramite push qualsiasi risorsa descritta dagli header `Link` nella risposta:

```caddy-d
push
```

Lo stesso, ma invia anche `/resources/style.css` per tutte le richieste:

```caddy-d
push * /resources/style.css
```

Invia `/foo.jpg` solo quando `/foo.html` viene richiesto dal client:

```caddy-d
push /foo.html /foo.jpg
```
