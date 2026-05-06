---
title: uri (Directiva de Caddyfile)
---

# uri

Manipula la URI de la solicitud. Puede quitar prefijos/sufijos de ruta o reemplazar subcadenas en la URI completa.

Esta directiva se diferencia de [`rewrite`](rewrite) en que `uri` cambia la URI de forma **diferenciable**, en lugar de reiniciarla a algo completamente diferente como hace `rewrite`. Mientras que `rewrite` se trata especialmente como una redirección interna, `uri` es solo otro middleware.


## Sintaxis

Se admiten varias operaciones diferentes:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

El primer argumento (que no es matcher) especifica la operación:

- **strip_prefix** elimina el prefijo de la ruta.

- **strip_suffix** elimina el sufijo de la ruta.

- **replace** realiza un reemplazo de subcadenas en toda la URI.

	- **&lt;target&gt;** es el prefijo, sufijo o cadena/expresión regular de búsqueda. Si es un prefijo, se puede omitir la barra inicial, ya que las rutas siempre comienzan con una barra.

	- **&lt;replacement&gt;** es la cadena de reemplazo. Admite grupos de captura con sintaxis `$name` o `${name}`, o con un número como índice, como `$1`. Consulta la [documentación de Go](https://golang.org/pkg/regexp/#Regexp.Expand) para más detalles. Si el valor de reemplazo es `""`, entonces el texto coincidente se elimina del valor.

	- **&lt;limit&gt;** es un límite opcional para el número máximo de reemplazos.

- **path_regexp** realiza una sustitución mediante expresión regular en la porción de ruta de la URI.

	- **&lt;target&gt;** es el prefijo, sufijo o cadena/expresión regular de búsqueda. Si es un prefijo, se puede omitir la barra inicial, ya que las rutas siempre empiezan con una barra.

	- **&lt;replacement&gt;** es la cadena de reemplazo. Admite grupos de captura con sintaxis `$name` o `${name}`, o con un número como índice, como `$1`. Consulta la [documentación de Go](https://golang.org/pkg/regexp/#Regexp.Expand) para más detalles. Si el valor de reemplazo es `""`, entonces el texto coincidente se elimina del valor.

- **query** realiza manipulaciones en la consulta URI, con el modo dependiendo del prefijo del nombre de parámetro o del número de argumentos. Un bloque puede usarse para especificar múltiples operaciones a la vez, agrupadas y ejecutadas en este orden: rename 🡒 set 🡒 append 🡒 replace 🡒 delete.

	- Sin prefijo, el parámetro se establece con el valor dado en la consulta.
	
	  Por ejemplo, `uri query foo bar` establece el valor del parámetro `foo` en `bar`.

	- Con prefijo `-` se elimina el parámetro de la consulta.
	
	  Por ejemplo, `uri query -foo` elimina el parámetro `foo` de la consulta.

	- Con prefijo `+` se agrega un parámetro a la consulta con el valor indicado. Esto **no** sobrescribe un parámetro existente con el mismo nombre (omite el `+` para sobrescribirlo).
	
	  Por ejemplo, `uri query +foo bar` añadirá `foo=bar` a la consulta.

	- Un parámetro con `>` como infijo renombrará el parámetro al valor que esté después de `>`. 
	
	  Por ejemplo, `uri query foo>bar` renombra el parámetro `foo` a `bar`.

	- Con tres argumentos se realiza un reemplazo de expresión regular del valor de consulta, donde el primer argumento es el nombre del parámetro, el segundo el valor de búsqueda y el tercero el reemplazo. El primer argumento (nombre del parámetro) puede ser `*` para realizar el reemplazo en todos los parámetros de consulta.
	
	  Admite grupos de captura con la sintaxis `$name` o `${name}`, o con un número como índice, como `$1`. Consulta la [documentación de Go](https://golang.org/pkg/regexp/#Regexp.Expand) para más detalles. Si el valor de reemplazo es `""`, entonces el texto coincidente se elimina del valor.
	
	  Por ejemplo, `uri query foo ^(ba)r $1z` reemplazaría el valor del parámetro `foo`, donde el valor empezaba con `bar`, con un resultado `baz`.

Las mutaciones de URI ocurren en la forma normalizada o sin escapar de la URI. Sin embargo, se pueden usar secuencias de escape en los patrones de prefijo o sufijo para coincidir solo con esos escapes literales en esas posiciones de la ruta de la solicitud. Por ejemplo, `uri strip_prefix /a/b` reescribirá tanto `/a/b/c` como `/a%2Fb/c` como `/c`; y `uri strip_prefix /a%2Fb` reescribirá `/a%2Fb/c` como `/c`, pero no coincidirá con `/a/b/c`.

La ruta de la URI limpia los puntos de recorrido de directorio antes de las modificaciones. Además, las barras dobles consecutivas (como `//`) se combinan salvo que `<target>` también contenga varias barras.

## Directivas similares

Otras directivas también pueden manipular la URI de la solicitud.

- [`rewrite`](rewrite) cambia toda la ruta y consulta a un nuevo valor en lugar de modificar solo parte del valor.

- [`handle_path`](handle_path) hace lo mismo que [`handle`](handle), pero elimina un prefijo de la solicitud antes de ejecutar sus handlers. Puede usarse en lugar de `uri strip_prefix` para eliminar una línea extra de configuración en muchos casos.


## Ejemplos

Eliminar `/api` del inicio de todas las rutas de solicitud:

```caddy-d
uri strip_prefix /api
```

Eliminar `.php` del final de todas las rutas de solicitud:

```caddy-d
uri strip_suffix .php
```

Reemplazar `/docs/` por `/v1/docs/` en cualquier URI de solicitud:

```caddy-d
uri replace /docs/ /v1/docs/
```

Colapsar todas las barras repetidas en la ruta de solicitud (pero no en la consulta de la solicitud) a una sola barra:

```caddy-d
uri path_regexp /{2,} /
```

Establecer el valor del parámetro de consulta `foo` a `bar`:

```caddy-d
uri query foo bar
```

Eliminar el parámetro `foo` de la consulta:

```caddy-d
uri query -foo
```

Renombrar el parámetro de consulta `foo` a `bar`:

```caddy-d
uri query foo>bar
```

Agregar el parámetro `bar` a la consulta:

```caddy-d
uri query +foo bar
```

Reemplazar el valor del parámetro `foo` cuando el valor empiece con `bar` por `baz`:

```caddy-d
uri query foo ^(ba)r $1z
```

Realizar múltiples operaciones de consulta al mismo tiempo:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
