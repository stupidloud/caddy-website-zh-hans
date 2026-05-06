---
title: 요청 매처 (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

# 요청 매처

요청 매처(Request matchers)는 다양한 기준에 따라 요청을 필터링(또는 분류)하는 데 사용됩니다.

- [구문](#syntax)
	- [예시](#examples)
	- [와일드카드 매처](#wildcard-matchers)
	- [경로 매처](#path-matchers)
	- [명명된 매처](#named-matchers)
- [표준 매처](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


## 구문 <a id="syntax"></a>

Caddyfile에서 지시어 바로 뒤에 오는 **매처 토큰**은 해당 지시어의 범위를 제한할 수 있습니다. 매처 토큰은 다음 형식 중 하나일 수 있습니다:

1. [**`*`**](#wildcard-matchers): 모든 요청과 일치 (와일드카드, 기본값).
2. [**`/path`**](#path-matchers): 슬래시로 시작하며 요청 경로와 일치.
3. [**`@name`**](#named-matchers): *명명된 매처*를 지정.

지시어가 매처를 지원하는 경우, 구문 문서에서 `[<matcher>]`로 표시됩니다. 매처 토큰은 [보통 선택 사항](/docs/caddyfile/directives#syntax)이며 `[ ]`로 표시됩니다. 매처 토큰을 생략하면 와일드카드 매처(`*`)와 동일합니다.


#### 예시 <a id="examples"></a>

이 지시어는 [모든](#wildcard-matchers) HTTP 요청에 적용됩니다:

```caddy-d
reverse_proxy localhost:9000
```

다음도 동일합니다 (`*`는 여기서 불필요함):

```caddy-d
reverse_proxy * localhost:9000
```

하지만 이 지시어는 `/api/`로 시작하는 [경로](#path-matchers)를 가진 요청에만 적용됩니다:

```caddy-d
reverse_proxy /api/* localhost:9000
```

경로 이외의 다른 것으로 매칭하려면 [명명된 매처](#named-matchers)를 정의하고 `@name`을 사용하여 참조하세요:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




### 와일드카드 매처 <a id="wildcard-matchers"></a>

와일드카드(또는 "catch-all") 매처 `*`는 모든 요청과 일치하며, 매처 토큰이 반드시 필요한 경우에만 쓰입니다. 예를 들어, 지시어에 전달하려는 첫 번째 인수가 우연히 경로와 같다면, 그것은 경로 매처처럼 보일 것입니다! 이럴 때 와일드카드 매처를 사용하여 모호함을 해결할 수 있습니다. 예:

```caddy-d
root * /home/www/mysite
```

그 외의 경우 이 매처는 자주 사용되지 않습니다. 구문상 필수적이지 않다면 생략하는 것을 권장합니다.


### 경로 매처 <a id="path-matchers"></a>

URI 경로로 매칭하는 것은 요청을 매칭하는 가장 일반적인 방법이므로, 다음과 같이 인라인으로 사용할 수 있습니다:

```caddy-d
redir /old.html /new.html
```

경로 매처 토큰은 반드시 슬래시 `/`로 시작해야 합니다.

**[경로 매칭](#path)은 기본적으로 접두사 매칭이 아닌 정확히 일치(exact match)입니다.** 빠른 접두사 매칭을 위해서는 끝에 `*`를 붙여야 합니다. `/foo*`는 `/foo`, `/foo/` 뿐만 아니라 `/foobar`와도 일치한다는 점에 유의하세요. 실제로는 `/foo/*`를 원할 수도 있습니다.


### 명명된 매처 <a id="named-matchers"></a>

경로 매처나 와일드카드 매처가 아닌 모든 매처는 명명된 매처여야 합니다. 이것은 특정 지시어 외부에서 정의되며 재사용할 수 있는 매처입니다.

고유한 이름을 가진 매처를 정의하면 [사용 가능한 모든 매처](#standard-matchers)를 하나의 세트로 결합할 수 있어 더 유연하게 사용할 수 있습니다:

```caddy-d
@name {
	...
}
```

세트에 매처가 하나만 있는 경우 다음과 같이 한 줄에 작성할 수도 있습니다:

```caddy-d
@name ...
```

그런 다음 지시어의 첫 번째 인수로 지정하여 매처를 사용할 수 있습니다:

```caddy-d
directive @name
```

예를 들어, 다음은 HTTP/1.1 웹소켓 요청을 `localhost:6001`로 프록시하고, 다른 요청은 `localhost:8080`으로 프록시합니다. `Connection` 헤더 필드에 `Upgrade`가 *포함되어 있고*, **동시에** `Upgrade` 필드 값이 정확히 `websocket`인 요청과 일치합니다:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

매처 세트가 단 하나의 매처로 구성된 경우 한 줄 구문도 작동합니다:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

특수의 경우로, [`expression` 매처](#expression)는 매처 이름 뒤에 하나의 [따옴표로 감싸진](/docs/caddyfile/concepts#tokens-and-quotes) 인수(CEL 표현식 자체)가 오면 매처 이름을 생략하고 사용할 수 있습니다:

```caddy-d
@not-found `{err.status_code} == 404`
```

지시어와 마찬가지로, 명명된 매처 정의는 해당 매처를 사용하는 [사이트 블록](/docs/caddyfile/concepts#structure) 내부에 있어야 합니다.

명명된 매처 정의는 *매처 세트(matcher set)*를 구성합니다. 세트 내의 매처들은 AND로 결합됩니다. 즉, 모든 매처가 일치해야 합니다. 예를 들어, 세트에 [`header`](#header)와 [`path`](#path) 매처가 모두 있으면 둘 다 일치해야 합니다.

동일한 유형의 여러 매처는 아래 섹션에서 설명하는 부울 대수(AND/OR)를 사용하여 병합될 수 있습니다 (예: 동일한 세트 내의 여러 [`path`](#path) 매처).

더 복잡한 부울 매칭 로직의 경우, **and** `&&`, **or** `||`, **괄호** `( )`를 지원하는 CEL 표현식을 작성할 수 있는 [`expression` 매처](#expression)를 사용하는 것이 좋습니다.





## 표준 매처 <a id="standard-matchers"></a>

전체 매처 문서는 [각 매처 모듈의 문서](/docs/json/apps/http/servers/routes/match/)에서 찾을 수 있습니다.

요청은 다음과 같은 방식으로 매칭될 수 있습니다:



### client_ip <a id="client-ip"></a>

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

클라이언트 IP 주소로 매칭합니다. 정확한 IP나 CIDR 범위를 허용합니다. IPv6 존(zones)이 지원됩니다.

이 매처는 [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) 전역 옵션이 구성되었을 때 사용하는 것이 가장 좋으며, 그렇지 않으면 [`remote_ip`](#remote-ip) 매처와 동일하게 동작합니다. 신뢰할 수 있는 프록시의 요청만 요청 시작 시 클라이언트 IP가 파싱됩니다. 신뢰할 수 없는 요청은 직전 피어의 원격 IP 주소나 [PROXY 프로토콜](/docs/caddyfile/options#proxy-protocol)을 통해 설정된 주소를 사용합니다.

축약형으로, `private_ranges`를 사용하여 모든 사설 IPv4 및 IPv6 범위를 매칭할 수 있습니다. 이는 `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1` 범위를 모두 지정하는 것과 같습니다.

명명된 매처당 여러 개의 `client_ip` 매처가 있을 수 있으며, 해당 범위는 병합되어 OR로 결합됩니다.

#### 예시:

사설 IPv4 주소의 요청과 일치:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

이 매처는 매칭을 반전시키기 위해 [`not`](#not) 매처와 자주 함께 쓰입니다. 예를 들어, 모든 사설 범의의 반대인 *공개* IPv4 및 IPv6 주소의 모든 연결을 중단하려면 다음과 같이 합니다:

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "안녕하세요, 사설 네트워크에서 오셨군요!"
}
```

[CEL 표현식](#expression)에서는 다음과 같습니다:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

`true` 또는 `false`를 반환하는 임의의 [CEL (Common Expression Language)](https://github.com/google/cel-spec) 표현식으로 매칭합니다.

대부분의 다른 요청 매처는 표현식 내에서 함수로 사용될 수 있으며, 이는 표현식 외부보다 부울 로직에 대해 더 많은 유연성을 제공합니다. CEL 표현식 내에서 지원되는 구문은 각 매처의 문서를 참조하세요.

Caddy [플레이스홀더](/docs/conventions#placeholders) (또는 [Caddyfile 축약형](/docs/caddyfile/concepts#placeholders))는 CEL 환경에서 해석되기 전에 전처리되어 일반 CEL 함수 호출로 변환되므로 이러한 CEL 표현식에서 사용할 수 있습니다. 플레이스홀더가 매처 함수의 문자열 인수로 전달되어야 하는 경우, 전처리를 방지하기 위해 맨 앞의 `{`를 백슬래시 `\`로 이스케이프해야 합니다. 예: `file('\{path}.md')`.

편의상, CEL 표현식으로만 구성된 명명된 매처를 정의할 때 매처 이름을 생략할 수 있습니다. CEL 표현식은 [따옴표로 감싸야](/docs/caddyfile/concepts#tokens-and-quotes) 합니다 (백틱이나 히어독 권장). 다음과 같이 가독성이 좋아집니다:

```caddy-d
@mutable `{method}.startsWith("P")`
```

이 경우 CEL 매처로 간주됩니다.

#### 예시:

메서드가 `P`로 시작하는 요청(예: `PUT` 또는 `POST`)과 일치:

```caddy-d
@methods expression {method}.startsWith("P")
```

핸들러가 에러 상태 코드 `404`를 반환한 요청과 일치하며, [`handle_errors` 지시어](/docs/caddyfile/directives/handle_errors)와 함께 사용됩니다:

```caddy-d
@404 expression {err.status_code} == 404
```

경로가 두 개의 서로 다른 정규 표현식 중 하나와 일치하는 요청과 일치: [`path_regexp`](#path-regexp) 매처는 일반적으로 명명된 매처당 한 번만 존재할 수 있으므로, 이는 표현식을 통해서만 가능합니다.

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

또는 매처 이름을 생략하고 단일 토큰으로 파싱되도록 [백틱](/docs/caddyfile/concepts#tokens-and-quotes)으로 감싸는 방식입니다:

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

[히어독 구문](/docs/caddyfile/concepts#heredocs)을 사용하여 여러 줄의 CEL 표현식을 작성할 수 있습니다:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

파일로 매칭합니다.

- `root`는 파일을 찾을 디렉토리를 정의합니다. 기본값은 현재 작업 디렉토리이거나, 설정된 경우 `root` [변수](/docs/modules/http.handlers.vars) (`{http.vars.root}`)입니다 ([`root` 지시어](/docs/caddyfile/directives/root)를 통해 설정 가능).

- `try_files`는 목록의 파일 중 try_policy와 일치하는 파일을 확인합니다.

  디렉토리를 매칭하려면 경로 끝에 슬래시 `/`를 추가하세요. 모든 파일 경로는 사이트 [루트](/docs/caddyfile/directives/root)에 상대적이며, [와일드카드 패턴(glob patterns)](https://pkg.go.dev/path/filepath#Match)이 확장됩니다.

  `try_policy`가 `first_exist`(기본값)인 경우, 목록의 마지막 항목은 `=`가 붙은 숫자(예: `=404`)일 수 있으며, 이는 폴백으로서 해당 코드로 에러를 발생시킵니다. 이 에러는 [`handle_errors`](/docs/caddyfile/directives/handle_errors)로 포착하여 처리할 수 있습니다.

- `try_policy`는 파일을 선택하는 방법을 지정합니다. 기본값은 `first_exist`입니다.

	- `first_exist`: 파일 존재 여부를 확인합니다. 존재하는 첫 번째 파일이 선택됩니다.

	- `first_exist_fallback`: `first_exist`와 유사하지만, 디스크 접근을 방지하기 위해 목록의 마지막 요소가 항상 존재한다고 가정합니다.

	- `smallest_size`: 크기가 가장 작은 파일을 선택합니다.

	- `largest_size`: 크기가 가장 큰 파일을 선택합니다.

	- `most_recently_modified`: 가장 최근에 수정된 파일을 선택합니다.

- `split_path`는 시도할 각 파일 경로에서 발견되는 목록의 첫 번째 구분자(delimiter)를 기준으로 경로를 분할합니다. 분할된 각 값에 대해 구분자 자체를 포함한 왼쪽 부분이 시도되는 파일 경로가 됩니다. 예를 들어, 구분자로 `.php`를 사용하는 `/remote.php/dav/`는 파일 `/remote.php`를 시도합니다. 각 구분자는 분할 구분자로 사용되기 위해 URI 경로 구성 요소의 끝에 나타나야 합니다. 이는 틈새 설정이며 주로 PHP 사이트를 서비스할 때 사용됩니다.

`first_exist` 정책을 사용하는 `try_files`가 매우 일반적이기 때문에, 다음과 같이 한 줄 축약형이 있습니다:

```caddy-d
file <files...>
```

빈 `file` 매처(뒤에 파일이 나열되지 않은 매처)는 요청된 파일(URI 그대로, [사이트 루트](/docs/caddyfile/directives/root)에 상대적인 파일)이 존재하는지 확인합니다. 이는 실질적으로 `file {path}`와 동일합니다.


<aside class="tip">

디스크에 파일이 존재하는지 여부에 따라 재작성하는 작업이 매우 흔하기 때문에, `file` 매처와 [`rewrite` 핸들러](/docs/caddyfile/directives/rewrite)의 축약형인 [`try_files` 지시어](/docs/caddyfile/directives/try_files)도 있습니다.

</aside>


매칭이 성공하면 네 개의 새로운 플레이스홀더를 사용할 수 있게 됩니다:

- `{file_match.relative}`: 파일의 루트 상대 경로. 요청을 재작성할 때 종종 유용합니다.
- `{file_match.absolute}`: 루트를 포함한 매칭된 파일의 절대 경로.
- `{file_match.type}`: 파일 유형, `file` 또는 `directory`.
- `{file_match.remainder}`: 파일 경로를 분할한 후 남은 부분 (`split_path`가 구성된 경우).


#### 예시:

경로가 존재하는 파일인 요청과 일치:

```caddy-d
@file file
```

경로 뒤에 `.html`이 붙은 파일이 존재하거나, 그렇지 않으면 경로 자체가 파일로 존재하는 요청과 일치:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

위와 동일하지만 한 줄 축약형을 사용하고, 파일을 찾지 못한 경우 404 에러를 발생시킴:

```caddy-d
@html-or-error file {path}.html {path} =404
```

[CEL 표현식](#expression)을 사용한 몇 가지 예시입니다. 플레이스홀더는 CEL 환경에서 해석되기 전에 전처리되어 일반 CEL 함수 호출로 변환되므로 여기서 연결(concatenation)이 사용됩니다. 또한 현재 파싱 제한으로 인해 플레이스홀더와 연결할 때는 긴 형식을 사용해야 합니다:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

요청 헤더 필드로 매칭합니다.

- `<field>`는 확인할 HTTP 헤더 필드의 이름입니다.
	- `!`로 시작하면 필드가 존재하지 않아야 일치합니다 (값 인수는 생략).
- `<value>`는 일치하기 위해 필드가 가져야 하는 값입니다. 하나 이상 지정할 수 있습니다.
	- `*`로 시작하면 빠른 접두사 일치를 수행합니다 (값의 끝에 나타남).
	- `*`로 끝나면 빠른 접미사 일치를 수행합니다 (값의 시작에 나타남).
	- `*`로 감싸면 빠른 부분 문자열 일치를 수행합니다 (값의 어느 곳에나 나타남).
	- 그렇지 않으면 빠른 정확한 일치입니다.

동일한 세트 내의 서로 다른 헤더 필드는 AND로 결합됩니다. 필드당 여러 값은 OR로 결합됩니다.

헤더 필드는 반복될 수 있으며 서로 다른 값을 가질 수 있습니다. 백엔드 애플리케이션은 헤더 필드 값이 단일 값이 아닌 배열임을 고려해야 하며, Caddy는 이러한 문제에 대해 의미 해석을 하지 않습니다.

#### 예시:

`Connection` 헤더에 `Upgrade`가 포함된 요청과 일치:

```caddy-d
@upgrade header Connection *Upgrade*
```

`Foo` 헤더가 `bar` 또는 `baz`를 포함하는 요청과 일치:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

`Foo` 헤더 필드가 아예 없는 요청과 일치:

```caddy-d
@not_foo header !Foo
```

[CEL 표현식](#expression)을 사용하여, `Connection` 헤더가 `Upgrade`를 포함하고 `Upgrade` 헤더가 `websocket`과 일치하는지 확인하여 웹소켓 요청과 일치 (HTTP/2는 이를 위해 `:protocol` 헤더를 가짐):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
### header_regexp <a id="header-regexp"></a>

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

[`header`](#header)와 유사하지만 정규 표현식을 지원합니다.

사용되는 정규 표현식 언어는 Go에 포함된 RE2입니다. [RE2 구문 참조](https://github.com/google/re2/wiki/Syntax) 및 [Go 정규식 구문 개요](https://pkg.go.dev/regexp/syntax)를 참조하세요.

v2.8.0부터 `name`이 제공되지 않으면 명명된 매처의 이름에서 이름을 가져옵니다. 예를 들어 명명된 매처 `@foo`는 이 매처의 이름을 `foo`로 만듭니다. 이름을 지정할 때의 주된 장점은 동일한 명명된 매처에서 두 개 이상의 정규식 매처(예: `header_regexp` 및 [`path_regexp`](#path-regexp), 또는 여러 다른 헤더 필드)가 사용되는 경우입니다.

캡처 그룹은 매칭 후 지시어에서 [플레이스홀더](/docs/caddyfile/concepts#placeholders)를 통해 접근할 수 있습니다:
- `{re.<name>.<capture_group>}` 여기서:
  - `<name>`은 정규 표현식의 이름입니다.
  - `<capture_group>`은 표현식 내 캡처 그룹의 이름 또는 번호입니다.

- 편의를 위해 이름이 없는 `{re.<capture_group>}`도 채워집니다. 주의할 점은 여러 정규식 매처가 순차적으로 사용되면 플레이스홀더 값이 다음 매처에 의해 덮어씌워진다는 것입니다.

캡처 그룹 `0`은 전체 정규식 매치, `1`은 첫 번째 캡처 그룹, `2`는 두 번째 캡처 그룹 등입니다. 따라서 `{re.foo.1}` 또는 `{re.1}`은 모두 첫 번째 캡처 그룹의 값을 가집니다.

정규식 패턴은 병합될 수 없으므로 헤더 필드당 하나의 정규 표현식만 지원됩니다. 더 많이 필요한 경우 [`expression` 매처](#expression)를 사용하는 것이 좋습니다. 여러 다른 헤더 필드에 대한 매치는 AND로 결합됩니다.

#### 예시:

`Cookie` 헤더에 `login_` 뒤에 16진수 문자열이 포함된 요청과 일치하며, 캡처 그룹은 `{re.login.1}` 또는 `{re.1}`로 접근할 수 있습니다.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

명명된 매처에서 이름을 추론하도록 이름을 생략하여 단순화할 수 있습니다:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

또는 [CEL 표현식](#expression)을 사용하는 경우:

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

요청의 `Host` 헤더 필드로 요청을 매칭합니다.

대부분의 사이트 블록은 이미 사이트 주소에 호스트를 나타내므로, 이 매처는 와일드카드 호스트 이름을 사용하는 사이트 블록에서 호스트 이름별 로직이 필요한 경우에 더 흔히 쓰입니다 (와일드카드 인증서 패턴 참조).

여러 개의 `host` 매처는 OR로 결합됩니다.

#### 예시:

하나의 서브도메인 매칭:

```caddy-d
@sub host sub.example.com
```

에이펙스(apex) 도메인과 서브도메인 매칭:

```caddy-d
@site host example.com www.example.com
```

[CEL 표현식](#expression)을 사용하여 여러 서브도메인 매칭:

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

HTTP 요청의 메서드(동사)로 매칭합니다. 메서드는 `POST`와 같이 대문자여야 합니다. 하나 또는 여러 개의 메서드를 매칭할 수 있습니다.

여러 개의 `method` 매처는 OR로 결합됩니다.

#### 예시:

`GET` 메서드 요청과 일치:

```caddy-d
@get method GET
```

`PUT` 또는 `DELETE` 메서드 요청과 일치:

```caddy-d
@put-delete method PUT DELETE
```

[CEL 표현식](#expression)을 사용하여 읽기 전용 메서드 매칭:

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

```caddy-d
not <matcher>
```

또는 AND로 결합된 여러 매처를 부정하려면 블록을 엽니다:

```caddy-d
not {
	<matchers...>
}
```

포함된 매처들의 결과가 부정됩니다.

#### 예시:

경로가 `/css/` 또는 `/js/`로 시작하지 *않는* 요청과 일치:

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

다음 중 어느 것도 *아닌* 요청과 일치:
- `/api/` 경로 접두사가 없음, **동시에**
- `POST` 요청 메서드가 아님

즉, 일치하기 위해서는 이들 중 어느 것도 해당하지 않아야 합니다:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

다음이 모두 해당하지는 *않는* 요청과 일치:
- `/api/` 경로 접두사가 있음, **동시에**
- `POST` 요청 메서드임

즉, 일치하기 위해서는 이들 중 하나 또는 둘 다 해당하지 않아야 합니다:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

부정을 위해 `!` 연산자를 사용할 수 있으므로 이 매처에 대한 [CEL 표현식](#expression)은 없습니다. 예:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

이는 괄호를 사용하여 다음과 같이 작성할 수도 있습니다:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

요청 경로(요청 URI의 경로 구성 요소)로 매칭합니다. 경로 매칭은 정확히 일치해야 하지만 대소문자를 구분하지 않습니다. 와일드카드 `*`를 사용할 수 있습니다:

- 끝에만 사용: 접두사 일치 (`/prefix/*`)
- 앞에만 사용: 접미사 일치 (`*.suffix`)
- 양쪽 끝에만 사용: 부분 문자열 일치 (`*/contains/*`)
- 중간에만 사용: 글로브(globular) 일치 (`/accounts/*/info`)

슬래시는 중요합니다. 예를 들어, `/foo*`는 `/foo`, `/foobar`, `/foo/`, `/foo/bar`와 모두 일치하지만, `/foo/*`는 `/foo`나 `/foobar`와 일치하지 *않습니다*.

요청 경로는 매칭 전에 디렉토리 순회 점(..)을 해결하기 위해 정리됩니다. 또한 매치 패턴에 여러 슬래시가 있지 않는 한 여러 슬래시는 하나로 병합됩니다. 즉, `/foo`는 `/foo` 및 `//foo`와 일치하지만, `//foo`는 `//foo`하고만 일치합니다.

주어진 URI에는 여러 가지 이스케이프 형태가 존재할 수 있으므로, 매치 패턴에도 이스케이프 시퀀스가 있는 위치를 제외하고 요청 경로는 정규화(URL 디코딩, 이스케이프 해제)됩니다. 예를 들어, `/foo/bar`는 `/foo/bar`와 `/foo%2Fbar` 모두에 일치하지만, `/foo%2Fbar`는 구성에서 이스케이프 시퀀스가 명시적으로 주어졌으므로 `/foo%2Fbar`하고만 일치합니다.

특수 와일드카드 이스케이프 `%*`는 `*` 대신 사용되어 매칭되는 범위를 이스케이프된 상태로 둘 수 있습니다. 예를 들어, `/bands/*/*`는 정규화된 공간에서 `/bands/AC/DC/T.N.T`처럼 보여 패턴과 일치하지 않으므로 `/bands/AC%2FDC/T.N.T`와 일치하지 않습니다. 하지만 `/bands/%*/*`는 `%*`로 표시된 범위가 이스케이프 시퀀스를 디코딩하지 않고 비교되므로 `/bands/AC%2FDC/T.N.T`와 일치합니다.

여러 경로는 OR로 결합됩니다.

#### 예시:

여러 디렉토리와 그 내용 매칭:

```caddy-d
@assets path /js/* /css/* /images/*
```

특정 파일 매칭:

```caddy-d
@favicon path /favicon.ico
```

파일 확장자 매칭:

```caddy-d
@extensions path *.js *.css
```

[CEL 표현식](#expression) 사용 시:

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
### path_regexp <a id="path-regexp"></a>

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

[`path`](#path)와 유사하지만 정규 표현식을 지원합니다. URI 디코딩/이스케이프 해제된 경로에 대해 실행됩니다.

사용되는 정규 표현식 언어는 Go에 포함된 RE2입니다. [RE2 구문 참조](https://github.com/google/re2/wiki/Syntax) 및 [Go 정규식 구문 개요](https://pkg.go.dev/regexp/syntax)를 참조하세요.

v2.8.0부터 `name`이 제공되지 않으면 명명된 매처의 이름에서 이름을 가져옵니다. 예를 들어 명명된 매처 `@foo`는 이 매처의 이름을 `foo`로 만듭니다. 이름을 지정할 때의 주된 장점은 동일한 명명된 매처에서 두 개 이상의 정규식 매처(예: `path_regexp` 및 [`header_regexp`](#header-regexp))가 사용되는 경우입니다.

캡처 그룹은 매칭 후 지시어에서 [플레이스홀더](/docs/caddyfile/concepts#placeholders)를 통해 접근할 수 있습니다:
- `{re.<name>.<capture_group>}` 여기서:
  - `<name>`은 정규 표현식의 이름입니다.
  - `<capture_group>`은 표현식 내 캡처 그룹의 이름 또는 번호입니다.

- 편의를 위해 이름이 없는 `{re.<capture_group>}`도 채워집니다. 주의할 점은 여러 정규식 매처가 순차적으로 사용되면 플레이스홀더 값이 다음 매처에 의해 덮어씌워진다는 것입니다.

캡처 그룹 `0`은 전체 정규식 매치, `1`은 첫 번째 캡처 그룹, `2`는 두 번째 캡처 그룹 등입니다. 따라서 `{re.foo.1}` 또는 `{re.1}`은 모두 첫 번째 캡처 그룹의 값을 가집니다.

정규식 패턴은 자신과 병합될 수 없으므로 명명된 매처당 하나의 `path_regexp` 패턴만 있을 수 있습니다. 더 많이 필요한 경우 [`expression` 매처](#expression)를 사용하는 것이 좋습니다.

#### 예시:

경로가 6글자 16진수 문자열 뒤에 `.css` 또는 `.js` 확장자로 끝나는 요청과 일치하며, `( )`로 묶인 캡처 그룹은 각각 `{re.static.1}` 및 `{re.static.2}` (또는 `{re.1}` 및 `{re.2}`)로 접근할 수 있습니다:

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

명명된 매처에서 이름을 추론하도록 이름을 생략하여 단순화할 수 있습니다:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

또는 [CEL 표현식](#expression)을 사용하여 디스크에 [`file`](#file)이 존재하는지도 확인하는 경우:

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

요청 프로토콜로 매칭합니다. `http`, `https`, `grpc`와 같은 광범위한 프로토콜 이름이나 `http/1.1`, `http/2+`와 같은 특정 또는 최소 HTTP 버전을 사용할 수 있습니다.

명명된 매처당 하나의 `protocol` 매처만 있을 수 있습니다.

#### 예시:

HTTP/2를 사용하는 요청과 일치:

```caddy-d
@http2 protocol http/2+
```

[CEL 표현식](#expression) 사용 시:

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

쿼리 문자열 매개변수로 매칭합니다. `key=value` 쌍의 시퀀스이거나 빈 문자열 ""이어야 합니다. 키는 정확히(대소문자 구분) 일치해야 하지만 임의의 값을 매칭하기 위해 `*`를 지원합니다. 값은 플레이스홀더를 사용할 수 있습니다. 빈 문자열은 쿼리 매개변수가 없는 HTTP 요청과 일치합니다.

명명된 매처당 여러 개의 `query` 매처가 있을 수 있으며, 키가 같은 쌍은 OR로 결합됩니다. 키가 다르면 AND로 결합됩니다. 따라서 매처의 모든 키는 적어도 하나의 일치하는 값을 가져야 합니다.

잘못된 쿼리 문자열(잘못된 구문, 이스케이프되지 않은 세미콜론 등)은 파싱에 실패하여 일치하지 않습니다.

**참고:** 쿼리 문자열 매개변수는 단일 값이 아닌 배열입니다. 쿼리 문자열에는 반복되는 키가 유효하며 각 키는 서로 다른 값을 가질 수 있기 때문입니다. 이 매처는 쿼리 문자열에 구성된 값 중 하나라도 할당되어 있으면 해당 키에 대해 일치합니다. 쿼리 문자열을 사용하는 백엔드 애플리케이션은 쿼리 문자열 값이 배열이며 여러 값을 가질 수 있음을 고려해야 합니다.

#### 예시:

임의의 값을 가진 `q` 쿼리 매개변수와 일치:

```caddy-d
@search query q=*
```

`sort` 쿼리 매개변수가 `asc` 또는 `desc`인 요청과 일치:

```caddy-d
@sorted query sort=asc sort=desc
```

[CEL 표현식](#expression)을 사용하여 `q`와 `sort` 모두 일치:

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
### remote_ip <a id="remote-ip"></a>

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

원격 IP 주소(즉, 직전 피어의 IP 주소 또는 [PROXY 프로토콜](/docs/caddyfile/options#proxy-protocol)을 통해 설정된 주소)로 매칭합니다. 정확한 IP나 CIDR 범위를 허용합니다. IPv6 존이 지원됩니다.

축약형으로, `private_ranges`를 사용하여 모든 사설 IPv4 및 IPv6 범위를 매칭할 수 있습니다. 이는 `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1` 범위를 모두 지정하는 것과 같습니다.

HTTP 헤더에서 파싱된 클라이언트의 "실제 IP"를 매칭하려면 대신 [`client_ip`](#client-ip) 매처를 사용하십시오.

명명된 매처당 여러 개의 `remote_ip` 매처가 있을 수 있으며, 해당 범위는 병합되어 OR로 결합됩니다.

#### 예시:

사설 IPv4 주소의 요청과 일치:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

이 매처는 매칭을 반전시키기 위해 [`not`](#not) 매처와 자주 함께 쓰입니다. 예를 들어, 모든 사설 범의의 반대인 *공개* IPv4 및 IPv6 주소의 모든 연결을 중단하려면 다음과 같이 합니다:

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "안녕하세요, 사설 네트워크에서 오셨군요!"
}
```

[CEL 표현식](#expression)에서는 다음과 같습니다:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

요청 컨텍스트의 변수 값 또는 플레이스홀더의 값으로 매칭합니다. 해당 값들 중 어느 하나라도 일치하면 일치하는 것으로 간주하도록 여러 값을 지정할 수 있습니다(OR로 결합).

**&lt;variable&gt;** 인수는 변수 이름이거나 중괄호 `{ }`로 묶인 플레이스홀더일 수 있습니다. (첫 번째 매개변수에서는 플레이스홀더가 확장되지 않습니다.)

이 매처는 출력을 설정하는 [`map` 지시어](/docs/caddyfile/directives/map), 라우트 내의 [`vars` 지시어](/docs/caddyfile/directives/vars), 또는 요청 컨텍스트에 정보를 설정하는 플러그인과 함께 사용할 때 가장 유용합니다.

#### 예시:

값이 `3` 또는 `5`인 `magic_number`라는 이름의 [`map` 지시어](/docs/caddyfile/directives/map) 출력과 일치:

```caddy-d
vars {magic_number} 3 5
```

임의의 플레이스홀더 값, 즉 인증된 사용자 ID가 `Bob` 또는 `Alice`인 경우와 일치:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

[`vars` 지시어](/docs/caddyfile/directives/vars)를 사용하여 변수를 설정하고 [`vars` 매처](#vars)로 일치시키는 전체 예제입니다. 여기서는 두 개의 요청 헤더를 하나의 변수로 결합하고 해당 변수와 일치시킵니다:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

[CEL 표현식](#expression)에서는 다음과 같습니다:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
### vars_regexp <a id="vars-regexp"></a>

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

[`vars`](#vars)와 유사하지만 정규 표현식을 지원합니다.

사용되는 정규 표현식 언어는 Go에 포함된 RE2입니다. [RE2 구문 참조](https://github.com/google/re2/wiki/Syntax) 및 [Go 정규식 구문 개요](https://pkg.go.dev/regexp/syntax)를 참조하세요.

v2.8.0부터 `name`이 제공되지 않으면 명명된 매처의 이름에서 이름을 가져옵니다. 예를 들어 명명된 매처 `@foo`는 이 매처의 이름을 `foo`로 만듭니다. 이름을 지정할 때의 주된 장점은 동일한 명명된 매처에서 두 개 이상의 정규식 매처(예: `vars_regexp` 및 [`header_regexp`](#header-regexp))가 사용되는 경우입니다.

캡처 그룹은 매칭 후 지시어에서 [플레이스홀더](/docs/caddyfile/concepts#placeholders)를 통해 접근할 수 있습니다:
- `{re.<name>.<capture_group>}` 여기서:
  - `<name>`은 정규 표현식의 이름입니다.
  - `<capture_group>`은 표현식 내 캡처 그룹의 이름 또는 번호입니다.

- 편의를 위해 이름이 없는 `{re.<capture_group>}`도 채워집니다. 주의할 점은 여러 정규식 매처가 순차적으로 사용되면 플레이스홀더 값이 다음 매처에 의해 덮어씌워진다는 것입니다.

캡처 그룹 `0`은 전체 정규식 매치, `1`은 첫 번째 캡처 그룹, `2`는 두 번째 캡처 그룹 등입니다. 따라서 `{re.foo.1}` 또는 `{re.1}`은 모두 첫 번째 캡처 그룹의 값을 가집니다.

정규식 패턴은 병합될 수 없으므로 변수 이름당 하나의 정규 표현식만 지원됩니다. 더 많이 필요한 경우 [`expression` 매처](#expression)를 사용하는 것이 좋습니다. 여러 다른 변수에 대한 매치는 AND로 결합됩니다.

#### 예시:

`4`로 시작하는 값을 가진 `magic_number`라는 이름의 [`map` 지시어](/docs/caddyfile/directives/map) 출력과 일치하며, 캡처 그룹은 `{re.magic.1}` 또는 `{re.1}`로 접근할 수 있습니다.

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

명명된 매처에서 이름을 추론하도록 이름을 생략하여 단순화할 수 있습니다:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

[CEL 표현식](#expression)에서는 다음과 같습니다:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
`
`
`
`
