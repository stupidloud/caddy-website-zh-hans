---
title: handle (Caddyfile 지시어)
---

# handle

동일한 중첩 수준의 다른 `handle` 블록과 상호 배타적으로 지시어 그룹을 평가합니다.

즉, 여러 개의 `handle` 지시어가 순차적으로 나타나면 첫 번째 *matching* `handle` 블록만 평가됩니다. 매처가 없는 handle은 *fallback* 경로처럼 작동합니다.

`handle` 지시어는 매처에 따라 [지시어 정렬 알고리즘](/docs/caddyfile/directives#sorting-algorithm)에 의해 정렬됩니다. [`handle_path`](handle_path) 지시어는 경로 매처가 있는 `handle`과 동일한 우선순위로 정렬되는 특수한 사례입니다.

필요한 경우 handle 블록을 중첩하여 사용할 수 있습니다. handle 블록 내부에는 HTTP 핸들러 지시어만 사용할 수 있습니다.

## 구문 <a id="syntax"></a>

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** 는 handle 블록 외부에서 사용되는 것과 마찬가지로 한 줄에 하나씩 나열된 HTTP 핸들러 지시어 또는 지시어 블록 목록입니다.



## 유사한 지시어 <a id="similar-directives"></a>

HTTP 핸들러 지시어를 감싸는 다른 지시어들이 있지만, 각각 원하는 동작에 따라 용도가 다릅니다:

- [`handle_path`](handle_path)는 `handle`과 동일하게 작동하지만, 핸들러를 실행하기 전에 요청에서 접두사를 제거합니다.

- [`handle_errors`](handle_errors)는 `handle`과 비슷하지만, Caddy가 요청 처리 중에 오류를 만났을 때만 호출됩니다.

- [`route`](route)는 `handle`처럼 다른 지시어를 감싸지만, 두 가지 차이점이 있습니다:
  1. route 블록은 서로 상호 배타적이지 않습니다.
  2. route 내의 지시어는 [정렬 순서가 변경되지 않으므로](/docs/caddyfile/directives#directive-order), 필요한 경우 더 많은 제어가 가능합니다.



## 예제 <a id="examples"></a>

`/foo/`로 시작하는 요청은 정적 파일 서버로 처리하고, 그 외의 요청은 리버스 프록시로 처리합니다:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

동일한 사이트 내에서 `handle`과 [`handle_path`](handle_path)를 섞어서 사용할 수 있으며, 이들은 여전히 서로 상호 배타적입니다:

```caddy
example.com {
	handle_path /foo/* {
		# "/foo" 접두사가 제거된 경로
	}

	handle /bar/* {
		# "/bar"가 그대로 유지된 경로
	}
}
```

더 복잡한 라우팅 로직을 만들기 위해 `handle` 블록을 중첩할 수 있습니다:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# 이 블록은 /foo/bar 하위 경로만 매칭합니다
		}

		handle {
			# 이 블록은 /foo/ 하위의 나머지 모든 항목을 매칭합니다
		}
	}

	handle {
		# 이 블록은 그 외의 모든 항목을 매칭합니다 (폴백 역할)
	}
}
```
