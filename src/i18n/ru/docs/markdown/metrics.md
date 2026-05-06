---
title: Monitoring Caddy с metrics
---

<a id="monitoring-caddy-with-metrics"></a>
# Monitoring Caddy с metrics

Запускаете ли вы тысячи экземпляров Caddy в cloud или один
Caddy server на embedded device, скорее всего в какой-то момент вам понадобится
high-level overview того, что делает Caddy и сколько времени это занимает.
Иными словами, вы захотите иметь возможность *monitor* Caddy.

<a id="enabling-metrics"></a>
## Включение metrics

Нужно включить metrics.

Если используется Caddyfile, включите metrics [в global options](/docs/caddyfile/options#metrics):

```caddy
{
	metrics
}
```

Если используется JSON, добавьте `"metrics": {}` в [`apps > http > servers` configuration](/docs/json/apps/http/servers/).

Чтобы добавить per-host metrics, можно вставить опцию `per_host`. Host-specific metrics теперь будут иметь tag Host.

```caddy
{
	metrics {
		per_host
	}
}
```

Эта конфигурация будет observe настроенные hosts. Если настроен HTTPS server, host будет observed, даже если он явно не настроен, например при on-demand TLS setup. Если HTTPS отключен, включаются только настроенные hosts из-за риска потенциально infinite cardinality. Чтобы observe все hosts в HTTP setup, даже ненастроенные, используйте опцию `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io) — monitoring platform, которая собирает
metrics с monitored targets, scraping metrics HTTP endpoints на этих
targets. Помимо помощи в отображении metrics через dashboarding tool вроде [Grafana](https://grafana.com/docs/grafana/latest/introduction/), Prometheus также используется для [alerting](https://prometheus.io/docs/alerting/latest/overview/).

Как и Caddy, Prometheus написан на Go и распространяется как single binary. Чтобы
установить его, см. [Prometheus Installation docs](https://prometheus.io/docs/prometheus/latest/installation/),
или на MacOS просто выполните `brew install prometheus`.

Прочитайте [Prometheus docs](https://prometheus.io/docs/introduction/first_steps/),
если вы совсем не знакомы с Prometheus; иначе продолжайте!

Чтобы настроить Prometheus для scrape из Caddy, нужен YAML configuration
file, похожий на этот:

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # default is 1 minute

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

После этого Prometheus можно запустить так:

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy также может push metrics в OpenTelemetry Protocol (OTLP) endpoint.
Это полезно для OTLP-native observability stacks, таких как OpenTelemetry
Collector, Grafana Alloy, Honeycomb или другие systems, напрямую принимающие OTLP metrics.

Включите OTLP metrics export с опцией `otlp`:

```caddy
{
	metrics {
		otlp
	}
}
```

OTLP exporter настраивается стандартными
[OpenTelemetry environment variables](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/),
соответствуя style конфигурации [`tracing`](/docs/caddyfile/directives/tracing)
в Caddy. Например:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

По умолчанию exporter использует OTLP over HTTP/protobuf. Установите
`OTEL_EXPORTER_OTLP_PROTOCOL=grpc`, чтобы использовать gRPC. Headers, endpoints,
protocols, exporter selection и collection intervals управляются environment variables, такими как `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`,
`OTEL_EXPORTER_OTLP_HEADERS` и `OTEL_METRIC_EXPORT_INTERVAL`.

Установите `OTEL_METRICS_EXPORTER=none`, чтобы отключить metric export без изменения
Caddyfile.

Когда OTLP export включен, Caddy exports те же metrics, которые собираются для
Prometheus endpoint. Exported metrics включают resource attributes для
`web_engine.name` и `web_engine.version`.

<a id="caddys-metrics"></a>
## Metrics Caddy

Как любой process, monitored через Prometheus, Caddy exposes HTTP endpoint,
который отвечает в [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format).
Prometheus client Caddy также настроен отвечать в [OpenMetrics exposition format](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts),
если он negotiated (то есть если header `Accept` установлен в
`application/openmetrics-text; version=0.0.1`).

По умолчанию endpoint `/metrics` доступен на [admin API](/docs/api)
(т. е. http://localhost:2019/metrics). Но если admin API
отключен или нужно слушать другой port или path, можно использовать
[handler `metrics`](/docs/caddyfile/directives/metrics), чтобы это настроить.

Metrics можно увидеть в любом browser или HTTP client вроде `curl`:

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

Вы увидите ряд metrics, которые в целом попадают в 4 categories:

- Runtime metrics
- Admin API metrics
- HTTP Middleware metrics
- Reverse proxy metrics

<a id="runtime-metrics"></a>
### Runtime metrics

Эти metrics покрывают internals process Caddy и предоставляются
автоматически Prometheus Go Client. Они имеют prefix `go_*` и
`process_*`.

Обратите внимание, что metrics `process_*` собираются только на Linux и Windows.

См. документацию для [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector),
[Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector)
и [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

<a id="admin-api-metrics"></a>
### Admin API metrics

Это metrics, которые помогают monitor Caddy admin API. Каждый admin
endpoint instrumented для tracking request counts и errors.

Эти metrics имеют prefix `caddy_admin_*`.

Например:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

Counter числа requests, обработанных admin endpoints, включая
modules в namespace `admin.api.*`.

Label  | Описание
-------|------------
`code` | HTTP status code
`handler` | Handler или module name
`method` | HTTP method
`path` | URL path, на который был mounted admin endpoint

#### `caddy_admin_http_request_errors_total`

Counter числа errors, встреченных в admin endpoints, включая
modules в namespace `admin.api.*`.

Label  | Описание
-------|------------
`handler` | Handler или module name
`method` | HTTP method
`path` | URL path, на который был mounted admin endpoint

<a id="http-middleware-metrics"></a>
### HTTP Middleware metrics

Все Caddy HTTP middleware handlers автоматически instrumented для
determining request latency, time-to-first-byte, errors и request/response
body sizes.

<aside class="tip">
	Поскольку все middleware handlers instrumented, и многие requests обрабатываются несколькими handlers, не суммируйте все counters вместе напрямую.
</aside>

Для histogram metrics ниже buckets сейчас не настраиваются.
Для durations используется default set buckets ([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables)
(5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s и 10s).
Для sizes buckets: 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB и 4MiB.

#### `caddy_http_requests_in_flight`

Gauge числа requests, которые сейчас обрабатываются этим server.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name

#### `caddy_http_request_errors_total`

Counter middleware errors, встреченных при обработке requests.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name

#### `caddy_http_requests_total`

Counter выполненных HTTP(S) requests.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name

#### `caddy_http_request_duration_seconds`

Histogram round-trip request durations.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name
`code` | HTTP status code
`method` | HTTP method

#### `caddy_http_request_size_bytes`

Histogram общего (estimated) размера request. Включает body.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name
`code` | HTTP status code
`method` | HTTP method

#### `caddy_http_response_size_bytes`

Histogram размера возвращенного response body.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name
`code` | HTTP status code
`method` | HTTP method

#### `caddy_http_response_duration_seconds`

Histogram time-to-first-byte для responses.

Label  | Описание
-------|------------
`server` | Server name
`handler` | Handler или module name
`code` | HTTP status code
`method` | HTTP method

<a id="reverse-proxy-metrics"></a>
### Reverse proxy metrics

#### `caddy_reverse_proxy_upstreams_healthy`

Gauge healthiness reverse proxy upstreams.

Value `0` означает, что upstream unhealthy, тогда как `1` означает, что upstream healthy.

Label  | Описание
-------|------------
`upstream` | Address upstream

<a id="sample-queries"></a>
## Sample Queries

Когда Prometheus начнет scraping metrics Caddy, можно увидеть некоторые
интересные metrics о том, как работает Caddy.

<aside class="tip">

Если вы запустили Prometheus server для scrape Caddy с config выше, попробуйте вставить эти queries в Prometheus UI по адресу [http://localhost:9090/graph](http://localhost:9090/graph)

</aside>


Например, чтобы увидеть per-second request rate, averaged over 5 minutes:

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Чтобы увидеть rate, с которым превышается ваш latency threshold 100ms:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Чтобы найти 95th percentile request duration на handler `file_server`,
можно использовать такой query:

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

Или чтобы увидеть median response size в bytes для успешных `GET` requests на
handler `file_server`:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
