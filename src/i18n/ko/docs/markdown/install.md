---
title: "설치"
---

# 설치

이 페이지에서는 시스템에 Caddy를 설치하는 다양한 방법을 설명합니다.

**공식:**

- [정적 바이너리(Static binaries)](#static-binaries)
- [Debian, Ubuntu, Raspbian 패키지](#debian-ubuntu-raspbian)
- [Fedora, RedHat, CentOS 패키지](#fedora-redhat-centos)
- [Arch Linux, Manjaro, Parabola 패키지](#arch-linux-manjaro-parabola)
- [Docker 이미지](#docker)
- [Railway 템플릿](#railway)

<aside class="tip">

우리의 [공식 패키지](https://github.com/caddyserver/dist)에는 표준 모듈만 제공됩니다. 타사 플러그인이 필요한 경우, [`xcaddy`를 사용하여 소스에서 빌드](/docs/build#xcaddy)하거나, [다운로드 페이지](/download)를 사용하거나, [Railway에 배포](#railway)하세요.

</aside>


**커뮤니티 유지 관리:**

- [Gentoo](#gentoo)
- [Homebrew (Mac)](#homebrew-mac)
- [Chocolatey (Windows)](#chocolatey-windows)
- [Scoop (Windows)](#scoop-windows)
- [Webi](#webi)
- [Ansible](#ansible)
- [Termux](#termux)
- [Nix/Nixpkgs/NixOS](#nixnixpkgsnixos)
- [Unikraft](#unikraft)
- [OPNsense](#opnsense)
- [Mise](#mise)


<a id="static-binaries"></a>
## 정적 바이너리

**프로덕션 시스템에 설치하는 경우 아래에서 사용 가능한 배포판용 공식 패키지를 사용하는 것이 좋습니다.**

1. Caddy 바이너리 얻기:
	- [GitHub의 릴리스에서](https://github.com/caddyserver/caddy/releases) ("Assets" 확장)
		- 자산 서명을 확인하는 방법은 [자산 서명 확인](/docs/signature-verification)을 참조하세요.
	- [다운로드 페이지에서](/download)
	- [소스에서 빌드하여](/docs/build) (`go` 또는 `xcaddy` 사용)
2. [Caddy를 시스템 서비스로 설치하세요.](/docs/running#manual-installation) 이는 프로덕션 서버에 강력히 권장됩니다.

실행 파일의 전체 경로를 입력하지 않고도 `caddy`를 실행할 수 있도록 `$PATH`(또는 Windows의 경우 `%PATH%`) 디렉터리 중 하나에 바이너리를 배치합니다. (자격이 되는 디렉터리 목록을 보려면 `echo $PATH`를 실행하세요.)

정적 바이너리를 최신 버전으로 교체하고 Caddy를 다시 시작하여 업그레이드할 수 있습니다. [`caddy upgrade` 명령](/docs/command-line#caddy-upgrade)을 사용하면 이를 쉽게 수행할 수 있습니다.



## Debian, Ubuntu, Raspbian

이 패키지를 설치하면 자동으로 이름이 `caddy`인 [systemd 서비스](/docs/running#linux-service)로서 Caddy를 시작하고 실행합니다. 또한 선택적 `caddy-api` 서비스와 함께 제공되는데, 이 서비스는 기본적으로 활성화되어 있지 *않지만* 구성 파일 대신 주로 API를 통해 Caddy를 구성하는 경우 사용해야 합니다.

설치한 후 [서비스 사용 지침](/docs/running#using-the-service)을 읽어보세요.

**안정판(Stable) 릴리스:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**테스트(Testing) 릴리스** (베타 및 릴리스 후보 포함):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Cloudsmith 저장소 보기**](https://cloudsmith.io/~caddy/repos/)

패키지된 지원 파일(systemd 서비스, bash 자동 완성 및 기본 구성)을 커스텀 Caddy 빌드와 함께 사용하려면 [여기에서 지침을 확인할 수 있습니다](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


## Fedora, RedHat, CentOS

이 패키지는 Caddy의 [systemd 서비스](/docs/running#linux-service) 유닛 파일 두 가지를 모두 제공하지만, 기본적으로 활성화하지는 않습니다. 서비스를 사용하는 것이 권장됩니다. 서비스를 사용하려면 [서비스 사용 지침](/docs/running#using-the-service)을 읽어보세요.

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Caddy COPR 보기**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


## Arch Linux, Manjaro, Parabola

이 패키지는 Caddy의 [systemd 서비스](/docs/running#linux-service) 유닛 파일 두 가지 모두의 많이 수정된 버전을 제공하지만, 기본적으로 활성화하지는 않습니다.
이러한 수정 사항에는 사용자 지정 시작/중지 동작 및 [systemd의 exec 문서](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing)에 설명된 추가 샌드박싱 플래그가 포함되어 있으며, 이로 인해 특정 호스트 디렉터리를 Caddy 프로세스에서 사용하지 못할 수 있습니다. 

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Arch Linux 저장소**](https://archlinux.org/packages/extra/x86_64/caddy/) 및 [**Arch Linux Wiki에서 Caddy 보기**](https://wiki.archlinux.org/title/Caddy)

## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Docker Hub에서 보기**](https://hub.docker.com/_/caddy)

[권장하는 Docker Compose 구성](/docs/running#docker-compose) 및 사용 지침을 확인하세요.


## Railway

[Railway](https://railway.com)의 후원을 통해 이 템플릿을 공식적으로 지원합니다:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


## Gentoo

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Gentoo 패키지 보기**](https://packages.gentoo.org/packages/www-servers/caddy)



## Homebrew (Mac)

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Homebrew 공식(formula) 보기**](https://formulae.brew.sh/formula/caddy)



## Chocolatey (Windows)

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd">choco install caddy</code></pre>

[**Chocolatey 패키지 보기**](https://chocolatey.org/packages/caddy)



## Scoop (Windows)

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd">scoop install caddy</code></pre>

[**Scoop 매니페스트 보기**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



## Webi

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

Linux 및 macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

localhost가 아닌 들어오는 연결(incoming connections)을 허용하려면 Windows 방화벽 규칙을 조정해야 할 수 있습니다.

[**Webi에서 보기**](https://webinstall.dev/caddy)



## Ansible

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Ansible 역할(role) 저장소 보기**](https://github.com/nvjacobo/caddy)



## Termux

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd">pkg install caddy</code></pre>

[**Termux build.sh 파일 보기**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



## Nix/Nixpkgs/NixOS

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

- 패키지 이름: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- NixOS 모듈: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Nixpkgs 검색**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) 및 [**NixOS 옵션 검색에서 Caddy 보기**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



## Unikraft

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

먼저 Unikraft의 보조 도구인 [`kraft`](https://unikraft.org/docs/cli)를 설치합니다:

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

그런 다음 다음을 사용하여 Unikraft로 Caddy를 실행합니다:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

localhost가 아닌 들어오는 연결을 허용하려면 [유니커널(unikernel) 인스턴스를 네트워크에 연결](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network)해야 합니다.

[**Unikraft 애플리케이션 카탈로그**](https://github.com/unikraft/catalog/tree/main/examples/caddy) 및 [**KraftCloud 플랫폼 예제(Unikraft 기반)**](https://github.com/kraftcloud/examples/tree/main/caddy)를 확인하세요.



## OPNsense

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**FreeBSD caddy-custom 메이크파일**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) 및 [**os-caddy 플러그인 소스 보기**](https://github.com/opnsense/plugins/tree/master/www/caddy)

## Mise

*참고: 이 방법은 커뮤니티에서 유지 관리하는 설치 방법입니다.*

폴리글롯 도구 버전 관리자인 [mise](https://github.com/jdx/mise)를 사용하는 경우 다음과 같은 명령을 사용하여 최신 버전을 설치할 수 있습니다:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
