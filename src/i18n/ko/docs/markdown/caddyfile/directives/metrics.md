---
title: metrics (Caddyfile 지시어)
---

# metrics

수집된 메트릭을 스크레이핑(scraping)할 수 있도록 노출하는 Prometheus 메트릭 노출 엔드포인트를 구성합니다. **먼저 [글로벌 옵션](/docs/caddyfile/options#metrics)에서 메트릭이 켜져 있어야 합니다.**

`/metrics` 엔드포인트는 [관리 API](/docs/api)에도 연결되어 있으며, 이는 구성할 수 없으며 관리 API가 비활성화된 경우에는 사용할 수 없습니다.

이 엔드포인트는 [Prometheus 노출 형식](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) 또는 협상된 경우 [OpenMetrics 노출 형식](https://pkg.go.dev/github.com/prometheus/client_golang@v1.9.0/prometheus/promhttp#HandlerOpts)(`application/openmetrics-text`)으로 메트릭을 반환합니다.

[메트릭으로 Caddy 모니터링하기](/docs/metrics)도 참조하십시오.

## 구문 <a id="syntax"></a>

```caddy-d
metrics [<matcher>] {
	disable_openmetrics
}
```

- **disable_openmetrics**는 OpenMetrics 협상을 비활성화합니다. 파싱 버그를 해결해야 하는 경우를 제외하고는 보통 필요하지 않습니다.

## 예제 <a id="examples"></a>

기본 `/metrics` 경로에서 메트릭을 노출합니다:

```caddy-d
metrics /metrics
```

다른 경로에서 메트릭을 노출합니다:

```caddy-d
metrics /foo/bar/baz
```

별도의 서브도메인에서 메트릭을 제공합니다:

```caddy
metrics.example.com {
	metrics
}
```

OpenMetrics 협상을 비활성화합니다:

```caddy-d
metrics /metrics {
	disable_openmetrics
}
```
