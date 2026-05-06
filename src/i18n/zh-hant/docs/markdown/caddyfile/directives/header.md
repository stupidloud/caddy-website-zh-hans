---
title: header (Caddyfile directive)
---

<a id="header"></a>
# header

操作 HTTP 回應 header 欄位。它可以設定、新增、以及刪除 header 值，或是使用正規表達式執行取代。

預設情況下，header 操作會立即執行，除非正在刪除任何 header（使用 `-` 前綴）或設定預設值（使用 `?` 前綴）。在這些情況下，header 操作會自動延遲執行，直到將其寫入客戶端為止。

若要操作 HTTP 請求 header，您可以使用 [`request_header`](request_header) 指令。


<a id="syntax"></a>
## Syntax

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# 新增
	+<field> <value>

	# 設定
	<field> <value>

	# 設定並啟用 defer
	><field> <value>

	# 刪除
	-<field>

	# 取代
	<field> <find> <replace>

	# 取代並啟用 defer
	><field> <find> <replace>

	# 預設
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** 是 header 欄位的名稱。

  若無前綴，則欄位會被設定（覆寫）。

  前綴為 `+` 表示新增欄位，而非在欄位已存在時覆寫（設定）該欄位；header 欄位可以在回應中出現多次。

  前綴為 `-` 表示刪除該欄位。欄位可以使用前綴或後綴 `*` 萬用字元來刪除所有相符的欄位。

  前綴為 `?` 表示為該欄位設定預設值。僅在該欄位尚不存在時才會寫入。

  前綴為 `>` 表示設定該欄位並啟用 `defer` 的快捷方式。

- **&lt;value&gt;** 是新增或設定欄位時的 header 欄位值。

- **&lt;find&gt;** 是要搜尋的正規表達式。可以使用 placeholder 作為搜尋模式的動態輸入。所使用的正規表達式語言是 Go 內建的 RE2。請參閱 [RE2 語法參考](https://github.com/google/re2/wiki/Syntax) 以及 [Go 正規表達式語法總覽](https://pkg.go.dev/regexp/syntax)。

- **&lt;replace&gt;** 是取代值；若執行搜尋並取代則為必填。使用 `$1` 或 `$2` 等來參照搜尋模式中的擷取群組。如果取代值為 `""`，則相符的文字將從值中移除。詳情請參閱 [Go 文件](https://golang.org/pkg/regexp/#Regexp.Expand)。

- **defer** 會延遲執行 header 操作，直到將回應傳送給客戶端為止。在以下情況下會自動啟用此選項：
	- 當使用 `-` 刪除任何 header 欄位時。
	- 當使用 `?` 設定預設值時。
	- 當在設定或取代操作中使用 `>` 前綴時。
	- 當存在一個或多個 `match` 條件時。

- **match** <span id="match"/> 是一個內嵌的 [response matcher](/docs/caddyfile/response-matchers)。header 操作僅會套用到滿足指定條件的回應。

對於多個 header 操作，您可以開啟一個區塊，並以同樣的方式每行指定一個操作。

當使用 `?` 前綴來設定預設 header 值時，如果它位於具有多個 header 操作的 `header` 區塊中，它會自動被分離到自己的 `header` 處理器中。[在底層](/docs/modules/http.handlers.headers#response/require)，使用 `?` 會設定一個 [response matcher](/docs/caddyfile/response-matchers)，它套用到該指令的整個處理器，該處理器僅套用 header 操作（例如 `defer`），但僅在該欄位尚未設定時。


<a id="examples"></a>
## Examples

在所有回應上設定自定義 header 欄位：

```caddy-d
header Custom-Header "My value"
```

移除 "Hidden" header 欄位：

```caddy-d
header -Hidden
```

在任何 Location header 中將 `http://` 取代為 `https://`：

```caddy-d
header Location http:// https://
```

在所有頁面上設定安全性與隱私 header： (**警告：** 僅在您了解其影響時才使用！)

```caddy-d
header {
	# 停用 FLoC 追蹤
	Permissions-Policy interest-cohort=()

	# 啟用 HSTS
	Strict-Transport-Security max-age=31536000;

	# 禁止客戶端進行媒體類型探測 (sniffing)
	X-Content-Type-Options nosniff

	# 點擊劫持防護
	X-Frame-Options DENY
}
```

旨在互斥的多個 header 指令：

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

如果上游未定義，則設定預設快取過期時間：

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

將所有對 GET 請求的成功回應標記為最多可快取一小時：

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

防止在上游伺服器發生異常時快取錯誤回應：

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

如果上游伺服器支援客戶端提示 (client hints)，則將淺色模式回應與深色模式回應標記為分別快取：
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

透過將萬用字元值替換為特定網域來防止過於寬鬆的 CORS header：
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**注意**： 在取代操作中，`<find>` 值被解釋為正規表達式。若要比對 `*` 字元，必須像上述範例一樣使用反斜線進行跳脫。

或者，您可以使用 [response matcher](/docs/caddyfile/response-matchers) 來逐字比對 header 值：
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

若要覆寫代理上游為以 `/no-cache` 開頭的路徑所設定的快取過期時間；必須啟用 `defer` 以確保在代理寫入其 header *之後* 設定該 header：

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

執行延遲更新 `Set-Cookie` header 以新增 `SameSite=None`；使用正規表達式擷取來獲取現有值，而 `$1` 則將其重新插入到開頭，並附加額外選項：

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
