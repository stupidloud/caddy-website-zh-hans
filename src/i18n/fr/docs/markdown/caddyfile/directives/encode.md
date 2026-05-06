---
title: encode (directive Caddyfile)
---

<script>
ready(function() {
	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();

	// Sélecteurs de réponse
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;" title="Sélecteur de réponse">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;" title="Sélecteur de réponse">header</a>';
		}
	});
});
</script>

# encode

Encode les réponses en utilisant l'encodage (ou les encodages) configuré(s). Un usage typique de l'encodage est la compression.

## Syntaxe

```caddy-d
encode [<matcher>] [<formats...>] {
	# formats d'encodage
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <taille>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** est la liste des formats d'encodage à activer. Si plusieurs encodages sont activés, l'encodage est choisi en fonction de l'en-tête `Accept-Encoding` de la requête ; si le client n'a pas de préférence marquée (q-factor), alors le premier encodage supporté est utilisé. Si omis, `zstd` (préféré) et `gzip` sont activés par défaut.

- **gzip** <span id="gzip"/> active la compression Gzip, optionnellement à un niveau spécifié.

- **zstd** <span id="zstd"/> active la compression Zstandard, optionnellement à un niveau spécifié (valeurs possibles = default, fastest, better, best). Le niveau de compression par défaut est approximativement équivalent au mode par défaut de Zstandard (niveau 3). 

- **minimum_length** <span id="minimum_length"/> le nombre minimum d'octets qu'une réponse doit avoir pour être encodée (par défaut : 512).

- **match** <span id="match"/> est un [sélecteur de réponse](/docs/caddyfile/response-matchers). Seules les réponses correspondantes sont encodées. Le défaut ressemble à ceci :

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


## Exemples

Activer la compression Gzip :

```caddy-d
encode gzip
```

Activer les compressions Zstandard et Gzip (avec Zstandard implicitement préféré, car il est listé en premier) :

```caddy-d
encode zstd gzip
```

Comme il s'agit de la valeur par défaut, la configuration précédente est strictement équivalente à :

```caddy-d
encode
```

Et dans un site complet, compresser les fichiers statiques servis par [`file_server`](file_server) :

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
