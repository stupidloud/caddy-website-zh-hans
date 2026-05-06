---
title: encode (Caddyfile directive)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();

	// Response matchers
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;" title="Response matcher">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;" title="Response matcher">header</a>';
		}
	});
});
</script>

# encode

Codifica respuestas usando los formatos de codificación configurados. Un uso típico de la codificación es la compresión.

## Syntax

```caddy-d
encode [<matcher>] [<formats...>] {
	# encoding formats
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** es la lista de formatos de codificación que se habilitan. Si se habilitan múltiples codificaciones, se elige la codificación en función del encabezado Accept-Encoding de la solicitud; si el cliente no tiene una preferencia fuerte (factor q), se usa la primera codificación soportada. Si se omite, se habilitan `zstd` (preferido) y `gzip` de forma predeterminada.

- **gzip** <span id="gzip"/> habilita compresión Gzip, opcionalmente con un nivel especificado.

- **zstd** <span id="zstd"/> habilita compresión Zstandard, opcionalmente con un nivel especificado (valores posibles = default, fastest, better, best). El nivel de compresión predeterminado es aproximadamente equivalente al modo predeterminado de Zstandard (nivel 3).

- **minimum_length** <span id="minimum_length"/> es el número mínimo de bytes que debe tener una respuesta para ser codificada (predeterminado: 512).

- **match** <span id="match"/> es un [response matcher](/docs/caddyfile/response-matchers). Solo se codifican las respuestas que coinciden. El valor predeterminado es este:

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


## Examples

Habilita compresión Gzip:

```caddy-d
encode gzip
```

Habilita compresión Zstandard y Gzip (con Zstandard preferido implícitamente al ir primero):

```caddy-d
encode zstd gzip
```

Como este es el valor predeterminado, la configuración anterior es estrictamente equivalente a:

```caddy-d
encode
```

Y en un sitio completo, comprimiendo archivos estáticos servidos por [`file_server`](file_server):

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
