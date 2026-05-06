---
title: Patrones comunes de Caddyfile
---

# Patrones comunes de Caddyfile

Esta página muestra algunas configuraciones completas y mínimas de Caddyfile para casos de uso frecuentes. Pueden servir como punto de partida para tus propios archivos de Caddyfile.

Estas no son soluciones listas para usar; tendrás que personalizar el nombre de dominio, puertos/sockets, rutas de directorio, etc. Están pensadas para ilustrar algunos de los patrones de configuración más comunes.

- [Servidor de archivos estáticos](#static-file-server)
- [Proxy inverso](#reverse-proxy)
- [PHP](#php)
- [Redirigir subdominio `www.`](#redirect-www-subdomain)
- [Barras finales](#trailing-slashes)
- [Certificados wildcard](#wildcard-certificates)
- [Aplicaciones de una sola página (SPAs)](#single-page-apps-spas)
- [Caddy haciendo proxy a otro Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## Servidor de archivos estáticos

```caddy
example.com {
	root /var/www
	file_server
}
```

Como suele ocurrir, la primera línea es la dirección del sitio. La directiva [`root`](/docs/caddyfile/directives/root) especifica la ruta raíz del sitio (`*` significa coincidir con todas las solicitudes, para desambiguar respecto a un [*path matcher*](/docs/caddyfile/matchers#path-matchers)) — cambia la ruta según tu sitio si no es el directorio de trabajo actual. Finalmente, habilitamos el [servidor de archivos estáticos](/docs/caddyfile/directives/file_server).



<a id="reverse-proxy"></a>
## Proxy inverso

Proxy de todas las solicitudes:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Solo proxy para solicitudes que empiecen por `/api/` y servir archivos estáticos para todo lo demás:

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Esto usa un [*request matcher*](/docs/caddyfile/matchers#syntax) para coincidir únicamente con solicitudes que empiecen con `/api/` y enviarlas al backend. Todas las demás solicitudes se servirán desde el [`root`](/docs/caddyfile/directives/root) del sitio con el [servidor de archivos estáticos](/docs/caddyfile/directives/file_server). Esto también depende del hecho de que `reverse_proxy` está más arriba en el [orden de directivas](/docs/caddyfile/directives#directive-order) que `file_server`.

Hay más [ejemplos de `reverse_proxy` aquí](/docs/caddyfile/directives/reverse_proxy#examples).


<a id="php"></a>
## PHP

### PHP-FPM

Con un servicio PHP FastCGI en ejecución, algo como esto funciona para la mayoría de aplicaciones PHP modernas:

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

Personaliza la raíz del sitio según corresponda; este ejemplo asume que el webroot de tu app PHP está en un directorio `public`; las solicitudes de archivos existentes en disco se servirán con [`file_server`](/docs/caddyfile/directives/file_server), y cualquier otra será enrutada a `index.php` para ser manejada por la app PHP.

A veces puedes usar un socket Unix para conectar con PHP-FPM:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

La directiva [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) es en realidad un atajo de [varias piezas de configuración](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

Alternativamente, puedes usar [FrankenPHP](https://frankenphp.dev/), que es una distribución de Caddy que llama a PHP directamente usando CGO (Go to C bindings). Puede ser hasta 4 veces más rápida que PHP-FPM, y todavía mejor si puedes usar el modo worker.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-www-subdomain"></a>
## Redirigir subdominio `www.`

Para **añadir** el subdominio `www.` con una redirección HTTP:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Para **eliminarlo**:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Para quitarlo en **múltiples dominios** al mismo tiempo; esto usa los placeholders `{labels.*}` que son las partes del hostname, indexadas desde la derecha desde `0` (`0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```


<a id="trailing-slashes"></a>
## Barras finales

Por lo general, no necesitas configurar esto tú mismo; la directiva [`file_server`](/docs/caddyfile/directives/file_server) agregará o eliminará automáticamente las barras finales de las solicitudes mediante redirecciones HTTP, según si el recurso solicitado es un directorio o un archivo, respectivamente.

Sin embargo, si lo necesitas, aún puedes forzar barras finales con tu configuración. Hay dos formas: interna o externa.

### Aplicación interna

Esto usa la directiva [`rewrite`](/docs/caddyfile/directives/rewrite). Caddy reescribirá internamente la URI para agregar o eliminar la barra final:

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

Con una reescritura, las solicitudes con y sin barra final serán equivalentes.

### Aplicación externa

Esto usa la directiva [`redir`](/docs/caddyfile/directives/redir). Caddy le pedirá al navegador cambiar la URI para agregar o eliminar la barra final:

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

Con una redirección, el cliente tendrá que reenviar la solicitud, forzando una sola URI aceptable para un recurso.


<a id="wildcard-certificates"></a>
## Certificados wildcard

Para la mayoría de issuers, incluida Let's Encrypt, debes habilitar el [ACME DNS challenge](/docs/automatic-https#dns-challenge) para que Caddy automatice certificados wildcard.

Con el DNS challenge habilitado, desde Caddy 2.10, Caddy preferirá un certificado wildcard aplicable que ya esté configurado o gestionado antes de gestionar un certificado separado para un subdominio.


Si necesitas servir varios subdominios con el mismo certificado wildcard, la mejor forma de gestionarlos es con un Caddyfile como este, usando la directiva [`handle`](/docs/caddyfile/directives/handle) y los [*host matchers*](/docs/caddyfile/matchers#host):

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# Fallback para dominios sin gestionar explícitamente
	handle {
		abort
	}
}
```

Debes habilitar el [ACME DNS challenge](/docs/automatic-https#dns-challenge) para que Caddy gestione automáticamente certificados wildcard.


<a id="single-page-apps-spas"></a>
## Aplicaciones de una sola página (SPAs)

Cuando una página web tiene su propio enrutamiento, los servidores pueden recibir muchas solicitudes para páginas que no existen en el lado servidor, pero que pueden renderizarse del lado cliente siempre que se sirva el archivo índice. A este tipo de aplicaciones web se les llama SPAs, o aplicaciones de página única.

La idea principal es que el servidor haga "try files" para ver si el archivo solicitado existe en el servidor y, si no, hacer *fallback* a un archivo índice donde el cliente gestione el enrutamiento (normalmente con JavaScript del lado cliente).

Una configuración típica de SPA suele verse así:

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

Si tu SPA está acoplada a una API u otros endpoints de solo servidor, te convendrá usar bloques `handle` para tratarlos de forma exclusiva:

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

Si tu `index.html` contiene referencias a assets JS/CSS con nombres de archivo con hash, quizá quieras considerar añadir una cabecera `Cache-Control` para indicar a los clientes que _no_ lo guarden en caché (de modo que si cambian los assets, los navegadores descarguen las nuevas versiones). Como la reescritura `try_files` se usa para servir tu `index.html` desde cualquier ruta que no coincida con otro archivo en disco, puedes envolver `try_files` con un `route` para que el manejador `header` se ejecute _después_ de la reescritura (normalmente se ejecutaría antes por el [orden de directivas](/docs/caddyfile/directives#directive-order)):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Caddy haciendo proxy a otro Caddy

Si tienes una instancia de Caddy de acceso público (llamémosla "front") y otra instancia de Caddy en tu red privada (llamémosla "back") que sirve tu app real, puedes usar la directiva [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) para reenviar solicitudes.

Instancia front:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Instancia back:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Este ejemplo sirve dos dominios distintos, ambos proxyados hacia la misma instancia back de Caddy, en el puerto `80`. Tu instancia back sirve los dos dominios de manera diferente, por eso está configurada con dos bloques de sitio separados.

- En la instancia back, [`http://`](/docs/caddyfile/concepts#addresses) se usa para aceptar HTTP en el puerto `80`. La instancia front termina TLS, y el tráfico entre front y back usa una red privada, así que no hay necesidad de volver a cifrarlo.

- Puedes usar un puerto distinto como `8080` en la instancia back si lo necesitas; solo añade `:8080` a cada dirección de sitio en la configuración de back, O define la [`http_port` opción global](/docs/caddyfile/options#http_port) en `8080`.

- En back, la opción global [`trusted_proxies`](/docs/caddyfile/options#trusted_proxies) se usa para indicarle a Caddy que confíe en la instancia front como proxy. Esto asegura que se preserve la IP real del cliente.

- Además, podrías tener más de una instancia back con [balanceo de carga](/docs/caddyfile/directives/reverse_proxy#load-balancing) entre ellas. Podrías configurar mTLS (TLS mutuo) usando [`acme_server`](/docs/caddyfile/directives/acme_server) en la instancia front para que actúe como CA de la instancia back (útil si el tráfico entre front y back cruza redes no confiables).
