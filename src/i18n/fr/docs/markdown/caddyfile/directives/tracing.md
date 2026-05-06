---
title: tracing (directive Caddyfile)
---

# tracing

Active l'intégration avec les outils de traçage d'OpenTelemetry, en utilisant [`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go).

Lorsqu'il est activé, il propagera un contexte de trace existant ou en initialisera un nouveau.

Il utilise [gRPC](https://github.com/grpc/) comme protocole d'exportateur, et W3C [tracecontext](https://www.w3.org/TR/trace-context/) ainsi que [baggage](https://www.w3.org/TR/baggage/) comme propagateurs.

L'ID de trace (trace ID) et l'ID de segment (span ID) sont ajoutés aux [journaux d'accès](/docs/caddyfile/directives/log) en tant que champs standards `traceID` et `spanID`. De plus, les espaces réservés `{http.vars.trace_id}` et `{http.vars.span_id}` sont disponibles ; par exemple, vous pouvez les utiliser dans une directive [`request_header`](request_header) pour transmettre les IDs à votre application.



## Syntaxe

```caddy-d
tracing {
	span <nom_segment>
	span_attributes {
		<attr1> <valeur1>
		<attr2> <valeur2>
	}
}
```

- **&lt;nom_segment&gt;** est un nom de segment (span name). Veuillez consulter les [conventions de nommage](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md) des segments.
- **&lt;span_attributes&gt;** sont des attributs supplémentaires attachés à chaque segment enregistré. De nombreux attributs de segment sont définis par défaut selon les [conventions sémantiques OTEL pour les segments HTTP](https://opentelemetry.io/docs/specs/semconv/http/http-spans/), comme des détails sur la requête, la réponse et le client.

  Des [espaces réservés](/docs/caddyfile/concepts#placeholders) peuvent être utilisés dans les noms et attributs de segments. Gardez à l'esprit que le nom du segment est défini avant que la requête ne soit transmise, donc seuls les espaces réservés de requête peuvent être utilisés. Tous les espaces réservés sont disponibles dans les attributs de segment.



## Configuration

### Variables d'environnement

Elle peut être configurée en utilisant les variables d'environnement définies par la [Spécification des variables d'environnement OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md).

Pour les détails de configuration de l'exportateur, veuillez consulter la [spécification](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md).

Par exemple :

```bash
export OTEL_EXPORTER_OTLP_HEADERS="monEnTeteAuth=monJeton,autreEnTete=valeur"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://mon-point-acces-otlp:55680
```



## Exemples

Voici un exemple de **Caddyfile** :

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
