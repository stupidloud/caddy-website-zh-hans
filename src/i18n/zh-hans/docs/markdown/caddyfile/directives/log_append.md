---
title: "log_append（Caddyfile 指令）"
---

# log_append

在当前请求的访问日志中添加一个字段。

应与[`log`指令](log)配合使用，该指令是启用访问日志记录的首要条件。

该值可以是静态字符串，也可以是[占位符](/docs/caddyfile/concepts#placeholders)，该占位符将在请求时被替换为实际的值。


## 语法

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

默认情况下，日志字段是在沿中间件链回溯时（即“晚期”）添加的，此时所有后续处理程序均已完成（例如在[`reverse_proxy`](reverse_proxy)、[`respond`](respond)或[`file_server`](file_server)等会写入响应的处理程序之后），因此它能捕获请求和响应的最终状态。

如果 `<` 作为键的前缀，该键将被标记为“early”，这意味着日志字段将在调用链中的下一个处理程序之前被添加到日志中，因此可以在请求被后续处理程序修改之前读取该请求。

仅用于调试（不可用于生产环境），当值是以下占位符之一时，该处理程序会进行特殊处理： `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}`，或 `{http.response.body_base64}`。若使用请求正文占位符，则会隐式启用“早期”模式，并缓冲请求正文。若使用响应正文占位符，则会启用响应缓冲以捕获响应正文，并在响应写入时“延迟”将该字段添加到日志中。


## 示例

在日志中显示请求所来自的网站区域，即 `static` 或 `dynamic`:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

在日志中显示实际使用的反向代理上游（即 `node1`, `node2` 或 `node3`）以及
通过代理连接上游所花费的时间（以毫秒为单位），以及代理上游写入响应头所花费的时间：

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

通过在键名前添加 `<`。这允许你在后续处理程序修改请求之前捕获其状态。例如，要在请求路径被重写之前记录原始请求路径（尽管这是一个刻意设计的示例，因为原始请求路径无论如何都会被记录，但这有助于说明要点）：

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

为了调试目的，请将请求和响应正文添加到日志中（请勿在生产环境中使用，因为这会影响性能并导致日志信息冗余）。如果预计正文包含不可打印字符的二进制数据，您可以改用占位符的 base64 编码版本（例如 `{http.request.body_base64}` 和 `{http.response.body_base64}`），这样更便于复制和检查：

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
