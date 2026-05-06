---
title: rewrite (directiva de Caddyfile)
---

# rewrite

Reescribe internamente el URI de la solicitud.

Una reescritura cambia una parte o la totalidad del URI de la solicitud. Ten en cuenta que el URI no incluye esquema ni autoridad (host y puerto), y los clientes normalmente no envían fragmentos. Por eso, esta directiva se usa sobre todo para manipulación de **path** y **query string**.

La directiva `rewrite` implica la intención de aceptar la solicitud, pero con modificaciones.

Es mutuamente exclusiva con otras directivas `rewrite` en el mismo bloque, por lo que es seguro definir reescrituras que de otro modo podrían encadenarse, ya que solo se ejecutará la primera que coincida.

Un [request matcher](/docs/caddyfile/matchers) que coincida con una solicitud antes de `rewrite` puede no coincidir con la misma solicitud después de la reescritura. Si quieres que tu `rewrite` comparta ruta con otros handlers, usa las directivas [`route`](route) o [`handle`](handle).


## Sintaxis

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** es el URI al que reescribir la solicitud. Solo se operará sobre los componentes del URI (path o query string) especificados en la reescritura. La ruta del URI es cualquier substring que venga antes de `?`. Si se omite `?`, se considera todo el token como ruta.

Antes de v2.8.0, el argumento `<to>` podía confundirse por el parser con un [token matcher](/docs/caddyfile/matchers#syntax) si empezaba con `/`, así que era necesario especificar un matcher wildcard (`*`).


## Directivas similares

Hay otras directivas que realizan reescrituras, pero con distinta intención o sin reemplazar por completo el URI:

- [`uri`](uri) manipula un URI (eliminar prefijo, sufijo o reemplazo de substring).

- [`try_files`](try_files) reescribe la solicitud según la existencia de archivos.


## Ejemplos

Reescribir todas las solicitudes a `index.html`, dejando intacta cualquier query string:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Nota que antes de v2.8.0 era necesario aquí un [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers) porque el primer argumento era ambiguo con un [path matcher](/docs/caddyfile/matchers#path-matchers), por ejemplo `rewrite * /foo`, pero ahora puede simplificarse a `rewrite /foo`.

</aside>

Prependir `/api` a todas las solicitudes, preservando el resto del URI, y luego hacer reverse proxy a una app:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Reemplazar la query string en solicitudes API con `a=b`, dejando el path sin cambios:

```caddy
example.com {
	rewrite ?a=b
}
```

Solo para solicitudes a `/api/`, preservar la query string existente y añadir un par clave/valor:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Cambiar path y query string, preservando la query original y añadiendo el path original como parámetro `p`:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
