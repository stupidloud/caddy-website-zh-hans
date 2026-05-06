---
title: "route（Caddyfile 指令）"
---

# route

按字面顺序并作为一个整体执行一组指令。

`route` 块中的指令不会[被内部重排](/docs/caddyfile/directives#directive-order)。`route` 块中只能使用 HTTP 处理器指令（将处理器或中间件加入链路的指令）。

该指令是个特例，它的子指令也是常规指令。

<a id="syntax"></a>
## 语法

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **&lt;directives...&gt;** 是一组指令或指令块，每行一个，和 `route` 块外的写法一致；不同之处在于这些指令不会被重排。这里只能使用 HTTP 处理器指令。


<a id="utility"></a>
## 用法

在某些高级场景或边界场景下，`route` 指令可用于对 HTTP 处理链中的部分流程进行完全控制。

由于 HTTP 中间件求值顺序有意义，Caddyfile 通常会在解析后重排指令，以降低配置复杂度；你不必自己保证输入顺序。

虽然[内置顺序](/docs/caddyfile/directives#directive-order)能覆盖多数站点需求，但有时你需要手动掌控某一段或全部处理链的顺序。`route` 就是为此设计的。

举个例子，考虑两个会终止请求的处理器：[`redir`](redir) 与 [`file_server`](file_server)。两者都会向客户端写响应，并不会调用链上的下一个处理器，因此同一请求只能执行其中一个。那谁先执行？通常 `redir` 在 `file_server` 之前执行，因为你一般只想在特定场景重定向，而在一般场景提供文件服务。

但有时第一个指令（`file_server`）的匹配器可能比第二个指令（`redir`）更具体。换句话说，你可能想“默认重定向”，只在特定文件时才服务文件。

于是你可能会写成这样（但它不会按预期工作）：

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

问题在于[指令排序](/docs/caddyfile/directives#sorting-algorithm)之后，`redir` 会被放到 `file_server` 前面。

而在该场景下，`redir` 的匹配器（隐式的 [`*`](/docs/caddyfile/matchers#wildcard-matchers)）是 `file_server`（`/specific.html`）的超集。

解决方案很简单：把这两条指令包进 `route`，就能保证 `file_server` 在 `redir` 之前执行。

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

另一个办法是让两个匹配器互斥，但当条件超过一两个时，这通常会变得很复杂。使用 `route` 时，两个处理器的互斥性是隐含的，因为它们都是终止处理器。

</aside>

现在 `file_server` 会被明确按顺序挂在 `redir` 之前。


<a id="similar-directives"></a>
## 类似指令

还有其他指令也能包裹 HTTP 处理器指令，但具体使用哪个取决于你要表达的行为：

- [`handle`](handle) 与 `route` 一样用于包裹其他指令，但有两点区别：1）`handle` 块之间彼此互斥；2）`handle` 内部的指令仍会按[正常顺序重排](/docs/caddyfile/directives#directive-order)。

- [`handle_path`](handle_path) 与 `handle` 行为类似，但在执行其处理器前会先去掉请求路径前缀。

- [`handle_errors`](handle_errors) 与 `handle` 类似，但只在 Caddy 处理请求时出现错误时才被调用。


<a id="examples"></a>
## 示例

将 `/api` 的请求原样代理到后端，并将其他请求按是否命中磁盘文件重写到 `/index.html`。然后服务该文件。

因为 [`try_files`](try_files) 的指令顺序高于 [`reverse_proxy`](reverse_proxy)，所以通常它会被排在前面先执行；这会导致所有 API 请求都重写到 `/index.html`，从而无法匹配 `/api*`，于是没有请求会被代理，而是由 [`file_server`](file_server) 返回 `404`。
将它们包进 `route` 可确保 `reverse_proxy` 总是在重写发生前先执行。

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

这不是唯一解法。你也可以使用一对 [`handle`](handle) 块：第一个匹配 `/api*` 到 `reverse_proxy`，第二个作为回退提供文件服务。参考 SPA 示例：[这份示例](/docs/caddyfile/patterns#single-page-apps-spas)。

</aside>
