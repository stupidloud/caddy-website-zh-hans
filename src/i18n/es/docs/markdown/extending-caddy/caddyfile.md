---
title: "Soporte de Caddyfile"
---

# Soporte de Caddyfile

Los módulos de Caddy se añaden automáticamente al [JSON nativo](/docs/json/) por su namespace cuando se registran mediante [`RegisterModule`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule). Eso los hace utilizables y documentables. Por eso el soporte de Caddyfile es opcional, pero suele pedirse por usuarios que prefieren usar Caddyfile.


## Unmarshaler

Para agregar soporte de Caddyfile a tu módulo, implementa simplemente la interfaz [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Tú defines la sintaxis del Caddyfile según como parsees los tokens.

La misión del `Unmarshaler` es preparar el tipo de tu módulo, por ejemplo rellenando sus campos, usando el [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser). Por ejemplo, un tipo llamado `Gizmo` podría tener este método:

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

Es buena idea documentar la sintaxis en el comentario de la función en la godoc. Mira la [godoc del paquete `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc) para más detalles de parseo de Caddyfile.

El token del nombre de la directiva se puede consumir o saltar con una llamada simple `d.Next()`.

Comprueba argumentos faltantes y/o de más con `d.NextArg()` o `d.RemainingArgs()`. Usa `d.ArgErr()` para un mensaje de error simple, o `d.Errf("some message")` para mostrar un error con explicación y, idealmente, sugerencia de solución.

También debes añadir un [interface guard](/docs/extending-caddy#interface-guards) para asegurar que la interfaz está bien implementada:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

### Bloques

Si necesitas aceptar más configuración de la que cabe en una sola línea, puedes permitir un bloque con subdirectivas usando `d.NextBlock()` y un bucle hasta volver al nivel de anidamiento original:

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

Mientras cada iteración consume todo el segmento (línea o bloque), esta es una forma limpia de procesar bloques.

## Directivas HTTP

El Caddyfile HTTP es la sintaxis de adaptador por defecto de Caddy (o “server type”). Es extensible, y puedes [registrar](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective) tus propias directivas de nivel superior para tu módulo:

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Si tu directiva solo devuelve un único handler HTTP (lo habitual), quizá te resulte más cómodo usar [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective):

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

La idea principal es que [la función de parseo](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) asociada a tu directiva devuelva uno o más valores [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue). (O, si usas `RegisterHandlerDirective`, devuelve directamente un `caddyhttp.MiddlewareHandler` ya creado.) Cada valor de configuración va asociado a una **["class"](#classes)** que indica al adaptador HTTP dónde puede usarse en el JSON final. Todos esos valores se agrupan y el adaptador usa ese pileta de opciones para construir el JSON.

Este diseño permite a tu directiva devolver cualquier configuración para cualquier clase reconocida, por lo que puede afectar a cualquier parte del JSON final para la que ese adaptador HTTP tenga una clase definida.

Si ya implementaste `UnmarshalCaddyfile()`, tu función de parseo puede ser algo así:

```go
// parseCaddyfileHandler unmarshals tokens from h into a new middleware handler value.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Consulta la godoc de [`httpcaddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc) para más información sobre el tipo [`httpcaddyfile.Helper`].


### Orden de handlers

Todas las directivas que devuelven middleware/handlers HTTP deben evaluarse en el orden correcto. Por ejemplo, un handler que define el directorio raíz debe ir antes del handler que accede a ese directorio para que conozca la ruta.

El Caddyfile HTTP [tiene un orden fijo para directivas estándar](/docs/caddyfile/directives#directive-order). Así los usuarios no dependen de detalles de implementación y puede configurarse correctamente. Una lista fija también evita no determinismo al ser el Caddyfile extensible.

**Cuando registras una nueva directiva handler, debes añadirla a esa lista antes de poder usarla fuera de un bloque `route`.** Puedes hacerlo con una de estas tres formas:

- (Recomendado) El autor del plugin puede llamar a [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) dentro de `init()` tras registrar la directiva, para insertarla en relación a otra [directiva estándar](/docs/caddyfile/directives#directive-order). Así los usuarios pueden usarla directamente en sitios sin configuración extra. Por ejemplo, para insertar `gizmo` después de `header`:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Los usuarios pueden agregar la opción global [`order`](/docs/caddyfile/options) para modificar el orden estándar de su Caddyfile. Ejemplo: `order gizmo before respond` insertará la directiva `gizmo` antes de `respond`.

- Los usuarios pueden colocar la directiva dentro de un bloque [`route`](/docs/caddyfile/directives/route). Como en `route` no hay reordenado, las directivas dentro del bloque no necesitan respetar la lista.

Si eliges una de las dos últimas opciones, documenta una recomendación de orden para los usuarios, indicando dónde debería situarse tu directiva.

### Clases

Esta tabla describe cada clase con tipos exportados reconocida por el adaptador HTTP:

Class name | Expected type | Description
---------- | ------------- | -----------
bind | `[]string` | Server listener bind addresses
route | `caddyhttp.Route` | HTTP handler route
error_route | `*caddyhttp.Subroute` | HTTP error handling route
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS connection policy
tls.cert_issuer | `certmagic.Issuer` | TLS certificate issuer
tls.cert_loader | `caddytls.CertificateLoader` | TLS certificate loader

## Tipos de servidor

Estructuralmente, Caddyfile es un formato simple, por eso pueden existir distintos tipos de Caddyfile (a veces llamados "tipos de servidor") para cubrir más necesidades.

El Caddyfile por defecto es el HTTP Caddyfile, al que probablemente ya estés familiarizado. Este formato configura principalmente la app [`http`][/docs/modules/http] y puede incluir pequeñas partes en otras secciones de la configuración JSON (por ejemplo, la app `tls` para cargar y automatizar certificados).

Si quieres configurar apps que no sean HTTP, quizá quieras implementar tu propio adaptador de configuración usando [tu propio tipo de servidor](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter). El adaptador Caddyfile parseará el input y te dará la lista de bloques de servidor, opciones y demás para que luego tu adaptador lo transforme en JSON.
