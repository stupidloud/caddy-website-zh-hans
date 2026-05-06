---
title: file_server (Directiva de Caddyfile)
---

<script>
ready(function() {
	// Corrige el argumento inline browse
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// Agregamos enlaces a todas las subdirectivas si se encuentra una etiqueta anchor coincidente en la página.
	addLinksToSubdirectives();
});
</script>

# file_server

Un servidor de archivos estáticos que admite sistemas de archivos reales y virtuales. Forma rutas de archivo concatenando la ruta URI de la solicitud a la [ruta raíz del sitio](root).

Por defecto, impone URIs canónicas; esto significa que se emitirán redirecciones HTTP para solicitudes a directorios que no terminen con una barra inclinada (para agregarla), o solicitudes a archivos que tengan barra final (para quitarla). Sin embargo, no se emiten redirecciones si una reescritura interna modifica el último elemento de la ruta (el nombre de archivo).

Lo más habitual es emparejar la directiva `file_server` con la directiva [`root`](root) para establecer la raíz de archivos de todo el sitio. Esta directiva también tiene una subdirectiva `root` (ver abajo) para establecer la raíz solo para este handler (no recomendado). Ten en cuenta que la raíz del sitio no garantiza aislamiento de sandbox: el servidor de archivos evita la traversal por componentes de ruta, pero los enlaces simbólicos dentro de la raíz aún pueden permitir acceso fuera de ella.

Cuando ocurren errores (por ejemplo archivo no encontrado `404`, permiso denegado `403`), se invocarán las rutas de error. Usa la directiva [`handle_errors`](handle_errors) para definir rutas de error y mostrar páginas de error personalizadas.

Cuando se usa `browse`, la salida predeterminada la produce la plantilla HTML. Los clientes pueden solicitar el listado de directorios como JSON o texto plano, usando los encabezados `Accept: application/json` o `Accept: text/plain` respectivamente. La salida JSON puede ser útil para scripts, y la salida en texto plano puede ser útil para uso en terminal humano.


## Sintaxis

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> especifica un sistema de archivos alternativo (quizá virtual). Puede usarse cualquier módulo de Caddy en el namespace `caddy.fs`. Cualquier ruta raíz/prefijo seguirá aplicándose a módulos de sistema de archivos alternativos. Por defecto, se usa el disco local.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 introduce la bandera [`--embed`](https://github.com/caddyserver/xcaddy#custom-builds) para incrustar un árbol de sistema de archivos en la compilación personalizada de Caddy y registra un módulo `fs` llamado `embedded`, lo que permite distribuir tu sitio estático como un ejecutable de Caddy.

- **root** <span id="root"/> establece la ruta de la raíz del sitio. Es similar a la directiva [`root`](root), excepto que solo se aplica a esta instancia de file_server y sobrescribe cualquier otra raíz de sitio que se haya definido. Valor predeterminado: `{http.vars.root}` o el directorio de trabajo actual. Nota: esta subdirectiva solo cambia la raíz para este handler. Para que otras directivas (como [`try_files`](try_files) o [`templates`](templates)) vean la misma raíz del sitio, usa la directiva [`root`](root).

- **hide** <span id="hide"/> es una lista de archivos o carpetas a ocultar; si se solicita, el servidor de archivos fingirá que no existen. Acepta placeholders y patrones glob. Ten en cuenta que estas son rutas de _sistema de archivos_, NO rutas de solicitud. En otras palabras, las rutas relativas usan el directorio de trabajo actual como base, NO la raíz del sitio; y todas las rutas se transforman a su forma absoluta antes de comparar (si es posible). Especificar un nombre de archivo o patrón sin separador de rutas ocultará todos los archivos con ese nombre en cualquier ubicación; de lo contrario, se intenta primero una coincidencia por prefijo de ruta y luego una coincidencia globular. Como esta es una configuración de Caddyfile, por defecto se incluirán los archivos de configuración activos. Las comparaciones de `hide` distinguen mayúsculas y minúsculas; en sistemas de archivos insensibles a mayúsculas, una ruta solicitada con diferente mayúscula/minúscula puede resolver al mismo archivo en disco, por lo que `hide` no debe usarse como frontera de seguridad para rutas sensibles.

- **index** <span id="index"/> es una lista de nombres de archivo para buscar como archivos de índice. Valor predeterminado: `index.html index.txt`

- **browse** <span id="browse"/> habilita listados de archivos para solicitudes a directorios que no tienen un archivo de índice.

  - **<template_file>** <span id="template_file"/> es un archivo de plantilla personalizado opcional para usar en listados de directorios. De forma predeterminada, usa la plantilla que se puede extraer con el comando `caddy file-server export-template`, que imprimirá la plantilla predeterminada en stdout. La plantilla embebida también está disponible [aquí en el código fuente ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html). Las plantillas de listado también pueden usar acciones del [módulo de plantillas estándar](/docs/modules/http.handlers.templates#docs).

  - **reveal_symlinks** <span id="reveal_symlinks"/> habilita mostrar los destinos de los symlinks en listados de directorios. Por defecto, los destinos de symlink están ocultos y solo se muestra el propio archivo de enlace.

  - **sort** <span id="sort"/> cambia el orden predeterminado de los listados de directorio. El primer parámetro es el campo/columna a ordenar: `name`, `namedirfirst`, `size` o `time`. El segundo argumento es una dirección opcional: `asc` o `desc`. Por ejemplo, `sort name desc` ordenará por nombre en orden descendente.

  - **file_limit** <span id="file_limit"/> establece un número máximo de archivos que mostrar en listados de directorios. Predeterminado: `10000`. Si el número de archivos supera este límite, solo se mostrarán los primeros N archivos, donde N es el límite especificado.

- **precompressed** <span id="precompressed"/> es la lista de formatos de codificación para buscar archivos secundarios precomprimidos. Los argumentos son una lista ordenada de formatos de codificación para buscar [archivos sidecar precomprimidos](https://en.wikipedia.org/wiki/Sidecar_file). Los formatos admitidos son `gzip` (`.gz`), `zstd` (`.zst`) y `br` (`.br`). Si se omiten, por defecto son `br zstd gzip` (en ese orden).

  Todas las búsquedas primero verifican la existencia del archivo sin comprimir. Una vez encontrado, Caddy busca sidecars con la extensión de cada formato habilitado. Si se encuentra un archivo sidecar precomprimido, Caddy responderá con ese archivo precomprimido y con el header de respuesta `Content-Encoding` configurado adecuadamente. De lo contrario, Caddy responderá con el archivo sin comprimir normalmente. Si la directiva [`encode`](encode) está habilitada, esta podría comprimir la respuesta al vuelo si no está precomprimida.

- **status** <span id="status"/> es una sobrescritura opcional de código de estado al escribir la respuesta. Es especialmente útil al responder a una solicitud con una [página de error personalizada](handle_errors). Puede ser un código de estado de 3 dígitos, por ejemplo `404`. Se admiten placeholders. De forma predeterminada, el código escrito suele ser `200` o `206` para contenido parcial.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> desactiva el comportamiento predeterminado de redirección (para añadir una barra final si la ruta de la solicitud es un directorio, o quitarla si la ruta de la solicitud es un archivo). Ten en cuenta que, por defecto, la canonicalización no ocurre si el último elemento de la ruta de la solicitud (el nombre de archivo) fue modificado por una reescritura interna, para evitar sobrescribir una reescritura explícita con un comportamiento implícito.

- **pass_thru** <span id="pass_thru"/> habilita el modo pass-thru, que continúa con el siguiente handler HTTP en la ruta si el archivo solicitado no se encuentra, en lugar de lanzar un error `404` (invocando rutas de [`handle_errors`](handle_errors)). Prácticamente, esto solo es útil dentro de un bloque [`route`](route) con otras directivas de handler después de `file_server`, porque esta directiva es efectivamente [la última en orden](/docs/caddyfile/directives#directive-order).


## Ejemplos

Un servidor de archivos estáticos desde el directorio actual:

```caddy-d
file_server
```

Con listados de archivos habilitados:

```caddy-d
file_server browse
```

Sirve solo archivos estáticos dentro de la carpeta `/static`:

```caddy-d
file_server /static/*
```

La directiva `file_server` normalmente se combina con la directiva [`root`](root) para establecer la ruta raíz desde la que se sirven los archivos:

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Si ejecutas Caddy como servicio systemd, leer archivos desde `/home` no funcionará, porque el usuario `caddy` no tiene permiso de ejecución en `/home` (necesario para atravesar directorios). Se recomienda colocar los archivos en `/srv` o `/var/www/html`.

</aside>


Oculta todas las carpetas `.git` y su contenido:

```caddy-d
file_server {
	hide .git
}
```

Si el cliente lo admite (`header Accept-Encoding`) comprueba la existencia de archivos precomprimidos junto al archivo solicitado. Así, si se solicita `/path/to/file`, verifica `/path/to/file.br`, `/path/to/file.zst` y `/path/to/file.gz` en ese orden y sirve el primer archivo disponible con el `Content-Encoding` correspondiente:

```caddy-d
file_server {
	precompressed
}
```
