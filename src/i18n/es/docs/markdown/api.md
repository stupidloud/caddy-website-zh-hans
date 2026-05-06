---
title: "API"
---

# API

Caddy se configura mediante un endpoint de administración al que se puede acceder mediante HTTP a través de una [API REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer). Puedes [configurar este endpoint](/docs/json/admin/) en la configuración de Caddy.

**Dirección por defecto: `localhost:2019`**

La dirección por defecto se puede cambiar mediante la variable de entorno `CADDY_ADMIN`. Algunos métodos de instalación pueden usar un valor distinto. La dirección de la configuración de Caddy siempre tiene prioridad sobre el valor por defecto.

<aside class="tip">
	Si ejecutas código que no confías completamente en tu servidor (yikes 😬), protege el endpoint de administración aislando procesos, parcheando programas con vulnerabilidades y configurando el endpoint para enlazarlo a un socket unix con permisos.
</aside>

La configuración más reciente se guarda en disco después de cualquier cambio (a menos que esté [desactivado](/docs/json/admin/config/)). Puedes reanudar la última configuración funcional después de reiniciar con [`caddy run --resume`](/docs/command-line#caddy-run), lo que garantiza la durabilidad de la configuración ante un corte de energía o un evento similar.

Para comenzar con la API, revisa el [tutorial de API](/docs/api-tutorial) o, si solo dispones de un minuto, nuestra [guía de inicio rápido de API](/docs/quick-starts/api).

---

- **[POST /load](#post-load)**
  Establece o reemplaza la configuración activa

- **[POST /stop](#post-stop)**
  Detiene la configuración activa y sale del proceso

- **[GET /config/[path]](#get-configpath)**
  Exporta la configuración de la ruta indicada

- **[POST /config/[path]](#post-configpath)**
  Establece o reemplaza un objeto; lo añade al array
  
- **[PUT /config/[path]](#put-configpath)**
  Crea un objeto nuevo; inserta en el array

- **[PATCH /config/[path]](#patch-configpath)**
  Reemplaza un objeto existente o un elemento de un array

- **[DELETE /config/[path]](#delete-configpath)**
  Elimina el valor de la ruta indicada

- **[Usar `@id` en JSON](#using-id-in-json)**
  Navega fácilmente dentro de la estructura de configuración

- **[Cambios concurrentes de configuración](#concurrent-config-changes)**
  Evita colisiones al hacer cambios de configuración sin sincronizar

- **[POST /adapt](#post-adapt)**
  Adapta una configuración a JSON sin ejecutarla

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Devuelve información sobre una CA concreta de [aplicación PKI](/docs/json/apps/pki/)

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Devuelve la cadena de certificados de una CA concreta de [aplicación PKI](/docs/json/apps/pki/)

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Devuelve el estado actual de los upstreams de proxy configurados


## POST /load

Establece la configuración de Caddy, sobrescribiendo cualquier configuración anterior. Bloquea hasta que la recarga se complete o falle. Los cambios de configuración son ligeros, eficientes y no producen tiempo de inactividad. Si la nueva configuración falla por cualquier motivo, la configuración anterior se restaura sin interrupción.

Este endpoint admite diferentes formatos de configuración mediante adaptadores. La cabecera `Content-Type` de la petición indica el formato de configuración usado en el cuerpo de la solicitud. Por lo general debe ser `application/json`, que corresponde al formato nativo de configuración de Caddy. Para otro formato, indica el `Content-Type` apropiado de modo que el valor tras la barra diagonal `/` sea el nombre del adaptador de configuración a usar. Por ejemplo, al enviar un Caddyfile usa un valor como `text/caddyfile`, o para JSON 5 usa `application/json5`.

Si la configuración nueva es igual a la actual, no se realizará ninguna recarga. Para forzar una recarga, establece `Cache-Control: must-revalidate` en las cabeceras de la petición.

### Ejemplos

Define una nueva configuración activa:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Nota: la opción `-d` de curl elimina los saltos de línea, así que si tu formato de configuración es sensible a los saltos de línea (por ejemplo, el Caddyfile), usa `--data-binary` en su lugar:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## POST /stop

Detiene el servidor de forma ordenada y sale del proceso. Para detener solo la configuración en ejecución sin salir del proceso, usa [DELETE /config/](#delete-configpath).

### Ejemplo

Detiene el proceso:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


## GET /config/[path]

Exporta la configuración actual de Caddy en la ruta indicada. Devuelve un cuerpo JSON.

### Ejemplos

Exporta la configuración completa y la imprime con formato:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					}
				]
			}
		}
	}
}</code></pre>

Exporta solo las direcciones de escucha:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[
	":443"
]</code></pre>



## POST /config/[path]

Cambia la configuración de Caddy en la ruta indicada por el cuerpo JSON de la petición. Si el valor de destino es un array, POST lo añade; si es un objeto, crea o reemplaza.

Como caso especial, se pueden añadir muchos elementos a un array si:

1. la ruta termina en `/...`
2. el elemento de la ruta antes de `/...` hace referencia a un array
3. la carga útil es un array

En ese caso, los elementos del array de la carga útil se expandirán y cada uno se añadirá al array de destino. En términos de Go, sería equivalente a:

```go
baseSlice = append(baseSlice, newElems...)
```

### Ejemplos

Añade una dirección de escucha:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Añade varias direcciones de escucha:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

## PUT /config/[path]

Cambia la configuración de Caddy en la ruta indicada por el cuerpo JSON de la petición. Si el valor de destino es una posición (índice) en un array, PUT inserta; si es un objeto, crea estrictamente un valor nuevo.

### Ejemplo

Añade una dirección de escucha en la primera posición:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


## PATCH /config/[path]

Cambia la configuración de Caddy en la ruta indicada por el cuerpo JSON de la petición. PATCH reemplaza estrictamente un valor existente o un elemento de array.

### Ejemplo

Reemplaza las direcciones de escucha:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



## DELETE /config/[path]

Elimina la configuración de Caddy en la ruta indicada. DELETE elimina el valor destino.

### Ejemplos

Para descargar la configuración actual pero dejar el proceso en ejecución:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Para detener solo uno de los servidores HTTP:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## Usar `@id` en JSON

Puedes incrustar IDs en tu documento JSON para acceder de manera más fácil a esas partes del JSON.

Añade un campo llamado `"@id"` en un objeto y asígnale un nombre único. Por ejemplo, si tuvieras un manejador reverse_proxy al que quieras acceder con frecuencia:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Para usarlo, realiza una petición al endpoint de API `/id/` de la misma forma que harías al endpoint `/config/` correspondiente, pero sin la ruta completa. El ID dirige la petición directamente a ese ámbito de la configuración.

Por ejemplo, para acceder a los upstreams del reverse proxy sin un ID, la ruta sería parecida a:

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

pero con un ID, la ruta se convierte en:

```
/id/my_proxy/upstreams
```

lo cual es mucho más fácil de recordar y escribir a mano.

## Concurrent config changes

<aside class="tip">

Esta sección aplica a todos los endpoints `/config/`. Es experimental y puede cambiar.

</aside>


La API de configuración de Caddy proporciona [garantías ACID <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) para peticiones individuales, pero los cambios que involucran más de una petición pueden tener colisiones o pérdida de datos si no se sincronizan correctamente.

Por ejemplo, dos clientes pueden hacer `GET /config/foo` al mismo tiempo, editar dentro de ese ámbito (ruta de configuración) y luego llamar a `POST|PUT|PATCH|DELETE /config/foo/...` simultáneamente para aplicar sus cambios, lo que resulta en una colisión: uno sobrescribe al otro, o el segundo podría dejar la configuración en un estado no deseado porque se aplicó sobre una versión distinta de la configuración sobre la que se basó. Esto ocurre porque los cambios no son conscientes entre sí.

La API de Caddy no admite transacciones que cubran múltiples peticiones, y HTTP es un protocolo sin estado. Sin embargo, puedes usar las cabeceras `Etag` y `If-Match` para detectar y prevenir colisiones en cualquier cambio usando un tipo de control de concurrencia optimista. Esto es útil si existe la posibilidad de usar los endpoints `/config/...` de Caddy en paralelo sin sincronización. Todas las respuestas a las peticiones `GET /config/...` incluyen una cabecera HTTP llamada `Etag` que contiene la ruta y un hash del contenido de ese ámbito (por ejemplo, `Etag: "/config/apps/http/servers 65760b8e"`). Solo tienes que establecer la cabecera `If-Match` en una petición mutativa con el valor de una cabecera `Etag` de una petición `GET` anterior.

El algoritmo básico es:

1. Realiza una petición `GET` a cualquier ámbito `S` dentro de la configuración. Conserva la cabecera `Etag` de la respuesta.
2. Realiza el cambio deseado en la configuración devuelta.
3. Ejecuta una petición `POST|PUT|PATCH|DELETE` dentro del ámbito `S`, estableciendo la cabecera `If-Match` de la petición al valor `Etag` almacenado.
4. Si la respuesta es HTTP 412 (Precondition Failed), repite desde el paso 1, o abandona tras demasiados intentos.

Este algoritmo permite cambios múltiples y superpuestos en la configuración de Caddy sin sincronización explícita de forma segura. Está diseñado para que los cambios simultáneos en distintas partes de la configuración no requieran reintento: solo los cambios que se solapan en el mismo ámbito de configuración pueden causar una colisión y por tanto requerir reintento.


## POST /adapt

Adapta una configuración a JSON de Caddy sin cargarla ni ejecutarla. Si tiene éxito, el documento JSON resultante se devuelve en el cuerpo de la respuesta.

La cabecera `Content-Type` se usa para indicar el formato de configuración de la misma manera que funciona [/load](#post-load). Por ejemplo, para adaptar un Caddyfile, establece `Content-Type: text/caddyfile`.

Este endpoint adaptará cualquier formato de configuración siempre que el [adaptador de configuración](/docs/config-adapters) correspondiente esté incorporado en tu build de Caddy.

### Ejemplos

Adapta un Caddyfile a JSON:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## GET /pki/ca/&lt;id&gt;

Devuelve información sobre una CA concreta de [aplicación PKI](/docs/json/apps/pki/) por su ID. Si el ID de CA solicitado es el predeterminado (`local`), la CA se aprovisionará si aún no se ha hecho. Otras IDs de CA devolverán un error si no se habían aprovisionado previamente.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


## GET /pki/ca/&lt;id&gt;/certificates

Devuelve la cadena de certificados de una CA concreta de [aplicación PKI](/docs/json/apps/pki/) por su ID. Si el ID de CA solicitado es el predeterminado (`local`), la CA se aprovisionará si aún no se ha hecho. Otras IDs de CA devolverán un error si no se habían aprovisionado antes.

Este endpoint lo usa internamente el comando [`caddy trust`](/docs/command-line#caddy-trust) para instalar el certificado raíz de la CA en el almacén de confianza de tu sistema.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

Devuelve el estado actual de los upstreams del reverse proxy configurado (backends) como un documento JSON.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Cada entrada del array JSON es un [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/) configurado almacenado en el pool global de upstreams.

- **address** es la dirección de conexión del upstream.
- **num_requests** es la cantidad de solicitudes activas que el upstream está gestionando actualmente.
- **fails** es el número actual de solicitudes fallidas recordadas, según lo configurado por las revisiones de salud pasivas.

Si tu objetivo es determinar la disponibilidad de un backend, debes comparar propiedades relevantes del upstream con la configuración del handler que estás usando. Por ejemplo, si has habilitado [health checks pasivos](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) para tus proxies, entonces también debes tener en cuenta los valores `fails` y `num_requests` para determinar si un upstream se considera disponible: comprueba que el valor de `fails` sea menor que el máximo de fallos configurado para tu proxy (es decir, [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)), y que `num_requests` sea menor o igual que el máximo configurado de solicitudes por upstream (es decir, [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) para el proxy completo, o [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) para upstreams individuales).
