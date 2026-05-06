---
title: "Написание config adapters"
---

<a id="writing-config-adapters"></a>
# Написание config adapters

По разным причинам вы можете захотеть настраивать Caddy в формате, отличном от [JSON](/docs/json/). Caddy имеет первоклассную поддержку этого через [config adapters](/docs/config-adapters).

Если для нужного вам language/syntax/format еще нет adapter, можно написать свой!

<a id="template"></a>
## Template

Вот template, с которого можно начать:

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

- См. godoc для [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- См. godoc для interface ['Adapter'](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

Возвращаемый JSON **не** должен иметь отступов; он всегда должен быть compact. Caller всегда может prettify его при необходимости.

Обратите внимание: config adapters являются Caddy *plugins*, но не являются Caddy *modules*, потому что они не интегрируются в часть config (хотя для удобства они появятся в `list-modules`). Поэтому у них нет methods `Provision()` или `Validate()`, и они не следуют остальному module lifecycle. Им нужно только реализовать interface `Adapter` и зарегистрироваться как adapters.

При заполнении fields config с типом `json.RawMessage` (т. е. module fields) используйте функции `JSON()` и `JSONModuleObject()`:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) предназначена для marshaling module values без встроенного имени module. (Часто используется для fields ModuleMap, где имя module является key в map.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) предназначена для marshaling module values с добавлением имени module в object. (Используется почти везде остальном.)


<a id="caddyfile-server-types"></a>
## Caddyfile Server Types

Также возможно реализовать custom Caddyfile format. Caddyfile adapter — это единая adapter implementation, и его default "server type" — HTTP, но он поддерживает alternate "server types" при регистрации. Например, HTTP Caddyfile регистрируется так:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Нужно реализовать [interface `caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) и соответствующим образом зарегистрировать свой adapter.
