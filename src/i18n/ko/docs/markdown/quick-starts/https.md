---
title: HTTPS quick-start
---

# HTTPS 빠른 시작

이 가이드는 [완전 관리형 HTTPS](/docs/automatic-https)를 즉시 실행하고 구동하는 방법을 알려줍니다.

<aside class="tip">
	Caddy는 설정에 호스트 이름이 제공되는 한 기본적으로 모든 사이트에 HTTPS를 사용합니다. 이 튜토리얼은 공개적으로 신뢰할 수 있는 사이트(즉, "localhost"가 아닌 사이트)를 HTTPS로 올린다고 가정하므로, 퍼블릭 도메인 이름과 외부 포트를 사용합니다.
</aside>

**사전 준비사항:**
- 기본적인 터미널 / 명령줄 기술
- DNS에 대한 기본 이해
- 등록된 퍼블릭 도메인 이름
- 포트 80 및 443에 대한 외부 접속 허용
- PATH에 `caddy`와 `curl` 포함

---

이 튜토리얼에서는 `example.com`을 실제 도메인 이름으로 변경하세요.

도메인의 A/AAAA 레코드가 서버를 가리키도록 설정합니다. 이 작업은 DNS 제공업체에 로그인하여 도메인 이름을 관리함으로써 수행할 수 있습니다.

계속하기 전에 신뢰할 수 있는 조회를 통해 레코드가 올바른지 확인하세요. `example.com`을 도메인 이름으로 변경하고 IPv6를 사용하는 경우 `type=A`를 `type=AAAA`로 변경합니다:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

또한 퍼블릭 인터페이스에서 포트 80과 443으로 서버에 외부 접속이 가능한지 확인하세요.

<aside class="tip">
	가정용 네트워크나 제한된 네트워크에 있는 경우 포트를 포워딩하거나 방화벽 설정을 조정해야 할 수도 있습니다.
</aside>

우리가 해야 할 일은 도메인 이름을 설정에 넣고 Caddy를 시작하는 것뿐입니다. 여기에는 몇 가지 방법이 있습니다.

## Caddyfile

이 방법은 HTTPS를 얻는 가장 일반적인 방법입니다.

첫 번째 줄에 도메인 이름이 들어가는 `Caddyfile`(확장자 없음)이라는 파일을 만듭니다. 예를 들면:

```caddy
example.com

respond "Hello, privacy!"
```

그런 다음 동일한 디렉토리에서 다음을 실행합니다:

<pre><code class="cmd bash">caddy run</code></pre>

Caddy가 TLS 인증서를 프로비저닝하고 HTTPS를 통해 사이트를 제공하는 것을 볼 수 있습니다. 이는 Caddyfile의 사이트 주소에 도메인 이름이 포함되어 있었기 때문에 가능했습니다.


## `file-server` 명령어

HTTPS를 통해 정적 파일을 제공하기만 하면 되는 경우 다음 명령어를 실행합니다(도메인 이름으로 변경):

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Caddy가 TLS 인증서를 프로비저닝하고 HTTPS를 통해 사이트를 제공하는 것을 볼 수 있습니다.


## `reverse-proxy` 명령어

HTTPS를 통한 간단한 역방향 프록시(TLS 터미네이터 역할)만 필요한 경우 다음 명령어를 실행합니다(도메인 이름과 실제 백엔드 주소로 변경):

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Caddy가 TLS 인증서를 프로비저닝하고 HTTPS를 통해 사이트를 제공하는 것을 볼 수 있습니다.


## JSON 설정

일반적인 원칙은 [호스트 매처(host matcher)](/docs/json/apps/http/servers/routes/match/host/)가 자동 HTTPS를 트리거한다는 것입니다.

따라서 다음과 같은 JSON 설정은 프로덕션 수준의 [자동 HTTPS](/docs/automatic-https)를 활성화합니다:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
