---
title: request_body (Caddyfile directive)
---

# request_body

受信リクエストのボディを操作するか、制限を設定します。

<a id="syntax"></a>
## 構文

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** は、リクエストボディに許可する最大サイズをバイト単位で指定します。[go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants) がサポートするすべてのサイズ値を受け付けます。これを超えるバイト数を読み取ろうとすると、HTTP ステータス `413` のエラーが返されます。

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** は、リクエストボディを指定した内容に設定します。内容には placeholder を含めて、データを動的に挿入できます。

<a id="examples"></a>
## 例

リクエストボディのサイズを 10 メガバイトに制限します。

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

SQL クエリを含む JSON 構造でリクエストボディを設定します。

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
