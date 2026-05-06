---
title: import (Directiva de Caddyfile)
---

# import

Incluye un [fragmento](/docs/caddyfile/concepts#snippets) o archivo, reemplazando esta directiva con el contenido del fragmento o archivo.

Esta directiva es un caso especial: se evalúa antes de que se analice la estructura y puede aparecer en cualquier lugar del Caddyfile.

## Sintaxis

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** es el nombre de archivo, patrón glob o nombre del [fragmento](/docs/caddyfile/concepts#snippets) a incluir. Su contenido reemplaza esta línea como si el contenido del archivo estuviera aquí desde el inicio.

  Si no se encuentra un archivo específico, se produce un error, pero un patrón glob vacío no es un error.

  Si se importa un archivo específico, se emitirá una advertencia si el archivo está vacío.

  Si el patrón es un nombre de archivo o un glob, siempre es relativo al archivo donde aparece `import`.

  Si se usa un patrón glob `*` como segmento final de la ruta, se ignoran los archivos ocultos (por ejemplo, archivos que comienzan con `.`). Para importar archivos ocultos, usa `.*` como segmento final.
- **&lt;args...&gt;** es una lista opcional de argumentos para pasar a los tokens importados. Este marcador de posición es un caso especial y se evalúa en tiempo de análisis del Caddyfile, no en tiempo de ejecución. Pueden usarse de varias formas, de forma similar a la [sintaxis de slices de Go](https://gobyexample.com/slices):
  - `{args[n]}` donde `n` es el índice posicional con base 0 del parámetro
  - `{args[:]}` donde se insertan todos los argumentos
  - `{args[:m]}` donde se insertan los argumentos antes de `m`
  - `{args[n:]}` donde se insertan los argumentos desde `n`
  - `{args[n:m]}` donde se insertan los argumentos en el rango entre `n` y `m`

  Para las formas que insertan muchos tokens, el marcador debe ser un [token](/docs/caddyfile/concepts#tokens-and-quotes) por sí solo; no puede formar parte de otro token. En otras palabras, debe tener espacios alrededor y no puede estar entre comillas.

  Ten en cuenta que antes de v2.7.0, la sintaxis era `{args.N}`, pero esta forma fue obsoleta en favor de la sintaxis más flexible anterior.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** es un bloque opcional para pasar a los tokens importados. Este marcador es un caso especial y se evalúa recursivamente en tiempo de análisis del Caddyfile, no en tiempo de ejecución. Puede usarse en dos formas:
  - `{block}` donde el contenido del bloque proporcionado se sustituirá por el marcador
  - `{blocks.key}` donde `key` es el primer token de un parámetro dentro del bloque proporcionado


## Ejemplos

Importa todos los archivos en una carpeta `sites-enabled` adyacente (excepto archivos ocultos):

```caddy-d
import sites-enabled/*
```

Importa un fragmento que configura encabezados CORS usando un argumento de importación:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Importa un fragmento que toma una lista de upstreams de proxy como argumentos:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Importa un fragmento que crea un proxy con una regla de reescritura de prefijo como primer argumento:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Importa un fragmento que responde con un mensaje y tipo de contenido "hello world" configurables:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Importa un fragmento que proporciona opciones extensibles para un reverse proxy:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Importa un fragmento que sirve cualquier conjunto de directivas, pero con un middleware pre-cargado:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
