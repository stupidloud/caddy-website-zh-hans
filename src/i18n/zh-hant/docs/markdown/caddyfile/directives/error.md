---
title: error (Caddyfile 指令)
---

# error

在 HTTP handler 鏈中觸發錯誤，並提供可選的訊息和推薦的 HTTP 狀態碼。

此 handler 不會寫入回應。相反，它旨在與 [`handle_errors`](handle_errors) 指令配對使用，以調用您的自定義錯誤處理邏輯。


<a id="syntax"></a>
## 語法

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** 是要寫入的 HTTP 狀態碼。預設為 `500`。
- **&lt;message&gt;** 是錯誤訊息。預設沒有錯誤訊息。
- **message** 是提供錯誤訊息的另一種方式；如果訊息有多行，這會很方便。

具體來說，第一個非 matcher 參數可以是 3 位數的狀態碼，也可以是錯誤訊息字串。如果是錯誤訊息，則下一個參數可以是狀態碼。


<a id="examples"></a>
## 範例

在某些請求路徑上觸發錯誤，並使用 [`handle_errors`](handle_errors) 寫入回應：

```caddy
example.com {
	root /srv

	# 為特定路徑觸發錯誤
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # 藉由提供 HTML 頁面來處理錯誤
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
