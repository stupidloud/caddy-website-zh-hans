---
title: "安装"
---

# 安装

本页面介绍了在您的系统上安装 Caddy 的各种方法。

**官方：**

- [静态二进制文件](#static-binaries)
- [Debian、Ubuntu、Raspbian 软件包](#debian-ubuntu-raspbian)
- [Fedora、RedHat、CentOS 软件包](#fedora-redhat-centos)
- [Arch Linux、Manjaro、Parabola 软件包](#arch-linux-manjaro-parabola)
- [Docker 镜像](#docker)
- [Railway 模板](#railway)

<aside class="tip">

我们的[官方软件包](https://github.com/caddyserver/dist)仅包含标准模块。如果您需要第三方插件，可以使用 [`xcaddy`](/docs/build#xcaddy) 从源代码编译，访问 [我们的下载页面](/download)，或在 [Railway 上部署](#railway)。

</aside>


**由社区维护：**

- [Gentoo](#gentoo)
- [Homebrew（Mac）](#homebrew-mac)
- [Chocolatey（Windows）](#chocolatey-windows)
- [Scoop（Windows）](#scoop-windows)
- [Webi](#webi)
- [Ansible](#ansible)
- [Termux](#termux)
- [Nix/Nixpkgs/NixOS](#nixnixpkgsnixos)
- [Unikraft](#unikraft)
- [OPNsense](#opnsense)
- [mise](#mise)


<a id="static-binaries"></a>
## 静态二进制文件

**若要在生产环境中安装，建议使用下方提供的适用于您所用发行版的官方软件包（如有）。**

1. 获取 Caddy 二进制文件：
	- [来自 GitHub 上的发布版本](https://github.com/caddyserver/caddy/releases)（展开“资源”）
		- 有关如何验证资产签名，请参阅《[验证资产签名](/docs/signature-verification)》
	- [来自我们的下载页面](/download)
	- [通过从源代码编译](/docs/build)（使用 `go` 或 `xcaddy`)
2. [将 Caddy 安装为系统服务。](/docs/running#manual-installation)强烈建议这样做，尤其是对于生产服务器。

将二进制文件放置在您的 `$PATH` （或 `%PATH%` 在 Windows 上）目录中，这样您就可以运行 `caddy` 时无需输入可执行文件的完整路径。（运行 `echo $PATH` 以查看符合条件的目录列表。）

您可以通过用新版替换静态二进制文件并重启 Caddy 来升级静态二进制文件。使用 [`caddy upgrade`](/docs/command-line#caddy-upgrade) 命令可以轻松完成此操作。



<a id="debian-ubuntu-raspbian"></a>
## Debian、Ubuntu、Raspbian

安装此软件包会自动启动并运行 Caddy，将其作为名为 `caddy` 的 systemd 服务。此外，它还附带了一个可选的 `caddy-api` 服务，该服务默认未启用，但如果您主要通过 API 而不是配置文件来配置 Caddy，则应使用该服务。

安装完成后，请阅读[服务使用说明](/docs/running#using-the-service)。

**稳定版：**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**测试版本**（包括测试版和候选发布版）：

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**查看 Cloudsmith 仓库**](https://cloudsmith.io/~caddy/repos/)

如果您希望在自定义构建的 Caddy 中使用打包的辅助文件（systemd 服务、bash 补全和默认配置），请参[阅此处的](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian)说明。


<a id="fedora-redhat-centos"></a>
## Fedora、RedHat、CentOS

本软件包包含 Caddy 的两个 [systemd 服务](/docs/running#linux-service)单元文件，但默认情况下不会启用它们。建议使用该服务。若要启用，请阅读[服务使用说明](/docs/running#using-the-service)。

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
## Arch Linux、Manjaro、Parabola

该软件包包含两个经过大幅修改的 Caddy [systemd 服务](/docs/running#linux-service)单元文件，但默认情况下并未启用它们。
这些修改包括自定义的启动/停止行为以及额外的沙箱标志，具体说明请参见 [systemd 的 exec 文档](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing)；这可能会导致 Caddy 进程无法访问某些主机目录。

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**在 Arch Linux 软件仓库中查看 Caddy**](https://archlinux.org/packages/extra/x86_64/caddy/) 以及 [**Arch Linux 维基**](https://wiki.archlinux.org/title/Caddy)

## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**在 Docker Hub 上查看**](https://hub.docker.com/_/caddy)

请参阅我们[推荐的 Docker Compose 配置](/docs/running#docker-compose)和使用说明。


## Railway

得益于 [Railway](https://railway.com) 的赞助，我们正式支持此模板：

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


## Gentoo

*注：这是由社区维护的安装方法。*

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**查看 Gentoo 软件包**](https://packages.gentoo.org/packages/www-servers/caddy)



## Homebrew (Mac)

*注：这是由社区维护的安装方法。*

<pre><code class="cmd bash">brew install caddy</code></pre>

[**查看 Homebrew 配方**](https://formulae.brew.sh/formula/caddy)



## Chocolatey (Windows)

*注：这是由社区维护的安装方法。*

<pre><code class="cmd">choco install caddy</code></pre>

[**查看 Chocolatey 软件包**](https://chocolatey.org/packages/caddy)



<a id="scoop-windows"></a>
## Scoop（Windows）

*注：这是由社区维护的安装方法。*

<pre><code class="cmd">scoop install caddy</code></pre>

[**查看 Scoop 清单**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



## Webi

*注：这是由社区维护的安装方法。*

Linux 和 macOS：

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows：

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

您可能需要调整 Windows 防火墙规则，以允许来自非本地主机的传入连接。

[**在 Webi 上查看**](https://webinstall.dev/caddy)



## Ansible

*注：这是由社区维护的安装方法。*

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**查看 Ansible 角色仓库**](https://github.com/nvjacobo/caddy)



## Termux

*注：这是由社区维护的安装方法。*

<pre><code class="cmd">pkg install caddy</code></pre>

[**查看 Termux 的 build.sh 文件**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



## Nix/Nixpkgs/NixOS

*注：这是由社区维护的安装方法。*

- 包名：[`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- NixOS 模块：[`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**在 Nixpkgs 搜索中查看 Caddy**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) 以及 [**在 NixOS 选项搜索中查看**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



## Unikraft

*注：这是由社区维护的安装方法。*

首先安装 Unikraft 的配套工具 [`kraft`](https://unikraft.org/docs/cli)：

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

然后使用 Unikraft 运行 Caddy，命令如下：

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

若要允许非本地主机的传入连接，您需要将[ unikernel 实例连接到网络](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network)。

[**查看 Unikraft 应用目录**](https://github.com/unikraft/catalog/tree/main/examples/caddy) 以及 [**KraftCloud 平台示例（由 Unikraft 提供支持）**](https://github.com/kraftcloud/examples/tree/main/caddy)。



## OPNsense

*注：这是由社区维护的安装方法。*

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**查看 FreeBSD caddy-custom 的 Makefile**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) 和 [**os-caddy 插件的源代码**](https://github.com/opnsense/plugins/tree/master/www/caddy)

## mise

*注：这是由社区维护的安装方法。*

如果您正在使用多语言工具管理器 [mise](https://github.com/jdx/mise)，可以使用如下命令安装最新版本：

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
