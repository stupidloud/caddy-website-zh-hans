---
title: Caddy 실행 유지하기
---

# Caddy 실행 유지하기

Caddy는 [명령줄 인터페이스](/docs/command-line)를 통해 직접 실행할 수도 있지만, 시스템 재부팅 시 자동으로 시작되도록 하고 stdout/stderr 로그를 캡처하는 등 계속 실행되도록 유지하기 위해 서비스 관리자를 사용하는 데는 여러 가지 장점이 있습니다.

- [Linux 서비스](#linux-service)
  - [유닛 파일 (Unit Files)](#unit-files)
  - [수동 설치](#manual-installation)
  - [서비스 사용하기](#using-the-service)
  - [systemd를 이용한 로컬 HTTPS](#local-https-with-systemd)
  - [재정의 (Overrides)](#overrides)
	- [환경 변수](#environment-variables)
	- [`run` 및 `reload` 재정의](#run-and-reload-override)
	- [크래시 시 다시 시작](#restart-on-crash)
  - [SELinux 고려 사항](#selinux-considerations)
- [Windows 서비스](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [설정](#setup)
  - [사용법](#usage)
  - [Docker를 이용한 로컬 HTTPS](#local-https-with-docker)

## Linux 서비스 <a id="linux-service"></a>

systemd를 사용하는 Linux 배포판에서 Caddy를 실행하는 권장 방법은 공식 systemd 유닛 파일을 사용하는 것입니다.

### 유닛 파일 (Unit Files)

사용 사례에 따라 선택할 수 있는 두 가지 다른 systemd 유닛 파일을 제공합니다:

- [Caddyfile](/docs/caddyfile)로 Caddy를 설정하는 경우 [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service). 다른 설정 어댑터나 JSON 설정 파일을 사용하려는 경우, `ExecStart` 및 `ExecReload` 명령을 [재정의](#overrides)할 수 있습니다.

- [API](/docs/api)를 통해서만 Caddy를 설정하는 경우 [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service). 이 서비스는 기본적으로 [영구 저장되는](/docs/json/admin/config/) `autosave.json`을 사용하여 Caddy를 시작하는 [`--resume`](/docs/command-line#caddy-run) 옵션을 사용합니다.

두 파일은 매우 유사하지만, 작업 흐름을 수용하기 위해 `ExecStart` 및 `ExecReload` 명령이 다릅니다.

서비스를 전환해야 하는 경우, 다른 서비스를 활성화하고 시작하기 전에 이전 서비스를 비활성화하고 중지해야 합니다. 예를 들어, `caddy` 서비스에서 `caddy-api` 서비스로 전환하려면:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>

### 수동 설치 <a id="manual-installation"></a>

일부 [설치 방법](/docs/install)은 자동으로 Caddy를 서비스로 실행하도록 설정합니다. 그렇지 않은 방법을 선택한 경우, 다음 지침에 따라 설정할 수 있습니다:

**요구 사항:**

- [다운로드](/download)했거나 [소스에서 빌드한](/docs/build) `caddy` 바이너리
- `systemctl --version` 232 이상
- `sudo` 권한

caddy 바이너리를 `$PATH`로 이동합니다. 예를 들면:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

작동하는지 테스트합니다:
<pre><code class="cmd bash">caddy version</code></pre>

`caddy`라는 이름의 그룹을 생성합니다:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

쓰기 가능한 홈 디렉터리가 있는 `caddy`라는 이름의 사용자를 생성합니다:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

설정 파일을 사용하는 경우, 방금 만든 `caddy` 사용자가 읽을 수 있는지 확인하세요.

다음으로, 사용 사례에 따라 [systemd 유닛 파일을 선택합니다](#unit-files).

**`ExecStart` 및 `ExecReload` 지시문을 다시 확인하세요.** 설치에 맞게 바이너리의 위치와 명령줄 인수가 올바른지 확인하세요! 예를 들어 설정 파일을 사용하는 경우, 기본값과 다르다면 `--config` 경로를 변경하세요.

서비스 파일이 저장되는 일반적인 위치는 `/etc/systemd/system/caddy.service`입니다.

서비스 파일을 저장한 후, 일반적인 systemctl 명령으로 서비스를 처음 시작할 수 있습니다:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

실행 중인지 확인합니다:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

이제 [서비스를 사용할](#using-the-service) 준비가 되었습니다!

### 서비스 사용하기 <a id="using-the-service"></a>

Caddyfile을 사용하는 경우, `nano`, `vi` 또는 선호하는 편집기로 설정을 편집할 수 있습니다:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

정적 사이트 파일은 `/var/www/html` 또는 `/srv`에 배치할 수 있습니다. `caddy` 사용자가 파일을 읽을 수 있는 권한이 있는지 확인하세요.

서비스가 실행 중인지 확인하려면:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
상태 명령은 현재 실행 중인 서비스 파일의 위치도 표시합니다.

공식 서비스 파일로 실행할 때 Caddy의 출력은 `journalctl`로 리디렉션됩니다. 전체 로그를 읽고 줄이 잘리는 것을 방지하려면:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

설정 파일을 사용하는 경우, 변경 후 Caddy를 안전하게(gracefully) 다시 로드할 수 있습니다:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

다음 명령으로 서비스를 중지할 수 있습니다:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Caddy의 설정을 변경하기 위해 서비스를 중지하지 마세요. 서버를 중지하면 다운타임이 발생합니다. 대신 reload 명령을 사용하세요.

</aside>

Caddy 프로세스는 `$HOME`이 `/var/lib/caddy`로 설정된 `caddy` 사용자로 실행됩니다. 이는 다음을 의미합니다:
- 기본 [데이터 저장 위치](/docs/conventions#data-directory)(인증서 및 기타 상태 정보용)는 `/var/lib/caddy/.local/share/caddy`가 됩니다.
- 기본 [설정 저장 위치](/docs/conventions#configuration-directory)(자동 저장되는 JSON 설정용, 주로 `caddy-api` 서비스에 유용함)는 `/var/lib/caddy/.config/caddy`가 됩니다.

### systemd를 이용한 로컬 HTTPS <a id="local-https-with-systemd"></a>

HTTPS를 사용하여 로컬 개발을 위해 Caddy를 사용할 때, `localhost` 또는 `app.localhost`와 같은 [호스트 이름](/docs/caddyfile/concepts#addresses)을 사용할 수 있습니다. 이를 통해 Caddy의 로컬 CA를 사용하여 인증서를 발급하는 [로컬 HTTPS](/docs/automatic-https#local-https)가 활성화됩니다.

서비스로 실행할 때 Caddy는 `caddy` 사용자로 실행되므로, 루트 CA 인증서를 시스템 신뢰 저장소(trust store)에 설치할 권한이 없습니다. 이를 수행하려면 [`sudo caddy trust`](/docs/command-line#caddy-trust)를 실행하여 설치를 진행하세요.

[`internal` 발급자](/docs/caddyfile/directives/tls#internal)를 사용할 때 다른 기기가 서버에 연결하도록 하려면, 해당 기기에도 루트 CA 인증서를 설치해야 합니다. 루트 CA 인증서는 `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`에서 찾을 수 있습니다. 요즘 많은 웹 브라우저는 (시스템의 신뢰 저장소를 무시하고) 자체 신뢰 저장소를 사용하므로, 그곳에도 인증서를 수동으로 설치해야 할 수 있습니다.

### 재정의 (Overrides)

서비스 파일의 측면을 재정의하는 가장 좋은 방법은 다음 명령을 사용하는 것입니다:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

이 명령은 기본 터미널 텍스트 편집기로 빈 파일을 열며, 여기에서 유닛 정의에 지시문을 재정의하거나 추가할 수 있습니다. 이를 "드롭인(drop-in)" 파일이라고 합니다.

#### 환경 변수 <a id="environment-variables"></a>

설정에서 사용할 환경 변수를 정의해야 하는 경우 다음과 같이 할 수 있습니다:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

마찬가지로, 환경 변수를 유지 관리하기 위해 별도의 파일(envfile)을 유지 관리하는 것을 선호하는 경우, 다음과 같이 [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) 지시문을 사용할 수 있습니다:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

그런 다음 `/etc/caddy/.env` 파일은 다음과 같이 보일 수 있습니다 (값 주위에 `"` 따옴표를 사용하지 마세요):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

#### `run` 및 `reload` 재정의 <a id="run-and-reload-override"></a>

설정 파일을 기본값인 Caddyfile에서 JSON 파일로 변경해야 하는 경우 (새 값을 설정하기 전에 `Exec*` 지시문은 [빈 문자열로 재설정되어야 함](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=)에 유의하세요):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

#### 크래시 시 다시 시작 <a id="restart-on-crash"></a>

예기치 않게 크래시가 발생할 경우 caddy가 5초 후에 스스로 다시 시작하도록 하려면:
```systemd
[Service]
# Automatically restart caddy if it crashes except if the exit code was 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

그런 다음 파일을 저장하고 텍스트 편집기를 종료한 후, 서비스가 적용되도록 다시 시작합니다:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>

### SELinux 고려 사항 <a id="selinux-considerations"></a>

SELinux가 활성화된 시스템에서는 두 가지 옵션이 있습니다:
1. [COPR 저장소](/docs/install#fedora-redhat-centos)를 사용하여 Caddy를 설치합니다. systemd 파일과 caddy 바이너리가 이미 생성되고 올바르게 레이블이 지정됩니다 (따라서 이 섹션을 무시해도 됩니다). 사용자 지정 빌드의 Caddy를 사용하려는 경우, 아래 설명된 대로 실행 파일에 레이블을 지정해야 합니다.

2. [이 사이트에서 Caddy를 다운로드](/download)하거나 [`xcaddy`](https://github.com/caddyserver/xcaddy)를 사용하여 컴파일합니다. 어느 경우든 직접 파일에 레이블을 지정해야 합니다.

systemd 유닛 파일과 해당 실행 파일은 각각 `systemd_unit_file_t` 및 `bin_t` 레이블이 지정되지 않으면 실행되지 않습니다.

`systemd_unit_file_t` 레이블은 `/etc/systemd/...`에 생성된 파일에 자동으로 적용되므로, [수동 설치](#manual-installation) 지침에 따라 그곳에 `caddy.service` 파일을 생성하세요.

`caddy` 바이너리에 태그를 지정하려면 다음 명령을 사용할 수 있습니다:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

## Windows 서비스 <a id="windows-service"></a>

Windows에서 Caddy를 서비스로 실행하는 방법에는 두 가지가 있습니다: [sc.exe](#scexe) 또는 [WinSW](#winsw).

### sc.exe

서비스를 생성하려면 다음을 실행합니다:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

(`YOURPATH`를 `caddy.exe`의 실제 경로로 바꾸세요)

시작하려면:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

중지하려면:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>

### WinSW

다음 지침을 사용하여 Windows에 Caddy를 서비스로 설치합니다.

**요구 사항:**

- [다운로드](/download)했거나 [소스에서 빌드한](/docs/build) `caddy.exe` 바이너리
- [WinSW](https://github.com/winsw/winsw/releases/latest) 서비스 래퍼의 최신 릴리스에서 가져온 모든 `.exe` (아래 서비스 설정은 v2.x 릴리스용으로 작성됨)

모든 파일을 서비스 디렉터리에 넣습니다. 다음 예제에서는 `C:\caddy`를 사용합니다.

`WinSW-x64.exe` 파일의 이름을 `caddy-service.exe`로 바꿉니다.

동일한 디렉터리에 `caddy-service.xml`을 추가합니다:

```xml
<service>
  <id>caddy</id>
  <!-- Display name of the service -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Service description -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

이제 다음을 사용하여 서비스를 설치할 수 있습니다:
<pre><code class="cmd bash">caddy-service install</code></pre>

Windows 서비스 콘솔을 시작하여 서비스가 제대로 실행되고 있는지 확인하고 싶을 수 있습니다:
<pre><code class="cmd bash">services.msc</code></pre>

Windows 서비스는 다시 로드할 수 없으므로 caddy에 직접 다시 로드하도록 지시해야 합니다:
<pre><code class="cmd bash">caddy reload</code></pre>

다시 시작하는 것은 일반적인 Windows 서비스 명령을 통해 가능합니다. 예를 들어 작업 관리자의 "서비스" 탭을 통해 할 수 있습니다.

서비스 래퍼를 사용자 지정하는 방법에 대해서는 [WinSW 문서](https://github.com/winsw/winsw/tree/master#usage)를 참조하세요.

## Docker Compose

Docker를 시작하고 실행하는 가장 간단한 방법은 Docker Compose를 사용하는 것입니다. 공식 Caddy Docker 이미지에 대한 추가 세부 정보는 [Docker Hub](https://hub.docker.com/_/caddy)의 문서를 참조하세요.

<aside class="tip">

이는 명령이 이제 V1의 `docker-compose`(하이픈) 대신 `docker compose`(공백)인 [Docker Compose V2](https://docs.docker.com/compose/reference/)를 사용하고 있다고 가정합니다.

</aside>

### 설정 <a id="setup"></a>

먼저 `compose.yml` 파일을 생성합니다(또는 이 서비스를 기존 파일에 추가합니다):

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

이미지 `<version>`을 최신 버전 번호로 채워 넣어야 합니다. 이 번호는 [Docker Hub](https://hub.docker.com/_/caddy)의 "Tags" 섹션 아래에 나열되어 있습니다.

이 설정의 역할:

- 머신이 재부팅될 때 Caddy 컨테이너가 자동으로 다시 시작되도록 `unless-stopped` 재시작 정책을 사용합니다.
- HTTP 및 HTTPS를 위해 각각 `80` 포트 및 `443` 포트에 바인딩하고, 추가로 HTTP/3를 위해 `443/udp`에 바인딩합니다.
- Caddyfile 설정이 포함된 `conf` 디렉터리를 바인드 마운트합니다.
- `/srv`에서 사이트의 정적 파일을 제공하기 위해 `site` 디렉터리를 바인드 마운트합니다.
- [중요한 정보를 보존](/docs/conventions#file-locations)하기 위해 `/data` 및 `/config`에 명명된 볼륨을 사용합니다.

그런 다음 `conf` 디렉터리의 유일한 파일로 `Caddyfile`이라는 이름의 파일을 만들고 [Caddyfile](/docs/caddyfile/concepts) 설정을 작성합니다.

제공할 정적 파일이 있는 경우 설정 파일 옆의 `site/` 디렉터리에 파일을 배치한 다음, `root /srv`를 사용하여 [`root`](/docs/caddyfile/directives/root)를 설정할 수 있습니다. 그렇지 않은 경우 `/srv` 볼륨 마운트를 제거할 수 있습니다.

<aside class="tip">

Caddy를 사용하여 다른 컨테이너로 [리버스 프록시(reverse proxy)](/docs/caddyfile/directives/reverse_proxy)를 수행하는 경우, Docker 네트워킹에서 `localhost`는 "이 머신"이 아니라 "이 컨테이너"를 의미한다는 점을 기억하세요. 따라서 예를 들어 `reverse_proxy localhost:8080`을 사용하지 말고, 대신 `reverse_proxy other-container:8080`을 사용하세요.

</aside>

플러그인이 포함된 사용자 지정 Caddy 빌드가 필요한 경우, [Docker 빌드 지침](/docs/build#docker)에 따라 사용자 지정 Docker 이미지를 생성하세요. `compose.yml` 옆에 `Dockerfile`을 생성한 다음, `compose.yml`의 `image:` 줄을 대신 `build: .`으로 바꾸세요.

### 사용법 <a id="usage"></a>

그런 다음 컨테이너를 시작할 수 있습니다:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Caddyfile을 변경한 후 Caddy를 다시 로드하려면:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

v2.11.0부터 Caddy가 `caddy run`과 설정 파일로 시작된 경우 `SIGUSR1`을 사용하여 다시 로드할 수 있습니다:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Caddy의 가장 최근 1000개 로그를 보고 새 로그가 스트리밍되는 것을 팔로우(follow)하려면:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

### Docker를 이용한 로컬 HTTPS <a id="local-https-with-docker"></a>

HTTPS를 사용하여 로컬 개발을 위해 Docker를 사용할 때, `localhost` 또는 `app.localhost`와 같은 [호스트 이름](/docs/caddyfile/concepts#addresses)을 사용할 수 있습니다. 이를 통해 Caddy의 로컬 CA를 사용하여 인증서를 발급하는 [로컬 HTTPS](/docs/automatic-https#local-https)가 활성화됩니다. 즉, 컨테이너 외부의 HTTP 클라이언트는 Caddy가 제공하는 TLS 인증서를 신뢰하지 않습니다. 이를 해결하려면 호스트 머신의 신뢰 저장소에 Caddy의 루트 CA 인증서를 설치할 수 있습니다:

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

요즘 많은 웹 브라우저는 (시스템의 신뢰 저장소를 무시하고) 자체 신뢰 저장소를 사용하므로, 위의 명령에서 컨테이너로부터 복사한 `root.crt` 파일을 사용하여 그곳에도 인증서를 수동으로 설치해야 할 수 있습니다.

- Firefox의 경우 환경설정 > 개인 정보 및 보안 > 인증서 > 인증서 보기 > 인증 기관 > 가져오기로 이동하여 `root.crt` 파일을 선택합니다.

- Chrome의 경우 설정 > 개인 정보 보호 및 보안 > 보안 > 인증서 관리 > 인증 기관 > 가져오기로 이동하여 `root.crt` 파일을 선택합니다.