---
title: "request_body（Caddyfile 指令）"
---

# request_body

对传入请求的实体进行操作或设置限制。

## 语法

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** 是请求正文允许的最大字节数。它支持 [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants) 支持的所有大小值。若读取的字节数超过此限制，将返回带有 HTTP 状态码的错误 `413`.

⚠️ *实验版* <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** 允许将请求正文设置为特定内容。该内容可以包含占位符，以便动态插入数据。

## 示例

将请求正文大小限制为 10 兆字节：

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

将请求正文设置为包含 SQL 查询的 JSON 结构：

```caddy
example.com {
	handle /jazz {
		request_body {
			set `\{"statementText":"SELECT name, genre, debut_year FROM artists WHERE genre = 'Jazz'"}`
		}

		reverse_proxy localhost:8080 {
			header_up Content-Type application/json
			method POST
			rewrite /execute-sql
		}
	}
}
```
