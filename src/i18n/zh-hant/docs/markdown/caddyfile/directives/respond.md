---
title: respond (Caddyfile 指令)
---

<a id="respond"></a>
# respond

向用戶端寫入硬編碼（hard-coded）或靜態的回應。

如果正文（body）非空，且尚未設置 `Content-Type` 標頭，則此指令會設置該標頭。除非正文是有效的 JSON 物件或陣列（此時會設置為 `application/json`），否則預設值為 `text/plain; utf-8`。對於所有其他類型的內容，請使用 [`header` 指令](/docs/caddyfile/directives/header) 顯式設置適當的 Content-Type。


<a id="syntax"></a>
## Syntax

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** 是要寫入的 HTTP 狀態碼。

  如果是 `103`（Early Hints），回應將不含正文且 handler chain 將會繼續執行。（HTTP `1xx` 回應是資訊性的，並非最終結果。）
  
  預設值：`200`

- **&lt;body&gt;** 是要寫入的回應正文。

- **body** 是提供正文的另一種方式；如果正文有多行，則此方式較為方便。

- **close** 將在寫入回應後關閉用戶端與伺服器的連線。

說明一下，第一個非 matcher 的參數可以是 3 位數的狀態碼或回應正文字串。如果它是正文，則下一個參數可以是狀態碼。

<aside class="tip">

使用錯誤狀態碼進行回應與在 handler chain 中回傳錯誤不同，後者會在內部調用錯誤處理程式（error handlers）。

</aside>


<a id="examples"></a>
## Examples

對所有健康檢查寫入帶有空正文的 200 狀態碼，並對所有其他請求寫入簡單的回應正文：

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

寫入錯誤回應並關閉連線：

<aside class="tip">

你可能更傾向於使用 [`error` 指令](error)，它會觸發一個可以使用 [`handle_errors` 指令](handle_errors) 處理的錯誤。

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

寫入 HTML 回應，使用 [heredoc 語法](/docs/caddyfile/concepts#heredocs) 控制空格，同時設置 `Content-Type` 標頭以匹配回應正文：

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
