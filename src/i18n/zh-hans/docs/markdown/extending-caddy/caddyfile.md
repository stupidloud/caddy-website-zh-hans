---
title: "Caddyfile 支持"
---

# Caddyfile 支持

Caddy 模块在[注册](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule)时会根据其命名空间自动添加到[原生 JSON 配置](/docs/json/)中，从而既可使用又具备文档记录。这使得对 Caddyfile 的支持完全可选，但偏好使用 Caddyfile 的用户通常会提出此需求。

## 反序列化器

若要为您的模块添加对 Caddyfile 的支持，只需实现 [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler) 接口即可。您可以通过解析令牌的方式，来决定模块采用哪种 Caddyfile 语法。

解序列器的任务仅仅是根据传入的[`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser)，设置模块的类型，例如填充其字段。例如，一个名为 `Gizmo` 可能具有以下方法：

```go
// UnmarshalCaddyfile implements caddyfile.Unmarshaler. Syntax:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consume directive name

	if !d.Args(&g.Name) {
		// not enough args
		return d.ArgErr()
	}
	if d.NextArg() {
		// optional arg
		g.Option = d.Val()
	}
	if d.NextArg() {
		// too many args
		return d.ArgErr()
	}

	return nil
}
```

建议在该方法的 godoc 注释中记录语法。有关解析 Caddyfile 的更多信息，请参阅[ `caddyfile` 包的 godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc)。

可以通过一个简单的 `d.Next()` 调用即可。

请务必使用以下命令检查参数是否缺失或多余： `d.NextArg()` 或 `d.RemainingArgs()`。使用 `d.ArgErr()` 来显示简单的“无效情况”提示，或者使用 `d.Errf("some message")` 来编写包含问题说明（最好附带建议解决方案）的有用错误信息。

你还应添加一个[接口检查](/docs/extending-caddy#interface-guards)，以确保该接口被正确满足：

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

### 模块

若需处理超出单行容量的配置内容，您可能希望允许包含子指令的代码块。这可以通过以下方式实现： `d.NextBlock()` 并循环迭代，直到返回原始嵌套层级：

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

只要循环的每次迭代都能处理完整个段（行或代码块），这便是一种优雅的处理代码块的方法。

## HTTP 指令

HTTP Caddyfile 是 Caddy 的默认 Caddyfile 适配器语法（或“服务器类型”）。它具有可扩展性，这意味着您可以为自己的模块[注册](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective)自定义的“顶级”指令：

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

如果您的指令只返回一个 HTTP 处理程序（这是常见的情况），您可能会觉得 [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) 更方便：

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

基本思路是，您关联到指令的[解析函数](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc)会返回一个或多个[`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue)值。（或者，如果使用 `RegisterHandlerDirective`，则只需直接返回已填充的 `caddyhttp.MiddlewareHandler` 值。）每个配置值都关联一个[“类”，](#classes)这有助于 HTTP Caddyfile 适配器识别该值可在最终 JSON 配置的哪些部分中使用。所有配置值会被汇总到一个集合中，适配器在构建最终 JSON 配置时会从中提取数据。

此设计允许您的指令为任何已识别的类返回任意配置值，这意味着它可以影响 HTTP Caddyfile 适配器为其指定了类的配置中的任何部分。

如果你已经实现了 `UnmarshalCaddyfile()` 方法，那么你的 parse 函数可以简单地写成：

```go
// parseCaddyfileHandler unmarshals tokens from h into a new middleware handler value.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

有关如何使用该 `httpcaddyfile.Helper` 类型。

### 处理程序顺序

所有返回 HTTP 中间件/处理程序值的指令都必须按正确顺序执行。例如，设置网站根目录的处理程序必须位于访问根目录的处理程序之前，这样后者才能知道目录路径是什么。

HTTP Caddyfile [中标准指令的顺序是硬编码的](/docs/caddyfile/directives#directive-order)。这确保了用户无需了解 Web 服务器最常用功能的实现细节，并使他们更容易编写正确的配置。鉴于 Caddyfile 的可扩展性，单一的硬编码列表还能避免非确定性。

**注册新的处理程序指令时，必须先将其添加到该列表中，才能在 `route` 块之外）使用。** 这可以通过以下三种方法之一实现：

- （推荐）插件作者可以在 `init()` ，将其插入到相对于另一个[标准指令](/docs/caddyfile/directives#directive-order)的顺序中。这样，用户无需额外配置即可直接在自己的网站中使用该指令。例如，若要将您的指令 `gizmo` 使其在 `header` 处理程序之后：

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- 用户可以添加[全局选项](/docs/caddyfile/options) [`order`](/docs/caddyfile/options) 来修改其 `Caddyfile` 的默认排序顺序。例如： `order gizmo before respond` 将插入一条新指令 `gizmo` ，使其在 `respond` 处理程序之前进行评估。随后该指令即可正常使用。

- 用户可以在[`route`块](/docs/caddyfile/directives/route)中放置该指令。由于路由块中的指令不会被重新排序，因此无需在列表中列出路由块中使用的指令。

如果您选择了后两个选项中的任意一个，请为用户提供一份说明，指出该指令在列表中的正确排序位置，以便他们能够正确使用它。

### 课程

下表列出了 HTTP Caddyfile 适配器所识别的、包含导出类型的各个类：

类名 | 预期类型 | 描述
---------- | ------------- | -----------
绑定 | `[]string` | 服务器监听器绑定地址
路由 | `caddyhttp.Route` | HTTP 处理程序路由
error_route | `*caddyhttp.Subroute` | HTTP 错误处理路由
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS 连接策略
tls.cert_issuer | `certmagic.Issuer` | TLS 证书签发者
tls.cert_loader | `caddytls.CertificateLoader` | TLS 证书加载器

## 服务器类型

从结构上看，Caddyfile 是一种简单的格式，因此可以有不同类型的 Caddyfile 格式（有时称为“服务器类型”），以满足不同的需求。

默认的 Caddyfile 格式是 HTTP Caddyfile，您可能对此已经很熟悉。该格式主要用于配置 [`http` 应用程序](/docs/modules/http)，同时可能仅在 Caddy 配置结构的其他部分（例如 `tls` app 用于加载和自动化证书）。

要配置 HTTP 以外的应用程序，您可能需要实现一个使用自定义[服务器类型的](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter)配置适配器。Caddyfile 适配器会为您解析输入内容，并返回服务器块和选项的列表，而您的适配器则需要解析该结构，并将其转换为 JSON 配置。
