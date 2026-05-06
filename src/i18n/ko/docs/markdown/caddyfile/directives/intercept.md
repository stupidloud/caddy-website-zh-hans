---
title: intercept (Caddyfile 지시어)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Response matchers
	const nameMatchers = Array.from($$_('pre.chroma .nd')).filter(item => item.innerText.includes('@name'));
	if (nameMatchers.length > 0) {
		const first = nameMatchers[0];
		const span = document.createElement('span');
		span.className = 'nd';
		first.parentNode.insertBefore(span, first);
		span.appendChild(first);
		span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;">@name</a>';
	}
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText === 'status') {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;">status</a>';
		}
	});
	
	const headerElements = $$_('pre.chroma .k');
	for (let item of headerElements) {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;">header</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# intercept

[`reverse_proxy` 지시어](reverse_proxy)의 [응답 가로채기](reverse_proxy#intercepting-responses) 기능을 일반화한 추상화입니다. [FrankenPHP](https://frankenphp.dev/)의 `php_server`와 같은 플러그인을 포함하여 응답을 생성하는 모든 핸들러와 함께 사용할 수 있습니다.

이 지시어를 사용하면 [응답을 매칭](/docs/caddyfile/response-matchers)할 수 있으며, 첫 번째로 매칭되는 `handle_response` 경로 또는 `replace_status`가 호출됩니다. 호출되면 원래의 응답 본문은 보류되며, 해당 경로에서 새로운 상태 코드나 필요한 응답 헤더 조작을 통해 다른 응답 본문을 작성할 기회를 갖게 됩니다. 만약 경로에서 새로운 응답 본문을 작성하지 *않으면*, 원래의 응답 본문이 대신 작성됩니다.


## 구문

```caddy-d
intercept [<matcher>] {
	@name {
		status <code...>
		header <field> [<value>]
	}

	replace_status [<response_matcher>] <code>

	handle_response [<response_matcher>] {
		<directives...>
	}
}
```

- **@name** 은 명명된 [응답 매처](/docs/caddyfile/response-matchers) 블록입니다. 각 응답 매처의 이름이 고유하다면 여러 개의 매처를 정의할 수 있습니다. 상태 코드와 응답 헤더의 존재 여부 또는 값에 따라 응답을 매칭할 수 있습니다.

- **replace_status** <span id="replace_status"/> 는 주어진 매처에 의해 매칭되었을 때 응답의 상태 코드를 단순히 변경합니다.

- **handle_response** <span id="handle_response"/> 는 원래의 응답이 주어진 응답 매처에 의해 매칭되었을 때 실행할 경로를 정의합니다. 매처를 생략하면 모든 응답이 가로채집니다. 여러 개의 `handle_response` 블록이 정의된 경우, 첫 번째로 매칭되는 블록이 적용됩니다. 블록 내부에서는 다른 모든 [지시어](/docs/caddyfile/directives)를 사용할 수 있습니다.

`handle_response` 경로 내에서는 원래 응답에서 정보를 가져오기 위해 다음과 같은 플레이스홀더를 사용할 수 있습니다:

- `{resp.status_code}` 원래 응답의 상태 코드입니다.

- `{resp.header.*}` 원래 응답의 헤더입니다.


## 예시

[FrankenPHP](https://frankenphp.dev/)의 `php_server`를 사용할 때, `intercept`를 사용하여 `X-Accel-Redirect` 지원을 구현하고 PHP 앱에서 요청한 대로 정적 파일을 제공할 수 있습니다:

```caddy
localhost {
	root /srv

	intercept {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}

	php_server
}
```
