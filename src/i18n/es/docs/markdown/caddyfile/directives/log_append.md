---
title: log_append (directiva de Caddyfile)
---

# log_append

Añade un campo al log de acceso para la solicitud actual.

Esto debe usarse junto con la directiva [`log`](log), que es necesaria para habilitar el logging de acceso en primer lugar.

El valor puede ser una cadena estática, o un [placeholder](/docs/caddyfile/concepts#placeholders) que se reemplazará por el valor del placeholder en el momento de la solicitud.


## Sintaxis

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

Por defecto, el campo de log se añade al subir por la cadena middleware (es decir, "tarde"), después de que todos los handlers siguientes hayan completado (por ejemplo, después de handlers como [`reverse_proxy`](reverse_proxy), [`respond`](respond) o [`file_server`](file_server), que escriben una respuesta), por lo que captura el estado final de la solicitud y la respuesta.

Si se usa `<` como prefijo de la clave, se marca como "temprano", lo que significa que el campo de log se añadirá a los logs _antes_ de llamar al siguiente handler de la cadena, de modo que la solicitud se pueda leer antes de que sea modificada por handlers posteriores.

Solo para depuración (no para uso en producción), el handler tiene un manejo especializado cuando el valor es uno de estos placeholders: `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}` o `{http.response.body_base64}`. Si se usa un placeholder del cuerpo de la solicitud, el modo "temprano" se habilita implícitamente y el cuerpo de la solicitud se almacenará en buffer. Si se usa un placeholder del cuerpo de la respuesta, se habilita el buffering de la respuesta para capturar el cuerpo de la respuesta y el campo se añade al log "tarde", mientras se escribe la respuesta.


## Ejemplos

Mostrar en los logs el área del sitio desde la que se sirve la solicitud, ya sea `static` o `dynamic`:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

Mostrar en los logs cuál upstream de reverse proxy se usó realmente (ya sea `node1`, `node2` o `node3`) y
el tiempo empleado en proxys al upstream en milisegundos, así como el tiempo que tardó el upstream en escribir la cabecera de la respuesta:

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Se puede agregar un campo al log "temprano" anteponiendo `<` a la clave. Esto permite capturar el estado de la solicitud antes de que sea modificada por handlers posteriores. Por ejemplo, para registrar la ruta original de solicitud antes de que se reescriba (aunque es un ejemplo forzado, ya que la ruta original ya se registra de todos modos, pero ayuda a ilustrar el punto):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

Para depuración, añade los cuerpos de solicitud y respuesta a los logs (no para producción, ya que esto afecta al rendimiento y hace los logs muy ruidosos). Si esperas que los cuerpos sean datos binarios con caracteres no imprimibles, puedes usar las variantes base64 de los placeholders (por ejemplo, `{http.request.body_base64}` y `{http.response.body_base64}`), que serán más fáciles de copiar y revisar:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
