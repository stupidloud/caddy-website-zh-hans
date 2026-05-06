---
title: log_name (directiva de Caddyfile)
---

# log_name

Sobrescribe el nombre del logger que se usará para una solicitud al escribir logs de acceso con la directiva [`log`](log).

Esta directiva es útil cuando quieres registrar solicitudes en diferentes archivos según alguna condición, como la ruta o el método de la solicitud.

Se pueden especificar más de un nombre de logger, de modo que el log de la solicitud se envíe a más de un logger coincidente.

Esto suele ir junto con la opción [`no_hostname`](log#no_hostname) de la directiva `log`, que evita que el logger se asocie con cualquiera de los hostnames del bloque del sitio, de modo que solo las solicitudes que establecen `log_name` envíen logs a ese logger.


## Sintaxis

```caddy-d
log_name [<matcher>] <names...>
```


## Ejemplos

Puede que quieras registrar solicitudes en archivos diferentes; por ejemplo, puede que quieras registrar las comprobaciones de salud (`health checks`) en un archivo separado del log principal de acceso.

Usar `no_hostname` en un `log` evita que el logger se asocie con ninguno de los hostnames del bloque del sitio (es decir, `localhost` aquí), de modo que solo las solicitudes que tengan `log_name` configurado con el nombre de ese logger reciban logs.

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
