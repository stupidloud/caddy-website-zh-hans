---
title: respond (Caddyfile 지시어)
---

# respond

클라이언트에 하드코딩된 정적 응답을 작성합니다.

본문(body)이 비어 있지 않은 경우, 이 지시어는 `Content-Type` 헤더가 아직 설정되지 않았다면 이를 설정합니다. 기본값은 `text/plain; utf-8`이며, 본문이 유효한 JSON 객체 또는 배열인 경우에는 `application/json`으로 설정됩니다. 다른 모든 유형의 콘텐츠에 대해서는 [`header` 지시어](/docs/caddyfile/directives/header)를 사용하여 적절한 Content-Type을 명시적으로 설정하세요.


## 구문

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** 는 작성할 HTTP 상태 코드입니다.

  만약 `103` (Early Hints)이라면, 응답은 본문 없이 작성되며 핸들러 체인이 계속됩니다. (HTTP `1xx` 응답은 최종 응답이 아닌 정보 제공용입니다.)
  
  기본값: `200`

- **&lt;body&gt;** 는 작성할 응답 본문입니다.

- **body**는 본문을 제공하는 또 다른 방법입니다. 여러 줄일 경우 편리합니다.

- **close**는 응답을 작성한 후 클라이언트와 서버의 연결을 닫습니다.

명확히 하자면, 매처(matcher)가 아닌 첫 번째 인자는 3자리 상태 코드이거나 응답 본문 문자열일 수 있습니다. 만약 본문인 경우, 다음 인자가 상태 코드가 될 수 있습니다.

<aside class="tip">

오류 상태 코드로 응답하는 것은 핸들러 체인에서 오류를 반환하는 것과 다릅니다. 핸들러 체인에서 오류를 반환하면 내부적으로 오류 핸들러를 호출합니다.

</aside>


## 예시

모든 상태 체크에는 빈 본문과 함께 200 상태 코드를 작성하고, 그 외의 모든 요청에는 간단한 응답 본문을 작성합니다:

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

오류 응답을 작성하고 연결을 닫습니다:

<aside class="tip">

대신 [`error` 지시어](error)를 사용하는 것이 좋을 수도 있습니다. 이 지시어는 [`handle_errors` 지시어](handle_errors)로 처리할 수 있는 오류를 발생시킵니다.

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

[heredoc 구문](/docs/caddyfile/concepts#heredocs)을 사용하여 공백을 제어하고, 응답 본문에 맞게 `Content-Type` 헤더도 설정하면서 HTML 응답을 작성합니다:

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
