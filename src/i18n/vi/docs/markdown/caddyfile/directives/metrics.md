---
title: metrics (Chỉ thị Caddyfile)
---

# metrics

Cấu hình một điểm cuối hiển thị các chỉ số (metrics) Prometheus để các chỉ số đã thu thập có thể được hiển thị cho việc thu thập dữ liệu (scraping). **Các chỉ số phải được [bật trong tùy chọn toàn cục (global options) của bạn](/docs/caddyfile/options#metrics) trước.**

Lưu ý rằng một điểm cuối `/metrics` cũng được đính kèm vào [admin API](/docs/api), cái mà không thể cấu hình được, và không khả dụng khi admin API bị vô hiệu hóa.

Điểm cuối này sẽ trả về các chỉ số theo [định dạng hiển thị Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) hoặc, nếu được thương lượng, theo [định dạng hiển thị OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts) (`application/openmetrics-text`).

Xem thêm [Giám sát Caddy với các chỉ số](/docs/metrics).

<a id="syntax"></a>
## Cú pháp

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics** vô hiệu hóa thương lượng OpenMetrics. Thường không cần thiết ngoại trừ khi cần khắc phục các lỗi phân tích cú pháp.

<a id="examples"></a>
## Ví dụ

Hiển thị các chỉ số tại đường dẫn mặc định `/metrics`:

```caddy-d
metrics /metrics
```

Hiển thị các chỉ số tại một đường dẫn khác:

```caddy-d
metrics /foo/bar/baz
```

Cung cấp các chỉ số tại một miền phụ (subdomain) riêng biệt:

```caddy
metrics.example.com {
	metrics
}
```

Vô hiệu hóa thương lượng OpenMetrics:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
