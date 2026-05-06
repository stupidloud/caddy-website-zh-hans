---
title: encode (директива Caddyfile)
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

Кодирует ответы с использованием настроенных encoding(s). Типичное применение encoding — сжатие.

<a id="syntax"></a>
## Синтаксис

```caddy-d
encode [<matcher>] [<formats...>] {
	# encoding formats
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** — список включаемых encoding formats. Если включено несколько encodings, encoding выбирается на основе header Accept-Encoding запроса; если у клиента нет сильного предпочтения (q-factor), используется первый поддерживаемый encoding. Если опущено, по умолчанию включаются `zstd` (предпочтительно) и `gzip`.

- **gzip** <span id="gzip"/> включает Gzip-сжатие, опционально с указанным уровнем.

- **zstd** <span id="zstd"/> включает Zstandard-сжатие, опционально с указанным уровнем (возможные значения = default, fastest, better, best). Уровень сжатия по умолчанию примерно соответствует стандартному режиму Zstandard (level 3). 

- **minimum_length** <span id="minimum_length"/> — минимальное число байтов, которое должен иметь ответ, чтобы он был закодирован (по умолчанию: 512).

- **match** <span id="match"/> — [response matcher](/docs/caddyfile/response-matchers). Кодируются только совпадающие ответы. Значение по умолчанию выглядит так:

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
## Примеры

Включить Gzip-сжатие:

```caddy-d
encode gzip
```

Включить Zstandard- и Gzip-сжатие (Zstandard неявно предпочтителен, потому что он указан первым):

```caddy-d
encode zstd gzip
```

Поскольку это значение по умолчанию, предыдущая конфигурация строго эквивалентна:

```caddy-d
encode
```

А в полном сайте — сжимать статические файлы, отдаваемые [`file_server`](file_server):

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
