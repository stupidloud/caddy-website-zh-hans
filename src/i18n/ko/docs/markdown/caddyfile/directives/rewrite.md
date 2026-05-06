---
title: rewrite (Caddyfile 지시어)
---

# rewrite

내부적으로 요청 URI를 재작성(rewrite)합니다.

재작성은 요청 URI의 일부 또는 전체를 변경합니다. URI에는 스킴(scheme)이나 권한(authority, 호스트 및 포트)이 포함되지 않으며, 클라이언트는 일반적으로 프래그먼트(fragment)를 보내지 않는다는 점에 유의하세요. 따라서 이 지시어는 주로 **경로(path)** 및 **쿼리(query)** 문자열 조작에 사용됩니다.

`rewrite` 지시어는 요청을 수락하되 수정하겠다는 의도를 내포합니다.

동일한 블록 내의 다른 `rewrite` 지시어와 상호 배타적이므로, 첫 번째로 일치하는 재작성만 실행됩니다. 따라서 서로 중첩될 수 있는 재작성들을 정의해도 안전합니다.

`rewrite` 이전의 요청과 일치하는 [요청 매처(request matcher)](/docs/caddyfile/matchers)가 `rewrite` 이후에는 동일한 요청과 일치하지 않을 수 있습니다. `rewrite`를 다른 핸들러와 경로를 공유하고 싶다면, [`route`](route) 또는 [`handle`](handle) 지시어를 사용하세요.


## 구문 <a id="syntax"></a>

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** 는 요청을 재작성할 대상 URI입니다. 재작성에 지정된 URI 구성 요소(경로 또는 쿼리 문자열)만 작업 대상이 됩니다. URI 경로는 `?` 앞에 오는 모든 부분 문자열입니다. `?`가 생략되면 토큰 전체가 경로로 간주됩니다.

v2.8.0 이전에는 `<to>` 인자가 `/`로 시작하는 경우 파서가 [매처 토큰](/docs/caddyfile/matchers#syntax)으로 혼동할 수 있었기 때문에, 와일드카드 매처 토큰(`*`)을 지정해야 했습니다.


## 유사한 지시어 <a id="similar-directives"></a>

재작성을 수행하지만 다른 의도를 내포하거나 URI를 완전히 교체하지 않고 재작성을 수행하는 다른 지시어들이 있습니다:

- [`uri`](uri)는 URI를 조작합니다(접두사, 접미사 제거 또는 부분 문자열 교체).

- [`try_files`](try_files)는 파일의 존재 여부에 따라 요청을 재작성합니다.



## 예시 <a id="examples"></a>

모든 요청을 `index.html`로 재작성하고, 쿼리 문자열은 변경하지 않은 상태로 둡니다:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

v2.8.0 이전에는 첫 번째 인자가 [경로 매처](/docs/caddyfile/matchers#path-matchers)와 모호했기 때문에(예: `rewrite * /foo`) [와일드카드 매처](/docs/caddyfile/matchers#wildcard-matchers)가 필요했지만, 이제는 `rewrite /foo`로 단순화할 수 있습니다.

</aside>

모든 요청 앞에 `/api`를 붙이고 나머지 URI를 보존한 다음, 앱으로 리버스 프록시합니다:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

API 요청의 쿼리 문자열을 `a=b`로 교체하고 경로는 변경하지 않습니다:

```caddy
example.com {
	rewrite ?a=b
}
```

`/api/` 요청에 대해서만 기존 쿼리 문자열을 유지하고 키-값 쌍을 추가합니다:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

경로와 쿼리 문자열을 모두 변경하며, 원래의 쿼리 문자열을 보존하면서 원래 경로를 `p` 파라미터로 추가합니다:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
