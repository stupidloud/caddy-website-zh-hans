---
title: redir (Caddyfile 지시어)
---

# redir

클라이언트에 HTTP 리다이렉트를 보냅니다.

이 지시어는 일치하는 요청을 그대로 거부하고 클라이언트가 다른 URL에서 다시 시도해야 함을 의미합니다. 이러한 이유로 [지시어 순서](/docs/caddyfile/directives#directive-order)가 매우 앞쪽에 배치됩니다.


## 구문 <a id="syntax"></a>

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** 는 대상 위치입니다. 응답의 [`Location` 헤더 <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location)가 됩니다.

- **&lt;code&gt;** 는 리다이렉트에 사용할 HTTP 상태 코드입니다. 다음이 될 수 있습니다:

	- `3xx` 범위의 양의 정수 또는 `401`
	
	- 일시적인 리다이렉트의 경우 `temporary` (`302`, 기본값)
	
	- 영구적인 리다이렉트의 경우 `permanent` (`301`)
	
	- HTML 문서를 사용하여 리다이렉트를 수행하는 경우 `html` (브라우저 리다이렉트에는 유용하지만 API 클라이언트에는 유용하지 않음)
	
	- 상태 코드 값이 있는 플레이스홀더



## 예제 <a id="examples"></a>

모든 요청을 `https://example.com`으로 리다이렉트합니다:

```caddy
www.example.com {
	redir https://example.com
}
```

동일하지만 [`{uri}` 플레이스홀더](/docs/caddyfile/concepts#placeholders)를 추가하여 기존 URI를 유지합니다:

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

동일하지만 영구적입니다:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

이전의 `/about-us` 페이지를 새 `/about` 페이지로 리다이렉트합니다:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
