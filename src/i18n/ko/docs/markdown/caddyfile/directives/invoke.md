---
title: invoke (Caddyfile 지시어)
---

# invoke

*⚠️ 실험적 기능*

[명명된 경로](/docs/caddyfile/concepts#named-routes)를 호출합니다.

이는 고유한 인메모리 상태를 가진 HTTP 핸들러 지시어와 함께 사용하거나, 로드 시 프로비저닝 비용이 많이 드는 경우 유용합니다. 수백 개 이상의 사이트가 있는 경우, 명명된 경로를 호출하면 메모리 사용량을 줄이는 데 도움이 될 수 있습니다.

<aside class="tip">

[`import`](/docs/caddyfile/directives/import)와 달리 `invoke`는 인자를 지원하지 않지만, [`vars`](/docs/caddyfile/directives/vars)를 사용하여 명명된 경로 내에서 사용할 변수를 정의할 수 있습니다.

</aside>

## 구문

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** 은 호출할 이전에 정의된 경로의 이름입니다. 경로를 찾을 수 없으면 오류가 발생합니다.


## 예시

여러 사이트에서 재사용할 수 있는 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)가 포함된 [명명된 경로](/docs/caddyfile/concepts#named-routes)를 정의합니다. 모든 사이트에 대해 동일한 인메모리 부하 분산 상태가 재사용됩니다.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Apex 도메인은 /app 하위 경로를 통해 앱에 액세스하고
# 그 외의 경우 메인 사이트에 액세스할 수 있도록 허용합니다.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# 하위 도메인을 통해서도 앱에 액세스할 수 있습니다.
app.example.com {
	invoke app-proxy
}
```
