---
title: tls (Caddyfile 지시어)
---

<script>
ready(function() {
	// 페이지에서 일치하는 앵커 태그가 발견되면 모든 하위 지시어에 대한 링크를 추가합니다.
	addLinksToSubdirectives();
});
</script>

# tls

사이트에 대한 TLS를 설정합니다.

**Caddy의 기본 TLS 설정은 안전합니다. 타당한 이유가 있고 그 영향을 충분히 이해하는 경우에만 이 설정을 변경하세요.** 이 지시어는 주로 ACME 계정 이메일 주소를 지정하거나, ACME CA 엔드포인트를 변경하거나, 직접 발급받은 인증서를 제공하는 데 사용됩니다.

호환성 참고: 보안 프로토콜로서의 민감한 특성으로 인해, 새로운 마이너 또는 패치 릴리스에서 TLS 기본값이 의도적으로 조정될 수 있습니다. 오래되거나 취약한 TLS 버전, 암호(cipher), 기능 등은 언제든지 제거될 수 있습니다. 변경에 매우 민감한 배포 환경이라면 일정하게 유지되어야 하는 값을 명시적으로 지정하고 업그레이드에 주의를 기울여야 합니다. 거의 모든 경우에 기본 설정을 사용하는 것을 권장합니다.


## 구문 <a id="syntax"></a>

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** 은 Caddy의 내부적이고 로컬에서 신뢰할 수 있는 CA를 사용하여 이 사이트의 인증서를 생성함을 의미합니다. [`internal`](#internal) 발급자를 더 자세히 설정하려면 [`issuer`](#issuer) 하위 지시어를 사용하세요.

- **force_automate** 는 다른 관리형 인증서가 적용되는 경우에도 Caddy가 사이트의 인증서를 자동으로 관리하도록 강제합니다.

- **&lt;email&gt;** 은 사이트의 인증서를 관리하는 ACME 계정에 사용할 이메일 주소입니다. 모든 사이트에 대해 한 번에 설정하려면 [`email` 전역 옵션](/docs/caddyfile/options#email)을 대신 사용하는 것이 좋습니다.

<aside class="tip">

Let's Encrypt에서 인증서 만료가 임박했다는 이메일을 보낼 수 있지만, Caddy가 갱신 시 다른 발급자(예: ZeroSSL)를 선택했을 수 있으므로 오해의 소지가 있을 수 있습니다. 로그 또는 인증서 자체(예: 브라우저에서)를 확인하여 어떤 발급자가 사용되었는지, 만료일이 여전히 유효한지 확인하세요. 유효하다면 Let's Encrypt의 이메일은 무시해도 안전합니다.

</aside>

- **&lt;cert_file&gt;** 및 **&lt;key_file&gt;** 은 인증서 및 개인 키 PEM 파일의 경로입니다. 하나만 지정하는 것은 허용되지 않습니다.

- **protocols** <span id="protocols"/> 는 최소 및 최대 프로토콜 버전을 지정합니다. 무엇을 하고 있는지 잘 아는 경우가 아니라면 이를 변경하지 마세요. Caddy는 항상 현대적인 기본값을 사용하므로 이를 설정해야 하는 경우는 드뭅니다.
  
  기본 최소값: `tls1.2`, 기본 최대값: `tls1.3`

- **ciphers** <span id="ciphers"/> 는 우선순위 내림차순으로 암호 스위트(cipher suite) 이름 목록을 지정합니다. 무엇을 하고 있는지 잘 아는 경우가 아니라면 이를 변경하지 마세요. TLS 1.3의 경우 암호 스위트를 사용자 정의할 수 없으며, 모든 TLS 1.2 암호가 기본적으로 활성화되는 것은 아닙니다. 지원되는 이름은 다음과 같습니다(Go 표준 라이브러리의 우선순위 순):
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> 는 지원할 EC 그룹 목록을 지정합니다. 기본값을 변경하지 않는 것을 권장합니다. 지원되는 값은 다음과 같습니다:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> 은 TLS 핸드셰이크의 [ALPN 확장 <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN)에서 알릴 값 목록입니다.

- **load** <span id="load"/> 는 인증서+키 번들인 PEM 파일을 로드할 폴더 목록을 지정합니다.

- **ca** <span id="ca"/> 는 ACME CA 엔드포인트를 변경합니다. 테스트 시 [Let's Encrypt의 스테이징 엔드포인트 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)를 설정하거나 내부 ACME 서버를 설정할 때 주로 사용됩니다. (전체 Caddyfile에 대해 이 값을 변경하려면 `acme_ca` [전역 옵션](/docs/caddyfile/options)을 대신 사용하세요.)

- **ca_root** <span id="ca_root"/> 는 시스템 신뢰 저장소에 없는 경우, ACME CA 엔드포인트에 대해 신뢰할 수 있는 루트 인증서가 포함된 PEM 파일을 지정합니다.

- **key_type** <span id="key_type"/> 은 CSR을 생성할 때 사용할 키 유형입니다. 특정 요구 사항이 있는 경우에만 설정하세요.

- **dns** <span id="dns"/> 는 지정된 제공자 플러그인을 사용하여 [DNS 챌린지](/docs/automatic-https#dns-challenge)를 활성화합니다. 이 플러그인은 [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) 저장소 중 하나에서 가져와야 합니다. 각 제공자 플러그인은 이름 뒤에 고유한 구문을 가질 수 있습니다. 자세한 내용은 해당 문서를 참조하세요. 각 DNS 제공자에 대한 지원 유지는 커뮤니티의 노력으로 이루어집니다. [위키에서 사용 중인 제공자의 DNS 챌린지를 활성화하는 방법을 알아보세요.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> 은 DNS 챌린지 사용 시 DNS TXT 레코드가 나타날 때까지 대기하는 최대 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 전파 확인을 비활성화하려면 `-1`로 설정하세요. 기본값은 2분입니다.

- **propagation_delay** <span id="propagation_delay"/> 는 DNS 챌린지 사용 시 DNS TXT 레코드 전파 확인을 시작하기 전에 대기할 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값은 `0` (대기 없음)입니다.

- **dns_ttl** <span id="dns_ttl"/> 은 DNS 챌린지에 사용되는 `TXT` 레코드의 TTL을 설정하는 [기간 값](/docs/conventions#durations)입니다. 거의 필요하지 않습니다.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> 은 DNS 챌린지에 사용할 도메인을 재정의합니다. 이는 챌린지를 다른 도메인에 위임하기 위함입니다.

  주 도메인의 DNS 제공자에 사용할 수 있는 [DNS 플러그인 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns)이 없는 경우 이를 사용하고 싶을 수 있습니다. 대신 플러그인이 _있는_ 보조 도메인을 가리키는 `_acme-challenge` 하위 도메인이 포함된 `CNAME` 레코드를 주 도메인에 추가할 수 있습니다. 이 옵션은 플러그인의 특별한 지원을 필요로 하지 않습니다.
  
  ACME 발급자가 주 도메인에 대한 DNS 챌린지를 해결하려고 할 때, `CNAME`을 따라 보조 도메인으로 이동하여 `TXT` 레코드를 찾게 됩니다.

  **참고:** 여기에는 CNAME 레코드의 전체 정규화된 이름(canonical name)을 값으로 사용하세요. `_acme-challenge` 하위 도메인은 자동으로 앞에 붙지 않습니다.

- **resolvers** <span id="resolvers"/> 는 DNS 챌린지를 수행할 때 사용할 DNS 리졸버를 사용자 정의합니다. 이는 시스템 리졸버나 기본 리졸버보다 우선합니다. 여기서 설정하면 리졸버가 모든 구성된 인증서 발급자에게 전파됩니다.

  이는 일반적으로 IP 주소 목록입니다. 예를 들어, [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns)를 사용하려면 다음과 같이 합니다:

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> 는 CA에서 제공한 키 ID 및 MAC 키를 사용하여 이 사이트에 대한 ACME 외부 계정 바인딩(External Account Binding, EAB)을 설정합니다.

- **on_demand** <span id="on_demand"/> 는 사이트 블록의 주소에 지정된 호스트 이름에 대해 [온디맨드 TLS(On-Demand TLS)](/docs/automatic-https#on-demand-tls)를 활성화합니다. **보안 경고:** 남용을 방지하기 위해 [`on_demand_tls` 전역 옵션](/docs/caddyfile/options#on-demand-tls)을 함께 설정하지 않는 한, 운영 환경에서 이를 사용하는 것은 안전하지 않습니다.

- **reuse_private_keys** <span id="reuse_private_keys"/> 는 인증서 갱신 시 개인 키 재사용을 활성화합니다. 기본적으로 피닝(pinning)을 방지하고 키 노출 범위를 줄이기 위해 모든 새 인증서에 대해 새 키가 생성됩니다. 키 피닝은 업계 베스트 프랙티스에 어긋납니다. 특정 이유가 없는 한 이 옵션은 권장되지 않으며, 향후 버전에서 제거될 수 있습니다.

- **client_auth** <span id="client_auth"/> 는 TLS 클라이언트 인증을 활성화하고 설정합니다:
  - **mode** <span id="mode"/> 는 클라이언트를 인증하는 모드입니다. 허용되는 값은 다음과 같습니다:

    | 모드 | 설명 |
    | --- | --- |
    | request | 클라이언트에게 인증서를 요청하지만, 없어도 허용함. 검증하지 않음 |
    | require | 클라이언트가 인증서를 제시해야 하지만, 검증하지 않음 |
    | verify_if_given | 클라이언트에게 인증서를 요청함. 없어도 허용하지만, 있다면 검증함 |
    | require_and_verify | 클라이언트가 검증된 유효한 인증서를 제시해야 함 |

    기본값: `trust_pool` 모듈이 제공되면 `require_and_verify`, 그렇지 않으면 `require`.
	
  - **trust_pool** <span id="trust_pool"/> 는 클라이언트 인증서를 검증할 인증서 제공 CA(인증 기관)의 소스를 설정합니다.
	
	신뢰할 수 있는 인증서 풀을 제공하는 데 사용되는 인증 기관 및 해당 세그먼트 내의 설정은 구성된 신뢰 풀 소스 모듈에 따라 달라집니다. Caddy에서 사용 가능한 표준 모듈은 [아래에 나열되어 있습니다](#trust-pool-providers). 타사 모듈을 포함한 전체 모듈 목록은 [`trust_pool` JSON 문서](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool)에 나열되어 있습니다.

    여러 개의 `trusted_*` 지시어를 사용하여 여러 CA 또는 리프(leaf) 인증서를 지정할 수 있습니다. 리프 인증서 중 하나로 나열되지 않았거나 지정된 CA 중 하나에 의해 서명되지 않은 클라이언트 인증서는 **mode**에 따라 거부됩니다.

  - **verifier** <span id="verifier"/> 는 사용자 정의 클라이언트 인증서 검증기 모듈의 사용을 활성화합니다. 이를 통해 인증서가 취소되지 않았는지 확인하는 등 사용자 정의 클라이언트 인증 확인을 수행할 수 있습니다.

- **issuer** <span id="issuer"/> 는 사용자 정의 인증서 발급자 또는 인증서를 가져올 소스를 설정합니다.

  어떤 발급자가 사용되는지와 이 세그먼트에서 뒤따르는 옵션은 사용 가능한 [발급자 모듈](#issuers)에 따라 달라집니다. `ca` 및 `dns`와 같은 다른 하위 지시어 중 일부는 실제로는 `acme` 발급자를 설정하기 위한 단축어이므로(이 하위 지시어는 나중에 추가됨), 이 지시어와 다른 지시어를 함께 지정하는 것은 혼란을 줄 수 있어 금지됩니다.
  
  이 하위 지시어는 중복 발급자를 설정하기 위해 여러 번 지정할 수 있습니다. 하나가 인증서 발급에 실패하면 다음 발급자가 시도됩니다.

- **get_certificate** <span id="get_certificate"/> 는 핸드셰이크 시에 [관리자 모듈](#certificate-managers)로부터 인증서를 가져오도록 활성화합니다.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> 는 TLS 암호를 파일로 로깅하는 기능을 활성화합니다. 이는 `SSLKEYLOGFILE`로도 알려져 있습니다. Wireshark 또는 다른 도구에서 파싱할 수 있는 NSS 키 로그 형식을 사용합니다. ⚠️ **보안 경고:** 이는 다른 프로그램이나 도구가 TLS 연결을 복호화할 수 있게 하여 보안을 완전히 무너뜨리므로 안전하지 않습니다. 그러나 이 기능은 디버깅 및 문제 해결에 유용할 수 있습니다.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> 는 0과 1 사이의 비율로, Caddy가 인증서 갱신을 시도하기 전에 남아 있어야 하는 인증서 수명을 결정합니다. 예를 들어, 인증서 수명이 90일이고 이 비율이 `0.3333`(기본값)인 경우, Caddy는 만료 전 30일 이하로 남았을 때 지속적으로 인증서 갱신을 시도합니다. [`renewal_window_ratio` 전역 옵션](/docs/caddyfile/options#renewal_window_ratio)으로 전역적으로 설정할 수도 있습니다.

  이를 변경해야 하는 경우는 거의 없지만, CA의 발급 시간이 매우 긴 경우 인증서 수명 후반에 갱신하도록 설정하는 데 유용할 수 있습니다.

  ACME 발급자가 [ARI 확장](https://datatracker.ietf.org/doc/rfc9773/)을 구현할 수 있으므로 이는 제안일 뿐이라는 점을 유념하세요. ARI는 ACME 클라이언트(이 경우 Caddy)가 갱신을 시도해야 하는 윈도우를 지정하며, 해당 윈도우는 이 비율과 일치하지 않을 수 있습니다.

- **force_automate** 는 인라인으로 지정하는 것과 동일합니다 (위 참조).

### 신뢰 풀 제공자 (Trust Pool Providers) <a id="trust-pool-providers"></a>

다음은 `trust_pool` 하위 지시어에서 사용할 수 있는 표준 신뢰 풀 제공자입니다:

#### inline

`inline` 모듈은 Caddyfile에 직접 나열된 신뢰할 수 있는 루트 인증서를 base64 DER 인코딩 형식으로 파싱합니다. `trust_der` 지시어는 여러 번 반복될 수 있습니다.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> 는 클라이언트 인증서를 검증하는 데 사용할 base64 DER 인코딩된 CA 인증서입니다.

#### file

`file` 모듈은 디스크의 PEM 파일에서 신뢰할 수 있는 루트 인증서를 읽습니다. `pem_file` 지시어는 같은 줄에 여러 파일 경로를 받을 수 있으며 여러 번 반복될 수 있습니다.

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> 는 클라이언트 인증서를 검증하는 데 사용할 PEM CA 인증서 파일의 경로입니다.

#### pki_root

`pki_root` 모듈은 [PKI 앱](/docs/caddyfile/options#pki-options)에 정의된 인증 기관에서 _루트_ 및 신뢰 인증서를 가져옵니다. `authority` 지시어는 동시에 여러 인증 기관을 받을 수 있으며 여러 번 반복될 수 있습니다.

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> 는 PKI 앱에 설정된 인증 기관의 이름입니다.

#### pki_intermediate

`pki_intermediate` 모듈은 [PKI 앱](/docs/caddyfile/options#pki-options)에 정의된 인증 기관에서 _중간_ 및 신뢰 인증서를 가져옵니다. `authority` 지시어는 동시에 여러 인증 기관을 받을 수 있으며 여러 번 반복될 수 있습니다.

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> 는 PKI 앱에 설정된 인증 기관의 이름입니다.

#### storage

`storage` 모듈은 Caddy [저장소(storage)](/docs/caddyfile/options#storage)에서 신뢰할 수 있는 인증서 루트를 추출합니다. `authority` 지시어는 동시에 여러 인증 기관을 받을 수 있으며 여러 번 반복될 수 있습니다.

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> 는 사용할 선택적 저장소 모듈입니다. 지정하지 않으면 기본 저장소 모듈이 사용됩니다. 지정하는 경우 한 번만 지정할 수 있습니다.

- **keys** <span id="keys"/> 는 인증서의 PEM 파일이 저장된 저장소 키 목록입니다. 이 지시어는 같은 줄에 여러 값을 받을 수 있으며 여러 번 지정할 수 있습니다.

#### http

`http` 모듈은 HTTP 엔드포인트에서 신뢰할 수 있는 인증서를 가져옵니다. `endpoints` 지시어는 동시에 여러 엔드포인트를 받을 수 있으며 여러 번 반복될 수 있습니다.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> 는 인증서를 가져올 HTTP 엔드포인트 목록입니다. 이 지시어는 같은 줄에 여러 값을 받을 수 있으며 여러 번 지정할 수 있습니다.

- **tls** <span id="tls"/> 는 HTTP 엔드포인트에 연결할 때 사용할 선택적 TLS 설정입니다. 세그먼트 파싱은 [다음 섹션](#tls-1)에 정의되어 있습니다.

##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> 는 신뢰 풀 제공자를 정의하는 선택적 지시어입니다. 설정은 [`trust_pool`](#trust_pool)과 동일한 동작을 따릅니다. 지정하는 경우 한 번만 지정할 수 있습니다.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> 는 TLS 핸드셰이크 검증을 끕니다. 이는 연결을 안전하지 않게 만들고 중간자 공격(man-in-the-middle attacks)에 취약하게 만듭니다. _운영 환경에서 사용하지 마세요._ 검증은 시스템에서 신뢰하는 인증 기관 또는 [`ca`](#ca) 지시어에 의해 결정된 인증 기관에 대해 수행됩니다.

- **handshake_timeout** <span id="handshake_timeout"/> 은 TLS 핸드셰이크가 완료될 때까지 대기하는 최대 [기간](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **server_name** <span id="server_name"/> 은 TLS 핸드셰이크에서 수신된 인증서를 검증할 때 사용되는 서버 이름을 설정합니다. 기본적으로 업스트림 주소의 호스트 부분이 사용됩니다.

- **renegotiation** <span id="renegotiation"/> 은 TLS 재협상(renegotiation) 레벨을 설정합니다. TLS 재협상은 첫 번째 핸드셰이크 이후에 후속 핸드셰이크를 수행하는 행위입니다. 레벨은 다음 중 하나일 수 있습니다:
  - `never` (기본값) 재협상을 비활성화합니다.
  - `once` 원격 서버가 연결당 한 번 재협상을 요청할 수 있도록 허용합니다.
  - `freely` 원격 서버가 반복적으로 재협상을 요청할 수 있도록 허용합니다.

### 검증기 (Verifiers) <a id="verifiers"></a>

클라이언트 인증서 검증기 모듈은 `trust_pool`이 구성된 경우, 신뢰할 수 있는 인증 기관에서 발급되었는지 확인한 후에 실행됩니다. 현재 표준 Caddy에 포함된 검증기는 `leaf` 하나입니다.

#### Leaf

`leaf` 검증기는 클라이언트 인증서가 정의된 허용된 인증서 세트 중 하나인지 확인합니다. 인증서 세트는 [로더(loader)](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders) 모듈을 사용하여 로드됩니다.

##### 로더 (Loaders)

표준 Caddy 배포판에는 4개의 로더가 포함되어 있으며, 그중 3개는 Caddyfile에서 사용할 수 있습니다.

###### File

`file` 로더는 지정된 PEM 파일에서 인증서 세트를 로드합니다.

```caddy-d
... file <pem_files...>
```

###### Folder

`folder` 로더는 명명된 디렉토리를 재귀적으로 탐색하여 수락된 클라이언트 인증서로 로드할 PEM 파일을 찾습니다.

```caddy-d
... folder <folders...>
```

###### PEM

`pem` 로더는 Caddyfile에 인라인된 PEM 형식의 인증서를 수락합니다.

```caddy-d
... pem <pem_strings...>
```

### 발급자 (Issuers) <a id="issuers"></a>

다음 발급자들은 `tls` 지시어와 함께 기본으로 제공됩니다:

#### acme

ACME 프로토콜을 사용하여 인증서를 가져옵니다. `acme`는 (Let's Encrypt를 사용하는) 기본 발급자이므로 일반적으로 명시적으로 설정할 필요가 없습니다.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> 은 ACME CA 디렉토리의 URL입니다.
  
  기본값: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> 은 챌린지 재시도 시 사용할 선택적 폴백 디렉토리입니다. 모든 챌린지가 실패하면 재시도 중에 이 엔드포인트가 사용됩니다. CA에 운영 엔드포인트의 속도 제한(rate limit)을 피하고 싶은 스테이징 엔드포인트가 있는 경우 유용합니다.

  기본값: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> 은 ACME 계정 연락용 이메일 주소입니다.

- **timeout** <span id="timeout"/> 은 ACME 작업이 타임아웃되기 전까지 대기할 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다.

- **disable_http_challenge** <span id="disable_http_challenge"/> 는 HTTP 챌린지를 비활성화합니다.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> 는 TLS-ALPN 챌린지를 비활성화합니다.

- **alt_http_port** <span id="alt_http_port"/> 는 HTTP 챌린지를 서비스할 대체 포트입니다. 포트 80에서 발생해야 하므로 이 대체 포트로 패킷을 전달해야 합니다.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> 는 TLS-ALPN 챌린지를 서비스할 대체 포트입니다. 포트 443에서 발생해야 하므로 이 대체 포트로 패킷을 전달해야 합니다.

- **eab** <span id="eab"/> 는 일부 ACME CA에서 요구할 수 있는 외부 계정 바인딩(External Account Binding)을 지정합니다.

- **trusted_roots** <span id="trusted_roots"/> 는 ACME CA 서버에 연결할 때 신뢰할 루트 인증서(PEM 파일 이름)입니다.

- **dns** <span id="dns"/> 는 DNS 챌린지를 설정합니다. [`dns` 전역 옵션](/docs/caddyfile/options#dns)에서 전역적으로 적용 가능한 DNS 제공자 모듈을 지정하지 않는 한, 여기서 제공자를 설정해야 합니다.

- **propagation_timeout** <span id="propagation_timeout"/> 은 DNS 챌린지 사용 시 DNS TXT 레코드가 나타날 때까지 대기하는 최대 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 전파 확인을 비활성화하려면 `-1`로 설정하세요. 기본값은 2분입니다.

- **propagation_delay** <span id="propagation_delay"/> 는 DNS 챌린지 사용 시 DNS TXT 레코드 전파 확인을 시작하기 전에 대기할 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값은 0 (대기 없음)입니다.

- **dns_ttl** <span id="dns_ttl"/> 은 DNS 챌린지에 사용되는 `TXT` 레코드의 TTL을 설정하는 [기간 값](/docs/conventions#durations)입니다. 거의 필요하지 않습니다.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> 은 DNS 챌린지에 사용할 도메인을 재정의합니다. 이는 챌린지를 다른 도메인에 위임하기 위함입니다.

  주 도메인의 DNS 제공자에 사용할 수 있는 [DNS 플러그인 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns)이 없는 경우 이를 사용하고 싶을 수 있습니다. 대신 플러그인이 _있는_ 보조 도메인을 가리키는 `_acme-challenge` 하위 도메인이 포함된 `CNAME` 레코드를 주 도메인에 추가할 수 있습니다. 이 옵션은 플러그인의 특별한 지원을 필요로 하지 않습니다.
  
  ACME 발급자가 주 도메인에 대한 DNS 챌린지를 해결하려고 할 때, `CNAME`을 따라 보조 도메인으로 이동하여 `TXT` 레코드를 찾게 됩니다.

  **참고:** 여기에는 CNAME 레코드의 전체 정규화된 이름(canonical name)을 값으로 사용하세요. `_acme-challenge` 하위 도메인은 자동으로 앞에 붙지 않습니다.

- **resolvers** <span id="resolvers"/> 는 DNS 챌린지를 수행할 때 사용할 DNS 리졸버를 사용자 정의합니다. 이는 시스템 리졸버나 기본 리졸버보다 우선합니다. 여기서 설정하면 리졸버가 모든 구성된 인증서 발급자에게 전파됩니다.

  이는 일반적으로 IP 주소 목록입니다. 예를 들어, [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns)를 사용하려면 다음과 같이 합니다:

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> 는 Caddy가 선호해야 하는 인증서 체인을 지정합니다. CA가 여러 체인을 제공하는 경우 유용합니다. 다음 옵션 중 하나를 사용하세요:
	- **smallest** <span id="smallest"/> 는 바이트 수가 가장 적은 체인을 선호하도록 Caddy에 지시합니다.

	- **root_common_name** <span id="root_common_name"/> 은 하나 이상의 일반 이름(common name) 목록입니다. Caddy는 지정된 일반 이름 중 하나 이상과 일치하는 루트를 가진 첫 번째 체인을 선택합니다.

	- **any_common_name** <span id="any_common_name"/> 은 하나 이상의 일반 이름 목록입니다. Caddy는 지정된 일반 이름 중 하나 이상과 일치하는 발급자를 가진 첫 번째 체인을 선택합니다.

- **profile** 은 인증서를 주문할 때 적용할 [ACME 프로필](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/)의 이름입니다. 이를 지정하는 경우 구성된(암시적 또는 명시적) 모든 CA가 이 프로필을 지원해야 합니다. 사용 가능한 프로필은 해당 CA의 문서를 참조하세요. 일부 CA는 프로필을 지원하지 않을 수 있습니다. 실험적 기능: ACME 프로필 사양은 아직 초안 상태이므로, 이 기능/함수는 변경되거나 제거될 수 있습니다.


#### zerossl

[ZeroSSL의 독자적인 인증서 발급 API](https://zerossl.com/documentation/api/)를 사용하여 인증서를 가져옵니다. API 키가 필요하며 요금제에 따라 결제가 필요할 수도 있습니다. 이 발급자는 [ZeroSSL의 ACME 엔드포인트](https://zerossl.com/documentation/acme/)와는 다르다는 점에 유의하세요. ZeroSSL의 ACME 엔드포인트를 사용하려면, 위에서 설명한 `acme` 발급자를 ZeroSSL의 ACME 디렉토리 엔드포인트로 설정하여 사용하세요.

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> 는 인증서 수명을 정의합니다. 특정 값만 허용됩니다. 자세한 내용은 [ZeroSSL 문서](https://zerossl.com/documentation/api/create-certificate/)를 참조하세요.
<!--   
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> 는 80번 포트가 아닌 경우 ZeroSSL의 HTTP 검증을 완료하는 데 사용할 포트입니다.
- **dns** <span id="zerossl_dns"/> 는 자동 레코드 프로비저닝을 위해 지정된 DNS 제공자를 사용하여 CNAME 검증 방법을 활성화합니다. DNS 제공자 플러그인은 [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) 저장소에서 설치해야 합니다. 각 제공자 플러그인은 이름 뒤에 고유한 구문을 가질 수 있습니다. 자세한 내용은 해당 문서를 참조하세요. 각 DNS 제공자에 대한 지원 유지는 커뮤니티의 노력으로 이루어집니다.
- **propagation_delay** <span id="zerossl_propagation_delay"/> 는 CNAME 레코드 전파를 확인하기 전에 대기할 시간입니다.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> 은 전파 확인을 포기하기 전까지 CNAME 레코드 전파를 대기할 시간입니다.
- **resolvers** <span id="zerossl_resolvers"/> 는 CNAME 레코드 전파를 확인할 때 사용할 사용자 정의 DNS 리졸버를 정의합니다.
- **dns_ttl** <span id="zerossl_dns_ttl"/> 은 검증 프로세스의 일부로 생성된 CNAME 레코드의 TTL을 설정합니다.



#### internal

내부 인증 기관에서 인증서를 가져옵니다.

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> 는 사용할 내부 CA의 이름입니다. 기본값: `local`. `local` CA를 설정하거나 대체 CA를 생성하려면 [PKI 앱 전역 옵션](/docs/caddyfile/options#pki-options)을 참조하세요.

  기본적으로 루트 CA 인증서의 수명은 `3600d`(10년)이고 중간 인증서의 수명은 `7d`(7일)입니다.

  Caddy는 루트 CA 인증서를 시스템 신뢰 저장소에 설치하려고 시도하지만, Caddy가 비특권 사용자로 실행되거나 Docker 컨테이너에서 실행되는 경우 실패할 수 있습니다. 이 경우 [`caddy trust`](/docs/command-line#caddy-trust) 명령을 사용하거나 [컨테이너 밖으로 복사](/docs/running#usage)하여 루트 CA 인증서를 수동으로 설치해야 합니다.

- **lifetime** <span id="lifetime"/> 은 내부적으로 발급된 리프 인증서의 유효 기간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값: `12h`. 꼭 필요한 경우가 아니라면 이를 변경하는 것을 권장하지 않습니다. 중간 인증서의 수명보다 짧아야 합니다.

- **sign_with_root** <span id="sign_with_root"/> 는 중간 인증서 대신 루트 인증서가 발급자가 되도록 강제합니다. 이는 권장되지 않으며 장치/클라이언트가 인증서 체인을 제대로 검증하지 못하는 경우(매우 드묾)에만 사용해야 합니다.



### 인증서 관리자 (Certificate Managers) <a id="certificate-managers"></a>

인증서 관리자 모듈은 발급자 모듈과 다릅니다. 관리자 모듈은 외부 도구 또는 서비스가 인증서를 갱신하도록 유지하는 반면, 발급자 모듈은 Caddy 자체가 인증서를 관리함을 의미합니다. (발급자 모듈은 인증서 서명 요청(CSR)을 입력으로 받지만, 인증서 관리자 모듈은 TLS ClientHello를 입력으로 받습니다.)

다음 관리자 모듈들은 `tls` 지시어와 함께 기본으로 제공됩니다:

#### tailscale

로컬에서 실행 중인 [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) 인스턴스에서 인증서를 가져옵니다. [Tailscale 계정에서 HTTPS가 활성화되어 있어야 하며](https://tailscale.com/kb/1153/enabling-https/) (또는 오픈 소스 [Headscale 서버 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)), Caddy 프로세스가 루트 권한으로 실행 중이거나 `tailscaled`가 Caddy 사용자에게 [인증서를 가져올 수 있는 권한](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)을 주도록 설정해야 합니다.

_**참고: 이는 일반적으로 필요하지 않습니다!** Caddy는 별도의 설정 없이 모든 `*.ts.net` 도메인에 대해 자동으로 Tailscale을 사용합니다._

```caddy-d
get_certificate tailscale  # 대개 불필요합니다!
```


#### http

HTTP(S) 요청을 하여 인증서를 가져옵니다. 응답의 상태 코드는 `200`이어야 하며 본문에는 개인 키뿐만 아니라 전체 인증서(중간 인증서 포함)가 포함된 PEM 체인이 있어야 합니다.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> 은 요청을 보낼 정규화된 URL입니다. 성능상의 이유로 로컬 엔드포인트를 사용하는 것이 강력히 권장됩니다. URL에는 다음 쿼리 문자열 파라미터가 추가됩니다: 

  - `server_name`: SNI 값
  - `signature_schemes`: 서명 알고리즘의 16진수 ID가 쉼표로 구분된 목록
  - `cipher_suites`: 암호 스위트의 16진수 ID가 쉼표로 구분된 목록
  - `local_ip`: 클라이언트가 요청을 보낸 IP 주소



## 예시 <a id="examples"></a>

사용자 정의 인증서와 키를 사용합니다. 인증서에는 사이트 주소와 일치하는 [SAN](https://en.wikipedia.org/wiki/Subject_Alternative_Name)이 있어야 합니다:

```caddy
example.com {
	tls cert.pem key.pem
}
```

ACME / Let's Encrypt를 통한 공개 인증서 대신, 현재 사이트 블록의 모든 호스트에 대해 [로컬에서 신뢰할 수 있는](/docs/automatic-https#local-https) 인증서를 사용합니다 (개발 환경에서 유용함):

```caddy
example.com {
	tls internal
}
```

로컬에서 신뢰할 수 있는 인증서를 사용하지만 백그라운드 대신 [온디맨드(On-Demand)](/docs/automatic-https#on-demand-tls) 방식으로 관리합니다. 이를 통해 모든 도메인을 Caddy 인스턴스로 향하게 하고 자동으로 인증서를 프로비저닝할 수 있습니다. 공격자가 서버 리소스를 고갈시키는 데 사용할 수 있으므로 Caddy 인스턴스가 공개적으로 액세스 가능한 경우에는 이를 사용해서는 안 됩니다:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

내부 CA에 대한 사용자 정의 옵션을 지정합니다 (`tls internal` 단축어를 사용할 수 없음):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

ACME 계정의 이메일 주소를 지정합니다 (모든 사이트에 단 하나의 이메일만 사용되는 경우 `email` [전역 옵션](/docs/caddyfile/options)을 사용하는 것이 좋습니다):

```caddy
example.com {
	tls your@email.com
}
```

환경 변수의 계정 자격 증명을 사용하여 Cloudflare에서 관리되는 도메인에 대한 DNS 챌린지를 활성화합니다. 이는 DNS 검증이 필요한 와일드카드 인증서 지원을 가능하게 합니다:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Caddy가 직접 관리하는 대신 HTTP를 통해 인증서 체인을 가져옵니다. [`get_certificate`](#certificate-managers)는 ACME 발급을 트리거하는 대신 모듈을 사용하여 인증서를 가져오는 [`on_demand`](#on_demand)가 활성화되어 있음을 의미합니다:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

TLS 클라이언트 인증을 활성화하고 [`trust_pool`](#trust_pool) `file` 제공자를 통해 제공된 모든 CA에 대해 검증된 유효한 인증서를 클라이언트가 제시하도록 요구합니다:

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
