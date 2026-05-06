---
title: Static files quick-start
---

# 정적 파일 빠른 시작

이 가이드는 프로덕션 수준의 정적 파일 서버를 즉시 구동하고 실행하는 방법을 알려줍니다.

**사전 준비사항:**
- 기본적인 터미널 / 명령줄 기술
- PATH에 `caddy` 포함
- 웹사이트가 포함된 폴더

---

빠른 파일 서버를 구동하고 실행하는 두 가지 쉬운 방법이 있습니다.

## 명령줄

터미널에서 사이트의 루트 디렉토리로 이동한 후 다음을 실행합니다:

<pre><code class="cmd bash">caddy file-server</code></pre>

권한 오류가 발생하면 운영 체제에서 낮은 포트(low ports)에 바인딩하는 것을 허용하지 않기 때문일 가능성이 높으므로 다음과 같이 높은 포트를 대신 사용하세요:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

그런 다음 브라우저에서 [localhost](http://localhost) (또는 [localhost:2015](http://localhost:2015))를 열어 사이트를 확인하세요!

인덱스 파일(index file)이 없지만 파일 목록을 표시하려면 `--browse` 옵션을 사용합니다:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

다른 폴더를 사이트 루트로 사용할 수 있습니다:

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



## Caddyfile

사이트의 루트에 다음 내용으로 `Caddyfile`이라는 파일을 만듭니다:

```caddy
localhost

file_server
```

낮은 포트에 바인딩할 권한이 없는 경우 `localhost`를 `localhost:2015`(또는 다른 높은 포트)로 바꿉니다.

그런 다음 동일한 디렉토리에서 다음을 실행합니다:

<pre><code class="cmd bash">caddy run</code></pre>

이제 브라우저에서 [localhost](https://localhost)(또는 설정의 주소)를 불러와 사이트를 볼 수 있습니다!

[`file_server` 지시어](/docs/caddyfile/directives/file_server)에는 사이트를 커스텀할 수 있는 더 많은 옵션이 있습니다. Caddyfile을 변경할 때는 Caddy를 [다시 로드(reload)](/docs/command-line#caddy-reload)하거나(또는 중지 후 다시 시작) 해야 합니다!

인덱스 파일이 없지만 파일 목록을 표시하려면 `browse` 인수를 사용합니다:

```caddy
localhost

file_server browse
```

다음과 같이 다른 폴더를 사이트 루트로 사용할 수도 있습니다:

```caddy
localhost

root /var/www/mysite
file_server
```
