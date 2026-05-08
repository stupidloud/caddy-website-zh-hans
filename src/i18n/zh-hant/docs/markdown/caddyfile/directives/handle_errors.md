---
title: handle_errors (Caddyfile 指令)
---

<a id="handle-errors"></a>
# handle_errors

設定錯誤處理程式。

當正常的 HTTP 請求 handler 傳回錯誤時，正常處理將停止並呼叫錯誤處理程式。錯誤處理程式形成一個 route，就像正常的 routes 一樣，它們可以執行正常 routes 可以執行的任何操作。這在處理 HTTP 請求期間的錯誤時，提供了極大的控制與彈性。例如，你可以提供靜態錯誤頁面、樣板化錯誤頁面，或使用 reverse_proxy 到另一個後端來處理錯誤。

該指令可以針對不同的狀態碼重複多次，以不同方式處理不同的錯誤。如果沒有指定狀態碼，它將匹配任何錯誤，作為其他錯誤處理程式不匹配時的回退方案。

請求的 context 會被帶入錯誤 routes 中，因此在請求 context 上設定的任何值（如 [site root](root) 或 [vars](vars)）也將保留在錯誤處理程式中。此外，在處理錯誤時可以使用 [新 placeholders](#placeholders)。

請注意，某些指令（例如 [`reverse_proxy`](reverse_proxy)）可能會寫入被歸類為錯誤的 HTTP 狀態回應，但這 *不會* 觸發錯誤 routes。

你可以使用 [`error`](error) 指令根據自己的路由決策明確觸發錯誤。


<a id="syntax"></a>
## 語法

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** 是一個或多個用於比對正在處理的錯誤的 HTTP 狀態碼。狀態碼可以是 3 位數字，或者是 `4xx` 或 `5xx` 這種特殊情況，分別比對 400-499 或 500-599 範圍內的所有狀態碼。如果沒有指定狀態碼，它將匹配任何錯誤，作為其他錯誤處理程式不匹配時的回退方案。

- **<directives...>** 是 HTTP handler [指令](/docs/caddyfile/directives) 和 [matchers](/docs/caddyfile/matchers) 的列表，每行一個。


<a id="placeholders"></a>
## Placeholders

以下 placeholders 在處理錯誤時可用。它們是完整 placeholders 的 [Caddyfile 簡寫](/docs/caddyfile/concepts#placeholders)，完整版可以在 [HTTP 伺服器錯誤 routes 的 JSON 文件](/docs/json/apps/http/servers/errors/#routes) 中找到。

| Placeholder | 描述 |
|---|---|
| `{err.status_code}` | 建議的 HTTP 狀態碼 |
| `{err.status_text}` | 與建議的狀態碼關聯的狀態文字 |
| `{err.message}` | 錯誤訊息 |
| `{err.trace}` | 錯誤來源 |
| `{err.id}` | 此錯誤發生情況的識別符 |


<a id="examples"></a>
## 示例

根據狀態碼自訂錯誤頁面（例如，針對 `404` 錯誤呼叫名為 `404.html` 的頁面）。請注意，[`file_server`](file_server) 在 `handle_errors` 中運行時會保留錯誤的 HTTP 狀態碼（假設你預先在站點中設定了 [site root](root)）：

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

使用 [`templates`](templates) 寫入自訂錯誤訊息的單一錯誤頁面：

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

如果你只想為某些錯誤代碼提供自訂錯誤頁面，可以預先使用 [`file`](/docs/caddyfile/matchers#file) matcher 檢查自訂錯誤檔案是否存在：

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

使用 reverse_proxy 到一個非常專業且非常有資格處理 HTTP 錯誤並改善你心情的伺服器 😸：

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

簡單地使用 [`respond`](respond) 回傳錯誤代碼和名稱：

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

以不同方式處理特定的錯誤代碼：

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

上面的行為與下面相同，下面使用 [`expression`](/docs/caddyfile/matchers#expression) matcher 針對狀態碼進行比對，並使用 [`handle`](handle) 實現互斥：

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
