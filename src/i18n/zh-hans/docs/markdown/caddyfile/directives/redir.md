---
title: "redir（Caddyfile 指令）"
---

# redir

向客户端发出 HTTP 重定向。

该指令表示，匹配到的请求应原样被拒绝，客户端应尝试访问其他 URL。因此，该[指令](/docs/caddyfile/directives#directive-order)在[规则列表中的位置](/docs/caddyfile/directives#directive-order)非常靠前。


## 语法

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** 是目标位置。它将成为响应的 <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location">`Location` 标头 <img src="/old/resources/images/external-link.svg" class="external-link"></a>。

- **&lt;code&gt;** 是重定向时使用的 HTTP 状态码。可以是：

	- 该范围内的正整数 `3xx` 范围内，或 `401`
	
	- `temporary` 用于临时重定向（`302`，这是默认设置）
	
	- `permanent` 用于永久重定向（`301`)
	
	- `html` 使用 HTML 文档来执行重定向（适用于重定向浏览器，但不适用于 API 客户端）
	
	- 包含状态码值的占位符



## 示例

将所有请求重定向至 `https://example.com`:

```caddy
www.example.com {
	redir https://example.com
}
```

同上，但通过在现有 URI 后附加 [`{uri}` 占位符](/docs/caddyfile/concepts#placeholders)来保留原有 URI：

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

同上，但永久生效：

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

将旧的 `/about-us` 页面到您的 `/about` 页面：

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
