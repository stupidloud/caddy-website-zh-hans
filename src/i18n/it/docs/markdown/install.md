---
title: "Installazione"
---

# Installazione

Questa pagina descrive vari metodi per installare Caddy sul vostro sistema.

**Ufficiali:**

- [Binari statici](#static-binaries)
- [Pacchetti Debian, Ubuntu, Raspbian](#debian-ubuntu-raspbian)
- [Pacchetti Fedora, RedHat, CentOS](#fedora-redhat-centos)
- [Pacchetti Arch Linux, Manjaro, Parabola](#arch-linux-manjaro-parabola)
- [Immagine Docker](#docker)
- [Template Railway](#railway)

<aside class="tip">

I nostri [pacchetti ufficiali](https://github.com/caddyserver/dist) includono solo i moduli standard. Se avete bisogno di plugin di terze parti, [compilate dai sorgenti con `xcaddy`](/docs/build#xcaddy), usate la [nostra pagina di download](/download), o [distribuite su Railway](#railway).

</aside>


**Gestiti dalla comunità:**

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


## Binari statici

<a id="static-binaries"></a>
**Se state installando su un sistema di produzione, raccomandiamo di usare il pacchetto ufficiale per la vostra distribuzione, se disponibile di seguito.**

1. Ottenete un binario di Caddy:
	- [dalle release su GitHub](https://github.com/caddyserver/caddy/releases) (espandete "Assets")
		- Fate riferimento a [Verifica delle firme degli asset](/docs/signature-verification) per sapere come verificare la firma dell'asset
	- [dalla nostra pagina di download](/download)
	- [compilando dai sorgenti](/docs/build) (sia con `go` che con `xcaddy`)
2. [Installate Caddy come servizio di sistema.](/docs/running#manual-installation) Questo è caldamente raccomandato, specialmente per i server di produzione.

Posizionate il binario in una delle directory del vostro `$PATH` (o `%PATH%` su Windows) in modo da poter eseguire `caddy` senza digitare il percorso completo del file eseguibile. (Eseguite `echo $PATH` per vedere l'elenco delle directory idonee.)

Potete aggiornare i binari statici sostituendoli con versioni più recenti e riavviando Caddy. Il [comando `caddy upgrade`](/docs/command-line#caddy-upgrade) può facilitare questa operazione.



## Debian, Ubuntu, Raspbian

<a id="debian-ubuntu-raspbian"></a>
L'installazione di questo pacchetto avvia ed esegue automaticamente Caddy come [servizio systemd](/docs/running#linux-service) chiamato `caddy`. Include anche un servizio opzionale `caddy-api` che *non* è abilitato per impostazione predefinita, ma dovrebbe essere utilizzato se configurate Caddy principalmente tramite la sua API invece dei file di configurazione.

Dopo l'installazione, leggete le [istruzioni sull'uso del servizio](/docs/running#using-the-service).

**Release stabili:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Release di test** (include beta e release candidate):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Visualizza i repository Cloudsmith**](https://cloudsmith.io/~caddy/repos/)

Se desiderate utilizzare i file di supporto del pacchetto (servizi systemd, completamento bash e configurazione predefinita) con una build personalizzata di Caddy, le istruzioni si trovano [qui](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


## Fedora, RedHat, CentOS

<a id="fedora-redhat-centos"></a>
Questo pacchetto include entrambi i file delle unità del [servizio systemd](/docs/running#linux-service) di Caddy, ma non li abilita per impostazione predefinita. L'uso del servizio è raccomandato. In tal caso, leggete le [istruzioni sull'uso del servizio](/docs/running#using-the-service).

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Visualizza il COPR di Caddy**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


## Arch Linux, Manjaro, Parabola

<a id="arch-linux-manjaro-parabola"></a>
Questo pacchetto include versioni pesantemente modificate di entrambi i file delle unità del [servizio systemd](/docs/running#linux-service) di Caddy, ma non li abilita per impostazione predefinita.
Tali modifiche includono un comportamento di avvio/arresto personalizzato e flag di sandboxing aggiuntivi spiegati nella [documentazione exec di systemd](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing), che potrebbero rendere alcune directory dell'host non disponibili al processo Caddy. 

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Visualizza Caddy nei repository di Arch Linux**](https://archlinux.org/packages/extra/x86_64/caddy/) e il [**Wiki di Arch Linux**](https://wiki.archlinux.org/title/Caddy)

## Docker

<a id="docker"></a>
<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Visualizza su Docker Hub**](https://hub.docker.com/_/caddy)

Consultate la nostra [configurazione Docker Compose raccomandata](/docs/running#docker-compose) e le istruzioni d'uso.


## Railway

<a id="railway"></a>
Grazie alla sponsorizzazione di [Railway](https://railway.com), supportiamo ufficialmente questo template:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


## Gentoo

<a id="gentoo"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Visualizza il pacchetto Gentoo**](https://packages.gentoo.org/packages/www-servers/caddy)



## Homebrew (Mac)

<a id="homebrew-mac"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Visualizza la formula Homebrew**](https://formulae.brew.sh/formula/caddy)



## Chocolatey (Windows)

<a id="chocolatey-windows"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd">choco install caddy</code></pre>

[**Visualizza il pacchetto Chocolatey**](https://chocolatey.org/packages/caddy)



## Scoop (Windows)

<a id="scoop-windows"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd">scoop install caddy</code></pre>

[**Visualizza il manifest di Scoop**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



## Webi

<a id="webi"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

Linux e macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Potrebbe essere necessario regolare le regole del firewall di Windows per consentire connessioni in entrata non provenienti da localhost.

[**Visualizza su Webi**](https://webinstall.dev/caddy)



## Ansible

<a id="ansible"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Visualizza il repository del ruolo Ansible**](https://github.com/nvjacobo/caddy)



## Termux

<a id="termux"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd">pkg install caddy</code></pre>

[**Visualizza il file build.sh di Termux**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



## Nix/Nixpkgs/NixOS

<a id="nixnixpkgsnixos"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

- Nome del pacchetto: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- Modulo NixOS: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Visualizza Caddy nella ricerca Nixpkgs**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) e nella [**ricerca delle opzioni NixOS**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



## Unikraft

<a id="unikraft"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

Per prima cosa installate lo strumento complementare di Unikraft, [`kraft`](https://unikraft.org/docs/cli):

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Quindi eseguite Caddy con Unikraft usando:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Per consentire connessioni in entrata non provenienti da localhost, è necessario [connettere l'istanza unikernel a una rete](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Visualizza il catalogo delle applicazioni Unikraft**](https://github.com/unikraft/catalog/tree/main/examples/caddy) e gli [**esempi della piattaforma KraftCloud (basata su Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy).



## OPNsense

<a id="opnsense"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**Visualizza il makefile caddy-custom di FreeBSD**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) e il [**sorgente del plugin os-caddy**](https://github.com/opnsense/plugins/tree/master/www/caddy)

## Mise

<a id="mise"></a>
_Nota: Questo è un metodo di installazione gestito dalla comunità._

Se state usando [mise](https://github.com/jdx/mise), il gestore di versioni di strumenti poliglotta, potete usare un comando come questo per installare l'ultima versione:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
