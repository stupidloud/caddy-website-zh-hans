---
title: "Instalar"
---

# Instalar

Esta página descreve vários métodos para instalar o Caddy no seu sistema.

**Oficial:**

- [Binários estáticos](#static-binaries)
- [Pacotes Debian, Ubuntu, Raspbian](#debian-ubuntu-raspbian)
- [Pacotes Fedora, RedHat, CentOS](#fedora-redhat-centos)
- [Pacotes Arch Linux, Manjaro, Parabola](#arch-linux-manjaro-parabola)
- [Imagem Docker](#docker)
- [Template Railway](#railway)

<aside class="tip">

Nossos [pacotes oficiais](https://github.com/caddyserver/dist) vêm apenas com os módulos padrão. Se você precisa de plugins de terceiros, [compile a partir do código-fonte com `xcaddy`](/docs/build#xcaddy), use [nossa página de download](/download) ou [implante no Railway](#railway).

</aside>

**Mantidos pela comunidade:**

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
## Binários estáticos

**Se você estiver instalando em um sistema de produção, recomendamos usar nosso pacote oficial para sua distribuição, se disponível abaixo.**

1. Obtenha um binário do Caddy:
	- [das releases no GitHub](https://github.com/caddyserver/caddy/releases) (expanda "Assets")
		- Consulte [Verificando assinaturas de artefatos](/docs/signature-verification) para ver como verificar a assinatura do artefato
	- [de nossa página de download](/download)
	- [compilando a partir do código-fonte](/docs/build) (com `go` ou `xcaddy`)
2. [Instale o Caddy como um serviço do sistema.](/docs/running#manual-installation) Isso é fortemente recomendado, especialmente para servidores de produção.

Coloque o binário em um dos diretórios do seu `$PATH` (ou `%PATH%` no Windows) para que você possa executar `caddy` sem digitar o caminho completo do executável. (Execute `echo $PATH` para ver a lista de diretórios que se qualificam.)

Você pode atualizar binários estáticos substituindo-os por versões mais novas e reiniciando o Caddy. O comando [`caddy upgrade`](/docs/command-line#caddy-upgrade) pode facilitar isso.

## Debian, Ubuntu, Raspbian

Instalar este pacote inicia e executa automaticamente o Caddy como um serviço [systemd](/docs/running#linux-service) chamado `caddy`. Ele também vem com um serviço opcional `caddy-api`, que **não** é habilitado por padrão, mas deve ser usado se você configurar o Caddy principalmente pela API em vez de arquivos de configuração.

Depois de instalar, leia as [instruções de uso do serviço](/docs/running#using-the-service).

**Versões estáveis:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Versões de teste** (inclui betas e release candidates):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Ver os repositórios Cloudsmith**](https://cloudsmith.io/~caddy/repos/)

Se você quiser usar os arquivos de suporte empacotados (serviços systemd, bash completion e configuração padrão) com um build personalizado do Caddy, as instruções podem ser [encontradas aqui](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).

## Fedora, RedHat, CentOS

Este pacote vem com os dois arquivos de unidade de serviço [systemd](/docs/running#linux-service) do Caddy, mas não os habilita por padrão. Usar o serviço é recomendado. Se fizer isso, leia as [instruções de uso do serviço](/docs/running#using-the-service).

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Ver o COPR do Caddy**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)

## Arch Linux, Manjaro, Parabola

Este pacote vem com versões bastante modificadas dos dois arquivos de unidade de serviço [systemd](/docs/running#linux-service) do Caddy, mas não os habilita por padrão.
Essas modificações incluem um comportamento personalizado de start/stop e flags adicionais de sandboxing, explicadas na [documentação de exec do systemd](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing), o que pode fazer com que certos diretórios do host não fiquem disponíveis para o processo do Caddy.

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Ver o Caddy nos repositórios do Arch Linux**](https://archlinux.org/packages/extra/x86_64/caddy/) e [**a wiki do Arch Linux**](https://wiki.archlinux.org/title/Caddy)

## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Ver no Docker Hub**](https://hub.docker.com/_/caddy)

Veja nossa [configuração recomendada do Docker Compose](/docs/running#docker-compose) e as instruções de uso.

## Railway

Por meio de um patrocínio da [Railway](https://railway.com), damos suporte oficial a este template:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)

## Gentoo

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Ver o pacote Gentoo**](https://packages.gentoo.org/packages/www-servers/caddy)

## Homebrew (Mac)

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Ver a fórmula do Homebrew**](https://formulae.brew.sh/formula/caddy)

## Chocolatey (Windows)

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd">choco install caddy</code></pre>

[**Ver o pacote Chocolatey**](https://chocolatey.org/packages/caddy)

## Scoop (Windows)

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd">scoop install caddy</code></pre>

[**Ver o manifesto Scoop**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)

## Webi

_Observação: este é um método de instalação mantido pela comunidade._

Linux e macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Talvez você precise ajustar as regras do firewall do Windows para permitir conexões de entrada que não venham de localhost.

[**Ver no Webi**](https://webinstall.dev/caddy)

## Ansible

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Ver o repositório da role Ansible**](https://github.com/nvjacobo/caddy)

## Termux

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd">pkg install caddy</code></pre>

[**Ver o arquivo build.sh do Termux**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)

## Nix/Nixpkgs/NixOS

_Observação: este é um método de instalação mantido pela comunidade._

- Nome do pacote: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- Módulo NixOS: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Ver o Caddy na busca do Nixpkgs**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) e [**na busca de opções do NixOS**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

## Unikraft

_Observação: este é um método de instalação mantido pela comunidade._

Primeiro instale a ferramenta companheira do Unikraft, [`kraft`](https://unikraft.org/docs/cli):

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Depois execute o Caddy com o Unikraft usando:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Para permitir conexões de entrada que não venham de localhost, você precisa [conectar a instância unikernel a uma rede](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Ver o catálogo de aplicações do Unikraft**](https://github.com/unikraft/catalog/tree/main/examples/caddy) e [**os exemplos da plataforma KraftCloud (alimentada por Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy).

## OPNsense

_Observação: este é um método de instalação mantido pela comunidade._

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**Ver o makefile caddy-custom do FreeBSD**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) e [**o código-fonte do plugin os-caddy**](https://github.com/opnsense/plugins/tree/master/www/caddy)

## Mise

_Observação: este é um método de instalação mantido pela comunidade._

Se você usa [mise](https://github.com/jdx/mise), o gerenciador poliglota de versões de ferramentas, pode usar um comando como este para instalar a última versão:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
