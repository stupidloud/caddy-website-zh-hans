---
title: php_fastcgi (Directiva de Caddyfile)
---

<script>
ready(function() {
	// Agregaremos enlaces a todas las subdirectivas si se encuentra una etiqueta anchor coincidente en la página.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Una directiva con configuración predeterminada que envía solicitudes a un servidor PHP FastCGI como php-fpm.

- [Sintaxis](#sintaxis)
- [Forma expandida](#forma-expandida)
  - [Explicación](#explicación)
- [Ejemplos](#ejemplos)

El [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) de Caddy puede servir cualquier aplicación FastCGI, pero esta directiva está diseñada específicamente para aplicaciones PHP. Es un atajo conveniente que sustituye una [configuración más larga](#forma-expandida).

Se espera que cualquier `index.php` en la raíz del sitio actúe como enrutador. Si esto no es deseable, reconfigura la subdirectiva [`try_files`](#try_files) para modificar el comportamiento predeterminado de rewrite, o usa la [forma expandida](#forma-expandida) como base y personalízala según tus necesidades.

Además de las subdirectivas listadas abajo, esta directiva también admite todas las subdirectivas de [`reverse_proxy`](reverse_proxy#syntax). Por ejemplo, puedes habilitar balanceo de carga y checks de salud.

**La mayoría de las aplicaciones PHP modernas funcionan bien sin subdirectivas adicionales ni personalización.** Las subdirectivas suelen usarse solo en casos límite o con aplicaciones PHP legacy.

## Sintaxis
<a id="sintaxis"></a>

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<cualquier otra subdirectiva reverse_proxy...>
}
```

- **<php-fpm_gateways...>** son las [direcciones](/docs/conventions#network-addresses) de los servidores FastCGI. Típicamente, un socket TCP o un archivo de socket unix.

- **root** <span id="root"/> establece la carpeta raíz del sitio. Se recomienda usar siempre la directiva [`root`](root) junto con `php_fastcgi`, pero sobrescribirla puede ser útil cuando el upstream de PHP-FPM usa una raíz distinta a la de Caddy (consulta [un ejemplo](#docker)). Si se usa, predetermina al valor de la directiva [`root`](root), de lo contrario usa el directorio de trabajo actual de Caddy.

- **split** <span id="split"/> configura los subcadenas para dividir la URI en dos partes. El primer subcadena coincidente se usará para separar el "path info" de la ruta. La primera parte se concatena con la subcadena coincidente y se asumirá como el nombre del recurso real (script CGI). La segunda parte se asigna a PATH_INFO para que la use el script CGI. Predeterminado: `.php`

- **index** <span id="index"/> especifica el nombre de archivo que se trata como índice de directorio. Esto afecta al matcher de archivos en la [forma expandida](#forma-expandida). Predeterminado: `index.php`. Puede establecerse en `off` para desactivar el fallback de rewrite a `index.php` cuando no se encuentra un archivo coincidente.

- **try_files** <span id="try_files"/> especifica una sobrescritura para el rewrite try-files predeterminado. Consulta la directiva [`try_files`](try_files) para más detalles. Predeterminado: `{path} {path}/index.php index.php`.

- **env** <span id="env"/> establece una variable de entorno adicional al valor indicado. Puede especificarse más de una vez para múltiples variables. Por defecto, ya se configuran todas las variables de entorno FastCGI relevantes (incluyendo headers HTTP), pero puedes agregar o sobrescribir variables según se necesite.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> cuando el directorio [`root`](#root) es un enlace simbólico (symlink), esto habilita resolverlo a su ruta real. A veces se usa como estrategia de despliegue, simplemente cambiando el symlink para apuntar a la nueva versión en otro directorio. Desactivado por defecto para evitar llamadas repetidas al sistema.

- **capture_stderr** <span id="capture_stderr"/> habilita la captura y registro de mensajes enviados por el upstream fastcgi en `stderr`. El log se hace con nivel `WARN` por defecto. Si la respuesta tiene estado `4xx` o `5xx`, se usará en su lugar nivel `ERROR`. Por defecto, `stderr` se ignora.

- **dial_timeout** <span id="dial_timeout"/> es un [valor de duración](/docs/conventions#durations) que establece cuánto esperar al conectarse al socket upstream. Predeterminado: `3s`.

- **read_timeout** <span id="read_timeout"/> es un [valor de duración](/docs/conventions#durations) que establece cuánto esperar al leer del upstream FastCGI. Sin tiempo de espera predeterminado.

- **write_timeout** <span id="write_timeout"/> es un [valor de duración](/docs/conventions#durations) que establece cuánto esperar al enviar al upstream FastCGI. Sin tiempo de espera predeterminado.


Como esta directiva es un wrapper opinado sobre reverse proxy, puedes usar cualquier subdirectiva de [`reverse_proxy`](reverse_proxy#syntax) para personalizarla.


## Forma expandida
<a id="forma-expandida"></a>

La directiva `php_fastcgi` (sin subdirectivas) es equivalente a la siguiente configuración. La mayoría de aplicaciones PHP modernas funcionan bien con este preset. Si la tuya no, puedes basarte en esto y personalizarla en lugar de usar el atajo `php_fastcgi`.

```caddy-d
route {
	# Agregar barra final para solicitudes de directorio
	# Esta redirección se desactiva automáticamente si "{http.request.uri.path}/index.php"
	# no aparece en la lista try_files
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Si el archivo solicitado no existe, prueba archivos de índice y asume que index.php siempre existe
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# Enruta archivos PHP al responder FastCGI
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

### Explicación
<a id="explicación"></a>

- La primera sección se encarga de canonicalizar la ruta de solicitud. El objetivo es asegurar que las solicitudes dirigidas a un directorio en disco realmente tengan la barra final `/` añadida en la ruta de solicitud, de modo que solo exista una URL válida para solicitudes a ese directorio.

  Esta canonicalización solo ocurre si la subdirectiva `try_files` contiene `{path}/index.php` (valor predeterminado).

  Se realiza con un matcher de solicitudes que coincide solo con solicitudes que _no_ terminan en una barra y que mapean a un directorio en disco que contiene un archivo `index.php`; si coincide, realiza una redirección HTTP 308 con la barra final agregada. Por ejemplo, redirige `/foo` a `/foo/` (agregando `/`, para canonicalizar la ruta al directorio), si `/foo/index.php` existe en disco.

- La siguiente sección se encarga de realizar rewrites de ruta según si existe un archivo coincidente en disco. Esto también tiene como efecto secundario recordar la parte de la ruta después de `.php` (si la ruta de solicitud la tiene). Esto es importante para que Caddy establezca correctamente las variables de entorno FastCGI.

  - Primero comprueba si `{path}` es un archivo que existe en disco. Si es así, reescribe a esa ruta. Esto esencialmente acorta el flujo, y se asegura de que las solicitudes a archivos que _sí_ existen en disco no se reescriban de otro modo (ver siguientes pasos abajo). Por ejemplo, si tienes un archivo `/js/app.js` en disco, entonces la solicitud a esa ruta se mantendrá igual.

  - Segundo, comprueba si `{path}/index.php` es un archivo que existe en disco. Si es así, reescribe a esa ruta. Para solicitudes a un directorio como `/foo/` buscará `/foo//index.php` (que se normaliza a `/foo/index.php`) y reescribirá la solicitud a esa ruta si existe. Este comportamiento a veces es útil si ejecutas otra app PHP en un subdirectorio de tu webroot.

  - Por último, siempre reescribirá a `index.php` (casi siempre existe para aplicaciones PHP modernas). Esto permite que tu app PHP maneje cualquier solicitud de rutas que _no_ mapeen a archivos en disco, usando el script `index.php` como entrypoint.

- Y finalmente, la última sección es la que realmente envía la solicitud a tu servicio PHP FastCGI (o PHP-FPM) para ejecutar tu código PHP. El matcher de solicitud solo coincidirá con solicitudes que terminen en `.php`, por lo que cualquier archivo que _no sea_ un script PHP y que _sí_ exista en disco no será gestionado por esta directiva y caerá hacia abajo.

La directiva `php_fastcgi` normalmente no es suficiente por sí sola. Casi siempre debe emparejarse con la directiva [`root`](root) para definir la ubicación de tus archivos en disco (para aplicaciones PHP modernas, puede ser `/var/www/html/public`, donde el directorio `public` es el que contiene `index.php`) y con la directiva [`file_server`](file_server) para servir archivos estáticos (tu JS, CSS, imágenes, etc.) que esta directiva no maneja y pasan al siguiente bloque.


## Ejemplos

Proxear todas las solicitudes PHP a un responder FastCGI que escucha en `127.0.0.1:9000`:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

Lo mismo, pero solo para solicitudes bajo `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

Cuando usas PHP-FPM escuchando por un socket unix:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

La directiva [`root`](root) casi siempre se usa para especificar el directorio que contiene los scripts PHP, y la directiva [`file_server`](file_server) para servir archivos estáticos:

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Al servir múltiples apps PHP con Caddy, la webroot de cada app debe ser diferente para que Caddy pueda leer y servir archivos estáticos por separado y detectar si existen archivos PHP.

Si usas Docker, a menudo tus contenedores PHP-FPM montarán los archivos en la misma raíz. En ese caso, la solución es montar los archivos en tu contenedor Caddy en directorios distintos, y luego usar la [subdirectiva `root`](#root) para establecer la raíz de cada contenedor:

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Para un sitio PHP que no use `index.php` como entrypoint, puedes optar por devolver un error `404` en su lugar. El error puede capturarse y manejarse con la directiva [`handle_errors`](handle_errors):

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
