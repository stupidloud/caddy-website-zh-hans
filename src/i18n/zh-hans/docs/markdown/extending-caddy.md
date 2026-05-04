---
title: "扩展 Caddy"
---

# 扩展 Caddy

由于采用了模块化架构，Caddy 非常容易进行扩展。大多数类型的 Caddy 扩展（或插件）如果扩展或接入 Caddy 的配置结构，通常被称为“模块”。需要明确的是，Caddy 模块与 [Go 模块](https://github.com/golang/go/wiki/Modules)是不同的（但它们本身也是 Go 模块）。

**先决条件：**
- 对 [Caddy 架构](/docs/architecture)有基本了解
- Go 语言能力
- <a href="https://golang.org/doc/install">`go` <img src="/old/resources/images/external-link.svg" class="external-link"></a>
- <a href="https://github.com/caddyserver/xcaddy">`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link"></a>


## 快速入门

Caddy 模块是指任何在导入其包时将自身注册为 Caddy 模块的命名类型。关键在于，该模块必须始终实现 [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module) 接口，该接口提供了其名称和构造函数。

在新的 Go 模块中，将以下模板粘贴到 Go 文件中，并自定义您的包名、类型名和 Caddy 模块 ID：

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo is an example; put your own type here.
type Gizmo struct {
}

// CaddyModule returns the Caddy module information.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

然后在项目目录下运行以下命令，你应该能在列表中看到你的模块：

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

[`xcaddy` 命令](https://github.com/caddyserver/xcaddy)是每位模块开发者工作流程中的重要环节。它会将 Caddy 与您的插件一起编译，然后使用给定的参数运行它。每次运行后，它都会丢弃临时二进制文件（类似于 `go run`）。

</aside>


恭喜，您的模块已成功注册到 Caddy，现在可以在 [Caddy 的配置文件](/docs/json/)中，凡是使用同一命名空间模块的地方均可使用该模块。

实际上， `xcaddy` 只是创建了一个新的 Go 模块，该模块同时依赖 Caddy 和您的插件（并使用适当的 `replace` 来使用您的本地开发版本），然后添加一个导入语句以确保其被编译进去：

```go
import _ "github.com/example/mymodule"
```


## 模块基础知识

Caddy 模块：

1. 实现 `caddy.Module` 接口，以提供 ID 和构造函数
2. 在正确的命名空间中拥有一个唯一的名称
3. 通常实现该命名空间中对主模块具有实际意义的某个或某些接口

**宿主模块**（或称*父模块*）是指负责加载/初始化其他模块的模块。它们通常为客体模块定义命名空间。

**客体模块**（或称*子模块*）是指会被加载或初始化的模块。所有模块都是客体模块。


## 模块 ID

每个 Caddy 模块都有一个唯一的 ID，由命名空间和名称组成：

- 完整的ID如下所示 `foo.bar.module_name`
- 命名空间将是 `foo.bar`
- 名称应为 `module_name` 该名称在其命名空间中必须是唯一的

模块 ID 必须遵循 `snake_case` 约定。

### 命名空间

命名空间类似于类，即一个命名空间定义了其中所有模块共有的某些功能。例如，我们可以预期 `http.handlers` 都是 HTTP 处理程序。因此，主模块可以对该命名空间中的客模块进行类型断言，将其 `interface{}` 类型，转换为更具体、更实用的类型，例如 `caddyhttp.MiddlewareHandler`.

访客模块必须正确设置命名空间，才能被主模块识别，因为主模块会向 Caddy 请求特定命名空间内的模块，以提供主模块所需的功能。例如，如果你编写了一个名为 `gizmo`，那么该模块的名称应为 `http.handlers.gizmo`，因为 `http` app 会在 `http.handlers` 命名空间中查找处理程序。

换句话说，Caddy 模块应根据其模块命名空间实现[特定的接口](/docs/extending-caddy/namespaces)。遵循这一约定，模块开发者可以直观地表示：“ `http.handlers` 命名空间中的所有模块都是 HTTP 处理程序。”从技术角度讲，这通常意味着：“ `http.handlers` 命名空间中的所有模块都实现了 `caddyhttp.MiddlewareHandler` 接口。”由于该方法集是已知的，因此可以断言并使用更具体的类型。

**[查看将所有标准 Caddy 命名空间映射到其 Go 类型的对照表。](/docs/extending-caddy/namespaces)**

该 `caddy` 和 `admin` 命名空间是保留的，不能用作应用名称。

若要编写可接入第三方主模块的模块，请查阅这些模块的命名空间文档。

### 名称

命名空间内的名称对用户而言意义重大且显而易见，但只要它具有唯一性、简洁且能准确反映其功能，其重要性便不那么突出。


## 应用模块

App 模块是一个具有空命名空间的模块，通常会成为其自身的顶级命名空间。App 模块实现了 [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App) 接口。

这些模块出现在 Caddy 配置文件顶层的 [`"apps"`](/docs/json/#apps) 属性中：

```json
{
	"apps": {}
}
```

示例[应用](/docs/json/apps/)包括 `http` 以及 `tls`。它们属于空命名空间。

为这些应用程序编写的客体模块应位于一个从应用程序名称派生的命名空间中。例如，HTTP 处理程序使用 `http.handlers` 命名空间，而 TLS 证书加载器则使用 `tls.certificates` 命名空间。

## 模块实现

模块可以是几乎任何类型，但结构体最为常见，因为它们可以存储用户配置。


### 配置

大多数模块都需要进行一些配置。只要您的类型与 JSON 兼容，Caddy 就会自动处理这些配置。因此，如果某个模块是结构体类型，则其字段需要添加结构体标签，这些标签应遵循 `snake_casing` ：

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

在结构体标签中使用 `omitempty` 选项，如果字段的值是其类型的零值，则该字段将从 JSON 输出中省略。这有助于在序列化时（例如将 Caddyfile 转换为 JSON）保持 JSON 配置的简洁和清晰。

模块初始化时，其配置已预先填入。模块初始化完成后，还可以执行额外的[配置](#provisioning)和[验证](#validating)步骤。


### 模块生命周期

模块的生命周期始于被主模块加载之时。此时会发生以下情况：

1. 调用 [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) 以获取该模块值的实例。
2. 该模块的配置被反序列化到该实例中。
3. 如果该模块是[`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner)，则 `Provision()` 方法将被调用。
4. 如果该模块是[`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator)，则 `Validate()` 方法将被调用。
5. 此时，宿主模块会将已加载的客体模块作为 `interface{}` 值，因此宿主模块通常会将客体模块的类型转换为更实用的类型。请查阅宿主模块的文档，了解其命名空间中对客体模块的要求，例如需要实现哪些方法。
6. 当不再需要某个模块时，如果该模块是[`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper)，则会调用 `Cleanup()` 方法。

请注意，在特定时刻，模块的多个已加载实例可能会发生重叠！在配置变更期间，新模块会在旧模块停止之前启动。请务必谨慎使用全局状态。建议使用[`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool)类型来帮助管理跨模块加载的全局状态。如果您的模块监听某个套接字，请使用 `caddy.Listen*()` 来获取支持重叠使用的套接字。

### 配置

模块的配置会在加载 JSON 配置时自动反序列化为其值。这意味着，例如，结构体的字段会自动为您填充。

不过，如果您的模块需要额外的配置步骤，您可以实现（可选的）[`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) 接口：

```go
// Provision sets up the module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: set up the module
	return nil
}
```

在此处，您应为用户未填写的字段（即非零值的字段）设置默认值。如果某个字段为必填项，且该字段未被设置，则应返回错误。对于零值具有特定含义的数值字段（例如某些超时时长），您可能需要支持 `-1` 表示“关闭”而非 `0`，因此若用户未进行配置，您可设置默认值。

这也是宿主模块通常加载其客体/子模块的位置。

模块可以通过调用 `ctx.App()`，但模块之间不得存在循环依赖。换言之，由 `http` 加载的模块，则不得依赖于 `tls` ，而该app `tls` 应用所加载的模块依赖于 `http` 应用。

此外，您应避免在 `Provision`，因为即使配置仅处于验证阶段，系统也会执行资源分配。在资源分配阶段，请不要期望该模块会被实际使用。

#### 日志

了解 Caddy 中的[日志记录机制](/docs/logging)。如果您的模块需要日志记录，请不要使用 `log.Print*()` 。换句话说，**请勿使用 Go 的全局日志器**。Caddy 采用 [zap](https://github.com/uber-go/zap) 实现高性能、高度灵活且结构化的日志记录。

要在模块中输出日志，请在模块的 Provision 方法中获取一个日志器：

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger is a *zap.Logger
}
```

然后，您可以使用 `g.logger`。详情请参阅 [zap 的 godoc](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger)。


### 验证

希望验证其配置的模块可以通过实现（可选的）[`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) 接口来完成：

```go
// Validate validates that the module has a usable config.
func (g Gizmo) Validate() error {
	// TODO: validate the module's setup
	return nil
}
```

Validate 应该是一个只读函数。它会在 `Provision()` 方法之后执行。


### 接口守护

Caddy 模块的行为是隐式的，因为 Go 语言中的接口是通过隐式方式满足的。只需在模块的类型中添加正确的方法，就足以决定该模块是否正确。因此，打错字或方法签名有误都可能导致意外的行为（或行为缺失）。

幸运的是，你可以向代码中添加一种简单且不增加开销的编译时检查，以确保已添加了正确的方法。这种检查被称为接口守护：

```go
var _ InterfaceName = (*YourType)(nil)
```

将 `InterfaceName` 替换为要实现的接口，并将 `YourType` 替换为您的模块类型的名称。

例如，像静态文件服务器这样的 HTTP 处理程序可能满足多个接口：

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

如果 `*FileServer` 不满足这些接口。

如果没有接口守护，可能会出现令人困惑的错误。例如，如果你的模块在使用前必须进行初始化，但你的 `Provision()` 方法存在错误（例如拼写错误或签名不正确），初始化将永远无法进行，这会让人百思不得其解。接口守护条件非常简单，且能有效防止这种情况。它们通常放在文件底部。


## 主机模块

当一个模块加载其自身的客体模块时，该模块便成为主模块。如果模块的某项功能可以通过不同方式实现，这种做法就非常有用。

主机模块几乎总是以结构体（struct）的形式存在。通常，支持一个客体模块需要两个结构体字段：一个用于存储其原始 JSON，另一个用于存储其解码后的值：

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

第一个字段（`GadgetRaw` 在此示例中）是存放未配置的原始 JSON 格式客机模块的位置。

第二个字段（`Gadget`）是最终配置值的存储位置。由于第二个字段不面向用户，我们使用 struct 标签将其从 JSON 中排除。（如果其他包不需要该字段，您也可以将其设为未导出，这样就无需使用 struct 标签。）

### Caddy 结构体标签

位于原始模块字段上的 `caddy` raw 模块字段中的 struct 标签有助于 Caddy 识别要加载的模块的命名空间和名称（构成完整的 ID）。它还用于生成文档。

struct 标签的格式非常简单： `key1=val1 key2=val2 ...`

对于模块字段，struct 标签将如下所示：

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

必须包含 `namespace=` 部分是必需的。它定义了用于查找该模块的命名空间。

该 `inline_key=` 部分仅在模块名称与模块本身*内联*出现时使用；这意味着该值是一个对象，其中一个键是*内联键*，其值为模块名称。如果省略，则字段类型必须是[`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap)或 `[]caddy.ModuleMap`，其中映射键即为模块名称。


### 加载来宾模块

要在配置阶段加载一个来宾模块，请调用[`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule)：

```go
// Provision sets up g and loads its gadget.
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

请注意，该 `LoadModule()` 该调用接受一个指向结构体的指针以及作为字符串的字段名。很奇怪，对吧？为什么不直接传递结构体字段呢？这是因为根据配置的布局，加载模块有几种不同的方式。这种方法签名允许 Caddy 使用反射来确定加载模块的最佳方式，最重要的是，读取其结构体标签。

如果某个访客模块必须由用户显式设置，那么在尝试加载该模块之前，如果 Raw 字段为 nil 或为空，应返回错误。

请注意加载的模块是如何进行类型断言的： `g.Gadget = val.(Gadgeter)` - 这是因为返回的 `val` 是一个 `interface{}` 类型，本身并不太实用。不过，我们期望声明的命名空间（`foo.gizmo.gadgets` 在我们的示例中来自 struct 标签）中的所有模块都实现了 `Gadgeter` 接口，因此这种类型断言是安全的，我们就可以使用它了！

如果您的宿主模块定义了一个新的命名空间，请务必[像我们在此处所做的那样](/docs/extending-caddy/namespaces)，为开发者详细记录该命名空间及其 Go 类型。

## 模块文档

注册该模块，以便新创建的 Caddy 模块能在模块文档中显示，并可在 http://caddyserver.com/download 上使用。注册地址为 http://caddyserver.com/account。如果您还没有账户，请先创建一个，然后点击“注册包”。

## 完整示例

假设我们要编写一个 HTTP 处理程序模块。这是一个为演示目的而设计的示例中间件，它会在每次 HTTP 请求时将访问者的 IP 地址打印到一个流中。

我们还希望它能通过 Caddyfile 进行配置，因为在非自动化场景下，大多数人更倾向于使用 Caddyfile。我们通过注册一个 Caddyfile 处理程序指令来实现这一点，这是一种能够向 HTTP 路由添加处理程序的指令。我们还实现了 `caddyfile.Unmarshaler` 接口。只需添加这几行代码，该模块即可通过 Caddyfile 进行配置！例如： `visitor_ip stdout`.

以下是该模块的代码，其中包含说明性注释：

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

// Middleware implements an HTTP handler that writes the
// visitor's IP address to a file or stream.
type Middleware struct {
	// The file or stream to write to. Can be "stdout"
	// or "stderr".
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule returns the Caddy module information.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision implements caddy.Provisioner.
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

// Validate implements caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP implements caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile implements caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consume directive name

	// require an argument
	if !d.NextArg() {
		return d.ArgErr()
	}

	// store the argument
	m.Output = d.Val()
	return nil
}

// parseCaddyfile unmarshals tokens from h into a new Middleware.
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
