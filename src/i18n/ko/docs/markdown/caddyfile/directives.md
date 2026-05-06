---
title: Caddyfile 지시어
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

# Caddyfile 지시어

지시어(Directives)는 사이트 [블록](/docs/caddyfile/concepts#blocks) 내에 나타나는 기능적 키워드입니다. 때때로 지시어는 *하위 지시어(subdirectives)*를 포함할 수 있는 자체 블록을 열 수 있지만, 별도로 명시되지 않는 한 지시어는 다른 지시어 내에서 사용할 수 **없습니다**. 예를 들어, `file_server`는 인증 방법을 모르기 때문에 `file_server` 블록 내에서 `basic_auth`를 사용할 수 없습니다. 하지만 `handle`이나 `route`와 같은 특수 지시어 블록은 HTTP 핸들러 지시어를 그룹화하도록 특별히 설계되었으므로 그 안에서 일부 지시어를 사용할 수 *있습니다*.

- [구문](#syntax)
- [지시어 순서](#directive-order)
- [정렬 알고리즘](#sorting-algorithm)

다음 지시어들은 Caddy에 기본으로 포함되어 있으며 HTTP Caddyfile에서 사용할 수 있습니다:

<div id="directive-table">

지시어 | 설명
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | HTTP 요청을 중단합니다
**[acme_server](/docs/caddyfile/directives/acme_server)** | 내장된 ACME 서버입니다
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | HTTP 기본 인증을 강제합니다
**[bind](/docs/caddyfile/directives/bind)** | 서버의 소켓 주소를 정의합니다
**[encode](/docs/caddyfile/directives/encode)** | 응답을 인코딩(주로 압축)합니다
**[error](/docs/caddyfile/directives/error)** | 오류를 발생시킵니다
**[file_server](/docs/caddyfile/directives/file_server)** | 디스크의 파일을 서비스합니다
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | 외부 서비스에 인증을 위임합니다
**[fs](/docs/caddyfile/directives/fs)** | 파일 I/O에 사용할 파일 시스템을 설정합니다
**[handle](/docs/caddyfile/directives/handle)** | 상호 배타적인 지시어 그룹을 정의합니다
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | 오류 처리를 위한 라우트를 정의합니다
**[handle_path](/docs/caddyfile/directives/handle_path)** | handle과 유사하지만 경로 접두사를 제거합니다
**[header](/docs/caddyfile/directives/header)** | 응답 헤더를 설정하거나 제거합니다
**[import](/docs/caddyfile/directives/import)** | 스니펫이나 파일을 포함합니다
**[intercept](/docs/caddyfile/directives/intercept)** | 다른 핸들러가 작성한 응답을 가로챕니다
**[invoke](/docs/caddyfile/directives/invoke)** | 명명된 라우트를 호출합니다
**[log](/docs/caddyfile/directives/log)** | 액세스/요청 로깅을 활성화합니다
**[log_append](/docs/caddyfile/directives/log_append)** | 액세스 로그에 필드를 추가합니다
**[log_skip](/docs/caddyfile/directives/log_skip)** | 일치하는 요청에 대해 액세스 로깅을 건너뜁니다
**[log_name](/docs/caddyfile/directives/log_name)** | 로그를 기록할 로거 이름을 재정의합니다
**[map](/docs/caddyfile/directives/map)** | 입력 값을 하나 이상의 출력 값으로 매핑합니다
**[method](/docs/caddyfile/directives/method)** | 내부적으로 HTTP 메서드를 변경합니다
**[metrics](/docs/caddyfile/directives/metrics)** | Prometheus 메트릭 엔드포인트를 구성합니다
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | FastCGI를 통해 PHP 사이트를 서비스합니다
**[push](/docs/caddyfile/directives/push)** | HTTP/2 서버 푸시를 사용하여 클라이언트에 콘텐츠를 푸시합니다
**[redir](/docs/caddyfile/directives/redir)** | 클라이언트에 HTTP 리다이렉트를 보냅니다
**[request_body](/docs/caddyfile/directives/request_body)** | 요청 본문을 조작합니다
**[request_header](/docs/caddyfile/directives/request_header)** | 요청 헤더를 조작합니다
**[respond](/docs/caddyfile/directives/respond)** | 클라이언트에 고정된 응답을 작성합니다
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | 강력하고 확장 가능한 역방향 프록시입니다
**[rewrite](/docs/caddyfile/directives/rewrite)** | 내부적으로 요청을 재작성합니다
**[root](/docs/caddyfile/directives/root)** | 사이트 루트 경로를 설정합니다
**[route](/docs/caddyfile/directives/route)** | 하나의 단위로 취급되는 지시어 그룹입니다
**[templates](/docs/caddyfile/directives/templates)** | 응답에 대해 템플릿을 실행합니다
**[tls](/docs/caddyfile/directives/tls)** | TLS 설정을 사용자 정의합니다
**[tracing](/docs/caddyfile/directives/tracing)** | OpenTelemetry 트레이싱과 통합합니다
**[try_files](/docs/caddyfile/directives/try_files)** | 파일 존재 여부에 따른 재작성을 수행합니다
**[uri](/docs/caddyfile/directives/uri)** | URI를 조작합니다
**[vars](/docs/caddyfile/directives/vars)** | 임의의 변수를 설정합니다

</div>

## 구문 <a id="syntax"></a>

각 지시어의 구문은 다음과 같은 형식입니다:

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

`<꺽쇠 괄호>`는 실제 값으로 대체될 토큰을 나타냅니다.

`[대괄호]`는 선택적 매개변수를 나타냅니다.

말줄임표 `...`는 하나 이상의 매개변수나 줄이 올 수 있음을 나타냅니다.

하위 지시어는 별도로 명시되지 않는 한 보통 `[대괄호]` 안에 없더라도 선택 사항입니다.


### 매처 <a id="matchers"></a>

대부분의(전부는 아님) 지시어는 요청을 필터링할 수 있는 [매처 토큰](/docs/caddyfile/matchers#syntax)을 허용합니다. 매처 토큰은 보통 선택 사항입니다. 지시어 구문에 다음과 같은 내용이 보인다면 해당 지시어는 매처를 지원하는 것입니다:

```caddy-d
[<matcher>]
```

모든 매처 토큰은 동일하게 작동하므로, 중복을 피하기 위해 각 페이지에서 모든 가능성을 설명하지는 않습니다. 대신 구문에 대한 자세한 설명은 [매처 문서](/docs/caddyfile/matchers)를 참조하세요.


## 지시어 순서 <a id="directive-order"></a>

많은 지시어가 HTTP 핸들러 체인을 조작합니다. 이러한 지시어가 평가되는 순서가 중요하므로, Caddy에는 기본 순서가 하드코딩되어 있습니다.

[`order` 전역 옵션](/docs/caddyfile/options#order)이나 [`route` 지시어](/docs/caddyfile/directives/route)를 사용하여 이 순서를 재정의하거나 사용자 정의할 수 있습니다.

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # reverse_proxy의 handle_response 블록에서만 사용
request_body

redir

# 들어오는 요청 조작
method
rewrite
uri
try_files

# 미들웨어 핸들러; 일부는 응답을 감쌉니다
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# 특수 라우팅 및 디스패칭 지시어
invoke
handle
handle_path
route

# 보통 요청에 응답하는 핸들러
abort
error
copy_response # reverse_proxy의 handle_response 블록에서만 사용
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



## 정렬 알고리즘 <a id="sorting-algorithm"></a>

사용 편의를 위해 Caddyfile 어댑터는 다음 규칙에 따라 지시어를 정렬합니다:

- 서로 다른 이름의 지시어는 [기본 순서](#directive-order)의 위치에 따라 정렬됩니다. 기본 순서는 [`order` 전역 옵션](/docs/caddyfile/options)으로 재정의할 수 있습니다. 플러그인 지시어는 순서가 *없으므로*, [`order`](/docs/caddyfile/options) 전역 옵션이나 [`route`](/docs/caddyfile/directives/route) 지시어를 사용하여 순서를 설정해야 합니다.

- 이름이 같은 지시어는 해당 [매처(matchers)](/docs/caddyfile/matchers#syntax)에 따라 정렬됩니다.

  - 가장 높은 우선순위는 단일 [경로 매처(path matcher)](/docs/caddyfile/matchers#path-matchers)를 가진 지시어입니다.

    경로 매처는 가장 구체적인 것부터 덜 구체적인 것 순으로 정렬됩니다.
	
	일반적으로 이는 경로 매처의 길이에 따라 정렬됩니다. 한 가지 예외는 경로가 `*`로 끝나고 두 매처의 경로가 그 외에 동일한 경우, `*`가 없는 매처가 더 구체적인 것으로 간주되어 더 높게 정렬됩니다.

    예:
    - `/foobar`는 `/foo`보다 구체적임
    - `/foo`는 `/foo*`보다 구체적임
    - `/foo/*`는 `/foo*`보다 구체적임

  - 다른 모든 매처를 가진 지시어는 Caddyfile에 나타나는 순서대로 그다음에 정렬됩니다.

    여기에는 여러 값을 가진 경로 매처와 [명명된 매처(named matchers)](/docs/caddyfile/matchers#named-matchers)가 포함됩니다.

  - 매처가 없는(즉, 모든 요청과 일치하는) 지시어는 마지막에 정렬됩니다.

- [`vars`](/docs/caddyfile/directives/vars) 지시어는 매처에 의한 정렬 순서가 반대입니다. 왜냐하면 서로 덮어쓸 수 있는 값을 설정하는 작업이 포함되므로 가장 구체적인 매처가 마지막에 평가되어야 하기 때문입니다.

- [`route`](/docs/caddyfile/directives/route) 지시어의 내용은 위의 모든 규칙을 무시하고 내부의 지시어가 나타나는 순서를 그대로 유지합니다.
