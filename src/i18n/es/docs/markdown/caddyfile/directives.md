---
title: Caddyfile Directives
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

# Caddyfile Directives

Las directivas son palabras clave funcionales que aparecen dentro de los [bloques](/docs/caddyfile/concepts#blocks) de un sitio. A veces pueden abrir sus propios bloques y contener *subdirectives*, pero las directivas **no pueden** usarse dentro de otras directivas salvo que se indique lo contrario. Por ejemplo, no puedes usar `basic_auth` dentro de un bloque `file_server`, porque `file_server` no sabe manejar autenticación. Sin embargo, *puedes* usar algunas directivas dentro de bloques de directivas especiales como `handle` y `route`, porque están diseñadas para agrupar directivas de manejadores HTTP.

- [Syntax](#syntax)
- [Directive Order](#directive-order)
- [Sorting Algorithm](#sorting-algorithm)

Las siguientes directivas vienen incluidas en Caddy y se pueden usar en el Caddyfile de HTTP:

<div id="directive-table">

Directive | Description
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Interrumpe la solicitud HTTP
**[acme_server](/docs/caddyfile/directives/acme_server)** | Un servidor ACME integrado
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Aplica HTTP Basic Authentication
**[bind](/docs/caddyfile/directives/bind)** | Personaliza la dirección del socket del servidor
**[encode](/docs/caddyfile/directives/encode)** | Codifica (normalmente comprime) respuestas
**[error](/docs/caddyfile/directives/error)** | Provoca un error
**[file_server](/docs/caddyfile/directives/file_server)** | Sirve archivos desde disco
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Delega la autenticación a un servicio externo
**[fs](/docs/caddyfile/directives/fs)** | Define el sistema de archivos para operaciones de E/S
**[handle](/docs/caddyfile/directives/handle)** | Un grupo de directivas excluyentes mutuamente
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Define rutas para manejar errores
**[handle_path](/docs/caddyfile/directives/handle_path)** | Igual que handle, pero elimina el prefijo de ruta
**[header](/docs/caddyfile/directives/header)** | Define o elimina encabezados de respuesta
**[import](/docs/caddyfile/directives/import)** | Incluye snippets o archivos
**[intercept](/docs/caddyfile/directives/intercept)** | Intercepta respuestas escritas por otros handlers
**[invoke](/docs/caddyfile/directives/invoke)** | Invoca una ruta con nombre
**[log](/docs/caddyfile/directives/log)** | Habilita logging de solicitudes/accesos
**[log_append](/docs/caddyfile/directives/log_append)** | Añade un campo al access log
**[log_skip](/docs/caddyfile/directives/log_skip)** | Omite el registro de acceso para solicitudes coincidentes
**[log_name](/docs/caddyfile/directives/log_name)** | Sobrescribe el nombre(s) del logger de escritura
**[map](/docs/caddyfile/directives/map)** | Mapea un valor de entrada a una o más salidas
**[method](/docs/caddyfile/directives/method)** | Cambia internamente el método HTTP
**[metrics](/docs/caddyfile/directives/metrics)** | Configura el endpoint de exposición de métricas de Prometheus
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Sirve sitios PHP sobre FastCGI
**[push](/docs/caddyfile/directives/push)** | Envía contenido al cliente con HTTP/2 server push
**[redir](/docs/caddyfile/directives/redir)** | Emite una redirección HTTP al cliente
**[request_body](/docs/caddyfile/directives/request_body)** | Manipula el cuerpo de la solicitud
**[request_header](/docs/caddyfile/directives/request_header)** | Manipula encabezados de solicitud
**[respond](/docs/caddyfile/directives/respond)** | Escribe una respuesta predefinida al cliente
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Un proxy inverso potente y extensible
**[rewrite](/docs/caddyfile/directives/rewrite)** | Reescribe la solicitud internamente
**[root](/docs/caddyfile/directives/root)** | Define la ruta al directorio raíz del sitio
**[route](/docs/caddyfile/directives/route)** | Un grupo de directivas tratado literalmente como una sola unidad
**[templates](/docs/caddyfile/directives/templates)** | Ejecuta plantillas en la respuesta
**[tls](/docs/caddyfile/directives/tls)** | Personaliza la configuración de TLS
**[tracing](/docs/caddyfile/directives/tracing)** | Integración con trazado de OpenTelemetry
**[try_files](/docs/caddyfile/directives/try_files)** | Reescribe según la existencia de archivos
**[uri](/docs/caddyfile/directives/uri)** | Manipula el URI
**[vars](/docs/caddyfile/directives/vars)** | Define variables arbitrarias

</div>

## Syntax

La sintaxis de cada directiva se parece a esto:

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

Los `<carets>` indican tokens que se sustituyen por valores reales.

Los`[brackets]` indican parámetros opcionales.

Las elipsis `...` indica continuación, es decir, uno o más parámetros o líneas.

Las *subdirectives* suelen ser opcionales salvo que se indique lo contrario, incluso si no aparecen entre `[brackets]`.


### Matchers

La mayoría, pero no todas, de las directivas aceptan [matcher tokens](/docs/caddyfile/matchers#syntax), que te permiten filtrar solicitudes. Los matcher tokens suelen ser opcionales. Las directivas admiten matchers si en su sintaxis aparece esto:

```caddy-d
[<matcher>]
```

Como todos los matcher tokens funcionan igual, las distintas posibilidades del matcher token no se describen en cada página para reducir duplicidad. En su lugar, consulta la [documentación de matchers](/docs/caddyfile/matchers) para una explicación detallada de la sintaxis.


## Directive order

Muchas directivas manipulan la cadena de handlers HTTP. El orden en que se evalúan esas directivas importa, así que Caddy incluye un orden predeterminado codificado.

Puedes sobrescribir/personalizar este orden usando la [`order` opción global](/docs/caddyfile/options#order) o la directiva [`route`](/docs/caddyfile/directives/route).

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # only in reverse_proxy's handle_response block
request_body

redir

# incoming request manipulation
method
rewrite
uri
try_files

# middleware handlers; some wrap responses
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# special routing & dispatching directives
invoke
handle
handle_path
route

# handlers that typically respond to requests
abort
error
copy_response # only in reverse_proxy's handle_response block
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



## Sorting algorithm

Para facilitar su uso, el adaptador de Caddyfile ordena las directivas con estas reglas:

- Las directivas con nombres distintos se ordenan por su posición en el [orden predeterminado](#directive-order). Ese orden predeterminado puede sobrescribirse con la [`order` opción global](/docs/caddyfile/options). Las directivas de plugins *no tienen* un orden, así que debes usar la opción global [`order`](/docs/caddyfile/options) o la directiva [`route`](/docs/caddyfile/directives/route) para definir uno.

- Las directivas con el mismo nombre se ordenan según sus [matchers](/docs/caddyfile/matchers#syntax).

  - La prioridad más alta corresponde a una directiva con un único [path matcher](/docs/caddyfile/matchers#path-matchers).

    Los path matchers se ordenan por especificidad, de más específico a menos específico.
	
	En general, esto se hace ordenando por la longitud del path matcher. Hay una excepción: si la ruta termina en `*` y las rutas de los dos matchers son idénticas en lo demás, el matcher sin `*` se considera más específico y se ordena antes.

    Por ejemplo:
    - `/foobar` es más específico que `/foo`
    - `/foo` es más específico que `/foo*`
    - `/foo/*` es más específico que `/foo*`

  - Una directiva con cualquier otro matcher se ordena después, en el orden en que aparece en el Caddyfile.

    Esto incluye path matchers con múltiples valores y [named matchers](/docs/caddyfile/matchers#named-matchers).

  - Una directiva sin matcher (es decir, que coincida con todas las solicitudes) se ordena al final.

- La directiva [`vars`](/docs/caddyfile/directives/vars) tiene su orden de *matcher* invertido, porque implica establecer valores que pueden sobrescribirse entre sí, por lo que el matcher más específico debe evaluarse al final.

- El contenido de la directiva [`route`](/docs/caddyfile/directives/route) ignora todas las reglas anteriores y conserva el orden en el que las directivas aparecen dentro.
