---
title: Monitorizar Caddy con métricas
---

# Monitorizar Caddy con métricas

No importa si ejecutas miles de instancias de Caddy en la nube o un único servidor Caddy en un dispositivo embebido, en algún momento querrás una vista de alto nivel de qué está haciendo Caddy y cuánto tarda. En resumen, necesitas poder **monitorizar** Caddy.

## Habilitar métricas

Debes activar métricas.

Si usas Caddyfile, habilita métricas en [global options](/docs/caddyfile/options#metrics):

```caddy
{
	metrics
}
```

Si usas JSON, añade `"metrics": {}` en tu configuración de [`apps > http > servers`.](/docs/json/apps/http/servers/)

Para agregar métricas por host, inserta `per_host`. Las métricas específicas por host tendrán ahora una etiqueta `Host`.

```caddy
{
	metrics {
		per_host
	}
}
```

Esta configuración observa hosts configurados. Si un servidor HTTPS está configurado, el host se observa aunque no esté explícitamente configurado, por ejemplo en TLS on-demand. Si HTTPS está deshabilitado, solo se habilitan los hosts configurados por riesgo de cardinalidad infinita. Para observar todos los hosts en configuración HTTP, incluso sin configurar, usa `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io) es una plataforma de monitorización que recoge métricas de objetivos monitorizados “scrapeando” sus endpoints HTTP. Además de mostrarlas con herramientas como [Grafana](https://grafana.com/docs/grafana/latest/introduction/), Prometheus también se usa para [alerting](https://prometheus.io/docs/alerting/latest/overview/).

Como Caddy, Prometheus está escrito en Go y se distribuye como un único binario. Para instalarlo, consulta la [documentación de instalación](https://prometheus.io/docs/prometheus/latest/installation/), o en macOS ejecuta `brew install prometheus`.

Si eres nuevo en Prometheus, lee primero su documentación introductoria y luego continúa.

Para configurar Prometheus y recopilar métricas de Caddy necesitas un YAML similar:

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # el default es 1 minuto

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

Entonces inicia Prometheus así:

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy también puede enviar métricas a un endpoint OpenTelemetry Protocol (OTLP). Esto es útil para stacks de observabilidad nativos de OTLP, como OpenTelemetry Collector, Grafana Alloy, Honeycomb u otros sistemas que reciban métricas OTLP directamente.

Activa la exportación OTLP con la opción `otlp`:

```caddy
{
	metrics {
		otlp
	}
}
```

El exporter OTLP se configura con las variables estándar de [OpenTelemetry](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/), alineadas con la configuración de [`tracing`](/docs/caddyfile/directives/tracing). Ejemplo:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Por defecto usa OTLP sobre HTTP/protobuf. Pon `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` para usar gRPC. Encabezados, endpoints, protocolos, exporter y periodos de recolección se controlan con variables como `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` y `OTEL_METRIC_EXPORT_INTERVAL`.

Para desactivar la exportación sin cambiar Caddyfile usa `OTEL_METRICS_EXPORTER=none`.

Con OTLP habilitado, Caddy exporta las mismas métricas recolectadas para el endpoint Prometheus. Los recursos incluyen atributos `web_engine.name` y `web_engine.version`.

## Métricas de Caddy

Como cualquier proceso monitorizado con Prometheus, Caddy expone un endpoint HTTP que responde con el [formato Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format). El cliente Prometheus de Caddy también puede responder con [OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) cuando se negocia (`application/openmetrics-text; version=0.0.1`).

Por defecto, hay un endpoint `/metrics` en la [admin API](/docs/api), normalmente en `http://localhost:2019/metrics`. Si la admin API está desactivada o quieres otro puerto/ruta, usa el handler [`metrics`](/docs/caddyfile/directives/metrics).

Puedes ver las métricas con cualquier navegador o cliente HTTP como `curl`:

```console
$ curl http://localhost:2019/metrics
# HELP caddy_admin_http_requests_total Counter of requests made to the Admin API's HTTP endpoints.
# TYPE caddy_admin_http_requests_total counter
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 2
# HELP caddy_http_request_duration_seconds Histogram of round-trip request durations.
# TYPE caddy_http_request_duration_seconds histogram
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.005"} 1
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.01"} 1
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.025"} 1
...
```

Las métricas vistas suelen entrar en 4 grupos:

- Runtime metrics
- Admin API metrics
- HTTP Middleware metrics
- Reverse proxy metrics

### Runtime metrics

Estas métricas cubren el interior de Caddy y las proporciona automáticamente el cliente Prometheus de Go. Usan prefijos `go_*` y `process_*`.

`process_*` solo se recopila en Linux y Windows.

Revisa la documentación del [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector), [Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector) y [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

### Admin API metrics

Estas métricas monitorizan la API de administración. Cada endpoint de admin está instrumentado para contar peticiones y errores.

Llevan prefijo `caddy_admin_*`.

Ejemplo:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

Contador de peticiones procesadas por endpoints de admin, incluyendo módulos en namespace `admin.api.*`.

Label  | Description
-------|------------
`code` | Código de estado HTTP
`handler` | Nombre del handler o módulo
`method` | Método HTTP
`path` | Ruta de URL donde está montado el endpoint

#### `caddy_admin_http_request_errors_total`

Contador de errores encontrados en endpoints de admin, incluyendo módulos en `admin.api.*`.

Label  | Description
-------|------------
`handler` | Nombre del handler o módulo
`method` | Método HTTP
`path` | Ruta de URL donde está montado el endpoint

### HTTP Middleware metrics

Todos los handlers middleware HTTP están instrumentados para medir latencia de petición, tiempo al primer byte, errores y tamaños de request/response.

<aside class="tip">
	Dado que todos los middleware están instrumentados y muchas peticiones pasan por múltiples handlers, no sumes simplemente todos los contadores.
</aside>

Para los histogramas siguientes, los buckets no son configurables. Para duraciones se usa `prometheus.DefBuckets` (5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s y 10s). Para tamaños: 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB y 4MiB.

#### `caddy_http_requests_in_flight`

Gauge del número de peticiones que el servidor está manejando actualmente.

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo

#### `caddy_http_request_errors_total`

Contador de errores de middleware al procesar peticiones.

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo

#### `caddy_http_requests_total`

Contador de peticiones HTTP(S).

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo

#### `caddy_http_request_duration_seconds`

Histograma de duración de peticiones.

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo
`code` | Código de estado HTTP
`method` | Método HTTP

#### `caddy_http_request_size_bytes`

Histograma del tamaño total estimado de la petición, incluyendo body.

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo
`code` | Código de estado HTTP
`method` | Método HTTP

#### `caddy_http_response_size_bytes`

Histograma del tamaño del cuerpo de respuesta devuelto.

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo
`code` | Código de estado HTTP
`method` | Método HTTP

#### `caddy_http_response_duration_seconds`

Histograma de tiempo al primer byte (TTFB) de respuestas.

Label  | Description
-------|------------
`server` | Nombre del servidor
`handler` | Nombre del handler o módulo
`code` | Código de estado HTTP
`method` | Método HTTP

### Reverse proxy metrics

#### `caddy_reverse_proxy_upstreams_healthy`

Gauge de salud de upsteam en reverse proxy.

Valor `0` indica upstream no saludable; `1` indica saludable.

Label  | Description
-------|------------
`upstream` | Dirección del upstream

## Consultas de ejemplo

Cuando Prometheus ya scrapea métricas de Caddy, puedes empezar a ver métricas útiles del rendimiento.

<aside class="tip">
	Si tienes Prometheus ejecutándose con la configuración de arriba, prueba estas consultas en la UI en [http://localhost:9090/graph](http://localhost:9090/graph)
</aside>


Para ver tasa de peticiones por segundo (media 5m):

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Para ver la tasa de peticiones cuya latencia supera 100ms:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Percentil 95 de duración en `file_server`:

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

Mediana de tamaño de respuesta en bytes para peticiones `GET` con éxito en `file_server`:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
