---
title: Actualizando a Caddy 2
---

Guia de Actualizacion
=============

Caddy 2 es una base de codigo totalmente nueva, escrita desde cero para mejorar Caddy 1. Caddy 2 no es compatible con versiones anteriores de Caddy 1. Pero no te preocupes: para la mayoria de configuraciones basicas, no cambia tanto. Esta guia te ayudara a migrar lo mas facil posible.

Esta guia no entra en detalle sobre las nuevas funcionalidades -- que son muy buenas, por cierto, te recomendamos [aprenderlas](/docs/getting-started) -- el objetivo aqui es dejarte funcionando en Caddy 2 cuanto antes.

- [Bits de alto nivel](#high-order-bits)
- [Pasos](#steps)
- [HTTPS y puertos](#https-and-ports)
- [Linea de comandos](#command-line)
- [Caddyfile](#caddyfile)
	- [Cambios principales](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [Archivos de servicio](#service-files)
- [Plugins](#plugins)
- [Obtener ayuda](#getting-help)



## High-order bits

- "Caddy 2" sigue llamandose `caddy`. Podemos usar "Caddy 2" para aclarar de que version hablamos y evitar confusion durante la transicion.
- La mayoria de usuarios solo necesitan reemplazar el binario `caddy` y su configuracion `Caddyfile` (despues de probar que funciona).
- Probablemente sea mejor empezar con Caddy 2 sin asumir que las practicas de Caddy 1 siguen igual.
- Puede que no puedas replicar exactamente una configuracion muy especifica de v1 en v2. Por lo general, hay una razon para eso.
- La linea de comandos ya no se usa para configurar servidores.
- Las variables de entorno ya no son necesarias para la configuracion.
- La forma principal de dar configuracion a Caddy 2 es a traves de su [API](/docs/api), pero tambien se puede usar el comando [`caddy`](/docs/command-line).
- Debes saber que el lenguaje de configuracion nativo de Caddy 2 es [JSON](/docs/json/), y el Caddyfile es un [adaptador de config](/docs/config-adapters) que convierte a JSON por ti. Casos muy personalizados o avanzados pueden requerir JSON, ya que no toda posible configuracion se puede expresar en Caddyfile.
- El Caddyfile es mayormente igual, pero tambien mucho mas potente; las directivas cambiaron.



## Steps

1. Familiarizate con Caddy 2 siguiendo nuestro tutorial de [Getting Started](/docs/getting-started).
2. Haz el paso 1 si no lo hiciste. En serio: no subestimamos lo importante que es saber usar Caddy 2 al menos un poco. (Es mas divertido.)
3. Usa la guia de abajo para migrar tus comandos `caddy`.
4. Usa la guia de abajo para migrar tu `Caddyfile`.
5. Prueba tu nueva config localmente o en un entorno de staging.
6. Prueba, prueba y vuelve a probar
7. Despliega y disfrute.



## HTTPS and ports

El puerto por defecto de Caddy ya no es `:2015`. El puerto por defecto de Caddy 2 es `:443` o, si no se conoce hostname o IP, el puerto `:80`. Siempre puedes personalizar los puertos en tu config.

El protocolo por defecto en Caddy 2 es [**siempre** HTTPS si se conoce un hostname o IP](/docs/automatic-https#overview). Esto es distinto a Caddy 1, donde solo dominios publicos usaban HTTPS por defecto. Ahora, _cada_ sitio usa HTTPS (salvo que se desactive explicitamente especificando `:80` o `http://`).

Las direcciones IP y host locales recibiran certificados de una [CA incrustada de confianza local](/docs/automatic-https#local-https). Los demas dominios usarán ZeroSSL o Let's Encrypt. (Todo esto es configurable.)

La estructura de almacenamiento de certificados y recursos ACME cambió. Caddy 2 probablemente obtenga nuevos certificados para tus sitios; pero si tienes muchos certificados, puedes migrarlos manualmente si no lo hace automaticamente. Consulta los issues [#2955](https://github.com/caddyserver/caddy/issues/2955) y [#3124](https://github.com/caddyserver/caddy/issues/3124) para detalles.



## Command line

El comando `caddy` ahora es `caddy run`.

Todas las flags de linea de comandos son distintas. Retiralas, porque ahora toda la config de servidor vive en el documento de config actual (normalmente Caddyfile o JSON). Probablemente encuentres lo que necesitas en la [estructura JSON](/docs/json/) o en las [opciones globales del Caddyfile](/docs/caddyfile/options) para reemplazar la mayoria de flags de v1.

Un comando como `caddy -conf ../Caddyfile` se convierte en `caddy run --config ../Caddyfile`.

Como antes, si tu Caddyfile esta en la carpeta actual, Caddy lo detectara y usara automaticamente; no hace falta la flag `--config`.

Las senales son mayormente las mismas, excepto USR1 y USR2 que ya no se soportan. Usa [`caddy reload`](/docs/command-line#caddy-reload) o la [API](/docs/api) para cargar una nueva config.

Ejecutar `caddy` sin config antes ejecutaba un servidor de archivos simple. El equivalente en Caddy 2 es [`caddy file-server`](/docs/command-line#caddy-file-server).

Las variables de entorno ya no son relevantes, excepto `HOME` (y opcionalmente cualquier variable `XDG_*` que definas). `CADDYPATH` esta [reemplazada por convenciones del OS](/docs/conventions#file-locations).



## Caddyfile

El [Caddyfile de v2](/docs/caddyfile/concepts) es muy similar al que ya conoces. Principalmente necesitaras cambiar directivas.

⚠️ **Lee con cuidado las nuevas directivas.** Sobre todo si tu config es avanzada, hay muchos matices. Estos consejos te ayudaran a migrar rapido, pero revisa la documentacion completa de cada directiva para entender implicaciones de la migracion. Y siempre prueba tus configs a fondo antes de produccion.


### Primary changes

- Si sirves archivos estaticos, debes agregar la directiva [`file_server` ](/docs/caddyfile/directives/file_server), ya que Caddy 2 ya no asume esto por defecto. Caddy 2 tampoco detecta MIME por defecto por seguridad; si falta Content-Type puede que tengas que setear el header con la directiva [header](/docs/caddyfile/directives/header).

- En v1 solo podias filtrar (o "match") directivas por ruta de solicitud. En v2, [el matching de solicitudes](/docs/caddyfile/matchers) es mucho mas potente. Las directivas v2 que agregan un middleware a la cadena de handlers HTTP o manipulan request/response de cualquier forma aprovechan esta funcionalidad. [Lee mas sobre matchers en v2.](/docs/caddyfile/matchers) Necesitarias conocerlos para entender el Caddyfile v2.

- Aunque muchos [placeholders](/docs/conventions#placeholders) son iguales, muchos cambiaron y ahora hay [muchos nuevos](/docs/modules/http#docs), incluyendo [atajos para Caddyfile](/docs/caddyfile/concepts#placeholders).

- Los logs de Caddy 2 son todos estructurados y el formato por defecto es JSON. Todos los niveles de logs pueden ir al mismo destino para procesamiento (pero puedes personalizarlo).

- Donde en Caddy 1 se hac�a matching por prefijo de ruta, en Caddy 2 ahora se hace de forma exacta por defecto. Si quieres coincidir un prefijo como `/foo/`, en Caddy 2 debes usar `/foo/*`.

Listaremos algunas de las directivas v1 mas comunes y describiremos como convertirlas para Caddyfile v2.

⚠️ **El hecho de que falte una directiva v1 en esta pagina no significa que v2 no pueda hacerlo.** Algunas directivas v1 no son necesarias, no se traducen bien, o se resuelven de otras formas en v2. Para personalizaciones avanzadas puede que debas bajar a JSON. Explora [nuestra documentacion](/docs/caddyfile) para encontrar lo que necesitas.


### basicauth

La autenticacion basica HTTP sigue configurandose con [`basic_auth`](/docs/caddyfile/directives/basic_auth). Sin embargo, la config de Caddy 2 no acepta passwords en texto plano. Debes usar su hash, puedes generarlo con [`caddy hash-password`](/docs/command-line#caddy-hash-password).

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


### browse

El listado de archivos ahora se habilita con [`file_server`](/docs/caddyfile/directives/file_server).

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


### errors

Las paginas de error personalizadas se logran con [`handle_errors`](/docs/caddyfile/directives/handle_errors).


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

### ext

Las extensiones implicitas de archivos se hacen con [`try_files`](/docs/caddyfile/directives/try_files).

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


### fastcgi

Si sirves PHP, el equivalente v2 es [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

Nota que la directiva `fastcgi` en v1 realizaba muchas tareas por debajo, incluyendo prueba de archivos en disco, rewrites y hasta redirecciones. La directiva `php_fastcgi` en v2 tambien lo hace, y su documento incluye una [forma expandida](/docs/caddyfile/directives/php_fastcgi#expanded-form) que puedes ajustar si tus requisitos son distintos.

No se necesita el preset `php` en v2, porque `php_fastcgi` asume PHP por defecto. Una linea como `php_fastcgi 127.0.0.1:9000 php` hara que el reverse proxy crea un segundo backend llamado `php`, provocando errores de conexion.

Los subdirectorios son diferentes en v2 -- probablemente no necesites ninguno para PHP.


### gzip

Ahora una sola directiva [`encode`](/docs/caddyfile/directives/encode) se usa para todas las codificaciones de respuesta, incluyendo multiples formatos.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

Dato curioso: Caddy 2 tambien soporta `zstd` (aunque ningun navegador lo usa aun).


### header

Esta directiva esta [casi sin cambios](/docs/caddyfile/directives/header), pero en v2 es mucho mas potente porque puede hacer reemplazos parciales de cadenas.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


### log

Habilita logging de acceso; la directiva [`log`](/docs/caddyfile/directives/log) sigue disponible en v2, pero todos los logs son estructurados y usan JSON por defecto.

La forma recomendada de habilitar access logging es:

```caddy-d
log
```

lo que envia logs estructurados a stderr. (Tambien puedes enviarlos a un archivo o socket de red; consulta la pagina de la directiva [`log`](/docs/caddyfile/directives/log).)

Por defecto, los logs estaran en formato JSON [estructurado](/docs/logging). Si aun necesitas CLF por compatibilidad legada, puedes usar plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder).


### proxy

El equivalente v2 es [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

Cambios notables: `header_upstream` y `header_downstream` ahora son `header_up` y `header_down`; y los subdirectorios relacionados con balanceo de carga usan prefijo `lb_`.

Otra diferencia importante es que v2 pasa todos los headers entrantes por defecto (incluido `Host`) y establece `X-Forwarded-For`. Es decir, el modo "transparent" de v1 es basicamente el default en v2 (pero si necesitas otros headers como X-Real-IP, debes configurarlos). Puedes seguir personalizando/reemplazando el header `Host` con `header_up`.

El proxy de websockets "funciona" en v2; no necesitas "habilitar" websockets como en v1.

Se removio la subdirectiva `without` porque los [rewrite hacks](#rewrite) ya no son necesarios en v2 gracias al mejor soporte de matchers.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


### redir

[Sin cambios](/docs/caddyfile/directives/redir), salvo algunos detalles del codigo de estado opcional. La mayoria de configs no necesita cambios.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


### rewrite

La semantica de reescritura de request ("redireccion interna") cambió un poco. Si usabas una especie de "rewrite hack" en v1 para hacer matching por algo mas que prefijo simple, en v2 no es necesario.

La [nueva directiva `rewrite`](/docs/caddyfile/directives/rewrite) es muy simple pero poderosa, ya que la mayor parte de su complejidad se delega a los [matchers](/docs/caddyfile/matchers) en v2:

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Fijate que simplemente usamos los [matcher tokens](/docs/caddyfile/matchers) normales de Caddy 2; ya no es un caso especial para esta directiva.

Empieza eliminando todos los rewrite hacks; conviértelos en [named matchers](/docs/caddyfile/concepts#named-matchers). Evalua cada `rewrite` de v1 para saber si realmente es necesaria en v2. Sugerencia: un Caddyfile v1 que usa `rewrite` para agregar un prefijo y luego `proxy` con `without` para quitar ese mismo prefijo es un rewrite hack y se puede eliminar.

Puedes encontrar utiles las nuevas directivas [`route`](/docs/caddyfile/directives/route) y [`handle`](/docs/caddyfile/directives/handle) para control avanzado de enrutamiento.


### root

Esta directiva permanece [sin cambios](/docs/caddyfile/directives/root).

Recuerda añadir [`file_server`](/docs/caddyfile/directives/file_server) si sirves archivos estaticos, porque Caddy 2 no lo asume por defecto como ocurria en v1.


### status

El equivalente v2 es [`respond`](/docs/caddyfile/directives/respond), que tambien puede escribir cuerpo de respuesta.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


### templates

La sintaxis general de [`templates`](/docs/caddyfile/directives/templates) se mantiene, pero las acciones y funciones de template cambian y mejoran mucho. Por ejemplo, ahora los templates pueden incluir archivos, renderizar markdown, hacer subrequests internos, analizar front matter y mas.

[Consulta la documentacion](/docs/modules/http.handlers.templates) para detalles de funciones nuevas.

- **v1:** `templates`
- **v2:** `templates`


### tls

Los fundamentos de la directiva [`tls`](/docs/caddyfile/directives/tls) no cambiaron, por ejemplo al especificar tu propio certificado y clave:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

Pero la logica de [auto-HTTPS](/docs/automatic-https) de Caddy _si_ cambio, asi que revisa eso.

Tambien cambiaron los nombres de los cipher suites.

Una configuracion comun en Caddy 2 es `tls internal` para servir un certificado de confianza local para un hostname de desarrollo que no sea `localhost` ni una IP.

La mayoria de sitios no necesitara esta directiva en absoluto.


## Service files

Recomendamos usar [uno de nuestros archivos de servicio systemd oficiales](/docs/running#linux-service) para despliegues de Caddy.

Si necesitas un servicio personalizado, parte desde el nuestro. Estan ajustados cuidadosamente por buenas razones. Personaliza el tuyo si hace falta.


## Plugins

Los plugins creados para v1 no son automaticamente compatibles con v2. Muchos plugins de v1 ni siquiera son necesarios en v2. A la vez, v2 es mucho mas extensible y flexible que v1.

Si quieres escribir un plugin para Caddy 2, [aprende como crear un modulo de Caddy](/docs/extending-caddy).


### Building Caddy 2 with plugins

Caddy 2 se puede descargar con plugins desde la [pagina de descargas interactiva](/download). Tambien puedes [compilar Caddy tu mismo](/docs/build) usando `xcaddy`. `xcaddy` automatiza las instrucciones en el archivo [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) de Caddy.


## Getting help

Si tienes problemas para hacer funcionar Caddy, primero revisa la documentacion del sitio. Toma tiempo para probar cosas nuevas y entender lo que sucede -- v2 es muy distinto de v1 en muchos aspectos (pero tambien muy familiar).

Si aun necesitas ayuda, se parte de [nuestra comunidad](https://caddy.community)! Puede que ayudar a otros sea la mejor forma de ayudarte tambien.
