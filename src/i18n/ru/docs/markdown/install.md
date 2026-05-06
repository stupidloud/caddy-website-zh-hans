---
title: "Установка"
---

<a id="install"></a>
# Установка

На этой странице описаны разные способы установки Caddy в вашей системе.

**Официальные:**

- [Статические бинарные файлы](#static-binaries)
- [Пакеты Debian, Ubuntu, Raspbian](#debian-ubuntu-raspbian)
- [Пакеты Fedora, RedHat, CentOS](#fedora-redhat-centos)
- [Пакеты Arch Linux, Manjaro, Parabola](#arch-linux-manjaro-parabola)
- [Docker image](#docker)
- [Шаблон Railway](#railway)

<aside class="tip">

Наши [официальные пакеты](https://github.com/caddyserver/dist) поставляются только со стандартными модулями. Если вам нужны сторонние плагины, [соберите из исходного кода с `xcaddy`](/docs/build#xcaddy), используйте [нашу страницу загрузки](/download) или [разверните на Railway](#railway).

</aside>


**Поддерживаются сообществом:**

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
## Статические бинарные файлы

**При установке на production-систему мы рекомендуем использовать официальный пакет для вашего дистрибутива, если он доступен ниже.**

1. Получите бинарный файл Caddy:
	- [из релизов на GitHub](https://github.com/caddyserver/caddy/releases) (раскройте "Assets")
		- Смотрите [Проверку подписей ресурсов](/docs/signature-verification), чтобы узнать, как проверить подпись ресурса
	- [с нашей страницы загрузки](/download)
	- [собрав из исходного кода](/docs/build) (с `go` или `xcaddy`)
2. [Установите Caddy как системный сервис.](/docs/running#manual-installation) Это настоятельно рекомендуется, особенно для production-серверов.

Поместите бинарный файл в один из каталогов вашего `$PATH` (или `%PATH%` в Windows), чтобы можно было запускать `caddy` без ввода полного пути к исполняемому файлу. (Выполните `echo $PATH`, чтобы увидеть список подходящих каталогов.)

Статические бинарные файлы можно обновлять, заменяя их более новыми версиями и перезапуская Caddy. Команда [`caddy upgrade`](/docs/command-line#caddy-upgrade) может упростить это.



<a id="debian-ubuntu-raspbian"></a>
## Debian, Ubuntu, Raspbian

Установка этого пакета автоматически запускает Caddy как [systemd service](/docs/running#linux-service) с именем `caddy`. Он также включает дополнительный сервис `caddy-api`, который по умолчанию *не* включен, но его следует использовать, если вы в основном настраиваете Caddy через API, а не через конфигурационные файлы.

После установки прочитайте [инструкции по использованию сервиса](/docs/running#using-the-service).

**Стабильные релизы:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Тестовые релизы** (включая beta-версии и release candidates):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Посмотреть репозитории Cloudsmith**](https://cloudsmith.io/~caddy/repos/)

Если вы хотите использовать пакетные вспомогательные файлы (systemd services, bash completion и конфигурацию по умолчанию) с собственной сборкой Caddy, инструкции можно [найти здесь](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


<a id="fedora-redhat-centos"></a>
## Fedora, RedHat, CentOS

Этот пакет поставляется с обоими unit-файлами [systemd service](/docs/running#linux-service) Caddy, но по умолчанию не включает их. Использовать сервис рекомендуется. Если вы так сделаете, прочитайте [инструкции по использованию сервиса](/docs/running#using-the-service).

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Посмотреть Caddy COPR**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


<a id="arch-linux-manjaro-parabola"></a>
## Arch Linux, Manjaro, Parabola

Этот пакет поставляется с сильно измененными версиями обоих unit-файлов [systemd service](/docs/running#linux-service) Caddy, но по умолчанию не включает их.
Эти изменения включают особое поведение start/stop и дополнительные флаги sandboxing, которые объяснены в [документации systemd exec](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing); из-за них некоторые каталоги хоста могут быть недоступны процессу Caddy. 

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Посмотреть Caddy в репозиториях Arch Linux**](https://archlinux.org/packages/extra/x86_64/caddy/) и [**Arch Linux Wiki**](https://wiki.archlinux.org/title/Caddy)

<a id="docker"></a>
## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Посмотреть на Docker Hub**](https://hub.docker.com/_/caddy)

Смотрите нашу [рекомендуемую конфигурацию Docker Compose](/docs/running#docker-compose) и инструкции по использованию.


<a id="railway"></a>
## Railway

Благодаря спонсорской поддержке [Railway](https://railway.com) мы официально поддерживаем этот шаблон:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


<a id="gentoo"></a>
## Gentoo

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Посмотреть пакет Gentoo**](https://packages.gentoo.org/packages/www-servers/caddy)



<a id="homebrew-mac"></a>
## Homebrew (Mac)

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Посмотреть Homebrew formula**](https://formulae.brew.sh/formula/caddy)



<a id="chocolatey-windows"></a>
## Chocolatey (Windows)

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd">choco install caddy</code></pre>

[**Посмотреть пакет Chocolatey**](https://chocolatey.org/packages/caddy)



<a id="scoop-windows"></a>
## Scoop (Windows)

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd">scoop install caddy</code></pre>

[**Посмотреть Scoop manifest**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



<a id="webi"></a>
## Webi

*Примечание: этот способ установки поддерживается сообществом.*

Linux и macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Возможно, вам потребуется изменить правила брандмауэра Windows, чтобы разрешить входящие подключения не только с localhost.

[**Посмотреть на Webi**](https://webinstall.dev/caddy)



<a id="ansible"></a>
## Ansible

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Посмотреть репозиторий роли Ansible**](https://github.com/nvjacobo/caddy)



<a id="termux"></a>
## Termux

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd">pkg install caddy</code></pre>

[**Посмотреть файл build.sh Termux**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



<a id="nixnixpkgsnixos"></a>
## Nix/Nixpkgs/NixOS

*Примечание: этот способ установки поддерживается сообществом.*

- Имя пакета: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- Модуль NixOS: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Посмотреть Caddy в поиске Nixpkgs**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) и [**поиск параметров NixOS**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



<a id="unikraft"></a>
## Unikraft

*Примечание: этот способ установки поддерживается сообществом.*

Сначала установите сопутствующий инструмент Unikraft, [`kraft`](https://unikraft.org/docs/cli):

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Затем запустите Caddy с Unikraft так:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Чтобы разрешить входящие подключения не только с localhost, нужно [подключить экземпляр unikernel к сети](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Посмотреть каталог приложений Unikraft**](https://github.com/unikraft/catalog/tree/main/examples/caddy) и [**примеры платформы KraftCloud (powered by Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy).



<a id="opnsense"></a>
## OPNsense

*Примечание: этот способ установки поддерживается сообществом.*

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**Посмотреть FreeBSD caddy-custom makefile**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) и [**исходный код плагина os-caddy**](https://github.com/opnsense/plugins/tree/master/www/caddy)

<a id="mise"></a>
## Mise

*Примечание: этот способ установки поддерживается сообществом.*

Если вы используете [mise](https://github.com/jdx/mise), polyglot-менеджер версий инструментов, можно установить последнюю версию такой командой:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
