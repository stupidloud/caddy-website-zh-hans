---
title: "使用指标监控 Caddy"
---

# 使用指标监控 Caddy

无论您是在云端运行数千个 Caddy 实例，还是只在嵌入式设备上运行一台 Caddy 服务器，您大概率都会在某个时候想要对 Caddy 的整体状态及耗时有一个高层视图。换句话说，您需要能够监控 Caddy。

## 启用指标

您需要开启指标功能。

如果使用 Caddyfile，请[在全局选项中](/docs/caddyfile/options#metrics)启用指标：

```caddy
{
	metrics
}
```

如果使用 JSON，请将 `"metrics": {}` 添加到您的 [`apps > http > servers` 配置](/docs/json/apps/http/servers/) 中。

要添加按主机统计的指标，您可以插入 `per_host` 选项。现在，特定于主机的指标将带有 Host 标签。

```caddy
{
	metrics {
		per_host
	}
}
```

此配置将监控已配置的主机。如果配置了 HTTPS 服务器，则会监控该主机，即使未显式配置（例如按需建立 TLS 连接）。如果禁用了 HTTPS，则仅启用已配置的主机，以规避潜在的无限基数风险。若要在 HTTP 配置中监控所有主机（包括未配置的主机），请使用 `observe_catchall_hosts` 选项。

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## 普罗米修斯

[Prometheus](https://prometheus.io) 是一个监控平台，它通过抓取目标上的指标 HTTP 端点来采集指标。Prometheus 不仅能帮助您通过 [Grafana](https://grafana.com/docs/grafana/latest/introduction/) 等仪表盘工具展示指标，还可用于[告警](https://prometheus.io/docs/alerting/latest/overview/)。

与 Caddy 一样，Prometheus 也是用 Go 语言编写的，并以单一二进制文件的形式发布。要安装它，请参阅《[Prometheus 安装指南](https://prometheus.io/docs/prometheus/latest/installation/)》，或者在 macOS 上直接运行 `brew install prometheus`。

阅读 [Prometheus 文档](https://prometheus.io/docs/introduction/first_steps/)
如果您是初次接触 Prometheus，请继续阅读！

要配置 Prometheus 从 Caddy 抓取数据，您需要一份 YAML 配置文件
类似于这样的文件：

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # default is 1 minute

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

然后，您可以按以下方式启动 Prometheus：

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy 还可以将指标推送到 OpenTelemetry 协议（OTLP）端点。这对于原生支持 OTLP 的可观测性栈非常有用，例如 OpenTelemetry Collector、Grafana Alloy、Honeycomb 或其他直接接收 OTLP 指标的系统。

使用 `otlp` 选项：

```caddy
{
	metrics {
		otlp
	}
}
```

OTLP 导出器可通过标准的 [OpenTelemetry 环境变量](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)进行配置，并与 Caddy 的 [`tracing`](/docs/caddyfile/directives/tracing) 配置样式一致。例如：

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

默认情况下，导出器使用基于 HTTP/protobuf 的 OTLP。设置 `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` 可改用 gRPC。头部、端点、协议、导出器选择和采集间隔由诸如 `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`、`OTEL_EXPORTER_OTLP_HEADERS` 和 `OTEL_METRIC_EXPORT_INTERVAL` 等环境变量控制。

设置 `OTEL_METRICS_EXPORTER=none` 禁用指标导出，而无需更改
Caddyfile。

启用 OTLP 导出功能后，Caddy 会导出与 Prometheus 端点相同的一组指标。导出的指标会带上 `web_engine.name` 和 `web_engine.version` 这两个资源属性。

## Caddy 的指标

与任何由 Prometheus 监控的进程一样，Caddy 也会暴露一个 HTTP 端点
采用 [Prometheus 文本格式](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) 响应。Caddy 的 Prometheus 客户端也已配置为在协商成功时使用 [OpenMetrics 格式](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts)响应（也就是当 `Accept` 头设置为 `application/openmetrics-text; version=0.0.1` 时）。

默认情况下，`/metrics` 端点可通过 [管理 API](/docs/api) 访问（即 http://localhost:2019/metrics）。如果管理 API 已禁用，或者您希望监听不同的端口或路径，可以使用 [`metrics`](/docs/caddyfile/directives/metrics) [处理程序](/docs/caddyfile/directives/metrics)进行配置。

您可以使用任何浏览器或 HTTP 客户端查看这些指标，例如 `curl`:

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

您会看到许多指标，这些指标大致可分为以下 4 类：

- 运行时指标
- 管理 API 指标
- HTTP 中间件指标
- 反向代理指标

### 运行时指标

这些指标涵盖了 Caddy 进程的内部机制，并提供
由 Prometheus Go 客户端自动生成。这些名称前缀为 `go_*` ，
`process_*`.

请注意， `process_*` 指标仅在 Linux 和 Windows 系统上收集。

请参阅 [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector) 的文档，
[进程收集器](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector)，
以及 [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector)。

### 管理 API 指标

这些指标有助于监控 Caddy 管理 API。每个管理
已对端点进行监控，以追踪请求次数和错误。

这些指标的前缀为 `caddy_admin_*`.

例如：

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

一个统计管理端点处理的请求数量的计数器，包括
位于 `admin.api.*` 命名空间中。

标签 | 描述
-------|------------
`code` | HTTP 状态码
`handler` | 处理程序或模块名称
`method` | HTTP 方法
`path` | 管理员端点挂载到的 URL 路径

#### `caddy_admin_http_request_errors_total`

一个统计管理端点中遇到的错误数量的计数器，包括
位于 `admin.api.*` 命名空间中。

标签 | 描述
-------|------------
`handler` | 处理程序或模块名称
`method` | HTTP 方法
`path` | 管理员端点挂载到的 URL 路径

### HTTP 中间件指标

所有 Caddy HTTP 中间件处理程序都会自动进行性能监控，用于
确定请求延迟、首次字节到达时间、错误以及请求/响应体大小。

<aside class="tip">
	由于所有中间件处理程序都经过了性能监控，且许多请求由多个处理程序共同处理，因此请务必不要简单地将所有计数器数值相加。
</aside>

对于下面的直方图指标，目前无法配置分桶。
对于持续时间，默认值（[`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables)
使用了一组时间桶（5毫秒、10毫秒、25毫秒、50毫秒、100毫秒、250毫秒、500毫秒、1秒、2.5秒、5秒和10秒）。
关于大小，桶的容量分别为 256 字节、1 千字节、4 千字节、16 千字节、64 千字节、256 千字节、1 兆字节和 4 兆字节。

#### `caddy_http_requests_in_flight`

该服务器当前正在处理的请求数量的指标。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称

#### `caddy_http_request_errors_total`

处理请求时遇到中间件错误的计数器。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称

#### `caddy_http_requests_total`

HTTP(S) 请求计数器。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称

#### `caddy_http_request_duration_seconds`

往返请求时长的直方图。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称
`code` | HTTP 状态码
`method` | HTTP 方法

#### `caddy_http_request_size_bytes`

请求总大小（估计值）的直方图。包含请求主体。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称
`code` | HTTP 状态码
`method` | HTTP 方法

#### `caddy_http_response_size_bytes`

返回响应正文大小的直方图。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称
`code` | HTTP 状态码
`method` | HTTP 方法

#### `caddy_http_response_duration_seconds`

响应首字节到达时间的直方图。

标签 | 描述
-------|------------
`server` | 服务器名称
`handler` | 处理程序或模块名称
`code` | HTTP 状态码
`method` | HTTP 方法

### 反向代理指标

#### `caddy_reverse_proxy_upstreams_healthy`

衡量反向代理上游健康状况的指标。

值 `0` 表示上游不健康，而 `1` 表示上游健康。

标签 | 描述
-------|------------
`upstream` | 上游地址

## 示例查询

一旦 Prometheus 开始抓取 Caddy 的指标，您就可以开始看到一些关于 Caddy 表现的有趣数据。

<aside class="tip">

如果您已根据上述配置启动了 Prometheus 服务器来监控 Caddy，请尝试将以下查询粘贴到 Prometheus 控制台（[http://localhost:9090/graph](http://localhost:9090/graph)）中

</aside>


例如，要查看每秒请求率（按5分钟平均计算）：

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

要查看超过 100 毫秒延迟阈值的频率：

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

要查找在 `file_server`
处理程序，您可以使用如下查询：

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

或者查看成功请求的响应大小中位数（以字节为单位） `GET` 请求的
`file_server` 处理程序：

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
