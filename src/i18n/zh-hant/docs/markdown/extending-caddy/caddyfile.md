---
title: "Caddyfile 支援"
---

<a id="caddyfile-support"></a>
# Caddyfile 支援

Caddy 模組在 [註冊](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) 時，會根據其命名空間自動添加到 [原生 JSON 配置](/docs/json/) 中，使其既可用又備有文件說明。這使得 Caddyfile 支援純粹是可選的，但偏好使用 Caddyfile 的使用者通常會要求提供此支援。

<a id="unmarshaler"></a>
## Unmarshaler

要為您的模組添加 Caddyfile 支援，只需實現 [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler) 介面。您可以透過解析權杖（token）的方式來選擇模組擁有的 Caddyfile 語法。

Unmarshaler 的工作只是設定模組的類型，例如透過使用傳遞給它的 [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) 來填寫其欄位。例如，名為 `Gizmo` 的模組類型可能具有此方法：

```go
// UnmarshalCaddyfile 實現了 caddyfile.Unmarshaler。語法：
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // 消耗指令名稱

	if !d.Args(&g.Name) {
		// 參數不足
		return d.ArgErr()
	}
	if d.NextArg() {
		// 可選參數
		g.Option = d.Val()
	}
	if d.NextArg() {
		// 參數過多
		return d.ArgErr()
	}

	return nil
}
```

在方法的 godoc 註釋中記錄語法是一個好主意。有關解析 Caddyfile 的更多資訊，請參閱 [`caddyfile` 套件的 godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc)。

指令名稱權杖可以透過簡單的 `d.Next()` 呼叫來消耗/跳過。

請務必使用 `d.NextArg()` 或 `d.RemainingArgs()` 檢查是否缺少或過多的參數。使用 `d.ArgErr()` 顯示簡單的「無效案例」訊息，或使用 `d.Errf("some message")` 製作一個有用的錯誤訊息，並解釋問題（理想情況下，還提供建議的解決方案）。

您還應該添加一個 [介面守衛（interface guard）](/docs/extending-caddy#interface-guards) 以確保介面被正確滿足：

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### 區塊（Blocks）

為了接受單行無法容納的更多配置，您可能希望允許帶有子指令的區塊。這可以使用 `d.NextBlock()` 並進行迭代，直到返回原始嵌套層級：

```go
for nesting := d.Nesting(); d.NextBlock(nesting); {
	switch d.Val() {
		case "sub_directive_1":
		// ...
		case "sub_directive_2":
		// ...
	}
}
```

只要迴圈的每次迭代都消耗了整個段落（行或區塊），這就是處理區塊的一種優雅方式。

<a id="http-directives"></a>
## HTTP 指令（Directives）

HTTP Caddyfile 是 Caddy 預設的 Caddyfile 轉接器語法（或稱「伺服器類型」）。它是可擴展的，這意味著您可以為您的模組 [註冊](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective) 您自己的「頂層」指令：

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

如果您的指令僅返回單個 HTTP handler（這是常見的情況），您可能會發現 [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) 更容易：

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

基本概念是您與指令關聯的 [解析函數](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) 會返回一個或多個 [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue) 值。（或者，如果使用 `RegisterHandlerDirective`，它只需直接返回填寫好的 `caddyhttp.MiddlewareHandler` 值。）每個配置值都與一個 [「類別（class）」](#classes) 相關聯，這有助於 HTTP Caddyfile 轉接器知道它可以用在最終 JSON 配置的哪些部分。所有配置值都會被堆放在一起，轉接器在構建最終 JSON 配置時會從中提取。

這種設計允許您的指令為任何公認的類別返回任何配置值，這意味著它可以影響 HTTP Caddyfile 轉接器具有指定類別的配置的任何部分。

如果您已經實現了 `UnmarshalCaddyfile()` 方法，那麼您的解析函數可以像下面這樣簡單：

```go
// parseCaddyfileHandler 將權杖從 h 反序列化為新的 middleware handler 值。
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

有關如何使用 `httpcaddyfile.Helper` 類型的更多資訊，請參閱 [`httpcaddyfile` 套件 godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc)。

<a id="handler-order"></a>
### Handler 順序

所有返回 HTTP middleware/handler 值的指令都需要以正確的順序執行。例如，設定網站根目錄的 handler 必須在存取根目錄的 handler 之前執行，以便它知道目錄路徑是什麼。

HTTP Caddyfile [對標準指令具有硬編碼的排序](/docs/caddyfile/directives#directive-order)。這確保了使用者不需要了解其網頁伺服器最常用功能的實現細節，並使他們更容易編寫正確的配置。鑑於 Caddyfile 的可擴展性，單個硬編碼列表還可以防止不確定性。

**當您註冊一個新的 handler 指令時，必須將其添加到該列表中才能使用（在 `route` 區塊之外）。** 這可以透過三種方法之一完成：

- （推薦）外掛作者可以在註冊指令後，在 `init()` 中呼叫 [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder)，以將指令插入到相對於另一個 [標準指令](/docs/caddyfile/directives#directive-order) 的順序中。這樣一來，使用者就可以直接在他們的網站中使用該指令，而無需額外的設定。例如，要將您的指令 `gizmo` 插入到 `header` handler 之後評估：

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- 使用者可以添加 [`order` 全域選項](/docs/caddyfile/options) 來修改其 Caddyfile 的標準順序。例如：`order gizmo before respond` 將插入一個新指令 `gizmo`，使其在 `respond` handler 之前評估。然後該指令就可以正常使用了。

- 使用者可以將指令放置在 [`route` 區塊](/docs/caddyfile/directives/route) 中。因為 route 區塊中的指令不會被重新排序，所以 route 區塊中使用的指令不需要出現在列表中。

如果您選擇後兩種選項之一，請為您的使用者提供一份關於您的指令在清單中應該排在什麼位置的建議，以便他們能夠正確地使用它。

<a id="classes"></a>
### 類別（Classes）

此表描述了 HTTP Caddyfile 轉接器所識別的具有導出類型的每個類別：

類別名稱 | 預期類型 | 描述
---------- | ------------- | -----------
bind | `[]string` | 伺服器監聽器綁定地址
route | `caddyhttp.Route` | HTTP handler route
error_route | `*caddyhttp.Subroute` | HTTP 錯誤處理 route
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS 連線策略
tls.cert_issuer | `certmagic.Issuer` | TLS 憑證發行者
tls.cert_loader | `caddytls.CertificateLoader` | TLS 憑證載入器

<a id="server-types"></a>
## 伺服器類型（Server Types）

從結構上講，Caddyfile 是一種簡單的格式，因此可以有不同類型的 Caddyfile 格式（有時稱為「伺服器類型」）以適應不同的需求。

預設的 Caddyfile 格式是 HTTP Caddyfile，您可能對此很熟悉。此格式主要配置 [`http` 應用程式](/docs/modules/http)，同時僅可能在 Caddy 配置結構的其他部分散佈一些配置（例如用於載入和自動化憑證的 `tls` 應用程式）。

要配置 HTTP 以外的應用程式，您可能需要實現自己的配置轉接器，該轉接器使用 [您自己的伺服器類型](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter)。Caddyfile 轉接器實際上會為您解析輸入並提供伺服器區塊和選項列表，由您的轉接器來理解該結構並將其轉換為 JSON 配置。
