---
title: "跟踪（Caddyfile 指令）"
---

# 追踪

支持与 OpenTelemetry 追踪功能集成，使用 <a href="https://github.com/open-telemetry/opentelemetry-go">`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link"></a>。

启用后，它将传播现有的跟踪上下文或初始化一个新的跟踪上下文。

它使用 [gRPC](https://github.com/grpc/) 作为导出协议，并采用 W3C [tracecontext](https://www.w3.org/TR/trace-context/) 和 [baggage](https://www.w3.org/TR/baggage/) 作为传播器。

跟踪 ID 和跨度 ID 会作为标准字段添加到[访问日志中](/docs/caddyfile/directives/log) `traceID` 和 `spanID` 字段。此外， `{http.vars.trace_id}` 和 `{http.vars.span_id}` 占位符；例如，您可以在[`request_header`](request_header)中使用它们，将ID传递给您的应用。



<span id="syntax"/>
## 语法

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** 是一个 span 名称。请参阅 span [命名规范](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md)。
- **&lt;span_attributes&gt;** 是附加到每个已记录片段上的额外属性。许多片段属性会根据 OTEL [针对 HTTP 片段的语义规范](https://opentelemetry.io/docs/specs/semconv/http/http-spans/)默认设置，例如关于请求、响应和客户端的详细信息。

  在 span 名称和属性中可以使用[占位符](/docs/caddyfile/concepts#placeholders)。请注意，span 名称是在请求转发之前设定的，因此只能使用请求占位符。所有占位符均可在 span 属性中使用。



<span id="configuration"/>
## 配置

<span id="environment-variables"/>
### 环境变量

可以通过定义的环境变量进行配置
根据 [OpenTelemetry 环境变量规范](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md)。

有关导出配置的详细信息，请
参见[规格说明](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md)。

例如：

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```



<span id="examples"/>
## 示例

以下是一个 **Caddyfile** 的示例：

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
