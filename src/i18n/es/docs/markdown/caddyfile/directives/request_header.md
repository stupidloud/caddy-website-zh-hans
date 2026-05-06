---
title: request_header (directiva de Caddyfile)
---

# request_header

Manipula campos de cabecera HTTP en la solicitud. Puede establecer, agregar y eliminar valores de cabecera, o realizar reemplazos usando expresiones regulares.

Si pretendes manipular cabeceras para proxy, usa en su lugar la [subdirectiva `header_up`](/docs/caddyfile/directives/reverse_proxy#header_up) de `reverse_proxy`, ya que esas manipulaciones son compatibles con proxy.

Para manipular cabeceras de respuesta HTTP, puedes usar la directiva [`header`](header).


## Sintaxis

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** es el nombre del campo de cabecera.

  Sin prefijo, el campo se establece (sobrescribe).

  Con prefijo `+`, se agrega el campo en lugar de sobrescribir (setear) si ya existe; los campos de cabecera pueden aparecer más de una vez en una solicitud.

  Con prefijo `-`, se elimina el campo. El campo puede usar prefijo o sufijo `*` comodines para eliminar todos los campos que coincidan.

- **&lt;value&gt;** es el valor del campo de cabecera, si se agrega o establece un campo.

- **&lt;find&gt;** es la subcadena o expresión regular que buscar.

- **&lt;replace&gt;** es el valor de reemplazo; obligatorio si se realiza una búsqueda y reemplazo.


## Ejemplos

Eliminar el header Referer de la solicitud:

```caddy-d
request_header -Referer
```

Eliminar todas las cabeceras que contengan un guion bajo desde la solicitud:

```caddy-d
request_header -*_*
```
