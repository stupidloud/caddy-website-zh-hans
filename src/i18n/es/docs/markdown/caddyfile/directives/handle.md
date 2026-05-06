---
title: handle (Caddyfile directive)
---

# handle

Evalúa un grupo de directivas de forma excluyente entre sí frente a otros bloques `handle` en el mismo nivel de anidamiento.

En otras palabras, cuando aparecen varias directivas `handle` en secuencia, solo se evaluará el primer bloque `handle` que *coincida*. Un `handle` sin matcher actúa como una ruta de reserva.

Las directivas `handle` se ordenan según el [algoritmo de orden de directivas](/docs/caddyfile/directives#sorting-algorithm) por sus matchers. La directiva [`handle_path`](handle_path) es un caso especial y se ordena con la misma prioridad que un `handle` con un matcher de ruta.

Los bloques handle pueden anidarse si es necesario. Solo se pueden usar directivas de handler HTTP dentro de ellos.

## Syntax

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** es una lista de directivas o bloques de directivas de handler HTTP, una por línea, igual que se usaría fuera de un bloque `handle`.


## Similar directives

Existen otras directivas que pueden envolver directivas de handler HTTP, pero cada una se usa según el comportamiento que quieras expresar:

- [`handle_path`](handle_path) hace lo mismo que `handle`, pero elimina un prefijo de la solicitud antes de ejecutar sus handlers.

- [`handle_errors`](handle_errors) es como `handle`, pero solo se invoca cuando Caddy encuentra un error durante el manejo de la solicitud.

- [`route`](route) envuelve otras directivas como lo hace `handle`, pero con dos diferencias:
  1. los bloques route no son excluyentes entre sí,
  2. las directivas dentro de un route no se [reordenan](/docs/caddyfile/directives#directive-order), lo que da más control cuando es necesario.



## Examples

Maneja las solicitudes en `/foo/` con el servidor de archivos estáticos y el resto con el proxy inverso:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

Puedes combinar `handle` y [`handle_path`](handle_path) en el mismo sitio, y seguirán siendo excluyentes entre sí:

```caddy
example.com {
	handle_path /foo/* {
		# La ruta elimina el prefijo "/foo"
	}

	handle /bar/* {
		# La ruta conserva "/bar"
	}
}
```

Puedes anidar bloques `handle` para crear lógica de enrutado más compleja:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Este bloque solo coincide con rutas bajo /foo/bar
		}

		handle {
			# Este bloque coincide con todo lo demás bajo /foo/
		}
	}

	handle {
		# Este bloque coincide con todo lo demás (actúa como fallback)
	}
}
```
