---
title: metrics (Caddyfile 指令)
---

<a id="metrics"></a>
# metrics

配置 Prometheus 指標公開端點，以便將收集到的指標公開供抓取。**必須先在 [全域選項](/docs/caddyfile/options#metrics) 中開啟 metrics。** 

請注意，`/metrics` 端點也附加在 [管理 API](/docs/api) 上，該端點不可配置，且在管理 API 被停用時不可用。

此端點將以 [Prometheus 公開格式](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) 傳回指標，或者如果經過協商，則以 [OpenMetrics 公開格式](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts) (`application/openmetrics-text`) 傳回。

另請參閱[使用指標監控 Caddy](/docs/metrics)。

<a id="syntax"></a>
## 語法

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** 停用 OpenMetrics 協商。通常沒有必要，除非是為了解決解析錯誤。

<a id="examples"></a>
## 範例

在預設的 `/metrics` 路徑公開指標：

```caddy-d
metrics /metrics
```

在另一個路徑公開指標：

```caddy-d
metrics /foo/bar/baz
```

在獨立的子網域提供指標服務：

```caddy
metrics.example.com {
	metrics
}
```

停用 OpenMetrics 協商：

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
