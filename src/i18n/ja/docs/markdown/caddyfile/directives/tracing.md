---
title: tracing (Caddyfile directive)
---

# tracing

[`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go) を使って、OpenTelemetry tracing 機能との連携を有効にします。

有効にすると、既存の trace context を伝播するか、新しい context を初期化します。

exporter protocol には [gRPC](https://github.com/grpc/) を使い、propagator には W3C [tracecontext](https://www.w3.org/TR/trace-context/) と [baggage](https://www.w3.org/TR/baggage/) を使います。

trace ID と span ID は、標準の `traceID` と `spanID` フィールドとして [access logs](/docs/caddyfile/directives/log) に追加されます。さらに、`{http.vars.trace_id}` と `{http.vars.span_id}` placeholder も利用できます。たとえば、[`request_header`](request_header) でこれらを使い、ID を app に渡せます。



<a id="syntax"></a>
## 構文

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** は span 名です。span の [naming guidelines](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md) を参照してください。
- **&lt;span_attributes&gt;** は、記録される各 span に付加される追加属性です。request、response、client に関する詳細など、多くの span 属性は OTEL [Semantic conventions for HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) に従ってデフォルトで設定されます。

  [Placeholders](/docs/caddyfile/concepts#placeholders) は span 名と属性で使用できます。span 名はリクエストが転送される前に設定されるため、使用できるのは request placeholder だけです。span 属性ではすべての placeholder を使用できます。



<a id="configuration"></a>
## 設定

<a id="environment-variables"></a>
### 環境変数

[OpenTelemetry Environment Variable Specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md) で定義されている環境変数を使って設定できます。

exporter 設定の詳細については、[spec](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md) を参照してください。

例:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```



<a id="examples"></a>
## 例

以下は **Caddyfile** の例です。

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
