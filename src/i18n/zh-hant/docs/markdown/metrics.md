---
title: 使用指標監視 Caddy
---

<a id="monitoring-caddy-with-metrics"></a>
# 使用指標監視 Caddy

無論你是在雲端執行數千個 Caddy 實例，還是在嵌入式裝置上執行單個 Caddy 伺服器，你很可能在某個時刻想要對 Caddy 正在做什麼以及花費了多少時間有一個高層級的概覽。換句話說，你將需要能夠 *monitor* Caddy。

<a id="enabling-metrics"></a>
## 啟用指標

你需要開啟指標功能。

如果使用 Caddyfile，請在 [全域選項](/docs/caddyfile/options#metrics) 中啟用指標：

```caddy
{
	metrics
}
```

如果使用 JSON，請將 `"metrics": {}` 新增到你的 [`apps > http > servers` 組態](/docs/json/apps/http/servers/) 中。

要新增每個主機的指標，你可以插入 `per_host` 選項。主機特定的指標現在將帶有 Host 標籤。

```caddy
{
	metrics {
		per_host
	}
}
```

此組態將觀察已設定的主機。如果設定了 HTTPS 伺服器，即使沒有明確設定主機（例如：隨選 TLS 設置），也會觀察該主機。如果停用了 HTTPS，由於潛在的無限基數風險，僅啟用已設定的主機。要在 HTTP 設置中觀察所有主機（即使是未設定的主機），請使用 `observe_catchall_hosts` 選項。

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

<a id="prometheus"></a>
## Prometheus

[Prometheus](https://prometheus.io) 是一個監測平台，透過抓取這些目標上的指標 HTTP 端點來收集來自受監測目標的指標。除了協助你使用 [Grafana](https://grafana.com/docs/grafana/latest/introduction/) 之類的儀表板工具顯示指標外，Prometheus 也用於 [警報](https://prometheus.io/docs/alerting/latest/overview/)。

與 Caddy 一樣，Prometheus 是用 Go 編寫的，並作為單個二進位檔案分發。要安裝它，請參閱 [Prometheus 安裝文件](https://prometheus.io/docs/prometheus/latest/installation/)，或者在 MacOS 上只需執行 `brew install prometheus`。

如果你是 Prometheus 的新手，請閱讀 [Prometheus 文件](https://prometheus.io/docs/introduction/first_steps/)，否則請繼續閱讀！

要設定 Prometheus 從 Caddy 抓取指標，你將需要一個類似於此的 YAML 組態檔案：

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # 預設為 1 分鐘

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

然後你可以像這樣啟動 Prometheus：

```console
$ prometheus --config.file=prometheus.yaml
```

<a id="opentelemetry"></a>
## OpenTelemetry

Caddy 也可以將指標推送到 OpenTelemetry Protocol (OTLP) 端點。這對於 OTLP 原生可觀測性堆疊非常有用，例如 OpenTelemetry Collector、Grafana Alloy、Honeycomb 或其他直接接收 OTLP 指標的系統。

使用 `otlp` 選項啟用 OTLP 指標匯出：

```caddy
{
	metrics {
		otlp
	}
}
```

OTLP 匯出器使用標準的 [OpenTelemetry 環境變數](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/) 進行設定，與 Caddy 的 [`tracing`](/docs/caddyfile/directives/tracing) 組態風格相匹配。例如：

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

預設情況下，匯出器使用基於 HTTP/protobuf 的 OTLP。設定 `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` 以改用 gRPC。標頭、端點、協定、匯出器選擇和收集間隔由 `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`、`OTEL_EXPORTER_OTLP_HEADERS` 和 `OTEL_METRIC_EXPORT_INTERVAL` 等環境變數控制。

設定 `OTEL_METRICS_EXPORTER=none` 可以在不更改 Caddyfile 的情況下停用指標匯出。

啟用 OTLP 匯出後，Caddy 會匯出為 Prometheus 端點收集的相同指標。匯出的指標包括 `web_engine.name` 和 `web_engine.version` 的資源屬性。

<a id="caddys-metrics"></a>
## Caddy 的指標

與任何使用 Prometheus 監測的程序一樣，Caddy 公開了一個以 [Prometheus 闡述格式](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) 回應的 HTTP 端點。如果協商成功（即 `Accept` 標頭設定為 `application/openmetrics-text; version=0.0.1`），Caddy 的 Prometheus 客戶端也設定為使用 [OpenMetrics 闡述格式](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) 進行回應。

預設情況下，[admin API](/docs/api) 提供了一個 `/metrics` 端點（即 http://localhost:2019/metrics）。但如果停用了 admin API，或者你希望在不同的連接埠或路徑上進行監聽，你可以使用 [`metrics` handler](/docs/caddyfile/directives/metrics) 來設定它。

你可以使用任何瀏覽器或 HTTP 客戶端（如 `curl`）查看指標：

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

你將看到許多指標，大致分為 4 類：

- 執行階段指標
- Admin API 指標
- HTTP 中間件指標
- 反向代理指標

<a id="runtime-metrics"></a>
### 執行階段指標

這些指標涵蓋 Caddy 程序的內部，並由 Prometheus Go 客戶端自動提供。它們的前綴為 `go_*` 和 `process_*`。

請注意，`process_*` 指標僅在 Linux 和 Windows 上收集。

請參閱 [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector)、[Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector) 和 [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector) 的文件。

<a id="admin-api-metrics"></a>
### Admin API 指標

這些指標有助於監測 Caddy admin API。每個 admin 端點都經過檢測以追蹤請求計數和錯誤。

這些指標的前綴為 `caddy_admin_*`。

例如：

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

<a id="caddy-admin-http-requests-total"></a>
#### `caddy_admin_http_requests_total`

由 admin 端點處理的請求數計數器，包括 `admin.api.*` 命名空間中的模組。

標籤 | 描述
-------|------------
`code` | HTTP 狀態碼
`handler` | handler 或模組名稱
`method` | HTTP 方法
`path` | admin 端點掛載的 URL 路徑

<a id="caddy-admin-http-request-errors-total"></a>
#### `caddy_admin_http_request_errors_total`

admin 端點中遇到的錯誤數計數器，包括 `admin.api.*` 命名空間中的模組。

標籤 | 描述
-------|------------
`handler` | handler 或模組名稱
`method` | HTTP 方法
`path` | admin 端點掛載的 URL 路徑

<a id="http-middleware-metrics"></a>
### HTTP 中間件指標

所有 Caddy HTTP 中間件 handler 都會自動進行檢測，以確定請求延遲、首位元組時間、錯誤以及請求/回應主體大小。

<aside class="tip">
	由於所有中間件 handler 都經過檢測，且許多請求由多個 handler 處理，請注意不要簡單地將所有計數器加在一起。
</aside>

對於下面的直方圖指標，桶 (buckets) 目前不可設定。對於持續時間，使用預設的 ([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables) 桶集合（5ms、10ms、25ms、50ms、100ms、250ms、500ms、1s、2.5s、5s 和 10s）。對於大小，桶分別為 256b、1kiB、4kiB、16kiB、64kiB、256kiB、1MiB 和 4MiB。

<a id="caddy-http-requests-in-flight"></a>
#### `caddy_http_requests_in_flight`

此伺服器當前正在處理的請求數的量表 (gauge)。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱

<a id="caddy-http-request-errors-total"></a>
#### `caddy_http_request_errors_total`

處理請求時遇到的中間件錯誤計數器。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱

<a id="caddy-http-requests-total"></a>
#### `caddy_http_requests_total`

HTTP(S) 請求數計數器。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱

<a id="caddy-http-request-duration-seconds"></a>
#### `caddy_http_request_duration_seconds`

請求來回持續時間的直方圖。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱
`code` | HTTP 狀態碼
`method` | HTTP 方法

<a id="caddy-http-request-size-bytes"></a>
#### `caddy_http_request_size_bytes`

請求總（估計）大小的直方圖。包括主體。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱
`code` | HTTP 狀態碼
`method` | HTTP 方法

<a id="caddy-http-response-size-bytes"></a>
#### `caddy_http_response_size_bytes`

返回的回應主體大小的直方圖。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱
`code` | HTTP 狀態碼
`method` | HTTP 方法

<a id="caddy-http-response-duration-seconds"></a>
#### `caddy_http_response_duration_seconds`

回應首位元組時間的直方圖。

標籤 | 描述
-------|------------
`server` | 伺服器名稱
`handler` | handler 或模組名稱
`code` | HTTP 狀態碼
`method` | HTTP 方法

<a id="reverse-proxy-metrics"></a>
### 反向代理指標

<a id="caddy-reverse-proxy-upstreams-healthy"></a>
#### `caddy_reverse_proxy_upstreams_healthy`

反向代理上游健康狀況的量表 (gauge)。

值 `0` 表示上游不健康，而 `1` 表示上游健康。

標籤 | 描述
-------|------------
`upstream` | 上游地址

<a id="sample-queries"></a>
## 範例查詢

一旦你讓 Prometheus 抓取 Caddy 的指標，你就可以開始查看一些關於 Caddy 效能的有趣指標。

<aside class="tip">

如果你已經啟動了一個 Prometheus 伺服器並使用上述組態抓取 Caddy，請嘗試將這些查詢貼到 [http://localhost:9090/graph](http://localhost:9090/graph) 的 Prometheus UI 中。

</aside>


例如，要查看 5 分鐘內的平均每秒請求率：

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

要查看延遲閾值超過 100ms 的比率：

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

要在 `file_server` handler 上查找第 95 個百分位數的請求持續時間，你可以使用如下查詢：

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

或者查看 `file_server` handler 上成功 `GET` 請求的回應大小中位數（以位元組為單位）：

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
