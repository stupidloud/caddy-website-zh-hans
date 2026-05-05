---
title: metrics (Caddyfile directive)
---

# metrics

Konfiguriert einen Prometheus-Metrics-Exposition-Endpunkt, damit die gesammelten Metrics zum Scraping bereitgestellt werden können. **Metrics müssen zuerst in Ihren [globalen Optionen aktiviert](/docs/caddyfile/options#metrics) werden.**

Beachten Sie, dass auch an die [admin API](/docs/api) ein `/metrics`-Endpunkt angehängt ist; dieser ist nicht konfigurierbar und nicht verfügbar, wenn die admin API deaktiviert ist.

Dieser Endpunkt gibt Metrics im [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) zurück oder, wenn ausgehandelt, im [OpenMetrics exposition format](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts) (`application/openmetrics-text`).

Siehe auch [Monitoring Caddy with metrics](/docs/metrics).

<a id="syntax"></a>
## Syntax

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** deaktiviert die OpenMetrics-Aushandlung. Normalerweise nur nötig, wenn Parsing-Bugs umgangen werden müssen.

<a id="examples"></a>
## Beispiele

Metrics am Standardpfad `/metrics` bereitstellen:

```caddy-d
metrics /metrics
```

Metrics an einem anderen Pfad bereitstellen:

```caddy-d
metrics /foo/bar/baz
```

Metrics auf einer separaten Subdomain ausliefern:

```caddy
metrics.example.com {
	metrics
}
```

OpenMetrics-Aushandlung deaktivieren:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
