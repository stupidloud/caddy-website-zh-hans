---
title: metrics (direttiva del Caddyfile)
---

# metrics

Configura un endpoint di esposizione delle metriche di Prometheus in modo che le metriche raccolte possano essere esposte per lo scraping. **Le metriche devono prima essere [attivate nelle opzioni globali](/docs/caddyfile/options#metrics).**

Si noti che un endpoint `/metrics` è associato anche all'[API di amministrazione](/docs/api), il quale non è configurabile e non è disponibile quando l'API di amministrazione è disabilitata.

Questo endpoint restituirà le metriche nel [formato di esposizione di Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) o, se negoziato, nel [formato di esposizione OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts) (`application/openmetrics-text`).

Consultate anche [Monitoraggio di Caddy con le metriche](/docs/metrics).

## Sintassi

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** disabilita la negoziazione OpenMetrics. Solitamente non necessario, eccetto quando occorre aggirare bug di analisi.

## Esempi

Espone le metriche sul percorso predefinito `/metrics`:

```caddy-d
metrics /metrics
```

Espone le metriche su un altro percorso:

```caddy-d
metrics /foo/bar/baz
```

Serve le metriche su un sottodominio separato:

```caddy
metrics.example.com {
	metrics
}
```

Disabilita la negoziazione OpenMetrics:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
