---
title: try_files (Directiva de Caddyfile)
---

# try_files

Reescribe la ruta URI de la solicitud al primer archivo existente de la lista dentro de la raíz del sitio. Si ningún archivo coincide, no se realiza ningún rewrite.


## Sintaxis

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** es la lista de archivos a probar. La ruta URI se reescribirá al primer archivo que exista.

  Para que coincidan directorios, agrega una barra `/` al final de la ruta. Todas las rutas de archivo son relativas a la [raíz](root) del sitio, y se expandirán los [patrones glob](https://pkg.go.dev/path/filepath#Match).

  Cada argumento también puede contener una cadena de consulta; en ese caso la query también se cambiará si coincide con ese archivo en particular.

  Si `try_policy` es `first_exist` (valor predeterminado), el último elemento de la lista puede ser un número prefijado por `=` (por ejemplo `=404`), que como fallback emitirá un error con ese código; el error puede capturarse y manejarse con [`handle_errors`](handle_errors).

- **policy** es la política para elegir el archivo entre la lista.

  Valor predeterminado: `first_exist`


## Forma expandida

La directiva `try_files` es básicamente un atajo para:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

Ten en cuenta que esta directiva no acepta un token matcher. Si necesitas lógica de coincidencia más compleja, usa la forma expandida anterior como base.

Consulta el [matcher `file`](/docs/caddyfile/matchers#file) para más detalles.


## Ejemplos

Si la solicitud no coincide con ningún archivo estático, reescribe a tu punto de entrada PHP de índice/ruteador:

```caddy-d
try_files {path} /index.php
```

Lo mismo, pero añadiendo la ruta original a la query string (requerido por algunas aplicaciones PHP heredadas):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

Lo mismo, pero también para directorios:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Intentar reescribir a un archivo o directorio si existe; de lo contrario emitir un error 404 (que puede capturarse y manejarse con [`handle_errors`](handle_errors)):

```caddy-d
try_files {path} {path}/ =404
```

Elegir la versión de archivo estático desplegada más recientemente (por ejemplo, servir `index.be331df.html` cuando se solicite `index.html`):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
