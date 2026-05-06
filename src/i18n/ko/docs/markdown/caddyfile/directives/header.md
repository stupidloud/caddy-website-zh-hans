---
title: header (Caddyfile 지시어)
---

# header

HTTP 응답 헤더 필드를 조작합니다. 헤더 값을 설정(set), 추가(add), 삭제(delete)하거나 정규 표현식을 사용하여 교체(replace)할 수 있습니다.

기본적으로 헤더 조작은 헤더가 삭제되거나(`-` 접두사) 기본값이 설정되는 경우(`?` 접두사)를 제외하고 즉시 수행됩니다. 이러한 경우 헤더 조작은 클라이언트에 기록될 때까지 자동으로 연기됩니다.

HTTP 요청 헤더를 조작하려면 [`request_header`](request_header) 지시어를 사용할 수 있습니다.


## 구문 <a id="syntax"></a>

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# 추가 (Add)
	+<field> <value>

	# 설정 (Set)
	<field> <value>

	# 연기하여 설정 (Set with defer)
	><field> <value>

	# 삭제 (Delete)
	-<field>

	# 교체 (Replace)
	<field> <find> <replace>

	# 연기하여 교체 (Replace with defer)
	><field> <find> <replace>

	# 기본값 (Default)
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** 는 헤더 필드의 이름입니다.

  접두사가 없으면 필드가 설정(덮어쓰기)됩니다.

  `+` 접두사를 붙이면 필드가 이미 존재하더라도 덮어쓰지 않고 필드를 추가합니다. 헤더 필드는 응답에서 두 번 이상 나타날 수 있습니다.

  `-` 접두사를 붙이면 필드를 삭제합니다. 필드에 접두사나 접미사 `*` 와일드카드를 사용하여 일치하는 모든 필드를 삭제할 수 있습니다.

  `?` 접두사를 붙이면 필드의 기본값을 설정합니다. 필드가 아직 존재하지 않는 경우에만 기록됩니다.

  `>` 접두사를 붙이면 필드를 설정하고 단축형으로 `defer`를 활성화합니다.

- **&lt;value&gt;** 는 필드를 추가하거나 설정할 때의 헤더 필드 값입니다.

- **&lt;find&gt;** 는 검색할 정규 표현식입니다. 검색 패턴에 동적 입력을 위해 플레이스홀더를 사용할 수 있습니다. 사용되는 정규 표현식 언어는 Go에 포함된 RE2입니다. [RE2 구문 참조](https://github.com/google/re2/wiki/Syntax) 및 [Go 정규식 구문 개요](https://pkg.go.dev/regexp/syntax)를 확인하세요.

- **&lt;replace&gt;** 는 교체할 값입니다. 검색 및 교체를 수행하는 경우 필수입니다. 검색 패턴에서 캡처 그룹을 참조하려면 `$1` 또는 `$2` 등을 사용하세요. 교체 값이 `""`이면 매칭된 텍스트가 값에서 제거됩니다. 자세한 내용은 [Go 문서](https://golang.org/pkg/regexp/#Regexp.Expand)를 참조하세요.

- **defer** 는 응답이 클라이언트에 전송될 때까지 헤더 조작 실행을 연기합니다. 이 옵션은 다음 조건에서 자동으로 활성화됩니다:
	- `-`를 사용하여 헤더 필드를 삭제할 때.
	- `?`로 기본값을 설정할 때.
	- 설정 또는 교체 작업에 `>` 접두사를 사용할 때.
	- 하나 이상의 `match` 조건이 있을 때.

- **match** <span id="match"/> 는 인라인 [응답 매처(response matcher)](/docs/caddyfile/response-matchers)입니다. 헤더 조작은 지정된 조건을 충족하는 응답에만 적용됩니다.

여러 헤더 조작을 수행하려면 블록을 열고 동일한 방식으로 한 줄에 하나씩 조작을 지정할 수 있습니다.

`?` 접두사를 사용하여 기본 헤더 값을 설정할 때, 여러 헤더 조작이 포함된 `header` 블록 내에 있었다면 자동으로 자체 `header` 핸들러로 분리됩니다. [내부적으로](/docs/modules/http.handlers.headers#response/require), `?`를 사용하면 지시어의 전체 핸들러에 적용되는 [응답 매처](/docs/caddyfile/response-matchers)를 구성합니다. 이는 필드가 아직 설정되지 않은 경우에만 (`defer`와 같은) 헤더 조작을 적용합니다.


## 예제 <a id="examples"></a>

모든 응답에 커스텀 헤더 필드 설정:

```caddy-d
header Custom-Header "My value"
```

"Hidden" 헤더 필드 제거:

```caddy-d
header -Hidden
```

Location 헤더의 `http://`를 `https://`로 교체:

```caddy-d
header Location http:// https://
```

모든 페이지에 보안 및 개인정보 보호 헤더 설정: (**경고:** 영향을 충분히 이해한 경우에만 사용하세요!)

```caddy-d
header {
	# FLoC 추적 비활성화
	Permissions-Policy interest-cohort=()

	# HSTS 활성화
	Strict-Transport-Security max-age=31536000;

	# 클라이언트의 미디어 유형 탐색 비활성화
	X-Content-Type-Options nosniff

	# 클릭재킹 방지
	X-Frame-Options DENY
}
```

상호 배타적으로 의도된 여러 header 지시어:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

업스트림에서 정의하지 않은 경우 기본 캐시 만료 설정:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

GET 요청에 대한 모든 성공적인 응답을 최대 1시간 동안 캐시 가능으로 표시:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

업스트림 서버에서 예외가 발생한 경우 오류 응답의 캐싱 방지:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

업스트림 서버가 클라이언트 힌트(client hints)를 지원하는 경우 라이트 모드 응답을 다크 모드 응답과 별도로 캐시 가능하도록 표시:
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

와일드카드 값을 특정 도메인으로 교체하여 지나치게 허용적인 CORS 헤더 방지:
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**참고**: 교체 작업에서 `<find>` 값은 정규 표현식으로 해석됩니다. `*` 문자를 매칭하려면 위 예제와 같이 백슬래시로 이스케이프해야 합니다.

또는, [응답 매처](/docs/caddyfile/response-matchers)를 사용하여 헤더 값을 문자 그대로 매칭할 수 있습니다:
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

`/no-cache`로 시작하는 경로에 대해 프록시 업스트림이 설정한 캐시 만료를 덮어쓰기 위해, 프록시가 헤더를 쓴 *after*에 헤더가 설정되도록 `defer`를 활성화하는 것이 필요합니다:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

`Set-Cookie` 헤더를 연기하여 업데이트하고 `SameSite=None`을 추가하기 위해; 정규식 캡처를 사용하여 기존 값을 가져오고, `$1`을 사용하여 추가 옵션과 함께 시작 부분에 다시 삽입합니다:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
