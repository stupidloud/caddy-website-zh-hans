---
title: reverse_proxy (Caddyfile directive)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="reverse_proxy"></a>
# reverse_proxy

Proxy proxy a una o más aplicaciones de backend mediante transporte configurable, balanceo de carga, comprobación de estado, manipulación de solicitudes y opciones de almacenamiento en búfer.

- [Sintaxis](#syntax)
- [Upstreams](#upstreams)
  - [Direcciones de upstreams](#upstream-addresses)
  - [Upstreams dinámicos](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Balanceo de carga](#load-balancing)
  - [Comprobaciones de estado activas](#active-health-checks)
  - [Comprobaciones de estado pasivas](#passive-health-checks)
  - [Eventos](#events)
- [Streaming](#streaming)
- [Encabezados](#headers)
- [Reescrituras](#rewrites)
- [Transportes](#transports)
  - [El transporte `http`](#the-http-transport)
  - [El transporte `fastcgi`](#the-fastcgi-transport)
- [Interceptación de respuestas](#intercepting-responses)
- [Ejemplos](#examples)



<a id="syntax"></a>
## Syntax

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# load balancing
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# active health checking
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive health checking
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# request/header manipulation
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# optionally intercept responses from upstream
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# special directives only available in handle_response
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



<a id="upstreams"></a>
## Upstreams

- **&lt;upstreams...&gt;** es una lista de backends al que reenviar las solicitudes.
- **to** <span id="to"/> es una forma alternativa de especificar la lista de backends, uno (o más) por línea.
- **dynamic** <span id="dynamic"/> configura un módulo de *dynamic upstreams*. Esto permite obtener la lista de backends de forma dinámica en cada solicitud. Consulta [dynamic upstreams](#dynamic-upstreams) más abajo para ver una descripción de los módulos dinámicos estándar. Los backends dinámicos se obtienen en cada iteración del ciclo proxy (es decir, potencialmente varias veces por solicitud si los reintentos de balanceo están habilitados) y tendrán preferencia sobre los backends estáticos. Si ocurre un error, `reverse_proxy` volverá a usar cualquier backend estático configurado.


<a id="upstream-addresses"></a>
### Upstream addresses

Las direcciones de upstream estático pueden tener forma de una URL que solo contenga esquema y host/puerto, o una [dirección de red de Caddy](/docs/conventions#network-addresses) convencional. Ejemplos válidos:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

Por defecto, las conexiones se realizan al upstream usando HTTP sin cifrar. Al usar la forma URL, un esquema puede usarse para definir atajos de algunos valores predeterminados de [`transport`](#transports).
- Usar `https://` como esquema hace que se utilice el [`http` transport](#the-http-transport) con [`tls`](#tls) activado.

  Además, puede que necesites sobrescribir el encabezado `Host` para que coincida con el valor TLS SNI, que los servidores usan para enrutamiento y selección de certificado. Consulta la sección [HTTPS](#https) más abajo para más detalles.

- Usar `h2c://` como esquema hará que se utilice el [`http` transport](#the-http-transport) con las [versiones HTTP](#versions) establecidas para permitir conexiones HTTP/2 en texto plano.

- Usar `http://` como esquema es idéntico a omitir el esquema, ya que HTTP ya es el valor predeterminado. Esta sintaxis se incluye para mantener simetría con los demás atajos de esquema.

Los esquemas no se pueden mezclar, ya que modifican la configuración de transporte común (un transporte con TLS no puede transportar tanto HTTPS como HTTP en texto plano). Cualquier configuración de transporte explícita no se sobrescribirá, y omitir esquemas o usar otros puertos no asumirá un transporte concreto.

Cuando se use IPv6 con una zona (por ejemplo direcciones link-local con una interfaz de red específica), **no** se puede usar un esquema como atajo porque `%` provocará un error de análisis de URL; configura el transporte de forma explícita.

Al usar la forma de [dirección de red](/docs/conventions#network-addresses), el tipo de red se especifica como prefijo de la dirección upstream. Esto no puede combinarse con un esquema URL. Como caso especial, `unix+h2c/` se admite como atajo para la red `unix/` junto con los mismos efectos que el esquema `h2c://`. Los rangos de puertos se admiten como atajo y se expanden a múltiples backends con el mismo host.

Las direcciones de upstream **no** pueden contener rutas o cadenas de consulta, porque eso implicaría reescribir la solicitud mientras se hace proxy, y ese comportamiento no está definido ni soportado. Puedes usar la directiva [`rewrite`](/docs/caddyfile/directives/rewrite) si necesitas eso.

Si la dirección no es una URL (es decir, no tiene esquema), se pueden usar [placeholders](/docs/caddyfile/concepts#placeholders), pero esto convierte el upstream en *dinámicamente estático*, lo que significa que potencialmente muchos backends distintos actúan como un único upstream estático para comprobaciones de estado y balanceo de carga. En la medida de lo posible, recomendamos usar un módulo de [dynamic upstreams](#dynamic-upstreams). Cuando se usan placeholders, se **debe** incluir un puerto (ya sea por sustitución del placeholder o como sufijo estático de la dirección).


<a id="dynamic-upstreams"></a>
### Dynamic upstreams

El reverse proxy de Caddy incluye varios módulos de upstream dinámico. Ten en cuenta que usarlos tiene implicaciones para el balanceo de carga y las comprobaciones de salud, según la configuración de política concreta: los health checks activos no se ejecutan para upstreams dinámicos; y el balanceo de carga y las comprobaciones pasivas funcionan mejor si la lista de backends es relativamente estable y consistente (especialmente con round-robin). Idealmente, los módulos dinámicos solo devuelven backends sanos y utilizables.


<a id="srv"></a>
#### SRV

Recupera los backends de registros DNS SRV.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** es el nombre de dominio completo del registro que se consulta (es decir, `_service._proto.name`).
- **service** es el componente de servicio del nombre completo.
- **proto** es el componente de protocolo del nombre completo. Puede ser `tcp` o `udp`.
- **name** es el componente de nombre. O, si `service` y `proto` están vacíos, es el nombre de dominio completo a consultar.
- **refresh** controla con qué frecuencia se actualiza la caché. Valor predeterminado: `1m`
- **resolvers** es la lista de resolutores DNS para sobrescribir los resolutores del sistema.
- **dial_timeout** es el tiempo de espera para hacer la consulta.
- **dial_fallback_delay** es cuánto esperar antes de crear una conexión RFC 6555 Fast Fallback. Predeterminado: `300ms`


<a id="aaaaa"></a>
#### A/AAAA

Recupera los backends desde registros DNS A/AAAA.

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** es el nombre de dominio a consultar.
- **port** es el puerto a usar para el backend.
- **refresh** indica cada cuánto se actualiza la caché. Valor predeterminado: `1m`
- **resolvers** es la lista de resolutores DNS para sobrescribir los resolutores del sistema.
- **dial_timeout** es el tiempo de espera para realizar la consulta.
- **dial_fallback_delay** es cuánto esperar antes de crear una conexión RFC 6555 Fast Fallback. Predeterminado: `300ms`
- **versions** es la lista de versiones IP a resolver. Predeterminado: `ipv4 ipv6`, que corresponden respectivamente a registros A y AAAA.


<a id="multi"></a>
#### Multi

Añade los resultados de varios módulos dinámicos. Útil si quieres fuentes redundantes de backends, por ejemplo: un clúster primario de SRV respaldado por un clúster secundario de SRV.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** es el nombre del módulo de dynamic upstream seguido de su configuración. Se puede especificar más de uno.




<a id="load-balancing"></a>
## Load balancing

El balanceo de carga normalmente se usa para repartir el tráfico entre varios backends. Habilitando reintentos, también puede usarse con uno o más backends, reteniendo solicitudes hasta que se pueda seleccionar un backend saludable (por ejemplo, para esperar y mitigar errores durante reinicios o redeploys).

Esto está habilitado por defecto con la política `random`. Los reintentos están deshabilitados de forma predeterminada.

- **lb_policy** <span id="lb_policy"/> es el nombre de la política de balanceo de carga y sus opciones. Predeterminado: `random`.

  Para las políticas con hashing, se usa el algoritmo [highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) para asegurar que un cliente o solicitud con la misma clave hash se asigne al mismo upstream, incluso si cambia la lista de backends.

  Algunas políticas admiten `fallback` como opción, si se indica; en ese caso usan un [bloque](/docs/caddyfile/concepts#blocks) con `fallback <policy>` que toma otra política de balanceo. Para esas políticas, el fallback predeterminado es `random`. Configurar un fallback permite usar una política secundaria si la principal no selecciona una opción, lo que permite combinaciones potentes. Puedes anidar fallbacks varias veces si lo deseas.
  
  Por ejemplo, `header` puede usarse como primaria para permitir que los desarrolladores elijan un upstream específico, con fallback `first` para todas las demás conexiones a fin de implementar failover primario/secundario.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` elige aleatoriamente un upstream

	- `random_choose <n>` selecciona dos o más backends aleatoriamente y luego elige uno con menor carga (`n` suele ser 2)

	- `first` elige el primer backend disponible según el orden de configuración, lo que permite failover primario/secundario; recuerda habilitar health checks junto con esto, de lo contrario el failover no ocurrirá

	- `round_robin` recorre cada upstream por turno

	- `weighted_round_robin <weights...>` recorre cada upstream respetando los pesos dados. La cantidad de pesos debe coincidir con la cantidad de backends configurados. Los pesos deben ser enteros no negativos. Con dos backends y pesos `5 1`, el primer upstream se seleccionaría 5 veces seguidas antes de seleccionar una vez el segundo, y luego se repite el ciclo. Si se usa `0` como peso, se desactiva la selección de ese upstream para nuevas solicitudes.

	- `least_conn` elige el upstream con menos solicitudes actuales; si más de un host tiene el mismo mínimo, se elige uno al azar

	- `ip_hash` asigna la IP remota (el peer inmediato) a un upstream pegajoso

	- `client_ip_hash` asigna la IP del cliente a un upstream pegajoso; esto se combina mejor con la opción global [`servers > trusted_proxies` ](/docs/caddyfile/options#trusted-proxies) que permite analizar la IP real del cliente, de lo contrario actúa igual que `ip_hash`

	- `uri_hash` asigna la URI de la solicitud (ruta y query) a un upstream pegajoso

	- `query [key]` asigna el query de una solicitud a un upstream pegajoso, hasheando el valor del query; si no está presente la clave especificada, se usa la política de fallback para seleccionar el upstream (`random` de forma predeterminada)

	- `header [field]` asigna un encabezado de solicitud a un upstream pegajoso, hasheando el valor del encabezado; si no existe ese encabezado, se usa la política de fallback para seleccionar el upstream (`random` por defecto)

	- `cookie [<name> [<secret>]]` en la primera solicitud de un cliente (cuando no existe cookie), se usa la política de fallback para elegir el upstream (`random` por defecto) y se añade un encabezado `Set-Cookie` a la respuesta (nombre de cookie predeterminado `lb` si no se especifica). El valor de la cookie es la dirección de conexión del upstream elegido, hasheada con HMAC-SHA256 (usando `<secret>` como secreto compartido, cadena vacía si no se especifica).
	
	  En solicitudes posteriores cuando la cookie está presente, ese valor se asignará al mismo upstream si está disponible; si no está o no se encuentra, se elige un nuevo upstream con la política de fallback y la cookie se vuelve a incluir en la respuesta.

	  Si quieres usar un upstream concreto para depuración, puedes calcular la cookie con el secreto y establecerla en tu cliente HTTP (navegador u otro). Por ejemplo, en PHP puedes ejecutar:
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```

	  También puedes definirla desde la consola Javascript, por ejemplo para fijar la cookie llamada `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> indica cuántas veces reintentar la selección de backends disponibles para cada solicitud si el siguiente host disponible está caído. Por defecto los reintentos están deshabilitados (cero).

  Si también se configura [`lb_try_duration`](#lb_try_duration), los reintentos pueden detenerse antes si se alcanza la duración. En otras palabras, la duración de reintento tiene prioridad sobre la cuenta de reintentos.

- **lb_try_duration** <span id="lb_try_duration"/> es un [valor de duración](/docs/conventions#durations) que define cuánto intentar seleccionar backends disponibles para cada solicitud si el siguiente host disponible está caído. Por defecto, los reintentos están desactivados (duración cero).

  Los clientes esperarán hasta ese tiempo mientras el balanceador trata de encontrar un host upstream disponible. Un punto de partida razonable podría ser `5s`, ya que el timeout de conexión del transport HTTP es `3s`; esto debería permitir al menos un reintento si no se puede alcanzar el upstream seleccionado inicialmente, pero ajústalo según tu caso.

- **lb_try_interval** <span id="lb_try_interval"/> es un [valor de duración](/docs/conventions#durations) que define cuánto esperar entre la selección del siguiente host del grupo. El valor predeterminado es `250ms`. Solo es relevante cuando una solicitud a un host upstream falla. Ten en cuenta que establecerlo en `0` con un `lb_try_duration` distinto de cero puede causar uso alto de CPU si todos los backends están caídos y la latencia es muy baja.

- **lb_retry_match** <span id="lb_retry_match"/> limita para qué solicitudes se permiten reintentos. Una solicitud debe cumplir esta condición para reintentar si la conexión al upstream tuvo éxito pero el round-trip posterior falló. Si la conexión al upstream falló, el reintento siempre se permite. Por defecto, solo se reintenta `GET`.

  La sintaxis de esta opción es igual a la de los [matchers de solicitud con nombre](/docs/caddyfile/matchers#named-matchers), pero sin `@name`. Si solo necesitas un matcher, puedes configurarlo en la misma línea. Para varios matchers, necesitas un bloque.



<a id="active-health-checks"></a>
### Active health checks

Las comprobaciones de estado activas ejecutan verificaciones periódicas en segundo plano. Para habilitarlas se requieren `health_uri` o `health_port`.

- **health_uri** <span id="health_uri"/> es la ruta del URI (y consulta opcional) para comprobaciones activas.

- **health_upstream** <span id="health_upstream"/> es el ip:port usado para health checks activos, si es distinto al upstream. Debe usarse junto con `health_header` y `{http.reverse_proxy.active.target_upstream}`.

- **health_port** <span id="health_port"/> es el puerto a usar en comprobaciones activas, si es distinto al puerto del upstream. Se ignora si se usa `health_upstream`.

- **health_interval** <span id="health_interval"/> es un [valor de duración](/docs/conventions#durations) que define la frecuencia de comprobaciones activas. Predeterminado: `30s`.

- **health_passes** <span id="health_passes"/> es el número de comprobaciones exitosas consecutivas para marcar un backend como saludable de nuevo. Predeterminado: `1`.

- **health_fails** <span id="health_fails"/> es el número de comprobaciones fallidas consecutivas para marcar un backend como no saludable. Predeterminado: `1`.

- **health_timeout** <span id="health_timeout"/> es un [valor de duración](/docs/conventions#durations) que define cuánto esperar por una respuesta antes de marcar el backend como caído. Predeterminado: `5s`.

- **health_method** <span id="health_method"/> es el método HTTP para la comprobación activa. Predeterminado: `GET`.

- **health_status** <span id="health_status"/> es el código HTTP esperado en un backend saludable. Puede ser un código de 3 dígitos o una clase de código que termine en `xx`. Por ejemplo: `200` (valor predeterminado), o `2xx`.

- **health_request_body** <span id="health_request_body"/> es la cadena que representa el cuerpo de la petición a enviar en la comprobación activa.

- **health_body** <span id="health_body"/> es una subcadena o expresión regular para comparar con el cuerpo de respuesta de una comprobación activa. Si el backend no devuelve un cuerpo que coincida, se marca como caído.

- **health_follow_redirects** <span id="health_follow_redirects"/> hará que la comprobación siga redirecciones del upstream. De forma predeterminada, una respuesta de redirección se cuenta como fallo.

- **health_headers** <span id="health_headers"/> permite indicar encabezados para las solicitudes de comprobación activa. Esto es útil si necesitas cambiar el encabezado `Host` o proporcionar autenticación al backend dentro de estas comprobaciones.



<a id="passive-health-checks"></a>
### Passive health checks

Las comprobaciones pasivas ocurren junto a solicitudes proxificadas reales. Para activarlas se requiere `fail_duration`.

- **fail_duration** <span id="fail_duration"/> es un [valor de duración](/docs/conventions#durations) que define cuánto recordar una solicitud fallida. Un valor > `0` habilita la comprobación pasiva; el valor predeterminado es `0` (off). Un punto de partida razonable podría ser `30s` para equilibrar tasas de error y capacidad de recuperación cuando un upstream no saludable vuelve a estar en línea; pero puedes ajustarlo según el caso.

- **max_fails** <span id="max_fails"/> es el número máximo de solicitudes fallidas dentro de `fail_duration` necesarias para considerar un backend como caído; debe ser `>= 1`; el predeterminado es `1`.

- **unhealthy_status** <span id="unhealthy_status"/> cuenta una solicitud como fallida si la respuesta devuelve uno de estos códigos. Puede ser un código de 3 dígitos o una clase terminada en `xx`, por ejemplo `404` o `5xx`.

- **unhealthy_latency** <span id="unhealthy_latency"/> es un [valor de duración](/docs/conventions#durations) que cuenta una solicitud como fallida si tarda tanto en responder.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> es el número permitido de solicitudes simultáneas a un backend antes de marcarlo como caído. En otras palabras, si un backend concreto ya está gestionando ese número de solicitudes, se considera "sobrecargado" y se priorizan otros backends.

  Debe ser un número razonablemente alto; al configurarlo, el proxy limita a `unhealthy_request_count × upstreams_count` el total de solicitudes simultáneas y las que excedan ese límite devolverán error por falta de backends disponibles.


<a id="events"></a>
## Events

Cuando un upstream pasa de saludable a no saludable o viceversa, se emite [un evento](/docs/caddyfile/options#event-options). Esos eventos pueden activar otras acciones, como enviar una notificación o escribir un log. Los eventos son:

- `healthy` se emite cuando un upstream se marca como saludable tras haber estado no saludable.
- `unhealthy` se emite cuando un upstream se marca como no saludable tras haber estado saludable.

En ambos casos, `host` se incluye como metadato del evento para identificar el upstream cuyo estado cambió. Puede usarse como placeholder con `{event.data.host}` en el handler `exec`, por ejemplo.


<a id="streaming"></a>
## Streaming

Por defecto, el proxy almacena parte de la respuesta en búfer por eficiencia en la transmisión.

El proxy también admite conexiones WebSocket, realizando primero la petición de upgrade HTTP y luego cambiando la conexión a un túnel bidireccional.

<aside class="tip">

Por defecto, las conexiones WebSocket se cierran de forma forzada (con un mensaje de control Close enviado al cliente y al upstream) cuando la configuración se recarga. Cada solicitud conserva una referencia a la configuración, por lo que cerrar conexiones antiguas es necesario para controlar el uso de memoria. Este comportamiento de cierre se puede personalizar con las opciones [`stream_timeout`](#stream_timeout) y [`stream_close_delay`](#stream_close_delay).

</aside>

- **flush_interval** <span id="flush_interval"/> es un [valor de duración](/docs/conventions#durations) que ajusta con qué frecuencia Caddy vacía el búfer de respuesta al cliente. Por defecto, no se hace flushing periódico. Un valor negativo (normalmente -1) activa el "modo baja latencia", que desactiva completamente el buffer de respuesta y vacía inmediatamente después de cada escritura al cliente, y no cancela la solicitud al backend aunque el cliente se desconecte pronto. Esta opción se ignora y las respuestas se vacían inmediatamente si ocurre alguno de estos casos:
	- `Content-Type: text/event-stream`
	- `Content-Length` desconocido
	- HTTP/2 en ambos extremos del proxy, `Content-Length` desconocido y `Accept-Encoding` no configurado o es `identity`

- **request_buffers** <span id="request_buffers"/> hará que el proxy lea hasta `<size>` bytes del cuerpo de la solicitud en un búfer antes de enviarla al upstream. Esto es ineficiente y solo debería hacerse si el upstream requiere leer cuerpos sin demoras (algo que debería corregirse en la aplicación upstream). Acepta todos los formatos de tamaño compatibles con [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **response_buffers** <span id="response_buffers"/> hará que el proxy lea hasta `<size>` bytes del cuerpo de la respuesta en un búfer antes de devolverla al cliente. Evita esto siempre que sea posible por rendimiento, pero puede ser útil si el backend tiene restricciones de memoria más estrictas. Acepta todos los formatos de tamaño compatibles con [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **stream_timeout** <span id="stream_timeout"/> es un [valor de duración](/docs/conventions#durations) tras el cual las solicitudes en streaming como WebSockets se cerrarán forzosamente al alcanzar el timeout. Esto termina conexiones si permanecen abiertas demasiado tiempo. Un punto de inicio razonable puede ser `24h` para descartar conexiones de más de un día. Predeterminado: sin timeout.

- **stream_close_delay** <span id="stream_close_delay"/> es un [valor de duración](/docs/conventions#durations) que retrasa el cierre forzado de solicitudes en streaming como WebSockets cuando la configuración se descarga; en su lugar, el stream permanece abierto hasta completar el retraso. En otras palabras, así se evitan cierres inmediatos al recargarse la configuración de Caddy. Puede ser conveniente para evitar una avalancha de reconexiones de clientes que fueron cerrados por la recarga anterior. Un punto de partida razonable podría ser `5m` para dar a los usuarios 5 minutos para abandonar la página naturalmente tras la recarga. Predeterminado: sin retardo.



<a id="headers"></a>
## Headers

El proxy puede **manipular encabezados** entre él y el backend:

- **header_up** <span id="header_up"/> establece, añade (con prefijo `+`), elimina (con prefijo `-`) o reemplaza (con dos argumentos, búsqueda y reemplazo) en un encabezado de solicitud dirigido al backend.

- **header_down** <span id="header_down"/> establece, añade (con prefijo `+`), elimina (con prefijo `-`) o reemplaza (con dos argumentos, búsqueda y reemplazo) en un encabezado de respuesta recibido desde el backend.

Por ejemplo, para establecer un encabezado de solicitud sobreescribiendo valores existentes:

```caddy-d
header_up Some-Header "the value"
```

Para añadir un encabezado de respuesta; ten en cuenta que puede haber múltiples valores para un mismo campo:

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

Para eliminar un encabezado de solicitud, evitando que llegue al backend:

```caddy-d
header_up -Some-Header
```

Para eliminar todos los encabezados de solicitud que coincidan por sufijo:

```caddy-d
header_up -Some-*
```

Para eliminar _todos_ los encabezados de solicitud y añadir solo los que quieras (no recomendado):

```caddy-d
header_up -*
```

Para realizar un reemplazo con expresión regular en un encabezado de solicitud:

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

El lenguaje de expresión regular usado es RE2, incluido en Go. Consulta la [referencia de sintaxis de RE2](https://github.com/google/re2/wiki/Syntax) y la [descripción general de sintaxis Go regexp](https://pkg.go.dev/regexp/syntax). La cadena de reemplazo se [expande](https://pkg.go.dev/regexp#Regexp.Expand), permitiendo usar valores capturados, como `$1` para el primer grupo.


<a id="defaults"></a>
### Defaults

Por defecto, Caddy reenvía los encabezados entrantes&mdash;incluido `Host`&mdash;al backend sin cambios, con tres excepciones:

- Configura o complementa el encabezado [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Configura el encabezado [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Configura el encabezado [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"></span> Para estos encabezados `X-Forwarded-*`, por defecto, el proxy ignorará sus valores de la solicitud de entrada para evitar suplantación.

Si Caddy no es el primer servidor que reciben tus clientes (por ejemplo, si hay un CDN delante de Caddy), puedes configurar `trusted_proxies` con una lista de rangos IP (CIDR) desde los que las solicitudes entrantes se consideran confiables para estos encabezados.

Se recomienda encarecidamente configurar esto mediante la opción global [`servers > trusted_proxies` ](/docs/caddyfile/options#trusted-proxies) en lugar de en el proxy, para que se aplique a todos los handlers proxy de tu servidor y habilite además el análisis de IP de cliente.

<aside class="tip">

Si usas Cloudflare delante de Caddy, ten en cuenta que podrías ser vulnerable a la suplantación del encabezado `X-Forwarded-For`. En [Authelia](https://www.authelia.com) está documentado un [workaround](https://www.authelia.com/integration/proxies/forwarded-headers/) para configurar Cloudflare de manera que ignore los valores entrantes de ese encabezado.

</aside>

Además, al usar el [`http` transport](#the-http-transport), se añadirá `Accept-Encoding: gzip` si falta en la solicitud del cliente. Esto permite que el upstream sirva contenido comprimido si puede. Este comportamiento se puede desactivar con [`compression off`](#compression) en el transport.


<a id="https"></a>
### HTTPS

Como la mayoría de encabezados conservan su valor original al hacer proxy, suele ser necesario sobrescribir `Host` con la dirección de upstream configurada al usar HTTPS, para que `Host` coincida con el valor TLS ServerName:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Desde Caddy v2.11.0 esto se hace automáticamente, por lo que ya no es necesario establecer `Host` explícitamente al hacer proxy a HTTPS. Si quieres desactivar ese comportamiento, puedes fijar `Host` a su valor original (aunque rara vez tiene sentido):

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

El encabezado `X-Forwarded-Host` sigue pasando [por defecto](#defaults), así que el upstream puede seguir usándolo si necesita conocer el valor original de `Host`.

Lo mismo aplica al terminar TLS en caddy y hacer proxy vía HTTP, ya sea a un puerto o a un socket unix. De hecho, Caddy debe recibir el Host correcto cuando es objetivo de `reverse_proxy`. En el caso de sockets unix, `upstream_hostport` será la ruta del socket y el Host debe establecerse explícitamente.



<a id="rewrites"></a>
## Rewrites

Por defecto, Caddy realiza la solicitud upstream con el mismo método y URI HTTP que la solicitud entrante, salvo que se haya realizado una reescritura en la cadena de middleware antes de llegar a `reverse_proxy`.

Antes de hacer proxy, la solicitud se clona; esto garantiza que cambios hechos por el handler no “se escapen” a otros handlers. Esto es útil cuando el manejo debe continuar después del proxy.

Además de las [manipulaciones de encabezados](#headers), el método y URI pueden cambiarse antes de enviarlas al upstream:

- **method** <span id="method"/> cambia el método HTTP de la solicitud clonada. Si se cambia a `GET` o `HEAD`, el cuerpo de la solicitud entrante **no** se envía upstream por este handler. Es útil si quieres que otro handler consuma el cuerpo.
- **rewrite** <span id="rewrite"/> cambia la URI (ruta y query) de la solicitud clonada. Es similar a la directiva [`rewrite`](/docs/caddyfile/directives/rewrite), excepto que no persiste la reescritura fuera del alcance de este handler.

Estas reescrituras son útiles para patrones de "pre-check requests", donde una solicitud se envía a otro servidor para ayudar a decidir cómo continuar con la solicitud actual.

Por ejemplo, la solicitud se podría enviar a una pasarela de autenticación para decidir si proviene de un usuario autenticado (por ejemplo, la cookie de sesión está presente) y debe continuar, o si se debe redirigir a una página de inicio de sesión. Para este patrón, Caddy ofrece la directiva de acceso rápido [`forward_auth`](/docs/caddyfile/directives/forward_auth) para saltarse la mayor parte del boilerplate de configuración.




<a id="transports"></a>
## Transports

El **transport** del proxy de Caddy es intercambiable (pluggable):

- **transport** <span id="transport"/> define cómo comunicarse con el backend. Predeterminado: `http`.


<a id="the-http-transport"></a>
### The `http` transport

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> es el tamaño, en bytes, del búfer de lectura. Acepta todos los formatos compatibles con [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Predeterminado: `4KiB`.

- **write_buffer** <span id="write_buffer"/> es el tamaño, en bytes, del búfer de escritura. Acepta todos los formatos compatibles con [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Predeterminado: `4KiB`.

- **max_response_header** <span id="max_response_header"/> es la máxima cantidad de bytes a leer de los encabezados de respuesta. Acepta todos los formatos compatibles con [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Predeterminado: `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> habilita [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (popularizado por HAProxy) en la conexión al upstream, anteponiendo los datos reales de IP del cliente. Se usa mejor con la opción global [`servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) si Caddy está detrás de otro proxy. Se soportan las versiones `v1` y `v2`. Solo debe usarse si sabes que el servidor upstream puede analizar PROXY protocol. Por defecto está desactivado.

- **dial_timeout** <span id="dial_timeout"/> es el máximo [duration](/docs/conventions#durations) al esperar al conectar con el socket de upstream. Predeterminado: `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> es el máximo [duration](/docs/conventions#durations) a esperar antes de crear una conexión RFC 6555 Fast Fallback. Un valor negativo lo desactiva. Predeterminado: `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> es el máximo [duration](/docs/conventions#durations) para esperar la lectura de los encabezados de respuesta desde el upstream. Predeterminado: sin timeout.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> es el máximo [duration](/docs/conventions#durations) para esperar los primeros encabezados de respuesta del upstream tras escribir completos los encabezados de solicitud si esta tiene `Expect: 100-continue`. Sin timeout por defecto.

- **read_timeout** <span id="read_timeout"/> es el máximo [duration](/docs/conventions#durations) para la siguiente lectura desde el backend. Sin timeout por defecto.

- **write_timeout** <span id="write_timeout"/> es el máximo [duration](/docs/conventions#durations) para la siguiente escritura hacia el backend. Sin timeout por defecto.

- **resolvers** <span id="resolvers"/> es la lista de resolutores DNS para sobrescribir resolutores del sistema.

- **tls** <span id="tls"/> usa HTTPS con el backend. Se activa automáticamente si especificas backends usando el esquema `https://`, o si configuras cualquiera de las opciones `tls_*` siguientes.

- **tls_client_auth** <span id="tls_client_auth"/> habilita autenticación TLS del cliente de dos formas: (1) indicando un nombre de dominio para el que Caddy debe obtener y renovar un certificado, o (2) indicando un certificado y clave para presentarse en autenticación TLS con el backend.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> desactiva la verificación del handshake TLS, haciendo la conexión insegura y vulnerable a ataques man-in-the-middle. _No usar en producción._

- **tls_curves** <span id="tls_curves"/> es una lista de curvas elípticas compatibles para la conexión upstream. Los valores predeterminados de Caddy son modernos y seguros, así que solo deberías configurarlo si tienes requisitos específicos.

- **tls_timeout** <span id="tls_timeout"/> es el máximo [duration](/docs/conventions#durations) para completar el handshake TLS. Sin timeout por defecto.

- **tls_trust_pool** <span id="tls_trust_pool"/> configura la fuente de autoridades certificadoras confiables similar al subcomando [`trust_pool`](/docs/caddyfile/directives/tls#trust_pool) descrito en la documentación de la directiva `tls`. La lista de fuentes de trust pool disponibles en una instalación estándar de Caddy está [aquí](/docs/caddyfile/directives/tls#trust-pool-providers).

- **tls_server_name** <span id="tls_server_name"/> establece el nombre de servidor usado al verificar el certificado recibido en el handshake TLS. Por defecto usa la parte host de la dirección de upstream.

  Solo debes sobrescribir esto si la dirección del upstream no coincide con el certificado que probablemente use el upstream. Por ejemplo, si la dirección del upstream es una IP, deberás configurarlo al hostname servido por el servidor upstream.

  Puede usarse un placeholder de solicitud, en cuyo caso se clonará la configuración de transporte HTTP para cada solicitud, lo que puede generar impacto de rendimiento.

- **tls_renegotiation** <span id="tls_renegotiation"/> establece el nivel de renegociación TLS. La renegociación TLS es realizar handshakes posteriores al primero. El nivel puede ser:
  - `never` (predeterminado): deshabilita renegociación.
  - `once`: permite a un servidor remoto solicitar renegociación una vez por conexión.
  - `freely`: permite a un servidor remoto solicitar repetidamente renegociación.

- **tls_except_ports** <span id="tls_except_ports"/> cuando TLS está habilitado, si el destino upstream usa uno de los puertos indicados, TLS se deshabilita para esas conexiones. Esto puede ser útil al configurar upstreams dinámicos, donde unos esperan HTTP y otros HTTPS.

- **keepalive** <span id="keepalive"/> puede ser `off` o un [valor de duración](/docs/conventions#durations) que indica cuánto mantener conexiones abiertas (timeout). Predeterminado: `2m`.

  ⚠️ Las solicitudes a backends HTTP/1.1 pueden fallar con errores "connection reset by peer" si la duración de keepalive excede el timeout de keepalive del upstream. Go HTTP transport reintentará solicitudes idempotentes, pero en otros casos Caddy responderá con código 502.

- **keepalive_interval** <span id="keepalive_interval"/> es la [duration](/docs/conventions#durations) entre comprobaciones de conectividad. Predeterminado: `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> define el número máximo de conexiones para mantener activas. Predeterminado: sin límite.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> si no es cero, controla el máximo de conexiones inactivas (keep-alive) a mantener por host. Predeterminado: `32`.

- **versions** <span id="versions"/> permite personalizar qué versiones HTTP soportar.
  
  Opciones válidas: `1.1`, `2`, `h2c`, `3`.

  Predeterminado: `1.1 2`, o si el [esquema del upstream](#upstream-addresses) es `h2c://`, entonces por defecto es `h2c 2`.

  `h2c` habilita conexiones HTTP/2 en texto plano hacia el upstream. Esta es una función no estándar que no usa el transport HTTP por defecto de Go, por lo que es exclusiva de otras opciones.

  `3` habilita conexiones HTTP/3 al upstream. ⚠️ Esta función es experimental y puede cambiar.

- **compression** <span id="compression"/> se puede usar para desactivar la compresión al backend estableciéndolo en `off`.

- **max_conns_per_host** <span id="max_conns_per_host"/> limita opcionalmente el número total de conexiones por host, incluyendo conexiones en los estados dialing, active e idle. Predeterminado: sin límite.

- **network_proxy** <span id="network_proxy"/> especifica el nombre de un módulo de proxy de red para solicitudes al servidor upstream. Si no se configura explícitamente, Caddy respeta el proxy configurado por variables de entorno según la [stdlib de Go](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), es decir `HTTP_PROXY`, `HTTPS_PROXY` y `NO_PROXY`. Cuando se indica un valor para este parámetro, las solicitudes fluyen por el reverse proxy en el orden: cliente (usuarios) → `reverse_proxy` → `network_proxy` → upstream. Los módulos incorporados son:
	- `none`, que se usa para ignorar configuraciones de entorno `HTTP_PROXY`, `HTTPS_PROXY` y `NO_PROXY`.
	- `url <url>`, que especifica una sola URL para sobrescribir la configuración del entorno.

<a id="the-fastcgi-transport"></a>
### The `fastcgi` transport

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> es la raíz del sitio. Predeterminado: `{http.vars.root}` o directorio actual.

- **split** <span id="split"/> indica dónde separar la ruta para obtener PATH_INFO al final de la URI.

- **env** <span id="env"/> configura una variable de entorno adicional con el valor indicado. Puede especificarse más de una vez para múltiples variables.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> permite resolver el directorio `root` a su valor real evaluando un enlace simbólico, si existe.

- **dial_timeout** <span id="dial_timeout"/> indica cuánto esperar al conectar con el socket de upstream. Acepta [valores de duración](/docs/conventions#durations). Predeterminado: `3s`.

- **read_timeout** <span id="read_timeout"/> es cuánto esperar al leer desde el servidor FastCGI. Acepta [valores de duración](/docs/conventions#durations). Predeterminado: sin timeout.

- **write_timeout** <span id="write_timeout"/> es cuánto esperar al enviar al servidor FastCGI. Acepta [valores de duración](/docs/conventions#durations). Predeterminado: sin timeout.

- **capture_stderr** <span id="capture_stderr"/> habilita la captura y logging de mensajes enviados por el servidor fastcgi upstream en `stderr`. El log se hace en nivel `WARN` por defecto. Si la respuesta tiene estado `4xx` o `5xx`, se utilizará nivel `ERROR`. Por defecto `stderr` se ignora.

<aside class="tip">

Si estás intentando servir una aplicación PHP moderna, puede interesarte la directiva [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi), que es un atajo para un proxy que usa la directiva `fastcgi`, con las reescrituras necesarias para usar `index.php` como punto de entrada del enrutamiento.

</aside>



<a id="intercepting-responses"></a>
## Intercepting responses

El reverse proxy se puede configurar para interceptar respuestas del backend. Para facilitarlo, se pueden definir [response matchers](/docs/caddyfile/response-matchers) (similar a la sintaxis de request matchers) y se invocará la primera ruta `handle_response` que coincida.

Cuando se invoca un response handler, la respuesta del backend no se escribe al cliente y en su lugar se ejecuta la ruta `handle_response` configurada, y depende de esa ruta escribir la respuesta. Si la ruta _no_ escribe respuesta, el manejo continúa con cualquier handler que esté [ordenado después](/docs/caddyfile/directives#directive-order) de este `reverse_proxy`.

- **@name** es el nombre de un [response matcher](/docs/caddyfile/response-matchers). Mientras cada response matcher tenga un nombre único, se pueden definir varios. Se puede coincidir una respuesta por código de estado y por presencia o valor de un encabezado de respuesta.

- **replace_status** <span id="replace_status"/> cambia simplemente el código de estado de la respuesta cuando coincide el matcher indicado.

- **handle_response** <span id="handle_response"/> define la ruta a ejecutar cuando coincide el matcher indicado (o, si no se indica matcher, todas las respuestas). Se aplica el primer bloque coincidente. Dentro de un bloque `handle_response`, se pueden usar otros [directives](/docs/caddyfile/directives).

Además, dentro de `handle_response` pueden usarse dos directivas handler especiales:

- **copy_response** <span id="copy_response"/> copia el cuerpo de respuesta recibido del backend de nuevo al cliente. Opcionalmente permite cambiar el código de estado mientras lo hace. Esta directiva se ordena [antes de `respond`](/docs/caddyfile/directives#directive-order).

- **copy_response_headers** <span id="copy_response_headers"/> copia los encabezados de respuesta del backend al cliente, incluyendo o excluyendo (`_OR_`) opcionalmente una lista de campos de encabezado (no se puede especificar tanto `include` como `exclude`). Esta directiva se ordena [después de `header`](/docs/caddyfile/directives#directive-order).

En las rutas de `handle_response` se ponen disponibles tres placeholders:

- `{rp.status_code}` El código de estado de la respuesta del backend.

- `{rp.status_text}` El texto de estado de la respuesta del backend.

- `{rp.header.*}` Los encabezados de la respuesta del backend.

Aunque el handler de respuesta de reverse_proxy puede copiar la nueva respuesta del proxy al cliente, no puede pasar esa nueva respuesta a un `reverse_proxy` posterior. Cada uso de `reverse_proxy` recibe el cuerpo de la solicitud original (o modificado por un módulo diferente).




<a id="examples"></a>
## Examples

Reenvía al proxy todas las solicitudes a un backend local:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


Balancear [Load-balance](#load-balancing) todas las solicitudes [entre 3 backends](#upstreams):

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


Lo mismo, pero solo solicitudes dentro de `/api`, y con persistencia mediante la [`cookie` policy](#lb_policy):

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


Usando [comprobaciones activas](#active-health-checks) para determinar qué backends están saludables y habilitando [retries](#lb_try_duration) en conexiones fallidas, manteniendo la solicitud hasta encontrar un backend saludable:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Configura algunas [opciones de transporte](#transports):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Proxy a un upstream [HTTPS](#https) (desde v2.11.0, Caddy establece automáticamente el encabezado `Host` para que coincida con el host del upstream, por lo que ya no es necesario hacerlo manualmente):

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Proxy a un upstream HTTPS, pero [⚠️ desactiva la verificación TLS](#tls_insecure_skip_verify). Esto NO ES RECOMENDADO, porque desactiva todas las comprobaciones de seguridad que aporta HTTPS; si es posible, usa proxy sobre HTTP en redes privadas, porque evita la falsa sensación de seguridad:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


En su lugar, puedes establecer confianza con el upstream [confiando explícitamente el certificado del upstream](#tls_trust_pool), y (opcionalmente) definiendo TLS-SNI para que coincida con el nombre de host del certificado del upstream:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```


[Quitar un prefijo de ruta](handle_path) antes de hacer proxy; pero ten en cuenta el [problema de subfolder <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575):

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


Reemplaza un prefijo de ruta antes de hacer proxy usando [`rewrite`](/docs/caddyfile/directives/rewrite):

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


Compatibilidad con `X-Accel-Redirect`, es decir, servir archivos estáticos solicitados, [interceptando la respuesta](#intercepting-responses):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Página de error personalizada para errores del upstream, [interceptando respuestas de error](#intercepting-responses) por código de estado:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Obtener backends [dinámicamente](#dynamic-upstreams) desde consultas DNS [`A`/`AAAA`](#aaaaa):

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Obtener backends [dinámicamente](#dynamic-upstreams) desde consultas de registro [`SRV`](#srv):

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


Usar [comprobaciones activas](#active-health-checks) y `health_upstream` puede ser útil al crear un servicio intermedio para realizar una comprobación de estado más profunda. Luego `{http.reverse_proxy.active.target_upstream}` puede usarse como encabezado para proporcionar el upstream original al servicio de health check.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
