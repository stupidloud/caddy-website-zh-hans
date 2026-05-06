---
title: metrics (директива Caddyfile)
---

# metrics

Настраивает Prometheus metrics exposition endpoint, чтобы собранные metrics можно
было предоставить для scraping. **Сначала metrics должны быть [включены в global options](/docs/caddyfile/options#metrics).**

Обратите внимание, что endpoint `/metrics` также прикреплен к [admin API](/docs/api),
он не настраивается и недоступен, когда admin API отключен.

Этот endpoint возвращает metrics в [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format)
или, если согласовано, в [OpenMetrics exposition format](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts)
(`application/openmetrics-text`).

См. также [Monitoring Caddy with metrics](/docs/metrics).

<a id="syntax"></a>
## Синтаксис

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** отключает OpenMetrics negotiation. Обычно это не 
  нужно, кроме случаев обхода parsing bugs.

<a id="examples"></a>
## Примеры

Предоставить metrics по path `/metrics` по умолчанию:

```caddy-d
metrics /metrics
```

Предоставить metrics по другому path:

```caddy-d
metrics /foo/bar/baz
```

Обслуживать metrics на отдельном subdomain:

```caddy
metrics.example.com {
	metrics
}
```

Отключить OpenMetrics negotiation:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
