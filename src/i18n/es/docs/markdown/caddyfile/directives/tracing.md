---
title: tracing (Directiva de Caddyfile)
---

# tracing

Habilita la integración con las instalaciones de trazado de OpenTelemetry, usando [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Cuando está habilitado, propagará un contexto de traza existente o inicializará uno nuevo.

Usa [gRPC](https://github.com/grpc/) como protocolo de exportador y W3C [tracecontext](https://www.w3.org/TR/trace-context/) y [baggage](https://www.w3.org/TR/baggage/) como propagadores.

El trace ID y el span ID se agregan a los [access logs](/docs/caddyfile/directives/log) como los campos estándar `traceID` y `spanID`. Además, están disponibles los placeholders `{http.vars.trace_id}` y `{http.vars.span_id}`; por ejemplo, puedes usarlos en un [`request_header`](request_header) para pasar los IDs a tu app.


## Sintaxis

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** es un nombre de span. Consulta las [guías de nomenclatura de span](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md).
- **&lt;span_attributes&gt;** son atributos adicionales adjuntos a cada span registrado. Muchos atributos de span se establecen por defecto según las [convenciones semánticas de OTEL para HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/), como detalles sobre la solicitud, respuesta y cliente.

  Los [placeholders](/docs/caddyfile/concepts#placeholders) pueden usarse en los nombres y atributos de span. Ten en cuenta que el nombre del span se establece antes de reenviar la solicitud, por lo que solo se pueden usar placeholders de la solicitud. Todos los placeholders están disponibles en los atributos del span.


## Configuración

### Variables de entorno

Puede configurarse usando las variables de entorno definidas por la
[Especificación de variables de entorno de OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md).

Para detalles de configuración del exportador, consulta la
[especificación](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Por ejemplo:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```


## Ejemplos

Aquí tienes un ejemplo de **Caddyfile**:

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
