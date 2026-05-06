---
title: log_append (Caddyfile 지시어)
---

# log_append

현재 요청의 액세스 로그에 필드를 추가합니다.

이 지시어는 먼저 액세스 로깅을 활성화하기 위해 필요한 [`log` 지시어](log)와 함께 사용해야 합니다.

값은 정적 문자열이거나, 요청 시점에 해당 값으로 대체되는 [플레이스홀더](/docs/caddyfile/concepts#placeholders)일 수 있습니다.


## 구문

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

기본적으로 로그 필드는 모든 후속 핸들러(예: 응답을 작성하는 [`reverse_proxy`](reverse_proxy), [`respond`](respond), [`file_server`](file_server) 등)가 완료된 후, 미들웨어 체인을 다시 거슬러 올라가는 도중(즉, "지연(late)")에 추가되므로 요청과 응답의 최종 상태를 캡처합니다.

키의 접두사로 `<` 를 사용하면 "조기(early)"로 표시됩니다. 이는 체인의 다음 핸들러를 호출하기 *전에* 로그 필드가 로그에 추가됨을 의미하므로, 후속 핸들러에 의해 수정되기 전의 요청을 읽을 수 있습니다.

디버깅 목적으로만(프로덕션용 아님), 값이 `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}`, `{http.response.body_base64}` 중 하나인 경우 핸들러가 특수 처리를 수행합니다. 요청 본문 플레이스홀더를 사용하면 "조기(early)" 모드가 암시적으로 활성화되고 요청 본문이 버퍼링됩니다. 응답 본문 플레이스홀더를 사용하면 응답 본문을 캡처하기 위해 응답 버퍼링이 활성화되며, 응답이 작성될 때 로그 필드가 "지연(late)"으로 추가됩니다.


## 예시

로그에 사이트에서 요청이 처리되는 영역을 `static` 또는 `dynamic`으로 표시합니다:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

로그에 실제로 사용된 역방향 프록시 업스트림(`node1`, `node2` 또는 `node3`)과 업스트림으로 프록시하는 데 걸린 시간(밀리초), 그리고 프록시 업스트림이 응답 헤더를 작성하는 데 걸린 시간을 표시합니다:

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

키 앞에 `<` 를 붙여 로그 필드를 "조기(early)"로 추가할 수 있습니다. 이를 통해 후속 핸들러에 의해 수정되기 전의 요청 상태를 캡처할 수 있습니다. 예를 들어, 재작성(rewrite)되기 전의 원래 요청 경로를 로깅하려면 다음과 같이 합니다(원래 요청 경로는 어차피 로깅되지만, 설명을 위한 예시입니다):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

디버깅 목적으로 요청 및 응답 본문을 로그에 추가합니다(성능을 저하시키고 로그를 매우 복잡하게 만들므로 프로덕션에서는 사용하지 마세요). 본문에 출력할 수 없는 문자가 포함된 바이너리 데이터가 포함될 것으로 예상되는 경우, 대신 베이스64(base64) 변형 플레이스홀더(예: `{http.request.body_base64}` 및 `{http.response.body_base64}`)를 사용하면 복사 및 검사가 더 쉬워집니다:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
