---
title: "push（Caddyfile 指令）"
---

# 推送

将服务器配置为使用 HTTP/2 服务器推送功能，主动向客户端发送资源。

可以通过指定响应中的 Link 标头来将资源与服务器推送关联。该指令将自动推送上游 Link 标头中描述的资源，支持以下格式：

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

其中 `<resource>` 以正斜杠开头 `/` （即具有相同主机的 URI 路径）。仅可推送同一主机上的资源。如果链接的资源是外部资源，或者它具有 `nopush` 属性，则不会被推送。

默认情况下，POST请求会包含一些被认为可以安全地从原始请求中复制的头部字段：

- Accept-Encoding
- Accept-Language
- 接受
- Cache-Control
- 用户代理

由于预计在缺少这些标头的情况下，许多请求会失败，因此无需手动配置这些标头。

推送请求在内部经过虚拟化处理，因此非常轻量级。


## 语法

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** 是要推送的目标 URI 路径。如果在该代码块中使用，其前可选地添加方法（GET 或 POST；默认是 GET）。
- **&lt;headers&gt;** 通过与 [`header` 指令](/docs/caddyfile/directives/header)相同的语法来处理推送请求的头部信息。某些头部信息会默认被保留，无需显式配置（参见上文）。



## 示例

将响应中包含的 `Link` 响应中的标头所描述的任何资源：

```caddy-d
push
```

同上，但还要推送 `/resources/style.css` 针对所有请求：

```caddy-d
push * /resources/style.css
```

点击 `/foo.jpg` 仅当 `/foo.html` 客户端请求时：

```caddy-d
push /foo.html /foo.jpg
```
