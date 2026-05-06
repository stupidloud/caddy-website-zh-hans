---
title: handle_path (Caddyfile 지시어)
---

<script>
ready(function() {
	// Add a link to [<path_matcher>] as a special case for this directive.
	// The matcher text includes <> characters which are parsed as HTML,
	// so we must use text() to change the link text.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Matcher token">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

[`handle` 지시어](handle)와 동일하게 작동하지만, 매칭된 경로 접두사를 제거하기 위해 암시적으로 [`uri strip_prefix`](uri)를 사용합니다.

특정 경로와 일치하는 요청을 처리하는 동시에 요청 URI에서 해당 경로를 제거하는 것은 충분히 일반적인 사용 사례이므로 편의를 위해 전용 지시어가 제공됩니다.


## 구문 <a id="syntax"></a>

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** 는 `handle_path` 블록 외부에서 사용되는 것과 마찬가지로 한 줄에 하나씩 나열된 HTTP 핸들러 지시어 또는 지시어 블록 목록입니다.

단일 [경로 매처](/docs/caddyfile/matchers#path-matchers)만 허용되며 필수입니다. `handle_path`에는 명명된 매처(named matchers)를 사용할 수 없습니다.

## 예제 <a id="examples"></a>

이 설정은:

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 사실상 아래와 동일하지만, `handle_path` 형태인 👆가 약간 더 간결합니다.

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

`handle_path`와 `handle`이 상호 배타적인 전체 Caddyfile 예제입니다. 하지만 [하위 폴더 문제 <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)에 유의하십시오.

```caddy
example.com {
	# /api 접두사를 제거하고 API를 서비스합니다
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# 정적 사이트를 서비스합니다
	handle {
		root /srv
		file_server
	}
}
```
