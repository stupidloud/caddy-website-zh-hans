---
title: metrics (diretiva do Caddyfile)
---

# metrics

Configura um endpoint de exposição de métricas do Prometheus para que as métricas coletadas possam ser expostas para scraping. **As métricas devem ser [habilitadas nas suas opções globais](/docs/caddyfile/options#metrics) primeiro.**

Observe que um endpoint `/metrics` também é anexado à [API de administração](/docs/api), que não é configurável e não está disponível quando a API de administração está desativada.

Esse endpoint retornará métricas no [formato de exposição do Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) ou, se negociado, no [formato de exposição OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts) (`application/openmetrics-text`).

Veja também [Monitorando o Caddy com métricas](/docs/metrics).

## Sintaxe

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** desativa a negociação de OpenMetrics. Normalmente não é necessário, exceto quando for preciso contornar bugs de parsing.

## Exemplos

Expor métricas no caminho padrão `/metrics`:

```caddy-d
metrics /metrics
```

Expor métricas em outro caminho:

```caddy-d
metrics /foo/bar/baz
```

Servir métricas em um subdomínio separado:

```caddy
metrics.example.com {
	metrics
}
```

Desativar a negociação de OpenMetrics:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
