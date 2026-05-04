---
title: "错误（Caddyfile 指令）"
---

# 错误

在 HTTP 处理程序链中触发一个错误，并可选地附带一条消息和建议的 HTTP 状态码。 

该处理程序不会返回响应。相反，它旨在与[`handle_errors`](handle_errors)指令配合使用，以调用您的自定义错误处理逻辑。


## 语法

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** 是要写入的 HTTP 状态码。默认值为 `500`.
- **&lt;message&gt;** 是错误信息。默认情况下不显示错误信息。
- **message** 是提供错误消息的另一种方式；若错误消息包含多行，使用此方法会更方便。

需要说明的是，第一个非匹配参数可以是三位数的状态码，也可以是错误消息字符串。如果是错误消息，则下一个参数可以是状态码。


## 示例

在特定请求路径上触发错误，并使用[`handle_errors`](handle_errors)来编写响应：

```caddy
example.com {
	root /srv

	# 对特定路径触发错误
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # 通过返回 HTML 页面处理错误
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
