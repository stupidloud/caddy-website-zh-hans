---
title: route (Caddyfile 지시어)
---

# route

지시어 그룹을 문자 그대로, 그리고 하나의 단위로 평가합니다.

route 블록에 포함된 지시어는 [내부적으로 재정렬되지 않습니다](/docs/caddyfile/directives#directive-order)。HTTP 핸들러 지시어(체인에 핸들러나 미들웨어를 추가하는 지시어)만 route 블록에서 사용할 수 있습니다.

이 지시어는 하위 지시어 또한 일반 지시어라는 점에서 특수한 경우입니다.


## 구문 <a id="syntax"></a>

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** 는 route 블록 외부와 마찬가지로 한 줄에 하나씩 작성되는 지시어 또는 지시어 블록의 목록입니다. 다만, 이 지시어들은 재정렬되지 않는다는 점이 다릅니다. HTTP 핸들러 지시어만 사용할 수 있습니다.



## 유용성 <a id="utility"></a>

`route` 지시어는 HTTP 핸들러 체인의 일부를 완전히 제어해야 하는 특정 고급 사용 사례나 엣지 케이스에서 유용합니다.

HTTP 미들웨어 평가 순서가 중요하기 때문에, Caddyfile은 일반적으로 파싱 후에 지시어를 재정렬하여 Caddyfile을 더 쉽게 사용할 수 있도록 합니다. 따라서 사용자는 입력 순서에 대해 걱정할 필요가 없습니다.

[내장된 순서](/docs/caddyfile/directives#directive-order)가 대부분의 사이트와 호환되지만, 때로는 사이트 전체나 일부에 대해 수동으로 순서를 제어해야 할 때가 있습니다. 바로 그럴 때 `route` 지시어를 사용합니다.

예를 들어, 두 개의 종료 핸들러(terminating handler)인 [`redir`](redir)과 [`file_server`](file_server)의 경우를 생각해 봅시다. 두 지시어 모두 클라이언트에 응답을 작성하고 체인의 다음 핸들러를 호출하지 않으므로, 특정 요청에 대해 이 중 하나만 실행됩니다.

그렇다면 어느 것이 먼저 실행될까요? 일반적으로 `redir`은 `file_server`보다 먼저 실행됩니다. 대개 특정 케이스에서만 리다이렉트를 수행하고 일반적인 경우에는 파일을 제공하기를 원하기 때문입니다.

하지만 첫 번째 지시어(`file_server`)가 두 번째 지시어(`redir`)보다 더 구체적인 매처를 갖는 경우가 있을 수 있습니다. 다시 말해, 일반적인 경우에는 리다이렉트하고 특정 파일만 제공하고 싶은 경우입니다.

그래서 다음과 같이 Caddyfile을 작성해 볼 수 있습니다(하지만 이는 예상대로 작동하지 않습니다!):

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

문제는 [지시어가 정렬된 후](/docs/caddyfile/directives#sorting-algorithm), `redir`이 `file_server`보다 앞에 오게 된다는 점입니다.

하지만 이 경우 `redir`의 매처(암시적인 [`*`](/docs/caddyfile/matchers#wildcard-matchers))는 `file_server`의 매처(`/specific.html`)를 포함하는 상위 집합(superset)입니다. (`*`는 `/specific.html`의 상위 집합입니다.)

다행히 해결 방법은 간단합니다. 이 두 지시어를 `route` 블록으로 감싸서 `file_server`가 `redir`보다 먼저 실행되도록 보장하면 됩니다:

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

이를 수행하는 또 다른 방법은 두 매처를 상호 배타적으로 만드는 것이지만, 조건이 한두 개 이상이면 금방 복잡해질 수 있습니다. `route` 지시어를 사용하면 두 핸들러가 모두 종료 핸들러이기 때문에 상호 배타성이 암시적으로 적용됩니다.

</aside>

이제 순서가 문자 그대로 받아들여지기 때문에 `file_server`가 `redir`보다 먼저 체인에 연결됩니다.



## 유사한 지시어 <a id="similar-directives"></a>

HTTP 핸들러 지시어를 감싸는 다른 지시어들이 있지만, 각각 원하는 동작에 따라 용도가 다릅니다:

- [`handle`](handle)은 `route`처럼 다른 지시어를 감싸지만 두 가지 차이점이 있습니다: 1) handle 블록은 서로 상호 배타적이며, 2) handle 내의 지시어는 평소처럼 [재정렬](/docs/caddyfile/directives#directive-order)됩니다.

- [`handle_path`](handle_path)는 `handle`과 동일한 작업을 수행하지만, 핸들러를 실행하기 전에 요청에서 접두사를 제거합니다.

- [`handle_errors`](handle_errors)는 `handle`과 비슷하지만, 요청 처리 중에 Caddy에서 오류가 발생했을 때만 호출됩니다.



## 예시 <a id="examples"></a>

`/api` 요청은 그대로 프록시하고, 다른 모든 요청은 디스크의 파일과 일치하는지 여부에 따라 재작성합니다. 일치하지 않으면 `/index.html`로 재작성합니다. 그 후 해당 파일을 제공합니다.

[`try_files`](try_files)는 [`reverse_proxy`](reverse_proxy)보다 지시어 순서가 높기 때문에 일반적으로 더 높게 정렬되어 먼저 실행됩니다. 이렇게 되면 모든 API 요청이 `/index.html`로 재작성되어 `/api*`와 일치하지 않게 되므로, 프록시가 되지 않고 대신 [`file_server`](file_server)로부터 `404` 응답을 받게 됩니다. 이 모든 것을 `route`로 감싸면 요청이 재작성되기 전에 `reverse_proxy`가 항상 먼저 실행되도록 보장합니다.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

이 문제에 대한 유일한 해결책은 아닙니다. 두 개의 [`handle`](handle) 블록을 사용하여 첫 번째 블록은 `/api*`를 `reverse_proxy`에 매칭시키고, 두 번째 블록은 폴백(fallback)으로 작동하여 파일을 서비스할 수도 있습니다. SPA의 [이 예시](/docs/caddyfile/patterns#single-page-apps-spas)를 참고하세요.

</aside>
