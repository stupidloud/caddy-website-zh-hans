---
title: header (Caddyfile directive)
---

# header

Manipula campos de encabezado de respuesta HTTP. Puede establecer, añadir y eliminar valores de encabezados, o realizar reemplazos usando expresiones regulares.

Por defecto, las operaciones de encabezado se ejecutan de inmediato, salvo que se esté eliminando algún encabezado (prefijo `-`) o estableciendo un valor predeterminado (prefijo `?`). En esos casos, las operaciones de encabezado se difieren automáticamente hasta el momento en que se escriben al cliente.

Para manipular encabezados de solicitudes HTTP, usa la directiva [`request_header`](request_header).


## Syntax

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>] {
	# Add
	+<field> <value>

	# Set
	<field> <value>

	# Set with defer
	><field> <value>

	# Delete
	-<field>

	# Replace
	<field> <find> <replace>

	# Replace with defer
	><field> <find> <replace>

	# Default
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** es el nombre del campo de encabezado.

  Sin prefijo, el campo se establece (sobrescribe).

  Usa el prefijo `+` para añadir el campo en lugar de sobrescribirlo si ya existe; los campos de encabezado pueden aparecer más de una vez en una respuesta.

  Usa el prefijo `-` para eliminar el campo. El campo puede usar comodines con prefijo o sufijo `*` para eliminar todos los campos que coincidan.

  Usa el prefijo `?` para establecer un valor predeterminado para el campo. El campo solo se escribe si todavía no existe.

  Usa el prefijo `>` para establecer el campo y habilitar `defer`, como atajo.

- **&lt;value&gt;** es el valor del campo de encabezado al añadir o establecer un campo.

- **&lt;find&gt;** es la expresión regular que se busca. Puedes usar placeholders para una entrada dinámica en el patrón de búsqueda. El lenguaje de expresiones regulares usado es RE2, incluido en Go. Consulta la [referencia de sintaxis de RE2](https://github.com/google/re2/wiki/Syntax) y la [descripción general de sintaxis regexp de Go](https://pkg.go.dev/regexp/syntax).

- **&lt;replace&gt;** es el valor de reemplazo; es obligatorio al realizar una operación buscar y reemplazar. Usa `$1` o `$2`, etc., para referirte a los grupos de captura del patrón de búsqueda. Si el valor de reemplazo es `""`, se elimina el texto coincidente del valor. Consulta la [documentación de Go](https://golang.org/pkg/regexp/#Regexp.Expand) para más detalles.

- **defer** retrasa la ejecución de las operaciones de encabezado hasta que la respuesta se envía al cliente. Esta opción se habilita automáticamente en estas situaciones:
	- Cuando se elimina cualquier campo de encabezado usando `-`.
	- Cuando se establece un valor predeterminado con `?`.
	- Cuando se usa el prefijo `>` en una operación de establecer o reemplazar.
	- Cuando hay una o más condiciones `match` presentes.

- **match** <span id="match"/> es un [response matcher](/docs/caddyfile/response-matchers) embebido. Las operaciones de encabezado se aplican solo a respuestas que cumplan con las condiciones especificadas.

Para realizar múltiples manipulaciones de encabezado, puedes abrir un bloque y especificar una manipulación por línea de la misma forma.

Cuando uses el prefijo `?` para establecer un valor de encabezado predeterminado, se separará automáticamente en su propio handler `header` si estaba en un bloque `header` con varias operaciones de encabezado. [Bajo el capó](/docs/modules/http.handlers.headers#response/require), usar `?` configura un [response matcher](/docs/caddyfile/response-matchers) que se aplica a todo el handler de la directiva, que solo aplica las operaciones de encabezado (como `defer`), pero solo si el campo aún no está definido.


## Examples

Establece un campo de encabezado personalizado en todas las respuestas:

```caddy-d
header Custom-Header "My value"
```

Elimina el campo de encabezado `Hidden`:

```caddy-d
header -Hidden
```

Reemplaza `http://` por `https://` en cualquier encabezado Location:

```caddy-d
header Location http:// https://
```

Establece encabezados de seguridad y privacidad en todas las páginas: (**ADVERTENCIA:** ¡úsalo solo si entiendes las implicaciones!)

```caddy-d
header {
	# disable FLoC tracking
	Permissions-Policy interest-cohort=()

	# enable HSTS
	Strict-Transport-Security max-age=31536000;

	# disable clients from sniffing the media type
	X-Content-Type-Options nosniff

	# clickjacking protection
	X-Frame-Options DENY
}
```

Múltiples directivas header que están pensadas para ser excluyentes entre sí:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Establece una expiración de caché predeterminada si el upstream no define una:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Marca como almacenables en caché durante una hora todas las respuestas exitosas de solicitudes GET:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Evita el caché de respuestas de error en caso de excepción en el servidor upstream:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Marca las respuestas en modo claro como cacheables de forma separada a las de modo oscuro si el upstream admite client hints:
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Evita encabezados CORS demasiado permisivos reemplazando valores comodín por un dominio específico:
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**Nota**: En las operaciones de reemplazo, el valor `<find>` se interpreta como una expresión regular. Para hacer coincidir el carácter `*`, debes escaparlo con una barra invertida como se muestra en el ejemplo anterior.

Alternativamente, puedes usar un [response matcher](/docs/caddyfile/response-matchers) para comparar el valor de un encabezado de forma literal:
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Para sobrescribir la expiración de caché que un proxy upstream estableció para rutas que empiecen por `/no-cache`; es necesario habilitar `defer` para asegurar que el encabezado se establezca _después_ de que el proxy escriba sus encabezados:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Para realizar una actualización diferida de un encabezado `Set-Cookie` y añadir `SameSite=None`; se usa una captura regexp para tomar el valor existente, y `$1` lo vuelve a insertar al inicio con la opción adicional:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
