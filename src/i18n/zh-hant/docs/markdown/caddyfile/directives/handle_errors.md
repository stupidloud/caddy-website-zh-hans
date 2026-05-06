---
title: handle_errors (Caddyfile 指令)
---

<a id="handle-errors"></a>
# handle_errors

设置错误处理程序。

当正常的 HTTP 请求 handler 返回错误时，正常处理将停止并调用错误处理程序。错误处理程序形成一个 route，就像正常的 routes 一样，它们可以执行正常 routes 可以执行的任何操作。这在处理 HTTP 请求期间的错误时提供了极大的控制和灵活性。例如，你可以提供静态错误页面、模板化错误页面，或者使用 reverse_proxy 到另一个后端来处理错误。

该指令可以针对不同的状态码重复多次，以不同方式处理不同的错误。如果没有指定状态码，它将匹配任何错误，作为其他错误处理程序不匹配时的回退方案。

请求的 context 会被带入错误 routes 中，因此在请求 context 上设置的任何值（如 [site root](root) 或 [vars](vars)）也将保留在错误处理程序中。此外，在处理错误时可以使用 [新 placeholders](#placeholders)。

请注意，某些指令（例如 [`reverse_proxy`](reverse_proxy)）可能会写入被归类为错误的 HTTP 状态响应，但这 *不会* 触发错误 routes。

你可以使用 [`error`](error) 指令根据自己的路由决策显式触发错误。


<a id="syntax"></a>
## 语法

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** 是一个或多个用于匹配正在处理的错误的 HTTP 状态码。状态码可以是 3 位数字，或者是 `4xx` 或 `5xx` 这种特殊情况，分别匹配 400-499 或 500-599 范围内的所有状态码。如果没有指定状态码，它将匹配任何错误，作为其他错误处理程序不匹配时的回退方案。

- **<directives...>** 是 HTTP handler [指令](/docs/caddyfile/directives) 和 [matchers](/docs/caddyfile/matchers) 的列表，每行一个。


<a id="placeholders"></a>
## Placeholders

以下 placeholders 在处理错误时可用。它们是完整 placeholders 的 [Caddyfile 简写](/docs/caddyfile/concepts#placeholders)，完整版可以在 [HTTP server 错误 routes 的 JSON 文档](/docs/json/apps/http/servers/errors/#routes) 中找到。

| Placeholder | 描述 |
|---|---|
| `{err.status_code}` | 建议的 HTTP 状态码 |
| `{err.status_text}` | 与建议的状态码关联的状态文本 |
| `{err.message}` | 错误消息 |
| `{err.trace}` | 错误来源 |
| `{err.id}` | 此错误发生情况的标识符 |


<a id="examples"></a>
## 示例

根据状态码自定义错误页面（例如，针对 `404` 错误调用名为 `404.html` 的页面）。请注意，[`file_server`](file_server) 在 `handle_errors` 中运行时会保留错误的 HTTP 状态码（假设你预先在站点中设置了 [site root](root)）：

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

使用 [`templates`](templates) 写入自定义错误消息的单个错误页面：

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

如果你只想为某些错误代码提供自定义错误页面，可以预先使用 [`file`](/docs/caddyfile/matchers#file) matcher 检查自定义错误文件是否存在：

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

使用 reverse_proxy 到一个非常专业且非常有资格处理 HTTP 错误并改善你心情的服务器 😸：

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

简单地使用 [`respond`](respond) 返回错误代码和名称：

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

以不同方式处理特定的错误代码：

```caddy-d
handle_errors 404 410 {
	respond "It's a 404 or 410 error!"
}

handle_errors 5xx {
	respond "It's a 5xx error."
}

handle_errors {
	respond "It's another error"
}
```

上面的行为与下面相同，下面使用 [`expression`](/docs/caddyfile/matchers#expression) matcher 针对状态码进行匹配，并使用 [`handle`](handle) 实现互斥：

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "It's a 404 or 410 error!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "It's a 5xx error."
	}

	handle {
		respond "It's another error"
	}
}
```
