---
title: Caddyfile 튜토리얼
---

# Caddyfile 튜토리얼

이 튜토리얼에서는 멋지고 기능적인 사이트 구성을 빠르고 쉽게 생성할 수 있도록 [HTTP Caddyfile](/docs/caddyfile)의 기본 사항을 가르쳐 드립니다.

**목표:**
- 🔲 첫 번째 사이트
- 🔲 정적 파일 서버
- 🔲 템플릿
- 🔲 압축
- 🔲 여러 사이트
- 🔲 매처(Matchers)
- 🔲 환경 변수
- 🔲 주석

**사전 준비 사항:**
- 기본적인 터미널 / 명령줄 기술
- 기본적인 텍스트 편집기 기술
- PATH에 `caddy` 포함

---

`Caddyfile`이라는 이름의 새 텍스트 파일(확장자 없음)을 만듭니다.

가장 먼저 입력해야 할 것은 사이트의 [주소](/docs/caddyfile/concepts#addresses)입니다:

```caddy
localhost
```

<aside class="tip">

운영 체제에서 HTTP 및 HTTPS 포트(각각 80 및 443)가 권한이 필요한 포트(privileged ports)인 경우, 상승된 권한으로 실행하거나 더 높은 포트를 사용해야 합니다. 더 높은 포트를 사용하려면 주소를 `localhost:2015`와 같이 변경하고 [http_port](/docs/caddyfile/options) Caddyfile 옵션을 사용하여 HTTP 포트를 변경하면 됩니다.

</aside>


그런 다음 Enter 키를 누르고 수행할 작업을 입력합니다. 이 튜토리얼에서는 Caddyfile을 다음과 같이 만듭니다:

```caddy
localhost

respond "Hello, world!"
```

저장하고 Caddy를 실행합니다(이것은 교육용 튜토리얼이므로 `--watch` 플래그를 사용하여 Caddyfile에 대한 변경 사항이 자동으로 적용되도록 합니다):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

권한 오류가 발생하면 주소에서 더 높은 포트(예: `localhost:2015`)를 사용하고 [HTTP 포트를 변경](/docs/caddyfile/options)하거나, 상승된 권한으로 실행해 보세요.

</aside>


처음에는 암호를 묻는 메시지가 표시됩니다. 이것은 Caddy가 HTTPS를 통해 사이트를 서비스할 수 있도록 하기 위함입니다.

<aside class="tip">

Caddy는 호스트 또는 IP가 사이트 주소의 일부인 한 기본적으로 HTTPS를 통해 모든 사이트를 서비스합니다. [자동 HTTPS](/docs/automatic-https)는 주소 앞에 `http://`를 명시적으로 접두사로 붙여 비활성화할 수 있습니다.

</aside>


<aside class="complete">첫 번째 사이트</aside>

브라우저에서 [localhost](https://localhost)를 열고 완전한 HTTPS와 함께 웹 서버가 작동하는지 확인하세요!

<aside class="tip">
	처음에 인증서 오류가 발생하면 브라우저를 다시 시작해야 할 수도 있습니다.
</aside>

이것은 특별히 흥미롭지 않으므로, 정적 응답을 디렉터리 목록이 활성화된 [파일 서버](/docs/caddyfile/directives/file_server)로 변경해 보겠습니다:

```caddy
localhost

file_server browse
```

Caddyfile을 저장한 다음 브라우저 탭을 새로 고침하세요. 파일 목록이나 현재 디렉터리에 인덱스 파일이 있는 경우 HTML 페이지가 표시되어야 합니다.

<aside class="complete">정적 파일 서버</aside>

## <a id="adding-functionality"></a>기능 추가

파일 서버로 흥미로운 작업을 해 보겠습니다. 템플릿 페이지를 서비스하는 것입니다. 새 파일을 만들고 다음을 붙여넣으세요:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

이것을 현재 디렉터리에 `caddy.html`로 저장하고 브라우저에서 로드하세요: [https://localhost/caddy.html](https://localhost/caddy.html)

출력은 다음과 같습니다:

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

잠깐만요. 오늘 날짜가 표시되어야 합니다. 왜 작동하지 않았을까요? 서버가 아직 템플릿을 평가하도록 구성되지 않았기 때문입니다! 고치기는 쉽습니다. Caddyfile에 한 줄을 추가하여 다음과 같이 만드세요:

```caddy
localhost

templates
file_server browse
```

저장한 다음 브라우저 탭을 다시 로드하세요. 다음과 같이 표시되어야 합니다:

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Caddy의 [템플릿 모듈](/docs/modules/http.handlers.templates)을 사용하면 다른 HTML 파일 포함, 하위 요청(sub-requests) 수행, 응답 헤더 설정, 데이터 구조 작업 등 정적 파일로 많은 유용한 작업을 수행할 수 있습니다!

<aside class="complete">템플릿</aside>

빠르고 현대적인 압축 알고리즘으로 응답을 압축하는 것은 좋은 관행입니다. [`encode`](/docs/caddyfile/directives/encode) 지시문을 사용하여 Gzip 및 Zstandard 지원을 활성화해 보겠습니다:

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">압축</aside>

이것이 반-고급의(semi-advanced), 프로덕션 준비가 완료된 사이트를 시작하고 실행하는 기본 프로세스입니다!

[자동 HTTPS](/docs/automatic-https)를 켤 준비가 되면 사이트의 주소(튜토리얼의 `localhost`)를 도메인 이름으로 바꾸기만 하면 됩니다. 자세한 내용은 [HTTPS 빠른 시작 가이드](/docs/quick-starts/https)를 참조하세요.

## <a id="multiple-sites"></a>여러 사이트

현재 Caddyfile로는 하나의 사이트 정의만 가질 수 있습니다! 첫 번째 줄만 사이트의 주소가 될 수 있고, 파일의 나머지 부분은 모두 해당 사이트에 대한 지시문이어야 합니다.

하지만 더 많은 사이트를 추가할 수 있도록 쉽게 만들 수 있습니다!

지금까지의 Caddyfile:

```caddy
localhost

encode
templates
file_server browse
```

이것은 다음 파일과 같습니다:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

두 번째 파일은 더 많은 사이트를 추가할 수 있다는 점만 다릅니다.

사이트 블록을 중괄호 `{ }`로 묶으면 동일한 Caddyfile에서 여러 개의 서로 다른 사이트를 정의할 수 있습니다.

예를 들어:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

사이트 블록을 중괄호로 묶을 때 [주소](/docs/caddyfile/concepts#addresses)만 중괄호 바깥에 나타나고 [지시문](/docs/caddyfile/directives)만 중괄호 안쪽에 나타납니다.

동일한 구성을 공유하는 여러 사이트의 경우 주소를 더 추가할 수 있습니다. 예:

```caddy
:8080, :8081 {
	...
}
```

각 주소가 고유하기만 하다면 원하는 만큼 많은 다른 사이트를 정의할 수 있습니다.

<aside class="complete">여러 사이트</aside>


## <a id="matchers"></a>매처(Matchers)

일부 지시문을 특정 요청에만 적용하고 싶을 수 있습니다. 예를 들어, 파일 서버와 역방향 프록시를 모두 가지고 싶다고 가정해 보겠습니다. 하지만 명백히 모든 요청에서 둘 다 수행할 수는 없습니다! 파일 서버가 정적 파일로 응답을 쓰거나, 역방향 프록시가 요청을 백엔드로 전달하고 응답을 다시 씁니다.

이 구성은 우리가 원하는 대로 작동하지 않습니다(`reverse_proxy`가 [지시문 순서(directive order)](/docs/caddyfile/directives#directive-order)로 인해 우선순위를 가집니다):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

실제로 역방향 프록시는 API 요청, 즉 기본 경로가 `/api/`인 요청에만 사용하고 싶을 수 있습니다. 이것은 [매처 토큰(matcher token)](/docs/caddyfile/matchers#syntax)을 추가하여 쉽게 수행할 수 있습니다:

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

이제 `/api/`로 시작하는 모든 요청에 대해 역방향 프록시가 우선순위를 갖습니다.

방금 추가한 `/api/*` 부분을 **매처 토큰**이라고 합니다. 슬래시 `/`로 시작하고 지시문 바로 뒤에 오기 때문에 매처 토큰인지 알 수 있습니다(확실히 하기 위해 항상 [지시문의 문서](/docs/caddyfile/directives)에서 찾을 수 있습니다).

매처는 정말 강력합니다. 명명된 매처(named matchers)를 선언하고 이를 `@name`과 같이 사용하여 요청 경로뿐만 아니라 그 이상의 것과 일치시킬 수 있습니다! 계속하기 전에 잠시 시간을 내어 [매처에 대해 자세히 알아보세요](/docs/caddyfile/matchers)!

<aside class="complete">매처</aside>

## <a id="environment-variables"></a>환경 변수

Caddyfile 어댑터는 Caddyfile이 구문 분석되기 전에 [환경 변수](/docs/caddyfile/concepts#environment-variables)를 대체할 수 있게 해줍니다.

먼저 (Caddy를 실행하는 동일한 셸에서) 환경 변수를 설정합니다:

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

그런 다음 Caddyfile에서 다음과 같이 사용할 수 있습니다:

```caddy
{$SITE_ADDRESS}

file_server
```

Caddyfile이 구문 분석되기 전에 다음과 같이 확장됩니다:

```caddy
localhost:9055

file_server
```

모든 수의 토큰에 대해 Caddyfile의 어느 곳에서나 환경 변수를 사용할 수 있습니다.

<aside class="complete">환경 변수</aside>


## <a id="comments"></a>주석

가장 도움이 될 마지막 한 가지: Caddyfile에 무언가를 기록하거나 메모하려면 `#`으로 시작하는 주석을 사용할 수 있습니다:

```caddy
# 이 줄은 주석입니다
```

<aside class="complete">주석</aside>

## <a id="further-reading"></a>추가 읽을거리

- [Caddyfile 개념](/docs/caddyfile/concepts)
- [지시문](/docs/caddyfile/directives)
- [일반적인 패턴](/docs/caddyfile/patterns)
