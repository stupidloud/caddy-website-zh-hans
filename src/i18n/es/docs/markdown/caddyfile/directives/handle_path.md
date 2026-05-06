---
title: handle_path (Directiva de Caddyfile)
---

<script>
ready(function() {
	// Añade un enlace a [<path_matcher>] como caso especial para esta directiva.
	// El texto del matcher incluye caracteres <> que se analizan como HTML,
	// así que debemos usar text() para cambiar el texto del enlace.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Token de matcher">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

Funciona igual que la directiva [`handle`](handle), pero usa implícitamente [`uri strip_prefix`](uri) para quitar el prefijo de ruta que coincide.

Manejar una solicitud que coincide con una ruta determinada (mientras se elimina esa ruta del URI de la solicitud) es un caso de uso lo suficientemente común como para tener su propia directiva por conveniencia.


## Sintaxis

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** es una lista de directivas del manejador HTTP o bloques de directivas, una por línea, igual que se usaría fuera de un bloque `handle_path`.

Solo se acepta un único [path matcher](/docs/caddyfile/matchers#path-matchers), y es obligatorio; no puedes usar matchers con nombre con `handle_path`.

## Ejemplos

Esta configuración:

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 es, en esencia, la misma que esta 👇, pero la forma `handle_path` 👆 es algo más breve.

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

Un ejemplo completo de Caddyfile, donde `handle_path` y `handle` son excluyentes; pero, ten en cuenta el [problema de subcarpeta <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# Sirve tu API y elimina el prefijo /api
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Sirve tu sitio estático
	handle {
		root /srv
		file_server
	}
}
```
