---
title: tracing (директива Caddyfile)
---

# tracing

Включает интеграцию с OpenTelemetry tracing facilities, используя [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Когда включено, propagates существующий trace context или инициализирует новый.

В качестве exporter protocol используется [gRPC](https://github.com/grpc/), а W3C [tracecontext](https://www.w3.org/TR/trace-context/) и [baggage](https://www.w3.org/TR/baggage/) используются как propagators.

Trace ID и span ID добавляются в [access logs](/docs/caddyfile/directives/log) как стандартные поля `traceID` и `spanID`. Кроме того, доступны placeholders `{http.vars.trace_id}` и `{http.vars.span_id}`; например, их можно использовать в [`request_header`](request_header), чтобы передать IDs вашему app.



<a id="syntax"></a>
## Синтаксис

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** — имя span. См. [рекомендации по именованию](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md) span.
- **&lt;span_attributes&gt;** — дополнительные attributes, прикрепляемые к каждому recorded span. Многие span attributes устанавливаются по умолчанию согласно OTEL [Semantic conventions for HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/), например детали request, response и client.

  [Placeholders](/docs/caddyfile/concepts#placeholders) можно использовать в span names и attributes. Учитывайте, что span name устанавливается до forwarding запроса, поэтому можно использовать только request placeholders. В span attributes доступны все placeholders.



<a id="configuration"></a>
## Конфигурация

<a id="environment-variables"></a>
### Environment variables

Ее можно настроить с помощью environment variables, определенных
в [OpenTelemetry Environment Variable Specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md).

Подробности конфигурации exporter см.
в [spec](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Например:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```



<a id="examples"></a>
## Примеры

Пример **Caddyfile**:

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
