---
title: Caddy 2로 업그레이드하기
---

업그레이드 가이드
=============

Caddy 2는 Caddy 1을 개선하기 위해 처음부터 다시 작성된 완전히 새로운 코드베이스입니다. Caddy 2는 Caddy 1과 하위 호환되지 않습니다. 하지만 걱정하지 마세요. 대부분의 기본적인 설정에서 크게 달라진 점은 없습니다. 이 가이드는 여러분이 최대한 쉽게 전환할 수 있도록 도와줄 것입니다.

이 가이드에서는 새로운 기능들에 대해 깊이 다루지는 않겠지만, 참고로 말씀드리면 정말 멋진 기능들이 많으니 [한번 알아보세요](/docs/getting-started). 여기서의 목표는 여러분이 Caddy 2를 빠르게 설치하고 실행할 수 있도록 하는 것입니다.

- [고차원적인 변경 사항](#high-order-bits)
- [단계](#steps)
- [HTTPS와 포트](#https-and-ports)
- [명령줄](#command-line)
- [Caddyfile](#caddyfile)
	- [주요 변경 사항](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [서비스 파일](#service-files)
- [플러그인](#plugins)
- [도움말 보기](#getting-help)



## 고차원적인 변경 사항 <a id="high-order-bits"></a>

- "Caddy 2"도 여전히 그냥 `caddy`라고 부릅니다. 전환 과정을 덜 혼란스럽게 만들기 위해 버전을 명확히 해야 할 때 "Caddy 2"라는 표현을 사용할 수 있습니다.
- 대부분의 사용자는 단순히 `caddy` 바이너리를 교체하고 (작동 여부를 테스트한 후) 업데이트된 `Caddyfile` 설정을 사용하면 됩니다.
- Caddy 1에서 가졌던 가정을 버리고 Caddy 2에 접근하는 것이 가장 좋을 수 있습니다.
- v1의 특정 구성을 v2에서 완벽하게 재현하지 못할 수도 있습니다. 보통 거기에는 타당한 이유가 있습니다.
- 명령줄은 더 이상 서버 구성에 사용되지 않습니다.
- 환경 변수는 더 이상 구성에 필요하지 않습니다.
- Caddy 2에 구성을 전달하는 주요 방법은 [API](/docs/api)를 통하는 것이지만, [`caddy` 명령](/docs/command-line)도 사용할 수 있습니다.
- Caddy 2의 기본 구성 언어는 [JSON](/docs/json/)이며, Caddyfile은 단지 JSON으로 변환해 주는 또 다른 [구성 어댑터(config adapter)](/docs/config-adapters)일 뿐이라는 점을 알아두어야 합니다. 매우 복잡하거나 고급 사례의 경우 모든 가능한 구성을 Caddyfile로 표현할 수 없으므로 JSON이 필요할 수 있습니다.
- Caddyfile은 대부분 비슷하지만 훨씬 더 강력해졌으며, 지시어(directives)가 변경되었습니다.



## 단계 <a id="steps"></a>

1. [시작하기](/docs/getting-started) 튜토리얼을 따라 하며 Caddy 2에 익숙해지세요.
2. 아직 하지 않았다면 1단계를 수행하세요. 진심으로요. 적어도 Caddy 2를 어떻게 사용하는지 아는 것이 얼마나 중요한지 아무리 강조해도 지나치지 않습니다. (그게 더 재미있습니다!)
3. 아래 가이드를 사용하여 `caddy` 명령을 전환하세요.
4. 아래 가이드를 사용하여 Caddyfile을 전환하세요.
5. 새로운 구성을 로컬 또는 스테이징 환경에서 테스트하세요.
6. 테스트하고, 테스트하고, 또 테스트하세요.
7. 배포하고 즐기세요!



## HTTPS와 포트 <a id="https-and-ports"></a>

Caddy의 기본 포트는 더 이상 `:2015`가 아닙니다. Caddy 2의 기본 포트는 `:443`이며, 호스트 이름이나 IP를 알 수 없는 경우 포트 `:80`입니다. 구성에서 포트를 언제든지 사용자 정의할 수 있습니다.

Caddy 2의 기본 프로토콜은 [호스트 이름이나 IP가 알려진 경우 *항상* HTTPS](/docs/automatic-https#overview)입니다. 이는 공개적으로 보이는 도메인만 기본적으로 HTTPS를 사용했던 Caddy 1과 다릅니다. 이제 포트 `:80` 또는 `http://`를 명시적으로 지정하여 비활성화하지 않는 한 *모든* 사이트가 HTTPS를 사용합니다.

IP 주소와 localhost 도메인은 [로컬에서 신뢰할 수 있는 내장 CA](/docs/automatic-https#local-https)로부터 인증서를 발급받습니다. 다른 모든 도메인은 ZeroSSL 또는 Let's Encrypt를 사용합니다. (이 모든 것은 구성 가능합니다.)

인증서 및 ACME 리소스의 저장 구조가 변경되었습니다. Caddy 2는 아마도 여러분의 사이트를 위해 새로운 인증서를 가져올 것입니다. 하지만 인증서가 많다면 수동으로 마이그레이션할 수 있습니다. 자세한 내용은 이슈 [#2955](https://github.com/caddyserver/caddy/issues/2955) 및 [#3124](https://github.com/caddyserver/caddy/issues/3124)를 참조하세요.



## 명령줄 <a id="command-line"></a>

`caddy` 명령은 이제 `caddy run`입니다.

모든 명령줄 플래그가 달라졌습니다. 플래그를 제거하세요. 모든 서버 구성은 이제 실제 구성 문서(주로 Caddyfile 또는 JSON) 내에 존재합니다. v1의 대부분의 명령줄 플래그를 대체할 필요한 기능들을 [JSON 구조](/docs/json/) 또는 [Caddyfile 전역 옵션](/docs/caddyfile/options)에서 찾을 수 있을 것입니다.

`caddy -conf ../Caddyfile`과 같은 명령은 `caddy run --config ../Caddyfile`이 됩니다.

이전과 마찬가지로, Caddyfile이 현재 폴더에 있으면 Caddy가 자동으로 찾아 사용하므로, 이 경우에는 `--config` 플래그를 사용할 필요가 없습니다.

시그널은 대부분 동일하지만, USR1 및 USR2는 더 이상 지원되지 않습니다. 대신 [`caddy reload`](/docs/command-line#caddy-reload) 명령이나 [API](/docs/api)를 사용하여 새로운 구성을 로드하세요.

아무런 구성 없이 `caddy`를 실행하면 간단한 파일 서버가 실행되었었습니다. Caddy 2에서의 해당 명령은 [`caddy file-server`](/docs/command-line#caddy-file-server)입니다.

환경 변수는 `HOME`(및 선택적으로 설정한 `XDG_*` 변수)을 제외하고는 더 이상 관련이 없습니다. `CADDYPATH`는 [운영체제 관례](/docs/conventions#file-locations)에 따라 대체되었습니다.



## Caddyfile <a id="caddyfile"></a>

[v2 Caddyfile](/docs/caddyfile/concepts)은 이미 익숙한 것과 매우 유사합니다. 주로 해야 할 일은 지시어를 변경하는 것입니다.

⚠️ **새로운 지시어들을 반드시 읽어보세요!** 특히 구성이 고급일수록 고려해야 할 미묘한 차이점이 많습니다. 이 팁들을 통해 대부분 빠르게 전환할 수 있겠지만, 업그레이드의 영향을 이해할 수 있도록 각 지시어에 대한 전체 문서를 읽어보시기 바랍니다. 그리고 물론, 프로덕션에 적용하기 전에 항상 구성을 철저히 테스트하세요.


### 주요 변경 사항 <a id="primary-changes"></a>

- 정적 파일을 서비스하는 경우, Caddy 2는 이를 기본적으로 가정하지 않으므로 [`file_server` 지시어](/docs/caddyfile/directives/file_server)를 추가해야 합니다. 또한 보안상의 이유로 Caddy 2는 기본적으로 MIME을 감지(sniff)하지 않습니다. Content-Type이 누락된 경우 [header](/docs/caddyfile/directives/header) 지시어를 사용하여 직접 헤더를 설정해야 할 수도 있습니다.

- v1에서는 요청 경로로만 지시어를 필터링(또는 "매칭")할 수 있었습니다. v2에서는 [요청 매칭(request matching)](/docs/caddyfile/matchers)이 훨씬 더 강력해졌습니다. HTTP 핸들러 체인에 미들웨어를 추가하거나 HTTP 요청/응답을 조작하는 모든 v2 지시어는 이 새로운 매칭 기능을 활용합니다. [v2 요청 매처에 대해 더 자세히 읽어보세요.](/docs/caddyfile/matchers) v2 Caddyfile을 이해하려면 이에 대해 알아야 합니다.

- 많은 [플레이스홀더(placeholders)](/docs/conventions#placeholders)가 동일하지만, 많은 것들이 변경되었으며 [Caddyfile용 축약형](/docs/caddyfile/concepts#placeholders)을 포함하여 [많은 새로운 것들](/docs/modules/http#docs)이 추가되었습니다.

- Caddy 2 로그는 모두 구조화되어 있으며, 기본 형식은 JSON입니다. 모든 로그 레벨은 단순히 처리될 동일한 로그로 전달될 수 있습니다 (필요한 경우 이를 사용자 정의할 수 있습니다).

- Caddy 1에서는 경로 접두사(path prefix)로 요청을 매칭했지만, Caddy 2에서는 경로 매칭이 기본적으로 정확히 일치(exact match)해야 합니다. `/foo/`와 같은 접두사를 매칭하려면 Caddy 2에서는 `/foo/*`가 필요합니다.

가장 일반적인 v1 지시어 몇 가지를 나열하고 v2 Caddyfile에서 사용하기 위해 변환하는 방법을 설명합니다.

⚠️ **v1 지시어가 이 페이지에 없다고 해서 v2에서 할 수 없다는 뜻은 아닙니다!** 일부 v1 지시어는 필요하지 않거나, 잘 변환되지 않거나, v2에서 다른 방식으로 충족됩니다. 일부 고급 사용자 정의의 경우 원하는 것을 얻기 위해 JSON으로 내려가야 할 수도 있습니다. 필요한 것을 찾으려면 [저희 문서](/docs/caddyfile)를 탐색해 보세요!


### basicauth <a id="basicauth"></a>

HTTP 기본 인증(Basic Authentication)은 여전히 [`basic_auth`](/docs/caddyfile/directives/basic_auth) 지시어로 구성됩니다. 하지만 Caddy 2 구성은 평문 비밀번호를 허용하지 않습니다. 비밀번호를 해시해야 하며, [`caddy hash-password`](/docs/command-line#caddy-hash-password)가 이를 도와줄 수 있습니다.

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


### browse <a id="browse"></a>

파일 브라우징은 이제 [`file_server`](/docs/caddyfile/directives/file_server) 지시어를 통해 활성화됩니다.

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


### errors <a id="errors"></a>

사용자 정의 에러 페이지는 [`handle_errors`](/docs/caddyfile/directives/handle_errors)로 구현할 수 있습니다.


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

### ext <a id="ext"></a>

암시적 파일 확장자는 [`try_files`](/docs/caddyfile/directives/try_files)로 처리할 수 있습니다.

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


### fastcgi <a id="fastcgi"></a>

PHP를 서비스한다고 가정할 때, v2에서의 해당 지시어는 [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi)입니다.

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

v1의 `fastcgi` 지시어는 디스크의 파일 시도, 요청 재작성, 심지어 리다이렉트까지 내부적으로 많은 작업을 수행했습니다. v2 `php_fastcgi` 지시어도 이러한 작업을 수행하지만, 문서는 요구 사항이 다른 경우 수정할 수 있도록 [확장된 형태](/docs/caddyfile/directives/php_fastcgi#expanded-form)를 제공합니다.

v2에서는 `php_fastcgi` 지시어가 기본적으로 PHP를 가정하므로 `php` 프리셋이 필요하지 않습니다. `php_fastcgi 127.0.0.1:9000 php`와 같은 라인은 역방향 프록시가 `php`라는 두 번째 백엔드가 있다고 생각하게 만들어 연결 오류를 발생시킵니다.

하위 지시어는 v2에서 다르지만, PHP의 경우 아마 필요하지 않을 것입니다.


### gzip <a id="gzip"></a>

이제 단일 지시어 [`encode`](/docs/caddyfile/directives/encode)가 여러 압축 형식을 포함한 모든 응답 인코딩에 사용됩니다.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

흥미로운 사실: Caddy 2는 `zstd`도 지원합니다 (하지만 아직 지원하는 브라우저는 없습니다).


### header <a id="header"></a>

[대부분 변경되지 않았지만](/docs/caddyfile/directives/header), v2에서는 부분 문자열 교체가 가능하므로 훨씬 더 강력해졌습니다.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


### log <a id="log"></a>

액세스 로그를 활성화합니다. [`log`](/docs/caddyfile/directives/log) 지시어는 v2에서도 여전히 사용할 수 있지만, 모든 로그는 기본적으로 JSON으로 인코딩된 구조화된 로그입니다.

액세스 로그를 활성화하는 권장 방법은 단순히 다음과 같습니다:

```caddy-d
log
```

이는 구조화된 로그를 stderr로 출력합니다. (파일이나 네트워크 소켓으로 출력할 수도 있습니다. [`log`](/docs/caddyfile/directives/log) 지시어 문서를 참조하세요.)

기본적으로 로그는 [구조화된](/docs/logging) JSON 형식입니다. 레거시 이유로 여전히 Common Log Format(CLF) 로그가 필요한 경우 [`transform-encoder`](https://github.com/caddyserver/transform-encoder) 플러그인을 사용할 수 있습니다.


### proxy <a id="proxy"></a>

v2에서의 해당 지시어는 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)입니다.

주목할 만한 하위 지시어 변경 사항은 `header_upstream` 및 `header_downstream`이 각각 `header_up` 및 `header_down`이 되었으며, 부하 분산 관련 하위 지시어에는 `lb_` 접두사가 붙습니다.

또 다른 중요한 차이점은 v2 프록시는 기본적으로 들어오는 모든 헤더(`Host` 헤더 포함)를 그대로 전달하고 `X-Forwarded-For` 헤더를 설정한다는 것입니다. 즉, v1의 "transparent" 모드가 v2에서는 기본적으로 적용됩니다 (하지만 X-Real-IP와 같은 다른 헤더가 필요한 경우 직접 설정해야 합니다). `header_up` 하위 지시어를 사용하여 `Host` 헤더를 여전히 덮어쓰거나 사용자 정의할 수 있습니다.

웹소켓 프록시는 v2에서 "그냥 작동"합니다. v1처럼 웹소켓을 "활성화"할 필요가 없습니다.

개선된 매처 지원 덕분에 v2에서는 [재작성 편법(rewrite hacks)](#rewrite)이 더 이상 필요하지 않으므로 `without` 하위 지시어는 제거되었습니다.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


### redir <a id="redir"></a>

선택적 상태 코드 인수에 대한 몇 가지 세부 사항을 제외하고는 [변경되지 않았습니다](/docs/caddyfile/directives/redir). 대부분의 구성은 변경할 필요가 없습니다.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


### rewrite <a id="rewrite"></a>

요청 재작성("내부 리다이렉트")의 의미가 약간 변경되었습니다. 단순한 경로 접두사 이외의 것으로 요청을 매칭하기 위해 v1에서 이른바 "재작성 편법(rewrite hack)"을 사용했다면, v2에서는 완전히 불필요합니다.

[새로운 `rewrite` 지시어](/docs/caddyfile/directives/rewrite)는 매우 단순하지만 매우 강력합니다. 대부분의 복잡한 처리는 v2의 [매처(matchers)](/docs/caddyfile/matchers)가 담당하기 때문입니다:

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

이 지시어에 대해 더 이상 특별한 케이스를 적용하지 않고 Caddy 2의 일반적인 [매처 토큰](/docs/caddyfile/matchers)을 어떻게 사용하는지 주목하세요.

모든 재작성 편법을 제거하는 것부터 시작하세요. 대신 [명명된 매처(named matchers)](/docs/caddyfile/concepts#named-matchers)로 바꾸세요. 각 v1 `rewrite`를 평가하여 v2에서 정말 필요한지 확인하세요. 힌트: 경로 접두사를 추가하기 위해 `rewrite`를 사용한 다음 해당 접두사를 제거하기 위해 `without`과 함께 `proxy`를 사용하는 v1 Caddyfile은 재작성 편법이며 제거할 수 있습니다.

고급 라우팅 로직을 더 잘 제어하기 위해 새로운 [`route`](/docs/caddyfile/directives/route) 및 [`handle`](/docs/caddyfile/directives/handle) 지시어가 유용할 수 있습니다.


### root <a id="root"></a>

[변경되지 않았습니다](/docs/caddyfile/directives/root).

v1에서는 항상 활성화되어 있었지만 Caddy 2는 이를 기본적으로 가정하지 않으므로, 정적 파일을 서비스하는 경우 [`file_server` 지시어](/docs/caddyfile/directives/file_server)를 추가해야 함을 잊지 마세요.


### status <a id="status"></a>

v2에서의 해당 지시어는 [`respond`](/docs/caddyfile/directives/respond)이며, 응답 본문도 작성할 수 있습니다.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


### templates <a id="templates"></a>

[`templates`](/docs/caddyfile/directives/templates) 지시어의 전반적인 구문은 변경되지 않았지만, 실제 템플릿 액션/함수는 다르고 훨씬 개선되었습니다. 예를 들어, 템플릿은 파일 포함, 마크다운 렌더링, 내부 서브 요청 수행, 프론트 매터 파싱 등이 가능합니다!

새로운 기능에 대한 자세한 내용은 [문서](/docs/modules/http.handlers.templates)를 참조하세요.

- **v1:** `templates`
- **v2:** `templates`


### tls <a id="tls"></a>

사용자 정의 인증서와 키를 지정하는 것과 같은 [`tls`](/docs/caddyfile/directives/tls) 지시어의 기본 사항은 변경되지 않았습니다:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

하지만 Caddy의 [자동 HTTPS 로직](/docs/automatic-https)은 변경되었으므로 주의하세요!

암호화 스위트(cipher suite) 이름도 변경되었습니다.

Caddy 2에서의 일반적인 구성은 `tls internal`을 사용하여 `localhost`나 IP 주소가 아닌 개발 호스트 이름에 대해 로컬에서 신뢰할 수 있는 인증서를 서비스하는 것입니다.

대부분의 사이트에는 이 지시어가 전혀 필요하지 않습니다.


## 서비스 파일 <a id="service-files"></a>

Caddy 배포 시 [공식 systemd 서비스 파일 중 하나](/docs/running#linux-service)를 사용하는 것을 권장합니다.

사용자 정의 서비스 파일이 필요한 경우, 저희 파일을 기반으로 작성하세요. 타당한 이유들로 신중하게 튜닝되었습니다! 필요한 경우 직접 사용자 정의하세요.


## 플러그인 <a id="plugins"></a>

v1용으로 작성된 플러그인은 v2와 자동으로 호환되지 않습니다. 많은 v1 플러그인은 v2에서 필요조차 없습니다. 반면에 v2는 v1보다 훨씬 더 쉽게 확장 가능하고 유연합니다!

Caddy 2용 플러그인을 작성하고 싶다면, [Caddy 모듈 작성 방법](/docs/extending-caddy)을 배워보세요.


### 플러그인을 포함하여 Caddy 2 빌드하기 <a id="building-caddy-2-with-plugins"></a>

Caddy 2는 [대화형 다운로드 페이지](/download)에서 플러그인과 함께 다운로드할 수 있습니다. 또는 `xcaddy`를 사용하여 [Caddy를 직접 빌드](/docs/build)하고 포함할 플러그인을 선택할 수 있습니다. `xcaddy`는 Caddy의 [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) 파일에 있는 지침을 자동화합니다.


## 도움말 보기 <a id="getting-help"></a>

Caddy를 작동시키는 데 어려움을 겪고 있다면 먼저 저희 웹사이트의 문서를 살펴보시기 바랍니다. 새로운 것들을 시도하고 무슨 일이 일어나고 있는지 이해하는 시간을 가져보세요 - v2는 여러 방면에서 v1과 매우 다르지만(동시에 매우 친숙하기도 합니다)!

여전히 도움이 필요하다면 [저희 커뮤니티](https://caddy.community)의 일원이 되어주세요! 다른 사람을 돕는 것이 자신을 돕는 가장 좋은 방법이기도 하다는 것을 알게 될 것입니다.
