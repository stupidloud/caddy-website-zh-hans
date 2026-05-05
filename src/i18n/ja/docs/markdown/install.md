---
title: "インストール"
---

<a id="install"></a>
# インストール

このページでは、システムに Caddy をインストールするさまざまな方法を説明します。

**公式:**

- [静的バイナリ](#static-binaries)
- [Debian、Ubuntu、Raspbian パッケージ](#debian-ubuntu-raspbian)
- [Fedora、RedHat、CentOS パッケージ](#fedora-redhat-centos)
- [Arch Linux、Manjaro、Parabola パッケージ](#arch-linux-manjaro-parabola)
- [Docker イメージ](#docker)
- [Railway テンプレート](#railway)

<aside class="tip">

[公式パッケージ](https://github.com/caddyserver/dist)には標準モジュールのみが含まれます。サードパーティ製プラグインが必要な場合は、[`xcaddy` でソースからビルド](/docs/build#xcaddy)するか、[ダウンロードページ](/download)を使うか、[Railway にデプロイ](#railway)してください。

</aside>


**コミュニティ管理:**

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
## 静的バイナリ

**本番システムにインストールする場合は、下記に利用可能なディストリビューション向け公式パッケージがあれば、それを使うことをおすすめします。**

1. Caddy バイナリを入手します:
	- [GitHub のリリース](https://github.com/caddyserver/caddy/releases)から入手する ("Assets" を展開)
		- アセット署名の検証方法は、[アセット署名の検証](/docs/signature-verification)を参照してください
	- [ダウンロードページ](/download)から入手する
	- [ソースからビルド](/docs/build)する (`go` または `xcaddy` を使用)
2. [Caddy をシステムサービスとしてインストールします。](/docs/running#manual-installation) 特に本番サーバーでは強く推奨します。

実行ファイルのフルパスを入力せずに `caddy` を実行できるよう、バイナリを `$PATH` (Windows では `%PATH%`) のいずれかのディレクトリに置いてください。(対象になるディレクトリ一覧を見るには `echo $PATH` を実行します。)

静的バイナリは、新しいバージョンに置き換えて Caddy を再起動することでアップグレードできます。[`caddy upgrade` コマンド](/docs/command-line#caddy-upgrade)を使うと、この作業を簡単にできます。



<a id="debian-ubuntu-raspbian"></a>
## Debian、Ubuntu、Raspbian

このパッケージをインストールすると、`caddy` という名前の [systemd service](/docs/running#linux-service) として Caddy が自動的に起動し、実行されます。また、任意で使える `caddy-api` service も同梱されています。これはデフォルトでは有効化されませんが、設定ファイルではなく API で Caddy を主に設定する場合に使うべきものです。

インストール後は、[サービスの使用手順](/docs/running#using-the-service)を読んでください。

**安定版リリース:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**テスト版リリース** (ベータ版とリリース候補を含む):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Cloudsmith リポジトリを見る**](https://cloudsmith.io/~caddy/repos/)

カスタム Caddy ビルドで、パッケージに含まれるサポートファイル (systemd services、bash 補完、デフォルト設定) を使いたい場合は、[こちら](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian)に手順があります。


<a id="fedora-redhat-centos"></a>
## Fedora、RedHat、CentOS

このパッケージには Caddy の [systemd service](/docs/running#linux-service) unit ファイルが両方含まれていますが、デフォルトでは有効化されません。サービスを使うことをおすすめします。使う場合は、[サービスの使用手順](/docs/running#using-the-service)を読んでください。

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Caddy COPR を見る**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


<a id="arch-linux-manjaro-parabola"></a>
## Arch Linux、Manjaro、Parabola

このパッケージには、Caddy の [systemd service](/docs/running#linux-service) unit ファイル両方の大きく変更された版が含まれていますが、デフォルトでは有効化されません。
これらの変更には、カスタムの start/stop 動作と追加のサンドボックス化フラグが含まれます。詳細は [systemd の exec ドキュメント](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing)で説明されており、その結果として一部のホストディレクトリを Caddy プロセスから利用できない場合があります。

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Arch Linux リポジトリ内の Caddy を見る**](https://archlinux.org/packages/extra/x86_64/caddy/)および[**Arch Linux Wiki**](https://wiki.archlinux.org/title/Caddy)

## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Docker Hub で見る**](https://hub.docker.com/_/caddy)

[推奨 Docker Compose 設定](/docs/running#docker-compose)と使用手順を参照してください。


## Railway

[Railway](https://railway.com) からのスポンサーシップにより、次のテンプレートを公式にサポートしています:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


## Gentoo

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Gentoo パッケージを見る**](https://packages.gentoo.org/packages/www-servers/caddy)



## Homebrew (Mac)

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Homebrew formula を見る**](https://formulae.brew.sh/formula/caddy)



## Chocolatey (Windows)

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd">choco install caddy</code></pre>

[**Chocolatey パッケージを見る**](https://chocolatey.org/packages/caddy)



## Scoop (Windows)

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd">scoop install caddy</code></pre>

[**Scoop manifest を見る**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



## Webi

*注: これはコミュニティ管理のインストール方法です。*

Linux と macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

localhost 以外からの受信接続を許可するには、Windows ファイアウォール規則の調整が必要になる場合があります。

[**Webi で見る**](https://webinstall.dev/caddy)



## Ansible

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Ansible role リポジトリを見る**](https://github.com/nvjacobo/caddy)



## Termux

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd">pkg install caddy</code></pre>

[**Termux build.sh ファイルを見る**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



## Nix/Nixpkgs/NixOS

*注: これはコミュニティ管理のインストール方法です。*

- パッケージ名: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- NixOS module: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Nixpkgs 検索で Caddy を見る**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)および[**NixOS options 検索**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



## Unikraft

*注: これはコミュニティ管理のインストール方法です。*

まず、Unikraft の補助ツール [`kraft`](https://unikraft.org/docs/cli) をインストールします:

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

次に、Unikraft で Caddy を次のように実行します:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

localhost 以外からの受信接続を許可するには、[unikernel instance をネットワークに接続](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network)する必要があります。

[**Unikraft application catalog を見る**](https://github.com/unikraft/catalog/tree/main/examples/caddy)および[**KraftCloud platform examples (powered by Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy)。



## OPNsense

*注: これはコミュニティ管理のインストール方法です。*

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**FreeBSD caddy-custom makefile を見る**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile)および[**os-caddy plugin source**](https://github.com/opnsense/plugins/tree/master/www/caddy)

## Mise

*注: これはコミュニティ管理のインストール方法です。*

多言語対応のツールバージョンマネージャー [mise](https://github.com/jdx/mise) を使っている場合は、次のようなコマンドで最新バージョンをインストールできます:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
