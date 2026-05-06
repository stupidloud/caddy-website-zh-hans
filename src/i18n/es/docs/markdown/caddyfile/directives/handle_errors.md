---
title: handle_errors (directiva de Caddyfile)
---

# handle_errors

Configura controladores de error.

Cuando los manejadores normales de solicitudes HTTP devuelven un error, el procesamiento normal se detiene y se invocan los controladores de error. Los manejadores de error forman una ruta que es igual que las rutas normales, y pueden hacer todo lo que pueden hacer las rutas normales. Esto permite mucho control y flexibilidad al tratar errores durante las solicitudes HTTP. Por ejemplo, puedes servir páginas de error estáticas, páginas de error templadas o hacer reverse proxy a otro backend para gestionar errores.

La directiva puede repetirse con distintos códigos de estado para tratar errores diferentes de forma distinta. Si no se especifican códigos de estado, coincidirá con cualquier error y actuará como reserva si ningún otro manejador de errores coincide.

El contexto de la solicitud se transmite a las rutas de error, por lo que cualquier valor establecido en el contexto de la solicitud como [site root](root) o [vars](vars) también se conserva en los manejadores de error. Además, [nuevos placeholders](#placeholders) están disponibles al manejar errores.

Ten en cuenta que ciertas directivas, por ejemplo [`reverse_proxy`](reverse_proxy), que pueden escribir una respuesta con un estado HTTP clasificado como error, **no** disparan las rutas de error.

Puedes usar la directiva [`error`](error) para disparar explícitamente un error según tus propias decisiones de enrutado.


## Sintaxis

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** es uno o más códigos de estado HTTP para coincidir contra el error que se está manejando. Los códigos pueden ser números de 3 dígitos, o casos especiales `4xx` o `5xx`, que coinciden con todos los códigos en los rangos `400`-`499` o `500`-`599`, respectivamente. Si no se especifican códigos de estado, se igualará cualquier error y actuará como ruta de reserva si no coincide ningún otro controlador de errores.

- **<directives...>** es una lista de [directivas](/docs/caddyfile/directives) de HTTP handler y [matchers](/docs/caddyfile/matchers), uno por línea.


## Placeholders

Los siguientes placeholders están disponibles al manejar errores. Son [atajos de Caddyfile](/docs/caddyfile/concepts#placeholders) de los placeholders completos que aparecen en [la documentación JSON de las rutas de error de un servidor HTTP](/docs/json/apps/http/servers/errors/#routes).

| Placeholder | Descripción |
|---|---|
| `{err.status_code}` | El código de estado HTTP recomendado |
| `{err.status_text}` | El texto de estado asociado al código recomendado |
| `{err.message}` | El mensaje del error |
| `{err.trace}` | El origen del error |
| `{err.id}` | Un identificador para esta ocurrencia del error |


## Examples

Páginas de error personalizadas basadas en el código de estado (por ejemplo, una página `404.html` para errores `404`). Observa que [`file_server`](file_server) conserva el código de estado HTTP del error cuando se ejecuta dentro de `handle_errors` (suponiendo que hayas definido antes un [site root](root) en tu sitio):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Una sola página de error que usa [`templates`](templates) para escribir un mensaje personalizado:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Si solo quieres páginas de error personalizadas para algunos códigos, puedes comprobar antes si existen los archivos de error con un matcher [`file`](/docs/caddyfile/matchers#file):

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

Hacer reverse proxy a un servidor especializado en gestionar errores HTTP y mejorar tu día 😸:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Simplemente usa [`respond`](respond) para devolver el código y nombre del error:

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Para manejar ciertos códigos de estado de forma diferente:

```caddy-d
handle_errors 404 410 {
	respond "Es un error 404 o 410"
}

handle_errors 5xx {
	respond "Es un error 5xx."
}

handle_errors {
	respond "Es otro error"
}
```

Lo anterior se comporta igual que lo siguiente, que usa un matcher [`expression`](/docs/caddyfile/matchers#expression) sobre los códigos de estado y usa [`handle`](handle) para exclusividad mutua:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "Es un error 404 o 410"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "Es un error 5xx."
	}

	handle {
		respond "Es otro error"
	}
}
```
