---
title: error (Caddyfile 지시어)
---

# error

HTTP 핸들러 체인에서 오류를 발생시킵니다. 선택적으로 메시지와 권장 HTTP 상태 코드를 포함할 수 있습니다.

이 핸들러는 응답을 작성하지 않습니다. 대신, 사용자 정의 오류 처리 로직을 호출하기 위해 [`handle_errors`](handle_errors) 지시어와 함께 사용하도록 설계되었습니다.


## 구문

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** 는 작성할 HTTP 상태 코드입니다. 기본값은 `500`입니다.
- **&lt;message&gt;** 는 오류 메시지입니다. 기본값은 오류 메시지가 없는 것입니다.
- **message** 는 오류 메시지를 제공하는 또 다른 방법입니다. 메시지가 여러 줄인 경우 편리합니다.

명확히 하자면, 매처(matcher)가 아닌 첫 번째 인자는 3자리 상태 코드이거나 오류 메시지 문자열일 수 있습니다. 오류 메시지인 경우, 다음 인자가 상태 코드가 될 수 있습니다.


## 예시

특정 요청 경로에서 오류를 발생시키고, [`handle_errors`](handle_errors)를 사용하여 응답을 작성합니다:

```caddy
example.com {
	root /srv

	# 특정 경로에 대해 오류 발생
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # HTML 페이지를 제공하여 오류 처리
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
