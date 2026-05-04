---
title: "encode（Caddyfile 指令）"
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

# 编码

使用配置的编码对响应进行编码。编码的典型用途是压缩。

## 语法

```caddy-d
encode [<matcher>] [<formats...>] {
	# encoding formats
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** 是待启用的编码格式列表。如果启用了多种编码，则根据请求的 Accept-Encoding 头部选择编码；如果客户端没有明确偏好（q-factor），则使用第一个受支持的编码。如果省略， `zstd` (preferred) 和 `gzip` 将默认启用。

- **gzip** <span id="gzip"/> 启用 Gzip 压缩，可选指定压缩级别。

- **zstd** <span id="zstd"/> 启用 Zstandard 压缩，可选指定压缩级别（可用值：default、fastest、better、best）。默认压缩级别大致相当于 Zstandard 的默认模式（级别 3）。 

- **minimum_length** <span id="minimum_length"/> 响应要被编码所需的最小字节数（默认值：512）。

- **match** <span id="match"/> 是一个[响应匹配器](/docs/caddyfile/response-matchers)。只有匹配的响应才会被编码。默认配置如下：

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


## 示例

启用 Gzip 压缩：

```caddy-d
encode gzip
```

启用 Zstandard 和 Gzip 压缩（由于 Zstandard 排在前面，因此默认优先使用它）：

```caddy-d
encode zstd gzip
```

由于这是默认值，因此上述配置与以下内容完全等同：

```caddy-d
encode
```

在完整网站中，对由 [`file_server`](file_server) 提供的静态文件进行压缩：

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
