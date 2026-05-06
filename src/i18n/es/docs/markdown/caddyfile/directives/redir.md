---
title: redir (Directiva de Caddyfile)
---

# redir

Envía un redireccionamiento HTTP al cliente.

Esta directiva implica que una solicitud que coincide debe rechazarse tal como está y que el cliente debe probar de nuevo en una URL diferente. Por esa razón, su [orden de ejecución](/docs/caddyfile/directives#directive-order) es muy temprano.


## Sintaxis

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** es la ubicación de destino. Pasa al [`header Location` de la respuesta <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location).

- **&lt;code&gt;** es el código de estado HTTP que se usará para el redireccionamiento. Puede ser:

	- Un entero positivo en el rango `3xx`, o `401`
	
	- `temporary` para una redirección temporal (`302`, este es el valor por defecto)
	
	- `permanent` para una redirección permanente (`301`)
	
	- `html` para usar un documento HTML para realizar la redirección (útil para redirigir navegadores pero no clientes API)
	
	- Un marcador de posición con un valor de código de estado


## Ejemplos

Redirige todas las solicitudes a `https://example.com`:

```caddy
www.example.com {
	redir https://example.com
}
```

Lo mismo, pero conservando la URI existente al añadir el [`placeholder` `{uri}`](/docs/caddyfile/concepts#placeholders):

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

Lo mismo, pero permanente:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Redirige tu antigua página `/about-us` a tu nueva página `/about`:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
