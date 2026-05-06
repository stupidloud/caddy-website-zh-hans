---
title: vars (Caddyfile 지시어)
---

# vars

하나 이상의 변수를 특정 값으로 설정하여 나중에 요청 처리 체인에서 사용할 수 있도록 합니다.

변수에 접근하는 주요 방법은 `{vars.variable_name}` 형식의 자리 표시자를 사용하거나, [`vars`](/docs/caddyfile/matchers#vars) 및 [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp) 요청 매처를 사용하는 것입니다.

[`templates`](templates) 지시어에서 `placeholder` 함수를 사용하여 변수를 사용할 수도 있습니다. 예를 들면 다음과 같습니다: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

특별한 경우로, 리플레이서(replacer)에 저장된 `http.auth.user.id` 라는 이름의 변수를 덮어써서 [액세스 로그(log)](log)의 `user_id` 필드를 업데이트할 수 있습니다.

## 구문 <a id="syntax"></a>

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** 은 설정할 변수 이름입니다.

- **&lt;value&gt;** 는 변수의 값입니다.

  가능한 경우 값이 타입 변환됩니다. `true` 와 `false` 는 불리언(boolean) 타입으로 변환되고, 숫자 값은 그에 따라 정수 또는 부동 소수점으로 변환됩니다. 이러한 변환을 피하고 문자열로 유지하려면 [따옴표](/docs/caddyfile/concepts#tokens-and-quotes) 로 묶을 수 있습니다.

## 예제 <a id="examples"></a>

요청 경로에 따라 조건부로 값을 갖는 단일 변수를 설정한 다음, 그 값으로 응답하는 예제:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

여러 변수를 설정하며, 각각 적절한 스칼라(scalar) 타입으로 변환되는 예제:

```caddy-d
vars {
	# 불리언
	abc true

	# 정수
	def 1

	# 부동 소수점
	ghi 2.3

	# 문자열
	jkl "example"
}
```
