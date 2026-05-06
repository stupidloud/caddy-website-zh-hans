---
title: tracing (direttiva del Caddyfile)
---

# tracing

Abilita l'integrazione con le funzionalità di tracciamento di OpenTelemetry, utilizzando [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Quando abilitato, propagherà un contesto di tracciamento esistente o ne inizializzerà uno nuovo.

Utilizza [gRPC](https://github.com/grpc/) come protocollo di esportazione e W3C [tracecontext](https://www.w3.org/TR/trace-context/) e [baggage](https://www.w3.org/TR/baggage/) come propagatori.

Il trace ID e lo span ID vengono aggiunti ai [log degli accessi](/docs/caddyfile/directives/log) come i campi standard `traceID` e `spanID`. Inoltre, sono disponibili i placeholder `{http.vars.trace_id}` e `{http.vars.span_id}`; ad esempio, potete usarli in una direttiva [`request_header`](request_header) per passare gli ID alla vostra app.


## Sintassi

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** è il nome di uno span. Consultate le [linee guida per la denominazione degli span](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md).
- **&lt;span_attributes&gt;** sono attributi aggiuntivi allegati a ogni span registrato. Molti attributi dello span sono impostati per impostazione predefinita secondo le [convenzioni semantiche OTEL per gli span HTTP](https://opentelemetry.io/docs/specs/semconv/http/http-spans/), come dettagli sulla richiesta, risposta e client.

  I [placeholder](/docs/caddyfile/concepts#placeholder) possono essere utilizzati nei nomi e negli attributi degli span. Tenete presente che il nome dello span viene impostato prima che la richiesta venga inoltrata, quindi possono essere utilizzati solo i placeholder della richiesta. Tutti i placeholder sono disponibili negli attributi degli span.


## Configurazione

### Variabili d'ambiente

Può essere configurato utilizzando le variabili d'ambiente definite dalla [Specifica delle Variabili d'Ambiente di OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md).

Per i dettagli sulla configurazione dell'esportatore, consultate la [specifica](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Per esempio:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="mioAuthHeader=mioToken,altroHeader=valore"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://mio-endpoint-otlp:55680
```


## Esempi

Ecco un esempio di **Caddyfile**:

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
