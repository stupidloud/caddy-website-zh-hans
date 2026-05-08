---
title: log_append (Caddyfile 指令)
---

<a id="log_append"></a>
# log_append

為當前請求的 access log 追加一個欄位。

這應該與 [`log` 指令](log) 一起使用，因為首先需要該指令來啟用 access logging。

值可以是一個靜態字串，或者是一個 [placeholder](/docs/caddyfile/concepts#placeholders)，它將在請求時被替換為 placeholder 的值。


<a id="syntax"></a>
## Syntax

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

預設情況下，log 欄位是在中間件鏈回傳時（即「晚期」）添加的，是在所有後續處理程序完成之後（例如像 [`reverse_proxy`](reverse_proxy)、[`respond`](respond) 或 [`file_server`](file_server) 這些寫入響應的處理程序），因此它捕捉了請求和響應的最終狀態。

如果使用 `<` 作為 key 的前綴，它被標記為「早期」，這意味著 log 欄位將在調用鏈中的下一個處理程序 *之前* 被添加到日誌中，因此可以在請求被後續處理程序修改之前讀取它。

僅出於調試目的（不用於生產環境），當值為以下 placeholder 之一時，處理程序具有專門的處理：`{http.request.body}`、`{http.request.body_base64}`、`{http.response.body}` 或 `{http.response.body_base64}`。如果使用請求體 placeholder，則隱式啟用「早期」模式，並且請求體將被緩衝。如果使用響應體 placeholder，則啟用響應緩衝以捕獲響應體，並在寫入響應時「晚期」將該欄位添加到日誌中。


<a id="examples"></a>
## Examples

在日誌中顯示請求所服務的網站區域，即 `static` 或 `dynamic`：

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

在日誌中顯示實際使用了哪個 reverse proxy 上游（或是 node1、node2 或 node3），以及代理到上游所花費的時間（以毫秒為單位），以及代理上游寫入響應標頭所花費的時間：

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

通過在 key 前綴加上 `<`，可以將欄位「早期」添加到日誌中。這允許你在請求被後續處理程序修改之前捕捉其狀態。例如，在日誌中記錄原始請求路徑在被重寫之前（雖然這是一個人為設計的例子，因為原始請求路徑無論如何都會被記錄，但這有助於說明這一點）：

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

出於調試目的，將請求體和響應體添加到日誌中（不用於生產環境，因為這會損害效能並使日誌變得非常雜亂）。如果你預期正文是帶有不可列印字元的二進位數據，則可以使用 placeholder 的 base64 變體（例如 `{http.request.body_base64}` 和 `{http.response.body_base64}`），這將更容易複製和檢查：

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
