---
title: "编写配置适配器"
---

# 编写配置适配器

出于各种原因，您可能希望使用非 [JSON](/docs/json/) 格式的配置来配置 Caddy。Caddy 通过[配置适配器](/docs/config-adapters)对此提供了原生支持。

如果尚未有适用于您偏好的语言/语法/格式的版本，您可以自己编写一个！

## 模板

以下是一个可供参考的模板：

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

- 有关[`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)的详细信息，请参阅 godoc
- 请参阅 godoc 了解“Adapter”接口

返回的 JSON **不应**缩进；它应始终保持紧凑。调用方如需美化格式，随时可以自行处理。

请注意，虽然配置适配器是 Caddy 的 *插件*，但它们并非 Caddy 的 *模块*，因为它们不会集成到配置的某个部分中（但出于 `list-modules` ）。因此，它们不具备 `Provision()` 或 `Validate()` 方法，也不遵循模块生命周期的其余部分。它们只需实现 `Adapter` 接口，并作为适配器进行注册即可。

在填充配置文件中属于 `json.RawMessage` 类型（即模块字段）时，请使用 `JSON()` 和 `JSONModuleObject()` 函数：

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) 用于在不包含模块名称的情况下序列化模块值。（常用于 ModuleMap 字段，其中模块名称是映射键。）
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) 用于将模块值进行序列化，并在对象名称后附加模块名。（几乎在其他所有地方都使用该方法。）


## Caddyfile 服务器类型

还可以实现自定义的 Caddyfile 格式。Caddyfile 适配器是一个单一的适配器实现，其默认“服务器类型”为 HTTP，但在注册时支持其他“服务器类型”。例如，HTTP Caddyfile 的注册方式如下：

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

你需要实现[`caddyfile.ServerType`接口](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType)，并据此注册你自己的适配器。
