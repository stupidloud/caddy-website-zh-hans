---
title: templates (Directiva de Caddyfile)
---

# templates

Ejecuta el cuerpo de la respuesta como un documento de [plantilla](/docs/modules/http.handlers.templates). Las plantillas proporcionan primitivas funcionales para crear páginas dinámicas simples. Entre sus funciones están subsolicitudes HTTP, inclusión de archivos HTML, renderizado de Markdown, análisis de JSON, estructuras de datos básicas, aleatoriedad, tiempo y más.


## Sintaxis

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** son los tipos MIME sobre los que actuará el middleware de templates; cualquier respuesta que no tenga un `Content-Type` elegible no se evaluará como plantilla.

  Valor predeterminado: `text/html text/plain`.

- **between** son los delimitadores de apertura y cierre para las acciones de plantilla. Puedes cambiarlos si interfieren con el resto del documento.

  Valor predeterminado: `{{printf "{{ }}"}}`.

- **root** es la raíz del sitio cuando se usan funciones que acceden al sistema de archivos.

  Por defecto usa la raíz del sitio definida por la directiva [`root`](root), o el directorio de trabajo actual si no está configurada.

- **extensions** permite registrar funciones de plantilla personalizadas proporcionadas por módulos del espacio de nombres `http.handlers.templates.functions.*`.

  Cada subdirectiva dentro del bloque corresponde a un nombre de módulo. Estos módulos pueden agregar funciones personalizadas al mapa de funciones de plantilla, normalmente para implementar componentes reutilizables. Esta función está pensada principalmente para plugins.

La documentación de las funciones de plantilla integradas se encuentra en [el módulo de templates](/docs/modules/http.handlers.templates#docs).



## Ejemplos

Para un ejemplo completo de un sitio que usa plantillas para servir markdown, consulta el código fuente de [este mismo sitio web](https://github.com/caddyserver/website)! En particular, revisa el [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) y [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html).

Habilita templates en un sitio estático:

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

Para servir una respuesta estática simple con una plantilla, asegúrate de establecer `Content-Type`:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Uso de una extensión de plantilla (plugin):

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# Requiere el plugin caddy-hitcounter:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
