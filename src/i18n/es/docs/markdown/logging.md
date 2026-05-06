---
title: Funcionamiento del logging
---

Funcionamiento del logging
=========================

El logging en Caddy es potente y flexible, pero puede ser distinto de lo que estás acostumbrado, especialmente si vienes de hosting compartido antiguo u otros servidores legacy.


## Descripción general

Hay dos aspectos principales del logging: emisión y consumo.

**La emisión** es producir mensajes y consiste en tres pasos:

1. Recopilar la información relevante (contexto)
2. Construir una representación útil (encoding)
3. Enviar esa representación a un destino (writing)

Esta funcionalidad está integrada en el core de Caddy y permite que cualquier parte del código de Caddy o de módulos (plugins) emita logs.

**El consumo** es la recepción y procesamiento de mensajes. Para que el logging sea útil, los logs emitidos deben consumirse. Un log solo escrito y nunca leído no aporta valor. Consumir logs puede ser tan simple como una salida en consola para un administrador, o tan avanzado como usar una herramienta de agregación o un servicio cloud para filtrar, contar y indexar eventos.

### Rol de Caddy

_Caddy es un emisor de logs_. No consume logs salvo el procesamiento mínimo requerido para codificar y escribir. Eso mantiene el core más simple, con menos bugs y casos límite, y reduce carga de mantenimiento. En última instancia, el procesamiento avanzado queda fuera del core.

Es posible que exista un módulo de app en Caddy que consuma logs, aunque hoy no haya uno conocido.


## Logs estructurados

Como muchas apps modernas, los logs de Caddy son _estructurados_. Esto significa que la información de un mensaje no es una cadena opaca o bytes, sino datos tipados y con nombre de campo hasta que se codifica y se escribe.

Compáralo con logs no estructurados como Common Log Format (CLF):

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Ese formato “tiene estructura” pero no es “structured”: solo sirve para registrar peticiones HTTP. No hay forma eficiente de recodificarlo con otro formato porque es una cadena opaca. Además, carece de mucha información; por ejemplo, no incluye el header `Host` de la petición. Solo es útil para un sitio único y para métricas básicas.

<aside class="tip">
	La falta de `Host` en CLF explica por qué esos logs suelen escribirse en archivos separados cuando hay más de un sitio: no hay forma de saber el `Host` desde la petición.
</aside>

Ahora, un log estructurado equivalente en Caddy, codificado como JSON y formateado para fácil lectura:

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"]
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Puedes ver que el log estructurado es más útil y contiene más información. Además, esa info no implica overhead adicional: los logs de Caddy son de baja asignación. Los logs estructurados no limitan tipos de datos ni contexto: pueden usarse en cualquier ruta de código y contener cualquier información.

Como los logs están tipados, se pueden codificar en cualquier formato. Si no quieres JSON, puedes usar cualquier otra representación mediante los [módulos de encoder](/docs/json/logging/logs/encoder/), y se pueden añadir más.

**Importante**: frente a los formatos legacy, un log estructurado puede transformarse a CLF [con `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), pero no al revés. Convertir CLF a un formato estructurado es difícil o ineficiente por falta de información.

En la práctica, un logging eficiente favorece estas ideas:

- Mejor tener demasiados logs que muy pocos
- Filtrar mejor que descartar
- Posponer la codificación para mayor flexibilidad e interoperabilidad


## Emisión

En código, la emisión se parece a esto:

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Esta línea es real en el reverse proxy de Caddy. Permite inspeccionar peticiones al upstream configurado con logging debug. Es clave para resolver problemas.
</aside>

En esa llamada hay nivel de log, mensaje y campos de datos, todos tipados. Caddy usa un logger de cero asignaciones para que la emisión sea rápida y con muy poco overhead.

La variable `logger` es un `zap.Logger` con contexto asociado: nombre y campos de datos. Eso permite heredar contexto y hacer tracing/metricas avanzadas.

Después, el mensaje pasa por una pipeline de procesamiento eficiente donde se codifica y se escribe.


## Pipeline de logging

Como viste, los mensajes los emiten **loggers**. Luego esos mensajes entran en **logs** para procesarlos.

Caddy permite [configurar múltiples logs](/docs/json/logging/logs/) con encoder, writer, nivel mínimo, sampling y lista de loggers a incluir o excluir. En Caddy siempre hay un log por defecto llamado `default`. Puedes personalizarlo indicando un log con clave `"default"` en [este objeto](/docs/json/logging/logs/).

<aside class="tip">
	Es buen momento para explorar [la documentación de logging de Caddy](/docs/json/logging/) y familiarizarse con esa estructura.
</aside>


- **Encoder:** formato del log; transforma la estructura interna en bytes.
- **Writer:** destino de salida, puede ser archivo o socket de red.
- **Level:** nivel de mensajes, de DEBUG a FATAL. Los mensajes por debajo se ignoran.
- **Sampling:** en rutas muy calientes puede emitirse demasiados logs; activar sampling reduce carga y mantiene una muestra representativa.
- **Include/exclude:** cada mensaje parte de un logger con un nombre. Los logs pueden incluir o excluir mensajes de ciertos loggers.

Cuando un log se emite:

- El nombre del logger origen se compara con las listas include/exclude de cada log; si está incluido (y no excluido), entra.
- Si hay sampling, una comprobación rápida decide si se mantiene o no.
- El mensaje se codifica usando el encoder configurado.
- Los bytes se escriben en el writer del log.

Por defecto, los mensajes van a todos los logs configurados. Esto sigue la filosofía de logging estructurado. Puedes limitar qué mensajes van a cada log con include/exclude, pero eso se usa más para separar mensajes de módulos que como reemplazo de una plataforma de agregación. Para mantener eficiente el pipeline, cualquier procesamiento avanzado queda fuera y se delega al consumo.

## Consumo

Después de emitidos y escritos, un consumidor lee, parsea y gestiona los mensajes.

Esto es distinto a la emisión, y el core de Caddy no lo maneja (aunque un módulo podría hacerlo). Hay muchas herramientas para procesar streams JSON (u otros formatos), mostrar, filtrar, indexar y consultar logs. Incluso puedes implementar tu propio consumidor.

Si ejecutas software legacy que requiere CLF separado por campos (por ejemplo por hostname), puedes usar una herramienta propia para convertir JSON a CLF con `sprintf()` y escribir por campo `request.host`.

Las capacidades de logs de Caddy también pueden usarse para métricas y tracing: métricas cuentan mensajes con ciertas características, y tracing une mensajes relacionados.

Las posibilidades son muy amplias para explotar logs de Caddy.
