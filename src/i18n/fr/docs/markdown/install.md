---
title: "Installation"
---

# Installation

Cette page décrit les différentes méthodes pour installer Caddy sur votre système.

**Officiel :**

- [Binaires statiques](#static-binaries)
- [Paquets Debian, Ubuntu, Raspbian](#debian-ubuntu-raspbian)
- [Paquets Fedora, RedHat, CentOS](#fedora-redhat-centos)
- [Paquets Arch Linux, Manjaro, Parabola](#arch-linux-manjaro-parabola)
- [Image Docker](#docker)
- [Modèle (template) Railway](#railway)

<aside class="tip">

Nos [paquets officiels](https://github.com/caddyserver/dist) ne contiennent que les modules standard. Si vous avez besoin de plugins tiers, [compilez depuis les sources avec `xcaddy`](/docs/build#xcaddy), utilisez [notre page de téléchargement](/download) ou [déployez sur Railway](#railway).

</aside>


**Maintenu par la communauté :**

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
## Binaires statiques

**Pour une installation sur un système de production, nous recommandons d'utiliser le paquet officiel de votre distribution s'il est listé ci-dessous.**

1. Obtenez un binaire Caddy :
	- [depuis les releases sur GitHub](https://github.com/caddyserver/caddy/releases) (déroulez "Assets")
		- Reportez-vous à [Vérification des signatures d'assets](/docs/signature-verification) pour savoir comment vérifier la signature
	- [depuis notre page de téléchargement](/download)
	- [en compilant depuis les sources](/docs/build) (avec `go` ou `xcaddy`)
2. [Installez Caddy comme un service système.](/docs/running#manual-installation) Ceci est fortement recommandé, surtout pour les serveurs de production.

Placez le binaire dans l'un des répertoires de votre `$PATH` (ou `%PATH%` sous Windows) afin de pouvoir lancer `caddy` sans taper le chemin complet du fichier. (Exécutez `echo $PATH` pour voir la liste des répertoires éligibles.)

Vous pouvez mettre à jour les binaires statiques en les remplaçant par des versions plus récentes et en redémarrant Caddy. La commande [`caddy upgrade`](/docs/command-line#caddy-upgrade) peut faciliter cette opération.


<a id="debian-ubuntu-raspbian"></a>
## Debian, Ubuntu, Raspbian

L'installation de ce paquet démarre et lance automatiquement Caddy en tant que [service systemd](/docs/running#linux-service) nommé `caddy`. Il contient également un service optionnel `caddy-api` qui n'est *pas* activé par défaut, mais qui devrait être utilisé si vous configurez principalement Caddy via son API plutôt que via des fichiers de configuration.

Après l'installation, veuillez lire les [instructions d'utilisation du service](/docs/running#using-the-service).

**Versions stables (Stable) :**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Versions de test (Testing)** (inclut les bêtas et les candidats à la release) :

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Voir les dépôts Cloudsmith**](https://cloudsmith.io/~caddy/repos/)

Si vous souhaitez utiliser les fichiers de support fournis (services systemd, complétion bash et configuration par défaut) avec un build Caddy personnalisé, les instructions se [trouvent ici](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


<a id="fedora-redhat-centos"></a>
## Fedora, RedHat, CentOS

Ce paquet contient les deux fichiers d'unité de [service systemd](/docs/running#linux-service) de Caddy, mais ne les active pas par défaut. L'utilisation du service est recommandée. Dans ce cas, veuillez lire les [instructions d'utilisation du service](/docs/running#using-the-service).

Fedora :

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL :

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Voir le COPR Caddy**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


<a id="arch-linux-manjaro-parabola"></a>
## Arch Linux, Manjaro, Parabola

Ce paquet est livré avec des versions lourdement modifiées des deux fichiers d'unité de [service systemd](/docs/running#linux-service) de Caddy, mais ne les active pas par défaut.
Ces modifications incluent un comportement de démarrage/arrêt personnalisé et des drapeaux de sandboxing (bac à sable) supplémentaires expliqués dans la [documentation d'exécution de systemd](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing), ce qui peut rendre certains répertoires de l'hôte inaccessibles au processus Caddy. 

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Voir Caddy dans les dépôts Arch Linux**](https://archlinux.org/packages/extra/x86_64/caddy/) et [**le Wiki Arch Linux**](https://wiki.archlinux.org/title/Caddy)

<a id="docker"></a>
## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Voir sur le Docker Hub**](https://hub.docker.com/_/caddy)

Consultez notre [configuration Docker Compose recommandée](/docs/running#docker-compose) et ses instructions d'utilisation.


<a id="railway"></a>
## Railway

Grâce au parrainage de [Railway](https://railway.com), nous supportons officiellement ce modèle (template) :

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


<a id="gentoo"></a>
## Gentoo

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Voir le paquet Gentoo**](https://packages.gentoo.org/packages/www-servers/caddy)



<a id="homebrew-mac"></a>
## Homebrew (Mac)

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Voir la formule Homebrew**](https://formulae.brew.sh/formula/caddy)



<a id="chocolatey-windows"></a>
## Chocolatey (Windows)

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd">choco install caddy</code></pre>

[**Voir le paquet Chocolatey**](https://chocolatey.org/packages/caddy)



<a id="scoop-windows"></a>
## Scoop (Windows)

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd">scoop install caddy</code></pre>

[**Voir le manifeste Scoop**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



<a id="webi"></a>
## Webi

_Note : Cette méthode d'installation est maintenue par la communauté._

Linux et macOS :

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows :

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Vous pourriez avoir besoin d'ajuster les règles du pare-feu Windows pour autoriser les connexions entrantes ne provenant pas de localhost.

[**Voir sur Webi**](https://webinstall.dev/caddy)



<a id="ansible"></a>
## Ansible

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Voir le dépôt du rôle Ansible**](https://github.com/nvjacobo/caddy)



<a id="termux"></a>
## Termux

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd">pkg install caddy</code></pre>

[**Voir le fichier build.sh de Termux**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



<a id="nixnixpkgsnixos"></a>
## Nix/Nixpkgs/NixOS

_Note : Cette méthode d'installation est maintenue par la communauté._

- Nom du paquet : [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- Module NixOS : [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Voir Caddy dans la recherche Nixpkgs**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) et [**la recherche d'options NixOS**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



<a id="unikraft"></a>
## Unikraft

_Note : Cette méthode d'installation est maintenue par la communauté._

Installez d'abord l'outil compagnon d'Unikraft, [`kraft`](https://unikraft.org/docs/cli) :

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Puis lancez Caddy avec Unikraft en utilisant :

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Pour autoriser les connexions entrantes ne provenant pas de localhost, vous devez [connecter l'instance unikernel à un réseau](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Voir le catalogue d'applications Unikraft**](https://github.com/unikraft/catalog/tree/main/examples/caddy) et [**les exemples de la plateforme KraftCloud (propulsée par Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy).



<a id="opnsense"></a>
## OPNsense

_Note : Cette méthode d'installation est maintenue par la communauté._

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**Voir le makefile FreeBSD caddy-custom**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) et [**le code source du plugin os-caddy**](https://github.com/opnsense/plugins/tree/master/www/caddy)

<a id="mise"></a>
## Mise

_Note : Cette méthode d'installation est maintenue par la communauté._

Si vous utilisez [mise](https://github.com/jdx/mise), le gestionnaire de versions d'outils polyglotte, vous pouvez utiliser une commande comme celle-ci pour installer la dernière version :

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
