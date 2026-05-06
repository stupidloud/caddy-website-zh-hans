---
title: push (Directiva de Caddyfile)
---

# push

Configura el servidor para enviar recursos de forma preventiva al cliente mediante HTTP/2 server push.

Los recursos pueden vincularse para server push especificando los encabezados Link de la respuesta. Esta directiva enviará automáticamente los recursos descritos por encabezados Link upstream en estos formatos:

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

donde `<resource>` comienza con una barra `/` (es decir, es una ruta URI con el mismo host). Solo se pueden enviar recursos del mismo host. Si un recurso enlazado es externo o tiene el atributo `nopush`, no se enviará.

Por defecto, las solicitudes push incluirán algunos encabezados que se consideran seguros para copiar desde la solicitud original:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

se asume que muchas solicitudes fallarían sin estos encabezados; por eso no es necesario configurarlos manualmente.

Las solicitudes push se virtualizan internamente, por lo que son muy ligeras.


## Sintaxis

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** es la ruta URI de destino que se debe hacer push. Si se usa dentro del bloque, opcionalmente puede ir precedido por el método (GET o POST; GET es el valor predeterminado).
- **&lt;headers&gt;** manipula los encabezados de la solicitud push usando la misma sintaxis que la directiva [`header`](/docs/caddyfile/directives/header). Algunos encabezados se trasladan por defecto y no necesitan ser configurados explícitamente (ver arriba).


## Ejemplos

Enviar por push cualquier recurso descrito por encabezados `Link` en la respuesta:

```caddy-d
push
```

Lo mismo, pero también hacer push de `/resources/style.css` para todas las solicitudes:

```caddy-d
push * /resources/style.css
```

Hacer push de `/foo.jpg` solo cuando el cliente solicita `/foo.html`:

```caddy-d
push /foo.html /foo.jpg
```
