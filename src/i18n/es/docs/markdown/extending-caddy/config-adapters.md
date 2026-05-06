---
title: "Escribir adaptadores de configuración"
---

# Escribir adaptadores de configuración

Por distintas razones, quizá quieras configurar Caddy usando un formato que no sea [JSON](/docs/json/). Caddy tiene soporte de primera clase para esto mediante [adaptadores de configuración](/docs/config-adapters).

Si aún no existe uno para el lenguaje/sintaxis/formato que prefieres, ¡puedes escribir uno!

## Plantilla

Aquí tienes una plantilla con la que puedes empezar:

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

- Consulta la documentación de [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- Consulta la documentación de la interfaz [`Adapter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

El JSON devuelto **no** debe llevar indentación; siempre debe estar en formato compacto. La persona que lo invoca puede formatearlo con sangrías si lo desea.

Ten en cuenta que, aunque los adaptadores de configuración son _plugins_ de Caddy, no son _modules_ de Caddy porque no se integran en una parte de la configuración (pero aparecerán en `list-modules` por conveniencia). Por eso no tienen métodos `Provision()` ni `Validate()` ni siguen el resto del ciclo de vida de los módulos. Solo necesitan implementar la interfaz `Adapter` y registrarse como adaptadores.

Cuando rellenes campos de la configuración que sean de tipo `json.RawMessage` (es decir, campos de módulos), usa las funciones `JSON()` y `JSONModuleObject()`:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) sirve para serializar los valores de los módulos sin incluir el nombre del módulo. (A menudo se usa en campos `ModuleMap`, donde el nombre del módulo es la clave del mapa.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) sirve para serializar valores de módulos agregando el nombre del módulo al objeto. (Se usa en la mayoría de los demás casos.)


## Tipos de servidor de Caddyfile

También es posible implementar un formato personalizado de Caddyfile. El adaptador Caddyfile es una única implementación de adaptador y su "tipo de servidor" predeterminado es HTTP, pero admite tipos de servidor alternativos en el registro. Por ejemplo, el Caddyfile HTTP se registra así:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Implementarías la interfaz [`caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) y registrarías tu propio adaptador en consecuencia.
