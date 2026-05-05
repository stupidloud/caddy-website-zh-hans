---
title: metrics (Caddyfile directive)
---

# metrics

収集した metrics を scraping 用に公開できるよう、Prometheus metrics exposition endpoint を設定します。**先に [global options で metrics を有効化](/docs/caddyfile/options#metrics)する必要があります。**

`/metrics` endpoint は [admin API](/docs/api) にも付属しています。そちらは設定できず、admin API が無効な場合は利用できません。

この endpoint は [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format)、またはネゴシエーションされた場合は [OpenMetrics exposition format](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts)（`application/openmetrics-text`）で metrics を返します。

[Monitoring Caddy with metrics](/docs/metrics) も参照してください。

<a id="syntax"></a>
## 構文

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** は OpenMetrics negotiation を無効にします。通常は不要ですが、パースの不具合を回避する必要がある場合に使います。

<a id="examples"></a>
## 例

デフォルトの `/metrics` パスで metrics を公開します。

```caddy-d
metrics /metrics
```

別のパスで metrics を公開します。

```caddy-d
metrics /foo/bar/baz
```

別の subdomain で metrics を提供します。

```caddy
metrics.example.com {
	metrics
}
```

OpenMetrics negotiation を無効にします。

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
