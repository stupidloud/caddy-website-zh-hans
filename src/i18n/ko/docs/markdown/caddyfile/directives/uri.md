---
title: uri (Caddyfile 지시어)
---

# uri

요청의 URI를 조작합니다. 경로 접두사/접미사를 제거하거나 전체 URI에서 하위 문자열을 대체할 수 있습니다.

이 지시어는 [`rewrite`](rewrite) 와는 다릅니다. `rewrite` 는 URI를 완전히 다른 것으로 재설정하는 반면, `uri` 는 URI를 *부분적으로* 변경합니다. `rewrite` 가 내부 리다이렉트로 특별하게 처리되는 반면, `uri` 는 단지 또 다른 미들웨어입니다.

## 구문 <a id="syntax"></a>

여러 가지 작업이 지원됩니다:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

첫 번째(매처가 아닌) 인자는 작업을 지정합니다:

- **strip_prefix** 는 경로에서 접두사를 제거합니다.

- **strip_suffix** 는 경로에서 접미사를 제거합니다.

- **replace** 는 전체 URI에서 하위 문자열 대체를 수행합니다.

	- **&lt;target&gt;** 은 접두사, 접미사 또는 검색 문자열/정규 표현식입니다. 접두사인 경우, 경로는 항상 슬래시로 시작하므로 선행 슬래시를 생략할 수 있습니다.

	- **&lt;replacement&gt;** 는 대체 문자열입니다. `$name` 이나 `${name}` 구문을 사용한 캡처 그룹이나 `$1` 과 같은 인덱스 번호 사용을 지원합니다. 자세한 내용은 [Go 문서](https://golang.org/pkg/regexp/#Regexp.Expand) 를 참조하십시오. 대체 값이 `""` 이면 일치하는 텍스트가 값에서 제거됩니다.

	- **&lt;limit&gt;** 는 최대 대체 횟수에 대한 선택적 제한입니다.

- **path_regexp** 는 URI의 경로 부분에 대해 정규 표현식 대체를 수행합니다.

	- **&lt;target&gt;** 은 접두사, 접미사 또는 검색 문자열/정규 표현식입니다. 접두사인 경우, 경로는 항상 슬래시로 시작하므로 선행 슬래시를 생략할 수 있습니다.

	- **&lt;replacement&gt;** 는 대체 문자열입니다. `$name` 이나 `${name}` 구문을 사용한 캡처 그룹이나 `$1` 과 같은 인덱스 번호 사용을 지원합니다. 자세한 내용은 [Go 문서](https://golang.org/pkg/regexp/#Regexp.Expand) 를 참조하십시오. 대체 값이 `""` 이면 일치하는 텍스트가 값에서 제거됩니다.

- **query** 는 URI 쿼리에 대한 조작을 수행하며, 모드는 매개변수 이름의 접두사나 인자의 수에 따라 달라집니다. 블록을 사용하여 여러 작업을 한 번에 지정할 수 있으며, rename 🡒 set 🡒 append 🡒 replace 🡒 delete 순서로 그룹화되어 수행됩니다.

	- 접두사가 없으면 매개변수가 쿼리에서 지정된 값으로 설정됩니다.
	
	  예를 들어, `uri query foo bar` 는 `foo` 매개변수의 값을 `bar` 로 설정합니다.

	- `-` 접두사를 붙이면 쿼리에서 매개변수를 제거합니다.
	
	  예를 들어, `uri query -foo` 는 쿼리에서 `foo` 매개변수를 삭제합니다.

	- `+` 접두사를 붙이면 지정된 값으로 쿼리에 매개변수를 추가합니다. 이는 동일한 이름의 기존 매개변수를 덮어쓰지 않습니다 (덮어쓰려면 `+` 를 생략하십시오).
	
	  예를 들어, `uri query +foo bar` 는 쿼리에 `foo=bar` 를 추가합니다.

	- 중간에 `>` 가 있는 매개변수는 매개변수 이름을 `>` 뒤의 값으로 변경합니다.
	
	  예를 들어, `uri query foo>bar` 는 `foo` 매개변수의 이름을 `bar` 로 변경합니다.

	- 세 개의 인자가 있는 경우, 쿼리 값 정규 표현식 대체가 수행됩니다. 여기서 첫 번째 인자는 쿼리 매개변수 이름, 두 번째는 검색 값, 세 번째는 대체 값입니다. 첫 번째 인자(매개변수 이름)는 모든 쿼리 매개변수에 대해 대체를 수행하기 위해 `*` 일 수 있습니다.
	
	  `$name` 이나 `${name}` 구문을 사용한 캡처 그룹이나 `$1` 과 같은 인덱스 번호 사용을 지원합니다. 자세한 내용은 [Go 문서](https://golang.org/pkg/regexp/#Regexp.Expand) 를 참조하십시오. 대체 값이 `""` 이면 일치하는 텍스트가 값에서 제거됩니다.
	
	  예를 들어, `uri query foo ^(ba)r $1z` 는 `foo` 매개변수의 값이 `bar` 로 시작하는 경우 그 값을 `baz` 로 대체합니다.

URI 변환은 URI의 정규화되거나 이스케이프가 해제된 형태에서 발생합니다. 그러나 접두사 또는 접미사 패턴에 이스케이프 시퀀스를 사용하여 요청 경로의 해당 위치에서 해당 리터럴 이스케이프만 일치시킬 수 있습니다. 예를 들어, `uri strip_prefix /a/b` 는 `/a/b/c` 와 `/a%2Fb/c` 를 모두 `/c` 로 재작성하고, `uri strip_prefix /a%2Fb` 는 `/a%2Fb/c` 를 `/c` 로 재작성하지만 `/a/b/c` 와는 일치하지 않습니다.

URI 경로는 수정되기 전에 디렉토리 탐색 점(..)이 제거됩니다. 또한 `<target>` 에도 여러 슬래시가 포함되어 있지 않은 한 여러 슬래시(예: `//`)는 하나로 합쳐집니다.

## 유사한 지시어 <a id="similar-directives"></a>

다른 지시어들도 요청 URI를 조작할 수 있습니다.

- [`rewrite`](rewrite) 는 값을 부분적으로 변경하는 대신 전체 경로와 쿼리를 새로운 값으로 변경합니다.

- [`handle_path`](handle_path) 는 [`handle`](handle) 과 동일하게 작동하지만, 핸들러를 실행하기 전에 요청에서 접두사를 제거합니다. 많은 경우 `uri strip_prefix` 대신 사용하여 설정 한 줄을 줄일 수 있습니다.

## 예제 <a id="examples"></a>

모든 요청 경로의 시작 부분에서 `/api` 를 제거합니다:

```caddy-d
uri strip_prefix /api
```

모든 요청 경로의 끝부분에서 `.php` 를 제거합니다:

```caddy-d
uri strip_suffix .php
```

모든 요청 URI에서 "/docs/" 를 "/v1/docs/" 로 대체합니다:

```caddy-d
uri replace /docs/ /v1/docs/
```

요청 경로(요청 쿼리 제외)에서 반복되는 모든 슬래시를 단일 슬래시로 합칩니다:

```caddy-d
uri path_regexp /{2,} /
```

`foo` 쿼리 매개변수의 값을 `bar` 로 설정합니다:

```caddy-d
uri query foo bar
```

쿼리에서 `foo` 매개변수를 제거합니다:

```caddy-d
uri query -foo
```

`foo` 쿼리 매개변수의 이름을 `bar` 로 변경합니다:

```caddy-d
uri query foo>bar
```

쿼리에 `bar` 매개변수를 추가합니다:

```caddy-d
uri query +foo bar
```

`foo` 쿼리 매개변수의 값이 `bar` 로 시작하는 경우 `baz` 로 대체합니다:

```caddy-d
uri query foo ^(ba)r $1z
```

여러 쿼리 작업을 한 번에 수행합니다:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
