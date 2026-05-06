---
title: metrics (directiva de Caddyfile)
---

# metrics

Configura un endpoint de exposición de métricas de Prometheus para que las métricas recopiladas puedan exponerse para ser scrapeadas. **Las métricas deben estar [activadas en tus opciones globales](/docs/caddyfile/options#metrics) primero.**

Ten en cuenta que también se adjunta un endpoint `/metrics` a la [API de administración](/docs/api), que no es configurable y no está disponible cuando la API de administración está deshabilitada.

Este endpoint devolverá métricas en el [formato de exposición de Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format)
o, si se negocia, en el [formato de exposición OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts)
(`application/openmetrics-text`).

Consulta también [Monitorizar Caddy con métricas](/docs/metrics)。

## Sintaxis

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** desactiva la negociación OpenMetrics. Normalmente no es
  necesario, salvo cuando hace falta evitar errores de análisis.

## Ejemplos

Exponer métricas en la ruta `/metrics` predeterminada:

```caddy-d
metrics /metrics
```

Exponer métricas en otra ruta:

```caddy-d
metrics /foo/bar/baz
```

Servir métricas en un subdominio separado:

```caddy
metrics.example.com {
	metrics
}
```

Desactivar la negociación OpenMetrics:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
