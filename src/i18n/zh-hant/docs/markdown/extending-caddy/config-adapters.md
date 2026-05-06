---
title: "編寫 Config Adapters"
---

<a id="writing-config-adapters"></a>
# 編寫 Config Adapters

出於各種原因，你可能希望使用非 [JSON](/docs/json/) 的格式來配置 Caddy。Caddy 通過 [config adapters](/docs/config-adapters) 對此提供了一流的支持。

如果你喜歡的語言/語法/格式尚不存在適配器，你可以自己編寫一個！

<a id="template"></a>
## 模板

這是一個你可以開始使用的模板：

```go
package myadapter

import (
	"fmt"

	"github.com/caddyserver/caddy/v2/caddyconfig"
)

func init() {
	caddyconfig.RegisterAdapter("adapter_name", MyAdapter{})
}

// MyAdapter adapts ____ to Caddy JSON.
type MyAdapter struct{
}

// Adapt adapts the body to Caddy JSON.
func (a MyAdapter) Adapt(body []byte, options map[string]interface{}) ([]byte, []caddyconfig.Warning, error) {
	// TODO: parse body and convert it to JSON
	return nil, nil, fmt.Errorf("not implemented")
}
```

- 參閱 [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter) 的 godoc
- 參閱 [`Adapter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter) 接口的 godoc

返回的 JSON **不應** 縮進；它應始終是緊湊的。如果調用者願意，他們可以隨時對其進行美化。

請注意，雖然 config adapters 是 Caddy *plugins*，但它們不是 Caddy *modules*，因為它們不會集成到配置的某一部分中（但為了方便起見，它們會顯示在 `list-modules` 中）。因此，它們沒有 `Provision()` 或 `Validate()` 方法，也不遵循其餘的 module 生命周期。它們只需要實現 `Adapter` 接口並註冊為適配器即可。

當填充配置中屬於 `json.RawMessage` 類型（即 module 字段）的字段時，請使用 `JSON()` 和 `JSONModuleObject()` 函數：

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) 用於序列化不嵌入 module 名稱的 module 值。（通常用於 module 名稱作為 map 鍵的 ModuleMap 字段。）
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) 用於序列化在對象中添加了 module 名稱的 module 值。（幾乎在其他所有地方都會用到。）


<a id="caddyfile-server-types"></a>
## Caddyfile Server Types

實現自定義 Caddyfile 格式也是可能的。Caddyfile 適配器是一個單一的適配器實現，其默認的「server type」是 HTTP，但它在註冊時支持備選的「server types」。例如，HTTP Caddyfile 是這樣註冊的：

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

你需要實現 [`caddyfile.ServerType` 接口](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) 並相應地註冊你自己的適配器。
