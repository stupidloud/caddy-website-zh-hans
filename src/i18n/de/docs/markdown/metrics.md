---
title: Caddy mit Metriken überwachen
---

<a id="monitoring-caddy-with-metrics"></a>
# Caddy mit Metriken überwachen

Egal ob du tausende Caddy-Instanzen in der Cloud betreibst oder einen einzelnen Caddy-Server auf einem Embedded-Gerät: Irgendwann möchtest du wahrscheinlich einen groben Überblick darüber haben, was Caddy tut und wie lange es dauert. Anders gesagt: Du möchtest Caddy *überwachen* können.

<a id="enabling-metrics"></a>
## Metriken aktivieren

Du musst Metriken einschalten.

Wenn du ein Caddyfile verwendest, aktiviere Metriken [in den globalen Optionen](/docs/caddyfile/options#metrics):

```caddy
{
	metrics
}
```

Wenn du JSON verwendest, füge deiner [`apps > http > servers`-Konfiguration](/docs/json/apps/http/servers/) `"metrics": {}` hinzu.

Um Metriken pro Host hinzuzufügen, kannst du die Option `per_host` einfügen. Host-spezifische Metriken haben dann ein Host-Tag.

```caddy
{
	metrics {
		per_host
	}
}
```

Diese Konfiguration beobachtet konfigurierte Hosts. Wenn ein HTTPS-Server konfiguriert ist, wird der Host beobachtet, auch wenn er nicht ausdrücklich konfiguriert wurde, z. B. bei On-Demand-TLS. Wenn HTTPS deaktiviert ist, werden wegen des Risikos potenziell unendlicher Kardinalität nur die konfigurierten Hosts aktiviert. Um in einem HTTP-Setup alle Hosts zu beobachten, auch nicht konfigurierte, verwende die Option `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

<a id="prometheus"></a>
## Prometheus

[Prometheus](https://prometheus.io) ist eine Monitoring-Plattform, die Metriken von überwachten Zielen sammelt, indem sie deren Metrik-HTTP-Endpunkte abruft. Neben der Darstellung von Metriken mit einem Dashboard-Tool wie [Grafana](https://grafana.com/docs/grafana/latest/introduction/) wird Prometheus auch für [alerting](https://prometheus.io/docs/alerting/latest/overview/) verwendet.

Wie Caddy ist Prometheus in Go geschrieben und wird als einzelne Binary ausgeliefert. Zur Installation siehe die [Prometheus-Installationsdokumentation](https://prometheus.io/docs/prometheus/latest/installation/) oder führe unter MacOS einfach `brew install prometheus` aus.

Wenn Prometheus für dich ganz neu ist, lies die [Prometheus-Dokumentation](https://prometheus.io/docs/introduction/first_steps/); andernfalls geht es hier weiter.

Um Prometheus so zu konfigurieren, dass es Caddy abruft, brauchst du eine YAML-Konfigurationsdatei ähnlich dieser:

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # Standard ist 1 Minute

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

Danach kannst du Prometheus so starten:

```console
$ prometheus --config.file=prometheus.yaml
```

<a id="opentelemetry"></a>
## OpenTelemetry

Caddy kann Metriken auch an einen OpenTelemetry Protocol (OTLP)-Endpunkt pushen. Das ist nützlich für OTLP-native Observability-Stacks, etwa OpenTelemetry Collector, Grafana Alloy, Honeycomb oder andere Systeme, die OTLP-Metriken direkt empfangen.

Aktiviere den Export von OTLP-Metriken mit der Option `otlp`:

```caddy
{
	metrics {
		otlp
	}
}
```

Der OTLP exporter wird mit den standardmäßigen [OpenTelemetry-Umgebungsvariablen](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/) konfiguriert und folgt damit dem Stil von Caddys [`tracing`](/docs/caddyfile/directives/tracing)-Konfiguration. Zum Beispiel:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Standardmäßig verwendet der exporter OTLP über HTTP/protobuf. Setze `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`, um stattdessen gRPC zu verwenden. Headers, endpoints, protocols, exporter selection und collection intervals werden über Umgebungsvariablen wie `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` und `OTEL_METRIC_EXPORT_INTERVAL` gesteuert.

Setze `OTEL_METRICS_EXPORTER=none`, um den Metrikexport zu deaktivieren, ohne das Caddyfile zu ändern.

Wenn OTLP-Export aktiviert ist, exportiert Caddy dieselben Metriken, die auch für den Prometheus-Endpunkt gesammelt werden. Exportierte Metriken enthalten resource attributes für `web_engine.name` und `web_engine.version`.

<a id="caddys-metrics"></a>
## Caddys Metriken

Wie jeder mit Prometheus überwachte Prozess stellt Caddy einen HTTP-Endpunkt bereit, der im [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) antwortet. Caddys Prometheus client ist außerdem so konfiguriert, dass er mit dem [OpenMetrics exposition format](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) antwortet, wenn es ausgehandelt wird, also wenn der `Accept`-Header auf `application/openmetrics-text; version=0.0.1` gesetzt ist.

Standardmäßig ist an der [admin API](/docs/api) ein `/metrics`-Endpunkt verfügbar (also http://localhost:2019/metrics). Wenn die admin API deaktiviert ist oder du auf einem anderen Port oder Pfad lauschen möchtest, kannst du dafür den [`metrics` handler](/docs/caddyfile/directives/metrics) konfigurieren.

Du kannst die Metriken mit jedem Browser oder HTTP-Client wie `curl` ansehen:

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

Es gibt eine Reihe von Metriken, die grob in 4 Kategorien fallen:

- Runtime-Metriken
- Admin-API-Metriken
- HTTP middleware metrics
- Reverse proxy metrics

<a id="runtime-metrics"></a>
### Runtime-Metriken

Diese Metriken decken Interna des Caddy-Prozesses ab und werden automatisch vom Prometheus Go Client bereitgestellt. Sie haben die Präfixe `go_*` und `process_*`.

Beachte, dass die `process_*`-Metriken nur unter Linux und Windows gesammelt werden.

Siehe die Dokumentation für den [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector), [Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector) und [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

<a id="admin-api-metrics"></a>
### Admin-API-Metriken

Diese Metriken helfen bei der Überwachung der Caddy admin API. Jeder admin endpoint ist instrumentiert, um Request-Zähler und Fehler zu erfassen.

Diese Metriken haben das Präfix `caddy_admin_*`.

Zum Beispiel:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

<a id="caddy-admin-http-requests-total"></a>
#### `caddy_admin_http_requests_total`

Ein counter für die Anzahl der Requests, die von admin endpoints verarbeitet wurden, einschließlich modules im namespace `admin.api.*`.

Label  | Beschreibung
-------|------------
`code` | HTTP-Statuscode
`handler` | Der handler- oder module-Name
`method` | Die HTTP-Methode
`path` | Der URL-Pfad, unter dem der admin endpoint gemountet wurde

<a id="caddy-admin-http-request-errors-total"></a>
#### `caddy_admin_http_request_errors_total`

Ein counter für die Anzahl der Fehler, die in admin endpoints aufgetreten sind, einschließlich modules im namespace `admin.api.*`.

Label  | Beschreibung
-------|------------
`handler` | Der handler- oder module-Name
`method` | Die HTTP-Methode
`path` | Der URL-Pfad, unter dem der admin endpoint gemountet wurde

<a id="http-middleware-metrics"></a>
### HTTP middleware metrics

Alle Caddy HTTP middleware handlers werden automatisch instrumentiert, um request latency, time-to-first-byte, errors sowie Größen von request/response bodies zu bestimmen.

<aside class="tip">
	Da alle middleware handlers instrumentiert sind und viele Requests von mehreren handlers verarbeitet werden, solltest du die counter nicht einfach alle aufsummieren.
</aside>

Für die Histogramm-Metriken unten sind die buckets derzeit nicht konfigurierbar. Für Dauern wird der Standardsatz von buckets ([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables)) verwendet (5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s und 10s). Für Größen sind die buckets 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB und 4MiB.

<a id="caddy-http-requests-in-flight"></a>
#### `caddy_http_requests_in_flight`

Ein gauge für die Anzahl der Requests, die dieser Server gerade verarbeitet.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name

<a id="caddy-http-request-errors-total"></a>
#### `caddy_http_request_errors_total`

Ein counter für middleware errors, die beim Verarbeiten von Requests aufgetreten sind.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name

<a id="caddy-http-requests-total"></a>
#### `caddy_http_requests_total`

Ein counter für gestellte HTTP(S)-Requests.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name

<a id="caddy-http-request-duration-seconds"></a>
#### `caddy_http_request_duration_seconds`

Ein Histogramm der Roundtrip-Dauern von Requests.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name
`code` | HTTP-Statuscode
`method` | Die HTTP-Methode

<a id="caddy-http-request-size-bytes"></a>
#### `caddy_http_request_size_bytes`

Ein Histogramm der gesamten (geschätzten) Größe des Requests. Enthält den Body.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name
`code` | HTTP-Statuscode
`method` | Die HTTP-Methode

<a id="caddy-http-response-size-bytes"></a>
#### `caddy_http_response_size_bytes`

Ein Histogramm der Größe des zurückgegebenen Response-Bodys.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name
`code` | HTTP-Statuscode
`method` | Die HTTP-Methode

<a id="caddy-http-response-duration-seconds"></a>
#### `caddy_http_response_duration_seconds`

Ein Histogramm der time-to-first-byte für Responses.

Label  | Beschreibung
-------|------------
`server` | Der Servername
`handler` | Der handler- oder module-Name
`code` | HTTP-Statuscode
`method` | Die HTTP-Methode

<a id="reverse-proxy-metrics"></a>
### Reverse proxy metrics

<a id="caddy-reverse-proxy-upstreams-healthy"></a>
#### `caddy_reverse_proxy_upstreams_healthy`

Ein gauge für den Gesundheitszustand der reverse proxy upstreams.

Der Wert `0` bedeutet, dass der upstream unhealthy ist; `1` bedeutet, dass der upstream healthy ist.

Label  | Beschreibung
-------|------------
`upstream` | Adresse des upstream

<a id="sample-queries"></a>
## Beispielabfragen

Sobald Prometheus Caddys Metriken abruft, kannst du interessante Metriken darüber sehen, wie Caddy arbeitet.

<aside class="tip">

Wenn du einen Prometheus-Server mit der obigen Konfiguration gestartet hast, um Caddy abzurufen, füge diese Abfragen in der Prometheus UI unter [http://localhost:9090/graph](http://localhost:9090/graph) ein.

</aside>


Um zum Beispiel die Requests pro Sekunde als Durchschnitt über 5 Minuten zu sehen:

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Um zu sehen, mit welcher Rate dein Latenzschwellwert von 100ms überschritten wird:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Um das 95. Perzentil der Request-Dauer beim handler `file_server` zu finden, kannst du eine Abfrage wie diese verwenden:

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

Oder um die mittlere Response-Größe in Bytes für erfolgreiche `GET`-Requests beim handler `file_server` zu sehen:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
