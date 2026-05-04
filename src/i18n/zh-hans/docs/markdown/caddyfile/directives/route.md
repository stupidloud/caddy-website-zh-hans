---
title: "route（Caddyfile 指令）"
---

# route

按字面顺序将一组指令作为一个整体进行评估。

route 块中的指令不会在内部[重新排序](/docs/caddyfile/directives#directive-order)。只有 HTTP 处理程序指令，也就是会向处理链中添加处理程序或中间件的指令，才能在 route 块中使用。

这是一个特例，因为它的子指令本身也都是普通指令。



## 语法

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** 是一组指令或指令块，每行一个，和 route 块外部的写法相同；但这些指令不会被重新排序。只能使用 HTTP 处理程序指令。




## 用途

`route` 指令在某些高级用例或边缘情况下很有用，因为它能让你对 HTTP 处理链的部分区域拥有绝对控制权。

由于 HTTP 中间件的评估顺序很重要，Caddyfile 在解析后通常会重新排列指令，以便更易使用；因此你不必担心自己输入的顺序。

虽然[内置顺序](/docs/caddyfile/directives#directive-order)适用于大多数站点，但有时你需要手动控制顺序，可能是整个站点，也可能只是其中一部分。这正是 `route` 指令的用途。

举个例子，考虑两个终止处理程序：[`redir`](redir) 和 [`file_server`](file_server)。它们都会向客户端写入响应，并且不会调用链中的下一个处理程序，所以对于某个请求，这两者通常只会执行一个。那么哪个会先执行呢？通常，`redir` 会排在 `file_server` 前面，因为一般来说你只会在特定情况下重定向，而在其他情况下直接提供文件。

不过，在某些情况下，第一个指令（`file_server`）的匹配器比第二个（`redir`）更具体。换句话说，你希望在一般情况下重定向，只在特定情况下提供某个特定文件。

因此，你可能会写出下面这样的 Caddyfile（但这不会按预期工作！）：

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

问题在于，在[指令排序](/docs/caddyfile/directives#sorting-algorithm)之后，`redir` 会排在 `file_server` 前面。

但在这种情况下，`redir` 的匹配器是隐含的[`*`](/docs/caddyfile/matchers#wildcard-matchers)，而这个匹配器是 `file_server` 的匹配器（`*`）的超集。

幸运的是，解决方法很简单：只需把这两个指令包裹在一个 `route` 块中，就能确保 `file_server` 在 `redir` 之前执行：

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

另一种做法是让这两个匹配器互斥，但如果条件超过一两个，这种方法很快就会变得复杂。使用 `route` 指令时，因为这两个处理程序都是终止处理程序，所以它们的互斥性是隐含的。

</aside>

现在 `file_server` 会在 `redir` 之前进入处理链，因为这里的顺序是按字面顺序保留的。




## 类似指令

还有其他指令也可以包裹 HTTP 处理程序指令，但它们各自的用途不同，取决于你想表达的行为：

- [`handle`](handle) 的作用和 `route` 类似，但有两点区别：1) handle 块彼此互斥；2) handle 内的指令通常会被[重新排序](/docs/caddyfile/directives#directive-order)。

- [`handle_path`](handle_path) 的作用与 `handle` 相同，但它会在运行处理程序前从请求中去掉前缀。

- [`handle_errors`](handle_errors) 类似于 `handle`，但只会在 Caddy 处理请求时遇到错误时调用。




## 示例

将 `/api` 的请求原样代理出去，并把其他请求重写为磁盘上匹配的文件，否则重写为 `/index.html`。随后由该文件进行响应。

由于 [`try_files`](try_files) 的指令顺序高于 [`reverse_proxy`](reverse_proxy)，它通常会排得更靠前并先执行；这会导致所有 API 请求都被重写为 `/index.html`，从而无法匹配 `/api*`，于是这些请求不会被代理，反而会得到来自 [`file_server`](file_server) 的 `404`。把它们都包在 `route` 中，可以确保 `reverse_proxy` 总是在请求被重写之前先执行。

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

这并不是解决这个问题的唯一方法。你也可以使用一对[`handle`](handle)块，让第一个匹配 `/api*` 并指向 `reverse_proxy`，第二个作为回退来提供文件。请参阅这个[单页应用（SPA）示例](/docs/caddyfile/patterns#single-page-apps-spas)。

</aside>
