---
title: forward_auth (Caddyfile 지시어)
---

<script>
ready(function() {
	// 코드 블록의 > 수정
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// >로 끝나면 건너뜀
			if (item.innerText.trim().endsWith('>')) return;
			// >를 <span class="p">&gt;</span>로 교체
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// uri 하위 지시어 수정. "uri" 지시어 때문에 매처 인자로 파싱되는 문제 해결
	$$_('.k').forEach(item => {
		if (item.innerText.includes('uri') && item.nextElementSibling && item.nextElementSibling.classList.contains('nd')) {
			const next = item.nextElementSibling;
			next.classList.remove('nd');
			next.classList.add('s');
			next.textContent = next.textContent;
		}
	});
});
</script>

# forward_auth

요청의 복제본을 인증 게이트웨이로 프록시하여, 처리를 계속할지 아니면 로그인 페이지로 보내야 할지를 결정하는 독자적인 방식의 지시어입니다.

- [구문](#syntax)
- [확장된 형태](#expanded-form)
- [예시](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Caddy의 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)도 외부 서비스에 "사전 확인 요청(pre-check requests)"을 수행할 수 있지만, 이 지시어는 인증 사례에 특별히 맞춰져 있습니다. 이 지시어는 사실 더 길고 일반적인 설정을 편리하게 사용할 수 있도록 만든 단축어입니다(아래 참조).

이 지시어는 `uri`가 리라이트된 상태로 설정된 업스트림에 `GET` 요청을 보냅니다:
- 업스트림이 `2xx` 상태 코드로 응답하면 액세스가 허용되며, `copy_headers`에 지정된 헤더 필드들이 원래 요청에 복사되고 처리가 계속됩니다.
- 그렇지 않고 업스트림이 다른 상태 코드로 응답하면 업스트림의 응답이 클라이언트에 그대로 전달됩니다. 이 응답에는 보통 인증 게이트웨이의 로그인 페이지로 리다이렉트하는 내용이 포함됩니다.

이 동작이 정확히 원하는 방식이 아니라면, 아래의 [확장된 형태](#expanded-form)를 참고하여 필요에 맞게 커스터마이징할 수 있습니다.

[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)의 모든 하위 지시어가 지원되며 내부 `reverse_proxy` 핸들러로 전달됩니다.


## 구문 <a id="syntax"></a>

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** 는 인증 요청을 보낼 업스트림(백엔드) 목록입니다.

- **uri** 는 업스트림에 보내는 요청에 설정할 URI(경로 및 쿼리)입니다. 이는 보통 인증 게이트웨이의 검증 엔드포인트입니다.

- **copy_headers** 는 요청이 성공 상태 코드를 받았을 때 응답에서 원래 요청으로 복사할 HTTP 헤더 필드 목록입니다.

  `>` 뒤에 새 이름을 지정하여 필드 이름을 변경할 수 있습니다. 예를 들어 `Before>After`와 같이 사용합니다.

  가독성을 위해 블록을 사용하여 한 줄에 하나씩 필드를 나열할 수도 있습니다.

이 지시어는 리버스 프록시를 래핑한 것이므로, [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax)의 모든 하위 지시어를 사용하여 커스터마이징할 수 있습니다.


## 확장된 형태 <a id="expanded-form"></a>

`forward_auth` 지시어는 다음 설정과 동일합니다. [Authelia](https://www.authelia.com/)와 같은 인증 게이트웨이는 이 프리셋과 잘 작동합니다. 만약 여러분의 게이트웨이가 작동하지 않는다면, `forward_auth` 단축어 대신 이 내용을 참고하여 필요에 맞게 수정해 사용하세요.

```caddy-d
reverse_proxy <upstreams...> {
	# 들어오는 요청 본문이 소비되지 않도록
	# 항상 GET을 사용합니다.
	method GET

	# URI를 인증 게이트웨이의
	# 검증 엔드포인트로 변경합니다.
	rewrite <to>

	# 위에서 URI가 리라이트되므로 원래의 메서드와
	# URI를 전달합니다. 이는 reverse_proxy에서
	# 이미 설정된 다른 X-Forwarded-* 헤더에 추가됩니다.
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# 성공적인 응답 시 응답 헤더를 복사합니다.
	@good status 2xx
	handle_response @good {
		# 예를 들어, 각 copy_headers 필드에 대해...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


## 예시 <a id="examples"></a>


### Authelia

리버스 프록시를 통해 앱을 제공하기 전에 [Authelia](https://www.authelia.com/)에 인증을 위임하는 예시입니다:

```caddy
# 인증 게이트웨이 자체를 서비스
auth.example.com {
	reverse_proxy authelia:9091
}

# 앱 서비스
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

자세한 내용은 Caddy와의 연동을 위한 [Authelia 문서](https://www.authelia.com/integration/proxies/caddy/)를 참조하세요.


### Tailscale

[Tailscale](https://tailscale.com/)(현재 이름은 [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/)이지만 Caddy에서도 작동함)에 인증을 위임하고, `copy_headers`의 대체 구문을 사용하여 복사된 헤더의 이름을 *변경*하는 예시입니다(각 헤더의 `>` 확인):

```caddy-d
forward_auth unix//run/tailscale.nginx-auth.sock {
	uri /auth
	header_up Remote-Addr {remote_host}
	header_up Remote-Port {remote_port}
	header_up Original-URI {uri}
	copy_headers {
		Tailscale-User>X-Webauth-User
		Tailscale-Name>X-Webauth-Name
		Tailscale-Login>X-Webauth-Login
		Tailscale-Tailnet>X-Webauth-Tailnet
		Tailscale-Profile-Picture>X-Webauth-Profile-Picture
	}
}
```
