---
title: encode (Caddyfile directive)
---

<script>
ready(function() {
	// Wir fügen Links zu allen Subdirektiven hinzu, wenn ein passender Anker auf der Seite gefunden wird.
	addLinksToSubdirectives();

	// Response-Matcher
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

Kodiert Responses mit den konfigurierten Encoding(s). Ein typischer Anwendungsfall für Encoding ist Kompression.

<a id="syntax"></a>
## Syntax

```caddy-d
encode [<matcher>] [<formats...>] {
	# Encoding-Formate
	gzip [<level>]
	zstd [<level>]

	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** ist die Liste der zu aktivierenden Encoding-Formate. Wenn mehrere Encodings aktiviert sind, wird das Encoding anhand des Accept-Encoding-Headers des Requests ausgewählt; wenn der Client keine starke Präferenz (q-Faktor) hat, wird das erste unterstützte Encoding verwendet. Wenn weggelassen, sind standardmäßig `zstd` (bevorzugt) und `gzip` aktiviert.

- **gzip** <span id="gzip"/> aktiviert Gzip-Kompression, optional mit einem angegebenen Level.

- **zstd** <span id="zstd"/> aktiviert Zstandard-Kompression, optional mit einem angegebenen Level (mögliche Werte = default, fastest, better, best). Der Standard-Kompressionslevel entspricht ungefähr dem Standardmodus von Zstandard (Level 3).

- **minimum_length** <span id="minimum_length"/> ist die Mindestanzahl an Bytes, die eine Response haben muss, damit sie kodiert wird (Standard: 512).

- **match** <span id="match"/> ist ein [Response-Matcher](/docs/caddyfile/response-matchers). Nur passende Responses werden kodiert. Der Standard sieht so aus:

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


<a id="examples"></a>
## Beispiele

Gzip-Kompression aktivieren:

```caddy-d
encode gzip
```

Zstandard- und Gzip-Kompression aktivieren (wobei Zstandard implizit bevorzugt wird, da es zuerst steht):

```caddy-d
encode zstd gzip
```

Da dies der Standardwert ist, ist die vorherige Konfiguration exakt gleichwertig mit:

```caddy-d
encode
```

Und in einer vollständigen Site, mit Kompression statischer Dateien, die von [`file_server`](file_server) ausgeliefert werden:

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
