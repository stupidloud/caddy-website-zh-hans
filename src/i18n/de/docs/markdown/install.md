---
title: "Installieren"
---

<a id="install"></a>
# Installieren

Diese Seite beschreibt verschiedene Methoden, Caddy auf deinem System zu installieren.

**Offiziell:**

- [Statische Binaries](#static-binaries)
- [Debian-, Ubuntu-, Raspbian-Pakete](#debian-ubuntu-raspbian)
- [Fedora-, RedHat-, CentOS-Pakete](#fedora-redhat-centos)
- [Arch-Linux-, Manjaro-, Parabola-Pakete](#arch-linux-manjaro-parabola)
- [Docker-Image](#docker)
- [Railway-Template](#railway)

<aside class="tip">

Unsere [offiziellen Pakete](https://github.com/caddyserver/dist) enthalten nur die Standardmodule. Wenn du Drittanbieter-Plugins brauchst, [baue aus dem Quellcode mit `xcaddy`](/docs/build#xcaddy), nutze [unsere Download-Seite](/download) oder [deploye auf Railway](#railway).

</aside>


**Von der Community gepflegt:**

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
## Statische Binaries

**Wenn du auf einem Produktionssystem installierst, empfehlen wir unser offizielles Paket für deine Distribution, falls es unten verfügbar ist.**

1. Beschaffe ein Caddy-Binary:
	- [aus den Releases auf GitHub](https://github.com/caddyserver/caddy/releases) ("Assets" ausklappen)
		- Siehe [Asset-Signaturen verifizieren](/docs/signature-verification), um die Signatur zu prüfen
	- [von unserer Download-Seite](/download)
	- [durch Bauen aus dem Quellcode](/docs/build) (entweder mit `go` oder `xcaddy`)
2. [Installiere Caddy als Systemdienst.](/docs/running#manual-installation) Das wird besonders für Produktionsserver dringend empfohlen.

Lege das Binary in einem deiner `$PATH`-Verzeichnisse ab (oder `%PATH%` unter Windows), damit du `caddy` ausführen kannst, ohne den vollständigen Pfad der ausführbaren Datei einzugeben. (Führe `echo $PATH` aus, um die passenden Verzeichnisse zu sehen.)

Statische Binaries kannst du aktualisieren, indem du sie durch neuere Versionen ersetzt und Caddy neu startest. Der Befehl [`caddy upgrade`](/docs/command-line#caddy-upgrade) kann das vereinfachen.



<a id="debian-ubuntu-raspbian"></a>
## Debian, Ubuntu, Raspbian

Die Installation dieses Pakets startet Caddy automatisch als [systemd-Dienst](/docs/running#linux-service) namens `caddy` und lässt ihn laufen. Es enthält außerdem einen optionalen Dienst `caddy-api`, der standardmäßig *nicht* aktiviert ist, aber verwendet werden sollte, wenn du Caddy hauptsächlich über seine API statt über config-Dateien konfigurierst.

Lies nach der Installation bitte die [Anweisungen zur Nutzung des Dienstes](/docs/running#using-the-service).

**Stabile Releases:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Testing-Releases** (einschließlich Betas und Release Candidates):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Cloudsmith-Repos ansehen**](https://cloudsmith.io/~caddy/repos/)

Wenn du die paketierten Support-Dateien (systemd-Dienste, bash completion und Standardkonfiguration) mit einem eigenen Caddy-Build verwenden möchtest, findest du die Anweisungen [hier](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


<a id="fedora-redhat-centos"></a>
## Fedora, RedHat, CentOS

Dieses Paket enthält beide [systemd service](/docs/running#linux-service)-Unit-Dateien von Caddy, aktiviert sie aber nicht standardmäßig. Die Nutzung des Dienstes wird empfohlen. Wenn du ihn verwendest, lies bitte die [Anweisungen zur Nutzung des Dienstes](/docs/running#using-the-service).

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Caddy COPR ansehen**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


<a id="arch-linux-manjaro-parabola"></a>
## Arch Linux, Manjaro, Parabola

Dieses Paket enthält stark angepasste Versionen beider [systemd service](/docs/running#linux-service)-Unit-Dateien von Caddy, aktiviert sie aber nicht standardmäßig.
Diese Anpassungen umfassen eigenes Start-/Stopp-Verhalten und zusätzliche Sandboxing-Flags, die in der [exec-Dokumentation von systemd](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing) erklärt werden. Dadurch sind bestimmte Host-Verzeichnisse für den Caddy-Prozess möglicherweise nicht verfügbar.

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Caddy in den Arch-Linux-Repositories ansehen**](https://archlinux.org/packages/extra/x86_64/caddy/) und [**das Arch-Linux-Wiki**](https://wiki.archlinux.org/title/Caddy)

<a id="docker"></a>
## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Auf Docker Hub ansehen**](https://hub.docker.com/_/caddy)

Siehe unsere [empfohlene Docker-Compose-Konfiguration](/docs/running#docker-compose) und Nutzungshinweise.


<a id="railway"></a>
## Railway

Durch ein Sponsoring von [Railway](https://railway.com) unterstützen wir offiziell dieses Template:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


<a id="gentoo"></a>
## Gentoo

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Gentoo-Paket ansehen**](https://packages.gentoo.org/packages/www-servers/caddy)



<a id="homebrew-mac"></a>
## Homebrew (Mac)

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Homebrew-Formel ansehen**](https://formulae.brew.sh/formula/caddy)



<a id="chocolatey-windows"></a>
## Chocolatey (Windows)

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd">choco install caddy</code></pre>

[**Chocolatey-Paket ansehen**](https://chocolatey.org/packages/caddy)



<a id="scoop-windows"></a>
## Scoop (Windows)

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd">scoop install caddy</code></pre>

[**Scoop-Manifest ansehen**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



<a id="webi"></a>
## Webi

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

Linux und macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Möglicherweise musst du die Windows-Firewallregeln anpassen, um eingehende Nicht-localhost-Verbindungen zu erlauben.

[**Auf Webi ansehen**](https://webinstall.dev/caddy)



<a id="ansible"></a>
## Ansible

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Ansible-Role-Repository ansehen**](https://github.com/nvjacobo/caddy)



<a id="termux"></a>
## Termux

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd">pkg install caddy</code></pre>

[**Termux build.sh-Datei ansehen**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



<a id="nixnixpkgsnixos"></a>
## Nix/Nixpkgs/NixOS

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

- Paketname: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- NixOS-Modul: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Caddy in der Nixpkgs-Suche ansehen**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) und [**die NixOS-Optionssuche**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



<a id="unikraft"></a>
## Unikraft

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

Installiere zuerst Unikrafts Begleitwerkzeug [`kraft`](https://unikraft.org/docs/cli):

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Führe Caddy dann mit Unikraft aus:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Um eingehende Nicht-localhost-Verbindungen zu erlauben, musst du [die Unikernel-Instanz mit einem Netzwerk verbinden](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Unikraft-Anwendungskatalog ansehen**](https://github.com/unikraft/catalog/tree/main/examples/caddy) und [**die KraftCloud-Plattformbeispiele (powered by Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy).



<a id="opnsense"></a>
## OPNsense

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**FreeBSD caddy-custom-Makefile ansehen**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) und [**den os-caddy-Plugin-Quellcode**](https://github.com/opnsense/plugins/tree/master/www/caddy)

<a id="mise"></a>
## Mise

_Hinweis: Dies ist eine von der Community gepflegte Installationsmethode._

Wenn du [mise](https://github.com/jdx/mise), den polyglotten Versionsmanager für Tools, verwendest, kannst du mit einem Befehl wie diesem die neueste Version installieren:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
