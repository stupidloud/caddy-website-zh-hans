---
title: "重写（Caddyfile 指令）"
---

# 重写

在内部重写请求 URI。

重写会更改请求 URI 的部分或全部内容。请注意，URI 不包含协议或主机及端口信息，且客户端通常不会发送片段。因此，该指令主要用于对 **路径** 和 **查询** 字符串进行操作。

该 `rewrite` 该指令表示有意接受该请求，但需进行修改。

它与其他 `rewrite` 指令互斥，因此可以安全地定义那些原本会相互嵌套的重写规则，因为系统只会执行第一个匹配的重写规则。

一种[请求匹配器](/docs/caddyfile/matchers)，它会在 `rewrite` 可能无法匹配 `rewrite`之后可能无法匹配该请求。若希望您的 `rewrite` 与其他处理程序共享路由，请使用[`route`](route)或[`handle`](handle)指令。



## 语法

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** 是请求重写后的目标 URI。仅对重写规则中指定的 URI 组件（路径或查询字符串）进行处理。URI 路径是指位于 `?`之前出现的任何子字符串。如果 `?` 被省略，则整个令牌将被视为路径。

在 v2.8.0 之前， `<to>` 参数若以 `/`，因此必须指定一个通配符匹配器标记（`*`).



## 类似的指令

还有其他一些指令也能执行重写，但它们的意图不同，或者在重写时不会完全替换 URI：

- [`uri`](uri) 用于处理 URI（去除前缀、后缀或替换子字符串）。

- [`try_files`](try_files) 会根据文件的存在情况重写请求。




## 示例

将所有请求重写为 `index.html`，同时保持查询字符串不变：

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

请注意，在 v2.8.0 之前，此处必须使用[通配符匹配器](/docs/caddyfile/matchers#wildcard-matchers)，因为第一个参数与[路径匹配器](/docs/caddyfile/matchers#path-matchers)存在歧义，即 `rewrite * /foo`，但现在可以简化为 `rewrite /foo`.

</aside>

在所有请求前添加前缀 `/api`，保留 URI 的其余部分，然后通过反向代理转发至应用程序：

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

将 API 请求中的查询字符串替换为 `a=b`，同时保持路径不变：

```caddy
example.com {
	rewrite ?a=b
}
```

仅针对对 `/api/`，请保留现有的查询字符串并添加一个键值对：

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

同时修改路径和查询字符串，在保留原始查询字符串的同时，将原始路径作为 `p` 参数：

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
