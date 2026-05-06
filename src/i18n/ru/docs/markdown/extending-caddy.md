---
title: "Расширение Caddy"
---

<a id="extending-caddy"></a>
# Расширение Caddy

Caddy легко расширять благодаря modular architecture. Большинство видов extensions (или plugins) Caddy известны как *modules*, если они расширяют или подключаются к структуре configuration Caddy. Для ясности: Caddy modules отличаются от [Go modules](https://github.com/golang/go/wiki/Modules) (хотя они также являются Go modules).

**Prerequisites:**
- Базовое понимание [архитектуры Caddy](/docs/architecture)
- Владение языком Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Quick Start

Caddy module — это любой named type, который регистрирует себя как Caddy module при import его package. Критически важно, что module всегда реализует interface [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), который предоставляет его name и constructor function.

В новом Go module вставьте следующий template в Go file и настройте package name, type name и Caddy module ID:

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

Затем выполните эту command из directory вашего project, и module должен появиться в list:

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

Команда [`xcaddy`](https://github.com/caddyserver/xcaddy) — важная часть workflow каждого module developer. Она compiles Caddy с вашим plugin, затем запускает его с заданными arguments. Временный binary каждый раз удаляется (похоже на `go run`).

</aside>


Поздравляем, ваш module регистрируется в Caddy и может использоваться в [config document Caddy](/docs/json/) в любых местах, где используются modules в том же namespace.

Под капотом `xcaddy` просто создает новый Go module, который requires и Caddy, и ваш plugin (с подходящим `replace`, чтобы использовать локальную development version), затем добавляет import, чтобы гарантировать compilation:

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Основы modules

Caddy modules:

1. Реализуют interface `caddy.Module`, чтобы предоставить ID и constructor
2. Имеют уникальное name в правильном namespace
3. Обычно satisfy некоторые interface(s), meaningful для host module этого namespace

**Host modules** (или *parent modules*) — modules, которые load/initialize другие modules. Обычно они определяют namespaces для guest modules.

**Guest modules** (или *child modules*) — modules, которые loaded или initialized. Все modules являются guest modules.


<a id="module-ids"></a>
## Module IDs

У каждого Caddy module есть уникальный ID, состоящий из namespace и name:

- Полный ID выглядит как `foo.bar.module_name`
- Namespace будет `foo.bar`
- Name будет `module_name`, и оно должно быть уникальным в своем namespace

Module IDs должны использовать convention `snake_case`.

<a id="namespaces"></a>
### Namespaces

Namespaces похожи на classes: namespace определяет functionality, общую для всех modules внутри него. Например, можно ожидать, что все modules в namespace `http.handlers` являются HTTP handlers. Из этого следует, что host module может type-assert guest modules в этом namespace из типов `interface{}` в более конкретный и полезный type, например `caddyhttp.MiddlewareHandler`.

Guest module должен быть корректно namespaced, чтобы host module его распознал, потому что host modules спрашивают Caddy о modules в определенном namespace, чтобы получить functionality, нужную host module. Например, если вы пишете HTTP handler module с именем `gizmo`, имя module будет `http.handlers.gizmo`, потому что app `http` ищет handlers в namespace `http.handlers`.

Иначе говоря, Caddy modules ожидаемо реализуют [определенные interfaces](/docs/extending-caddy/namespaces) в зависимости от своего module namespace. С этим convention developers modules могут говорить интуитивные вещи вроде: "Все modules в namespace `http.handlers` являются HTTP handlers." Технически это обычно означает: "Все modules в namespace `http.handlers` реализуют interface `caddyhttp.MiddlewareHandler`." Поскольку этот method set известен, можно assert и использовать более конкретный type.

**[Посмотрите таблицу соответствия всех standard Caddy namespaces их Go types.](/docs/extending-caddy/namespaces)**

Namespaces `caddy` и `admin` reserved и не могут быть app names.

Чтобы писать modules, которые подключаются к 3rd-party host modules, изучите документацию этих modules по namespaces.

<a id="names"></a>
### Names

Name внутри namespace важно и хорошо видно users, но само по себе не особенно важно, если оно unique, concise и осмысленно отражает назначение.


<a id="app-modules"></a>
## App Modules

Apps — это modules с empty namespace, которые по convention становятся собственным top-level namespace. App modules реализуют interface [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Эти modules появляются в property [`"apps"`](/docs/json/#apps) top-level config Caddy:

```json
{
	"apps": {}
}
```

Примеры [apps](/docs/json/apps/) — `http` и `tls`. Их namespace пустой.

Guest modules, написанные для этих apps, должны находиться в namespace, производном от app name. Например, HTTP handlers используют namespace `http.handlers`, а TLS certificate loaders — namespace `tls.certificates`.

<a id="module-implementation"></a>
## Реализация module

Module может быть почти любым type, но structs наиболее распространены, потому что могут хранить user configuration.


<a id="configuration"></a>
### Configuration

Большинству modules нужна configuration. Caddy делает это автоматически, если ваш type compatible with JSON. Поэтому если module является struct type, его fields должны иметь struct tags, использующие `snake_casing` согласно convention Caddy:

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

Опция `omitempty` в struct tag исключит field из JSON output, если оно имеет zero value своего type. Это полезно, чтобы JSON config оставалась clean и concise при marshaling (например, при адаптации из Caddyfile в JSON).

Когда module initialized, его configuration уже заполнена. Также можно выполнить дополнительные шаги [provisioning](#provisioning) и [validation](#validating) после initialization module.


<a id="module-lifecycle"></a>
### Module Lifecycle

Жизнь module начинается, когда он loaded host module. Происходит следующее:

1. Вызывается [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New), чтобы получить instance value module.
2. Configuration module unmarshaled в этот instance.
3. Если module является [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner), вызывается method `Provision()`.
4. Если module является [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator), вызывается method `Validate()`.
5. В этот момент host module получает loaded guest module как value `interface{}`, поэтому host module обычно type-assert guest module в более полезный type. Проверьте документацию host module, чтобы узнать требования к guest module в его namespace, например какие methods нужно реализовать.
6. Когда module больше не нужен, и если он является [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper), вызывается method `Cleanup()`.

Обратите внимание, что несколько loaded instances вашего module могут пересекаться во времени! При config changes новые modules запускаются до остановки старых. Осторожно используйте global state. Используйте type [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool), чтобы помогать управлять global state между module loads. Если ваш module listens on socket, используйте `caddy.Listen*()`, чтобы получить socket с поддержкой overlapping usage.

<a id="provisioning"></a>
### Provisioning

Configuration module будет автоматически unmarshaled в его value (при загрузке JSON config). Это означает, например, что struct fields будут заполнены за вас.

Однако если module требует дополнительных provisioning steps, можно реализовать optional interface [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner):

```go
// Provision sets up the module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: set up the module
	return nil
}
```

Здесь следует устанавливать default values для fields, которые не были предоставлены user (fields, которые не являются zero value). Если field required, можно вернуть error, если оно не задано. Для numeric fields, где zero value имеет смысл (например, timeout duration), можно поддержать `-1` как "off" вместо `0`, чтобы устанавливать default value, если user не настроил его.

Также обычно именно здесь host modules загружают свои guest/child modules.

Module может обращаться к другим apps через `ctx.App()`, но modules не должны иметь circular dependencies. Иными словами, module, loaded app `http`, не может depend on app `tls`, если module, loaded app `tls`, depend on app `http`. (Очень похоже на правила, запрещающие import cycles в Go.)

Кроме того, избегайте expensive operations в `Provision`, поскольку provisioning выполняется даже если config только validated. В provisioning phase не ожидайте, что module действительно будет used.

<a id="logs"></a>
#### Logs

См. [как logging работает](/docs/logging) в Caddy. Если вашему module нужен logging, не используйте `log.Print*()` из Go standard library. Иными словами, **не используйте global logger Go**. Caddy использует high-performance, highly flexible, structured logging с [zap](https://github.com/uber-go/zap).

Чтобы emit logs, получите logger в method Provision вашего module:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger is a *zap.Logger
}
```

Затем можно emit structured, leveled logs с помощью `g.logger`. Подробности см. в [godoc zap](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger).


<a id="validating"></a>
### Validating

Modules, которым нужно validate configuration, могут сделать это, удовлетворив optional interface [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator):

```go
// Validate validates that the module has a usable config.
func (g Gizmo) Validate() error {
	// TODO: validate the module's setup
	return nil
}
```

Validate должна быть read-only function. Она запускается после method `Provision()`.


<a id="interface-guards"></a>
### Interface guards

Поведение Caddy module implicit, потому что Go interfaces satisfied implicitly. Достаточно просто добавить правильные methods к type вашего module, чтобы сделать или сломать correctness module. Поэтому typo или неправильная method signature могут привести к неожиданному отсутствию behavior.

К счастью, есть простой compile-time check без overhead, который можно добавить в code, чтобы убедиться, что вы добавили правильные methods. Они называются interface guards:

```go
var _ InterfaceName = (*YourType)(nil)
```

Замените `InterfaceName` на interface, который вы собираетесь satisfy, а `YourType` — на name type вашего module.

Например, HTTP handler вроде static file server может satisfy multiple interfaces:

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Это предотвращает compilation program, если `*FileServer` не satisfy эти interfaces.

Без interface guards могут появиться confusing bugs. Например, если module должен provision itself перед использованием, но method `Provision()` содержит mistake (например, misspelled или wrong signature), provisioning никогда не произойдет, что приведет к confusion. Interface guards очень просты и могут это предотвратить. Обычно они находятся внизу file.


<a id="host-modules"></a>
## Host Modules

Module становится host module, когда загружает собственные guest modules. Это полезно, если часть functionality module может быть реализована разными способами.

Host module почти всегда является struct. Обычно для поддержки guest module нужны два struct fields: одно для raw JSON, другое для decoded value:

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

Первое field (`GadgetRaw` в этом примере) — место, где находится raw, unprovisioned JSON form guest module.

Второе field (`Gadget`) — место, где в итоге будет храниться final, provisioned value. Поскольку второе field не user-facing, мы исключаем его из JSON через struct tag. (Его также можно сделать unexported, если оно не нужно другим packages, и тогда struct tag не нужен.)

<a id="caddy-struct-tags"></a>
### Caddy struct tags

Struct tag `caddy` на raw module field помогает Caddy узнать namespace и name (составляющие complete ID) module, который нужно загрузить. Он также используется для generating documentation.

Struct tag имеет очень простой format: `key1=val1 key2=val2 ...`

Для module fields struct tag выглядит так:

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

Часть `namespace=` обязательна. Она задает namespace, в котором нужно искать module.

Часть `inline_key=` используется только если name module будет найден *inline* вместе с самим module; это означает, что value является object, где один из keys — *inline key*, а его value — name module. Если опущено, field type должен быть [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) или `[]caddy.ModuleMap`, где map key — name module.


<a id="loading-guest-modules"></a>
### Loading guest modules

Чтобы загрузить guest module, вызовите [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) во время provision phase:

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

Обратите внимание, что call `LoadModule()` принимает pointer на struct и field name как string. Странно, верно? Почему бы не передать struct field напрямую? Потому что есть несколько разных способов загрузки modules в зависимости от layout config. Такая method signature позволяет Caddy использовать reflection, чтобы понять лучший способ загрузки module и, главное, прочитать его struct tags.

Если guest module должен быть явно задан user, нужно вернуть error, если Raw field nil или empty, до попытки его загрузить.

Обратите внимание, как loaded module type-asserted: `g.Gadget = val.(Gadgeter)` — это потому, что returned `val` имеет type `interface{}`, который сам по себе не очень полезен. Однако мы ожидаем, что все modules в declared namespace (`foo.gizmo.gadgets` из struct tag в нашем примере) реализуют interface `Gadgeter`, поэтому этот type assertion безопасен, и затем мы можем его использовать!

Если host module определяет новый namespace, обязательно документируйте и этот namespace, и его Go type(s) для developers [как мы сделали здесь](/docs/extending-caddy/namespaces).

<a id="module-documentation"></a>
## Module Documentation

Зарегистрируйте module, чтобы новый Caddy module появился в module documentation и был доступен на http://caddyserver.com/download. Регистрация доступна на http://caddyserver.com/account. Создайте account, если его еще нет, и нажмите "Register package".

<a id="complete-example"></a>
## Полный пример

Предположим, мы хотим написать HTTP handler module. Это будет искусственный middleware для демонстрации, который печатает IP address visitor в stream при каждом HTTP request.

Мы также хотим, чтобы его можно было настроить через Caddyfile, потому что большинство людей предпочитает использовать Caddyfile в non-automated situations. Мы делаем это, регистрируя Caddyfile handler directive — тип directive, который может добавить handler в HTTP route. Также реализуем interface `caddyfile.Unmarshaler`. Добавив эти несколько строк code, module можно настроить через Caddyfile! Например: `visitor_ip stdout`.

Ниже code такого module с поясняющими comments:

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
