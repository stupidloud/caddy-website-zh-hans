---
title: file_server (Caddyfile 지시어)
---

<script>
ready(function() {
	// 인라인 browse 인자 수정
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// 일치하는 앵커 태그가 페이지에서 발견되면 모든 하위 지시어에 대한 링크를 추가합니다.
	addLinksToSubdirectives();
});
</script>

# file_server

실제 파일 시스템과 가상 파일 시스템을 모두 지원하는 정적 파일 서버입니다. 요청의 URI 경로를 [사이트의 루트 경로](root)에 추가하여 파일 경로를 생성합니다.

기본적으로 표준(canonical) URI를 강제합니다. 즉, 슬래시로 끝나지 않는 디렉토리 요청에는 슬래시를 추가하기 위해, 슬래시로 끝나는 파일 요청에는 슬래시를 제거하기 위해 HTTP 리다이렉트를 보냅니다. 하지만 내부 리라이트(rewrite)가 경로의 마지막 요소(파일명)를 수정한 경우에는 리다이렉트가 수행되지 않습니다.

가장 일반적으로 `file_server` 지시어는 전체 사이트의 파일 루트를 설정하기 위해 [`root`](root) 지시어와 함께 사용됩니다. 이 지시어에는 이 핸들러에 대해서만 루트를 설정하는 `root` 하위 지시어(아래 참조)도 있지만, 권장되지 않습니다. 사이트 루트가 샌드박스 보장을 제공하지 않는다는 점에 유의하세요. 파일 서버는 경로 컴포넌트를 통한 디렉토리 트래버설은 방지하지만, 루트 내의 심볼릭 링크를 통해 루트 외부로의 접근은 여전히 허용될 수 있습니다.

오류가 발생하면(예: 파일 찾을 수 없음 `404`, 권한 없음 `403`), 오류 라우트가 호출됩니다. [`handle_errors`](handle_errors) 지시어를 사용하여 오류 라우트를 정의하고 사용자 정의 오류 페이지를 표시할 수 있습니다.

`browse`를 사용할 때 기본 출력은 HTML 템플릿에 의해 생성됩니다. 클라이언트는 `Accept: application/json` 또는 `Accept: text/plain` 헤더를 사용하여 디렉토리 목록을 각각 JSON 또는 일반 텍스트로 요청할 수 있습니다. JSON 출력은 스크립팅에 유용하며, 일반 텍스트 출력은 터미널 사용자에게 유용할 수 있습니다.


## 구문

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> 는 사용할 대체(또는 가상) 파일 시스템을 지정합니다. `caddy.fs` 네임스페이스의 모든 Caddy 모듈을 여기서 사용할 수 있습니다. 모든 루트 경로/접두사는 여전히 대체 파일 시스템 모듈에 적용됩니다. 기본적으로 로컬 디스크가 사용됩니다.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0에는 커스텀 Caddy 빌드에 파일 시스템 트리를 포함하는 [`--embed` 플래그](https://github.com/caddyserver/xcaddy#custom-builds)가 도입되었으며, 정적 사이트를 Caddy 실행 파일로 배포할 수 있게 해주는 `embedded`라는 `fs` 모듈을 등록합니다.

- **root** <span id="root"/> 는 사이트 루트 경로를 설정합니다. 이는 [`root`](root) 지시어와 비슷하지만, 이 파일 서버 인스턴스에만 적용되며 정의된 다른 사이트 루트를 오버라이드합니다. 기본값: `{http.vars.root}` 또는 현재 작업 디렉토리. 참고: 이 하위 지시어는 이 핸들러의 루트만 변경합니다. 다른 지시어(예: [`try_files`](try_files) 또는 [`templates`](templates))가 동일한 사이트 루트를 알게 하려면 대신 [`root`](root) 지시어를 사용하세요.

- **hide** <span id="hide"/> 는 숨길 파일 또는 폴더 목록입니다. 요청 시 파일 서버는 해당 파일이 존재하지 않는 것처럼 작동합니다. 플레이스홀더와 glob 패턴을 허용합니다. 이는 요청 경로가 아니라 *파일 시스템* 경로임에 유의하세요. 즉, 상대 경로는 사이트 루트가 아닌 현재 작업 디렉토리를 기준으로 하며, 모든 경로는 비교 전에 절대 경로로 변환됩니다(가능한 경우). 경로 구분자 없이 파일 이름이나 패턴을 지정하면 위치에 관계없이 일치하는 이름을 가진 모든 파일이 숨겨집니다. 그렇지 않으면 경로 접두사 일치를 시도한 후 glob 일치를 시도합니다. 이는 Caddyfile 설정이므로 활성 설정 파일들이 기본적으로 추가됩니다. 숨김 비교는 대소문자를 구분합니다. 대소문자를 구분하지 않는 파일 시스템에서는 대소문자가 다른 요청 경로가 여전히 동일한 디스크 경로로 확인될 수 있으므로, `hide`를 민감한 경로에 대한 보안 경계로 취급해서는 안 됩니다.

- **index** <span id="index"/> 는 인덱스 파일로 찾을 파일 이름 목록입니다. 기본값: `index.html index.txt`

- **browse** <span id="browse"/> 는 인덱스 파일이 없는 디렉토리 요청에 대해 파일 목록 표시를 활성화합니다.

  - **<template_file>** <span id="template_file"/> 은 디렉토리 목록에 사용할 선택적 사용자 정의 템플릿 파일입니다. 기본값은 `caddy file-server export-template` 명령을 사용하여 추출할 수 있는 템플릿입니다. 내장된 템플릿은 [여기 소스 코드 ![외부 링크](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html)에서도 찾을 수 있습니다. Browse 템플릿은 [표준 templates 모듈](/docs/modules/http.handlers.templates#docs)의 액션도 사용할 수 있습니다.

  - **reveal_symlinks** <span id="reveal_symlinks"/> 는 디렉토리 목록에서 심볼릭 링크의 대상을 표시하도록 설정합니다. 기본적으로 심볼릭 링크 대상은 숨겨지며 링크 파일 자체만 표시됩니다.

  - **sort** <span id="sort"/> 는 디렉토리 목록의 기본 정렬 방식을 변경합니다. 첫 번째 인자는 정렬할 필드/열입니다: `name`, `namedirfirst`, `size`, 또는 `time`. 두 번째 인자는 선택적 정렬 방향입니다: `asc` 또는 `desc`. 예를 들어, `sort name desc`는 이름을 기준으로 내림차순 정렬합니다.

  - **file_limit** <span id="file_limit"/> 는 디렉토리 목록에 표시할 최대 파일 수를 설정합니다. 기본값: `10000`. 파일 수가 이 제한을 초과하면 지정된 제한까지의 파일만 표시됩니다.

- **precompressed** <span id="precompressed"/> 는 미리 압축된 사이드카(sidecar) 파일을 찾을 인코딩 형식 목록입니다. 인자는 미리 압축된 [사이드카 파일](https://en.wikipedia.org/wiki/Sidecar_file)을 찾기 위해 검색할 인코딩 형식의 순서 있는 목록입니다. 지원되는 형식은 `gzip` (`.gz`), `zstd` (`.zst`), `br` (`.br`)입니다. 형식이 생략되면 기본적으로 `br zstd gzip` 순서로 검색합니다.

  모든 파일 조회는 먼저 압축되지 않은 파일이 존재하는지 확인합니다. 발견되면 Caddy는 활성화된 각 형식의 확장자를 가진 사이드카 파일을 찾습니다. 미리 압축된 사이드카 파일이 발견되면 Caddy는 `Content-Encoding` 응답 헤더를 적절히 설정하여 해당 파일로 응답합니다. 그렇지 않으면 평소와 같이 압축되지 않은 파일로 응답합니다. 만약 [`encode` 지시어](encode)가 활성화되어 있다면, 미리 압축되지 않은 경우 응답을 실시간으로 압축할 수 있습니다.

- **status** <span id="status"/> 는 응답을 작성할 때 사용할 선택적 상태 코드 오버라이드입니다. [사용자 정의 오류 페이지](handle_errors)로 요청에 응답할 때 특히 유용합니다. 3자리 상태 코드(예: `404`)일 수 있으며 플레이스홀더를 지원합니다. 기본적으로 작성되는 상태 코드는 보통 `200`이거나 부분 콘텐츠의 경우 `206`입니다.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> 는 기본 동작인 리다이렉트(요청 경로가 디렉토리면 슬래시 추가, 파일이면 슬래시 제거)를 비활성화합니다. 기본적으로 요청 경로의 마지막 요소(파일명)가 내부 리라이트를 거친 경우, 명시적인 리라이트가 암시적 동작으로 인해 훼손되는 것을 방지하기 위해 표준화가 수행되지 않습니다.

- **pass_thru** <span id="pass_thru"/> 는 패스스루 모드를 활성화합니다. 이 모드에서는 요청된 파일을 찾을 수 없을 때 `404` 오류를 발생시키는([`handle_errors`](handle_errors) 호출) 대신 라우트의 다음 HTTP 핸들러로 계속 진행합니다. 실제로 이는 `file_server` 뒤에 다른 핸들러 지시어가 오는 [`route`](route) 블록 내부에서만 유용합니다. 왜냐하면 이 지시어는 사실상 [마지막 순서](/docs/caddyfile/directives#directive-order)로 배치되기 때문입니다.


## 예시

현재 디렉토리를 기준으로 하는 정적 파일 서버:

```caddy-d
file_server
```

파일 목록 표시 활성화:

```caddy-d
file_server browse
```

`/static` 폴더 내의 정적 파일만 제공:

```caddy-d
file_server /static/*
```

`file_server` 지시어는 보통 파일을 제공할 루트 경로를 설정하기 위해 [`root` 지시어](root)와 함께 사용됩니다:

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Caddy를 systemd 서비스로 실행 중인 경우 `/home`에서 파일을 읽는 것은 작동하지 않을 수 있습니다. `caddy` 사용자에게 `/home` 디렉토리에 대한 "실행(executable)" 권한이 없기 때문입니다(탐색에 필요함). 대신 파일을 `/srv`나 `/var/www/html`에 두는 것을 권장합니다.

</aside>


모든 `.git` 폴더와 그 내용을 숨김:

```caddy-d
file_server {
	hide .git
}
```

클라이언트가 지원하는 경우(`Accept-Encoding` 헤더), 요청된 파일과 함께 미리 압축된 파일이 있는지 확인합니다. 예를 들어 `/path/to/file`이 요청되면 `/path/to/file.br`, `/path/to/file.zst`, `/path/to/file.gz` 순으로 확인하고 첫 번째로 발견된 파일을 해당 `Content-Encoding`과 함께 제공합니다:

```caddy-d
file_server {
	precompressed
}
```
