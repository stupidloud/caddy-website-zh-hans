---
title: tracing (chỉ thị Caddyfile)
---

# tracing

Kích hoạt tích hợp với các cơ sở truy vết OpenTelemetry, sử dụng [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Khi được bật, nó sẽ lan truyền một ngữ cảnh truy vết hiện có hoặc khởi tạo một ngữ cảnh mới.

Nó sử dụng [gRPC](https://github.com/grpc/) làm giao thức xuất và W3C [tracecontext](https://www.w3.org/TR/trace-context/) và [baggage](https://www.w3.org/TR/baggage/) làm bộ lan truyền.

Trace ID và span ID được thêm vào [nhật ký truy cập](/docs/caddyfile/directives/log) dưới dạng các trường tiêu chuẩn `traceID` và `spanID`. Ngoài ra, các trình giữ chỗ `{http.vars.trace_id}` và `{http.vars.span_id}` có sẵn; ví dụ, bạn có thể sử dụng chúng trong một [`request_header`](request_header) để chuyển các ID cho ứng dụng của bạn.



<a id="syntax"></a>
## Cú pháp

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** là tên span. Vui lòng xem [hướng dẫn đặt tên](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md) span.
- **&lt;span_attributes&gt;** là các thuộc tính bổ sung được đính kèm vào mỗi span được ghi lại. Nhiều thuộc tính span được thiết lập theo mặc định theo [Quy ước ngữ nghĩa OTEL cho HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) như thông tin chi tiết về yêu cầu, phản hồi và máy khách.

  [Trình giữ chỗ](/docs/caddyfile/concepts#placeholders) có thể được sử dụng trong tên và thuộc tính span. Lưu ý rằng tên span được thiết lập trước khi yêu cầu được chuyển tiếp, vì vậy chỉ có thể sử dụng các trình giữ chỗ yêu cầu. Tất cả các trình giữ chỗ đều có sẵn trong các thuộc tính span.



<a id="configuration"></a>
## Cấu hình

<a id="environment-variables"></a>
### Biến môi trường

Nó có thể được cấu hình bằng các biến môi trường được xác định bởi [Đặc tả Biến Môi trường OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md).

Để biết chi tiết cấu hình bộ xuất, vui lòng xem [đặc tả](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Ví dụ:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```



<a id="examples"></a>
## Ví dụ

Dưới đây là một ví dụ **Caddyfile**:

```caddy
example.com {
	handle /api* {
		tracing {
			span api
		}
		request_header X-Trace-Id {http.vars.trace_id}
		reverse_proxy localhost:8081
	}

	handle {
		tracing {
			span app
			span_attributes {
				user_id {http.request.cookie.user-id}
			}
		}
		reverse_proxy localhost:8080
	}
}
```
