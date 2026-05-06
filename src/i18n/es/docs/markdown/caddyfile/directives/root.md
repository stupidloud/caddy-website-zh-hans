---
title: root (Caddyfile directive)
---

# root

Establece la ruta raíz del sitio, que usan varios *matchers* y directivas que acceden al sistema de archivos. Si no se configura, la raíz por defecto del sitio es el directorio de trabajo actual.

Específicamente, esta directiva establece el placeholder `{http.vars.root}`. Es excluyente respecto a otras directivas `root` en el mismo bloque, por lo que es seguro definir múltiples raíces con *matchers* que se solapan: no se encadenan ni se sobrescriben entre sí.

Esta directiva no habilita automáticamente el servicio de archivos estáticos, por lo que suele usarse junto con la [`file_server` directiva](file_server) o la [`php_fastcgi` directiva](php_fastcgi).


## Syntax

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** es la ruta que se usará como raíz del sitio.

Antes de v2.8.0, el argumento `<path>` podía confundirse para el parser con un [token matcher](/docs/caddyfile/matchers#syntax) si empezaba por `/`, por lo que era necesario especificar un wildcard matcher (`*`).


## Examples

Establece la raíz del sitio en `/home/bob/public_html` (asumiendo que Caddy se ejecuta como el usuario `bob`):

<aside class="tip">

Si estás ejecutando Caddy como servicio systemd, leer archivos desde `/home` no funcionará, porque el usuario `caddy` no tiene permiso de "ejecución" en el directorio `/home` (necesario para atravesar el árbol). Se recomienda colocar los archivos en `/srv` o `/var/www/html`.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Ten en cuenta que antes de la v2.8.0 era necesario un [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers) porque el primer argumento era ambiguo con un [path matcher](/docs/caddyfile/matchers#path-matchers), por ejemplo `root * /srv`, pero ahora puede simplificarse a `root /srv`.

</aside>


Establece la raíz del sitio en `public_html` (relativa al directorio de trabajo actual) para todas las solicitudes:

```caddy-d
root public_html
```

Cambia la raíz del sitio solo para las solicitudes en `/foo/*`:

```caddy-d
root /foo/* /home/user/public_html/foo
```

La directiva `root` se suele emparejar con [`file_server`](file_server) para servir archivos estáticos y/o con [`php_fastcgi`](php_fastcgi) para servir un sitio PHP:

```caddy
example.com {
	root /srv
	file_server
}
```
