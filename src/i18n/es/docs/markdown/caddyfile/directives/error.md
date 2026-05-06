---
title: error (directiva de Caddyfile)
---

# error

Dispara un error en la cadena de handlers HTTP, con un mensaje opcional y un código de estado HTTP recomendado.

Este handler no escribe una respuesta. En su lugar, está pensado para combinarse con la directiva [`handle_errors`](handle_errors) para ejecutar tu lógica personalizada de manejo de errores.


## Sintaxis

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** es el código de estado HTTP que se enviará. El valor por defecto es `500`.
- **&lt;message&gt;** es el mensaje de error. El valor por defecto no incluye mensaje de error.
- **message** es una forma alternativa de proporcionar un mensaje de error; resulta conveniente si tiene varias líneas.

Para aclarar, el primer argumento que no sea matcher puede ser un código de estado de 3 dígitos o una cadena de mensaje de error. Si es un mensaje de error, el siguiente argumento puede ser el código de estado.


## Ejemplos

Disparar un error en ciertas rutas de solicitud y usar [`handle_errors`](handle_errors) para escribir una respuesta:

```caddy
example.com {
	root /srv

	# Disparar errores para ciertas rutas
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Manejar el error sirviendo una página HTML 
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
