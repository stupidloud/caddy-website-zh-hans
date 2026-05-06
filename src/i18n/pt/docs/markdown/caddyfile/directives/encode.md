---
title: encode (diretiva do Caddyfile)
---

<script>
ready(function() {
	// Vamos adicionar links a todas as subdiretivas se um anchor correspondente for encontrado na página.
	addLinksToSubdirectives();

	// Matchers de resposta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;" title="Matcher de resposta">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;" title="Matcher de resposta">header</a>';
		}
	});
});
</script>

# encode

Codifica respostas usando o(s) encoding(s) configurado(s). Um uso típico de encoding é compressão.

## Sintaxe

```caddy-d
encode [<matcher>] [<formats...>] {
	# formatos de encoding
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** é a lista de formatos de encoding a habilitar. Se vários encodings estiverem habilitados, o encoding é escolhido com base no cabeçalho Accept-Encoding da requisição; se o cliente não tiver preferência forte (q-factor), então o primeiro encoding suportado é usado. Se omitido, `zstd` (preferido) e `gzip` são habilitados por padrão.

- **gzip** <span id="gzip"/> habilita compressão Gzip, opcionalmente em um nível especificado.

- **zstd** <span id="zstd"/> habilita compressão Zstandard, opcionalmente em um nível especificado (valores possíveis = default, fastest, better, best). O nível padrão de compressão é aproximadamente equivalente ao modo padrão do Zstandard (nível 3).

- **minimum_length** <span id="minimum_length"/> é o número mínimo de bytes que uma resposta deve ter para ser codificada (padrão: 512).

- **match** <span id="match"/> é um [matcher de resposta](/docs/caddyfile/response-matchers). Apenas respostas correspondentes serão codificadas. O padrão se parece com isto:

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


## Exemplos

Habilitar compressão Gzip:

```caddy-d
encode gzip
```

Habilitar compressão Zstandard e Gzip (com Zstandard implicitamente preferido, já que vem primeiro):

```caddy-d
encode zstd gzip
```

Como esse é o valor padrão, a configuração anterior é estritamente equivalente a:

```caddy-d
encode
```

E, em um site completo, compactando arquivos estáticos servidos por [`file_server`](file_server):

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
