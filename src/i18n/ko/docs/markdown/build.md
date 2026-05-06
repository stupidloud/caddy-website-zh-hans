---
title: "소스에서 빌드"
---

# 소스에서 빌드

사용자 정의 빌드가 필요한 경우(예: 플러그인 포함) Caddy를 빌드하는 여러 옵션이 있습니다:
- [Git](#git): Git 리포지토리에서 빌드
- [`xcaddy`](#xcaddy): `xcaddy`를 사용하여 빌드
- [Docker](#docker): 사용자 정의 Docker 이미지 빌드

요구 사항:

- [Go](https://golang.org/doc/install) 1.20 이상

[데비안/우분투/라즈비안을 위한 사용자 정의 빌드의 패키지 지원 파일](#package-support-files-for-custom-builds-for-debianubunturaspbian) 섹션에는 데비안 파생 시스템에서 APT 명령을 사용하여 Caddy를 설치했지만 작업에 사용자 정의 빌드 실행 파일이 필요한 사용자를 위한 지침이 포함되어 있습니다.



## <a id="git"></a>Git

요구 사항:

- Go 설치됨(위 참조)

리포지토리 복제:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

git이 없는 경우 [GitHub에서](https://github.com/caddyserver/caddy) 소스 코드를 파일 아카이브로 다운로드할 수 있습니다. 각 [릴리스(release)](https://github.com/caddyserver/caddy/releases)에는 소스 스냅샷도 있습니다.

빌드:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

[Go의 버그](https://github.com/golang/go/issues/29228)로 인해 이 기본 단계에는 버전 정보가 포함되지 않습니다. 버전(`caddy version`)을 원하면 Caddy를 메인 모듈이 아닌 종속성으로 컴파일해야 합니다. 이에 대한 지침은 Caddy의 [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) 파일에 있습니다. 또는 이를 자동화하는 [`xcaddy`](#xcaddy)를 사용할 수 있습니다.

</aside>

Go 프로그램은 다른 플랫폼용으로 컴파일하기 쉽습니다. 다른 부분인 `GOOS`, `GOARCH` 및/또는 `GOARM` 환경 변수만 설정하면 됩니다. ([자세한 내용은 Go 설명서를 참조하세요.](https://golang.org/doc/install/source#environment))

예를 들어, Windows가 아닌 환경에서 Windows용 Caddy를 컴파일하려면:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

또는 Linux가 아니거나 ARMv6가 아닌 환경에서 Linux ARMv6용으로 컴파일하는 것도 비슷합니다:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## <a id="xcaddy"></a>xcaddy

[`xcaddy` 명령](https://github.com/caddyserver/xcaddy)은 버전 정보 및/또는 플러그인과 함께 Caddy를 빌드하는 가장 쉬운 방법입니다.

요구 사항:

- Go 설치됨(위 참조)
- [`xcaddy`](https://github.com/caddyserver/xcaddy/releases)가 `PATH`에 있는지 확인하세요.

Caddy 소스 코드를 다운로드할 필요가 **없습니다**(알아서 처리해 줍니다).

그러면 다음과 같이 간단하게 (버전 정보와 함께) Caddy를 빌드할 수 있습니다:

<pre><code class="cmd bash">xcaddy build</code></pre>

플러그인과 함께 빌드하려면 `--with`를 사용하세요:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

보시다시피 `@` 구문으로 플러그인의 버전을 사용자 정의할 수 있습니다. 버전은 태그 이름, 커밋 SHA 또는 브랜치일 수 있습니다.

`xcaddy`를 사용한 교차 플랫폼 컴파일은 `go` 명령과 동일하게 작동합니다. 예를 들어 macOS용으로 교차 컴파일하려면:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## <a id="docker"></a>Docker

사용자 정의 모듈로 새 Caddy 바이너리를 빌드하기 위한 지름길로 `:builder` 이미지를 사용할 수 있습니다:

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

시작하려면 `<version>`을 Caddy의 최신 버전으로 교체해야 합니다.

두 번째 `FROM` 명령어에 유의하세요. 이것은 일반 `caddy` 이미지 위에 새로 빌드된 바이너리를 단순히 덮어씌움으로써 훨씬 더 작은 이미지를 생성합니다.

빌더는 [위에 설명된](#xcaddy) 프로세스와 유사하게 제공된 모듈로 Caddy를 빌드하기 위해 `xcaddy`를 사용합니다. `--mount=type=cache,target=/go/pkg/mod` 및 `--mount=type=cache,target=/root/.cache/go-build` 옵션은 각각 Go 모듈 종속성과 빌드 아티팩트를 캐시하는 데 사용되며, 후속 빌드 속도를 높입니다. 이 플래그는 `xcaddy`가 아닌 [Docker의 기능](https://docs.docker.com/build/cache/optimize/#use-cache-mounts)입니다.

Docker Compose를 사용하려면 권장하는 [`compose.yml`](/docs/running#docker-compose) 및 사용 지침을 참조하세요.



## <a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>데비안/우분투/라즈비안을 위한 사용자 정의 빌드의 패키지 지원 파일

이 절차는 `caddy` 패키지의 지원 파일을 유지하면서 사용자 정의 `caddy` 바이너리 실행을 단순화하는 것을 목표로 합니다.

이 절차를 통해 사용자는 공식 패키지의 기본 구성, systemd 서비스 파일 및 bash 자동 완성(bash-completion)을 활용할 수 있습니다.

요구 사항:
- [다음 지침](/docs/install#debian-ubuntu-raspbian)에 따라 `caddy` 패키지를 설치합니다.
- 사용자 정의 `caddy` 바이너리를 빌드하거나(위 섹션 참조) 사용자 정의 빌드를 [다운로드](/download)합니다.
- 사용자 정의 `caddy` 바이너리는 현재 디렉터리에 위치해야 합니다.

절차:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

설명:

- `dpkg-divert`는 `/usr/bin/caddy` 바이너리를 `/usr/bin/caddy.default`로 이동시키고, 어떤 패키지가 이 위치에 파일을 설치하려고 할 경우를 대비해 우회(diversion) 설정을 합니다.

- `update-alternatives`는 원하는 caddy 바이너리에서 `/usr/bin/caddy`로 심볼릭 링크(symlink)를 생성합니다.

- `systemctl restart caddy`는 기본 버전의 Caddy 서버를 종료하고 사용자 정의 버전을 시작합니다.

아래 명령을 실행하고 화면의 정보를 따라 사용자 정의 `caddy` 바이너리와 기본 `caddy` 바이너리 사이를 변경할 수 있습니다. 그런 다음 Caddy 서비스를 다시 시작합니다.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

이 시점 이후에 Caddy를 업그레이드하려면 [`caddy upgrade`](/docs/command-line#caddy-upgrade)를 실행할 수 있습니다. 이것은 현재 빌드와 동일한 플러그인을 가진 최신 버전의 Caddy 빌드를 [다운로드](/download)하려고 시도한 다음, 현재 바이너리를 새 것으로 교체합니다.