---
title: handle_errors (Caddyfile 지시어)
---

# handle_errors

에러 핸들러를 설정합니다.

일반적인 HTTP 요청 핸들러가 에러를 반환하면, 일반적인 처리가 중단되고 에러 핸들러가 호출됩니다. 에러 핸들러는 일반 라우트와 똑같은 라우트를 형성하며, 일반 라우트가 할 수 있는 모든 것을 할 수 있습니다. 이를 통해 HTTP 요청 처리 중 발생하는 에러를 다룰 때 뛰어난 제어력과 유연성을 얻을 수 있습니다. 예를 들어, 정적 에러 페이지나 템플릿 에러 페이지를 제공하거나, 에러 처리를 위해 다른 백엔드로 리버스 프록시를 수행할 수 있습니다.

이 지시어는 서로 다른 에러 코드를 다르게 처리하기 위해 여러 번 반복될 수 있습니다. 상태 코드가 지정되지 않으면 모든 에러와 일치하며, 다른 에러 핸들러가 일치하지 않을 때 폴백(fallback)으로 작동합니다.

요청 컨텍스트는 에러 라우트로 전달되므로, [사이트 루트(root)](root)나 [변수(vars)](vars)와 같이 요청 컨텍스트에 설정된 모든 값은 에러 핸들러에서도 유지됩니다. 또한 에러 처리 시 [새로운 플레이스홀더](#placeholders)를 사용할 수 있습니다.

특정 지시어(예: 에러로 분류되는 HTTP 상태와 함께 응답을 작성할 수 있는 [`reverse_proxy`](reverse_proxy))는 에러 라우트를 트리거하지 *않음*에 유의하세요.

사용자 정의 라우팅 결정에 따라 명시적으로 에러를 발생시키려면 [`error`](error) 지시어를 사용할 수 있습니다.


## 구문 <a id="syntax"></a>

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** 는 처리 중인 에러와 매칭할 하나 이상의 HTTP 상태 코드입니다. 상태 코드는 3자리 숫자일 수도 있고, 각각 400-499 또는 500-599 범위의 모든 상태 코드와 일치하는 `4xx` 또는 `5xx`와 같은 특수 케이스일 수도 있습니다. 상태 코드가 지정되지 않으면 모든 에러와 일치하며, 다른 에러 핸들러가 일치하지 않을 때 폴백으로 작동합니다.

- **<directives...>** 는 한 줄에 하나씩 나열된 HTTP 핸들러 [지시어](/docs/caddyfile/directives) 및 [매처](/docs/caddyfile/matchers) 목록입니다.


## 플레이스홀더 <a id="placeholders"></a>

에러 처리 중에 다음 플레이스홀더를 사용할 수 있습니다. 이들은 [HTTP 서버의 에러 라우트에 대한 JSON 문서](/docs/json/apps/http/servers/errors/#routes)에서 찾을 수 있는 전체 플레이스홀더에 대한 [Caddyfile 축약형](/docs/caddyfile/concepts#placeholders)입니다.

| 플레이스홀더 | 설명 |
|---|---|
| `{err.status_code}` | 권장되는 HTTP 상태 코드 |
| `{err.status_text}` | 권장되는 상태 코드와 관련된 상태 텍스트 |
| `{err.message}` | 에러 메시지 |
| `{err.trace}` | 에러의 원인 |
| `{err.id}` | 이 에러 발생에 대한 식별자 |


## 예시 <a id="examples"></a>

상태 코드에 기반한 사용자 정의 에러 페이지(예: `404` 에러의 경우 `404.html`이라는 페이지). `handle_errors`에서 실행될 때 [`file_server`](file_server)는 에러의 HTTP 상태 코드를 유지함에 유의하세요(사이트에 [사이트 루트(root)](root)를 미리 설정했다고 가정함):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

사용자 정의 에러 메시지를 작성하기 위해 [`templates`](templates)를 사용하는 단일 에러 페이지:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

일부 에러 코드에 대해서만 사용자 정의 에러 페이지를 제공하고 싶다면, [`file`](/docs/caddyfile/matchers#file) 매처를 사용하여 사용자 정의 에러 파일의 존재 여부를 미리 확인할 수 있습니다:

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

HTTP 에러를 처리하고 여러분의 하루를 개선하는 데 고도로 숙련된 전문 서버로 리버스 프록시 😸:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

간단히 [`respond`](respond)를 사용하여 에러 코드와 이름을 반환합니다:

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

특정 에러 코드를 다르게 처리하려면:

```caddy-d
handle_errors 404 410 {
	respond "It's a 404 or 410 error!"
}

handle_errors 5xx {
	respond "It's a 5xx error."
}

handle_errors {
	respond "It's another error"
}
```

위의 동작은 상태 코드에 대해 [`expression`](/docs/caddyfile/matchers#expression) 매처를 사용하고 상호 배타성을 위해 [`handle`](handle)을 사용하는 아래와 동일합니다:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "It's a 404 or 410 error!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "It's a 5xx error."
	}

	handle {
		respond "It's another error"
	}
}
```
