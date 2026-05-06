---
title: tracing (Caddyfile directive)
---

# tracing

Habilita a integração com as facilidades de tracing do OpenTelemetry, usando [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Quando habilitado, ele propagará um contexto de trace existente ou inicializará um novo.

Ele usa [gRPC](https://github.com/grpc/) como protocolo de exportação e W3C [tracecontext](https://www.w3.org/TR/trace-context/) e [baggage](https://www.w3.org/TR/baggage/) como propagadores.

O trace ID e o span ID são adicionados aos [logs de acesso](/docs/caddyfile/directives/log) como os campos padrão `traceID` e `spanID`. Além disso, os placeholders `{http.vars.trace_id}` e `{http.vars.span_id}` ficam disponíveis; por exemplo, você pode usá-los em um [`request_header`](request_header) para repassar os IDs para sua aplicação.


<a id="syntax"></a>
## Sintaxe

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** é o nome de um span. Consulte as [diretrizes de nomenclatura](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md) de spans.
- **&lt;span_attributes&gt;** são atributos adicionais anexados a cada span registrado. Muitos atributos de span são definidos por padrão conforme as [convenções semânticas da OTEL para spans HTTP](https://opentelemetry.io/docs/specs/semconv/http/http-spans/), como detalhes sobre a requisição, a resposta e o cliente.

  [Placeholders](/docs/caddyfile/concepts#placeholders) podem ser usados em nomes de span e atributos. Tenha em mente que o nome do span é definido antes de a requisição ser encaminhada, então apenas placeholders de requisição podem ser usados. Todos os placeholders estão disponíveis nos atributos do span.


<a id="configuration"></a>
## Configuração

<a id="environment-variables"></a>
### Variáveis de ambiente

Ele pode ser configurado usando as variáveis de ambiente definidas pela [OpenTelemetry Environment Variable Specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md).

Para detalhes da configuração do exporter, consulte a [spec](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Por exemplo:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```


<a id="examples"></a>
## Exemplos

Aqui vai um exemplo de **Caddyfile**:

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
