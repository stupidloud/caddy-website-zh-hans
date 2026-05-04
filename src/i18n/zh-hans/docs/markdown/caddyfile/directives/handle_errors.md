---
title: "handle_errors（Caddyfile 指令）"
---

# 处理错误

设置错误处理程序。

当常规的 HTTP 请求处理程序返回错误时，常规处理将停止，并调用错误处理程序。错误处理程序构成了一条路由，其工作原理与常规路由完全相同，并且能够执行常规路由所能执行的所有操作。这使得在处理 HTTP 请求中的错误时，能够实现高度的控制和灵活性。例如，您可以提供静态错误页面、基于模板的错误页面，或者通过反向代理将错误处理任务转交给另一个后端。

该指令可以配合不同的状态码重复使用，以便针对不同错误采取不同的处理方式。如果未指定状态码，则该指令将匹配任何错误，并在其他错误处理程序均不匹配时作为备用方案。

请求上下文会被传递到错误路由中，因此请求上下文中设置的任何值（例如[站点根目录](root)或[变量](vars)）在错误处理程序中也会被保留。此外，在处理错误时还可以使用[新的占位符](#placeholders)。

请注意，某些指令（例如 [`reverse_proxy`](reverse_proxy)）虽然可能会返回被归类为错误的 HTTP 状态码，但不会触发错误路由。

您可以使用[`error`](error)指令，根据自己的路由决策显式触发错误。


<span id="syntax"/>
## 语法

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** 是要与正在处理的错误进行匹配的一个或多个 HTTP 状态码。这些状态码可以是 3 位数字，也可以是 `4xx` 或 `5xx` 的特例，分别匹配 400-499 或 500-599 范围内的所有状态码。如果未指定状态码，则会匹配任何错误，并在其他错误处理程序均不匹配时作为备用方案。

- **<directives...>** 是一组 HTTP 处理程序指令和[匹配器](/docs/caddyfile/matchers)，每行一个。


<a id="placeholders"></a>
<span id="placeholders"/>
## 占位符

在处理错误时，可以使用以下占位符。这些是 [Caddyfile](/docs/caddyfile/concepts#placeholders) 中对完整占位符的[简写形式](/docs/caddyfile/concepts#placeholders)，完整的占位符可在 [HTTP 服务器的错误路由 JSON 文档](/docs/json/apps/http/servers/errors/#routes)中找到。

| 占位符 | 描述 |
|---|---|
| `{err.status_code}` | 推荐的 HTTP 状态码 |
| `{err.status_text}` | 与推荐状态码关联的状态文本 |
| `{err.message}` | 错误信息 |
| `{err.trace}` | 错误的来源 |
| `{err.id}` | 此错误实例的标识符 |


<span id="examples"/>
## 示例

根据状态码设置自定义错误页面（例如，一个名为 `404.html` 用于 `404` ）。请注意，当在 `handle_errors` 时会保留错误的 HTTP 状态码（假设您已事先在站点中设置了[站点根目录](root)）：

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

一个使用 [`templates`](templates) 来写入自定义错误信息的错误页面：

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

如果您只想针对某些错误代码提供自定义错误页面，可以使用[`file`](/docs/caddyfile/matchers#file)匹配器预先检查自定义错误文件是否存在：

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

将请求转发至一台专业服务器，它不仅擅长处理 HTTP 错误，还能让你的每一天都更顺畅 😸：

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

只需使用 [`respond`](respond) 即可返回错误代码和名称

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

要对特定错误代码采取不同的处理方式：

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

上面的代码与下面的代码行为相同，后者使用[`expression`](/docs/caddyfile/matchers#expression)匹配器处理状态码，并使用[`handle`](handle)实现互斥：

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
