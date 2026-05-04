---
title: "指标（Caddyfile 指令）"
---

# 指标

配置一个 Prometheus 指标发布端点，以便收集到的指标能够
将暴露给爬虫抓取。**请先[在全局选项中开启](/docs/caddyfile/options#metrics)指标功能。**

请注意， `/metrics` 该端点也连接到了[管理 API](/docs/api)，
该功能不可配置，且在禁用管理 API 时不可用。

该端点将以 [Prometheus 数据呈现格式](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format)返回指标
或者，如果经过协商，则采用 [OpenMetrics 描述格式](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts)
(`application/openmetrics-text`).

另请参阅[“使用指标监控 Caddy](/docs/metrics)”。

## 语法

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** 禁用 OpenMetrics 协商。通常不 
  除非需要绕过解析错误，否则这是必要的。

## 示例

在默认路径下公开指标 `/metrics` 路径：

```caddy-d
metrics /metrics
```

在另一个路径上暴露指标：

```caddy-d
metrics /foo/bar/baz
```

在单独的子域名上提供指标：

```caddy
metrics.example.com {
	metrics
}
```

禁用 OpenMetrics 协商：

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
