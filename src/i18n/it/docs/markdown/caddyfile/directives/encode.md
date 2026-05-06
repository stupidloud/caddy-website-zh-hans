---
title: encode (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();

	// Matcher di risposta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;" title="Matcher di risposta">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;" title="Matcher di risposta">header</a>';
		}
	});
});
</script>

# encode

Codifica le risposte utilizzando la codifica o le codifiche configurate. Un uso tipico della codifica è la compressione.

## Sintassi

```caddy-d
encode [<matcher>] [<formats...>] {
	# formati di codifica
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** è l'elenco dei formati di codifica da abilitare. Se sono abilitate più codifiche, la codifica viene scelta in base all'header `Accept-Encoding` della richiesta; se il client non ha una forte preferenza (q-factor), viene usata la prima codifica supportata. Se omesso, `zstd` (preferito) e `gzip` sono abilitati per impostazione predefinita.

- **gzip** <span id="gzip"/> abilita la compressione Gzip, opzionalmente a un livello specificato.

- **zstd** <span id="zstd"/> abilita la compressione Zstandard, opzionalmente a un livello specificato (valori possibili = default, fastest, better, best). Il livello di compressione predefinito è approssimativamente equivalente alla modalità Zstandard predefinita (livello 3).

- **minimum_length** <span id="minimum_length"/> il numero minimo di byte che una risposta deve avere per essere codificata (predefinito: 512).

- **match** <span id="match"/> è un [matcher di risposta](/docs/caddyfile/response-matchers). Solo le risposte corrispondenti vengono codificate. L'impostazione predefinita appare così:

  ```caddy-d
  match {
  	header Content-Type application/atom+xml*
  	header Content-Type application/eot*
  	header Content-Type application/font*
  	header Content-Type application/geo+json*
  	header Content-Type application/graphql+json*
  	header Content-Type application/javascript*
  	header Content-Type application/json*
  	header Content-Type application/ld+json*
  	header Content-Type application/manifest+json*
  	header Content-Type application/opentype*
  	header Content-Type application/otf*
  	header Content-Type application/rss+xml*
  	header Content-Type application/truetype*
  	header Content-Type application/ttf*
  	header Content-Type application/vnd.api+json*
  	header Content-Type application/vnd.ms-fontobject*
  	header Content-Type application/wasm*
  	header Content-Type application/x-httpd-cgi*
  	header Content-Type application/x-javascript*
  	header Content-Type application/x-opentype*
  	header Content-Type application/x-otf*
  	header Content-Type application/x-perl*
  	header Content-Type application/x-protobuf*
  	header Content-Type application/x-ttf*
  	header Content-Type application/xhtml+xml*
  	header Content-Type application/xml*
  	header Content-Type font/*
  	header Content-Type image/svg+xml*
  	header Content-Type image/vnd.microsoft.icon*
  	header Content-Type image/x-icon*
  	header Content-Type multipart/bag*
  	header Content-Type multipart/mixed*
  	header Content-Type text/*
  }
  ```


## Esempi

Abilita la compressione Gzip:

```caddy-d
encode gzip
```

Abilita la compressione Zstandard e Gzip (con Zstandard implicitamente preferito, poiché è il primo):

```caddy-d
encode zstd gzip
```

Dato che questo è il valore predefinito, la configurazione precedente è strettamente equivalente a:

```caddy-d
encode
```

E in un sito completo, comprimendo i file statici serviti da [`file_server`](file_server):

```caddy
example.com {
	root * /srv
	encode
	file_server
}
```
