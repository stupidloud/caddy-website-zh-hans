---
title: "安裝"
---

<a id="install"></a>
# 安裝

本頁面介紹了在您的系統上安裝 Caddy 的各種方法。

**官方：**

- [靜態二進位檔案](#static-binaries)
- [Debian, Ubuntu, Raspbian 套件](#debian-ubuntu-raspbian)
- [Fedora, RedHat, CentOS 套件](#fedora-redhat-centos)
- [Arch Linux, Manjaro, Parabola 套件](#arch-linux-manjaro-parabola)
- [Docker 映像檔](#docker)
- [Railway 範本](#railway)

<aside class="tip">

我們的 [官方套件](https://github.com/caddyserver/dist) 僅包含標準模組。如果您需要第三方插件，請 [使用 `xcaddy` 從源代碼構建](/docs/build#xcaddy)、使用 [我們的下載頁面](/download) 或 [在 Railway 上部署](#railway)。

</aside>


**社群維護：**

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
## 靜態二進位檔案

**如果是安裝到生產系統，如果下方有適用於您發行版的官方套件，我們建議使用官方套件。**

1. 獲取 Caddy 二進位檔案：
	- [從 GitHub 上的版本發布中獲取](https://github.com/caddyserver/caddy/releases)（展開「Assets」）
		- 參考 [驗證資產簽名](/docs/signature-verification) 了解如何驗證資產簽名
	- [從我們的下載頁面獲取](/download)
	- [從源代碼構建](/docs/build)（使用 `go` 或 `xcaddy`）
2. [將 Caddy 安裝為系統服務。](/docs/running#manual-installation) 強烈建議執行此操作，特別是對於生產伺服器。

將二進位檔案放置在您的 `$PATH`（或 Windows 上的 `%PATH%`）目錄之一，這樣您就可以直接運行 `caddy` 而無需輸入可執行文件的完整路徑。（運行 `echo $PATH` 查看符合條件的目錄列表。）

您可以通過將靜態二進位檔案替換為新版本並重啟 Caddy 來進行升級。[`caddy upgrade` 命令](/docs/command-line#caddy-upgrade) 可以簡化此過程。



<a id="debian-ubuntu-raspbian"></a>
## Debian, Ubuntu, Raspbian

安裝此套件會自動啟動並將 Caddy 作為名為 `caddy` 的 [systemd 服務](/docs/running#linux-service) 運行。它還附帶一個可選的 `caddy-api` 服務，該服務預設 *not* 啟用，但如果您主要通過 API 而不是配置檔案來配置 Caddy，則應使用該服務。

安裝後，請閱讀 [服務使用說明](/docs/running#using-the-service)。

**穩定版本：**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**測試版本** （包含測試版和發行候選版）：

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**查看 Cloudsmith 倉庫**](https://cloudsmith.io/~caddy/repos/)

如果您希望在自定義 Caddy 構建中使用隨附的支援檔案（systemd 服務、bash 完成和預設配置），可以 [在此處找到說明](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian)。


<a id="fedora-redhat-centos"></a>
## Fedora, RedHat, CentOS

此套件附帶了 Caddy 的兩個 [systemd 服務](/docs/running#linux-service) 單元檔案，但預設不啟用它們。建議使用該服務。如果您這樣做，請閱讀 [服務使用說明](/docs/running#using-the-service)。

Fedora：

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL：

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**查看 Caddy COPR**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


<a id="arch-linux-manjaro-parabola"></a>
## Arch Linux, Manjaro, Parabola

此套件附帶了經過大幅修改的 Caddy 兩個 [systemd 服務](/docs/running#linux-service) 單元檔案，但預設不啟用它們。
這些修改包括自定義的啟動/停止行為和額外的沙箱標記，這些標記在 [systemd 的執行文件](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing) 中有詳細說明，這可能導致某些主機目錄對 Caddy 程式不可用。

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**在 Arch Linux 倉庫中查看 Caddy**](https://archlinux.org/packages/extra/x86_64/caddy/) 以及 [**Arch Linux Wiki**](https://wiki.archlinux.org/title/Caddy)

<a id="docker"></a>
## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**在 Docker Hub 上查看**](https://hub.docker.com/_/caddy)

請參閱我們 [推薦的 Docker Compose 配置](/docs/running#docker-compose) 和使用說明。


<a id="railway"></a>
## Railway

通過來自 [Railway](https://railway.com) 的贊助，我們官方支援此範本：

[![在 Railway 上部署](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


<a id="gentoo"></a>
## Gentoo

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**查看 Gentoo 套件**](https://packages.gentoo.org/packages/www-servers/caddy)



<a id="homebrew-mac"></a>
## Homebrew (Mac)

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd bash">brew install caddy</code></pre>

[**查看 Homebrew formula**](https://formulae.brew.sh/formula/caddy)



<a id="chocolatey-windows"></a>
## Chocolatey (Windows)

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd">choco install caddy</code></pre>

[**查看 Chocolatey 套件**](https://chocolatey.org/packages/caddy)



<a id="scoop-windows"></a>
## Scoop (Windows)

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd">scoop install caddy</code></pre>

[**查看 Scoop manifest**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



<a id="webi"></a>
## Webi

*注意：這是一個社群維護的安裝方法。*

Linux 和 macOS：

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows：

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

您可能需要調整 Windows 防火牆規則以允許非本地主機的傳入連線。

[**在 Webi 上查看**](https://webinstall.dev/caddy)



<a id="ansible"></a>
## Ansible

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**查看 Ansible role 倉庫**](https://github.com/nvjacobo/caddy)



<a id="termux"></a>
## Termux

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd">pkg install caddy</code></pre>

[**查看 Termux build.sh 檔案**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



<a id="nixnixpkgsnixos"></a>
## Nix/Nixpkgs/NixOS

*注意：這是一個社群維護的安裝方法。*

- 套件名稱：[`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- NixOS 模組：[`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**在 Nixpkgs 搜尋中查看 Caddy**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) 以及 [**NixOS 選項搜尋**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



<a id="unikraft"></a>
## Unikraft

*注意：這是一個社群維護的安裝方法。*

首先安裝 Unikraft 的配套工具 [`kraft`](https://unikraft.org/docs/cli)：

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

然後使用以下命令運行帶有 Unikraft 的 Caddy：

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

要允許非本地主機傳入連線，您需要 [將 unikernel 實例連接到網絡](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network)。

[**查看 Unikraft 應用程式目錄**](https://github.com/unikraft/catalog/tree/main/examples/caddy) 以及 [**KraftCloud 平台範例（由 Unikraft 提供支援）**](https://github.com/kraftcloud/examples/tree/main/caddy)。



<a id="opnsense"></a>
## OPNsense

*注意：這是一個社群維護的安裝方法。*

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**查看 FreeBSD caddy-custom makefile**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) 以及 [**os-caddy 插件源代碼**](https://github.com/opnsense/plugins/tree/master/www/caddy)

<a id="mise"></a>
## Mise

*注意：這是一個社群維護的安裝方法。*

如果您正在使用 [mise](https://github.com/jdx/mise)（多語言工具版本管理器），可以使用類似以下的命令來安裝最新版本：

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
