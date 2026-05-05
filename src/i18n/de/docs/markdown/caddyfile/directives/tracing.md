---
title: tracing (Caddyfile directive)
---

# tracing

Aktiviert die Integration mit OpenTelemetry-Tracing-Funktionen unter Verwendung von [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Wenn aktiviert, wird ein vorhandener Trace-Kontext weitergegeben oder ein neuer initialisiert.

Als Exporter-Protokoll wird [gRPC](https://github.com/grpc/) verwendet, als Propagatoren W3C [tracecontext](https://www.w3.org/TR/trace-context/) und [baggage](https://www.w3.org/TR/baggage/).

Die Trace-ID und Span-ID werden Access Logs als Standardfelder `traceID` und `spanID` hinzugefügt. Zusätzlich sind die Platzhalter `{http.vars.trace_id}` und `{http.vars.span_id}` verfügbar; Sie können sie beispielsweise in einem [`request_header`](request_header) verwenden, um die IDs an Ihre App weiterzugeben.



<a id="syntax"></a>
## Syntax

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** ist ein Span-Name. Siehe dazu die [Namensrichtlinien](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md) für Spans.
- **&lt;span_attributes&gt;** sind zusätzliche Attribute, die jedem aufgezeichneten Span angehängt werden. Viele Span-Attribute werden standardmäßig gemäß den OTEL [Semantic conventions for HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) gesetzt, etwa Details zu Anfrage, Antwort und Client.

  [Platzhalter](/docs/caddyfile/concepts#placeholders) können in Span-Namen und -Attributen verwendet werden. Beachten Sie, dass der Span-Name gesetzt wird, bevor die Anfrage weitergeleitet wird; deshalb können dort nur Anfrage-Platzhalter verwendet werden. In Span-Attributen sind alle Platzhalter verfügbar.



<a id="configuration"></a>
## Konfiguration

<a id="environment-variables"></a>
### Umgebungsvariablen

Die Konfiguration kann über die Umgebungsvariablen erfolgen, die in der [OpenTelemetry Environment Variable Specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md) definiert sind.

Details zur Exporter-Konfiguration finden Sie in der [Spezifikation](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Zum Beispiel:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```



<a id="examples"></a>
## Beispiele

Hier ist ein **Caddyfile**-Beispiel:

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
