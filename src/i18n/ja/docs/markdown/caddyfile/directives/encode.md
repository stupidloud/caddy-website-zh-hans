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

設定された encoding を使ってレスポンスをエンコードします。encoding の典型的な用途は圧縮です。

<a id="syntax"></a>
## 構文

```caddy-d
encode [<matcher>] [<formats...>] {
	# encoding formats
	gzip [<level>]
	zstd [<level>]

	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** は、有効にする encoding format のリストです。複数の encoding が有効な場合、リクエストの Accept-Encoding header に基づいて encoding が選ばれます。クライアントに強い優先度（q-factor）がない場合は、最初にサポートされている encoding が使われます。省略すると、デフォルトで `zstd`（優先）と `gzip` が有効になります。

- **gzip** <span id="gzip"/> は Gzip 圧縮を有効にします。任意で level を指定できます。

- **zstd** <span id="zstd"/> は Zstandard 圧縮を有効にします。任意で level を指定できます（指定可能な値 = default、fastest、better、best）。デフォルトの圧縮 level は、Zstandard のデフォルトモード（level 3）とほぼ同等です。

- **minimum_length** <span id="minimum_length"/> は、レスポンスをエンコードするために必要な最小バイト数です（デフォルト: 512）。

- **match** <span id="match"/> は [response matcher](/docs/caddyfile/response-matchers) です。一致するレスポンスだけがエンコードされます。デフォルトは次のようになります。

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
## 例

Gzip 圧縮を有効にします。

```caddy-d
encode gzip
```

Zstandard と Gzip 圧縮を有効にします（Zstandard が先にあるため暗黙的に優先されます）。

```caddy-d
encode zstd gzip
```

これはデフォルト値なので、前の設定は厳密には次と同等です。

```caddy-d
encode
```

完全なサイト内で、[`file_server`](file_server) によって提供される静的ファイルを圧縮します。

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
