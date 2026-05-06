---
title: metrics (directive Caddyfile)
---

# metrics

Configure un point d'accès d'exposition de métriques Prometheus afin que les métriques collectées puissent être exposées pour être interroguées (scraping). **Les métriques doivent être [activées dans vos options globales](/docs/caddyfile/options#metrics) au préalable.**

Notez qu'un point d'accès `/metrics` est également rattaché à l'[API d'administration](/docs/api), lequel n'est pas configurable, et n'est pas disponible lorsque l'API d'administration est désactivée.

Ce point d'accès retournera des métriques au [format d'exposition Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) ou, si négocié, au [format d'exposition OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts) (`application/openmetrics-text`).

Consultez également [Surveiller Caddy avec des métriques](/docs/metrics).

## Syntaxe

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** désactive la négociation OpenMetrics. Généralement non nécessaire sauf pour contourner des bugs d'analyse.

## Exemples

Exposer les métriques sur le chemin par défaut `/metrics` :

```caddy-d
metrics /metrics
```

Exposer les métriques sur un autre chemin :

```caddy-d
metrics /foo/bar/baz
```

Servir les métriques sur un sous-domaine séparé :

```caddy
metrics.example.com {
	metrics
}
```

Désactiver la négociation OpenMetrics :

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
