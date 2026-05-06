---
title: tracing (Caddyfile 지시어)
---

# tracing

[`opentelemetry-go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/open-telemetry/opentelemetry-go)를 사용하여 OpenTelemetry 추적 시설과의 통합을 활성화합니다.

활성화되면 기존 추적 컨텍스트를 전파하거나 새로운 컨텍스트를 초기화합니다.

내보내기 프로토콜로 [gRPC](https://github.com/grpc/)를 사용하고, 전파자로 W3C [tracecontext](https://www.w3.org/TR/trace-context/) 및 [baggage](https://www.w3.org/TR/baggage/)를 사용합니다.

추적 ID와 스팬 ID는 표준 `traceID` 및 `spanID` 필드로 [액세스 로그](/docs/caddyfile/directives/log)에 추가됩니다. 또한 `{http.vars.trace_id}` 및 `{http.vars.span_id}` 자리 표시자를 사용할 수 있습니다. 예를 들어, 앱에 ID를 전달하기 위해 [`request_header`](request_header)에서 이를 사용할 수 있습니다.

## 구문 <a id="syntax"></a>

```caddy-d
tracing {
	span <span_name>
	span_attributes {
		<attr1> <value1>
		<attr2> <value2>
	}
}
```

- **&lt;span_name&gt;** 은 스팬 이름입니다. 스팬 [명명 가이드라인](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/trace/api.md)을 참조하십시오.
- **&lt;span_attributes&gt;** 는 기록된 각 스팬에 첨부되는 추가 속성입니다. 요청, 응답 및 클라이언트에 대한 세부 정보와 같은 HTTP 스팬에 대한 OTEL [의미 체계 규약(Semantic conventions)](https://opentelemetry.io/docs/specs/semconv/http/http-spans/)에 따라 많은 스팬 속성이 기본적으로 설정됩니다.

  스팬 이름과 속성에 [자리 표시자](/docs/caddyfile/concepts#placeholders)를 사용할 수 있습니다. 스팬 이름은 요청이 전달되기 전에 설정되므로 요청 자리 표시자만 사용할 수 있습니다. 스팬 속성에서는 모든 자리 표시자를 사용할 수 있습니다.

## 설정 <a id="configuration"></a>

### 환경 변수 <a id="environment-variables"></a>

[OpenTelemetry 환경 변수 사양](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/configuration/sdk-environment-variables.md)에 정의된 환경 변수를 사용하여 설정할 수 있습니다.

내보내기 설정에 대한 자세한 내용은 [사양](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.7.0/specification/protocol/exporter.md)을 참조하십시오.

예시:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="myAuthHeader=myToken,anotherHeader=value"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://my-otlp-endpoint:55680
```

## 예제 <a id="examples"></a>

다음은 **Caddyfile** 예시입니다:

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
