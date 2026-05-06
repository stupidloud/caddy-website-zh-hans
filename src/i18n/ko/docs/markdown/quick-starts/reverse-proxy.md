---
title: Reverse proxy quick-start
---

# 리버스 프록시 빠른 시작

이 가이드는 HTTPS를 사용하거나 사용하지 않는 프로덕션 수준의 리버스 프록시를 즉시 설정하고 실행하는 방법을 알려줍니다.

**사전 준비사항:**
- 기본적인 터미널 / 명령줄 기술
- PATH에 `caddy` 포함
- 프록시 대상인 실행 중인 백엔드 프로세스

---

이 튜토리얼은 백엔드 HTTP 서비스가 `127.0.0.1:9000`에서 실행되고 있다고 가정합니다. 이 명령어들은 Linux용이지만 다른 운영 체제에도 동일한 원리가 적용됩니다.

설정 파일 없이 간단한 리버스 프록시를 실행하거나 설정 파일을 사용하여 더 많은 유연성과 제어를 수행할 수 있습니다.


## 명령줄

기기의 2080번 포트에서 9000번 포트로 평문 HTTP 프록시를 시작하려면 다음을 실행합니다:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

그런 다음 테스트해 봅니다:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

[`reverse-proxy` 명령어](/docs/command-line#reverse-proxy)는 빠르고 쉬운 리버스 프록시를 위한 것입니다. (요구 사항이 간단하다면 프로덕션 환경에서도 사용할 수 있습니다.)

## Caddyfile

현재 작업 디렉토리에 다음 내용으로 `Caddyfile`이라는 파일을 만듭니다:

```caddy
:2080

reverse_proxy :9000
```

이 설정 파일은 위의 `caddy reverse-proxy` 명령어와 대략적으로 동일합니다.

그런 다음 동일한 디렉토리에서 다음을 실행합니다:

<pre><code class="cmd bash">caddy run</code></pre>

그런 다음 프록시를 테스트해 봅니다:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Caddyfile을 변경한 경우 Caddy를 반드시 [다시 로드(reload)](/docs/command-line#caddy-reload)하세요.

이것은 간단한 예시였습니다. [`reverse_proxy` 지시어](/docs/caddyfile/directives/reverse_proxy)를 사용하여 훨씬 더 많은 작업을 수행할 수 있습니다.

## 클라이언트에서 프록시까지의 HTTPS

Caddy는 호스트 이름(도메인 이름)을 알고 있는 경우 자동으로, 그리고 기본적으로 [HTTPS를 통해 프록시를 제공합니다](/docs/automatic-https). `--from` 플래그를 생략하면 `caddy reverse-proxy` 명령어의 기본값은 `localhost`가 되며, Caddyfile의 첫 번째 줄을 프록시의 도메인 이름으로 바꿀 수도 있습니다.

- `localhost` 또는 `.localhost`로 끝나는 도메인을 사용하면 Caddy는 자동 갱신되는 자체 서명 인증서(self-signed certificate)를 사용합니다. 처음 이 작업을 수행할 때 Caddy가 CA의 루트 인증서를 시스템의 신뢰 저장소(trust store)에 설치하려고 시도하므로 비밀번호를 입력해야 할 수도 있습니다.
- 다른 도메인 이름을 사용하는 경우 Caddy는 공개적으로 신뢰할 수 있는 인증서를 발급받으려고 시도합니다. DNS 레코드가 기기를 가리키는지, 포트 80과 443이 공개적으로 열려 있고 Caddy를 가리키는지 확인하세요.

포트를 지정하지 않으면 Caddy는 HTTPS의 기본값으로 443을 사용합니다. 이 경우 낮은 포트(low ports)에 바인딩할 권한도 필요합니다. Linux에서 이 작업을 수행하는 두 가지 방법은 다음과 같습니다:

- root 권한으로 실행 (예: `sudo -E`).
- 또는 `sudo setcap cap_net_bind_service=+ep $(which caddy)`를 실행하여 Caddy에 이 특정 권한을 부여.

HTTPS를 제공하는 가장 기본적인 `caddy reverse-proxy` 명령어는 다음과 같습니다:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

그런 다음 테스트해 봅니다:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

`--from` 플래그를 사용하여 호스트 이름을 커스텀할 수 있습니다:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

낮은 포트에 바인딩할 권한이 없는 경우 더 높은 포트에서 프록시할 수 있습니다:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Caddyfile을 사용하는 경우 첫 번째 줄을 도메인 이름으로 변경하기만 하면 됩니다. 예:

```caddy
example.com

reverse_proxy :9000
```

## 프록시에서 백엔드까지의 HTTPS

백엔드가 TLS를 지원하는 경우 Caddy는 자신과 백엔드 간에 HTTPS를 사용하여 프록시를 수행할 수도 있습니다. 백엔드 주소에 `https://`를 사용하기만 하면 됩니다:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

이렇게 하려면 백엔드의 인증서가 Caddy가 실행 중인 시스템에서 신뢰할 수 있어야 합니다. (Caddy는 명시적으로 설정되지 않은 한 자체 서명 인증서를 신뢰하지 않습니다.)

물론 양쪽 모두에서 HTTPS를 수행할 수도 있습니다:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

이렇게 하면 클라이언트에서 프록시까지, 그리고 프록시에서 백엔드까지 HTTPS가 제공됩니다.

프록시 대상을 향하는(to) 호스트 이름이 프록시 출처의(from) 호스트 이름과 다른 경우 `--change-host-header` 플래그를 사용해야 합니다:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

기본적으로 Caddy는 `Host`를 포함한 모든 HTTP 헤더를 변경하지 않고 통과시키며, Caddy는 Host 헤더에서 TLS ServerName을 파생합니다. `--change-host-header`는 TLS 핸드셰이크가 성공적으로 완료될 수 있도록 Host 헤더를 백엔드의 Host 헤더로 재설정합니다. 위의 예시에서 `example.com`에서 `localhost:9000`으로 변경됩니다 (그리고 TLS 핸드셰이크에서는 `localhost`가 사용됩니다).
