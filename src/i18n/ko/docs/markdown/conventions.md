---
title: 관례
---

# 관례

Caddy 생태계는 플랫폼 전반에서 일관되고 직관적인 환경을 제공하기 위해 몇 가지 관례를 준수합니다.


- [네트워크 주소](#network-addresses)
- [플레이스홀더](#placeholders)
- [파일 위치](#file-locations)
  - [데이터 디렉터리](#data-directory)
  - [구성 디렉터리](#configuration-directory)
- [기간](#durations)



## <a id="network-addresses"></a>네트워크 주소

전화(dial)하거나 바인딩할 네트워크 주소를 지정할 때, Caddy는 다음과 같은 형식의 문자열을 허용합니다:

```
network/address
```

네트워크 부분은 선택 사항이며(기본값은 `tcp`), [Go의 `net.Dial` 함수](https://pkg.go.dev/net#Dial)가 인식하는 모든 것을 사용할 수 있습니다. 네트워크가 지정된 경우, 슬래시(`/`) 하나로 네트워크와 주소 부분을 구분해야 합니다.

네트워크는 다음 중 하나일 수 있습니다. `4` 또는 `6`이 접미사로 붙은 것은 각각 IPv4 또는 IPv6 전용을 의미합니다:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

주소 부분은 다음 중 어떤 형식이든 될 수 있습니다:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

호스트는 호스트 이름, 해석 가능한 도메인 이름 또는 IP 주소일 수 있습니다.

IPv6 주소의 경우, 주소는 대괄호 `[]`로 묶어야 합니다. 영역 식별자(`%`로 시작)는 선택 사항입니다(주로 링크-로컬 주소에 사용됨).

포트는 단일 값(`:8080`) 또는 포함 범위를 나타내는 범위(`:8080-8085`)일 수 있습니다. 포트 범위는 단일 주소들로 배가됩니다. 모든 구성 필드가 포트 범위를 허용하는 것은 아닙니다. 특수 포트 `:0`은 사용 가능한 모든 포트를 의미합니다.

유닉스 소켓 경로는 `unix*` 네트워크 유형을 사용할 때만 허용됩니다. 네트워크와 주소를 구분하는 슬래시는 경로의 일부로 간주되지 않습니다.

유닉스 소켓이 바인드 주소로 사용되는 경우, 파이프(`|`)로 구분하여 경로 뒤에 파일 권한 모드를 선택적으로 지정할 수 있습니다. 기본값은 `0200`(8진수), 즉 `u=w,g=,o=`(기호)입니다. 앞의 `0`은 선택 사항입니다.

유효한 예시:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Caddy 네트워크 주소는 URL이 아닙니다. URL은 [OSI 모델 <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture)의 하위 계층과 상위 계층을 결합하지만, Caddy는 종종 특정 어플리케이션과 독립적으로 네트워크 주소를 사용하므로 이를 결합하면 문제가 발생할 수 있습니다. Caddy에서 네트워크 주소는 L3-L5에서 전화하거나 바인딩할 수 있는 리소스를 정확히 가리키지만, URL은 L3-L7을 결합하므로 너무 방대합니다. 네트워크 주소는 호스트+포트와 경로가 상호 배타적이어야 하지만 URL은 그렇지 않습니다. 네트워크 주소는 때때로 포트 범위를 지원하지만 URL은 지원하지 않습니다.

</aside>




## <a id="placeholders"></a>플레이스홀더

Caddy 구성은 *플레이스홀더(placeholders)* 사용을 지원합니다. 플레이스홀더를 사용하는 것은 정적 구성에 동적인 값을 주입하는 간단한 방법입니다.

<aside class="tip">

플레이스홀더는 다른 소프트웨어의 변수와 유사한 개념입니다. 예를 들어 [nginx에는 `$uri` 및 `$document_root`와 같은 변수 <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html)가 있으며, Caddy의 해당 요소는 [`{http.request.uri}`](/docs/json/apps/http/#docs) 및 [`{http.vars.root}`](/docs/caddyfile/directives/root)입니다.

</aside>


플레이스홀더는 양쪽이 중괄호 `{ }`로 묶여 있으며 그 안에 식별자가 포함됩니다(예: `{foo.bar}`). 여는 중괄호는 이스케이프(`\{like.this}`)하여 치환을 방지할 수 있습니다. 플레이스홀더 식별자는 일반적으로 모듈 간의 충돌을 피하기 위해 점으로 구분된 네임스페이스를 가집니다.

어떤 플레이스홀더를 사용할 수 있는지는 문맥에 따라 다릅니다. 모든 플레이스홀더가 구성의 모든 부분에서 사용 가능한 것은 아닙니다. 예를 들어, [HTTP 앱은 HTTP 요청 처리와 관련된 구성 영역에서만 사용할 수 있는 플레이스홀더를 설정합니다](/docs/json/apps/http/#docs). 요청이 [`reverse_proxy` 핸들러](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs)를 통과할 때, 핸들러는 몇 가지 프록시 전용 플레이스홀더를 설정합니다. 이러한 플레이스홀더는 프록싱 중에는 물론 그 이후(`handle_response` 등)에도 참조할 수 있으며, 예를 들어 응답 헤더를 설정하거나 액세스 로그를 보강할 때 사용됩니다.

다음 플레이스홀더는 항상 사용 가능합니다 (글로벌):

플레이스홀더 | 설명
------------|-------------
`{env.*}` | 환경 변수; 예: `{env.HOME}`
`{file.*}` | 파일의 내용; 예: `{file./path/to/secret.txt}`
`{system.hostname}` | 시스템의 로컬 호스트 이름
`{system.slash}` | 시스템의 파일 경로 구분자
`{system.os}` | 시스템의 운영 체제(OS)
`{system.arch}` | 시스템의 아키텍처
`{system.wd}` | 현재 작업 디렉터리
`{time.now}` | Go Time 구조체 형태의 현재 시간
`{time.now.http}` | [HTTP 헤더 <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)에서 사용되는 형식의 현재 시간
`{time.now.unix}` | 초 단위 유닉스 타임스탬프 형식의 현재 시간
`{time.now.unix_ms}` | 밀리초 단위 유닉스 타임스탬프 형식의 현재 시간
`{time.now.common_log}` | 공통 로그 형식(Common Log Format)의 현재 시간
`{time.now.year}` | YYYY 형식의 현재 연도

모든 구성 필드가 플레이스홀더를 지원하는 것은 아니지만, 예상되는 대부분의 위치에서 지원합니다. 플레이스홀더 지원은 해당 필드에 명시적으로 추가되어야 합니다. 플러그인 개발자는 [이 문서](/docs/extending-caddy/placeholders)를 읽고 자신의 모듈에 플레이스홀더 지원을 추가하는 방법을 배울 수 있습니다.




## <a id="file-locations"></a>파일 위치

이 섹션에는 다양한 파일을 찾을 수 있는 위치에 대한 정보가 포함되어 있습니다. 여기에 설명된 파일 및 디렉터리 경로는 기본값일 뿐이며, 일부는 재정의할 수 있습니다.

### <a id="your-config-files"></a>사용자의 구성 파일

구성 파일을 보관하는 관례적인 단일 위치는 없습니다. 사용자에게 가장 적합한 위치에 보관하세요.

<aside class="tip">

이에 대한 유일한 예외는 현재 작업 디렉터리에 있는 `Caddyfile`이라는 이름의 파일일 수 있습니다. 다른 구성 파일이 지정되지 않은 경우 caddy 명령이 편의를 위해 이 파일을 시도합니다.

</aside>


기본 구성 파일과 함께 제공되는 배포판은 패키지/배포판 유지 관리자에게는 명확하더라도 이 구성 파일의 위치를 문서화해야 합니다. 대부분의 Linux 설치의 경우, Caddyfile은 `/etc/caddy/Caddyfile`에서 찾을 수 있습니다.


### <a id="data-directory"></a>데이터 디렉터리

Caddy는 [구성된 스토리지 모듈](/docs/json/storage/)(기본값: 로컬 파일 시스템)에 의해 뒷받침되는 데이터 디렉터리에 TLS 인증서와 기타 중요한 자산을 저장합니다.

`XDG_DATA_HOME` 환경 변수가 설정된 경우, 위치는 `$XDG_DATA_HOME/caddy`입니다.

그렇지 않으면 운영 체제 관례에 따라 플랫폼마다 경로가 다릅니다:

운영 체제 | 데이터 디렉터리 경로
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (또는 `/sdcard/caddy`)

다른 모든 OS는 Linux/BSD 디렉터리 경로를 사용합니다.

**데이터 디렉터리는 캐시로 취급되어서는 안 됩니다.** 이곳의 내용은 휘발성이 아니며 단순히 성능만을 위한 것도 아닙니다. Caddy는 TLS 인증서, 개인 키, OCSP 스테이플 및 기타 필요한 정보를 데이터 디렉터리에 저장합니다. 그 영향을 이해하지 못한 채 내용을 삭제해서는 안 됩니다.

이 디렉터리가 영구적이고 Caddy에 의해 쓰기 가능해야 한다는 점이 매우 중요합니다.


### <a id="configuration-directory"></a>구성 디렉터리

이곳은 Caddy가 특정 구성을 디스크에 저장할 수 있는 위치입니다. 특히, 나중에 [`caddy run --resume`](/docs/command-line#caddy-run)을 사용하여 쉽게 재개할 수 있도록 마지막 활성 구성을 (기본적으로) 이 폴더에 보관합니다.

<aside class="tip">

구성 디렉터리는 [사용자의 구성 파일](#your-config-files)을 저장해야 하는 곳은 아닙니다. (물론 저장할 수는 있습니다.)

</aside>


`XDG_CONFIG_HOME` 환경 변수가 설정된 경우, 위치는 `$XDG_CONFIG_HOME/caddy`입니다.

그렇지 않으면 운영 체제 관례에 따라 플랫폼마다 경로가 다릅니다:


운영 체제 | 구성 디렉터리 경로
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

다른 모든 OS는 Linux/BSD 디렉터리 경로를 사용합니다.

이 디렉터리가 영구적이고 Caddy에 의해 쓰기 가능해야 한다는 점이 매우 중요합니다.


## <a id="durations"></a>기간

기간(Duration) 문자열은 Caddy 구성 전반에서 흔히 사용됩니다. 이들은 [Go의 `time.ParseDuration` 구문](https://golang.org/pkg/time/#ParseDuration)과 동일한 형식을 따르지만, 일(day)을 의미하는 `d`도 사용할 수 있습니다(단순함을 위해 1일 = 24시간으로 가정합니다). 유효한 단위는 다음과 같습니다:

- `ns` (nanosecond)
- `us`/`µs` (microsecond)
- `ms` (millisecond)
- `s` (second)
- `m` (minute)
- `h` (hour)
- `d` (day)

예시:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

[JSON 구성](/docs/json/)에서 기간 값은 나노초를 나타내는 정수일 수도 있습니다.
