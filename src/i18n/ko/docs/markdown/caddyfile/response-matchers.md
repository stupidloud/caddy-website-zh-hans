---
title: 응답 매처 (Response matchers) (Caddyfile)
---

<script>
ready(function() {
	// Response matchers
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# 응답 매처 <a id="response-matchers"></a>

**응답 매처(Response matchers)** 는 특정 기준에 따라 응답을 필터링(또는 분류)하는 데 사용됩니다.

이들은 일반적으로 클라이언트로 작성되는 응답에 대해 결정을 내리기 위해 다른 특정 지시어 내부의 설정으로만 나타납니다.

- [구문](#syntax)
- [매처](#matchers)
	- [status](#status)
	- [header](#header)

## 구문 <a id="syntax"></a>

지시어가 응답 매처를 수용하는 경우, 구문 문서에서 `[<response_matcher>]` 또는 `[<inline_response_matcher>]`로 표시됩니다.

- **<response_matcher>** 토큰은 이전에 선언된 이름이 있는 응답 매처의 이름일 수 있습니다. 예: `@name`.
- **<inline_response_matcher>** 토큰은 사전에 선언할 필요 없이 응답 기준 자체일 수 있습니다. 예: `status 200`.

### 이름이 있는 매처 (Named) <a id="named"></a>

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
응답의 한 가지 측면만 지시어와 관련이 있는 경우, 이름과 기준을 같은 줄에 놓을 수 있습니다:

```caddy-d
@name status <code...>
```

### 인라인 매처 (Inline) <a id="inline"></a>

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

## 매처 <a id="matchers"></a>

### status <a id="status"></a>

```caddy-d
status <code...>
```

HTTP 상태 코드별로 매칭합니다.

- **&lt;code...&gt;** 는 HTTP 상태 코드 목록입니다. `2xx` 및 `3xx`와 같은 특수 케이스는 각각 `200`-`299` 및 `300`-`399` 범위의 모든 상태 코드와 일치합니다.

#### 예시:

```caddy-d
@success status 2xx
```



### header <a id="header"></a>

```caddy-d
header <field> [<value>]
```

응답 헤더 필드별로 매칭합니다.

- `<field>`는 확인할 HTTP 헤더 필드의 이름입니다.
	- 앞에 `!`가 붙으면 매칭을 위해 해당 필드가 존재하지 않아야 합니다 (값 인자 생략).
- `<value>`는 일치하기 위해 필드가 가져야 하는 값입니다.
	- 앞에 `*`가 붙으면 빠른 접미사 일치를 수행합니다 (끝에 나타남).
	- 뒤에 `*`가 붙으면 빠른 접두사 일치를 수행합니다 (시작 부분에 나타남).
	- `*`로 감싸면 빠른 부분 문자열 일치를 수행합니다 (어디서나 나타남).
	- 그렇지 않으면 빠른 정확한 일치입니다.

동일한 세트 내의 서로 다른 헤더 필드는 AND로 연결됩니다. 필드당 여러 값은 OR로 연결됩니다.

헤더 필드는 반복될 수 있고 서로 다른 값을 가질 수 있음에 유의하세요. 백엔드 애플리케이션은 헤더 필드 값이 단일 값이 아니라 배열임을 고려해야 하며, Caddy는 이러한 모호한 상황에서 의미를 해석하지 않습니다.

#### 예시:

`bar` 값을 포함하는 `Foo` 헤더가 있는 응답과 일치:

```caddy-d
@upgrade header Foo *bar*
```

`Foo` 헤더의 값이 `bar` 또는 `baz`인 응답과 일치:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

`Foo` 헤더 필드가 전혀 없는 응답과 일치:

```caddy-d
@not_foo header !Foo
```
