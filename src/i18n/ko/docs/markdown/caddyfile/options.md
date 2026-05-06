---
title: 전역 옵션 (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


# 전역 옵션 <a id="global-options"></a>

Caddyfile에는 전역적으로 적용되는 옵션을 지정하는 방법이 있습니다. 일부 옵션은 기본값으로 작동하고, 다른 옵션은 특정 사이트가 아닌 HTTP 서버 전체를 커스텀하며, 또 다른 옵션은 Caddyfile [어댑터](/docs/config-adapters)의 동작을 커스텀합니다.

Caddyfile의 가장 윗부분은 **전역 옵션 블록**이 될 수 있습니다. 이 블록은 키가 없는 블록입니다:

```caddy
{
	...
}
```

이 블록은 최대 하나만 존재할 수 있으며, 반드시 Caddyfile의 첫 번째 블록이어야 합니다.

사용 가능한 옵션은 다음과 같습니다 (각 옵션을 클릭하면 해당 문서로 이동합니다):

```caddy
{
	# 일반 옵션 (General Options)
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS 옵션 (TLS Options)
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# 서버 옵션 (Server Options)
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# 파일 시스템 (File Systems)
	filesystem <name> <module> {
		<options...>
	}

	# PKI 옵션 (PKI Options)
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# 이벤트 옵션 (Event options)
	events {
		on <event> <handler...>
	}
}
```


## 일반 옵션 <a id="general-options"></a>

##### `debug`
디버그 모드를 활성화하여 [기본 로거](#log)의 로그 레벨을 `DEBUG`로 설정합니다. 이는 트러블슈팅 시 유용한 더 자세한 정보를 보여줍니다 (운영 환경에서는 매우 상세하게 출력됩니다). [커뮤니티 포럼](https://caddy.community)에 도움을 요청하기 전에 이 옵션을 활성화하는 것을 권장합니다. 예를 들어, Caddyfile 상단에 다른 전역 옵션 없이 사용할 경우:

```caddy
{
	debug
}
```


##### `http_port`
서버가 HTTP에 사용할 포트입니다.

**내부 전용입니다.** 클라이언트의 HTTP 포트를 변경하지 않습니다. 이는 일반적으로 내부 네트워크에서 라우팅 목적으로 Caddy에 도달하기 전에 `80` 포트를 다른 포트(예: `8080`)로 포트 포워딩해야 하는 경우에 사용됩니다.

기본값: `80`


##### `https_port`
서버가 HTTPS에 사용할 포트입니다.

**내부 전용입니다.** 클라이언트의 HTTPS 포트를 변경하지 않습니다. 이는 일반적으로 내부 네트워크에서 라우팅 목적으로 Caddy에 도달하기 전에 `443` 포트를 다른 포트(예: `8443`)로 포트 포워딩해야 하는 경우에 사용됩니다.

기본값: `443`


##### `default_bind`
사이트에서 [`bind` 지시어](/docs/caddyfile/directives/bind)를 사용하지 않을 경우 모든 사이트에 사용될 기본 바인딩 주소입니다. 기본값: 비어 있음 (모든 인터페이스에 바인딩됨).

<aside class="tip">

이 설정은 Caddyfile에 의해 생성된 서버에만 적용된다는 점에 유의하세요. 즉, HTTP에서 HTTPS로의 리다이렉트를 위해 [자동 HTTPS](/docs/automatic-https)가 생성한 HTTP 서버에는 이 바인딩 주소가 상속되지 않습니다. 이를 해결하려면 `http://` 사이트(지시어 없이 비어 있어도 됨)를 선언하여 Caddyfile이 어댑팅될 때 바인딩 주소를 받을 수 있도록 하세요.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
HTTP 핸들러 지시어에 순서를 할당합니다. HTTP 핸들러는 순차적인 체인으로 실행되므로 핸들러가 올바른 순서로 실행되는 것이 중요합니다. 표준 지시어는 [미리 정의된 순서](/docs/caddyfile/directives#directive-order)가 있지만, 서드파티 HTTP 핸들러 모듈을 사용하는 경우 이 옵션을 사용하거나 지시어를 [`route` 블록](/docs/caddyfile/directives/route)에 배치하여 순서를 명시적으로 정의해야 합니다. 순서는 절대적(`first` 또는 `last`)으로 지정하거나 다른 지시어에 대한 상대적(`before` 또는 `after`)으로 지정할 수 있습니다.

예를 들어, [`replace-response` 플러그인](https://github.com/caddyserver/replace-response)을 사용하려면 응답이 인코딩되기 전에 교체 작업을 수행할 수 있도록 해당 지시어가 `encode` 뒤에 오도록 설정해야 합니다 (응답은 핸들러 체인을 따라 내려가는 것이 아니라 올라가기 때문입니다):

```caddy
{
	order replace after encode
}
```


##### `storage`
Caddy의 스토리지 메커니즘을 구성합니다. 기본값은 [`file_system`](/docs/json/storage/file_system/)입니다. 플러그인으로 제공되는 다른 많은 [스토리지 모듈](/docs/json/storage/)을 사용할 수 있습니다.

예를 들어, 파일 시스템의 스토리지 위치를 변경하려면:

```caddy
{
	storage file_system /path/to/custom/location
}
```

스토리지 모듈 커스텀은 일반적으로 여러 Caddy 인스턴스에서 스토리지의 인증서와 키를 동기화하여 모두 동일한 정보를 사용하도록 할 때 필요합니다. 자세한 내용은 [자동 HTTPS의 스토리지 섹션](/docs/automatic-https#storage)을 참조하세요.


##### `storage_clean_interval`
오래되거나 만료된 자산을 스토리지에서 스캔하고 제거하는 빈도입니다. 이 스캔 작업은 스토리지 모듈에서 많은 읽기(및 목록 조회) 작업을 수행하므로 대규모 배포의 경우 더 긴 간격을 선택하세요. [기간 값](/docs/conventions#durations)을 허용합니다.

스토리지는 프로세스가 처음 시작될 때 항상 정리됩니다. 그 후, 이전 정리가 이 간격의 절반 미만 시간 내에 완료된 경우 이전 정리가 시작된 후 이 기간이 지나면 새로운 정리가 시작됩니다 (그렇지 않으면 다음 시작은 건너뜁니다).

기본값: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
[관리 API 엔드포인트](/docs/api)를 커스텀합니다. 플레이스홀더를 허용합니다. [네트워크 주소](/docs/conventions#network-addresses)를 받습니다.

기본값: `localhost:2019` (`CADDY_ADMIN` 환경 변수가 설정되지 않은 경우).

`off`로 설정하면 관리 엔드포인트가 비활성화됩니다. 비활성화되면 [`caddy reload` 명령](/docs/command-line#caddy-reload)이 관리 API를 사용하여 실행 중인 서버에 새 설정을 푸시하므로, 서버를 중지하고 다시 시작하지 않고는 **설정 변경이 불가능**해집니다.

실행 중인 서버의 주소가 기본값에서 변경된 경우, 호환되는 [명령어](/docs/command-line)에서 `--address` CLI 플래그를 사용하여 현재 관리 엔드포인트를 지정해야 함을 기억하세요.

또한 다음 서브 옵션을 지원합니다:

- **origins**는 엔드포인트에 연결할 수 있는 [오리진(origins)](https://developer.mozilla.org/ko/docs/Glossary/Origin) 목록을 구성합니다.

  기본값은 지능적으로 선택됩니다:
  - 수신 주소가 루프백(예: `localhost`, 루프백 IP 또는 유닉스 소켓)인 경우 허용되는 오리진은 `localhost`, `::1`, `127.0.0.1`이며 수신 주소 포트와 결합됩니다 (따라서 `localhost:2019`는 유효한 오리진입니다).
  - 수신 주소가 루프백이 아닌 경우 허용되는 오리진은 수신 주소와 동일합니다.

  수신 주소 호스트가 와일드카드 인터페이스(빈 문자열, `0.0.0.0` 또는 `[::]`)가 아닌 경우 `Host` 헤더 강제가 수행됩니다. 실질적으로 이는 인터페이스가 `localhost`이므로 기본적으로 `Host` 헤더가 `origins`에 있는지 확인함을 의미합니다. 하지만 와일드카드 인터페이스가 있는 `:2020`과 같은 주소의 경우 `Host` 헤더 검증이 수행되지 않습니다.

- **enforce_origin**은 `Origin` 요청 헤더의 강제 검증을 수행합니다. 이는 클라이언트가 CORS 헤더를 보내거나 클라이언트가 `Sec-Fetch-Mode: no-cors`를 사용하여 CORS를 명시적으로 비활성화할 때마다 암시적으로 수행됩니다. 그 외의 경우, 이 옵션은 수신 주소가 와일드카드 인터페이스이고(`Host`가 검증되지 않으므로) 관리 API가 공용 인터넷에 노출될 때 가장 유용합니다. 이는 CORS 프리플라이트 체크를 활성화하고 `Origin` 헤더가 `origins` 목록에 대해 검증되도록 합니다. 개발 머신에서 Caddy를 실행하고 웹 브라우저에서 관리 API에 액세스해야 하는 경우에만 이 옵션을 사용하세요.

예를 들어, 관리 API를 다른 포트의 모든 인터페이스에 노출하려면 다음과 같이 설정합니다. ⚠️ 이 포트는 **공개적으로 노출되어서는 안 됩니다.** 그렇지 않으면 누구나 서버를 제어할 수 있습니다. 공개해야 하는 경우 오리진 강제 검증 활성화를 고려하세요:

```caddy
{
	admin :2020
}
```

관리 API를 끄려면 다음과 같이 설정합니다. ⚠️ 이 경우 서버를 중지하고 시작하지 않고는 **설정 재로드가 불가능**해집니다:

```caddy
{
	admin off
}
```

파일 권한을 통해 액세스 제어가 가능한 [유닉스 소켓](/docs/conventions#network-addresses)을 관리 API에 사용하려면:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

일치하는 `Origin` 헤더가 있는 요청만 허용하려면:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`

관리 API를 통해 수행된 설정 변경 사항을 잃지 않도록 현재 JSON 설정을 [설정 디렉토리](/docs/conventions#configuration-directory)에 유지할지 여부를 제어합니다. 현재는 `off` 옵션만 지원됩니다. 기본적으로 설정은 유지됩니다.

```caddy
{
	persist_config off
}
```



##### `log`
이름이 지정된 로거를 구성합니다.

동작을 커스텀할 특정 로거를 나타내기 위해 이름을 전달할 수 있습니다. 이름을 지정하지 않으면 `default` 로거의 동작이 수정됩니다. `default` 로거와 [Caddy의 로깅 작동 방식](/docs/logging)에 대한 자세한 설명을 읽어보실 수 있습니다.

`log`를 여러 번 사용하여 서로 다른 이름을 가진 여러 로거를 구성할 수 있습니다.

이는 HTTP 요청 로깅(액세스 로그라고도 함)만 구성하는 [`log` 지시어](/docs/caddyfile/directives/log)와 다릅니다. `log` 전역 옵션은 지시어와 설정 구조를 공유하며(`include` 및 `exclude` 제외), 전체 문서는 지시어 페이지에서 찾을 수 있습니다.

- **output**은 로그를 기록할 위치를 구성합니다.

  전체 문서는 [`log` 지시어](/docs/caddyfile/directives/log#output-modules)를 참조하세요.

- **format**은 로그를 인코딩하거나 형식을 지정하는 방법을 설명합니다.

  전체 문서는 [`log` 지시어](/docs/caddyfile/directives/log#format-modules)를 참조하세요.

- **level**은 기록할 최소 엔트리 레벨입니다.

  기본값: `INFO`.

  가능한 값: `DEBUG`, `INFO`, `WARN`, `ERROR` 및 드물게 `PANIC`, `FATAL`.

- **include**는 이 로거에 포함할 로그 이름을 지정합니다.

  기본적으로 이 목록은 비어 있습니다 (즉, 모든 로그가 포함됩니다).

  예를 들어 관리 API에서 내보낸 로그만 포함하려면 `admin.api`를 포함합니다.

- **exclude**는 이 로거에서 제외할 로그 이름을 지정합니다.

  기본적으로 이 목록은 비어 있습니다 (즉, 제외되는 로그가 없습니다).

  예를 들어 HTTP 액세스 로그만 제외하려면 `http.log.access`를 제외합니다.

`include`와 `exclude`가 허용하는 로거 이름은 사용된 모듈에 따라 다르며, 가장 쉬운 확인 방법은 이전 로그를 확인하는 것입니다.

다음은 모든 HTTP 액세스 로그와 관리 로그를 stdout에 json으로 로깅하는 예시입니다:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
HTTP 서버를 종료할 때(즉, 설정 변경 중이나 Caddy가 중지될 때)의 유예 기간을 정의합니다.

유예 기간 동안에는 새로운 연결을 수락하지 않고, 유휴 연결은 닫히며, 활성 연결은 요청을 마칠 때까지 기다립니다. 클라이언트가 유예 기간 내에 요청을 마치지 않으면 서버가 강제로 종료되어 재로드를 완료하고 리소스를 확보합니다. [기간 값](/docs/conventions#durations)을 허용합니다.

기본적으로 유예 기간은 무한하며, 이는 연결이 강제로 닫히지 않음을 의미합니다.

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
중지될 서버가 정상적으로 계속 작동하는 [유예 기간(#grace_period)] *이전*의 [기간](/docs/conventions#durations)을 정의합니다. 단, `{http.shutting_down}` 플레이스홀더는 `true`로 평가되고 `{http.time_until_shutdown}`은 유예 기간이 시작될 때까지의 시간을 제공합니다.

이로 인해 설정 변경의 일부로 서버가 종료되는 경우 지연이 발생하며, 실질적으로 변경을 나중으로 예약합니다. 이는 헬스 체커에 이 서버의 임박한 종료를 알리고 로드 밸런서가 순환에서 이를 제외할 시간을 주는 데 유용합니다. 예시:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


## TLS 옵션 <a id="tls-options"></a>

##### `auto_https`
Caddy가 사이트에 대한 인증서 관리 및 HTTP에서 HTTPS로의 리다이렉트를 자동화할 수 있게 해주는 기능인 [자동 HTTPS](/docs/automatic-https)를 구성합니다.

선택할 수 있는 몇 가지 모드가 있습니다:

- `off`: 인증서 자동화와 HTTP에서 HTTPS로의 리다이렉트를 모두 비활성화합니다.

- `disable_redirects`: HTTP에서 HTTPS로의 리다이렉트만 비활성화합니다.

- `disable_certs`: 인증서 자동화만 비활성화합니다.

- `ignore_loaded_certs`: 수동으로 로드된 인증서에 나타나는 이름에 대해서도 인증서를 자동화합니다. [`tls` 지시어](/docs/caddyfile/directives/tls)를 사용하여 수동으로 지정한 인증서에 포함된 이름(또는 와일드카드)을 자동으로 관리하고 싶은 경우 유용합니다.

<aside class="tip">

이 옵션은 사이트 주소에 유효한 도메인 이름이 있을 때 항상 HTTPS인 Caddy의 기본 프로토콜에는 영향을 미치지 않습니다. 즉, `auto_https off`로 설정해도 사이트가 HTTP로 서비스되지는 않으며, 자동 인증서 관리와 리다이렉트만 비활성화됩니다.

따라서 사이트를 HTTP로 서비스하려면 [사이트 주소](/docs/caddyfile/concepts#addresses) 앞에 `http://`를 붙이거나 뒤에 `:80`(또는 [`http_port` 옵션](#http_port))을 붙여야 합니다.

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
귀하의 이메일 주소입니다. 주로 CA와 ACME 계정을 생성할 때 사용되며, 인증서에 문제가 발생할 경우를 대비하여 설정을 강력히 권장합니다.

<aside class="tip">

Let's Encrypt에서 인증서 만료가 임박했다는 이메일을 보낼 수 있지만, Caddy가 갱신 시 다른 발급자(예: ZeroSSL)를 선택했을 수 있으므로 오해의 소지가 있습니다. 로그 또는 인증서 자체(브라우저 등에서)를 확인하여 어떤 발급자가 사용되었는지, 만료일이 여전히 유효한지 확인하세요. 유효하다면 Let's Encrypt의 이메일은 무시해도 무방합니다.

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
클라이언트가 ClientHello에서 SNI를 사용하지 않을 때 사용할 기본 TLS ServerName을 설정합니다.

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ *실험적 기능*

구성된 경우, 원래의 ServerName이 캐시의 어떤 인증서와도 일치하지 않으면 폴백이 ClientHello의 TLS ServerName이 됩니다.

이 기능은 매우 특수한 경우에 사용됩니다. 일반적으로 클라이언트가 CDN이고 다운스트림 핸드셰이크의 ServerName을 통과시키지만 오리진의 호스트명이 있는 인증서를 수락할 수 있는 경우, 이를 오리진의 호스트명으로 설정합니다. Caddy가 이 이름에 대한 인증서를 관리하고 있어야 함에 유의하세요.

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
Let's Encrypt와 같은 (공개) ACME CA를 통하지 않고 기본적으로 **모든** 인증서를 내부적으로 발급하게 합니다. 이는 개발 환경에서 유용한 퀵 토글입니다.

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
로컬 CA의 루트를 시스템 신뢰 저장소와 Java 및 Mozilla Firefox 신뢰 저장소에 설치하려는 시도를 건너뜁니다.

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
ACME CA의 디렉토리 URL을 지정합니다. 테스트나 개발 목적이라면 Let's Encrypt의 [스테이징 엔드포인트 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)로 설정하는 것이 강력히 권장됩니다. 기본값: ZeroSSL 및 Let's Encrypt 운영 엔드포인트.

전역적으로 구성된 ACME CA가 모든 사이트에 적용되지 않을 수 있음에 유의하세요. 기본 ACME 발급자를 사용하기 위한 [호스트명 요구 사항](/docs/automatic-https#hostname-requirements)을 참조하세요.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
시스템 신뢰 저장소에 없는 경우 ACME CA 엔드포인트에 대한 신뢰할 수 있는 루트 인증서가 포함된 PEM 파일을 지정합니다.

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
모든 ACME 트랜잭션에 사용할 외부 계정 바인딩(External Account Binding)을 지정합니다.

예를 들어, 가짜 ZeroSSL 자격 증명을 사용하는 경우:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
모든 ACME 트랜잭션에 사용할 [ACME DNS 챌린지](/docs/automatic-https#dns-challenge) 제공자를 구성합니다.

DNS 제공자용 플러그인이 포함된 Caddy의 커스텀 빌드가 필요합니다.

제공자 이름 뒤의 토큰은 [`tls` 지시어의 `acme` 발급자](/docs/caddyfile/directives/tls#acme)에서 지정된 것과 동일하게 제공자를 설정합니다.

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
관련 컨텍스트에서 로컬로 지정된 것이 없을 때 사용할 기본 DNS 제공자를 구성합니다. 예를 들어, ACME DNS 챌린지가 활성화되었지만 DNS 제공자가 구성되지 않은 경우 이 전역 기본값이 사용됩니다. 또한 ECH(Encrypted ClientHello) 구성을 게시하는 데에도 적용됩니다.

이 기능이 작동하려면 Caddy 바이너리가 지정된 DNS 제공자 모듈과 함께 컴파일되어야 합니다.

환경 변수의 자격 증명을 사용하는 예시:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Caddy 2.10 beta 1 이상이 필요합니다.)


##### `ech`
지정된 공용 도메인 이름을 TLS 핸드셰이크의 평문 서버 이름(SNI)으로 사용하여 ECH(Encrypted ClientHello)를 활성화합니다. 적절한 조건에서 ECH는 연결 중에 사이트의 도메인 이름이 네트워크상에 노출되지 않도록 보호할 수 있습니다. Caddy는 지정된 각 공용 이름에 대해 하나의 ECH 구성을 생성하고 게시합니다. 게시는 호환되는 클라이언트(적절하게 구성된 최신 브라우저 등)가 사이트에 액세스하기 위해 ECH를 사용해야 함을 알게 되는 방식입니다.

제대로 작동하려면 클라이언트가 기대하는 방식으로 ECH 구성이 게시되어야 합니다. 대부분의 브라우저(DNS-over-HTTPS 또는 DNS-over-TLS 활성화됨)는 ECH 구성이 HTTPS 유형의 DNS 레코드에 게시되기를 기대합니다. Caddy는 이러한 게시를 자동으로 수행하지만, `dns` 서브 옵션이나 [`dns` 전역 옵션](#dns)으로 DNS 제공자를 지정해야 하며, Caddy 바이너리가 지정된 DNS 제공자 모듈과 함께 빌드되어야 합니다. (커스텀 빌드는 [다운로드 페이지](/download)에서 가능합니다.)

**개인정보 보호 공지:**

- 일반적으로 **[*익명성 세트(anonymity set)*](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction)의 크기를 최대화**하는 것이 권장됩니다. 따라서 대부분의 사용자에게 모든 사이트를 보호하기 위해 *단 하나의* 공용 도메인 이름만 구성할 것을 권장합니다.
- **서버는 지정한 공용 도메인 이름에 대해 권한이 있어야 하며**(즉, 해당 도메인이 서버를 가리켜야 함), Caddy가 해당 도메인에 대한 인증서를 획득하기 때문입니다. 이러한 인증서는 사양을 준수하는 클라이언트가 일부 경우에 ECH를 사용하여 안정적이고 안전하게 연결되도록 돕는 데 필수적입니다. 이는 응용 프로그램 데이터(귀하의 사이트 - 공용 도메인 이름과 동일한 사이트를 정의하지 않는 한)가 아니라 적절한 ECH 핸드셰이크를 촉진하는 데만 사용됩니다.
- 상황에 따라 다를 수 있습니다. 위험 부담이 큰 경우 ECH가 모든 상황에 맞는 해결책은 아니므로 전문가와 상담하여 **위협 모델을 검토**할 것을 권장합니다.

Cloudflare에 파킹된 네임서버에 게시하기 위해 환경 변수의 자격 증명을 사용하는 예시:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

이렇게 하면 호환되는 클라이언트가 평문으로 노출된 개별 사이트 이름 대신 `ech.example.net`을 사용하여 모든 사이트를 로드하게 됩니다.

성공적인 게시를 위해서는 사이트 도메인이 구성된 DNS 제공자에 파킹되어 있어야 하며, 제공된 자격 증명/제공자 구성을 통해 레코드를 수정할 수 있어야 합니다.

(Caddy 2.10 beta 1 이상이 필요합니다.)


##### `on_demand_tls`
[주문형(On-Demand) TLS](/docs/automatic-https#on-demand-tls)가 활성화된 경우 이를 구성하지만, 직접 활성화하지는 않습니다 (활성화하려면 [`tls` 지시어의 `on_demand` 서브 지시어](/docs/caddyfile/directives/tls#syntax)를 사용하세요). 오용을 방지하기 위해 운영 환경에서 사용하려면 필수입니다.

- **ask**는 Caddy가 지정된 URL로 HTTP 요청을 보내 도메인에 대한 인증서 발급이 허용되는지 확인하게 합니다.

  요청에는 도메인 이름 값을 포함하는 `?domain=` 쿼리 문자열이 포함됩니다.

  엔드포인트가 `2xx` 상태 코드를 반환하면 Caddy는 해당 이름에 대한 인증서를 얻을 수 있는 권한을 부여받습니다. 그 외의 상태 코드는 인증서 발급을 취소하고 TLS 핸드셰이크 오류를 발생시킵니다.

<aside class="tip">

ask 엔드포인트는 이상적으로는 몇 밀리초 내에 *가능한 한 빨리* 응답해야 합니다. 일반적으로 엔드포인트는 도메인 이름별 인덱스가 있는 데이터베이스에서 상수 시간 조회를 수행해야 하며, 루프는 피하세요. DNS 쿼리나 다른 네트워크 요청을 수행하지 마세요.

</aside>

- **permission**은 특정 이름에 대해 인증서를 발급해야 하는지 결정하기 위해 커스텀 모듈을 사용할 수 있게 합니다. 모듈은 [`caddytls.OnDemandPermission` 인터페이스](https://pkg.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission)를 구현해야 합니다. `http` 권한 모듈이 포함되어 있으며, 이것이 `ask` 옵션이 사용하는 것이고 하위 호환성을 위한 지름길로 남아 있습니다.

- ⚠️ **interval** 및 **burst** 속도 제한 옵션을 사용할 수 있었으나 권장되지 않습니다. 여전히 설정에 있다면 제거하세요.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
TLS 인증서에 대해 생성할 키 유형을 지정합니다. 커스텀해야 할 구체적인 필요가 있는 경우에만 변경하세요.

가능한 값은 `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`입니다.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
TLS 인증서의 발급자(또는 소스)를 정의합니다.

이를 통해 [`tls` 지시어의 `issuer` 서브 지시어](/docs/caddyfile/directives/tls#issuer)를 사용하여 사이트별로 구성하는 대신 전역적으로 발급자를 구성할 수 있습니다.

시도할 발급자를 두 개 이상 구성하려는 경우 반복해서 사용할 수 있습니다. 정의된 순서대로 시도됩니다.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
로드되어 관리 중인 모든 인증서의 만료 여부를 스캔하고 만료된 경우 갱신을 트리거하는 빈도입니다.

기본값: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
CA에 발급을 요청할 인증서의 유효 기간입니다.

이 값은 ACME 주문의 `notAfter` 필드를 계산하는 데 사용되므로 시스템 시계가 합리적으로 동기화되어 있어야 합니다. 참고: 모든 CA가 이를 지원하는 것은 아닙니다. 귀하의 CA가 이를 허용하는지, 어떤 값을 사용할 수 있는지 확인하려면 CA의 ACME 문서를 확인하세요.

기본값: `0` (CA가 수명을 선택하며, 보통 90일)

⚠️ 실험적 기능입니다. 변경되거나 제거될 수 있습니다.

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
[OCSP 스테이플 <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling)의 업데이트가 필요한지 확인하는 빈도입니다.

기본값: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
OCSP 스테이플링을 비활성화하기 위해 `off`로 설정할 수 있습니다. 방화벽으로 인해 응답자에 도달할 수 없는 환경에서 유용합니다.

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
Caddy가 인증서 갱신을 시도하기 전에 남아 있어야 하는 인증서 수명의 비율(0에서 1 사이)입니다. 예를 들어 인증서 수명이 90일이고 이 비율이 `0.3333`(기본값)인 경우 Caddy는 만료까지 30일 이하로 남았을 때 지속적으로 인증서 갱신을 시도합니다. [`tls` 지시어의 `renewal_window_ratio` 서브 지시어](/docs/caddyfile/directives/tls#renewal_window_ratio)를 사용하여 사이트별로 설정할 수도 있습니다.

이 값을 변경해야 하는 경우는 거의 없지만, CA의 발급 시간이 매우 긴 경우 인증서 수명 후반부에 갱신하는 데 유용할 수 있습니다.

ACME 발급자가 ACME 클라이언트(이 경우 Caddy)가 갱신을 시도해야 하는 기간을 지시하는 [ARI 확장](https://datatracker.ietf.org/doc/rfc9773/)을 구현할 수 있으며, 해당 기간이 이 비율과 일치하지 않을 수 있으므로 이는 제안 사항임에 유의하세요.

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
CA가 여러 인증서 체인을 제공하는 경우 이 옵션을 사용하여 Caddy가 선호할 체인을 지정할 수 있습니다. 다음 옵션 중 하나를 설정하세요:

- **smallest**는 바이트 수가 가장 적은 체인을 선호하도록 Caddy에 지시합니다.

- **root_common_name**은 하나 이상의 일반 이름(common names) 목록입니다. Caddy는 지정된 일반 이름 중 적어도 하나와 일치하는 루트가 있는 첫 번째 체인을 선택합니다.

- **any_common_name**은 하나 이상의 일반 이름 목록입니다. Caddy는 지정된 일반 이름 중 적어도 하나와 일치하는 발급자가 있는 첫 번째 체인을 선택합니다.

`preferred_chains`를 전역 옵션으로 지정하면 [재정의하는 발급자 수준 구성](/docs/caddyfile/directives/tls#acme)이 없는 한 모든 발급자에 영향을 미칩니다.

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


## 서버 옵션 <a id="server-options"></a>

잠재적으로 여러 사이트에 걸쳐 있는 설정으로 [HTTP 서버](/docs/json/apps/http/servers/)를 커스텀하므로 사이트 블록에서 올바르게 구성할 수 없습니다. 이 옵션들은 HTTP 계층 아래의 리스너/소켓 또는 기타 기능에 영향을 미칩니다.

서버당 서로 다른 옵션을 구성하기 위해 서로 다른 `listener_address` 값으로 두 번 이상 지정할 수 있습니다. 예를 들어 `servers :443`은 리스너 주소 `:443`에 바인딩된 서버에만 적용됩니다. 리스너 주소를 생략하면 나머지 서버에 옵션이 적용됩니다.

<aside class="tip">

Caddyfile에 있는 서버의 수신 주소를 찾으려면 [`caddy adapt`](/docs/command-line#caddy-adapt) 명령을 사용하세요.

</aside>


예를 들어 `:80` 및 `:443` 포트의 서버에 대해 서로 다른 옵션을 구성하려면 두 개의 `servers` 블록을 지정합니다:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

`servers`를 사용할 때는 Caddyfile에 **실제로 나타나는**(즉, 사이트 블록에 의해 생성된) 서버에만 적용됩니다. [자동 HTTPS](/docs/automatic-https)는 HTTP->HTTPS 리다이렉트를 제공하고 ACME HTTP 챌린지를 해결하기 위해 `80` 포트(또는 [`http_port` 옵션](#http_port))에서 수신 대기하는 서버를 생성한다는 점을 기억하세요. 이는 런타임, 즉 Caddyfile 어댑터가 `servers`를 적용한 *후에* 발생합니다. 즉, `http://` 또는 `:80`과 같은 사이트 블록을 명시적으로 선언하지 않는 한 `servers`는 `:80`에 적용되지 **않습니다.**


<aside class="tip">

[`bind` 지시어](/docs/caddyfile/directives/bind) 또는 [`default_bind` 전역 옵션](#default_bind)을 사용하는 경우, `listener_address`는 사이트 블록의 포트와 결합된 바인딩 주소와 *반드시* 일치해야 하며, 그렇지 않으면 설정이 적용되지 않습니다. 예시:

```caddy
{
	# 바인딩 주소가 누락되어 서버와 일치하지 않음
	servers :8080 {
		name private
	}

	# 정확히 일치하므로 작동함
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

이 서버에 할당할 커스텀 이름입니다. 일반적으로 로그 및 메트릭에서 이름으로 서버를 식별하는 데 도움이 됩니다. 설정하지 않으면 Caddy는 `srvX` 패턴을 사용하여 동적으로 정의합니다. 여기서 `X`는 `0`부터 시작하여 구성의 서버 수에 따라 증가합니다.

구성의 사이트 블록에서 생성된 서버에만 설정이 적용된다는 점에 유의하세요. [자동 HTTPS](/docs/automatic-https)는 런타임에 `:80`(또는 [`http_port`](#http_port)) 서버를 생성하므로 이름을 변경하려면 적어도 빈 `http://` 사이트 블록이 필요합니다.

예시:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

소켓 리스너의 동작을 수정할 수 있는 [리스너 래퍼(listener wrappers)](/docs/json/apps/http/servers/listener_wrappers/)를 구성할 수 있습니다. 지정된 순서대로 적용됩니다.

###### `tls`

`tls` 리스너 래퍼는 리스너 래퍼 체인에서 TLS 리스너가 있어야 할 위치를 표시하는 no-op 리스너 래퍼입니다. 다른 리스너 래퍼를 TLS 핸드셰이크 앞에 배치해야 하는 경우에만 사용해야 합니다.

###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/)는 처음 몇 바이트를 사용하여 TLS 핸드셰이크가 아니라 HTTP 요청임을 감지함으로써, TLS 포트로 들어오는 HTTP 요청 연결에 대해 HTTP->HTTPS 리다이렉트를 제공합니다. 스키마가 지정되지 않은 경우 브라우저가 HTTP를 시도하므로 표준 포트(`443`)가 아닌 포트에서 HTTPS를 서비스할 때 가장 유용합니다. `tls` 리스너 래퍼 *앞에* 배치해야 합니다. 예시:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

[`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) 리스너 래퍼(v2.7.0 이전에는 플러그인을 통해서만 사용 가능)는 [PROXY 프로토콜](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) 파싱을 활성화합니다(HAProxy에 의해 대중화됨). 연결 시작 시 평문 데이터를 파싱하므로 `tls` 리스너 래퍼 *앞에* 사용해야 합니다:

PROXY 프로토콜의 메타데이터는 매처 평가 또는 [`trusted_proxies`](#trusted_proxies) 전에 연결에 적용될 수 있음을 주의하세요. 직전 피어의 IP 주소는 추가 평가를 위해 손실됩니다.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout**은 PROXY 헤더를 기다리는 최대 기간을 지정합니다. 기본값은 `5s`입니다.

- **allow**는 PROXY 헤더를 받을 신뢰할 수 있는 소스의 CIDR 범위 목록입니다. 유닉스 소켓은 기본적으로 신뢰되며 이 옵션의 일부가 아닙니다.

- **deny**는 PROXY 헤더를 거부할 신뢰할 수 있는 소스의 CIDR 범위 목록입니다.

- **fallback_policy**는 PROXY 헤더가 허용/거부 목록에 없는 주소에서 올 경우 취할 조치입니다. 기본 폴백 정책은 `ignore`입니다. `fallback_policy`에 허용되는 값은 다음과 같습니다:
	- `ignore`: PROXY 헤더의 주소를 무시하지만 연결 수락
	- `use`: PROXY 헤더의 주소 사용
	- `reject`: PROXY 헤더가 전송될 때 연결 거부
	- `require`: PROXY 헤더 전송 요구, 없으면 거부
	- `skip`: PROXY 헤더 없이 연결 수락


예를 들어, 특정 범위의 IP 주소에서 PROXY 헤더를 수락하고 다른 범위에서는 거부하며 타임아웃이 2초인 HTTPS 서버(`tls` 리스너 래퍼 필요)의 경우:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body**는 클라이언트의 업로드 읽기를 허용하는 기간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 이를 짧은 0이 아닌 값으로 설정하면 slowloris 공격을 완화할 수 있지만 합법적으로 느린 클라이언트에도 영향을 줄 수 있습니다. 기본값은 타임아웃 없음입니다.

- **read_header**는 클라이언트의 요청 헤더 읽기를 허용하는 기간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값은 타임아웃 없음입니다.

- **write**는 클라이언트에 쓰기를 허용하는 기간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 큰 파일을 서비스할 때 이를 작은 값으로 설정하면 합법적으로 느린 클라이언트에 부정적인 영향을 줄 수 있음에 유의하세요. 기본값은 타임아웃 없음입니다.

- **idle**은 킵얼라이브(keep-alives)가 활성화되었을 때 다음 요청을 기다리는 최대 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 리소스 고갈을 방지하기 위해 기본값은 5분입니다.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

다른 데이터가 전송되지 않을 때 TCP 계층에서 연결을 유지하기 위해 TCP 킵얼라이브 패킷을 보내는 간격입니다. 기본값은 `15s`입니다.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

다른 데이터가 전송되지 않을 때 TCP 킵얼라이브 패킷을 보내기 전에 연결이 유휴 상태여야 하는 기간입니다. 기본값은 `15s`입니다.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

연결이 끊긴 것으로 간주하기 전에 보낼 최대 TCP 킵얼라이브 패킷 수입니다. 기본값은 `9`입니다.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

기본적으로 0-RTT(초기 데이터)는 QUIC 리스너(즉, HTTP/3)에 대해 활성화되어 클라이언트가 TLS 핸드셰이크의 첫 번째 왕복에서 데이터를 보낼 수 있게 하며, 이는 반복 연결의 성능을 향상시킬 수 있습니다.

QUIC 리스너에 대해 0-RTT를 비활성화하려면 이를 `off`로 설정할 수 있습니다. 0-RTT를 비활성화하는 한 가지 이유는 [`remote_ip` 매처](/docs/caddyfile/matchers#remote-ip)를 사용하는 경우인데, 이는 TLS 핸드셰이크가 완료되기 전에 라우팅이 발생하는 경우 원격 주소가 확인되어야 하는 의존성을 도입합니다. 그 경우 HTTP 425 응답이 작성되지만 일부 클라이언트(브라우저)가 오작동하여 재시도를 수행하지 않을 수 있으므로, 0-RTT를 비활성화하면 0-RTT의 성능 이점을 잃는 대신 사용자가 425 응답을 보지 않도록 보장할 수 있습니다.

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

요청을 신뢰해야 하는 프록시 서버의 IP 범위(CIDR) 구성을 허용합니다. 기본적으로 어떤 프록시도 신뢰하지 않습니다.

이를 활성화하면 신뢰할 수 있는 요청의 HTTP 헤더에서 *실제* 클라이언트 IP를 파싱하게 됩니다 (기본값은 `X-Forwarded-For`이며, 다른 헤더를 구성하려면 [`client_ip_headers`](#client-ip-headers)를 참조하세요). 신뢰할 수 있는 경우 클라이언트 IP는 [액세스 로그](/docs/caddyfile/directives/log)에 추가되고, `{client_ip}` [플레이스홀더](/docs/caddyfile/concepts#placeholders)로 사용 가능하며, [`client_ip` 매처](/docs/caddyfile/matchers#client-ip)를 사용할 수 있게 합니다. 요청이 신뢰할 수 있는 프록시에서 온 것이 아니면 클라이언트 IP는 직접 들어오는 연결의 원격 IP 주소 또는 사용된 경우 [PROXY 프로토콜](#proxy-protocol)에 의해 설정된 주소로 설정됩니다. 기본적으로 헤더의 IP는 왼쪽에서 오른쪽으로 파싱됩니다. 이 동작을 변경하려면 [`trusted_proxies_strict`](#trusted-proxies-strict)를 참조하세요.

일부 매처나 핸들러는 결정을 내리기 위해 요청의 신뢰 상태를 사용할 수 있습니다. 예를 들어 신뢰할 수 있는 경우 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) 핸들러는 민감한 `X-Forwarded-*` 요청 헤더를 프록시하고 보강합니다.

현재 Caddy의 표준 배포판에는 `static` [IP 소스 모듈](/docs/json/apps/http/servers/trusted_proxies/)만 포함되어 있지만, 플러그인을 통해 IP 범위의 동적 목록을 유지하도록 [확장](/docs/extending-caddy)할 수 있습니다.


###### `static`

신뢰할 정적(변경되지 않는) IP 범위(CIDR) 목록을 받습니다.

지름길로 `private_ranges`를 사용하여 모든 사설 IPv4 및 IPv6 범위를 일치시킬 수 있습니다. 이는 다음 모든 범위를 지정하는 것과 동일합니다: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

구문은 다음과 같습니다:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

다음은 예시 IPv4 범위와 IPv6 범위를 신뢰하는 전체 예시입니다:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

[`trusted_proxies`](#trusted-proxies)가 활성화된 경우, 헤더([`client_ip_headers`](#client-ip-headers)로 구성됨)의 IP는 기본적으로 왼쪽에서 오른쪽으로 파싱됩니다. 처음 발견되는 신뢰할 수 없는 IP 주소가 실제 클라이언트 주소가 됩니다. v2.8부터는 `trusted_proxies_strict`를 사용하여 이러한 헤더의 오른쪽에서 왼쪽 파싱을 옵트인할 수 있습니다. 하위 호환성을 위해 이 옵션은 기본적으로 비활성화되어 있습니다.

HAProxy, CloudFlare, AWS ALB, CloudFront 등과 같은 업스트림 프록시는 새로운 연결 원격 주소를 `X-Forwarded-For`의 오른쪽에 추가합니다. 가장 왼쪽의 IP 주소는 클라이언트에 의해 스포핑될 수 있으므로, 이들을 사용할 때는 `trusted_proxies_strict`를 활성화하는 것이 권장됩니다.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

특히 AWS ALB의 경우, 이 옵션을 반드시 활성화하고 싶을 것입니다. [그들의 문서에 따르면](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15) XFF 모드를 `append`로 설정해야만 실제 클라이언트 IP를 식별할 수 있습니다. 이 IP는 `X-Forwarded-For`의 오른쪽에 추가되며 `trusted_proxies_strict`를 통해서만 안전하게 추출할 수 있습니다.

</aside>

##### `trusted_proxies_unix`

`trusted_proxies_unix` 옵션은 유닉스 소켓에서 오는 모든 연결을 신뢰할 수 있게 합니다. 이는 Caddy가 유닉스 소켓을 통해 연결하는 리버스 프록시(다른 Caddy 인스턴스일 수 있음) 뒤에 있을 때 유용합니다 (즉, [`bind` 지시어](/docs/caddyfile/directives/bind)가 유닉스 소켓으로 설정된 경우). 이는 기본적으로 비활성화되어 있습니다.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

[`trusted_proxies`](#trusted-proxies)와 연동하여 클라이언트의 IP 주소를 결정하는 데 사용할 헤더 구성을 허용합니다. 기본적으로 `X-Forwarded-For`만 고려됩니다. 여러 헤더 필드를 지정할 수 있으며, 이 경우 비어 있지 않은 첫 번째 헤더 값이 사용됩니다.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

메트릭 수집을 활성화합니다. 메트릭을 스크래핑하거나 OTLP로 푸시하기 전에 필요합니다. 메트릭은 매우 바쁜 서버에서 성능을 저하시킬 수 있음에 유의하세요. (우리 커뮤니티는 이를 개선하기 위해 노력하고 있습니다. 참여해 주세요!)

```caddy
{
	metrics
}
```

`per_host` 옵션을 추가하여 메트릭에 호스트 이름을 레이블로 지정할 수 있습니다.

```caddy
{
	metrics {
		per_host
	}
}
```

클라이언트가 보낼 수 있는 모든 가능한 호스트를 관찰하는 데 따른 무한한 카디널리티(cardinality) 잠재력 때문에, Caddy는 구성된 호스트에 대해서만 메트릭을 기록하고 다른 모든 호스트(예: attacker.com)는 "_other" 레이블 아래에 집계합니다. 모든 호스트를 강제로 관찰하고 잠재적인 무한 카디널리티가 허용 가능한 위험인 경우 `observe_catchall_hosts`를 추가할 수 있습니다. `observe_catchall_hosts`를 추가해도 `per_host`가 활성화되지는 않음에 유의하세요. 그러나 HTTPS 서버의 경우 인증서가 무제한 카디널리티에 대한 보호를 제공하므로 자동으로 활성화되지만, HTTP 서버의 경우 임의의 Host 헤더로 인한 카디널리티 공격을 방지하기 위해 기본적으로 비활성화됩니다.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

`otlp` 옵션을 추가하여 동일한 메트릭을 OpenTelemetry 프로토콜(OTLP) 엔드포인트로 푸시할 수 있습니다. 내보내기 도구는 `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` 및 `OTEL_METRICS_EXPORTER`와 같은 표준 OpenTelemetry `OTEL_*` 환경 변수에 의해 구성됩니다.

```caddy
{
	metrics {
		otlp
	}
}
```

예시:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

자세한 내용은 [메트릭으로 Caddy 모니터링하기](/docs/metrics)를 참조하세요.

##### `trace`

호출되는 각 개별 핸들러를 로깅합니다. 로그가 `DEBUG` 레벨로 출력되어야 합니다 ([`debug` 전역 옵션](#debug)으로 설정 가능).

참고: 이는 HTTP 핸들러 모듈의 구성을 로깅할 수 있습니다. 구성에 민감한 데이터가 있는 안전하지 않은 컨텍스트에서는 이 기능을 활성화하지 마세요.

⚠️ 실험적 기능입니다. 변경되거나 제거될 수 있습니다.

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

클라이언트의 HTTP 요청 헤더에서 파싱할 최대 크기입니다. 제한을 초과하면 서버는 HTTP 상태 `431 Request Header Fields Too Large`로 응답합니다. [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go)에서 지원하는 모든 형식을 허용합니다. 기본적으로 제한은 `1MB`입니다.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

HTTP/1 요청에 대해 전이중(full-duplex) 통신을 활성화합니다.

HTTP/1 요청의 경우, Go HTTP 서버는 기본적으로 응답 작성을 시작하기 전에 요청 본문의 읽지 않은 부분을 소비하여 핸들러가 요청 읽기와 응답 작성을 동시에 수행하는 것을 방지합니다. 이 옵션을 활성화하면 이 동작이 비활성화되고 핸들러가 응답을 동시에 작성하면서 요청을 계속 읽을 수 있게 됩니다.

HTTP/2+ 요청의 경우 Go HTTP 서버는 항상 동시 읽기 및 응답을 허용하므로 이 옵션은 효과가 없습니다.

일부 오래된 클라이언트는 교착 상태(deadlock)를 유발할 수 있는 전이중 HTTP/1을 지원하지 않을 수 있으므로 HTTP 클라이언트로 충분히 테스트하세요. 자세한 내용은 [golang/go#57786](https://github.com/golang/go/issues/57786)을 참조하세요.

⚠️ 실험적 기능입니다. 변경되거나 제거될 수 있습니다.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

기본적으로 잠재적으로 민감한 정보(`Cookie`, `Set-Cookie`, `Authorization` 및 `Proxy-Authorization`)가 포함된 헤더가 있는 액세스 로그([`log` 지시어](/docs/caddyfile/directives/log)로 활성화됨)는 `REDACTED`로 기록됩니다.

이러한 헤더를 수정하지 않고 로깅하려면 `log_credentials` 옵션을 활성화할 수 있습니다.

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

지원할 HTTP 프로토콜의 공백으로 구분된 목록입니다.

기본값: `h1 h2 h3`

허용되는 값은 다음과 같습니다:
- HTTP/1.1용 `h1`
- HTTP/2용 `h2`
- 일반 텍스트 기반 HTTP/2용 `h2c`
- HTTP/3용 `h3`

현재 HTTP/2(H2C 포함)를 활성화하면 Go 표준 라이브러리가 HTTP 서버 사용 시 HTTP/1.1을 비활성화하지 못하게 하므로 반드시 HTTP/1.1 활성화를 의미합니다. 하지만 HTTP/1.1 또는 HTTP/3은 독립적으로 활성화할 수 있습니다.

H2C("Cleartext HTTP/2" 또는 "H2 over TCP") 및 HTTP/3은 Go 표준 라이브러리에 의해 구현되지 않으므로 일부 기능이 제한될 수 있습니다. 응용 프로그램에 절대적으로 필요한 경우가 아니면 H2C를 활성화하지 않는 것이 좋습니다.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

이를 활성화하면 요청의 `Host` 헤더가 클라이언트의 TLS ClientHello에 의해 전송된 `ServerName` 값과 일치해야 하며, 이는 TLS 클라이언트 인증 사용 시 필수적인 보호 조치입니다. 불일치가 있는 경우 클라이언트에 HTTP 상태 `421 Misdirected Request` 응답이 기록됩니다.

[클라이언트 인증](/docs/caddyfile/directives/tls#client_auth)이 구성된 경우 이 옵션은 자동으로 켜집니다. 이는 TLS 핸드셰이크 중에 보호되지 않은 SNI 값을 보낸 다음 연결 수립 후 Host 헤더에 보호된 도메인을 넣어서 악용될 수 있는 TLS 클라이언트 인증 우회(domain fronting)를 허용하지 않습니다. 이 동작은 안전한 기본값이지만, 도메인 프론팅을 원하고 호스트명에 따라 액세스가 제한되지 않는 프록시를 실행하는 경우 등에는 `insecure_off`를 사용하여 명시적으로 끌 수 있습니다.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



## 파일 시스템 <a id="file-systems"></a>

`filesystem` 전역 옵션을 사용하면 파일 I/O에 사용할 수 있는 하나 이상의 파일 시스템을 선언할 수 있습니다.

이를 통해 클라우드에서 실행 중인 원격 파일 시스템, 파일과 같은 인터페이스를 가진 데이터베이스 또는 Caddy 바이너리 내에 포함된 파일에서 읽을 수 있도록 연결할 수 있습니다.

파일 시스템은 이를 식별하기 위한 이름과 함께 선언됩니다. 즉, 필요한 경우 동일한 유형의 파일 시스템을 두 개 이상 연결할 수 있습니다.

기본적으로 Caddy에는 파일 시스템 모듈이 없으므로 사용하려는 파일 시스템용 플러그인을 사용하여 Caddy를 빌드해야 합니다.

#### 예시

가상의 `custom` 파일 시스템 모듈을 사용하여 두 개의 파일 시스템을 선언할 수 있습니다:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



## PKI 옵션 <a id="pki-options"></a>

PKI(공개 키 기반 구조) 앱은 Caddy의 [로컬 HTTPS](/docs/automatic-https#local-https) 및 [ACME 서버](/docs/caddyfile/directives/acme_server) 기능의 기초입니다. 이 앱은 인증서 서명이 가능한 인증 기관(CA)을 정의합니다.

기본 CA ID는 `local`입니다. `ca`를 구성할 때 ID를 생략하면 `local`로 간주됩니다.

##### `name`
인증 기관의 사용자용 이름입니다.

기본값: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
루트 인증서의 CommonName 필드에 넣을 이름입니다.

기본값: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
중간 인증서의 CommonName 필드에 넣을 이름입니다.

기본값: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
중간 인증서가 유효한 [기간](/docs/conventions#durations)입니다. 이 값은 반드시 루트 인증서의 수명(`3600d` 또는 10년)보다 작아야 합니다.

기본값: `7d`. 절대적으로 필요한 경우가 아니면 이 값을 변경하는 것을 *권장하지 않습니다.*

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
중간 인증서(및 해당되는 경우 루트 인증서)의 갱신이 필요한지 확인하는 빈도 [기간](/docs/conventions#durations)입니다.

기본값: `10m`. 절대적으로 필요한 경우가 아니면 이 값을 변경하는 것을 *권장하지 않습니다.*

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
Caddy가 인증서 갱신을 시도하기 전에 남아 있어야 하는 인증서 수명의 비율(0에서 1 사이)입니다. 예를 들어 인증서 수명이 1년이고 이 비율이 `0.2`(기본값)인 경우 Caddy는 만료까지 73일 이하로 남았을 때 지속적으로 인증서 갱신을 시도합니다.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
CA의 루트로 사용할 키 쌍(인증서 및 개인 키)입니다. 지정하지 않으면 자동으로 생성되고 관리됩니다.

- **format**은 인증서와 개인 키가 제공되는 형식입니다. 현재는 `pem_file`만 지원되며 이것이 기본값이므로 이 필드는 선택 사항입니다.
- **cert**는 인증서입니다. `pem_file` 형식을 사용할 때 PEM 파일의 경로여야 합니다.
- **key**는 개인 키입니다. `pem_file` 형식을 사용할 때 PEM 파일의 경로여야 합니다.

##### `intermediate`
CA의 중간 인증서로 사용할 키 쌍(인증서 및 개인 키)입니다. 지정하지 않으면 자동으로 생성되고 관리됩니다.

- **format**은 인증서와 개인 키가 제공되는 형식입니다. 현재는 `pem_file`만 지원되며 이것이 기본값이므로 이 필드는 선택 사항입니다.
- **cert**는 인증서입니다. `pem_file` 형식을 사용할 때 PEM 파일의 경로여야 합니다.
- **key**는 개인 키입니다. `pem_file` 형식을 사용할 때 PEM 파일의 경로여야 합니다.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


## 이벤트 옵션 <a id="event-options"></a>

Caddy 모듈은 흥미로운 일이 발생할 때(또는 발생하려고 할 때) 이벤트를 내보냅니다.

이벤트에는 일반적으로 메타데이터 페이로드가 포함됩니다. 이벤트와 페이로드에 대해 배우는 가장 좋은 방법은 각 모듈의 문서를 참조하는 것이지만, [`debug` 전역 옵션](#debug)을 활성화하고 로그를 읽어서 이벤트와 데이터 페이로드를 확인할 수도 있습니다.

##### `on`

이벤트 핸들러를 명명된 이벤트에 바인딩합니다. 이벤트 핸들러 모듈의 이름을 지정하고 그 뒤에 구성을 지정합니다.

예를 들어 인증서를 획득한 후 명령을 실행하려면([서드파티 플러그인 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec) 필요), 플레이스홀더를 사용하여 이벤트 페이로드의 일부를 스크립트에 전달합니다:

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

### 이벤트

Caddy에서 다음과 같은 표준 이벤트를 내보냅니다:

- [`tls` 이벤트 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [`reverse_proxy` 이벤트](/docs/caddyfile/directives/reverse_proxy#events)

플러그인도 이벤트를 내보낼 수 있으므로 자세한 내용은 해당 문서를 확인하세요.
