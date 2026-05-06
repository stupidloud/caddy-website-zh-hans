---
title: "자동 HTTPS"
---

# 자동 HTTPS

**Caddy는 HTTPS를 자동으로, 그리고 *기본적으로* 사용한 최초의 웹 서버입니다.**

자동 HTTPS는 모든 사이트에 대한 TLS 인증서를 프로비저닝하고 갱신을 유지합니다. 또한 HTTP를 HTTPS로 자동으로 리디렉션해 줍니다! Caddy는 안전하고 현대적인 기본 설정을 사용하며, 다운타임, 추가 구성 또는 별도의 도구가 필요하지 않습니다.

<aside class="tip">
	Caddy는 자동 HTTPS 기술을 혁신했습니다. 우리는 이것이 가능해진 2015년 첫날부터 이 작업을 수행해 왔습니다. Caddy의 HTTPS 자동화 로직은 세계에서 가장 성숙하고 강력합니다.
</aside>

작동 방식을 보여주는 28초 분량의 영상입니다:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**메뉴:**

- [개요](#overview)
- [활성화](#activation)
- [효과](#effects)
- [호스트 이름 요구 사항](#hostname-requirements)
- [로컬 HTTPS](#local-https)
- [테스트](#testing)
- [ACME 챌린지](#acme-challenges)
- [온디맨드 TLS](#on-demand-tls)
- [오류](#errors)
- [스토리지](#storage)
- [와일드카드 인증서](#wildcard-certificates)
- [암호화된 ClientHello (ECH)](#encrypted-clienthello-ech)



## <a id="overview"></a>개요

**기본적으로 Caddy는 모든 사이트를 HTTPS를 통해 서비스합니다.**

- Caddy는 자동으로 로컬에서 신뢰되는(허용되는 경우) 자체 서명된 인증서를 사용하여 IP 주소와 로컬/내부 호스트 이름을 HTTPS로 서비스합니다.
	- 예: `localhost`, `127.0.0.1`
- Caddy는 [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) 또는 [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com)과 같은 공인 ACME CA의 인증서를 사용하여 공인 DNS 이름을 HTTPS로 서비스합니다.
	- 예: `example.com`, `sub.example.com`, `*.example.com`

Caddy는 관리되는 모든 인증서를 최신 상태로 갱신하고, HTTP(기본 포트 `80`)를 HTTPS(기본 포트 `443`)로 자동 리디렉션합니다.

**로컬 HTTPS의 경우:**

- Caddy는 고유한 루트 인증서를 신뢰 저장소에 설치하기 위해 비밀번호를 요청할 수 있습니다. 이는 루트당 한 번만 발생하며 언제든지 제거할 수 있습니다.
- Caddy의 루트 CA 인증서를 신뢰하지 않고 사이트에 접속하는 모든 클라이언트는 보안 오류가 표시됩니다.

**공인 도메인 이름의 경우:**

<aside class="tip">

이는 Caddy뿐만 아니라 모든 기본적인 운영 웹사이트에 대한 일반적인 요구 사항입니다. 주요 차이점은 Caddy가 인증서를 프로비저닝할 수 있도록 실행 **전**에 DNS 레코드를 올바르게 설정하는 것입니다.

</aside>


- 도메인의 A/AAAA 레코드가 서버를 가리키고,
- 외부에서 `80` 및 `443` 포트가 열려 있고,
- Caddy가 해당 포트에 바인딩할 수 있거나(또는 해당 포트가 Caddy로 포워딩되는 경우),
- [데이터 디렉터리](/docs/conventions#data-directory)가 쓰기 가능하고 영구적이며,
- 도메인 이름이 설정의 관련 위치에 나타나면,

사이트는 자동으로 HTTPS를 통해 서비스됩니다. 다른 조치를 취할 필요가 없습니다. 그냥 작동합니다!

HTTPS는 공유된 공공 인프라를 활용하므로, 서버 관리자는 이 페이지의 나머지 정보를 이해하여 불필요한 문제를 방지하고, 문제가 발생했을 때 문제를 해결하며, 고급 배포를 적절하게 구성해야 합니다.



## <a id="activation"></a>활성화

Caddy는 서비스 중인 도메인 이름(즉, 호스트 이름) 또는 IP 주소를 알게 되면 암묵적으로 자동 HTTPS를 활성화합니다. Caddy를 실행하거나 구성하는 방식에 따라 Caddy에 도메/IP를 알리는 여러 가지 방법이 있습니다:

- [Caddyfile](/docs/caddyfile)의 [사이트 주소](/docs/caddyfile/concepts#addresses)
- [JSON 경로](/docs/modules/http#servers/routes) 최상위 수준의 [호스트 매처(host matcher)](/docs/json/apps/http/servers/routes/match/host/)
- [`--domain`](/docs/command-line#caddy-file-server) 또는 [`--from`](/docs/command-line#caddy-reverse-proxy)과 같은 명령줄 플래그
- [automate](/docs/json/apps/tls/certificates/automate/) 인증서 로더

다음 중 어느 하나라도 해당되면 자동 HTTPS 활성화가 전체 또는 부분적으로 차단됩니다:

- [JSON](/docs/json/apps/http/servers/automatic_https/) 또는 [Caddyfile](/docs/caddyfile/options#auto-https)을 통해 명시적으로 비활성화한 경우
- 구성에 호스트 이름이나 IP 주소를 제공하지 않은 경우
- 오직 HTTP 포트에서만 수신 대기하는 경우
- Caddyfile에서 [사이트 주소](/docs/caddyfile/concepts#addresses) 앞에 `http://`를 붙인 경우
- 수동으로 인증서를 로드한 경우([`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/)가 설정된 경우 제외)

**특별한 경우:**

- `.ts.net`으로 끝나는 도메인은 Caddy가 직접 관리하지 않습니다. 대신 Caddy는 핸드셰이크 시점에 로컬에서 실행 중인 [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) 인스턴스에서 이러한 인증서를 자동으로 가져오려고 시도합니다. 이를 위해서는 [Tailscale 계정에서 HTTPS가 활성화되어 있어야 하며 <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) Caddy 프로세스가 루트 권한으로 실행 중이거나 `tailscaled`가 Caddy 사용자에게 [인증서를 가져올 권한](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)을 부여하도록 구성해야 합니다.


## <a id="effects"></a>효과

자동 HTTPS가 활성화되면 다음과 같은 일이 발생합니다:

- [모든 적격한 도메인 이름](#hostname-requirements)에 대해 인증서를 획득하고 갱신합니다.
- HTTP가 HTTPS로 리디렉션됩니다([HTTP 포트](/docs/modules/http#http_port) `80` 사용).

자동 HTTPS는 명시적인 구성을 덮어쓰지 않으며, 보완만 합니다.

이미 HTTP 포트에서 수신 대기 중인 [서버](/docs/json/apps/http/servers/)가 있는 경우, HTTP->HTTPS 리디렉션 경로는 호스트 매처가 있는 경로 뒤에, 그러나 사용자 정의 캐치올(catch-all) 경로 앞에 삽입됩니다.

필요한 경우 [자동 HTTPS를 사용자 정의하거나 비활성화](/docs/json/apps/http/servers/automatic_https/)할 수 있습니다. 예를 들어, 특정 도메인 이름을 건너뛰거나 리디렉션을 비활성화할 수 있습니다(Caddyfile의 경우 [글로벌 옵션](/docs/caddyfile/options)을 사용하세요).


## <a id="hostname-requirements"></a>호스트 이름 요구 사항

다음 조건을 충족하는 모든 호스트 이름(도메인 이름)은 전체 관리 인증서를 받을 자격이 있습니다:

- 비어 있지 않음
- 영숫자, 하이픈, 점 및 와일드카드(`*`)로만 구성됨
- 점으로 시작하거나 끝나지 않음([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

또한, 다음 조건을 충족하는 호스트 이름은 공인 인증서를 받을 자격이 있습니다:

- localhost가 아님(`.localhost`, `.local`, `.internal`, `.home.arpa` TLD 포함)
- IP 주소가 아님
- 가장 왼쪽 레이블에만 단일 와일드카드 `*`가 있음


## <a id="local-https"></a>로컬 HTTPS

Caddy는 내부 및 로컬 호스트를 포함하여 호스트(도메인, IP 또는 호스트 이름)가 지정된 모든 사이트에 대해 자동으로 HTTPS를 사용합니다. 일부 호스트는 공용이 아니거나(`예: 127.0.0.1`, `localhost`), 일반적으로 공인 인증서 자격이 없습니다(`예: IP 주소` -- 일부 CA에서만 인증서를 받을 수 있음). 이들은 비활성화하지 않는 한 여전히 HTTPS를 통해 서비스됩니다.

비공용 사이트를 HTTPS를 통해 서비스하기 위해 Caddy는 자체 인증 기관(CA)을 생성하고 이를 사용하여 인증서에 서명합니다. 신뢰 체인은 루트와 중간 인증서로 구성됩니다. 리프(Leaf) 인증서는 중간 인증서에 의해 서명됩니다. 이들은 [Caddy의 데이터 디렉터리](/docs/conventions#data-directory)의 `pki/authorities/local`에 저장됩니다.

Caddy의 로컬 CA는 [Smallstep 라이브러리 <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/)를 기반으로 합니다.

로컬 HTTPS는 ACME를 사용하지 않으며 DNS 검증도 수행하지 않습니다. 이는 로컬 머신에서만 작동하며 CA의 루트 인증서가 설치된 곳에서만 신뢰됩니다.

### <a id="ca-root"></a>CA 루트

루트의 개인 키는 암호학적으로 안전한 의사 난수 소스를 사용하여 고유하게 생성되며 제한된 권한으로 스토리지에 유지됩니다. 서명 작업을 수행하기 위해서만 메모리에 로드되며, 작업이 끝나면 가비지 컬렉션의 대상이 되어 메모리에서 제거됩니다.

비준수 클라이언트를 지원하기 위해 루트로 직접 서명하도록 Caddy를 구성할 수 있지만, 이는 기본적으로 비활성화되어 있으며 루트 키는 중간 인증서 서명에만 사용됩니다.

루트 키가 처음 사용될 때 Caddy는 이를 시스템의 로컬 신뢰 저장소에 설치하려고 시도합니다. 권한이 없는 경우 비밀번호를 요청합니다. 이 동작은 [Caddyfile의 `skip_install_trust`](/docs/caddyfile/options#skip-install-trust) 또는 [JSON 설정의 `"install_trust": false`](/docs/json/apps/pki/certificate_authorities/install_trust/)를 통해 비활성화할 수 있습니다. 권한이 없는 사용자로 실행되어 실패한 경우, [`caddy trust`](/docs/command-line#caddy-trust)를 실행하여 권한이 있는 사용자로 설치를 재시도할 수 있습니다.

<aside class="tip">
	컴퓨터가 해킹되지 않았고 고유한 루트 키가 유출되지 않았다면, 자신의 머신에서 Caddy의 루트 인증서를 신뢰하는 것은 안전합니다.
</aside>

Caddy의 루트 CA가 설치되면 로컬 신뢰 저장소에 "Caddy Local Authority"(다른 이름을 구성하지 않은 경우)로 표시됩니다. 원할 경우 언제든지 제거할 수 있습니다([`caddy untrust`](/docs/command-line#caddy-untrust) 명령을 사용하면 쉽습니다).

인증서를 로컬 신뢰 저장소에 자동으로 설치하는 것은 편의를 위한 것일 뿐이며 작동이 보장되지 않습니다. 특히 컨테이너를 사용하거나 Caddy를 권한이 없는 시스템 서비스로 실행하는 경우 더욱 그렇습니다. 궁극적으로 내부 PKI를 사용하는 경우, Caddy의 루트 CA가 필요한 신뢰 저장소에 올바르게 추가되었는지 확인하는 것은 시스템 관리자의 책임입니다(이는 웹 서버의 범위를 벗어납니다).


### <a id="ca-intermediates"></a>CA 중간 인증서

중간 인증서와 키도 생성되며, 이는 리프(개별 사이트) 인증서 서명에 사용됩니다.

루트 인증서와 달리 중간 인증서는 수명이 훨씬 짧으며 필요에 따라 자동으로 갱신됩니다.


## <a id="testing"></a>테스트

Caddy 구성을 테스트하거나 실험하려면 [ACME 엔드포인트를 변경](/docs/modules/tls.issuance.acme#ca)하여 스테이징 또는 개발 URL로 설정하세요. 그렇지 않으면 도달한 속도 제한에 따라 최대 일주일 동안 HTTPS 접근이 차단될 수 있는 속도 제한에 걸릴 가능성이 높습니다.

Caddy의 기본 CA 중 하나는 [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/)이며, 동일한 [속도 제한 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/)이 적용되지 않는 [스테이징 엔드포인트 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)를 제공합니다:

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

## <a id="acme-challenges"></a>ACME 챌린지

공인 TLS 인증서를 얻으려면 공인 제3자 기관의 검증이 필요합니다. 오늘날 이 검증 프로세스는 [ACME 프로토콜 <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555)을 통해 자동화되며, 아래에 설명된 세 가지 방식("챌린지 유형") 중 하나로 수행될 수 있습니다.

처음 두 가지 챌린지 유형은 기본적으로 활성화되어 있습니다. 여러 챌린지가 활성화된 경우, Caddy는 특정 챌린지에 대한 우발적인 의존을 피하기 위해 무작위로 하나를 선택합니다. 시간이 지남에 따라 어떤 챌린지 유형이 가장 성공적인지 학습하고 이를 먼저 선호하기 시작하지만, 필요한 경우 다른 사용 가능한 챌린지 유형으로 폴백(fall back)합니다.


### <a id="http-challenge"></a>HTTP 챌린지

HTTP 챌린지는 대상 호스트 이름의 A/AAAA 레코드에 대해 신뢰할 수 있는 DNS 조회를 수행한 다음, HTTP를 사용하여 `80` 포트를 통해 임시 암호화 리소스를 요청합니다. CA가 예상된 리소스를 확인하면 인증서가 발급됩니다.

이 챌린지는 `80` 포트가 외부에서 액세스 가능해야 합니다. Caddy가 80번 포트에서 직접 수신 대기할 수 없는 경우, 80번 포트의 패킷이 Caddy의 [HTTP 포트](/docs/json/apps/http/http_port/)로 포워딩되어야 합니다.

이 챌린지는 기본적으로 활성화되어 있으며 명시적인 설정이 필요하지 않습니다.


### <a id="tls-alpn-challenge"></a>TLS-ALPN 챌린지

TLS-ALPN 챌린지는 대상 호스트 이름의 A/AAAA 레코드에 대해 신뢰할 수 있는 DNS 조회를 수행한 다음, 특수한 ServerName 및 ALPN 값이 포함된 TLS 핸드셰이크를 사용하여 `443` 포트를 통해 임시 암호화 리소스를 요청합니다. CA가 예상된 리소스를 확인하면 인증서가 발급됩니다.

이 챌린지는 `443` 포트가 외부에서 액세스 가능해야 합니다. Caddy가 443번 포트에서 직접 수신 대기할 수 없는 경우, 443번 포트의 패킷이 Caddy의 [HTTPS 포트](/docs/json/apps/http/https_port/)로 포워딩되어야 합니다.

이 챌린지는 기본적으로 활성화되어 있으며 명시적인 설정이 필요하지 않습니다.


### <a id="dns-challenge"></a>DNS 챌린지

DNS 챌린지는 대상 호스트 이름의 `TXT` 레코드에 대해 신뢰할 수 있는 DNS 조회를 수행하고, 특정 값을 가진 특수 `TXT` 레코드를 찾습니다. CA가 예상된 값을 확인하면 인증서가 발급됩니다.

이 챌린지는 열린 포트가 필요하지 않으며, 인증서를 요청하는 서버가 외부에서 액세스 가능할 필요도 없습니다. 그러나 DNS 챌린지는 구성이 필요합니다. Caddy는 특수 `TXT` 레코드를 설정(및 삭제)할 수 있도록 도메인의 DNS 공급자에 액세스하기 위한 자격 증명을 알아야 합니다. DNS 챌린지가 활성화되면 다른 챌린지는 기본적으로 비활성화됩니다.

ACME CA는 챌린지 검증을 위해 `TXT` 레코드를 조회할 때 DNS 표준을 따르므로, CNAME 레코드를 사용하여 챌린지 응답을 다른 DNS 영역에 위임할 수 있습니다. 이는 `_acme-challenge` 하위 도메인을 [다른 영역](/docs/caddyfile/directives/tls#dns_challenge_override_domain)으로 위임하는 데 사용될 수 있습니다. 이는 DNS 공급자가 API를 제공하지 않거나 Caddy용 DNS 플러그인 중 하나에서 지원되지 않는 경우 특히 유용합니다.

DNS 공급자 지원은 커뮤니티의 노력으로 이루어집니다. [위키에서 공급자에 대해 DNS 챌린지를 활성화하는 방법을 알아보세요.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


## <a id="on-demand-tls"></a>온디맨드 TLS

Caddy는 설정 로드 시점이 아니라 요구되는 첫 번째 TLS 핸드셰이크 중에 동적으로 새 인증서를 획득하는 **온디맨드 TLS**라는 새로운 기술을 개척했습니다. 결정적으로, 이는 도메인 이름을 미리 구성 파일에 하드코딩할 필요가 **없습니다**.

많은 기업들이 수만 개의 사이트를 서비스할 때 운영상의 번거로움 없이 더 낮은 비용으로 TLS 배포를 확장하기 위해 이 독특한 기능에 의존합니다.

온디맨드 TLS는 다음과 같은 경우에 유용합니다:

- 서버를 시작하거나 다시 로드할 때 모든 도메인 이름을 알 수 없는 경우,
- 도메인 이름이 즉시 제대로 구성되지 않을 수 있는 경우(DNS 레코드가 아직 설정되지 않음),
- 도메인 이름을 직접 제어하지 않는 경우(예: 고객 도메인).

온디맨드 TLS가 활성화되면 인증서를 얻기 위해 설정에 도메인 이름을 지정할 필요가 없습니다. 대신, Caddy가 아직 인증서를 가지고 있지 않은 서버 이름(SNI)에 대해 TLS 핸드셰이크가 수신되면, Caddy가 핸드셰이크를 완료하는 데 사용할 인증서를 얻는 동안 핸드셰이크가 보류됩니다. 지연은 보통 몇 초에 불과하며 초기 핸드셰이크만 느립니다. 인증서가 캐시되고 재사용되며 갱신이 백그라운드에서 이루어지기 때문에 이후의 모든 핸드셰이크는 빠릅니다. 이후의 핸드셰이크는 인증서를 최신 상태로 유지하기 위해 유지 관리를 트리거할 수 있지만, 인증서가 아직 만료되지 않은 경우 이 유지 관리는 백그라운드에서 수행됩니다.

### 온디맨드 TLS 사용하기

**온디맨드 TLS는 남용을 방지하기 위해 활성화와 제한이 모두 필요합니다.**

온디맨드 TLS 활성화는 JSON 설정을 사용하는 경우 [TLS 자동화 정책](/docs/json/apps/tls/automation/policies/)에서, Caddyfile을 사용하는 경우 [`tls` 디렉티브가 있는 사이트 블록](/docs/caddyfile/directives/tls)에서 수행됩니다.

이 기능의 남용을 방지하려면 제한 사항을 구성해야 합니다. 이는 JSON 설정의 [`automation` 객체](/docs/json/apps/tls/automation/on_demand/) 또는 Caddyfile의 [`on_demand_tls` 글로벌 옵션](/docs/caddyfile/options#on-demand-tls)에서 수행됩니다. 제한 사항은 "글로벌"하며 사이트별 또는 도메인별로 구성할 수 없습니다. 주요 제한 사항은 핸드셰이크의 도메인에 대해 인증서를 획득하고 관리할 권한이 있는지 묻기 위해 Caddy가 HTTP 요청을 보낼 "ask" 엔드포인트입니다. 즉, 데이터베이스의 계정 테이블을 조회하여 고객이 해당 도메인 이름으로 가입했는지 확인할 수 있는 내부 백엔드가 필요합니다.

CA가 인증서를 얼마나 빨리 발급할 수 있는지 유의하세요. 몇 초 이상 걸리면 사용자 경험에 부정적인 영향을 미칠 수 있습니다(첫 번째 클라이언트에만 해당).

지연 처리되는 특성과 남용 방지를 위해 필요한 추가 구성으로 인해, 실제 사례가 위에 설명된 경우에만 온디맨드 TLS를 활성화하는 것이 좋습니다.

[온디맨드 TLS를 효과적으로 사용하는 방법에 대한 자세한 내용은 위키 문서를 참조하세요.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

## <a id="errors"></a>오류

Caddy는 인증서 관리 중 오류가 발생해도 계속 진행하기 위해 최선을 다합니다.

기본적으로 인증서 관리는 백그라운드에서 수행됩니다. 즉, 시작을 차단하거나 사이트 속도를 늦추지 않습니다. 그러나 이는 모든 인증서를 사용할 수 있기 전에도 서버가 실행된다는 것을 의미합니다. 백그라운드 실행을 통해 Caddy는 긴 기간 동안 지수 백오프(exponential backoff)를 사용하여 재시도할 수 있습니다.

인증서 획득 또는 갱신 중 오류가 발생하면 다음과 같은 일이 발생합니다:

1. 단순한 일시적 오류일 가능성에 대비해 짧은 일시 중지 후 한 번 재시도합니다.
2. 잠시 일시 중지한 후 다음으로 활성화된 챌린지 유형으로 전환합니다.
3. 활성화된 모든 챌린지 유형을 시도한 후, [다음에 구성된 발급자를 시도합니다](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. 모든 발급자를 시도한 후 지수 백오프를 수행합니다.
	- 시도 간 최대 1일
	- 최대 30일 동안

Let's Encrypt로 재시도하는 동안 Caddy는 속도 제한 문제를 피하기 위해 [스테이징 환경 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)으로 전환합니다. 이것이 완벽한 전략은 아니지만 일반적으로 유용합니다.

ACME 챌린지는 최소 몇 초가 소요되며, 내부 속도 제한은 우발적인 남용을 완화하는 데 도움이 됩니다. Caddy는 사용자나 CA가 구성한 것 외에도 내부 속도 제한을 사용하여, 사용자가 백만 개의 도메인 이름을 Caddy에 제공하더라도 점진적으로(그러나 가능한 한 빨리) 모든 도메인에 대한 인증서를 얻도록 합니다. Caddy의 내부 속도 제한은 현재 10초당 ACME 계정당 10회 시도입니다.

리소스 누수를 방지하기 위해 Caddy는 설정이 변경될 때 진행 중인 작업(ACME 트랜잭션 포함)을 중단합니다. Caddy는 잦은 설정 재로드를 처리할 수 있지만, 이러한 운영상의 고려 사항을 염두에 두고 재로드를 줄이고 Caddy가 백그라운드에서 인증서 획득을 실제로 완료할 수 있는 기회를 주도록 설정 변경을 일괄 처리하는 것이 좋습니다.

### <a id="issuer-fallback"></a>발급자 폴백

Caddy는 인증서를 성공적으로 얻지 못할 경우 다른 CA로 완전히 중복된 자동 페일오버(failover)를 지원하는 최초의(그리고 현재까지 유일한) 서버입니다.

기본적으로 Caddy는 두 개의 ACME 호환 CA인 [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org)와 [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com)을 활성화합니다. Caddy가 Let's Encrypt에서 인증서를 얻을 수 없으면 ZeroSSL로 시도하며, 둘 다 실패하면 백오프 후 나중에 다시 시도합니다. 설정에서 전역적으로 또는 특정 이름에 대해 Caddy가 인증서를 얻는 데 사용할 발급자를 사용자 정의할 수 있습니다.


## <a id="storage"></a>스토리지

Caddy는 공인 인증서, 개인 키 및 기타 자산을 [구성된 스토리지 시설](/docs/json/storage/)에 저장합니다(구성되지 않은 경우 기본 스토리지에 저장됨 - 자세한 내용은 링크 참조).

**기본 설정을 사용할 때 알아야 할 가장 중요한 점은 `$HOME` 폴더가 쓰기 가능하고 영구적이어야 한다는 것입니다.** 문제 해결을 돕기 위해 `--environ` 플래그를 지정하면 Caddy가 시작할 때 환경 변수를 출력합니다.

동일한 스토리지를 사용하도록 구성된 모든 Caddy 인스턴스는 해당 리소스를 자동으로 공유하고 클러스터로서 인증서 관리를 조정합니다.

ACME 트랜잭션을 시도하기 전에 Caddy는 구성된 스토리지가 쓰기 가능한지, 충분한 용량이 있는지 테스트합니다. 이는 불필요한 락 경합(lock contention)을 줄이는 데 도움이 됩니다.


## <a id="wildcard-certificates"></a>와일드카드 인증서

Caddy는 적격한 와일드카드 이름으로 사이트를 서비스하도록 구성된 경우 와일드카드 인증서를 획득하고 관리할 수 있습니다. 사이트 이름의 가장 왼쪽 도메인 레이블만 와일드카드인 경우 와일드카드 자격이 있습니다. 예를 들어, `*.example.com`은 자격이 있지만 `sub.*.example.com`, `foo*.example.com`, `*bar.example.com`, `*.*.example.com`은 자격이 없습니다. (이는 WebPKI의 제한 사항입니다.)

Caddyfile을 사용하는 경우 Caddy는 인증서 주체 이름과 관련하여 사이트 이름을 문자 그대로 받아들입니다. 즉, `sub.example.com`으로 정의된 사이트는 Caddy가 `sub.example.com`에 대한 인증서를 관리하게 하고, `*.example.com`으로 정의된 사이트는 Caddy가 `*.example.com`에 대한 와일드카드 인증서를 관리하게 합니다. 이에 대한 예시는 [일반적인 Caddyfile 패턴](/docs/caddyfile/patterns#wildcard-certificates) 페이지에서 확인할 수 있습니다. 다른 동작이 필요한 경우 [JSON 설정](/docs/json/)을 사용하면 인증서 주체와 사이트 이름("호스트 매처")을 더 정밀하게 제어할 수 있습니다.

Caddy 2.10부터 와일드카드 인증서를 자동화할 때 Caddy는 설정에 있는 개별 하위 도메인에 대해 와일드카드 인증서를 사용합니다. 명시적으로 구성하지 않는 한(예: `force_automate` 사용) 개별 하위 도메인에 대한 인증서를 얻지 않습니다.

와일드카드 인증서는 광범위한 권한을 나타내며, 개별 인증서를 관리하는 것이 PKI에 부담을 주거나 CA가 강제하는 속도 제한에 걸릴 정도로 하위 도메인이 아주 많은 경우, 또는 키 유출 시 DNS 영역의 상당 부분이 노출될 위험을 감수할 만큼 프라이버시 이점이 가치 있는 경우에만 사용해야 합니다. 와일드카드 인증서만으로는 특정 하위 도메인을 숨기는 프라이버시를 제공하지 않습니다. 암호화된 ClientHello (ECH)가 활성화되지 않는 한 TLS ClientHello 패킷에 여전히 노출됩니다. (아래 참조)

**참고:** [Let's Encrypt에서 와일드카드 인증서를 얻으려면 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) [DNS 챌린지](#dns-challenge)가 필요합니다.


## <a id="encrypted-clienthello-ech"></a>암호화된 ClientHello (ECH)

일반적으로 TLS 핸드셰이크에는 접속하려는 도메인인 서버 이름 표시(SNI)를 포함한 ClientHello를 평문으로 보내는 과정이 포함됩니다. 이는 핸드셰이크 이후에 연결을 암호화하는 데 필요한 매개변수가 포함되어 있기 때문입니다. 물론 이는 ClientHello에서 가장 민감한 부분인 도메인 이름을 노출시키며, 목적지 IP가 여러 사이트를 서비스할 때 어떤 서비스에 연결하는지 드러내게 됩니다. 일부 정부가 인터넷을 검열하는 방식이기도 합니다.

암호화된 ClientHello를 사용하면 클라이언트는 진짜 ClientHello를 "외부" ClientHello로 감싸서 "내부" ClientHello를 복호화하기 위한 매개변수를 설정함으로써 도메인 이름을 보호할 수 있습니다. 그러나 이것이 실제로 작동하고 프라이버시 이점을 제공하려면 많은 유동적인 요소들이 완벽하게 결합되어야 합니다.

먼저, 클라이언트는 ClientHello를 암호화하는 데 사용할 매개변수 또는 구성을 알아야 합니다. 이 정보에는 공개 키와 "외부" 도메인("공인 이름(public name)") 등이 포함됩니다. 이 구성은 신뢰할 수 있는 방식으로 게시되거나 배포되어야 합니다.

이론적으로는 종이에 적어서 모두에게 나눠줄 수도 있겠지만, 대부분의 주요 브라우저는 사이트에 접속할 때 ECH 매개변수가 포함된 HTTPS 유형의 DNS 레코드 조회를 지원합니다. 따라서 (1) ECH 구성(공개/개인 키 쌍 및 기타 매개변수)을 생성하고, (2) base64로 인코딩된 ECH 구성이 포함된 HTTPS 유형의 DNS 레코드를 생성해야 합니다.

아니면... Caddy가 이 모든 것을 대신하게 할 수 있습니다. Caddy는 ECH 구성을 자동으로 생성, 게시 및 서비스할 수 있는 최초이자 유일한 웹 서버입니다.

HTTPS 레코드가 게시되면 클라이언트는 사이트에 접속할 때 HTTPS 레코드에 대한 DNS 조회를 수행해야 합니다. 일반적으로 DNS 조화는 평문으로 이루어지며, 이는 결과적으로 ECH 핸드셰이크의 보안을 저하시키므로 브라우저는 DNS-over-HTTPS (DoH) 또는 DNS-over-TLS (DoT)와 같은 보안 DNS 프로토콜을 사용해야 합니다. 브라우저에 따라 이를 수동으로 활성화해야 할 수도 있습니다.

클라이언트가 ECH 구성을 안전하게 다운로드하면, 내장된 공개 키를 사용하여 ClientHello를 암호화하고 사이트 접속을 진행합니다. 그러면 Caddy는 내부 ClientHello를 복호화하여 사이트를 서비스하며, 도메인 이름은 통신 중에 평문으로 나타나지 않습니다.

### 배포 고려 사항

ECH는 미묘한 기술입니다. Caddy가 ECH를 완전히 자동화하더라도 최대의 프라이버시 이점을 얻으려면 많은 사항을 고려해야 합니다. 또한 다양한 트레이드오프(trade-off)를 알고 있어야 합니다. 

#### 게시

Caddy는 해당 도메인에 대한 레코드가 이미 있는 경우에만 해당 도메인에 대한 HTTPS 레코드를 생성합니다. 이는 와일드카드에 포함될 수 있는 하위 도메인에 대한 DNS 조회를 방해하는 것을 방지합니다. 사이트가 서버를 가리키는 A/AAAA 레코드를 하나 이상 가지고 있는지 확인하세요. DNS 레코드에 와일드카드만 사용하는 경우 해당 와일드카드 도메인도 Caddy 설정에 나타나야 합니다.

Caddy는 CNAME 레코드가 있는 도메인에 대해서는 HTTPS 레코드를 게시하지 않습니다.

#### ECH GREASE

Wireshark를 열고 최신 버전의 Firefox나 Chrome과 같은 주요 브라우저(ECH가 비활성화된 경우에도)에서 사이트에 접속하면 핸드셰이크에 `encrypted_client_hello` 확장이 포함된 것을 볼 수 있습니다:

![ECH GREASE](/resources/images/ech-grease.png)

이것의 목적은 진짜 ECH 핸드셰이크를 평문 핸드셰이크와 구별할 수 없게 만드는 것입니다. ECH 핸드셰이크가 일반적인 것과 다르게 보인다면, 검열관은 최소한의 부수적 피해로 ECH 핸드셰이크를 차단할 수 있습니다. 그러나 ECH 확장처럼 보이는 모든 핸드셰이크를 차단한다면 인터넷의 대부분을 차단하게 될 것입니다. (목표는 광범위한 검열의 비용을 높이는 것입니다.)

이는 주로 연결 문제를 해결할 때 알아두어야 할 사항입니다.

#### 키 교체

인증서 키와 마찬가지로 동일한 키를 오랫동안 사용하는 것은 좋은 습관이 아니며(매우 안전하지 않을 수도 있습니다), 따라서 ECH 키는 정기적으로 교체되어야 합니다. 인증서와 달리 ECH 구성은 엄격하게 만료되지 않지만, 그럼에도 불구하고 서버는 이를 교체해야 합니다.

하지만 키 교체는 까다롭습니다. 클라이언트가 업데이트된 키에 대해 알아야 하기 때문입니다. 서버가 단순히 이전 키를 새 키로 교체하면 클라이언트에게 즉시 알리지 않는 한 모든 ECH 핸드셰이크가 실패하게 됩니다. 그러나 단순히 업데이트된 키를 게시하는 것만으로는 충분하지 않습니다. 현실적으로 DNS 레코드에는 TTL이 있고 리졸버는 응답을 캐싱하기 때문입니다. 클라이언트가 업데이트된 HTTPS 레코드를 조회하고 새 ECH 구성을 사용하기 시작하는 데 몇 분, 몇 시간 또는 며칠이 걸릴 수 있습니다.

이러한 이유로 서버는 일정 기간 동안 이전 ECH 구성을 계속 지원해야 합니다. 그렇지 않으면 대규모로 서버 이름이 평문으로 노출될 위험이 있습니다. Caddy는 주기적으로 키를 교체하며, 최종적으로 삭제될 때까지 일정 기간 동안 교체된 키를 지원합니다.

그러나 그것만으로는 부족할 수 있습니다. 일부 클라이언트는 여러 이유로 업데이트된 키를 받지 못할 수 있으며, 그럴 때마다 서버 이름이 노출될 위험이 있습니다. 따라서 연결 중에 클라이언트에게 업데이트된 구성을 인밴드(in-band)로 제공하는 또 다른 방법이 필요합니다. 그것이 바로 *외부 이름(outer name)* (또는 *공인 이름(public name)*)의 목적입니다.

#### 공인 이름

"외부" ClientHello는 오리진 서버만 알 수 있는 두 가지 미묘한 차이점이 있는 일반적인 ClientHello입니다:

1. SNI 확장이 가짜입니다.
2. ECH 확장이 진짜입니다.

해당 "외부" SNI 확장에는 실제 도메인을 보호하는 공인 이름이 포함되어 있습니다. 이 이름은 무엇이든 될 수 있지만, Caddy가 이에 대한 인증서를 획득하므로 **서버가 공인 이름에 대한 권한을 가지고 있어야 합니다**.

클라이언트가 ECH 연결을 시도했지만 서버가 내부 ClientHello를 복호화할 수 없는 경우, 실제로 외부 이름에 대한 인증서를 사용하여 외부 ClientHello로 핸드셰이크를 완료할 수 있습니다. 이 보안 연결은 엄격하게 클라이언트에게 현재 ECH 구성을 보내는 용도로만 사용됩니다. 즉, 초기 TLS 연결을 완료하기 위한 유일한 목적으로 사용되는 임시 TLS 연결입니다. 어플리케이션 데이터는 전송되지 않으며 ECH 키만 전송됩니다. 클라이언트가 업데이트된 키를 받으면 의도한 대로 TLS 연결을 설정할 수 있습니다.

이러한 방식으로 진짜 서버 이름은 계속 보호되고 동기화되지 않은 클라이언트도 연결할 수 있으며, 이는 보안의 필수 요소입니다.

외부 이름은 사이트의 도메인 중 하나, 하위 도메인 또는 서버를 가리키는 다른 도메인 이름일 수 있습니다. 하나의 일반적인 이름을 선택하는 것이 좋습니다. 예를 들어 Cloudflare는 수백만 개의 사이트를 `cloudflare-ech.com` 뒤에서 서비스합니다. 이는 익명성 세트(anonymity set)의 크기를 늘리는 데 중요합니다.

공인 이름은 비어 있으면 안 됩니다. 즉, 작동하려면 공인 이름이 구성되어야 합니다. Caddy는 현재 이를 강제하지 않지만(나중에 강제할 수도 있음), ECH 사양에서는 공인 이름이 최소 1바이트 이상이어야 한다고 규정하고 있습니다. 일부 소프트웨어는 빈 이름을 허용하지만 그렇지 않은 소프트웨어도 있습니다. 이로 인해 브라우저는 ECH를 사용하지만 서버는 이를 유효하지 않은 것으로 거부하거나, 설정이 DNS 레코드에 제대로 있음에도 브라우저가 ECH를 사용하지 않는(유효하지 않기 때문에) 혼란스러운 동작이 발생할 수 있습니다. 프라이버시를 보장하기 위해 적절한 ECH 구성 및 게시를 확인하는 것은 사이트 소유자의 책임입니다.


#### 익명성 세트

ECH의 프라이버시 이점을 극대화하려면 익명성 세트의 크기를 극대화하도록 노력하세요. 본질적으로 이 세트는 관찰자에게 동일한 동작을 보이는 클라이언트 측 서버로 구성됩니다. 아이디어는 관찰자가 클라이언트가 접속하려는 가능한 사이트나 서비스를 쉽게 축소하거나 추론할 수 없도록 하는 것입니다.

실제로 모든 사이트에 대해 하나의 공인 이름만 사용하는 것이 좋습니다. (ECH 구성당 공인 이름은 하나뿐이므로, 이는 특정 시점에 활성화된 ECH 구성이 하나만 있음을 의미합니다.) Caddy를 클러스터로 운영하는 경우, Caddy는 다른 인스턴스와 ECH 구성을 자동으로 공유하고 조정하므로 이 부분이 자동으로 처리됩니다.

극단적으로 말하면, 인터넷의 모든 사이트가 단일 IP 주소와 하나의 공인 이름 뒤에 있을 수 있거나 있어야 한다는 것을 의미합니다...


#### 중앙 집중화

...이는 다음 주제인 중앙 집중화로 이어집니다. ECH에 대한 비판 중 하나는 중앙 집중화를 유도하는 경향이 있다는 것입니다. 이는 최소 두 가지 방식으로 나타납니다: (1) 클라이언트가 DNS 조회를 위해 DoH/DoT를 선호하게 되어 모든 DNS 조회가 소수의 공급자에게 집중되고, (2) 대규모로 익명성 세트의 크기를 극대화하기 때문입니다.

DoH나 DoT를 사용하면 DNS 조회가 모두 DoH/DoT 공급자를 통하게 됩니다. 클라이언트와 공급자 사이의 DNS 데이터는 암호화되지만, 공급자와 DNS 서버 사이는 암호화되지 않습니다. 글로벌 DoH/DoT는 실질적으로 모든 흥미로운 평문 DNS 트래픽을 관찰이나 실패에 취약한 몇 개의 큰 파이프로 집중시킵니다.

마찬가지로 대규모로 익명성 세트를 진정으로 극대화한다면, 모든 사이트가 `cloudflare-ech.com`과 같은 단일 공인 이름 뒤에 보호될 것입니다. 이는 프라이버시에는 좋지만 인터넷 전체가 Cloudflare와 해당 도메인 하나의 처분에 맡겨지게 됩니다. 물론 그렇게까지 극대화하는 것이 필요하거나 실용적이지는 않지만, 이론적인 함의는 여전히 유효합니다.

각 조직이나 개인이 모든 사이트에 대해 단일 이름을 선택하여 사용하는 것이 좋으며, 대부분의 경우 이는 충분한 프라이버시를 제공할 것입니다. 하지만 개별 사례에 맞는 위협 모델은 전문가와 상의하시기 바랍니다.


#### 하위 도메인 프라이버시

ECH를 사용하면 올바르게 배포된 경우 이론적으로 사이드 채널로부터 하위 도메인을 비밀/비공개로 유지할 수 있습니다.

일반적으로 하위 도메인은 공개 정보이므로 대부분의 사이트는 이것이 필요하지 않습니다. 도메인 이름에 민감한 정보를 넣지 않는 것이 좋습니다. 그렇긴 하지만...

민감한 하위 도메인이 인증서 투명성(CT) 로그에 노출되는 것을 방지하려면 대신 와일드카드 인증서를 사용하세요. 즉, 설정에 `sub.example.com`을 넣는 대신 `*.example.com`을 넣으세요. (중요한 정보는 [와일드카드 인증서](#wildcard-certificates)를 참조하세요.)

또 다른 유출 소스는 대부분의 권한 있는 DNS 서버가 기본적으로 사용하는 DNSSEC입니다. "존 워킹(zone walking)"이라는 관행을 통해, 존재 여부에 대한 인증된 거부를 제공하는 데 사용되는 NSEC 레코드를 살펴봄으로써 하위 도메인을 나열할 수 있습니다. 이를 위해 레코드는 알파벳 순서로 다음 사용 가능한 하위 도메인을 가리키며 모든 레코드의 연결 리스트를 형성합니다. 이를 방지하려면 도메인이 최소한 NSEC3를 사용하거나 이상적으로는 와일드카드 CNAME 레코드를 사용하고 있는지 확인하세요.

그런 다음 Caddy에서 ECH를 활성화하세요. 와일드카드 인증서와 ECH, 와일드카드 CNAME 레코드를 결합하면, 접속을 시도하는 모든 클라이언트가 ECH를 사용하고 강력하게 구현된 경우 하위 도메인을 적절하게 숨길 수 있습니다. (프라이버시를 유지하는 것은 여전히 클라이언트에 달려 있습니다.)


### ECH 활성화하기

작동하는 ECH는 DNS 레코드에 구성을 게시해야 하므로, DNS 공급자를 위해 [caddy-dns 모듈](https://github.com/caddy-dns)이 포함된 Caddy 빌드가 필요합니다.

그런 다음 Caddyfile에서 글로벌 옵션에 DNS 공급자 설정과 사용하려는 ECH 공인 이름을 지정합니다:

```caddy
{
	dns <provider config...>
	ech example.com
}
```

기억하세요:

- DNS 공급자 모듈이 포함되어야 하며 공급자/계정에 맞는 올바른 설정이 있어야 합니다.
- ECH 공인 이름은 서버를 가리켜야 합니다. Caddy회 인증서를 획득합니다. 사이트 도메인 중 하나일 필요는 없습니다.

JSON을 사용하는 경우 `tls` 앱에 다음 속성을 추가합니다:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// 공급자 설정
}
```

이러한 설정은 ECH를 활성화하고 모든 사이트에 대해 ECH 구성을 게시합니다. JSON 설정은 동작을 사용자 정의하거나 고급 설정이 필요한 경우 더 많은 유연성을 제공합니다.

### ECH 확인하기

아직 ECH 관련 도구가 많지 않으므로, 이 글을 쓰는 시점에서 작동 여부를 확인하는 가장 좋고 보편적인 방법은 Wireshark를 사용하여 ServerName 필드에서 공인 이름을 확인하는 것입니다.

먼저 서버를 시작하고 로그에 도메인에 대해 "published ECH configuration list"와 같은 내용이 언급되는지 확인하세요. (게시 중 오류가 발생하면 DNS 공급자 모듈이 [libdns 1.0](https://github.com/libdns/libdns)을 지원하는지 확인하고 문제가 발생하면 공급자 저장소에 이슈를 제기하세요.) Caddy는 공인 이름에 대한 인증서도 얻어야 합니다.

다음으로 브라우저에 ECH가 활성화되어 있는지 확인하세요. DoH/DoT를 활성화해야 할 수도 있습니다. 또한 브라우저(또는 시스템)의 DNS 캐시를 지워 새로 게시된 HTTPS 레코드를 가져오도록 하는 것이 좋습니다. 기존 연결을 재사용하지 않도록 브라우저를 닫거나 최소한 새 비밀 탭을 여는 것을 권장합니다.

그런 다음 Wireshark를 열고 적절한 네트워크 인터페이스에서 수신 대기를 시작합니다. Wireshark 패킷을 수집하는 동안 브라우저에서 사이트를 로드합니다. 그런 다음 Wireshark를 일시 중지할 수 있습니다. TLS ClientHello를 찾으면 접속한 실제 도메인 이름 대신 *공인 이름*이 ServerName 필드에 표시되어야 합니다.

기억하세요: ECH를 사용하지 않더라도 `encrypted_client_hello` 확장을 계속 볼 수 있습니다. 핵심 지표는 SNI 값입니다. ECH가 제대로 작동한다면 Wireshark에서 실제 사이트 이름을 평문으로 보아서는 안 됩니다.

ECH 배포 문제가 발생하면 먼저 [포럼](https://caddy.community)에 문의하세요. 버그인 경우 GitHub에 [이슈를 제기](https://github.com/caddyserver/caddy/issues)할 수 있습니다.


### 스토리지의 ECH

ECH 구성은 `ech/configs` 폴더 아래의 [데이터 디렉터리](/docs/conventions#data-directory) 내 구성된 스토리지 모듈(기본값은 파일 시스템)에 저장됩니다.

다음 폴더는 임의로 생성되며 상대적으로 중요하지 않은 ECH 구성 ID입니다. 무작위성은 핑거프린팅/추적을 방지하기 위해 사양에서 권장하는 사항입니다.

메타데이터 사이드카 파일은 Caddy가 마지막 게시 시점을 추적하는 데 도움을 줍니다. 이는 매번 설정을 다시 로드할 때마다 DNS 공급자에게 과도한 요청을 보내는 것을 방지합니다. 이 상태를 초기화해야 하는 경우 메타데이터 파일을 안전하게 삭제할 수 있습니다. 그러나 이로 인해 키가 교체되는 시점도 초기화될 수 있습니다. 파일로 들어가서 게시에 관한 정보만 지울 수도 있습니다.
