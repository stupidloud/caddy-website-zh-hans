---
title: Caddyfile Quick-start
---

# Caddyfile 빠른 시작

`Caddyfile`이라는 이름의 새로운 텍스트 파일(확장자 없음)을 만듭니다.

Caddyfile에 가장 먼저 입력할 내용은 사이트의 주소입니다:

```caddy
localhost
```

<aside class="tip">

HTTP 및 HTTPS 포트(각각 80 및 443)가 운영 체제에서 권한이 필요한 포트(privileged ports)인 경우, 관리자 권한으로 실행하거나 더 높은 번호의 포트를 사용해야 합니다. 권한을 얻으려면 `sudo -E`를 사용하여 root 권한으로 실행하거나 `sudo setcap cap_net_bind_service=+ep $(which caddy)`를 사용하세요. 또는 더 높은 번호의 포트를 사용하려면 주소를 `localhost:2080`과 같이 변경하고 [`http_port`](/docs/caddyfile/options) Caddyfile 옵션을 사용하여 HTTP 포트를 변경하면 됩니다.

</aside>

그런 다음 Enter 키를 누르고 수행할 작업을 입력하여 다음과 같이 만듭니다:

```caddy
localhost

respond "Hello, world!"
```

이를 저장하고 Caddyfile이 포함된 동일한 폴더에서 Caddy를 실행합니다:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy는 기본적으로 로컬 사이트를 포함한 모든 사이트를 HTTPS를 통해 제공하므로 비밀번호를 묻는 메시지가 표시될 수 있습니다. (비밀번호 프롬프트는 처음 한 번만 나타납니다!)

<aside class="tip">

로컬 HTTPS의 경우 Caddy가 인증서와 고유한 프라이빗 키를 자동으로 생성합니다. 루트 인증서가 시스템의 신뢰 저장소(trust store)에 추가되기 때문에 비밀번호를 입력해야 합니다. 이 과정을 통해 인증서 오류 없이 HTTPS를 통해 로컬에서 개발할 수 있습니다.

</aside>

(권한 오류가 발생하면 관리자 권한으로 실행하거나 1023보다 높은 포트를 선택해야 할 수도 있습니다.)

브라우저에서 [localhost](http://localhost)를 열거나 `curl`을 사용해 봅니다:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

중괄호 `{ }`로 감싸면 Caddyfile에 여러 사이트를 정의할 수 있습니다. Caddyfile을 다음과 같이 변경합니다:

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

두 가지 방법으로 Caddy에 업데이트된 설정을 제공할 수 있습니다. 직접 API를 사용하거나:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

또는 백그라운드에서 동일한 API 요청을 대신 수행해 주는 reload 명령어를 사용합니다:

<pre><code class="cmd bash">caddy reload</code></pre>

새로운 "goodbye" 엔드포인트를 [브라우저](https://localhost:2016)나 `curl`에서 테스트하여 제대로 작동하는지 확인해 보세요:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Caddy 사용을 완료했다면 중지하는 것을 잊지 마세요:

<pre><code class="cmd bash">caddy stop</code></pre>

## 더 읽어보기

- [Caddyfile 개념](/docs/caddyfile/concepts)
- [지시어](/docs/caddyfile/directives)
- [일반적인 패턴](/docs/caddyfile/patterns)
