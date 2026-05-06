---
title: Opciones globales (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


# Opciones globales

El Caddyfile tiene una forma de especificar opciones que se aplican de forma global. Algunas opciones actuan como valores predeterminados; otras personalizan servidores HTTP y no se aplican solo a un sitio en particular; y otras personalizan el comportamiento del [adaptador](/docs/config-adapters).

La parte superior de tu Caddyfile puede ser un **bloque de opciones globales**. Este es un bloque que no tiene claves:

```caddy
{
	...
}
```

Solo puede haber uno, y debe ser el primer bloque del Caddyfile.

Las opciones posibles son (haz clic en cada opción para ir a su documentacion):

```caddy
{
	# Opciones generales
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# Opciones TLS
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Opciones de servidor
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# Sistemas de archivos
	filesystem <name> <module> {
		<options...>
	}

	# Opciones PKI
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Opciones de eventos
	events {
		on <event> <handler...>
	}
}
```


## Opciones generales

##### `debug`
Habilita el modo debug, que establece el nivel de registro en `DEBUG` para el [logger predeterminado](#log). Esto muestra más detalles utiles para solucionar problemas (y es muy detallado en produccion). Te pedimos que lo habilites antes de pedir ayuda en los [foros de la comunidad](https://caddy.community). Por ejemplo, en la parte superior de tu Caddyfile, si no tienes otras opciones globales:

```caddy
{
	debug
}
```


##### `http_port`
El puerto que el servidor usara para HTTP.

**Solo para uso interno**; no cambia el puerto HTTP para los clientes. Esto suele usarse si en tu red interna necesitas redirigir el puerto `80` a uno distinto (por ejemplo `8080`) antes de llegar a Caddy, por motivos de enrutado.

Predeterminado: `80`


##### `https_port`
El puerto que el servidor usara para HTTPS.

**Solo para uso interno**; no cambia el puerto HTTPS para los clientes. Esto suele usarse si en tu red interna necesitas redirigir el puerto `443` a uno distinto (por ejemplo `8443`) antes de llegar a Caddy, por motivos de enrutado.

Predeterminado: `443`


##### `default_bind`
Las direcciones de enlace predeterminadas para todos los sitios, si la directiva [`bind` ](/docs/caddyfile/directives/bind) no se usa en el sitio. Predeterminado: vacio, lo que vincula a todas las interfaces.

<aside class="tip">

Recuerda que esto solo aplica a los servidores que genera el Caddyfile; esto significa que el servidor HTTP creado por [Automatic HTTPS](/docs/automatic-https) para redirecciones HTTP-a-HTTPS no heredara estas direcciones de enlace. Como alternativa, declara un sitio `http://` (puede estar vacio, sin directivas) para que exista cuando se adapte el Caddyfile, y reciba las direcciones de enlace.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
Asigna un orden a una o varias directivas de manejadores HTTP. Como los manejadores HTTP se ejecutan en una cadena secuencial, es necesario que se ejecuten en el orden correcto. Las directivas estandar tienen [un orden predefinido](/docs/caddyfile/directives#directive-order), pero si usas módulos manejadores HTTP de terceros, debes definir el orden explicitamente usando esta opcion o colocando la directiva dentro de un [`route` bloque](/docs/caddyfile/directives/route). El orden puede describirse de forma absoluta (`first` o `last`), o relativa (`before` o `after`) respecto a otra directiva.

Por ejemplo, para usar el plugin [`replace-response`](https://github.com/caddyserver/replace-response), deberías asegurarte de que su directiva se ordene despues de `encode` para que pueda hacer sustituciones antes de codificar la respuesta (porque las respuestas fluyen hacia arriba en la cadena de manejadores, no hacia abajo):

```caddy
{
	order replace after encode
}
```


##### `storage`
Configura el mecanismo de almacenamiento de Caddy. El valor predeterminado es [`file_system`](/docs/json/storage/file_system/). Hay muchos otros [modulos de almacenamiento](/docs/json/storage/) disponibles como plugins.

Por ejemplo, para cambiar la ubicacion de almacenamiento del sistema de archivos:

```caddy
{
	storage file_system /path/to/custom/location
}
```

Personalizar el modulo de almacenamiento suele ser necesario cuando sincronizas el almacenamiento de varias instancias de Caddy para asegurarte de que todas usan los mismos certificados y claves. Consulta la [seccion de Automatic HTTPS sobre almacenamiento](/docs/automatic-https#storage) para mas detalles.


##### `storage_clean_interval`
Cada cuanto se escanean las unidades de almacenamiento para eliminar activos antiguos o vencidos y eliminarlos. Estos escaneos realizan muchas lecturas (y operaciones de listado) sobre el modulo de almacenamiento, por lo que debes elegir un intervalo mayor para despliegues grandes. Acepta [valores de duracion](/docs/conventions#durations).

El almacenamiento siempre se limpiara cuando el proceso se inicia por primera vez. Luego, se iniciara un nuevo barrido tras ese intervalo desde el inicio de la limpieza anterior si la limpieza anterior termino en menos de la mitad de ese intervalo (de lo contrario se omitira el siguiente inicio).

Predeterminado: `24h`

```caddy
{
	storage_clean_interval 7d
}
```



##### `admin`
Personaliza el [endpoint de la API administrativa](/docs/api). Acepta marcadores de posicion. Toma [direcciones de red](/docs/conventions#network-addresses).

Predeterminado: `localhost:2019`, a menos que la variable `CADDY_ADMIN` de entorno este configurada.

Si se establece en `off`, el endpoint administrativo se desactiva. Cuando esta desactivado, **los cambios de configuracion seran imposibles** sin detener e iniciar el servidor, porque el comando [`caddy reload`](/docs/command-line#caddy-reload) usa la API administrativa para enviar la nueva configuracion al servidor en ejecucion.

Recuerda usar el flag de CLI `--address` con los [comandos](/docs/command-line) compatibles para especificar el endpoint administrativo actual, si la direccion del servidor en ejecucion se modifico respecto al valor predeterminado.

Tambien admite estas sub-opciones:

- **origins** configura la lista de [orígenes](https://developer.mozilla.org/en-US/docs/Glossary/Origin) que pueden conectarse al endpoint.

  Si se omite se selecciona un valor inteligente:
  - si la direccion de escucha es loopback (por ejemplo `localhost` o una IP de loopback, o un socket unix) entonces los orígenes permitidos son `localhost`, `::1` y `127.0.0.1`, combinados con el puerto de escucha (por ejemplo `localhost:2019` es un origen valido).
  - si la direccion de escucha no es loopback, el origen permitido es la misma direccion de escucha.

  Si el host de la direccion de escucha no es una interfaz wildcard (wildcards incluyen: cadena vacia, `0.0.0.0`, o `[::]`), se fuerza la validacion de la cabecera `Host`. En la practica esto significa que por defecto la cabecera `Host` se valida para que este en `origins`, ya que la interfaz es `localhost`. Pero para una direccion como `:2020` que usa una interfaz wildcard, la validacion de la cabecera `Host` no se realiza.

- **enforce_origin** fuerza la aplicacion del encabezado de solicitud `Origin`. Esto se hace de forma implicita siempre que los encabezados CORS sean enviados por el cliente o si el cliente desactiva CORS explicitamente con `Sec-Fetch-Mode: no-cors`. En otros casos, esta opcion es mas util cuando la direccion de escucha es una interfaz wildcard (ya que `Host` no se valida) y la API administrativa esta expuesta a internet publicamente. Activa las comprobaciones preflight de CORS y asegura que la cabecera `Origin` se valide contra la lista `origins`. Usa esta opcion solo si ejecutas Caddy en tu maquina de desarrollo y necesitas acceder a la API administrativa desde un navegador web.

Por ejemplo, para exponer la API administrativa en un puerto distinto, en todas las interfaces — ⚠️ este puerto **no deberia exponerse publicamente**, de lo contrario cualquiera podria controlar tu servidor; considera activar la validacion de origen si necesitas que sea publicamente accesible:

```caddy
{
	admin :2020
}
```

Para desactivar la API administrativa — ⚠️ esto hace **imposibles recargas de configuración** sin detener e iniciar el servidor:

```caddy
{
	admin off
}
```

Para usar un [socket unix](/docs/conventions#network-addresses) para la API administrativa, permitiendo control de acceso por permisos de archivo:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Para permitir solo solicitudes con un encabezado `Origin` coincidente:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`

Controla si la configuracion JSON actual debe persistirse en el [directorio de configuracion](/docs/conventions#configuration-directory), para evitar perder cambios realizados mediante la API administrativa. Actualmente solo se admite la opcion `off`. Por defecto la configuracion se persiste.

```caddy
{
	persist_config off
}
```



##### `log`
Configura loggers con nombre.

El nombre puede pasarse para indicar un logger especifico cuyo comportamiento quieres personalizar. Si no se indica nombre, se modifica el comportamiento del logger `default`. Puedes leer mas sobre el logger `default` y una explicacion de [como funciona el registro en Caddy](/docs/logging).

Se pueden configurar varios loggers con nombres distintos usando la opcion `log` varias veces.

Esto difiere de la [directiva `log`](/docs/caddyfile/directives/log), que solo configura el registro de solicitudes HTTP (tambien conocido como logs de acceso). La opcion global `log` comparte su estructura de configuracion con la directiva (excepto `include` y `exclude`) y su documentacion completa esta en la pagina de la directiva.

- **output** indica donde escribir los registros.

  Consulta la [directiva `log`](/docs/caddyfile/directives/log#output-modules) para documentacion completa.

- **format** describe como codificar o formatear los logs.

  Consulta la [directiva `log`](/docs/caddyfile/directives/log#format-modules) para documentacion completa.

- **level** es el nivel minimo de entrada a registrar.

  Predeterminado: `INFO`.

  Valores posibles: `DEBUG`, `INFO`, `WARN`, `ERROR` y, en casos muy raros, `PANIC`, `FATAL`.

- **include** especifica los nombres de logs que deben incluirse en este logger.

  Por defecto, esta lista esta vacia (es decir, se incluyen todos los logs).

  Por ejemplo, para incluir solo logs emitidos por la API administrativa, usa `admin.api`.

- **exclude** especifica los nombres de logs que deben excluirse de este logger.

  Por defecto, esta lista esta vacia (es decir, no se excluyen logs).

  Por ejemplo, para excluir unicamente logs de acceso HTTP, excluye `http.log.access`.

Los nombres de logger que aceptan `include` y `exclude` dependen de los modulos usados, y la forma mas sencilla de descubrirlos es mirando los logs previos.

Aqui tienes un ejemplo para registrar en json todos los logs de acceso HTTP y API administrativa en stdout:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
Define el periodo de gracia para cerrar servidores HTTP (por ejemplo durante cambios de configuracion o cuando Caddy se detiene).

Durante el periodo de gracia, no se aceptan conexiones nuevas, se cierran conexiones inactivas y las conexiones activas se esperan impacientemente para terminar sus solicitudes. Si los clientes no terminan su solicitud dentro del periodo de gracia, el servidor se forzara a cerrarse para permitir que la recarga complete y liberar recursos. Acepta [valores de duracion](/docs/conventions#durations).

Por defecto, el periodo de gracia es eterno, lo que significa que las conexiones nunca se cierran de forma forzada.

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
Define una [duracion](/docs/conventions#durations)
_antes_ del [periodo de gracia](#grace_period) durante el cual un servidor que va a detenerse continua funcionando con normalidad, excepto que el marcador de posicion `{http.shutting_down}` evalua `true` y `{http.time_until_shutdown}` indica el tiempo hasta que comienza el periodo de gracia.

Esto provoca una demora si algun servidor se esta apagando como parte de un cambio de configuracion, y agenda efectivamente el cambio para mas tarde. Es util para avisar a los verificadores de estado del servidor inminente apagado y para dar tiempo a que un balanceador de carga lo retire de la rotacion; por ejemplo:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


## Opciones TLS

##### `auto_https`
Configura [Automatic HTTPS](/docs/automatic-https), la funcion que habilita a Caddy para automatizar la gestion de certificados y redirecciones HTTP-a-HTTPS para tus sitios.

Hay varias formas:

- `off`: desactiva la automatizacion de certificados y las redirecciones HTTP-a-HTTPS.

- `disable_redirects`: desactiva solo las redirecciones HTTP-a-HTTPS.

- `disable_certs`: desactiva solo la automatizacion de certificados.

- `ignore_loaded_certs`: automatiza certificados incluso para nombres que aparecen en certificados cargados manualmente. Es util si especificaste un certificado usando la [directiva `tls`](/docs/caddyfile/directives/tls) y este contiene nombres (o comodines) que deseas que se gestionen automaticamente.

<aside class="tip">

Esta opcion no afecta el protocolo predeterminado de Caddy, que siempre es HTTPS, cuando la direccion de un sitio tiene un dominio valido. Esto significa que `auto_https off` no hara que tu sitio se sirva por HTTP, solo desactiva la gestion automatica de certificados y redirecciones.

Esto significa que si deseas servir tu sitio por HTTP, debes cambiar su [direccion de sitio](/docs/caddyfile/concepts#addresses) para que tenga prefijo `http://` o sufijo `:80` (o la opcion [`http_port`](#http_port)).

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
Tu direccion de correo electronico. Se usa principalmente al crear una cuenta ACME con tu CA, y se recomienda fuertemente en caso de problemas con tus certificados.

<aside class="tip">

Ten en cuenta que Let's Encrypt puede enviarte correos sobre la proximidad de vencimiento de tu certificado, pero eso puede ser confuso porque Caddy puede haber elegido un emisor distinto (por ejemplo ZeroSSL) al renovar. Revisa tus registros y/o el propio certificado (en tu navegador, por ejemplo) para ver que emisor se uso y que su vencimiento sigue siendo valido; si es asi, puedes ignorar con seguridad el correo de Let's Encrypt.

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
Establece un ServerName TLS por defecto cuando los clientes no usan SNI en su ClientHello.

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ <i>Experimental</i>

Si se configura, el fallback se convierte en el ServerName TLS en el ClientHello si el ServerName original no coincide con ningun certificado en la cache.

Los usos son muy nicho; normalmente, si un cliente es un CDN y reenvia el ServerName del handshake aguas abajo pero puede aceptar un certificado con el nombre de host de origen en su lugar, entonces deberias establecer esto como el nombre de host de tu origen. Ten en cuenta que Caddy debe estar gestionando un certificado para ese nombre.

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
Hace que **todos** los certificados se emitan internamente por defecto, en lugar de a traves de una ACME CA publica como Let's Encrypt. Es util como cambio rapido en entornos de desarrollo.

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
Omite los intentos de instalar la raiz de la CA local en el almacen de confianza del sistema, asi como en los almacenes de confianza de Java y Mozilla Firefox.

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
Especifica la URL al directorio de la ACME CA. Se recomienda encarecidamente establecerla en el [endpoint de staging de Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) para pruebas o desarrollo. Predeterminado: endpoints de produccion de ZeroSSL y Let's Encrypt.

Ten en cuenta que una ACME CA configurada globalmente puede que no se aplique a todos los sitios; consulta los [requisitos de nombres de host](/docs/automatic-https#hostname-requirements) para usar el emisor ACME predeterminado.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
Especifica un archivo PEM que contiene un certificado raiz de confianza para endpoints ACME, si no esta en el almacen de confianza del sistema.

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
Especifica un External Account Binding para usar en todas las transacciones ACME.

Por ejemplo, con credenciales de ejemplo de ZeroSSL:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
Configura el proveedor del [desafio DNS de ACME](/docs/automatic-https#dns-challenge) que se usara para todas las transacciones ACME.

Requiere una compilacion personalizada de Caddy con un plugin para tu proveedor DNS.

Los tokens que siguen al nombre del proveedor configuran el proveedor del mismo modo que se especifican en la subdirectiva `acme` de la [directiva `tls`](/docs/caddyfile/directives/tls#acme).

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
Configura un proveedor DNS predeterminado para usar cuando no haya ninguno especificado localmente en el contexto relevante. Por ejemplo, si el desafio DNS de ACME esta habilitado pero no tiene un proveedor DNS configurado, se usara este valor global por defecto. Tambien se aplica para publicar la configuracion de Encrypted ClientHello (ECH).

Tu binario de Caddy debe estar compilado con el modulo de proveedor DNS especificado para que esto funcione.

Ejemplo, usando credenciales desde una variable de entorno:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Requiere Caddy 2.10 beta 1 o superior.)


##### `ech`
Habilita Encrypted ClientHello (ECH) usando uno o varios nombres de dominio publicos como nombre de servidor en texto plano (SNI) durante el handshake TLS. Con las condiciones adecuadas, ECH puede ayudar a proteger en la red los nombres de dominio de tus sitios. Caddy generara y publicara una configuracion ECH para cada nombre publico indicado. La publicacion permite que clientes compatibles (como navegadores modernos bien configurados) sepan usar ECH para acceder a tus sitios.

Para que funcione correctamente, la configuracion ECH debe publicarse de una forma esperada por los clientes. La mayoria de navegadores (con DNS-over-HTTPS o DNS-over-TLS activado) esperan configuraciones ECH publicadas en registros DNS de tipo HTTPS. Caddy realiza esta publicacion automaticamente, pero debes especificar un proveedor DNS bien sea con la subopcion `dns` o globalmente con la opcion `dns` global ([#dns](#dns)), y tu binario de Caddy debe compilarse con el modulo de proveedor DNS especificado. (Existen builds personalizados en nuestra [pagina de descarga](/download).)

*Avisos de privacidad:*

- Es recomendable **maximizar el tamaño de tu *anonymity set* *** (https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction). Como tal, solemos recomendar que la mayoria de usuarios configuren solo un nombre de dominio publico para proteger todos sus sitios.
- **Tu servidor deberia ser autorizador para los nombres de dominio publicos que especifiques** (es decir, deben apuntar a tu servidor), porque Caddy obtiene un certificado para ellos. Estos certificados son esenciales para que clientes conformes con la especificacion se conecten de forma fiable y segura con ECH en algunos casos. Solo se usan para facilitar un handshake ECH adecuado, no para datos de aplicacion (tus sitios, salvo que definas un sitio igual que tu nombre de dominio publico).
- Cada circunstancia puede ser distinta. Si el riesgo es alto, recomendamos consultar expertos para **revisar tu modelo de amenazas**, porque ECH no es una solucion unica.

Ejemplo usando credenciales desde una variable de entorno para publicar en servidores de nombres alojados en Cloudflare:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Esto deberia hacer que clientes compatibles carguen todos tus sitios con `ech.example.net`, en lugar de los nombres de sitio individuales expuestos en texto plano.

La publicacion correcta requiere que los dominios de tu sitio esten alojados en el proveedor DNS configurado y que los registros se puedan modificar con las credenciales / configuracion del proveedor dados.

(Requiere Caddy 2.10 beta 1 o superior.)


##### `on_demand_tls`
Configura [On-Demand TLS](/docs/automatic-https#on-demand-tls) en los sitios donde este habilitado, pero no lo habilita (para habilitarlo, usa la subdirectiva `on_demand` de la directiva `tls` ([docs](/docs/caddyfile/directives/tls#syntax))). Es obligatorio para entornos de produccion para evitar abusos.

- **ask** hara que Caddy realice una solicitud HTTP al URL indicado, preguntando si un dominio tiene permiso para que se emita un certificado.

  La solicitud incluye un query string `?domain=` con el valor del nombre de dominio.

  Si el endpoint devuelve un codigo de estado `2xx`, Caddy queda autorizado para obtener un certificado para ese nombre. Cualquier otro codigo de estado cancelara la emision del certificado y generara un error en el handshake TLS.

<aside class="tip">

El endpoint `ask` deberia responder tan rapido como sea posible, idealmente en pocos milisegundos. Normalmente, tu endpoint debe hacer una busqueda en tiempo constante en una base de datos con indice por nombre de dominio; evita bucles. Evita hacer consultas DNS ni otras solicitudes de red.

</aside>

- **permission** permite el uso de modulos personalizados para determinar si debe emitirse un certificado para un nombre concreto. El modulo debe implementar la interfaz [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission). Se incluye un modulo de permiso `http`, que es lo que usa la opcion `ask`, y se mantiene como atajo por compatibilidad.

- ⚠️ Las opciones de limite de tasa **interval** y **burst** estuvieron disponibles, pero **no se recomiendan**. Retira de tu configuracion si aun las tienes.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
Especifica el tipo de clave para generar certificados TLS; cambia esto solo si tienes una necesidad concreta.

Los valores posibles son: `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
Define el emisor (o fuente) de certificados TLS.

Esto permite configurar emisores de forma global, en lugar de por sitio como harías con la subdirectiva `issuer` de la [directiva `tls`](/docs/caddyfile/directives/tls#issuer).

Puede repetirse si deseas configurar mas de un emisor para probar. Se probaran en el orden definido.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
Cada cuanto se escanean todos los certificados administrados y cargados en busca de expiracion para activar la renovacion si expiraron.

Predeterminado: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
El periodo de validez que se solicita a la CA al emitir un certificado.

Este valor se usa para calcular el campo `notAfter` de la orden ACME; por lo tanto el sistema debe tener un reloj razonablemente sincronizado. NOTA: no todas las CA lo admiten. Consulta la documentacion de tu CA en ACME para ver si esta permitido y que valores se pueden usar.

Predeterminado: `0` (la CA elige la vida util, normalmente 90 dias)

⚠️ Esta es una funcion experimental. Sujeta a cambios o eliminacion.

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
Cada cuanto se comprueba si los [OCSP staplings <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling) necesitan actualizacion.

Predeterminado: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
Se puede poner en `off` para desactivar OCSP stapling. Es util en entornos donde los responders no son alcanzables por firewall.

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
La relacion (entre 0 y 1) de la vida util del certificado que debe quedar antes de que Caddy intente renovarlo. Por ejemplo, si un certificado tiene una vida util de 90 dias y esta relacion es `0.3333` (valor predeterminado), entonces Caddy intentara renovar continuamente cuando queden 30 dias o menos antes de expirar. Tambien se puede ajustar por sitio con la subdirectiva `renewal_window_ratio` de la directiva `tls` ([docs](/docs/caddyfile/directives/tls#renewal_window_ratio)).

Lo normal es que casi nunca necesites cambiar esto, pero puede ser util para renovar mas tarde en la vida del certificado si tu CA tiene un tiempo de emision muy largo.

Ten en cuenta que esto es solo una sugerencia, ya que los emisores ACME pueden implementar la [extension ARI](https://datatracker.ietf.org/doc/rfc9773/) que indica a un emisor ACME (en este caso Caddy) una ventana de intento de renovacion, y esa ventana puede no coincidir con esta relacion.

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
Si tu CA proporciona multiples cadenas de certificados, puedes usar esta opcion para indicar cual cadena prefiere Caddy. Establece una de las opciones siguientes:

- **smallest** indicara a Caddy que prefiera cadenas con menor tamaño en bytes.

- **root_common_name** es una lista de uno o mas common names; Caddy elegira la primera cadena cuya raiz coincida con alguno de los common names especificados.

- **any_common_name** es una lista de uno o mas common names; Caddy elegira la primera cadena cuyo emisor coincida con alguno de los common names especificados.

Ten en cuenta que configurar `preferred_chains` como opcion global afectara a todos los emisores si no existe ninguna [configuracion de nivel de emisor que sobrescriba](/docs/caddyfile/directives/tls#acme).

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


## Opciones de servidor

Personaliza [servidores HTTP](/docs/json/apps/http/servers/) con ajustes que pueden abarcar multiples sitios y por eso no pueden configurarse correctamente en bloques de sitio. Estas opciones afectan al listener/socket o a otras facilidades bajo la capa HTTP.

Puede especificarse mas de una vez con distintos valores de `listener_address` para configurar opciones distintas por servidor. Por ejemplo, `servers :443` solo se aplicara al servidor que este enlazado a la direccion de escucha `:443`. Omitir la direccion del listener aplicara las opciones a cualquier servidor restante.

<aside class="tip">

Usa el comando [`caddy adapt`](/docs/command-line#caddy-adapt) para encontrar las direcciones de escucha de los servidores de tu Caddyfile.

</aside>


Por ejemplo, para configurar opciones diferentes para los servidores en puertos `:80` y `:443`, especificarias dos bloques `servers`:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

Al usar `servers`, se aplicara **solo** a servidores que **realmente aparezcan** en tu Caddyfile (es decir, los producidos por un bloque de sitio). Recuerda que [Automatic HTTPS](/docs/automatic-https) creara un servidor escuchando en `:80` (o [`http_port`](#http_port)) para servir redirecciones HTTP->HTTPS y resolver el reto HTTP ACME; esto ocurre en tiempo de ejecucion, es decir, _despues_ de que el adaptador del Caddyfile aplique `servers`. En otras palabras, esto significa que `servers` **no se aplicara** a `:80` a menos que declares un bloque de sitio explicitamente como `http://` o `:80`.

<aside class="tip">

Si usas la directiva [`bind`](/docs/caddyfile/directives/bind) o la opcion global [`default_bind`](/docs/caddyfile/options#default_bind), el `listener_address` *DEBE* coincidir con la direccion de enlace combinada con el puerto del bloque de sitio, o las configuraciones no se aplicaran. Por ejemplo:

```caddy
{
	# Esto NO coincidira con el servidor, falta la direccion de enlace
	servers :8080 {
		name private
	}

	# Esto funcionara porque coincide exactamente
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

Un nombre personalizado para asignar a este servidor. Normalmente es util para identificar un servidor por su nombre en logs y metricas. Si no se establece, Caddy lo definira dinamicamente usando el patron `srvX`, donde `X` empieza en `0` y se incrementa segun el numero de servidores en la configuracion.

Recuerda que solo los servidores producidos por bloques de sitio en tu configuracion recibiran ajustes aplicados. [Automatic HTTPS](/docs/automatic-https) crea un servidor `:80` (o [`http_port`](#http_port)) en tiempo de ejecucion, de modo que si quieres renombrarlo, necesitas al menos un sitio `http://` vacio.

Por ejemplo:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

Permite configurar [listener wrappers](/docs/json/apps/http/servers/listener_wrappers/), que pueden modificar el comportamiento del socket de escucha. Se aplican en el orden indicado.

###### `tls`

El listener wrapper `tls` es un wrapper no-op que marca donde debe ir el listener TLS dentro de una cadena de listener wrappers. Solo deberias usarlo si otro listener wrapper debe ir delante del handshake TLS.

###### `http_redirect`

El [`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) permite redirecciones HTTP->HTTPS para conexiones que llegan al puerto TLS como solicitudes HTTP, detectando con los primeros bytes que no es un handshake TLS sino una solicitud HTTP. Es especialmente útil al servir HTTPS en un puerto no estandar (distinto de `443`), ya que los navegadores intentaran HTTP si no se especifica el esquema. Debe colocarse _antes_ del listener wrapper `tls`. Ejemplo:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

El listener wrapper [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) (antes de v2.7.0 solo estaba disponible via plugin) habilita el parsing de [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (popularizado por HAProxy). Esto debe usarse _antes_ del listener wrapper `tls` porque analiza datos de texto plano al inicio de la conexion:

Ten en cuenta que metadatos de PROXY protocol pueden aplicarse a la conexion antes de evaluar matchers o [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies). La IP inmediata del par se pierde para evaluaciones posteriores.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** especifica la duracion maxima de espera para la cabecera PROXY. El valor por defecto es `5s`.

- **allow** es una lista de rangos CIDR de fuentes confiables para recibir cabeceras PROXY. Los sockets unix son confiables por defecto y no forman parte de esta opcion.

- **deny** es una lista de rangos CIDR de fuentes confiables de las que rechazar cabeceras PROXY.

- **fallback_policy** es la accion que se ejecuta si la cabecera PROXY proviene de una direccion que no esta ni en la lista allow ni en deny. La politica por defecto es `ignore`. Valores aceptados para `fallback_policy` son:
	- `ignore`: aceptar la conexion usando la direccion de cabecera PROXY
	- `use`: usar la direccion de la cabecera PROXY
	- `reject`: rechazar la conexion cuando se envia la cabecera PROXY
	- `require`: requerir que se envie la cabecera PROXY, rechazar si no esta presente
	- `skip`: acepta una conexion sin requerir cabecera PROXY.


Por ejemplo, para un servidor HTTPS (que necesite el listener wrapper `tls`) que acepta cabeceras PROXY de un rango IP concreto, y rechaza cabeceras PROXY de otro rango, con un tiempo de espera de 2 segundos:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body** es un [valor de duracion](/docs/conventions#durations) que indica cuanto tiempo se permite leer en una carga util del cliente. Establecer un valor corto distinto de cero puede mitigar ataques slowloris, pero tambien puede afectar a clientes legittimos pero lentos. El valor por defecto es sin limite.

- **read_header** es un [valor de duracion](/docs/conventions#durations) que establece cuanto tiempo se permite leer encabezados de solicitud del cliente. Por defecto, sin limite.

- **write** es un [valor de duracion](/docs/conventions#durations) que establece cuanto tiempo se permite escribir al cliente. Ten en cuenta que establecer un valor bajo al servir archivos grandes puede afectar negativamente a clientes lentos reales. Por defecto, sin limite.

- **idle** es un [valor de duracion](/docs/conventions#durations) que define el tiempo maximo de espera para la siguiente solicitud cuando keep-alive esta habilitado. Predeterminado a 5 minutos para ayudar a evitar agotamiento de recursos.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

El intervalo al que se envian paquetes TCP keepalive para mantener viva la conexion a nivel TCP cuando no se transmiten otros datos. Predeterminado `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

La duracion que una conexion debe estar inactiva antes de enviar paquetes TCP keepalive cuando no se transmiten otros datos. Predeterminado `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

La cantidad maxima de paquetes TCP keepalive que se envian antes de considerar la conexion muerta. Predeterminado `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

Por defecto, 0-RTT (datos tempranos) esta habilitado para listeners QUIC (por ejemplo HTTP/3) para permitir que los clientes envien datos en el primer round trip del handshake TLS, lo que puede mejorar el rendimiento para conexiones repetidas.

Puedes establecerlo en `off` para desactivar 0-RTT para listeners QUIC. Un motivo para desactivar 0-RTT es si se usa el matcher [`remote_ip`](/docs/caddyfile/matchers#remote-ip), que introduce una dependencia sobre la verificacion de la direccion remota si el enrutamiento ocurre antes de completar el handshake TLS. En ese caso se envia una respuesta HTTP 425, pero algunos clientes (navegadores) pueden comportarse de forma incorrecta y no reintentar, de modo que desactivar 0-RTT asegura que los usuarios no vean respuestas 425, con el coste de perder los beneficios de rendimiento de 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

Permite configurar rangos IP (CIDRs) de servidores proxy de los que se deberian confiar solicitudes. Por defecto, no se confia en ningun proxy.

Habilitar esto hace que las solicitudes confiables tengan la IP real del cliente parseada desde encabezados HTTP (por defecto `X-Forwarded-For`; consulta [`client_ip_headers`](#client-ip-headers) para configurar otros encabezados). Si es confiable, la IP del cliente se agrega a los [logs de acceso](/docs/caddyfile/directives/log), esta disponible como marcador de posicion `{client_ip}` [placeholder](/docs/caddyfile/concepts#placeholders), y permite usar el matcher [`client_ip`](/docs/caddyfile/matchers#client-ip). Si la solicitud no viene de un proxy confiable, la IP del cliente se establece en la IP remota de la conexion entrante directa o en la direccion que provea [PROXY protocol](/docs/caddyfile/options#proxy-protocol) si se usa. Por defecto, las IP en cabeceras se analizan de izquierda a derecha. Consulta [`trusted_proxies_strict`](#trusted-proxies-strict) para cambiar este comportamiento.

Algunos matchers o handlers pueden usar el estado de confianza de la solicitud para tomar decisiones. Por ejemplo, si es confiable, el handler [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) proxyea y aumenta los encabezados sensibles `X-Forwarded-*` de la solicitud.

Actualmente, solo el modulo `static` de [fuentes IP](/docs/json/apps/http/servers/trusted_proxies/) viene incluido en la distribucion estandar de Caddy, pero esto puede [extenderse](/docs/extending-caddy) con plugins para mantener una lista dinamica de rangos IP.


###### `static`

Acepta una lista estatica (sin cambios) de rangos IP (CIDRs) para confiar.

Como atajo, se puede usar `private_ranges` para coincidir con todos los rangos privados IPv4 e IPv6. Es lo mismo que especificar estos rangos: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

La sintaxis es:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

Aqui tienes un ejemplo completo, confiando en un rango IPv4 y otro IPv6:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

Cuando [`trusted_proxies`](#trusted-proxies) esta habilitado, las IP en las cabeceras (configuradas por [`client_ip_headers`](#client-ip-headers)) se analizan por defecto de izquierda a derecha. La primera direccion IP no confiable encontrada se convierte en la direccion real del cliente. Desde v2.8, puedes elegir analizar estas cabeceras de derecha a izquierda con `trusted_proxies_strict`. Por defecto, esta opcion esta deshabilitada por compatibilidad con versiones anteriores.

Proxies aguas arriba como HAProxy, CloudFlare, AWS ALB, CloudFront, etc. agregan cada nueva direccion remota conectada a la derecha de `X-Forwarded-For`. Se recomienda habilitar `trusted_proxies_strict` cuando trabajas con estos, ya que la IP mas a la izquierda puede ser suplantada por el cliente.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

Especficamente en el caso de AWS ALB, probablemente quieras habilitar esta opcion. [Segun su documentacion](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15), solo puedes identificar la IP real del cliente configurando el modo XFF en `append`. Esta IP se agrega a la derecha de `X-Forwarded-For` y solo se puede extraer de forma segura mediante `trusted_proxies_strict`.

</aside>

##### `trusted_proxies_unix`

La opcion `trusted_proxies_unix` permite confiar en todas las conexiones que provienen de sockets Unix, lo que es util cuando Caddy esta detras de un reverse proxy (posiblemente otra instancia de Caddy) que se conecta a traves de un socket Unix (es decir, la directiva [`bind`](/docs/caddyfile/directives/bind) esta configurada a un socket unix). Esto esta deshabilitado por defecto.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

Junto con [`trusted_proxies`](#trusted-proxies), permite configurar que encabezados usar para determinar la IP del cliente. Por defecto, solo se considera `X-Forwarded-For`. Se pueden especificar varios campos de encabezado; en ese caso se usa el primer valor no vacio.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

Habilita la coleccion de metricas; necesario antes de consultar metricas o enviarlas con OTLP. Ten en cuenta que las metricas reducen el rendimiento en servidores muy ocupados. (Nuestra comunidad trabaja para mejorar esto. ¡Participa!)

```caddy
{
	metrics
}
```

Puedes añadir la opcion `per_host` para etiquetar metricas con el nombre del host de la metrica.

```caddy
{
	metrics {
		per_host
	}
}
```

Por la posible cardinalidad infinita al observar todos los hosts que puede enviar un cliente, Caddy solo registrara metricas para hosts configurados, mientras que todos los demas hosts (por ejemplo attacker.com) se agrupan bajo la etiqueta "_other". Para forzar la observacion de todos los hosts, y cuando la cardinalidad infinita sea un riesgo aceptable, agrega `observe_catchall_hosts`. Ten en cuenta que agregar `observe_catchall_hosts` no habilita `per_host`. Sin embargo, esto se habilita automaticamente para servidores HTTPS (ya que los certificados proveen algo de proteccion contra cardinalidad sin limites), pero esta deshabilitado para servidores HTTP por defecto para prevenir ataques de cardinalidad desde encabezados Host arbitrarios.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Puedes agregar la opcion `otlp` para enviar las mismas metricas a un endpoint de OpenTelemetry Protocol (OTLP). El exportador se configura mediante las variables de entorno estandar de OpenTelemetry `OTEL_*`, como `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` y `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Por ejemplo:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Consulta [Monitorear Caddy con metricas](/docs/metrics) para mas detalles.

##### `trace`

Registra cada handler individual que se invoca. Requiere que el log se emita con nivel `DEBUG` (puedes hacerlo con la [opcion global `debug`](#debug)).

NOTA: Esto puede registrar la configuracion de tus modulos manejadores HTTP; no lo habilites en contextos inseguros cuando haya datos sensibles en la configuracion.

⚠️ Esta es una caracteristica experimental. Sujeta a cambios o eliminacion.

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

El tamaño maximo que se analizara de los encabezados HTTP del cliente. Si se excede el limite, el servidor respondera con el estado HTTP `431 Request Header Fields Too Large`. Acepta todos los formatos compatibles con [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Por defecto, el limite es `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

Habilita comunicacion full-duplex para solicitudes HTTP/1.

Para solicitudes HTTP/1, el servidor HTTP de Go consume por defecto cualquier parte no leida del cuerpo de solicitud antes de empezar a escribir la respuesta, impidiendo que los handlers lean concurrentemente del request y escriban la respuesta al mismo tiempo. Habilitar esta opcion desactiva ese comportamiento y permite que los handlers continúen leyendo del request mientras escriben la respuesta concurrentemente.

Para solicitudes HTTP/2+, el servidor HTTP de Go siempre permite lecturas y respuestas concurrentes, por lo que esta opcion no tiene efecto.

Prueba exhaustivamente con tus clientes HTTP, ya que algunos clientes antiguos pueden no soportar HTTP/1 full-duplex y causar un bloqueo. Consulta [golang/go#57786](https://github.com/golang/go/issues/57786) para mas informacion.

⚠️ Esta es una caracteristica experimental. Sujeta a cambios o eliminacion.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

Por defecto, los logs de acceso (habilitados con la [directiva `log`](/docs/caddyfile/directives/log)) con encabezados que puedan contener informacion sensible (`Cookie`, `Set-Cookie`, `Authorization` y `Proxy-Authorization`) se registran como `REDACTED`.

Si deseas que estos encabezados no se redacten, puedes habilitar la opcion `log_credentials`.

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

La lista separada por espacios de protocolos HTTP admitidos.

Predeterminado: `h1 h2 h3`

Valores aceptados:
- `h1` para HTTP/1.1
- `h2` para HTTP/2
- `h2c` para HTTP/2 over cleartext
- `h3` para HTTP/3

Actualmente, habilitar HTTP/2 (incluyendo H2C) implica necesariamente habilitar HTTP/1.1 porque la libreria estandar de Go no permite deshabilitar HTTP/1.1 cuando se usa su servidor HTTP. Sin embargo, HTTP/1.1 o HTTP/3 se pueden habilitar de forma independiente.

Ten en cuenta que H2C ("HTTP/2 en texto plano" o "H2 sobre TCP") y HTTP/3 no estan implementados por la libreria estandar de Go, por lo que algunas funcionalidades pueden estar limitadas. Recomendamos no habilitar H2C salvo que sea absolutamente necesario para tu aplicacion.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

Habilitar esto requiere que la cabecera `Host` de una solicitud coincida con el valor de `ServerName` enviado por el ClientHello TLS del cliente, como salvaguarda necesaria al usar autenticacion TLS de cliente. Si hay una discrepancia, se devuelve al cliente el estado HTTP `421 Misdirected Request`.

Esta opcion se activara automaticamente si se configura la [autenticacion de cliente](/docs/caddyfile/directives/tls#client_auth). Esto evita el bypass de autenticacion TLS del cliente (domain fronting) que podria explotarse enviando un valor de SNI sin proteger durante un handshake TLS, y luego colocando un dominio protegido en la cabecera Host tras establecer la conexion. Este comportamiento es seguro por defecto, pero puedes desactivarlo explicitamente con `insecure_off`; por ejemplo, en el caso de ejecutar un proxy donde se desea domain fronting y no haya restriccion de acceso por nombre de host.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



## Sistemas de archivos

La opcion global `filesystem` permite declarar uno o mas sistemas de archivos que se pueden usar para E/S de archivos.

Esto puede permitirte conectarte a un sistema de archivos remoto en la nube, o una base de datos con una interfaz tipo archivo, e incluso leer archivos incrustados dentro del binario de Caddy.

Los sistemas de archivos se declaran con un nombre para identificarlos. Esto significa que puedes conectarte a mas de un sistema de archivos del mismo tipo si lo necesitas.

Por defecto, Caddy no incluye modulos de sistemas de archivos, por lo que deberas compilar Caddy con un plugin para el sistema de archivos que quieras usar.

#### Ejemplo

Usando un modulo `custom` de sistema de archivos hipotetico, puedes declarar dos sistemas:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



## Opciones PKI

La aplicacion PKI (Public Key Infrastructure) es la base de [Local HTTPS](/docs/automatic-https#local-https) y [ACME server](/docs/caddyfile/directives/acme_server) de Caddy. La aplicacion define autoridades de certificacion (CAs) capaces de firmar certificados.

El ID de CA predeterminado es `local`. Si se omite el ID al configurar `ca`, se asume `local`.

##### `name`
El nombre visible para el usuario de la autoridad certificadora.

Predeterminado: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
El nombre a introducir en el campo CommonName del certificado raiz.

Predeterminado: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
El nombre a introducir en el campo CommonName de los certificados intermedios.

Predeterminado: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
La [duracion](/docs/conventions#durations) durante la que los certificados intermedios son validos. Este valor **debe** ser menor que la vida util del certificado raiz (`3600d` o 10 años).

Predeterminado: `7d`. _No se recomienda_ cambiarlo, salvo que sea absolutamente necesario.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
La [duracion](/docs/conventions#durations) de cada cuanto se debe comprobar si se deben renovar certificados intermedios (y raiz, cuando corresponda).

Predeterminado: `10m`. _No se recomienda_ cambiarlo, salvo que sea absolutamente necesario.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
La relacion (entre 0 y 1) de la vida util del certificado que debe quedar para que Caddy intente renovar certificados. Por ejemplo, si un certificado tiene vida util de 1 año y esta relacion es `0.2` (valor predeterminado), Caddy intentara renovar continuamente cuando queden 73 dias o menos antes del vencimiento.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
Un par de claves (certificado y clave privada) para usar como raiz de la CA. Si no se especifica, se generara y gestionara automaticamente.

- **format** es el formato en el que se proporcionan el certificado y la clave privada. Actualmente solo se admite `pem_file`, que es el predeterminado, por lo que este campo es opcional.
- **cert** es el certificado. Debe ser la ruta a un archivo PEM, al usar el formato `pem_file`.
- **key** es la clave privada. Debe ser la ruta a un archivo PEM, al usar el formato `pem_file`.

##### `intermediate`
Un par de claves (certificado y clave privada) para usar como intermedio de la CA. Si no se especifica, se generara y gestionara automaticamente.

- **format** es el formato en el que se proporcionan el certificado y la clave privada. Actualmente solo se admite `pem_file`, que es el predeterminado, por lo que este campo es opcional.
- **cert** es el certificado. Debe ser la ruta a un archivo PEM, al usar el formato `pem_file`.
- **key** es la clave privada. Debe ser la ruta a un archivo PEM, al usar el formato `pem_file`.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


## Opciones de eventos

Los modulos de Caddy emiten eventos cuando ocurren cosas interesantes (o estan a punto de ocurrir).

Los eventos suelen incluir una carga util de metadatos. La mejor forma de aprender sobre los eventos y sus cargas es desde la documentacion de cada modulo, pero tambien puedes verlos habilitando la opcion global [`debug`](#debug) y leyendo los logs.

##### `on`

Vincula un controlador de eventos al evento con nombre. Especifica el nombre del modulo de controlador de eventos, seguido de su configuración.

Por ejemplo, para ejecutar un comando tras obtener un certificado ([plugin de terceros <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec) requerido), con una parte de la carga del evento pasada al script usando un marcador:

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

### Eventos

Estos eventos estandar son emitidos por Caddy:

- [`eventos tls` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- Eventos [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#events)

Los plugins tambien pueden emitir eventos, asi que consulta su documentacion para obtener detalles.
