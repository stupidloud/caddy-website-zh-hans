---
title: "respond（Caddyfile 指令）"
---

# 回复

向客户端发送一个硬编码/静态响应。

如果正文不为空，则该指令会设置 `Content-Type` 标头（如果尚未设置）。默认值为 `text/plain; utf-8`，除非正文是一个有效的 JSON 对象或数组，在这种情况下，该字段将设置为 `application/json`。对于所有其他类型的内容，请使用[`header`指令](/docs/caddyfile/directives/header)显式设置正确的 `Content-Type`。


## 语法

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** 是要写入的 HTTP 状态码。

  如果 `103`（早期提示），响应将不包含正文，且处理程序链将继续执行。（HTTP `1xx` 响应属于信息性响应，而非最终响应。）
  
  默认： `200`

- **&lt;body&gt;** 是待写入的响应正文。

- **body** 是提供正文内容的另一种方式；如果正文内容有多行，这种方式会比较方便。

- **close** 将在写入响应后关闭客户端与服务器的连接。

需要说明的是，第一个非匹配器参数可以是 3 位数的状态码，也可以是响应正文字符串。如果是正文，则下一个参数可以是状态码。

<aside class="tip">

返回错误状态码与在处理程序链中抛出错误不同，后者会在内部调用错误处理程序。

</aside>


## 示例

对所有健康检查返回一个正文为空的 200 状态码，对其他所有请求返回一个简单的响应正文：

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

编写错误响应并关闭连接：

<aside class="tip">

您可能更倾向于使用[`error`指令](error)，该指令会触发一个错误，该错误可通过[`handle_errors`指令](handle_errors)进行处理。

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

编写一个 HTML 响应，使用 [heredoc 语法](/docs/caddyfile/concepts#heredocs)控制空格，并设置 `Content-Type` 响应头与响应主体相匹配：

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
