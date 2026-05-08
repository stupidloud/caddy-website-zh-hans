---
title: request_body (Caddyfile 指令)
---

<a id="request-body"></a>
# request_body

操作或設定對傳入請求主體（body）的限制。

<a id="syntax"></a>
## 語法

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** 是請求主體允許的最大位元組數。它支援 [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants) 支援的所有大小值。讀取超過此位元組數將回傳 HTTP 狀態碼 413 的錯誤。

⚠️ *實驗性功能* <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** 允許將請求主體設定為特定內容。內容可以包含 placeholder 以動態插入數據。

<a id="examples"></a>
## 範例

將請求主體大小限制為 10 MB：

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

使用包含 SQL 查詢的 JSON 結構設定請求主體：

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
