---
title: encode (Caddyfile 指令)
---

<script>
ready(function() {
	// 如果在頁面中找到匹配的錨點標籤，我們將添加指向所有子指令的鏈接。
	addLinksToSubdirectives();

	// 回應匹配器 (Response matchers)
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

<a id="encode"></a>
# encode

使用配置的編碼格式對回應進行編碼。編碼的一個典型用途是壓縮。

<a id="syntax"></a>
## 語法

```caddy-d
encode [<matcher>] [<formats...>] {
	# 編碼格式
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** 是要啟用的編碼格式列表。如果啟用了多個編碼，將根據請求的 `Accept-Encoding` 標頭選擇編碼；如果客戶端沒有強烈偏好 (q-factor)，則使用第一個支援的編碼。如果省略，預設會啟用 `zstd` (首選) 和 `gzip`。

- **gzip** <span id="gzip"/> 啟用 Gzip 壓縮，可選指定級別。

- **zstd** <span id="zstd"/> 啟用 Zstandard 壓縮，可選指定級別（可能的值 = `default`, `fastest`, `better`, `best`）。預設壓縮級別大致相當於預設的 Zstandard 模式（級別 3）。

- **minimum_length** <span id="minimum_length"/> 回應應具有的最小位元組數才能進行編碼（預設：512）。

- **match** <span id="match"/> 是一個 [response matcher](/docs/caddyfile/response-matchers)。只有匹配的回應才會被編碼。預設如下所示：

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
## 範例

啟用 Gzip 壓縮：

```caddy-d
encode gzip
```

啟用 Zstandard 和 Gzip 壓縮（隱式首選 Zstandard，因為它排在第一位）：

```caddy-d
encode zstd gzip
```

由於這是預設值，前面的配置與以下配置完全等價：

```caddy-d
encode
```

在一個完整的站點中，壓縮由 [`file_server`](file_server) 提供服務的靜態檔案：

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
