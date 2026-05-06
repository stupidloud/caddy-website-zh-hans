---
title: "Extender Caddy"
---

# Extender Caddy

Caddy es fácil de extender gracias a su arquitectura modular. La mayor parte de las extensiones (o plugins) de Caddy se conocen como _módulos_ si amplían o se integran en la estructura de configuración de Caddy. Para aclarar, los módulos de Caddy son distintos de los [módulos de Go](https://github.com/golang/go/wiki/Modules) (aunque también son módulos de Go).

**Requisitos previos:**
- Conocer la arquitectura de Caddy ([Architecture](/docs/architecture))
- Conocimientos de Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


## Inicio rápido

Un módulo de Caddy es cualquier tipo con nombre que se registra como un módulo de Caddy cuando su paquete se importa. Lo importante es que un módulo siempre implementa la interfaz [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), que proporciona su nombre y una función constructora.

En un nuevo módulo de Go, pega esta plantilla en un archivo `.go` y personaliza el nombre del paquete, el nombre del tipo y el ID del módulo de Caddy:

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

Luego ejecuta este comando desde el directorio de tu proyecto y deberías ver tu módulo en la lista:

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

El comando [`xcaddy`](https://github.com/caddyserver/xcaddy) es una parte importante del flujo de cualquier desarrollador de módulos. Compila Caddy con tu plugin y luego lo ejecuta con los argumentos indicados. Descarta el binario temporal cada vez (igual que `go run`).

</aside>


Enhorabuena, tu módulo ya está registrado en Caddy y puede usarse en [el documento de configuración de Caddy](/docs/json/) en cualquier lugar donde ese namespace acepte módulos.

Por debajo, `xcaddy` simplemente crea un nuevo módulo de Go que requiere tanto a Caddy como a tu plugin (con un `replace` apropiado para usar tu versión local), y luego añade una importación para asegurar que se compile:

```go
import _ "github.com/example/mymodule"
```


## Conceptos básicos de módulos

Módulos de Caddy:

1. Implementan la interfaz `caddy.Module` para proporcionar un ID y un constructor
2. Tienen un nombre único en el namespace correspondiente
3. Por lo general, satisfacen una o más interfaces que tienen sentido para el módulo anfitrión de ese namespace

Los **módulos anfitrión** (o _parent modules_) cargan e inicializan otros módulos. Normalmente definen namespaces para los módulos invitados.

Los **módulos invitados** (o _child modules_) son módulos que se cargan o inicializan. Todos los módulos son módulos invitados.


## IDs de módulos

Cada módulo de Caddy tiene un ID único, con namespace y nombre:

- Un ID completo tiene la forma `foo.bar.module_name`
- El namespace sería `foo.bar`
- El nombre sería `module_name`, que debe ser único dentro de ese namespace

Los IDs de módulos deben usar la convención `snake_case`.

### Namespaces

Un namespace funciona como una clase: define funcionalidad común entre todos los módulos dentro de él. Por ejemplo, podemos esperar que todos los módulos del namespace `http.handlers` sean manejadores HTTP. Esto significa que un módulo anfitrión puede hacer *type assert* de los módulos invitados en ese namespace desde `interface{}` hacia un tipo específico y útil como `caddyhttp.MiddlewareHandler`.

Un módulo invitado debe estar bien tipado para su namespace para que el módulo anfitrión lo reconozca, porque los módulos anfitrión piden a Caddy módulos de un namespace concreto para proporcionar la funcionalidad que necesitan. Por ejemplo, si escribes un módulo de tipo handler llamado `gizmo`, el nombre del módulo sería `http.handlers.gizmo`, porque la aplicación `http` buscará handlers en el namespace `http.handlers`.

En otras palabras, los módulos de Caddy deberían implementar las [interfaces adecuadas](/docs/extending-caddy/namespaces) según su namespace. Con esta convención, los autores de módulos pueden decir cosas intuitivas como “todos los módulos en el namespace `http.handlers` son middleware handlers”. Más técnicamente, suele significar “todos los módulos en el namespace `http.handlers` implementan la interfaz `caddyhttp.MiddlewareHandler`”. Al conocer ese set de métodos, se puede afirmar el tipo correcto y usarlo.

**[Ver una tabla que mapea todos los namespaces estándar de Caddy con sus tipos Go.](/docs/extending-caddy/namespaces)**

Los namespaces `caddy` y `admin` están reservados y no pueden ser nombres de app.

Para escribir módulos que se integren en módulos de terceros, consulta la documentación del namespace de ese módulo.

### Nombres

El nombre dentro de un namespace es visible para usuarios y bastante importante, pero no tiene que ser perfecto; basta con que sea único, conciso y tenga sentido respecto a su función.


## Módulos App

Las apps son módulos con namespace vacío y que por convención se convierten en su propio namespace superior. Los módulos App implementan la interfaz [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Estos módulos aparecen en la propiedad [`"apps"`](/docs/json/#apps) del nivel superior de la configuración JSON de Caddy:

```json
{
	"apps": {}
}
```

Ejemplos de apps en [`/docs/json/apps/`](/docs/json/apps/) son `http` y `tls`. Sus namespaces son vacíos.

Los módulos invitados de estas apps deben ir en un namespace derivado del nombre de la app. Por ejemplo, los handlers HTTP usan `http.handlers` y los cargadores de certificados TLS usan `tls.certificates`.

## Implementación de módulos

Un módulo puede ser casi cualquier tipo, pero las estructuras (`struct`) son las más comunes porque pueden recibir configuración de usuarios.


### Configuración

La mayoría de los módulos requiere algo de configuración. Caddy la maneja automáticamente si tu tipo es compatible con JSON. Por eso, si el módulo es una estructura, debe llevar etiquetas de struct con `snake_casing` según convención de Caddy:

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

La opción `omitempty` en la etiqueta JSON omitirá el campo si su valor es el cero del tipo. Esto ayuda a mantener limpia y concisa la configuración JSON al serializarse (por ejemplo, al adaptar Caddyfile a JSON).

Cuando se inicializa un módulo, su configuración ya viene rellenada. También se pueden ejecutar pasos adicionales de [provisioning](#provisioning) y [validación](#validating).


### Ciclo de vida de módulos

La vida de un módulo empieza cuando un módulo anfitrión lo carga. Ocurre esto:

1. Se llama a [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) para crear una instancia del módulo.
2. La configuración del módulo se desempaqueta en esa instancia.
3. Si el módulo implementa [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner), se llama a `Provision()`.
4. Si el módulo implementa [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator), se llama a `Validate()`.
5. En este punto, el módulo anfitrión recibe el módulo invitado cargado como `interface{}`, así que normalmente hará un type assertion al tipo correcto. Revisa la documentación del módulo anfitrión para saber qué métodos debe implementar el módulo invitado en ese namespace.
6. Cuando ya no se necesita el módulo y este implementa [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#CleanerUpper), se llama a `Cleanup()`.

Ten en cuenta que pueden solaparse varias instancias activas de un mismo módulo en paralelo. Durante cambios de configuración, se inician módulos nuevos antes de detener los antiguos. Maneja el estado global con cuidado. Usa el tipo [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) para ayudar a administrar estado global entre cargas.

Si tu módulo escucha en un socket, usa `caddy.Listen*()` para obtener un socket con soporte de uso simultáneo.

### Provisioning

La configuración de un módulo se deserializa en su valor automáticamente al cargar JSON. Eso significa, por ejemplo, que los campos del struct se rellenan.

Sin embargo, si tu módulo requiere pasos de provisioning extra, puedes implementar (opcionalmente) la interfaz [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner):

```go
// Provision sets up the module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: set up the module
	return nil
}
```

Aquí puedes definir valores por defecto para campos no configurados por el usuario. Si un campo es obligatorio, puedes retornar error si falta. Para campos numéricos donde el valor cero tiene significado (por ejemplo, timeouts), puede tener sentido usar `-1` para representar `off` en lugar de `0`, y así elegir un valor por defecto adecuado.

También suele ser aquí donde los módulos anfitrión cargan sus módulos invitados/child.

Un módulo puede acceder a otras apps llamando `ctx.App()`, pero no debe haber dependencias circulares. En otras palabras, un módulo cargado por la app `http` no puede depender de la app `tls` si un módulo cargado por `tls` depende de `http`. (Muy parecido a evitar ciclos de import en Go.)

Además, evita operaciones costosas en `Provision`: el provisioning se ejecuta incluso si la configuración solo se valida. Mientras se está provisionando, no asumas que el módulo se usará realmente.

#### Logs

Consulta [cómo funciona el logging](/docs/logging) en Caddy. Si tu módulo necesita logs, no uses `log.Print*()` de la librería estándar de Go. En resumen, **no uses el logger global de Go**. Caddy usa logging estructurado y con alto rendimiento con [zap](https://github.com/uber-go/zap).

Para emitir logs, crea un logger en `Provision`:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger es un *zap.Logger
}
```

Luego puedes emitir logs estructurados con niveles usando `g.logger`. Revisa la [godoc de zap](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger).


### Validating

Los módulos que quieran validar su configuración pueden hacerlo implementando (opcionalmente) la interfaz [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=tab#Validator):

```go
// Validate validates that the module has a usable config.
func (g Gizmo) Validate() error {
	// TODO: validate the module's setup
	return nil
}
```

`Validate` debe ser solo de lectura. Se ejecuta después de `Provision()`.


### Interface guards

El comportamiento de un módulo Caddy es implícito porque las interfaces de Go también lo son. Si añades métodos incorrectos o con firma errónea, puedes romper la corrección del módulo. Un error tipográfico puede causar un bug difícil de detectar.

Afortunadamente, puedes agregar una comprobación de compilación sin coste:

```go
var _ InterfaceName = (*YourType)(nil)
```

Reemplaza `InterfaceName` por la interfaz que deba implementar tu módulo y `YourType` por el nombre de tu tipo.

Por ejemplo, un handler HTTP como el servidor de archivos estáticos puede implementar varias interfaces:

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Con esto, el programa no compilará si `*FileServer` no cumple esas interfaces.

Sin interface guards, pueden pasar errores confusos. Por ejemplo, si el módulo debe provisionarse antes de usarse y `Provision()` tiene un error de firma o nombre, nunca se provisionará, produciendo un problema difícil de diagnosticar. Los interface guards ayudan a evitarlo. Normalmente se colocan al final del archivo.


## Módulos anfitrión

Un módulo se vuelve anfitrión cuando carga sus propios módulos invitados. Esto es útil cuando una parte de la funcionalidad se puede implementar de varias formas.

Un módulo anfitrión suele ser una estructura. Normalmente se usan dos campos: uno para el JSON en bruto y otro para el valor procesado:

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

El primer campo (`GadgetRaw` en este ejemplo) contiene la forma JSON sin provisionar del módulo invitado.

El segundo campo (`Gadget`) contiene el valor provisionado final. Como no es visible para usuarios, se excluye del JSON con una etiqueta. También podrías desexportarlo si no se usa en otros paquetes.

### Etiquetas de struct de Caddy

La etiqueta `caddy` del campo en bruto le indica a Caddy el namespace y nombre (ID completo) del módulo a cargar. También se usa para generar documentación.

El formato es simple: `clave1=valor1 clave2=valor2 ...`

Para campos de módulo, la etiqueta se ve así:

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

`namespace=` es obligatorio. Define en qué namespace buscar el módulo.

`inline_key=` solo se usa si el nombre del módulo se encuentra _inline_ dentro del campo; esto significa que el valor es un objeto con una clave (la _inline key_) cuyo valor es el nombre del módulo. Si se omite, el tipo de campo debe ser [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) o `[]caddy.ModuleMap`, donde la clave del mapa es el nombre de módulo.


### Cargar módulos invitados

Para cargar un módulo invitado, llama a [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) durante `Provision`:

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

La llamada a `LoadModule()` recibe un puntero al struct y el nombre del campo como cadena. Puede parecer rara; la ventaja es que existen varias formas de cargar módulos según la forma de configuración, y este método permite a Caddy usar reflexión para elegir la mejor.

Si un módulo invitado debe configurarse explícitamente por el usuario, devuelve error si el campo bruto está vacío o nulo.

Observa cómo el módulo cargado se convierte: `g.Gadget = val.(Gadgeter)`; el valor `val` es un `interface{}` y no muy útil. Pero asumimos que todos los módulos en el namespace declarado (por ejemplo `foo.gizmo.gadgets` del ejemplo) implementan `Gadgeter`, por lo que esta afirmación de tipo es segura.

Si tu módulo anfitrión define un namespace nuevo, documenta ese namespace y sus tipos Go [como hemos hecho aquí](/docs/extending-caddy/namespaces).


## Documentación de módulos

Registra el módulo para que aparezca en la documentación de Caddy y esté disponible en http://caddyserver.com/download. La función de registro está en http://caddyserver.com/account. Crea una cuenta y entra, luego haz clic en “Register package”.


## Ejemplo completo

Imaginemos que queremos crear un módulo handler HTTP. Será un middleware de ejemplo que escribe la IP del visitante en un flujo en cada petición HTTP.

También lo queremos configurable vía Caddyfile, porque la mayoría de usuarios prefieren Caddyfile en configuraciones no automatizadas. Para eso registramos una directiva en el Caddyfile, una especie de directiva que añade un handler a la ruta HTTP. También implementamos la interfaz `caddyfile.Unmarshaler`. Con estas pocas líneas, el módulo se puede configurar desde Caddyfile, por ejemplo: `visitor_ip stdout`.

Aquí está el código del módulo, con comentarios ilustrativos:

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
