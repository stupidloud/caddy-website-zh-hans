---
title: route (Directiva de Caddyfile)
---

# route

Evalúa un grupo de directivas literalmente y como una sola unidad.

Las directivas contenidas en un bloque `route` no se [reordenarán internamente](/docs/caddyfile/directives#directive-order). Solo se pueden usar en un bloque route las directivas de manejador HTTP (las que agregan handlers o middleware a la cadena).

Esta directiva es un caso especial en el que sus subdirectivas también son directivas regulares.


## Sintaxis

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** es una lista de directivas o bloques de directivas, una por línea, igual que fuera de un bloque `route`; con la diferencia de que estas directivas no se reordenarán. Solo se pueden usar directivas de manejador HTTP.



## Utilidad

La directiva `route` es útil en algunos casos de uso avanzados o borde para tomar control absoluto sobre partes de la cadena de handlers HTTP.

Debido a que el orden de evaluación del middleware HTTP es importante, el Caddyfile normalmente reordena las directivas después del análisis para que sea más fácil de usar; así no tienes que preocuparte por el orden en que escribas las cosas.

Aunque el [orden integrado](/docs/caddyfile/directives#directive-order) es compatible con la mayoría de sitios, a veces necesitas controlar manualmente el orden, ya sea para todo el sitio o solo para una parte. Para eso sirve la directiva `route`.

Para ilustrar, considera el caso de dos handlers terminales: [`redir`](redir) y [`file_server`](file_server). Ambos escriben la respuesta al cliente y no llaman al siguiente handler en la cadena, por lo que solo uno se ejecutará para una petición determinada. Entonces, ¿cuál va primero? Normalmente, `redir` se ejecuta antes que `file_server` porque normalmente querrías emitir una redirección solo en casos específicos y servir archivos en el caso general.

Sin embargo, puede haber ocasiones en que el primer handler (`file_server`) tenga un matcher más específico que el segundo (`redir`). En otras palabras, quieres redirigir en el caso general y servir solo un archivo concreto.

Así que podrías probar un Caddyfile como este (pero no funcionará como esperas):

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

El problema es que, después de la [ordenación de directivas](/docs/caddyfile/directives#sorting-algorithm), `redir` queda antes que `file_server`.

Pero en este caso el matcher de `redir` (un [`*`](/docs/caddyfile/matchers#wildcard-matchers) implícito) es un superconjunto del matcher de `file_server` (`*` es un superconjunto de `/specific.html`).

Por suerte, la solución es sencilla: solo envuelve esas dos directivas en un bloque `route`, para garantizar que `file_server` se ejecute antes de `redir`:

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

Otra forma de hacerlo es hacer que los dos matchers sean excluyentes mutuamente, pero esto puede complicarse rápidamente si hay más de una o dos condiciones. Con la directiva `route`, la exclusividad mutua de los dos handlers es implícita porque ambos son handlers terminales.

</aside>

Ahora `file_server` se encadenará antes de `redir` porque el orden se toma literalmente.


## Directivas similares

Hay otras directivas que pueden envolver directivas de handlers HTTP, pero cada una tiene su uso según el comportamiento que quieras lograr:

- [`handle`](handle) envuelve otras directivas como lo hace `route`, pero con dos diferencias: 1) los bloques handle son mutuamente excluyentes entre sí, y 2) las directivas dentro de un handle se [reordenan](/docs/caddyfile/directives#directive-order) normalmente.

- [`handle_path`](handle_path) hace lo mismo que `handle`, pero elimina un prefijo de la solicitud antes de ejecutar sus handlers.

- [`handle_errors`](handle_errors) es como `handle`, pero solo se invoca cuando Caddy encuentra un error durante el manejo de la solicitud.


## Ejemplos

Proxiar solicitudes a `/api` tal como están, y reescribir todas las demás solicitudes según si coinciden con un archivo en disco, o bien `/index.html`. Luego se sirve ese archivo.

Dado que [`try_files`](try_files) tiene un orden de directiva más alto que [`reverse_proxy`](reverse_proxy), normalmente se ordenaría antes y se ejecutaría primero; esto haría que todas las solicitudes de API se reescriban a `/index.html` y fallaran al coincidir con `/api*`, por lo que ninguna sería proxificada y en su lugar terminaría en `404` desde [`file_server`](file_server). Encerrar todo en `route` garantiza que `reverse_proxy` siempre se ejecute primero, antes de reescribir la solicitud.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Esta no es la única solución a este problema. También podrías usar un par de bloques [`handle`](handle), con el primero emparejando `/api*` hacia `reverse_proxy`, y el segundo actuando como fallback y sirviendo los archivos. Consulta [este ejemplo](/docs/caddyfile/patterns#single-page-apps-spas) de una SPA.

</aside>
