---
title: acme_server (Caddyfile 지시어)
---

# acme_server

내장된 [ACME 프로토콜](https://tools.ietf.org/html/rfc8555) 서버 핸들러입니다. 이를 통해 Caddy 인스턴스는 다른 ACME 호환 소프트웨어(다른 Caddy 인스턴스 포함)를 위한 인증서를 발급할 수 있습니다.

활성화되면 `/acme/*` 경로와 일치하는 요청은 ACME 서버에 의해 처리됩니다.


## 클라이언트 설정

ACME 서버 기본값을 사용하는 경우, ACME 클라이언트는 ACME 엔드포인트로 `https://localhost/acme/local/directory`를 사용하도록 설정하기만 하면 됩니다. (`local`은 Caddy의 기본 CA ID입니다.)


## 구문

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <duration>
	resolvers  <resolvers...>
	challenges <challenges...>
	allow_wildcard_names
	allow {
		domains <domains...>
		ip_ranges <addresses...>
	}
	deny {
		domains <domains...>
		ip_ranges <addresses...>
	}
}
```

- **ca** 는 인증서 서명에 사용할 인증 기관(CA)의 ID를 지정합니다. 기본값은 `local`이며, 이는 Caddy의 기본 CA로 로컬에서 사용되는 자체 서명 인증서를 위한 것이며 개발 환경에서 가장 일반적입니다. 더 넓은 용도로 사용하려면 혼동을 피하기 위해 다른 CA를 지정하는 것이 좋습니다. 지정된 ID의 CA가 이미 존재하지 않으면 새로 생성됩니다. 대체 CA를 설정하려면 [PKI 앱 전역 옵션](/docs/caddyfile/options#pki-options)을 참조하세요.

- **lifetime** (기본값: `12h`) 은 발급된 인증서의 유효 기간을 지정하는 [기간](/docs/conventions#durations)입니다. 이 값은 서명에 사용되는 [중간 인증서(intermediate certificate)](/docs/caddyfile/options#intermediate-lifetime)의 수명보다 짧아야 합니다. 꼭 필요한 경우가 아니면 이 값을 변경하지 않는 것이 좋습니다.

- **resolvers** 는 ACME DNS 챌린지를 해결하기 위해 TXT 레코드를 조회할 때 사용할 DNS 리졸버의 주소입니다. 별도로 지정하지 않으면 기본적으로 UDP와 53번 포트를 사용하는 [네트워크 주소](/docs/conventions#network-addresses)를 허용합니다. 호스트가 IP 주소인 경우 업스트림 서버를 확인하기 위해 직접 연결됩니다. 호스트가 IP 주소가 아닌 경우 Go 표준 라이브러리의 [이름 확인 규칙(name resolution convention)](https://golang.org/pkg/net/#hdr-Name_Resolution)을 사용하여 주소를 확인합니다. 여러 리졸버가 지정된 경우 그중 하나가 무작위로 선택됩니다.

- **challenges** 는 활성화할 챌린지 유형을 설정합니다. 설정하지 않거나 지시어에 값 없이 사용하면 모든 챌린지 유형이 활성화됩니다. 허용되는 값은 http-01, tls-alpn-01, dns-01입니다.

- **allow_wildcard_names** 는 와일드카드 SAN (Subject Alternative Name)을 포함한 인증서 발급을 활성화합니다.

- **allow**, **deny** 는 `acme_server`의 운영 정책을 설정합니다. 정책 평가는 [여기](https://smallstep.com/docs/step-ca/policies/#policy-evaluation)에 설명된 Step-CA 기준을 따릅니다.

	- **domains** 는 정책 평가 기준에 따라 허용하거나 거부할 주체 도메인 이름을 설정합니다.

	- **ip_ranges** 는 정책 평가 기준에 따라 허용하거나 거부할 주체 IP 범위를 설정합니다.

## 예시

`acme.example.com` 도메인에서 ID가 `home`인 ACME 서버를 운영하고, [`pki` 전역 옵션](/docs/caddyfile/options#pki-options)을 통해 CA를 커스터마이징하며, `internal` 발급자를 사용하여 자체 인증서를 발급하는 예시입니다:

```caddy
{
	pki {
		ca home {
			name "My Home CA"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

다른 Caddy 서버가 있다면, 위 ACME 서버를 사용하여 자체 인증서를 발급받을 수 있습니다:

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
