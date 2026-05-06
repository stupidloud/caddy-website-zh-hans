---
title: respond (directiva de Caddyfile)
---

# respond

Escribe una respuesta hard-coded/estática al cliente.

Si el cuerpo no está vacío, esta directiva establece la cabecera `Content-Type` si aún no está establecida. El valor por defecto es `text/plain; utf-8`, salvo que el cuerpo sea un objeto o array JSON válido, en cuyo caso se establece `application/json`. Para otros tipos de contenido, establece explícitamente el Content-Type correcto usando la directiva [`header`](/docs/caddyfile/directives/header).


## Sintaxis

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** es el código de estado HTTP a escribir.

  Si es `103` (Early Hints), la respuesta se escribirá sin cuerpo y la cadena de handlers continuará. (Las respuestas HTTP `1xx` son informativas, no finales.)
  
  Valor por defecto: `200`

- **&lt;body&gt;** es el cuerpo de respuesta a escribir.

- **body** es una forma alternativa de proporcionar un cuerpo; es conveniente si tiene varias líneas.

- **close** cerrará la conexión del cliente al servidor tras escribir la respuesta.

Para aclarar, el primer argumento que no sea matcher puede ser un código de estado de 3 dígitos o una cadena de cuerpo de respuesta. Si es un cuerpo, el argumento siguiente puede ser el código de estado.

<aside class="tip">

Responder con un código de error es distinto a devolver un error en la cadena de handlers, lo cual invoca internamente controladores de errores.

</aside>


## Ejemplos

Escribir un estado 200 vacío con cuerpo vacío para todas las comprobaciones de estado, y una respuesta simple para el resto de solicitudes:

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

Escribir una respuesta de error y cerrar la conexión:

<aside class="tip">

Puedes preferir usar en su lugar la directiva [`error`](error), que dispara un error que puede manejarse con [`handle_errors`](handle_errors).

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

Escribir una respuesta HTML, usando [sintaxis heredoc](/docs/caddyfile/concepts#heredocs) para controlar espacios en blanco, y además establecer la cabecera `Content-Type` para que coincida con el cuerpo de respuesta:

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
