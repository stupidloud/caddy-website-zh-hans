---
title: fs (directiva de Caddyfile)
---

# fs

Configura qué sistema de archivos debe usarse para realizar operaciones de E/S de archivos.

Esto te permite conectarte a un sistema de archivos remoto en la nube, o a una base de datos con una interfaz de tipo archivo, o incluso leer archivos integrados dentro del binario de Caddy.

Primero debes declarar un nombre de sistema de archivos usando la [`opción global filesystem`](/docs/caddyfile/options#filesystem), luego puedes usar esta directiva para indicar qué sistema de archivos usar.

Esta directiva suele usarse junto con la [`directiva file_server`](file_server) para servir archivos estáticos, o con la [`directiva try_files`](try_files) para hacer reescrituras según la existencia de archivos. Normalmente también se usa con la [`directiva root`](root) para establecer la ruta raíz dentro del sistema de archivos.


## Sintaxis

```caddy-d
fs [<matcher>] <filesystem>
```

## Ejemplos

Usando un sistema de archivos llamado `foo`, usando un módulo imaginario llamado `custom` que podría requerir autenticación:

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

Para servir solo imágenes desde el sistema de archivos `foo`, y el resto desde el sistema de archivos por defecto:

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
