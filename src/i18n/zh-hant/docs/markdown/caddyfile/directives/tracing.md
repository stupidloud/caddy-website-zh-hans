---
title: tracing (Caddyfile 指令)
---

<a id="tracing"></a>
# tracing

啟用與 OpenTelemetry 追蹤功能的整合，使用 [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go)。

啟用後，它將傳播現有的追蹤上下文（trace context）或初始化一個新的追蹤上下文。

它使用 [gRPC](https://github.com/grpc/) 作為導出器協定（exporter protocol），並使用 W3C [tracecontext](https://www.w3.org/TR/trace-context/) 和 [baggage](https://www.w3.org/TR/baggage/) 作為傳播器（propagator）。

追蹤 ID（trace ID）和 span ID 會作為標準的 `traceID` 和 `spanID` 欄位新增到 [存取紀錄（access logs）](/docs/caddyfile/directives/log) 中。此外，還可以使用 `{http.vars.trace_id}` 和 `{http.vars.span_id}` 這兩個 placeholder；例如，您可以在 [`request_header`](request_header) 中使用它們將 ID 傳遞給您的應用程式。



<a id="syntax"></a>
## 語法

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** 是 span 名稱。請參閱 span [命名指南](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md)。
- **&lt;span_attributes&gt;** 是附加到每個記錄的 span 的額外屬性。許多 span 屬性會根據 OTEL 的 [HTTP span 語義慣例](https://opentelemetry.io/docs/specs/semconv/http/http-spans/)（如請求、回應和客戶端的詳細資訊）預設設定。

  在 span 名稱和屬性中可以使用 [placeholder](/docs/caddyfile/concepts#placeholders)。請記住，span 名稱是在請求轉發之前設定的，因此只能使用請求相關的 placeholder。在 span 屬性中則可以使用所有的 placeholder。



<a id="configuration"></a>
## 配置

<a id="environment-variables"></a>
### 環境變數

可以使用由 [OpenTelemetry 環境變數規範](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md) 定義的環境變數進行配置。

有關導出器（exporter）配置的詳細資訊，請參閱 [規範](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md)。

例如：

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```



<a id="examples"></a>
## 範例

這是一個 **Caddyfile** 範例：

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
