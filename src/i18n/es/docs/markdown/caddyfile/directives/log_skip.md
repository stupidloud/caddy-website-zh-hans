---
title: log_skip (directiva de Caddyfile)
---

# log_skip

Omite el registro de acceso para las solicitudes que coincidan.

Esto debe usarse junto con la directiva [`log`](log) para omitir el registro de solicitudes que no son relevantes para tus necesidades.

Antes de v2.8.0, esta directiva se llamaba `skip_log`, pero se renombró para mantener la coherencia con otras directivas.


## Sintaxis

```caddy-d
log_skip [<matcher>]
```


## Ejemplos

Omitir el registro de acceso para archivos estáticos almacenados en una subruta:

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```

Omitir el registro de acceso para solicitudes que coincidan con un patrón; en este caso, para archivos con extensiones particulares:

```caddy-d
@skip path_regexp \\.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```

No se necesita el matcher si se encuentra dentro de una ruta que ya está dentro de un matcher. Por ejemplo, con un handle para un servidor de archivos para una subruta concreta:

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
