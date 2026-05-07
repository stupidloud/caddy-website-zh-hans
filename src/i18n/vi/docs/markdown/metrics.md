---
title: Giám sát Caddy bằng các số liệu (metrics)
---

<a id="monitoring-caddy-with-metrics"></a>
# Giám sát Caddy bằng các số liệu (metrics)

Cho dù bạn đang chạy hàng nghìn phiên bản Caddy trên đám mây hay một máy chủ Caddy duy nhất trên một thiết bị nhúng, rất có thể tại một thời điểm nào đó bạn sẽ muốn có một cái nhìn tổng quan cấp cao về những gì Caddy đang làm và mất bao lâu để thực hiện. Nói cách khác, bạn sẽ muốn có khả năng _giám sát_ Caddy.

<a id="enabling-metrics"></a>
## Kích hoạt số liệu (metrics)

Bạn sẽ cần bật tính năng số liệu.

Nếu sử dụng Caddyfile, hãy bật metrics [trong các tùy chọn toàn cục (global options)](/docs/caddyfile/options#metrics):

```caddy
{
	metrics
}
```

Nếu sử dụng JSON, hãy thêm `"metrics": {}` vào [cấu hình `apps > http > servers`](/docs/json/apps/http/servers/) của bạn.

Để thêm các số liệu cho từng host (per-host), bạn có thể chèn tùy chọn `per_host`. Các số liệu cụ thể cho host giờ đây sẽ có thẻ (tag) Host.

```caddy
{
	metrics {
		per_host
	}
}
```

Cấu hình này sẽ quan sát các host đã được cấu hình. Nếu máy chủ HTTPS được cấu hình, host đó sẽ được quan sát, ngay cả khi không được cấu hình rõ ràng, ví dụ: thiết lập TLS theo yêu cầu (on-demand TLS). Nếu HTTPS bị vô hiệu hóa, chỉ các host đã cấu hình mới được bật do rủi ro về số lượng phần tử (cardinality) có thể vô hạn. Để quan sát tất cả các host trong thiết lập HTTP, ngay cả những host không được cấu hình, hãy sử dụng tùy chọn `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io) là một nền tảng giám sát thu thập các số liệu từ các mục tiêu được giám sát bằng cách thu thập (scraping) các điểm cuối (endpoints) HTTP số liệu trên các mục tiêu này. Ngoài việc giúp bạn hiển thị các số liệu bằng công cụ bảng điều khiển (dashboard) như [Grafana](https://grafana.com/docs/grafana/latest/introduction/), Prometheus còn được sử dụng để [cảnh báo](https://prometheus.io/docs/alerting/latest/overview/).

Giống như Caddy, Prometheus được viết bằng Go và được phân phối dưới dạng một tệp thực thi duy nhất. Để cài đặt nó, hãy xem [tài liệu Cài đặt Prometheus](https://prometheus.io/docs/prometheus/latest/installation/), hoặc trên MacOS chỉ cần chạy `brew install prometheus`.

Đọc [tài liệu Prometheus](https://prometheus.io/docs/introduction/first_steps/) nếu bạn hoàn toàn mới làm quen với Prometheus, nếu không hãy đọc tiếp!

Để cấu hình Prometheus thu thập dữ liệu từ Caddy, bạn sẽ cần một tệp cấu hình YAML tương tự như sau:

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # mặc định là 1 phút

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

Sau đó, bạn có thể khởi động Prometheus như thế này:

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy cũng có thể đẩy các số liệu đến một điểm cuối Giao thức OpenTelemetry (OTLP). Điều này hữu ích cho các ngăn xếp quan sát (observability stacks) bản địa OTLP, chẳng hạn như OpenTelemetry Collector, Grafana Alloy, Honeycomb hoặc các hệ thống khác nhận trực tiếp các số liệu OTLP.

Kích hoạt xuất số liệu OTLP bằng tùy chọn `otlp`:

```caddy
{
	metrics {
		otlp
	}
}
```

Bộ xuất (exporter) OTLP được cấu hình bằng các [biến môi trường OpenTelemetry](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/) tiêu chuẩn, phù hợp với phong cách cấu hình [`tracing`](/docs/caddyfile/directives/tracing) của Caddy. Ví dụ:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Theo mặc định, bộ xuất sử dụng OTLP qua HTTP/protobuf. Đặt `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` để sử dụng gRPC thay thế. Các tiêu đề (headers), điểm cuối, giao thức, lựa chọn bộ xuất và khoảng thời gian thu thập được kiểm soát bởi các biến môi trường như `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` và `OTEL_METRIC_EXPORT_INTERVAL`.

Đặt `OTEL_METRICS_EXPORTER=none` để vô hiệu hóa việc xuất số liệu mà không cần thay đổi Caddyfile.

Khi tính năng xuất OTLP được bật, Caddy sẽ xuất các số liệu tương tự được thu thập cho điểm cuối Prometheus. Các số liệu được xuất bao gồm các thuộc tính tài nguyên cho `web_engine.name` và `web_engine.version`.

<a id="caddys-metrics"></a>
## Các số liệu của Caddy

Giống như bất kỳ tiến trình nào được giám sát bằng Prometheus, Caddy hiển thị một điểm cuối HTTP phản hồi theo [định dạng trình bày Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format). Trình khách (client) Prometheus của Caddy cũng được cấu hình để phản hồi bằng [định dạng trình bày OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) nếu được thương lượng (nghĩa là, nếu tiêu đề `Accept` được đặt thành `application/openmetrics-text; version=0.0.1`).

Theo mặc định, có một điểm cuối `/metrics` có sẵn tại [admin API](/docs/api) (tức là http://localhost:2019/metrics). Nhưng nếu admin API bị vô hiệu hóa hoặc bạn muốn lắng nghe trên một cổng hoặc đường dẫn khác, bạn có thể sử dụng [trình xử lý `metrics`](/docs/caddyfile/directives/metrics) để cấu hình điều này.

Bạn có thể xem các số liệu bằng bất kỳ trình duyệt hoặc trình khách HTTP nào như `curl`:

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

Có một số số liệu bạn sẽ thấy, về cơ bản thuộc 4 loại:

- Số liệu thời gian chạy (Runtime metrics)
- Số liệu Admin API
- Số liệu HTTP Middleware
- Số liệu Reverse proxy

<a id="runtime-metrics"></a>
### Số liệu thời gian chạy (Runtime metrics)

Các số liệu này bao quát các phần nội bộ của tiến trình Caddy và được cung cấp tự động bởi Prometheus Go Client. Chúng được bắt đầu bằng tiền tố `go_*` và `process_*`.

Lưu ý rằng các số liệu `process_*` chỉ được thu thập trên Linux và Windows.

Xem tài liệu cho [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector), [Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector), và [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

<a id="admin-api-metrics"></a>
### Số liệu Admin API

Đây là các số liệu giúp giám sát Caddy admin API. Mỗi điểm cuối admin được thiết lập để theo dõi số lượng yêu cầu và lỗi.

Các số liệu này có tiền tố là `caddy_admin_*`.

Ví dụ:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

<a id="caddyadminhttprequeststotal"></a>
#### `caddy_admin_http_requests_total`

Một bộ đếm số lượng yêu cầu được xử lý bởi các điểm cuối admin, bao gồm các mô-đun trong không gian tên (namespace) `admin.api.*`.

Nhãn (Label) | Mô tả
-------|------------
`code` | Mã trạng thái HTTP
`handler` | Tên trình xử lý hoặc mô-đun
`method` | Phương thức HTTP
`path` | Đường dẫn URL mà điểm cuối admin được gắn vào

<a id="caddyadminhttprequesterrorstotal"></a>
#### `caddy_admin_http_request_errors_total`

Một bộ đếm số lượng lỗi gặp phải trong các điểm cuối admin, bao gồm các mô-đun trong không gian tên `admin.api.*`.

Nhãn | Mô tả
-------|------------
`handler` | Tên trình xử lý hoặc mô-đun
`method` | Phương thức HTTP
`path` | Đường dẫn URL mà điểm cuối admin được gắn vào

<a id="http-middleware-metrics"></a>
### Số liệu HTTP Middleware

Tất cả các trình xử lý middleware HTTP của Caddy được thiết lập tự động để xác định độ trễ yêu cầu, thời gian cho byte đầu tiên (time-to-first-byte), lỗi và kích thước thân (body) yêu cầu/phản hồi.

<aside class="tip">
	Bởi vì tất cả các trình xử lý middleware đều được thiết lập, và nhiều yêu cầu được xử lý bởi nhiều trình xử lý, hãy đảm bảo không chỉ đơn giản là cộng tất cả các bộ đếm lại với nhau.
</aside>

Đối với các số liệu biểu đồ (histogram) bên dưới, các thùng (buckets) hiện không thể cấu hình. Đối với thời gian, bộ thùng mặc định ([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables)) được sử dụng (5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s và 10s). Đối với kích thước, các thùng là 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB và 4MiB.

<a id="caddyhttprequestsinflight"></a>
#### `caddy_http_requests_in_flight`

Một thước đo (gauge) số lượng yêu cầu hiện đang được xử lý bởi máy chủ này.

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun

<a id="caddyhttprequesterrorstotal"></a>
#### `caddy_http_request_errors_total`

Một bộ đếm các lỗi middleware gặp phải trong khi xử lý yêu cầu.

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun

<a id="caddyhttprequeststotal"></a>
#### `caddy_http_requests_total`

Một bộ đếm các yêu cầu HTTP(S) được thực hiện.

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun

<a id="caddyhttprequestdurationseconds"></a>
#### `caddy_http_request_duration_seconds`

Một biểu đồ về thời gian khứ hồi của yêu cầu.

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun
`code` | Mã trạng thái HTTP
`method` | Phương thức HTTP

<a id="caddyhttprequestsizebytes"></a>
#### `caddy_http_request_size_bytes`

Một biểu đồ về tổng kích thước (ước tính) của yêu cầu. Bao gồm cả thân (body).

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun
`code` | Mã trạng thái HTTP
`method` | Phương thức HTTP

<a id="caddyhttpresponsesizebytes"></a>
#### `caddy_http_response_size_bytes`

Một biểu đồ về kích thước của thân phản hồi được trả về.

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun
`code` | Mã trạng thái HTTP
`method` | Phương thức HTTP

<a id="caddyhttpresponsedurationseconds"></a>
#### `caddy_http_response_duration_seconds`

Một biểu đồ về thời gian cho byte đầu tiên của các phản hồi.

Nhãn | Mô tả
-------|------------
`server` | Tên máy chủ
`handler` | Tên trình xử lý hoặc mô-đun
`code` | Mã trạng thái HTTP
`method` | Phương thức HTTP

<a id="reverse-proxy-metrics"></a>
### Số liệu Reverse proxy

<a id="caddyreverseproxyupstreamshealthy"></a>
#### `caddy_reverse_proxy_upstreams_healthy`

Một thước đo về tình trạng sức khỏe của các upstream reverse proxy.

Giá trị `0` có nghĩa là upstream không khỏe mạnh, trong khi `1` có nghĩa là upstream khỏe mạnh.

Nhãn | Mô tả
-------|------------
`upstream` | Địa chỉ của upstream

<a id="sample-queries"></a>
## Các truy vấn mẫu

Khi bạn đã có Prometheus thu thập các số liệu của Caddy, bạn có thể bắt đầu thấy một số số liệu thú vị về hiệu suất của Caddy.

<aside class="tip">

Nếu bạn đã khởi động một máy chủ Prometheus để thu thập dữ liệu Caddy với cấu hình ở trên, hãy thử dán các truy vấn này vào giao diện người dùng Prometheus tại [http://localhost:9090/graph](http://localhost:9090/graph)

</aside>


Ví dụ, để xem tỷ lệ yêu cầu mỗi giây, tính trung bình trong 5 phút:

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Để xem tỷ lệ mà ngưỡng độ trễ 100ms của bạn đang bị vượt quá:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Để tìm thời gian yêu cầu ở phân vị thứ 95 trên trình xử lý `file_server`, bạn có thể sử dụng một truy vấn như sau:

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

Hoặc để xem kích thước phản hồi trung vị tính bằng byte cho các yêu cầu `GET` thành công trên trình xử lý `file_server`:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
