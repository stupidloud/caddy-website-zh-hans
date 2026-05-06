---
title: encode (Caddyfile 지시어)
---

<script>
ready(function() {
	// 일치하는 앵커 태그가 페이지에서 발견되면 모든 하위 지시어에 대한 링크를 추가합니다.
	addLinksToSubdirectives();

	// 응답 매처 (Response matchers)
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;" title="Response matcher">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;" title="Response matcher">header</a>';
		}
	});
});
</script>

# encode

설정된 인코딩 방식을 사용하여 응답을 인코딩합니다. 인코딩의 일반적인 용도는 압축입니다.

## 구문

```caddy-d
encode [<matcher>] [<formats...>] {
	# 인코딩 형식
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** 는 활성화할 인코딩 형식의 목록입니다. 여러 인코딩이 활성화된 경우 요청의 Accept-Encoding 헤더를 기반으로 인코딩이 선택됩니다. 클라이언트의 뚜렷한 선호도(q-factor)가 없는 경우 지원되는 첫 번째 인코딩이 사용됩니다. 생략하면 `zstd` (권장)와 `gzip`이 기본적으로 활성화됩니다.

- **gzip** <span id="gzip"/> 은 Gzip 압축을 활성화하며, 선택적으로 지정된 레벨을 사용할 수 있습니다.

- **zstd** <span id="zstd"/> 는 Zstandard 압축을 활성화하며, 선택적으로 지정된 레벨을 사용할 수 있습니다 (가능한 값: default, fastest, better, best). 기본 압축 레벨은 대략 Zstandard 기본 모드(레벨 3)와 비슷합니다.

- **minimum_length** <span id="minimum_length"/> 는 응답이 인코딩되기 위해 필요한 최소 바이트 수입니다 (기본값: 512).

- **match** <span id="match"/> 는 [응답 매처(response matcher)](/docs/caddyfile/response-matchers)입니다. 일치하는 응답만 인코딩됩니다. 기본값은 다음과 같습니다:

  ```caddy-d
  match {
  	header Content-Type application/atom+xml*
  	header Content-Type application/eot*
  	header Content-Type application/font*
  	header Content-Type application/geo+json*
  	header Content-Type application/graphql+json*
  	header Content-Type application/javascript*
  	header Content-Type application/json*
  	header Content-Type application/ld+json*
  	header Content-Type application/manifest+json*
  	header Content-Type application/opentype*
  	header Content-Type application/otf*
  	header Content-Type application/rss+xml*
  	header Content-Type application/truetype*
  	header Content-Type application/ttf*
  	header Content-Type application/vnd.api+json*
  	header Content-Type application/vnd.ms-fontobject*
  	header Content-Type application/wasm*
  	header Content-Type application/x-httpd-cgi*
  	header Content-Type application/x-javascript*
  	header Content-Type application/x-opentype*
  	header Content-Type application/x-otf*
  	header Content-Type application/x-perl*
  	header Content-Type application/x-protobuf*
  	header Content-Type application/x-ttf*
  	header Content-Type application/xhtml+xml*
  	header Content-Type application/xml*
  	header Content-Type font/*
  	header Content-Type image/svg+xml*
  	header Content-Type image/vnd.microsoft.icon*
  	header Content-Type image/x-icon*
  	header Content-Type multipart/bag*
  	header Content-Type multipart/mixed*
  	header Content-Type text/*
  }
  ```


## 예시

Gzip 압축 활성화:

```caddy-d
encode gzip
```

Zstandard 및 Gzip 압축 활성화 (Zstandard가 먼저 있으므로 암시적으로 우선됨):

```caddy-d
encode zstd gzip
```

이것이 기본값이므로, 이전 설정은 다음과 완전히 동일합니다:

```caddy-d
encode
```

그리고 전체 사이트에서, [`file_server`](file_server)가 제공하는 정적 파일을 압축하는 예시입니다:

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
