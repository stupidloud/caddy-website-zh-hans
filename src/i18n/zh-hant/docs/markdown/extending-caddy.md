---
title: "擴充 Caddy"
---

<a id="extending-caddy"></a>
# 擴充 Caddy

由於其模組化架構，Caddy 非常容易擴充。大多數種類的 Caddy 擴充功能（或插件）如果擴充或插入到 Caddy 的配置結構中，則被稱為 *modules*。需要明確的是，Caddy modules 與 [Go modules](https://github.com/golang/go/wiki/Modules) 是不同的（但它們也是 Go modules）。

**先決條件：**
- 對 [Caddy 的架構](/docs/architecture) 有基本了解
- 精通 Go 語言
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Quick Start

Caddy module 是指任何在導入其套件時將自身註冊為 Caddy module 的具名類型。至關重要的是，module 始終實現 [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module) 接口，該接口提供其 ID 和一個構造函數。

在一個新的 Go module 中，將以下模板貼到 Go 文件中，並自定義您的套件名稱、類型名稱和 Caddy module ID：

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo 是個範例；在此處放置您自己的類型。
type Gizmo struct {
}

// CaddyModule 回傳 Caddy module 資訊。
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

然後在專案目錄下執行此命令，您應該會在列表中看到您的 module：

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

[`xcaddy` 命令](https://github.com/caddyserver/xcaddy) 是每個 module 開發者工作流程的重要組成部分。它使用您的插件編譯 Caddy，然後使用給定的參數運行它。它每次都會丟棄臨時二進制文件（類似於 `go run`）。

</aside>


恭喜，您的 module 已在 Caddy 註冊，並可以在 [Caddy 的 config document](/docs/json/) 中任何使用相同 namespace 的 module 的地方使用。

在底層，`xcaddy` 只是創建一個同時需要 Caddy 和您的插件的新 Go module（使用適當的 `replace` 來使用您的本地開發版本），然後添加一個導入以確保它被編譯進去：

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Module Basics

Caddy modules：

1. 實現 `caddy.Module` 接口以提供 ID 和構造函數
2. 在適當的 namespace 中具有唯一的名稱
3. 通常滿足對該 namespace 的 host module 有意義的某些接口

**Host modules**（或 *parent modules*）是載入/初始化其他 module 的 module。它們通常為 guest modules 定義 namespaces。

**Guest modules**（或 *child modules*）是被載入或初始化的 module。所有 modules 都是 guest modules。


<a id="module-ids"></a>
## Module IDs

每個 Caddy module 都有一個唯一的 ID，由 namespace 和名稱組成：

- 一個完整的 ID 看起來像 `foo.bar.module_name`
- namespace 將是 `foo.bar`
- 名稱將是 `module_name`，它在其 namespace 中必須是唯一的

Module IDs 必須使用 `snake_case` 慣例。

<a id="namespaces"></a>
### Namespaces

Namespaces 就像類別，即一個 namespace 定義了其內部所有 modules 共有的某些功能。例如，我們可以預期 `http.handlers` namespace 中的所有 modules 都是 HTTP handlers。因此，host module 可以將該 namespace 中的 guest modules 從 `interface{}` 類型類型斷言為更具體、更有用的類型，例如 `caddyhttp.MiddlewareHandler`。

guest module 必須正確設定 namespace，以便被 host module 識別，因為 host module 會向 Caddy 請求特定 namespace 內的 modules，以提供 host module 所需的功能。例如，如果您要編寫一個名為 `gizmo` 的 HTTP handler module，您的 module 名稱將是 `http.handlers.gizmo`，因為 `http` app 會在 `http.handlers` namespace 中尋找 handlers。

換句話說，Caddy modules 預期根據其 module namespace 實現 [特定的接口](/docs/extending-caddy/namespaces)。有了這個慣例，module 開發者可以說出直觀的話，例如「`http.handlers` namespace 中的所有 modules 都是 HTTP handlers」。更技術性地說，這通常意味著「`http.handlers` namespace 中的所有 modules 都實現了 `caddyhttp.MiddlewareHandler` 接口」。因為該方法集是已知的，所以可以斷言並使用更具體的類型。

**[查看將所有標準 Caddy namespaces 映射到其 Go 類型的表格。](/docs/extending-caddy/namespaces)**

`caddy` 和 `admin` namespaces 是保留的，不能作為 app 名稱。

要編寫插入第三方 host modules 的 modules，請諮詢這些 modules 的 namespace 文檔。

<a id="names"></a>
### Names

namespace 內的名稱具有重要意義且對使用者高度可見，但只要它唯一、簡潔且對其功能有意義，就並非特別重要。


<a id="app-modules"></a>
## App Modules

Apps 是具有空 namespace 的 modules，依照慣例，它們會成為自己的頂層 namespace。App modules 實現了 [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App) 接口。

這些 modules 出現在 Caddy 配置頂層的 [`"apps"`](/docs/json/#apps) 屬性中：

```json
{
	"apps": {}
}
```

範例 [apps](/docs/json/apps/) 是 `http` 和 `tls`。它們使用的是空 namespace。

為這些 apps 編寫的 guest modules 應該位於從 app 名稱派生的 namespace 中。例如，HTTP handlers 使用 `http.handlers` namespace，而 TLS certificate loaders 使用 `tls.certificates` namespace。

<a id="module-implementation"></a>
## Module Implementation

module 幾乎可以是任何類型，但 struct 最常見，因為它們可以保存使用者配置。


<a id="configuration"></a>
### Configuration

大多數 modules 需要一些配置。只要您的類型與 JSON 兼容，Caddy 就會自動處理此問題。因此，如果 module 是一個 struct 類型，它的欄位將需要 struct tags，根據 Caddy 慣例，這些標籤應使用 `snake_casing`：

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

在 struct tag 中使用 `omitempty` 選項將在欄位為其類型的零值時從 JSON 輸出中省略該欄位。這在編組時（例如從 Caddyfile 適配到 JSON）有助於保持 JSON 配置的整潔和簡潔。

當一個 module 初始化時，它的配置已經被填寫好了。在 module 初始化之後，也可以執行額外的 [provisioning](#provisioning) 和 [validation](#validating) 步驟。


<a id="module-lifecycle"></a>
### Module Lifecycle

module 的生命始於它被 host module 載入時。會發生以下情況：

1. 調用 [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) 以獲取 module 值的實例。
2. module 的配置被反編組到該實例中。
3. 如果 module 是一個 [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner)，則調用 `Provision()` 方法。
4. 如果 module 是一個 [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator)，則調用 `Validate()` 方法。
5. 此時，host module 會收到作為 `interface{}` 值的已載入 guest module，因此 host module 通常會將 guest module 類型斷言為更有用的類型。查看 host module 的文檔以了解其 namespace 對 guest module 的要求，例如需要實現哪些方法。
6. 當不再需要一個 module 時，如果它是一個 [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper)，則調用 `Cleanup()` 方法。

請注意，您的 module 的多個載入實例可能會在特定時間重疊！在配置更改期間，新的 modules 會在舊的 modules 停止之前啟動。請務必小心使用全局狀態。使用 [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) 類型來幫助管理跨 module 載入的全局狀態。如果您的 module 在 socket 上監聽，請使用 `caddy.Listen*()` 來獲取一個支持重疊使用的 socket。

<a id="provisioning"></a>
### Provisioning

module 的配置將自動反編組到其值中（在載入 JSON 配置時）。這意味著，例如，struct 欄位將為您填寫。

但是，如果您的 module 需要額外的配置步驟，您可以實現（可選的）[`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) 接口：

```go
// Provision 設置 module。
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: 設置 module
	return nil
}
```

這是您應該為使用者未提供的欄位（不是其零值的欄位）設置默認值的地方。如果一個欄位是必填的，如果未設置，您可以回傳錯誤。對於零值具有含義的數字欄位（例如某些逾時持續時間），您可能希望支持 `-1` 表示「關閉」而不是 `0`，因此如果使用者未配置，您可以設置默認值。

這通常也是 host modules 載入其 guest/child modules 的地方。

module 可以通過調用 `ctx.App()` 訪問其他 apps，但 modules 之間不能有循環依賴。換句話說，如果 `tls` app 載入的 module 依賴於 `http` app，則 `http` app 載入的 module 不能依賴於 `tls` app。（與 Go 中禁止循環導入的規則非常相似。）

此外，您應該避免在 `Provision` 中執行昂貴的操作，因為即使僅僅是驗證配置，也會執行 provisioning。在 provisioning 階段，不要指望 module 真的會被使用。

<a id="logs"></a>
#### Logs

查看 Caddy 中的 [logging 如何運作](/docs/logging)。如果您的 module 需要 logging，請不要使用 Go 標準庫中的 `log.Print*()`。換句話說，**不要使用 Go 的全局 logger**。Caddy 使用 [zap](https://github.com/uber-go/zap) 進行高性能、高度靈備、結構化的 logging。

要發送 logs，請在 module 的 Provision 方法中獲取一個 logger：

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger 是一個 *zap.Logger
}
```

然後您可以使用 `g.logger` 發送結構化、帶級別的 logs。有關詳細資訊，請參閱 [zap 的 godoc](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger)。


<a id="validating"></a>
### Validating

想要驗證其配置的 modules 可以通過滿足（可選的）[`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) 接口來實現：

```go
// Validate 驗證 module 是否具有可用的配置。
func (g Gizmo) Validate() error {
	// TODO: 驗證 module 的設置
	return nil
}
```

Validate 應該是一個唯讀函數。它在 `Provision()` 方法之後執行。


<a id="interface-guards"></a>
### Interface guards

Caddy module 行為是隱式的，因為 Go 接口是隱式滿足的。只需將正確的方法添加到您的 module 類型中，就可以決定 module 的正確性。因此，拼寫錯誤或方法簽名錯誤可能會導致意外的（缺乏）行為。

幸運的是，您可以向代碼中添加一個簡單、無開銷的編譯時檢查，以確保您添加了正確的方法。這些被稱為 interface guards：

```go
var _ InterfaceName = (*YourType)(nil)
```

將 `InterfaceName` 替換為您打算滿足的接口，將 `YourType` 替換為您 module 類型的名稱。

例如，像靜態文件伺服器這樣的 HTTP handler 可能會滿足多個接口：

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

如果 `*FileServer` 不滿足這些接口，這將阻止程序編譯。

如果沒有 interface guards，可能會混入令人困惑的 bugs。例如，如果您的 module 在使用前必須進行自我配置，但您的 `Provision()` 方法有錯誤（例如拼寫錯誤或簽名錯誤），則 provisioning 永遠不會發生，從而導致令人費解的問題。Interface guards 非常容易且可以防止這種情況。它們通常放在文件的底部。


<a id="host-modules"></a>
## Host Modules

當一個 module 載入自己的 guest modules 時，它就變成了 host module。如果 module 的某部分功能可以以不同的方式實現，這很有用。

host module 幾乎總是一個 struct。通常，支持 guest module 需要兩個 struct 欄位：一個用於保存其原始 JSON，另一個用於保存其解碼後的值：

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

第一個欄位（在本例中為 `GadgetRaw`）是 guest module 的原始、未 provision 的 JSON 形式所在之處。

第二個欄位（`Gadget`）是最終 provision 的值最終存儲的地方。由於第二個欄位不面向使用者，我們使用 struct tag 將其從 JSON 中排除。（如果其他套件不需要它，您也可以不導出它，這樣就不需要 struct tag。）

<a id="caddy-struct-tags"></a>
### Caddy struct tags

原始 module 欄位上的 `caddy` struct tag 有助於 Caddy 知道要載入的 module 的 namespace 和名稱（組成完整的 ID）。它也用於生成文檔。

struct tag 的格式非常簡單：`key1=val1 key2=val2 ...`

對於 module 欄位，struct tag 看起來像：

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

`namespace=` 部分是必填的。它定義了尋找 module 的 namespace。

`inline_key=` 部分僅在 module 名稱與 module 本身 *inline* 發現時使用；這意味著值是一個對象，其中一個鍵是 *inline key*，其值是 module 的名稱。如果省略，則欄位類型必須是 [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) 或 `[]caddy.ModuleMap`，其中 map key 是 module 名稱。


<a id="loading-guest-modules"></a>
### Loading guest modules

要載入 guest module，請在 provision 階段調用 [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule)：

```go
// Provision 設置 g 並載入其 gadget。
func (g *Gizmo) Provision(ctx caddy.Context) error {
	if g.GadgetRaw != nil {
		val, err := ctx.LoadModule(g, "GadgetRaw")
		if err != nil {
			return fmt.Errorf("loading gadget module: %v", err)
		}
		g.Gadget = val.(Gadgeter)
	}
	return nil
}
```

請注意，`LoadModule()` 調用接受指向 struct 的指針和作為字串的欄位名稱。很奇怪，對吧？為什麼不直接傳遞 struct 欄位呢？這是因為根據配置的佈局，有幾種不同的載入 module 的方式。此方法簽名允許 Caddy 使用反射來找出載入 module 的最佳方式，最重要的是，讀取其 struct tags。

如果 guest module 必須由使用者顯式設置，則在嘗試載入它之前，如果 Raw 欄位為 nil 或為空，您應該回傳錯誤。

注意載入的 module 是如何進行類型斷言的：`g.Gadget = val.(Gadgeter)` —— 這是因為回傳的 `val` 是一個 `interface{}` 類型，它並非特別有用。但是，我們預期聲明的 namespace 中的所有 modules（本例中為來自 struct tag 的 `foo.gizmo.gadgets`）都實現了 `Gadgeter` 接口，因此此類型斷言是安全的，然後我們就可以使用它了！

如果您的 host module 定義了一個新的 namespace，請務必為開發者記錄該 namespace 及其 Go 類型，[就像我們在這裡所做的那樣](/docs/extending-caddy/namespaces)。

<a id="module-documentation"></a>
## Module Documentation

註冊 module 以使新的 Caddy module 出現在 module 文檔中，並在 http://caddyserver.com/download 中可用。註冊可在 http://caddyserver.com/account 進行。如果您還沒有帳戶，請創建一個新帳戶並點擊「Register package」。

<a id="complete-example"></a>
## Complete Example

假設我們想編寫一個 HTTP handler module。這將是一個用於演示目的的人造中間件，它將訪問者的 IP 地址打印到每個 HTTP 請求的流中。

我們還希望它能透過 Caddyfile 進行配置，因為大多數人更喜歡在非自動化情況下使用 Caddyfile。我們通過註冊一個 Caddyfile handler 指令來實現這一點，這是一種可以將 handler 添加到 HTTP route 的指令。我們還實現了 `caddyfile.Unmarshaler` 接口。通過添加這幾行代碼，可以使用 Caddyfile 配置此 module！例如：`visitor_ip stdout`。

這是此類 module 的代碼，附有說明性註釋：

```go
package visitorip

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/caddyserver/caddy/v2"
	"github.com/caddyserver/caddy/v2/caddyconfig/caddyfile"
	"github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile"
	"github.com/caddyserver/caddy/v2/modules/caddyhttp"
)

func init() {
	caddy.RegisterModule(Middleware{})
	httpcaddyfile.RegisterHandlerDirective("visitor_ip", parseCaddyfile)
}

// Middleware 實現了一個將訪問者的 IP 地址寫入文件或流的 HTTP handler。
type Middleware struct {
	// 要寫入的文件或流。可以是 "stdout" 或 "stderr"。
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule 回傳 Caddy module 資訊。
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision 實現 caddy.Provisioner。
func (m *Middleware) Provision(ctx caddy.Context) error {
	switch m.Output {
	case "stdout":
		m.w = os.Stdout
	case "stderr":
		m.w = os.Stderr
	default:
		return fmt.Errorf("an output stream is required")
	}
	return nil
}

// Validate 實現 caddy.Validator。
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP 實現 caddyhttp.MiddlewareHandler。
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile 實現 caddyfile.Unmarshaler。
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // 消耗指令名稱

	// 需要一個參數
	if !d.NextArg() {
		return d.ArgErr()
	}

	// 存儲參數
	m.Output = d.Val()
	return nil
}

// parseCaddyfile 將 h 中的 token 反編組為新的 Middleware。
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Interface guards
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
