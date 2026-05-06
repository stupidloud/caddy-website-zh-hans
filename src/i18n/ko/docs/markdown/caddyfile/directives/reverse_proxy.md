---
title: reverse_proxy (Caddyfile 지시어)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

구성 가능한 전송(transport), 부하 분산(load balancing), 상태 확인(health checking), 요청 조작 및 버퍼링 옵션을 사용하여 하나 이상의 백엔드로 요청을 프록시합니다.

- [Syntax](#syntax)
- [Upstreams](#upstreams)
  - [Upstream addresses](#upstream-addresses)
  - [Dynamic upstreams](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Load balancing](#load-balancing)
  - [Active health checks](#active-health-checks)
  - [Passive health checks](#passive-health-checks)
  - [Events](#events)
- [Streaming](#streaming)
- [Headers](#headers)
- [Rewrites](#rewrites)
- [Transports](#transports)
  - [The `http` transport](#the-http-transport)
  - [The `fastcgi` transport](#the-fastcgi-transport)
- [Intercepting responses](#intercepting-responses)
- [Examples](#examples)



## 구문 <a id="syntax"></a>

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# load balancing
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# active health checking
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive health checking
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# request/header manipulation
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# optionally intercept responses from upstream
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# special directives only available in handle_response
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



## 업스트림 <a id="upstreams"></a>

- **&lt;upstreams...&gt;** 는 프록시할 업스트림(백엔드) 목록입니다.
- **to** <span id="to"/> 는 업스트림 목록을 지정하는 또 다른 방법으로, 한 줄에 하나(또는 그 이상)씩 작성합니다.
- **dynamic** <span id="dynamic"/> 은 *동적 업스트림* 모듈을 구성합니다. 이를 통해 모든 요청에 대해 동적으로 업스트림 목록을 가져올 수 있습니다. 표준 동적 업스트림 모듈에 대한 설명은 아래의 [동적 업스트림](#dynamic-upstreams) 섹션을 참조하세요. 동적 업스트림은 모든 프록시 루프 반복 시(즉, 부하 분산 재시도가 활성화된 경우 요청당 여러 번) 검색되며 정적 업스트림보다 우선시됩니다. 오류가 발생하면 프록시는 정적으로 구성된 업스트림을 대신 사용합니다.


### 업스트림 주소 <a id="upstream-addresses"></a>

정적 업스트림 주소는 스키마와 호스트/포트만 포함하는 URL 형태이거나 전통적인 [Caddy 네트워크 주소](/docs/conventions#network-addresses) 형태일 수 있습니다. 유효한 예시는 다음과 같습니다:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

기본적으로 연결은 일반 텍스트 HTTP를 통해 업스트림으로 이루어집니다. URL 형태를 사용할 때, 스키마를 일부 [`transport`](#transports) 기본값 설정을 위한 약어로 사용할 수 있습니다.
- `https://` 를 스키마로 사용하면 [`tls`](#tls)가 활성화된 [`http` 전송](#the-http-transport)을 사용합니다.

  또한 서버가 라우팅 및 인증서 선택에 사용하는 TLS SNI 값과 일치하도록 `Host` 헤더를 재정의해야 할 수도 있습니다. 자세한 내용은 아래의 [HTTPS](#https) 섹션을 참조하세요.

- `h2c://` 를 스키마로 사용하면 [HTTP 버전](#versions)이 일반 텍스트 HTTP/2 연결을 허용하도록 설정된 [`http` 전송](#the-http-transport)을 사용합니다.

- `http://` 를 스키마로 사용하는 것은 스키마를 생략한 것과 동일합니다. HTTP가 이미 기본값이기 때문입니다. 이 구문은 다른 스키마 약어와의 대칭성을 위해 포함되었습니다.

스키마를 혼합하여 사용할 수 없습니다. 스키마가 공통 전송 구성을 수정하기 때문입니다(TLS가 활성화된 전송은 HTTPS와 일반 텍스트 HTTP를 모두 전송할 수 없습니다). 명시적인 전송 구성은 덮어쓰이지 않으며, 스키마를 생략하거나 다른 포트를 사용한다고 해서 특정 전송을 가정하지는 않습니다.

영역(zone)이 포함된 IPv6(예: 특정 네트워크 인터페이스가 있는 링크 로컬 주소)를 사용할 때는 `%` 문자가 URL 파싱 오류를 발생시키므로 스키마를 약어로 사용할 수 **없습니다**. 대신 전송을 명시적으로 구성하세요.

[네트워크 주소](/docs/conventions#network-addresses) 형태를 사용할 때, 네트워크 유형은 업스트림 주소의 접두사로 지정됩니다. 이는 URL 스키마와 결합할 수 없습니다. 특수한 경우로, `unix+h2c/` 는 `unix/` 네트워크와 `h2c://` 스키마의 효과를 동시에 적용하는 약어로 지원됩니다. 포트 범위는 동일한 호스트를 가진 여러 업스트림으로 확장되는 약어로 지원됩니다.

업스트림 주소에는 경로(path)나 쿼리 문자열이 포함될 수 **없습니다**. 이는 프록싱과 동시에 요청을 재작성하는 것을 의미하며, 이러한 동작은 정의되지 않았거나 지원되지 않습니다. 이 기능이 필요한 경우 [`rewrite`](/docs/caddyfile/directives/rewrite) 지시어를 사용할 수 있습니다.

주소가 URL이 아닌 경우(즉, 스키마가 없는 경우) [플레이스홀더](/docs/caddyfile/concepts#placeholders)를 사용할 수 있지만, 이 경우 해당 업스트림은 *동적 정적(dynamically static)* 상태가 됩니다. 즉, 상태 확인 및 부하 분산 측면에서 잠재적으로 많은 서로 다른 백엔드가 하나의 정적 업스트림처럼 작동함을 의미합니다. 가능하면 [동적 업스트림](#dynamic-upstreams) 모듈을 대신 사용하는 것을 권장합니다. 플레이스홀더를 사용할 때는 포트가 **반드시** 포함되어야 합니다(플레이스홀더 대체 값에 포함되거나 주소의 정적 접미사로 포함되어야 함).


### 동적 업스트림 <a id="dynamic-upstreams"></a>

Caddy's reverse proxy comes standard with some dynamic upstream modules. Note that using dynamic upstreams has implications for load balancing and health checks, depending on specific policy configuration: active health checks do not run for dynamic upstreams; and load balancing and passive health checks are best served if the list of upstreams is relatively stable and consistent (especially with round-robin). Ideally, dynamic upstream modules only return healthy, usable backends.


#### SRV <a id="srv"></a>

SRV DNS 레코드에서 업스트림을 검색합니다.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** 은 조회할 레코드의 전체 도메인 이름입니다(예: `_service._proto.name`).
- **service** 는 전체 이름의 서비스 구성 요소입니다.
- **proto** 는 전체 이름의 프로토콜 구성 요소입니다. `tcp` 또는 `udp` 중 하나입니다.
- **name** 은 이름 구성 요소입니다. 또는 `service`와 `proto`가 비어 있는 경우 쿼리할 전체 도메인 이름입니다.
- **refresh** 는 캐시된 결과를 얼마나 자주 새로 고칠지 지정합니다. 기본값: `1m`
- **resolvers** 는 시스템 리졸버를 재정의할 DNS 리졸버 목록입니다.
- **dial_timeout** 은 쿼리 연결 시도의 타임아웃입니다.
- **dial_fallback_delay** 는 RFC 6555 Fast Fallback 연결을 시작하기 전 대기 시간입니다. 기본값: `300ms`



#### A/AAAA <a id="aaaaa"></a>

A/AAAA DNS 레코드에서 업스트림을 검색합니다.

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** 은 쿼리할 도메인 이름입니다.
- **port** 는 백엔드에 사용할 포트입니다.
- **refresh** 는 캐시된 결과를 얼마나 자주 새로 고칠지 지정합니다. 기본값: `1m`
- **resolvers** 는 시스템 리졸버를 재정의할 DNS 리졸버 목록입니다.
- **dial_timeout** 은 쿼리 연결 시도의 타임아웃입니다.
- **dial_fallback_delay** 는 RFC 6555 Fast Fallback 연결을 시작하기 전 대기 시간입니다. 기본값: `300ms`
- **versions** 는 분석할 IP 버전 목록입니다. 기본값: `ipv4 ipv6`이며 각각 A 및 AAAA 레코드에 해당합니다.


#### Multi <a id="multi"></a>

여러 동적 업스트림 모듈의 결과를 추가합니다. 예를 들어 보조 SRV 클러스터가 백업하는 기본 SRV 클러스터와 같이 중복된 업스트림 소스가 필요한 경우 유용합니다.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** 는 동적 업스트림용 모듈의 이름과 그 뒤에 오는 구성입니다. 하나 이상 지정할 수 있습니다.




## 부하 분산 <a id="load-balancing"></a>

부하 분산은 일반적으로 여러 업스트림 간에 트래픽을 분산하는 데 사용됩니다. 재시도를 활성화하면 하나 이상의 업스트림과 함께 사용하여 정상적인 업스트림이 선택될 때까지 요청을 보류할 수도 있습니다(예: 업스트림을 재부팅하거나 다시 배포하는 동안 대기하고 오류를 완화하기 위해).

이 기능은 기본적으로 활성화되어 있으며 `random` 정책을 사용합니다. 재시도는 기본적으로 비활성화되어 있습니다.

- **lb_policy** <span id="lb_policy"/> 는 부하 분산 정책의 이름과 옵션입니다. 기본값: `random`.

  해싱이 포함된 정책의 경우, [최고 무작위 가중치(HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) 알고리즘을 사용하여 업스트림 목록이 변경되더라도 동일한 해시 키를 가진 클라이언트나 요청이 동일한 업스트림에 매핑되도록 합니다.

  일부 정책은 폴백(fallback) 옵션을 지원하며, 이 경우 `fallback <policy>`를 포함하는 [블록](/docs/caddyfile/concepts#blocks)을 사용하고 다른 부하 분산 정책을 인자로 받습니다. 이러한 정책의 경우 기본 폴백은 `random`입니다. 폴백을 구성하면 기본 정책이 업스트림을 선택하지 못할 경우 보조 정책을 사용할 수 있어 강력한 조합이 가능합니다. 폴백은 필요에 따라 여러 번 중첩될 수 있습니다.
  
  예를 들어 개발자가 특정 업스트림을 선택할 수 있도록 `header`를 기본 정책으로 사용하고, 다른 모든 연결에 대해서는 주/보조 장애 조치(failover)를 구현하기 위해 `first`를 폴백으로 사용할 수 있습니다.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` 은 업스트림을 무작위로 선택합니다.

	- `random_choose <n>` 은 두 개 이상의 업스트림을 무작위로 선택한 다음 부하가 가장 적은 것을 선택합니다(`n`은 보통 2).

	- `first` 는 구성에 정의된 순서대로 사용 가능한 첫 번째 업스트림을 선택하여 주/보조 장애 조치를 가능하게 합니다. 상태 확인을 함께 활성화해야 장애 조치가 발생합니다.

	- `round_robin` 은 각 업스트림을 차례대로 순회합니다.

	- `weighted_round_robin <weights...>` 는 제공된 가중치를 존중하면서 각 업스트림을 차례대로 순회합니다. 가중치 인자의 개수는 구성된 업스트림의 개수와 일치해야 합니다. 가중치는 음수가 아닌 정수여야 합니다. 예를 들어 가중치가 `5 1`인 두 개의 업스트림이 있는 경우, 첫 번째 업스트림이 5번 연속으로 선택된 후 두 번째 업스트림이 한 번 선택되고 다시 주기가 반복됩니다. 가중치로 0을 사용하면 새 요청에 대해 해당 업스트림 선택을 비활성화합니다.

	- `least_conn` 은 현재 요청 수가 가장 적은 업스트림을 선택합니다. 둘 이상의 호스트가 동일한 최소 요청 수를 가지면 그중 하나를 무작위로 선택합니다.

	- `ip_hash` 는 원격 IP(직전 피어)를 고정된(sticky) 업스트림에 매핑합니다.

	- `client_ip_hash` 는 클라이언트 IP를 고정된 업스트림에 매핑합니다. 이는 실제 클라이언트 IP 파싱을 가능하게 하는 [`servers > trusted_proxies` 전역 옵션](/docs/caddyfile/options#trusted-proxies)과 함께 사용하는 것이 가장 좋으며, 그렇지 않으면 `ip_hash`와 동일하게 작동합니다.

	- `uri_hash` 는 요청 URI(경로 및 쿼리)를 고정된 업스트림에 매핑합니다.

	- `query [key]` 는 쿼리 값을 해싱하여 요청 쿼리를 고정된 업스트림에 매핑합니다. 지정된 키가 없으면 폴백 정책을 사용하여 업스트림을 선택합니다(기본값: `random`).

	- `header [field]` 는 헤더 값을 해싱하여 요청 헤더를 고정된 업스트림에 매핑합니다. 지정된 헤더 필드가 없으면 폴백 정책을 사용하여 업스트림을 선택합니다(기본값: `random`).

	- `cookie [<name> [<secret>]]` 은 클라이언트의 첫 번째 요청(쿠키가 없는 경우)에서 폴백 정책을 사용하여 업스트림을 선택하고(기본값: `random`), 응답에 `Set-Cookie` 헤더를 추가합니다(지정되지 않은 경우 기본 쿠키 이름은 `lb`). 쿠키 값은 선택된 업스트림의 전화 접속 주소를 HMAC-SHA256으로 해싱한 값입니다(`<secret>`을 공유 비밀키로 사용하며, 지정되지 않은 경우 빈 문자열 사용).
	
	  쿠키가 존재하는 후속 요청에서 쿠키 값은 사용 가능한 경우 동일한 업스트림에 매핑됩니다. 사용 불가능하거나 찾을 수 없는 경우 폴백 정책으로 새 업스트림을 선택하고 쿠키가 응답에 추가됩니다.

	  디버깅 목적으로 특정 업스트림을 사용하려는 경우 업스트림 주소를 비밀키로 해싱하고 HTTP 클라이언트(브라우저 등)에서 쿠키를 설정할 수 있습니다. 예를 들어 PHP를 사용하면 다음을 실행하여 쿠키 값을 계산할 수 있습니다. 여기서 `10.1.0.10:8080` 은 업스트림 중 하나의 주소이고 `secret` 은 구성된 비밀키입니다.
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  브라우저의 자바스크립트 콘솔을 통해 쿠키를 설정할 수 있습니다. 예를 들어 `lb`라는 이름의 쿠키를 설정하려면 다음과 같이 합니다.
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> 는 다음 사용 가능한 호스트가 다운된 경우 각 요청에 대해 사용 가능한 백엔드를 다시 선택할 횟수입니다. 기본적으로 재시도는 비활성화(0)되어 있습니다.

  If [`lb_try_duration`](#lb_try_duration) is also configured, then retries may stop early if the duration is reached. In other words, the retry duration takes precedence over the retry count.

- **lb_try_duration** <span id="lb_try_duration"/> 은 다음 사용 가능한 호스트가 다운된 경우 각 요청에 대해 사용 가능한 백엔드를 선택하려고 시도하는 시간을 정의하는 [기간 값](/docs/conventions#durations)입니다. 기본적으로 재시도는 비활성화(0 기간)되어 있습니다.

  부하 분산 장치가 사용 가능한 업스트림 호스트를 찾는 동안 클라이언트는 최대 이 시간 동안 대기합니다. HTTP 전송의 기본 다이얼 타임아웃이 `3s`이므로 적절한 시작점은 `5s`일 수 있습니다. 이렇게 하면 첫 번째로 선택된 업스트림에 연결할 수 없는 경우 최소 한 번의 재시도가 가능합니다. 하지만 사용 사례에 맞는 적절한 균형을 찾기 위해 자유롭게 실험해 보세요.

- **lb_try_interval** <span id="lb_try_interval"/> 은 풀에서 다음 호스트를 선택하는 사이의 대기 시간을 정의하는 [기간 값](/docs/conventions#durations)입니다. 기본값은 `250ms`입니다. 업스트림 호스트에 대한 요청이 실패한 경우에만 관련이 있습니다. 0이 아닌 `lb_try_duration`과 함께 이 값을 `0`으로 설정하면 모든 백엔드가 다운되고 지연 시간이 매우 짧을 때 CPU 회전이 발생할 수 있습니다.

- **lb_retry_match** <span id="lb_retry_match"/> 는 재시도가 허용되는 요청을 제한합니다. 업스트림에 대한 연결은 성공했지만 후속 라운드 트립이 실패한 경우 재시도하려면 요청이 이 조건을 충족해야 합니다. 업스트림에 대한 연결이 실패하면 항상 재시도가 허용됩니다. 기본적으로 `GET` 요청만 재시도됩니다.

  이 옵션의 구문은 [이름이 지정된 요청 매처](/docs/caddyfile/matchers#named-matchers)와 동일하지만 `@name`은 없습니다. 단일 매처만 필요한 경우 동일한 라인에서 구성할 수 있습니다. 여러 매처의 경우 블록이 필요합니다.



### 활성 상태 확인 <a id="active-health-checks"></a>

활성 상태 확인은 타이머를 사용하여 백그라운드에서 상태 확인을 수행합니다. 이를 활성화하려면 `health_uri` 또는 `health_port`가 필요합니다.

- **health_uri** <span id="health_uri"/> 는 활성 상태 확인을 위한 URI 경로(및 선택적 쿼리)입니다.

- **health_upstream** <span id="health_upstream"/> 은 업스트림과 다른 경우 활성 상태 확인에 사용할 ip:port입니다. 이는 `health_header` 및 `{http.reverse_proxy.active.target_upstream}`과 함께 사용해야 합니다.

- **health_port** <span id="health_port"/> 는 업스트림의 포트와 다른 경우 활성 상태 확인에 사용할 포트입니다. `health_upstream`이 사용되면 무시됩니다.

- **health_interval** <span id="health_interval"/> 은 활성 상태 확인을 수행하는 빈도를 정의하는 [기간 값](/docs/conventions#durations)입니다. 기본값: `30s`.

- **health_passes** <span id="health_passes"/> 는 백엔드를 다시 정상으로 표시하기 위해 필요한 연속 상태 확인 횟수입니다. 기본값: `1`.

- **health_fails** <span id="health_fails"/> 는 백엔드를 비정상으로 표시하기 위해 필요한 연속 상태 확인 횟수입니다. 기본값: `1`.

- **health_timeout** <span id="health_timeout"/> 은 백엔드를 다운으로 표시하기 전 응답을 기다리는 시간을 정의하는 [기간 값](/docs/conventions#durations)입니다. 기본값: `5s`.

- **health_method** <span id="health_method"/> 는 활성 상태 확인에 사용할 HTTP 메서드입니다. 기본값: `GET`.

- **health_status** <span id="health_status"/> 는 정상적인 백엔드에서 기대하는 HTTP 상태 코드입니다. 3자리 상태 코드이거나 `xx`로 끝나는 상태 코드 클래스일 수 있습니다. 예: `200` (기본값), 또는 `2xx`.

- **health_request_body** <span id="health_request_body"/> 는 활성 상태 확인 시 보낼 요청 본문을 나타내는 문자열입니다.

- **health_body** <span id="health_body"/> 는 활성 상태 확인의 응답 본문에서 일치시킬 부분 문자열 또는 정규 표현식입니다. 백엔드가 일치하는 본문을 반환하지 않으면 다운으로 표시됩니다.

- **health_follow_redirects** <span id="health_follow_redirects"/> 는 상태 확인 시 업스트림에서 제공하는 리다이렉트를 따르도록 합니다. 기본적으로 리다이렉트 응답은 상태 확인 실패로 간주됩니다.

- **health_headers** <span id="health_headers"/> 는 활성 상태 확인 요청에 설정할 헤더를 지정할 수 있게 해줍니다. `Host` 헤더를 변경해야 하거나 상태 확인의 일부로 백엔드에 인증을 제공해야 하는 경우 유용합니다.



### 수동 상태 확인 <a id="passive-health-checks"></a>

수동 상태 확인은 실제 프록시된 요청과 인라인으로 발생합니다. 이를 활성화하려면 `fail_duration`이 필요합니다.

- **fail_duration** <span id="fail_duration"/> 은 실패한 요청을 기억할 기간을 정의하는 [기간 값](/docs/conventions#durations)입니다. `0`보다 큰 기간은 수동 상태 확인을 활성화하며 기본값은 `0`(꺼짐)입니다. 비정상적인 업스트림을 다시 온라인 상태로 가져올 때 응답성과 오류율의 균형을 맞추기 위해 적절한 시작점은 `30s`일 수 있습니다. 하지만 사용 사례에 맞는 적절한 균형을 찾기 위해 자유롭게 실험해 보세요.

- **max_fails** <span id="max_fails"/> 는 백엔드를 다운된 것으로 간주하기 전까지 `fail_duration` 내에 필요한 최대 실패 요청 횟수입니다. `1` 이상이어야 하며 기본값은 `1`입니다.

- **unhealthy_status** <span id="unhealthy_status"/> 는 응답이 이러한 상태 코드 중 하나와 함께 돌아오면 요청이 실패한 것으로 간주합니다. 3자리 상태 코드이거나 `xx`로 끝나는 상태 코드 클래스일 수 있습니다(예: `404` 또는 `5xx`).

- **unhealthy_latency** <span id="unhealthy_latency"/> 는 응답을 받는 데 이 시간이 걸리면 요청이 실패한 것으로 간주하는 [기간 값](/docs/conventions#durations)입니다.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> 는 백엔드를 다운으로 표시하기 전까지 허용되는 동시 요청 수입니다. 즉, 특정 백엔드가 현재 이만큼의 요청을 처리하고 있다면 "과부하"로 간주되어 다른 백엔드가 선호됩니다.

  이 값은 적절히 큰 숫자여야 합니다. 이를 구성하면 프록시가 총 `unhealthy_request_count × upstreams_count`개의 동시 요청 제한을 갖게 되며, 그 이후의 요청은 사용 가능한 업스트림이 없어 오류가 발생합니다.


## 이벤트 <a id="events"></a>

업스트림이 정상 상태에서 비정상 상태로 전환되거나 그 반대의 경우 [이벤트](/docs/caddyfile/options#event-options)가 발생합니다. 이러한 이벤트는 알림 전송이나 메시지 로깅과 같은 다른 작업을 트리거하는 데 사용될 수 있습니다. 이벤트는 다음과 같습니다:

- `healthy` 는 업스트림이 이전에 비정상이었다가 정상으로 표시될 때 발생합니다.
- `unhealthy` 는 업스트림이 이전에 정상이었다가 비정상으로 표시될 때 발생합니다.

두 경우 모두 상태가 변경된 업스트림을 식별하기 위해 `host`가 이벤트의 메타데이터로 포함됩니다. 예를 들어 `exec` 이벤트 핸들러와 함께 `{event.data.host}` 플레이스홀더로 사용할 수 있습니다.



## 스트리밍 <a id="streaming"></a>

기본적으로 프록시는 전송 효율을 위해 응답을 부분적으로 버퍼링합니다.

프록시는 또한 웹소켓(WebSocket) 연결을 지원하여 HTTP 업그레이드 요청을 수행한 다음 연결을 양방향 터널로 전환합니다.

<aside class="tip">

By default, WebSocket connections are forcibly closed (with a Close control message sent to both the client and upstream) when the config is reloaded. Each request holds a reference to the config, so closing old connections is necessary to keep memory usage in check. This closing behaviour can be customized with the [`stream_timeout`](#stream_timeout) and [`stream_close_delay`](#stream_close_delay) options.

</aside>

- **flush_interval** <span id="flush_interval"/> 는 Caddy가 응답 버퍼를 클라이언트로 플러시(flush)해야 하는 빈도를 조정하는 [기간 값](/docs/conventions#durations)입니다. 기본적으로 주기적인 플러시는 수행되지 않습니다. 음수 값(보통 -1)은 응답 버퍼링을 완전히 비활성화하고 클라이언트에 쓸 때마다 즉시 플러시하는 "저지연 모드(low-latency mode)"를 의미하며, 클라이언트가 일찍 연결을 끊더라도 백엔드에 대한 요청을 취소하지 않습니다. 응답에서 다음 중 하나가 적용되는 경우 이 옵션은 무시되고 응답이 클라이언트로 즉시 플러시됩니다:
	- `Content-Type: text/event-stream`
	- `Content-Length` 가 불분명함
	- 프록시 양쪽에서 HTTP/2를 사용하고 `Content-Length` 가 불분명하며 `Accept-Encoding` 이 설정되지 않았거나 "identity"인 경우

- **request_buffers** <span id="request_buffers"/> 를 사용하면 프록시가 요청 본문에서 최대 `<size>` 양의 바이트를 버퍼로 읽어들인 후 업스트림으로 보냅니다. 이는 매우 비효율적이며 업스트림이 지연 없이 요청 본문을 읽어야 하는 경우에만 수행해야 합니다(이는 업스트림 애플리케이션이 수정해야 할 사항입니다). [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go)에서 지원하는 모든 크기 형식을 허용합니다.

- **response_buffers** <span id="response_buffers"/> 를 사용하면 프록시가 응답 본문에서 최대 `<size>` 양의 바이트를 버퍼로 읽어들인 후 클라이언트에 반환합니다. 성능상의 이유로 가능하면 피해야 하지만 백엔드에 더 엄격한 메모리 제약이 있는 경우 유용할 수 있습니다. [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go)에서 지원하는 모든 크기 형식을 허용합니다.

- **stream_timeout** <span id="stream_timeout"/> 은 웹소켓과 같은 스트리밍 요청이 타임아웃 종료 시 강제로 닫히게 되는 [기간 값](/docs/conventions#durations)입니다. 이는 기본적으로 연결이 너무 오랫동안 열려 있는 경우 연결을 취소합니다. 하루보다 오래된 연결을 선별하기 위해 적절한 시작점은 `24h`일 수 있습니다. 기본값: 타임아웃 없음.

- **stream_close_delay** <span id="stream_close_delay"/> 는 구성이 언로드될 때 웹소켓과 같은 스트리밍 요청이 강제로 닫히는 것을 지연시키는 [기간 값](/docs/conventions#durations)입니다. 대신 지연이 완료될 때까지 스트림은 열린 상태로 유지됩니다. 즉, 이를 활성화하면 Caddy의 구성이 다시 로드될 때 스트림이 즉시 닫히는 것을 방지합니다. 이전 구성이 닫히면서 연결이 끊긴 클라이언트가 한꺼번에 다시 연결되는 현상(thundering herd)을 피하기 위해 이를 활성화하는 것이 좋습니다. 구성 다시 로드 후 사용자가 자연스럽게 페이지를 떠날 수 있도록 `5m` 정도의 시간을 주는 것이 적절한 시작점일 수 있습니다. 기본값: 지연 없음.



## 헤더 <a id="headers"></a>

프록시는 자신과 백엔드 사이에서 **헤더를 조작**할 수 있습니다.

- **header_up** <span id="header_up"/> 은 백엔드로 가는 요청 헤더를 설정(set), 추가(`+` 접두사 사용), 삭제(`-` 접두사 사용)하거나 교체(검색 및 교체 두 개의 인자 사용)합니다.

- **header_down** <span id="header_down"/> 은 백엔드에서 내려오는 응답 헤더를 설정, 추가(`+` 접두사 사용), 삭제(`-` 접두사 사용)하거나 교체(검색 및 교체 두 개의 인자 사용)합니다.

예를 들어 기존 값을 덮어쓰고 요청 헤더를 설정하려면 다음과 같이 합니다.

```caddy-d
header_up Some-Header "the value"
```

응답 헤더를 추가하려면 다음과 같이 합니다. 헤더 필드에는 여러 값이 있을 수 있습니다.

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

요청 헤더를 삭제하여 백엔드에 도달하지 못하게 하려면 다음과 같이 합니다.

```caddy-d
header_up -Some-Header
```

접미사 일치를 사용하여 일치하는 모든 요청 헤더를 삭제하려면 다음과 같이 합니다.

```caddy-d
header_up -Some-*
```

모든 요청 헤더를 삭제한 후 원하는 헤더만 개별적으로 추가하려면 다음과 같이 합니다(권장하지 않음).

```caddy-d
header_up -*
```

요청 헤더에 대해 정규 표현식 교체를 수행하려면 다음과 같이 합니다.

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

사용되는 정규 표현식 언어는 Go에 포함된 RE2입니다. [RE2 구문 참조](https://github.com/google/re2/wiki/Syntax) 및 [Go 정규식 구문 개요](https://pkg.go.dev/regexp/syntax)를 참조하세요. 교체 문자열은 [확장(expand)](https://pkg.go.dev/regexp#Regexp.Expand)되어 캡처된 값을 사용할 수 있습니다(예: 첫 번째 캡처 그룹인 `$1`).


### 기본값 <a id="defaults"></a>

기본적으로 Caddy는 세 가지 예외를 제외하고 `Host`를 포함하여 들어오는 헤더를 수정 없이 백엔드로 전달합니다.

- [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) 헤더 필드를 설정하거나 추가합니다.
- [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto) 헤더 필드를 설정합니다.
- [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host) 헤더 필드를 설정합니다.

<span id="trusted_proxies"/> 이러한 `X-Forwarded-*` 헤더의 경우, 기본적으로 프록시는 스푸핑을 방지하기 위해 들어오는 요청의 값을 무시합니다.

If Caddy is not the first server being connected to by your clients (for example when a CDN is in front of Caddy), you may configure `trusted_proxies` with a list of IP ranges (CIDRs) from which incoming requests are trusted to have sent good values for these headers.

It is strongly recommended that you configure this via the [`servers > trusted_proxies` global option](/docs/caddyfile/options#trusted-proxies) instead of in the proxy, so that this applies to all proxy handlers in your server, and this has the benefit of enabling client IP parsing.

<aside class="tip">

If you're using Cloudflare in front of Caddy, be aware that you may be vulnerable to spoofing of the `X-Forwarded-For` header. Our friends at [Authelia](https://www.authelia.com) have documented a [workaround](https://www.authelia.com/integration/proxies/forwarded-headers/) to configure Cloudflare to ignore incoming values for this header.

</aside>

또한 [`http` 전송](#the-http-transport)을 사용할 때 클라이언트의 요청에 헤더가 없으면 `Accept-Encoding: gzip` 헤더가 설정됩니다. 이를 통해 업스트림은 가능한 경우 압축된 콘텐츠를 제공할 수 있습니다. 이 동작은 전송 시 [`compression off`](#compression)로 비활성화할 수 있습니다.


### HTTPS <a id="https"></a>

(대부분의) 헤더는 프록시될 때 원래 값을 유지하므로, HTTPS로 프록시할 때는 구성된 업스트림 주소로 `Host` 헤더를 재정의하여 `Host` 헤더가 TLS ServerName 값과 일치하도록 해야 하는 경우가 많습니다.

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Since Caddy v2.11.0, this is done automatically, so it is no longer necessary to explicitly override the `Host` header when proxying to HTTPS. If you wish to opt out of this behavior, you can set the `Host` header to its original value (but this rarely makes sense to do):

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

The `X-Forwarded-Host` header is still passed [by default](#defaults), so the upstream may still use that if it needs to know the original `Host` header value.

The same applies when terminating TLS in caddy and proxying via HTTP, whether to a port or a unix socket. Indeed, caddy itself must receive the correct Host, when it is the target of `reverse_proxy`. In the unix socket case, the `upstream_hostport` will be the socket path, and the Host must be set explicitly.



## 재작성 <a id="rewrites"></a>

기본적으로 Caddy는 `reverse_proxy`에 도달하기 전 미들웨어 체인에서 재작성이 수행되지 않는 한 들어오는 요청과 동일한 HTTP 메서드 및 URI로 업스트림 요청을 수행합니다.

프록시하기 전에 요청이 복제됩니다. 이는 핸들러 중에 요청에 가해진 모든 수정 사항이 다른 핸들러로 누출되지 않도록 보장합니다. 이는 프록시 이후에도 처리가 계속되어야 하는 상황에서 유용합니다.

In addition to [header manipulations](#headers), the request's method and URI may be changed before it is sent to the upstream:

- **method** <span id="method"/> 는 복제된 요청의 HTTP 메서드를 변경합니다. 메서드가 `GET` 또는 `HEAD` 로 변경되면 들어오는 요청의 본문은 이 핸들러에 의해 업스트림으로 전송되지 않습니다. 이는 다른 핸들러가 요청 본문을 소비하도록 하려는 경우 유용합니다.
- **rewrite** <span id="rewrite"/> 는 복제된 요청의 URI(경로 및 쿼리)를 변경합니다. 이는 [`rewrite` 지시어](/docs/caddyfile/directives/rewrite)와 유사하지만, 이 핸들러의 범위를 벗어나면 재작성이 유지되지 않는다는 점이 다릅니다.

이러한 재작성은 현재 요청의 처리를 계속하는 방법에 대한 결정을 돕기 위해 다른 서버로 요청을 보내는 "사전 확인 요청(pre-check requests)"과 같은 패턴에 유용한 경우가 많습니다.

For example, the request could be sent to an authentication gateway to decide whether the request was from an authenticated user (e.g. the request has a session cookie) and should continue, or should instead be redirected to a login page. For this pattern, Caddy provides a shortcut directive [`forward_auth`](/docs/caddyfile/directives/forward_auth) to skip most of the config boilerplate.




## 전송 <a id="transports"></a>

Caddy의 프록시 **전송(transport)** 은 플러그형입니다.

- **transport** <span id="transport"/> 는 백엔드와 통신하는 방법을 정의합니다. 기본값은 `http` 입니다.


### http 전송 <a id="the-http-transport"></a>

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> 는 읽기 버퍼의 크기(바이트)입니다. [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go)에서 지원하는 모든 형식을 허용합니다. 기본값: `4KiB`.

- **write_buffer** <span id="write_buffer"/> 는 쓰기 버퍼의 크기(바이트)입니다. [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go)에서 지원하는 모든 형식을 허용합니다. 기본값: `4KiB`.

- **max_response_header** <span id="max_response_header"/> 는 응답 헤더에서 읽을 최대 바이트 양입니다. [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go)에서 지원하는 모든 형식을 허용합니다. 기본값: `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> 은 업스트림으로의 연결에서 [PROXY 프로토콜](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt)(HAProxy에서 대중화됨)을 활성화하여 실제 클라이언트 IP 데이터를 앞에 추가합니다. Caddy가 다른 프록시 뒤에 있는 경우 [`servers > trusted_proxies` 전역 옵션](/docs/caddyfile/options#trusted-proxies)과 함께 사용하는 것이 가장 좋습니다. 버전 `v1` 및 `v2` 가 지원됩니다. 이는 업스트림 서버가 PROXY 프로토콜을 파싱할 수 있음을 알고 있는 경우에만 사용해야 합니다. 기본적으로 이는 비활성화되어 있습니다.

- **dial_timeout** <span id="dial_timeout"/> 은 업스트림 소켓에 연결할 때 대기할 최대 [기간](/docs/conventions#durations)입니다. 기본값: `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> 는 RFC 6555 Fast Fallback 연결을 시작하기 전 대기할 최대 [기간](/docs/conventions#durations)입니다. 음수 값은 이를 비활성화합니다. 기본값: `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> 은 업스트림에서 응답 헤더를 읽기 위해 대기할 최대 [기간](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> 은 요청에 `Expect: 100-continue` 헤더가 있는 경우 요청 헤더를 완전히 쓴 후 업스트림의 첫 번째 응답 헤더를 기다리는 최대 [기간](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **read_timeout** <span id="read_timeout"/> 은 백엔드에서 다음 읽기를 대기할 최대 [기간](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **write_timeout** <span id="write_timeout"/> 은 백엔드로 다음 쓰기를 대기할 최대 [기간](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **resolvers** <span id="resolvers"/> 는 시스템 리졸버를 재정의할 DNS 리졸버 목록입니다.

- **tls** <span id="tls"/> 는 백엔드와 HTTPS를 사용합니다. `https://` 스키마를 사용하여 백엔드를 지정하거나 아래의 `tls_*` 옵션 중 하나라도 구성된 경우 자동으로 활성화됩니다.

- **tls_client_auth** <span id="tls_client_auth"/> 는 두 가지 방법 중 하나로 TLS 클라이언트 인증을 활성화합니다. (1) Caddy가 인증서를 가져오고 갱신된 상태를 유지해야 하는 도메인 이름을 지정하거나, (2) 백엔드와 TLS 클라이언트 인증을 위해 제시할 인증서 및 키 파일을 지정합니다.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> 는 TLS 핸드셰이크 확인을 꺼서 연결을 안전하지 않게 만들고 중간자 공격에 취약하게 만듭니다. *프로덕션 환경에서 사용하지 마세요.*

- **tls_curves** <span id="tls_curves"/> 는 업스트림 연결을 위해 지원할 타원 곡선 목록입니다. Caddy의 기본값은 현대적이고 안전하므로 특별한 요구 사항이 있는 경우에만 이를 구성해야 합니다.

- **tls_timeout** <span id="tls_timeout"/> 은 TLS 핸드셰이크가 완료될 때까지 대기할 최대 [기간](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **tls_trust_pool** <span id="tls_trust_pool"/> 은 `tls` 지시어 문서에 설명된 [`trust_pool` 하위 지시어](/docs/caddyfile/directives/tls#trust_pool)와 유사하게 신뢰할 수 있는 인증 기관의 소스를 구성합니다. 표준 Caddy 설치에서 사용 가능한 신뢰 풀 소스 목록은 [여기](/docs/caddyfile/directives/tls#trust-pool-providers)에서 확인할 수 있습니다.

- **tls_server_name** <span id="tls_server_name"/> 은 TLS 핸드셰이크에서 수신된 인증서를 확인할 때 사용되는 서버 이름을 설정합니다. 기본적으로 이는 업스트림 주소의 호스트 부분을 사용합니다.

  You only need to override this if your upstream address does not match the certificate the upstream is likely to use. For example if the upstream address is an IP address, then you would need to configure this to the hostname being served by the upstream server.

  A request placeholder may be used, in which case a clone of the HTTP transport config will be used on every request, which may incur a performance penalty.

- **tls_renegotiation** <span id="tls_renegotiation"/> 은 TLS 재협상 수준을 설정합니다. TLS 재협상은 첫 번째 핸드셰이크 이후에 후속 핸드셰이크를 수행하는 행위입니다. 수준은 다음 중 하나일 수 있습니다.
  - `never` (기본값) 은 재협상을 비활성화합니다.
  - `once` 는 원격 서버가 연결당 한 번 재협상을 요청할 수 있도록 허용합니다.
  - `freely` 는 원격 서버가 반복적으로 재협상을 요청할 수 있도록 허용합니다.

- **tls_except_ports** <span id="tls_except_ports"/> 는 TLS가 활성화된 경우 업스트림 대상이 지정된 포트 중 하나를 사용하면 해당 연결에 대해 TLS가 비활성화됩니다. 이는 일부 업스트림은 HTTP를 기대하고 다른 업스트림은 HTTPS 요청을 기대하는 동적 업스트림을 구성할 때 유용할 수 있습니다.

- **keepalive** <span id="keepalive"/> 는 `off` 이거나 연결을 열린 상태로 유지할 시간(타임아웃)을 지정하는 [기간 값](/docs/conventions#durations)입니다. 기본값: `2m`.

  ⚠️ Requests to HTTP/1.1 upstreams may fail due to "connection reset by peer" errors if the keepalive duration exceeds the upstream server's keepalive timeout. Idempotent requests will be retried by Go's HTTP transport, but Caddy will respond with status code 502 in other cases.

- **keepalive_interval** <span id="keepalive_interval"/> 은 활성 프로브 사이의 [기간](/docs/conventions#durations)입니다. 기본값: `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> 는 활성 상태로 유지할 최대 연결 수를 정의합니다. 기본값: 제한 없음.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> 가 0이 아니면 호스트당 유지할 최대 유휴(keep-alive) 연결 수를 제어합니다. 기본값: `32`.

- **versions** <span id="versions"/> 를 사용하면 지원할 HTTP 버전을 사용자 정의할 수 있습니다.
  
  Valid options are: `1.1`, `2`, `h2c`, `3`. 

  Default: `1.1 2`, or if the [upstream's scheme](#upstream-addresses) is `h2c://`, then the default is `h2c 2`.

  `h2c` 는 업스트림으로의 일반 텍스트 HTTP/2 연결을 활성화합니다. 이는 Go의 기본 HTTP 전송을 사용하지 않는 비표준 기능이므로 다른 기능과 상충됩니다.

  `3` 은 업스트림으로의 HTTP/3 연결을 활성화합니다. ⚠️ 이는 실험적 기능이며 변경될 수 있습니다.

- **compression** <span id="compression"/> 을 `off` 로 설정하여 백엔드로의 압축을 비활성화할 수 있습니다.

- **max_conns_per_host** <span id="max_conns_per_host"/> 는 선택 사항으로 다이얼링, 활성 및 유휴 상태의 연결을 포함하여 호스트당 총 연결 수를 제한합니다. 기본값: 제한 없음.

- **network_proxy** <span id="network_proxy"/> 는 업스트림 서버에 대한 요청에 사용할 네트워크 프록시 모듈의 이름을 지정합니다. 명시적으로 구성하지 않으면 Caddy는 [Go 표준 라이브러리](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment)에 따라 환경 변수를 통해 구성된 프록시(`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`)를 존중합니다. 이 매개변수에 값이 제공되면 요청은 클라이언트(사용자) → `reverse_proxy` → `network_proxy` → 업스트림 순서로 흐릅니다. 기본 제공 모듈은 다음과 같습니다.
	- `none`: `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` 의 환경 설정을 무시하는 데 사용됩니다.
	- `url <url>`: 환경 구성을 재정의하는 단일 URL을 지정하는 데 사용됩니다.

### fastcgi 전송 <a id="the-fastcgi-transport"></a>

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> 는 사이트의 루트입니다. 기본값: `{http.vars.root}` 또는 현재 작업 디렉토리.

- **split** <span id="split"/> 은 URI 끝에서 PATH_INFO를 가져오기 위해 경로를 나눌 위치입니다.

- **env** <span id="env"/> 는 추가 환경 변수를 지정된 값으로 설정합니다. 여러 환경 변수에 대해 두 번 이상 지정할 수 있습니다.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> 는 심볼릭 링크가 존재하는 경우 이를 평가하여 `root` 디렉토리를 실제 값으로 분석하도록 활성화합니다.

- **dial_timeout** <span id="dial_timeout"/> 은 업스트림 소켓에 연결할 때 대기할 시간입니다. [기간 값](/docs/conventions#durations)을 허용합니다. 기본값: `3s`.

- **read_timeout** <span id="read_timeout"/> 은 FastCGI 서버에서 읽을 때 대기할 시간입니다. [기간 값](/docs/conventions#durations)을 허용합니다. 기본값: 타임아웃 없음.

- **write_timeout** <span id="write_timeout"/> 은 FastCGI 서버로 보낼 때 대기할 시간입니다. [기간 값](/docs/conventions#durations)을 허용합니다. 기본값: 타임아웃 없음.

- **capture_stderr** <span id="capture_stderr"/> 를 사용하면 업스트림 FastCGI 서버가 `stderr` 로 보내는 모든 메시지를 캡처하고 기록할 수 있습니다. 로깅은 기본적으로 `WARN` 수준에서 수행됩니다. 응답에 `4xx` 또는 `5xx` 상태가 있으면 `ERROR` 수준이 대신 사용됩니다. 기본적으로 `stderr` 은 무시됩니다.

<aside class="tip">

If you're trying to serve a modern PHP application, you may be looking for the [`php_fastcgi` directive](/docs/caddyfile/directives/php_fastcgi), which is a shortcut for a proxy using the `fastcgi` directive, with the necessary rewrites for using `index.php` as the routing entrypoint.

</aside>



## 응답 가로채기 <a id="intercepting-responses"></a>

리버스 프록시는 백엔드로부터의 응답을 가로채도록 구성할 수 있습니다. 이를 용이하게 하기 위해 (요청 매처 구문과 유사하게) [응답 매처](/docs/caddyfile/response-matchers)를 정의할 수 있으며 첫 번째 일치하는 `handle_response` 경로가 호출됩니다.

응답 핸들러가 호출되면 백엔드의 응답은 클라이언트에 기록되지 않고 구성된 `handle_response` 경로가 대신 실행되며, 해당 경로에서 응답을 기록하는 것은 그 경로의 몫입니다. 경로가 응답을 기록하지 *않으면* 요청 처리는 이 `reverse_proxy` 뒤에 [순서가 지정된](/docs/caddyfile/directives#directive-order) 모든 핸들러와 함께 계속됩니다.

- **@name** 은 [응답 매처](/docs/caddyfile/response-matchers)의 이름입니다. 각 응답 매처가 고유한 이름을 갖는 한 여러 매처를 정의할 수 있습니다. 응답은 상태 코드와 응답 헤더의 존재 여부 또는 값으로 일치시킬 수 있습니다.

- **replace_status** <span id="replace_status"/> 는 지정된 매처와 일치할 때 단순히 응답의 상태 코드를 변경합니다.

- **handle_response** <span id="handle_response"/> 는 지정된 매처와 일치할 때(또는 매처를 생략한 경우 모든 응답에 대해) 실행할 경로를 정의합니다. 첫 번째로 일치하는 블록이 적용됩니다. `handle_response` 블록 내부에서는 다른 모든 [지시어](/docs/caddyfile/directives)를 사용할 수 있습니다.

또한 `handle_response` 내부에서는 두 가지 특수 핸들러 지시어를 사용할 수 있습니다.

- **copy_response** <span id="copy_response"/> 는 백엔드로부터 받은 응답 본문을 클라이언트에 다시 복사합니다. 선택적으로 그렇게 하는 동안 응답의 상태 코드를 변경할 수 있게 해줍니다. 이 지시어는 [`respond` 보다 먼저 순서가 지정됩니다](/docs/caddyfile/directives#directive-order).

- **copy_response_headers** <span id="copy_response_headers"/> 는 백엔드의 응답 헤더를 클라이언트로 복사하며 선택적으로 헤더 필드 목록을 포함하거나 제외할 수 있습니다(`include`와 `exclude`를 동시에 지정할 수 없음). 이 지시어는 [`header` 보다 나중에 순서가 지정됩니다](/docs/caddyfile/directives#directive-order).

Three placeholders will be made available within the `handle_response` routes:

- `{rp.status_code}` 백엔드 응답의 상태 코드입니다.

- `{rp.status_text}` 백엔드 응답의 상태 텍스트입니다.

- `{rp.header.*}` 백엔드 응답의 헤더입니다.

While the reverse proxy response handler can copy the new response received from the proxy back to the client, it cannot pass on that new response to a subsequent reverse proxy. Every use of `reverse_proxy` receives the body from the original request (or as modified with a different module).




## 예시 <a id="examples"></a>

Reverse proxy all requests to a local backend:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


[Load-balance](#load-balancing) all requests [between 3 backends](#upstreams):

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


Same, but only requests within `/api`, and sticky by using the [`cookie` policy](#lb_policy):

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


Using [active health checks](#active-health-checks) to determine which backends are healthy, and enabling [retries](#lb_try_duration) on failed connections, holding the request until a healthy backend is found:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Configure some [transport options](#transports):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Reverse proxy to an [HTTPS upstream](#https) (since v2.11.0, Caddy will automatically set the `Host` header to match the upstream's host, so it is no longer necessary to do so manually):

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Reverse proxy to an HTTPS upstream, but [⚠️ disable TLS verification](#tls_insecure_skip_verify). This is NOT RECOMMENDED, since it disables all security checks that HTTPS offers; proxying over HTTP in private networks is preferred if possible, because it avoids the false sense of security:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


Instead you may establish trust with the upstream by explicitly [trusting the upstream's certificate](#tls_trust_pool), and (optionally) setting TLS-SNI to match the hostname in the upstream's certificate:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



[Strip a path prefix](handle_path) before proxying; but be aware of the [subfolder problem <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575):

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


Replace a path prefix before proxying, using a [`rewrite`](/docs/caddyfile/directives/rewrite):

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


`X-Accel-Redirect` support, i.e. serving static files as requested, by [intercepting the response](#intercepting-responses):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Custom error page for errors from upstream, by [intercepting error responses](#intercepting-responses) by status code:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Get backends [dynamically](#dynamic-upstreams) from [`A`/`AAAA` record](#aaaaa) DNS queries:

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Get backends [dynamically](#dynamic-upstreams) from [`SRV` record](#srv) DNS queries:

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


Using [active health checks](#active-health-checks) and `health_upstream` can be helpful when creating an intermediate service to do a more thorough health check. `{http.reverse_proxy.active.target_upstream}` can then be used as a header to provide the original upstream to the health check service.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
