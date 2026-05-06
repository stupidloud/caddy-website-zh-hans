---
title: 메트릭으로 Caddy 모니터링
---

# 메트릭으로 Caddy 모니터링

클라우드에서 수천 개의 Caddy 인스턴스를 실행하든, 임베디드 디바이스에서 단일 Caddy 서버를 실행하든, 어느 시점에서는 Caddy가 무엇을 하고 있고 시간이 얼마나 걸리는지에 대한 개략적인 정보를 원하게 될 가능성이 높습니다. 다시 말해, Caddy를 *모니터링*하고 싶어질 것입니다.

## 메트릭 활성화

메트릭을 켜야 합니다.

Caddyfile을 사용하는 경우 [전역 옵션](/docs/caddyfile/options#metrics)에서 메트릭을 활성화합니다.

```caddy
{
	metrics
}
```

JSON을 사용하는 경우 [`apps > http > servers` 구성](/docs/json/apps/http/servers/)에 `"metrics": {}`를 추가합니다.

호스트별 메트릭을 추가하려면 `per_host` 옵션을 삽입할 수 있습니다. 이제 호스트별 메트릭에 Host 태그가 지정됩니다.

```caddy
{
	metrics {
		per_host
	}
}
```

이 구성은 구성된 호스트를 관찰합니다. HTTPS 서버가 구성된 경우, 온디맨드 TLS 설정과 같이 명시적으로 구성되지 않은 경우에도 호스트가 관찰됩니다. HTTPS가 비활성화된 경우 무한 카디널리티 위험 가능성 때문에 구성된 호스트만 활성화됩니다. 구성되지 않은 호스트를 포함하여 HTTP 설정의 모든 호스트를 관찰하려면 `observe_catchall_hosts` 옵션을 사용합니다.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io)는 대상의 메트릭 HTTP 엔드포인트를 스크랩하여 모니터링 대상에서 메트릭을 수집하는 모니터링 플랫폼입니다. [Grafana](https://grafana.com/docs/grafana/latest/introduction/)와 같은 대시보드 도구로 메트릭을 표시하는 데 도움을 줄 뿐만 아니라, Prometheus는 [경고(alerting)](https://prometheus.io/docs/alerting/latest/overview/)에도 사용됩니다.

Caddy와 마찬가지로 Prometheus는 Go로 작성되었으며 단일 바이너리로 배포됩니다. 설치하려면 [Prometheus 설치 문서](https://prometheus.io/docs/prometheus/latest/installation/)를 참조하거나 MacOS의 경우 `brew install prometheus`를 실행하기만 하면 됩니다.

Prometheus를 처음 사용하는 경우 [Prometheus 문서](https://prometheus.io/docs/introduction/first_steps/)를 읽어보시고, 그렇지 않다면 계속 읽어보세요!

Caddy에서 스크랩하도록 Prometheus를 구성하려면 다음과 유사한 YAML 구성 파일이 필요합니다.

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # 기본값은 1분입니다.

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

그런 다음 이와 같이 Prometheus를 시작할 수 있습니다.

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy는 OTLP(OpenTelemetry Protocol) 엔드포인트로 메트릭을 푸시할 수도 있습니다. 이는 OpenTelemetry Collector, Grafana Alloy, Honeycomb 또는 OTLP 메트릭을 직접 수신하는 기타 시스템과 같은 OTLP 네이티브 관찰 가능성 스택에 유용합니다.

`otlp` 옵션으로 OTLP 메트릭 내보내기를 활성화합니다.

```caddy
{
	metrics {
		otlp
	}
}
```

OTLP 내보내기(exporter)는 Caddy의 [`tracing`](/docs/caddyfile/directives/tracing) 구성 스타일과 일치하는 표준 [OpenTelemetry 환경 변수](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)로 구성됩니다. 예를 들어:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

기본적으로 내보내기는 HTTP/protobuf를 통한 OTLP를 사용합니다. 대신 gRPC를 사용하려면 `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`를 설정합니다. 헤더, 엔드포인트, 프로토콜, 내보내기 선택 및 수집 간격은 `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` 및 `OTEL_METRIC_EXPORT_INTERVAL`과 같은 환경 변수로 제어됩니다.

Caddyfile을 변경하지 않고 메트릭 내보내기를 비활성화하려면 `OTEL_METRICS_EXPORTER=none`을 설정합니다.

OTLP 내보내기가 활성화되면 Caddy는 Prometheus 엔드포인트에 대해 수집된 것과 동일한 메트릭을 내보냅니다. 내보낸 메트릭에는 `web_engine.name` 및 `web_engine.version`에 대한 리소스 속성이 포함됩니다.

## Caddy의 메트릭

Prometheus로 모니터링되는 모든 프로세스와 마찬가지로 Caddy는 [Prometheus 노출 형식(exposition format)](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format)으로 응답하는 HTTP 엔드포인트를 노출합니다. 협상된 경우(즉, `Accept` 헤더가 `application/openmetrics-text; version=0.0.1`로 설정된 경우) Caddy의 Prometheus 클라이언트도 [OpenMetrics 노출 형식](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts)으로 응답하도록 구성됩니다.

기본적으로 [관리자 API](/docs/api)에서 사용할 수 있는 `/metrics` 엔드포인트가 있습니다(예: http://localhost:2019/metrics). 그러나 관리자 API가 비활성화되어 있거나 다른 포트 또는 경로에서 수신 대기하려는 경우 [`metrics` 핸들러](/docs/caddyfile/directives/metrics)를 사용하여 이를 구성할 수 있습니다.

`curl`과 같은 브라우저나 HTTP 클라이언트로 메트릭을 볼 수 있습니다.

```console
$ curl http://localhost:2019/metrics
# HELP caddy_admin_http_requests_total Counter of requests made to the Admin API's HTTP endpoints.
# TYPE caddy_admin_http_requests_total counter
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 2
# HELP caddy_http_request_duration_seconds Histogram of round-trip request durations.
# TYPE caddy_http_request_duration_seconds histogram
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.005"} 1
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.01"} 1
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.025"} 1
...
```

크게 4가지 범주에 해당하는 여러 메트릭을 볼 수 있습니다.

- 런타임 메트릭
- 관리자 API 메트릭
- HTTP 미들웨어 메트릭
- 리버스 프록시 메트릭

### 런타임 메트릭

이 메트릭은 Caddy 프로세스의 내부를 다루며 Prometheus Go 클라이언트에서 자동으로 제공합니다. 이 메트릭에는 `go_*` 및 `process_*` 접두사가 붙습니다.

`process_*` 메트릭은 Linux 및 Windows에서만 수집됩니다.

[Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector), [Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector) 및 [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector)에 대한 문서를 참조하세요.

### 관리자 API 메트릭

Caddy 관리자 API를 모니터링하는 데 도움이 되는 메트릭입니다. 각 관리자 엔드포인트는 요청 수와 오류를 추적하도록 계측됩니다.

이러한 메트릭에는 `caddy_admin_*` 접두사가 붙습니다.

예를 들어:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

`admin.api.*` 네임스페이스의 모듈을 포함하여 관리자 엔드포인트에서 처리한 요청 수의 카운터입니다.

레이블 | 설명
-------|------------
`code` | HTTP 상태 코드
`handler` | 핸들러 또는 모듈 이름
`method` | HTTP 메서드
`path` | 관리자 엔드포인트가 마운트된 URL 경로

#### `caddy_admin_http_request_errors_total`

`admin.api.*` 네임스페이스의 모듈을 포함하여 관리자 엔드포인트에서 발생한 오류 수의 카운터입니다.

레이블 | 설명
-------|------------
`handler` | 핸들러 또는 모듈 이름
`method` | HTTP 메서드
`path` | 관리자 엔드포인트가 마운트된 URL 경로

### HTTP 미들웨어 메트릭

모든 Caddy HTTP 미들웨어 핸들러는 요청 지연 시간, 첫 번째 바이트까지의 시간(time-to-first-byte), 오류, 요청/응답 본문 크기를 확인하기 위해 자동으로 계측됩니다.

<aside class="tip">
	모든 미들웨어 핸들러가 계측되고 많은 요청이 여러 핸들러에 의해 처리되므로 모든 카운터를 단순히 함께 합산하지 마세요.
</aside>

아래 히스토그램 메트릭의 경우 현재 버킷을 구성할 수 없습니다.
지연 시간(duration)의 경우 기본 버킷 세트([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables))가 사용됩니다(5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s 및 10s).
크기의 경우 버킷은 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB 및 4MiB입니다.

#### `caddy_http_requests_in_flight`

현재 이 서버에서 처리 중인 요청 수의 게이지(gauge)입니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름

#### `caddy_http_request_errors_total`

요청을 처리하는 동안 발생한 미들웨어 오류의 카운터입니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름

#### `caddy_http_requests_total`

이루어진 HTTP(S) 요청의 카운터입니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름

#### `caddy_http_request_duration_seconds`

왕복 요청 지연 시간의 히스토그램입니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름
`code` | HTTP 상태 코드
`method` | HTTP 메서드

#### `caddy_http_request_size_bytes`

요청의 총 (예상) 크기 히스토그램입니다. 본문(body)을 포함합니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름
`code` | HTTP 상태 코드
`method` | HTTP 메서드

#### `caddy_http_response_size_bytes`

반환된 응답 본문 크기의 히스토그램입니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름
`code` | HTTP 상태 코드
`method` | HTTP 메서드

#### `caddy_http_response_duration_seconds`

응답의 첫 번째 바이트까지의 시간에 대한 히스토그램입니다.

레이블 | 설명
-------|------------
`server` | 서버 이름
`handler` | 핸들러 또는 모듈 이름
`code` | HTTP 상태 코드
`method` | HTTP 메서드

### 리버스 프록시 메트릭

#### `caddy_reverse_proxy_upstreams_healthy`

리버스 프록시 업스트림의 상태 게이지입니다.

값 `0`은 업스트림이 비정상임을 의미하고 `1`은 업스트림이 정상임을 의미합니다.

레이블 | 설명
-------|------------
`upstream` | 업스트림의 주소

## 샘플 쿼리

Prometheus에서 Caddy의 메트릭을 스크랩하게 되면 Caddy의 성능에 대한 몇 가지 흥미로운 메트릭을 볼 수 있습니다.

<aside class="tip">

위의 구성으로 Caddy를 스크랩하기 위해 Prometheus 서버를 시작했다면 [http://localhost:9090/graph](http://localhost:9090/graph)의 Prometheus UI에 다음 쿼리를 붙여넣어 보세요.

</aside>


예를 들어, 5분 동안 평균 초당 요청 속도를 보려면:

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

지연 시간 임계값 100ms를 초과하는 속도를 보려면:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

`file_server` 핸들러에서 95번째 백분위수(percentile) 요청 지연 시간을 찾으려면 다음과 같은 쿼리를 사용할 수 있습니다.

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

또는 `file_server` 핸들러에서 성공적인 `GET` 요청에 대한 메디안 응답 크기(바이트)를 보려면:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
