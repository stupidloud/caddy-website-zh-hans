---
title: abort (Caddyfile 지시어)
---

# abort

HTTP 핸들러 체인을 즉시 중단하고 연결을 닫아 클라이언트에 대한 모든 응답을 방지합니다. 동일한 연결에서 동시에 활성화된 다른 HTTP 스트림도 중단됩니다.


## 구문

```caddy-d
abort [<matcher>]
```

## 예시

와일드카드 인증서를 사용할 때 알 수 없는 도메인으로 들어오는 연결을 강제로 닫습니다:

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# 처리되지 않은 도메인은 여기로 넘어오지만,
		# 이러한 요청을 수락하고 싶지 않습니다.
        abort
    }
}
```
