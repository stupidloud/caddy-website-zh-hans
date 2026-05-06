---
title: request_header (Caddyfile 지시어)
---

# request_header

요청의 HTTP 헤더 필드를 조작합니다. 헤더 값을 설정(set), 추가(add), 삭제(delete)하거나 정규 표현식을 사용하여 교체(replace)를 수행할 수 있습니다.

프록시 처리를 위해 헤더를 조작하려는 경우, `reverse_proxy`의 [`header_up` 하위 지시어](/docs/caddyfile/directives/reverse_proxy#header_up)를 대신 사용하세요. 해당 조작 방식은 프록시를 인식합니다.

HTTP 응답 헤더를 조작하려면 [`header`](header) 지시어를 사용할 수 있습니다.


## 구문

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** 는 헤더 필드의 이름입니다.

  접두사가 없으면 필드가 설정(덮어쓰기)됩니다.

  접두사 `+`를 붙이면 기존 필드가 존재할 경우 덮어쓰는(설정하는) 대신 필드를 추가합니다. 헤더 필드는 하나의 요청에 여러 번 나타날 수 있습니다.

  접두사 `-`를 붙이면 필드를 삭제합니다. 필드에 접두사나 접미사로 `*` 와일드카드를 사용하여 일치하는 모든 필드를 삭제할 수 있습니다.

- **&lt;value&gt;** 는 필드를 추가하거나 설정할 때의 헤더 필드 값입니다.

- **&lt;find&gt;** 는 검색할 부분 문자열 또는 정규 표현식입니다.

- **&lt;replace&gt;** 는 교체할 값입니다. 검색 및 교체를 수행할 때 필요합니다.


## 예시

요청에서 Referer 헤더를 제거합니다:

```caddy-d
request_header -Referer
```

요청에서 밑줄(_)이 포함된 모든 헤더를 삭제합니다:

```caddy-d
request_header -*_*
```
