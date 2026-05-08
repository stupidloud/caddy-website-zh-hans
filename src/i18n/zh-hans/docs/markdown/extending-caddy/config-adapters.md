---
title: "编写配置适配器"
---

# 编写配置适配器

出于各种原因，您可能希望用非 [JSON](/docs/json/) 格式来配置 Caddy。Caddy 通过[配置适配器](/docs/config-adapters)对这种场景提供了一等支持。

如果您偏好的语言/语法/格式还没有现成适配器，也可以自己编写一个。

<a id="template"></a>
## 模板

以下是可直接开始使用的模板：

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

- 查看 [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter) 的 godoc
- 查看 [`Adapter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter) 接口的 godoc

返回的 JSON **不应**缩进；应始终保持紧凑。调用方如有需要，可在之后再将其美化。

请注意，配置适配器虽然是 Caddy 的 *插件*，但不是 Caddy 的 *模块*，因为它们不会接入配置树中的某个模块（但会为了便利出现在 `list-modules`）。因此，它们没有 `Provision()` 或 `Validate()` 方法，也不遵循模块生命周期的其他阶段。它们只需实现 `Adapter` 接口并注册为适配器即可。

在处理配置里类型为 `json.RawMessage` 的字段（也就是模块字段）时，请使用 `JSON()` 和 `JSONModuleObject()` 函数：

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) 用于在不包含模块名称的情况下序列化模块值。（常用于 ModuleMap 字段，其中模块名称是映射键。）
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) 用于在对象中序列化模块值并附带模块名称。（几乎在其他场景都会使用该方法。）


<a id="caddyfile-server-types"></a>
## Caddyfile 服务器类型

也可以实现自定义 Caddyfile 格式。Caddyfile 适配器是一个单一适配器实现，默认“服务器类型”为 HTTP，但在注册时可支持其他“服务器类型”。例如，HTTP Caddyfile 的注册方式如下：

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

你需要实现 [`caddyfile.ServerType` 接口](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType)，然后据此注册自己的适配器。
