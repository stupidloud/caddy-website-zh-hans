---
title: "rewrite（Caddyfile 指令）"
---

# rewrite

在内部重写请求 URI。

rewrite 会改变请求 URI 的一部分或全部内容。注意，URI 不包含方案和权限信息（host 与 port），客户端通常也不会发送 fragment，因此该指令主要用于**路径**和**查询字符串**改写。

`rewrite` 表示“接收该请求，但带修改”。

它与同块内其他 `rewrite` 指令互斥，因此即使定义了本可级联执行的重写，也只会执行第一个匹配的 `rewrite`。

在 `rewrite` 前匹配请求的[请求匹配器](/docs/caddyfile/matchers)可能在重写后不再匹配该请求。如果你希望 `rewrite` 与其他处理器处于同一 route，请使用 [`route`](route) 或 [`handle`](handle) 指令。

## 语法

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** 是要重写到的目标 URI。重写只会作用于 URI 中显式指定的组件（路径或查询字符串）。URI 路径是 `?` 之前的字符串；若省略 `?`，则整段 token 将被视为路径。

在 v2.8.0 之前，如果 `<to>` 以 `/` 开头，解析器可能会将其误认为是 [匹配器 token](/docs/caddyfile/matchers#syntax)，因此当时需要显式写上通配符匹配器 token（`*`）。

## 类似指令

还存在其他用于改写的指令，但它们表达的意图不同，或是没有完整替换 URI 就实现改写：

- [`uri`](uri) 操作 URI（前缀、后缀或子串替换）。

- [`try_files`](try_files) 会根据文件是否存在来重写请求。


## 示例

将所有请求改写到 `index.html`，并保持查询字符串不变：

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

注意，在 v2.8.0 之前，这里需要使用 [通配符匹配器](/docs/caddyfile/matchers#wildcard-matchers)，因为第一个参数与 [路径匹配器](/docs/caddyfile/matchers#path-matchers)存在歧义，例如 `rewrite * /foo`，现在可简化为 `rewrite /foo`。

</aside>

给所有请求加上 `/api` 前缀，其余 URI 保持不变，再反向代理到应用：

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

将 API 请求的查询字符串替换为 `a=b`，并保持路径不变：

```caddy
example.com {
	rewrite ?a=b
}
```

只对 `/api/` 的请求保留原查询字符串并新增一个键值对：

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

同时改写路径和查询字符串，将原路径作为 `p` 参数保留：

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
