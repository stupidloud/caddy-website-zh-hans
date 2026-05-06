---
title: "Instalar"
---

# Instalar

Esta página describe varios métodos para instalar Caddy en tu sistema.

**Oficial:**

- [Binarios estáticos](#static-binaries)
- [Paquetes Debian, Ubuntu, Raspbian](#debian-ubuntu-raspbian)
- [Paquetes Fedora, RedHat, CentOS](#fedora-redhat-centos)
- [Paquetes Arch Linux, Manjaro, Parabola](#arch-linux-manjaro-parabola)
- [Imagen Docker](#docker)
- [Plantilla de Railway](#railway)

<aside class="tip">

Nuestros [paquetes oficiales](https://github.com/caddyserver/dist) solo incluyen los módulos estándar. Si necesitas plugins de terceros, [compila desde el código fuente con `xcaddy`](/docs/build#xcaddy), usa [nuestra página de descarga](/download) o [despliega en Railway](#railway).

</aside>


**Mantenidos por la comunidad:**

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
## Binarios estáticos

**Si instalas en un sistema de producción, recomendamos usar nuestro paquete oficial para tu distribución si está disponible a continuación.**

1. Obtén un binario de Caddy:
	- [de los lanzamientos en GitHub](https://github.com/caddyserver/caddy/releases) (expande "Assets")
		- Consulta [Verificar firmas de activos](/docs/signature-verification) para verificar la firma del paquete
	- [desde nuestra página de descarga](/download)
	- [compilando desde el código fuente](/docs/build) (con `go` o `xcaddy`)
2. [Instala Caddy como servicio del sistema](/docs/running#manual-installation). Esto se recomienda especialmente para servidores de producción.

Coloca el binario en uno de los directorios de tu `$PATH` (o `%PATH%` en Windows) para poder ejecutar `caddy` sin tener que escribir la ruta completa del ejecutable. (Ejecuta `echo $PATH` para ver la lista de directorios válidos.)

Puedes actualizar los binarios estáticos reemplazándolos por versiones más recientes y reiniciando Caddy. El [`comando caddy upgrade`](/docs/command-line#caddy-upgrade) puede hacer esto más sencillo.



<a id="debian-ubuntu-raspbian"></a>
## Debian, Ubuntu, Raspbian

Instalar este paquete inicia y ejecuta automáticamente Caddy como un [servicio systemd](/docs/running#linux-service) llamado `caddy`. También incluye un servicio opcional `caddy-api` que _no_ está habilitado por defecto, pero se debe usar si configuras Caddy principalmente a través de su API en lugar de archivos de configuración.

Después de instalar, por favor lee las [instrucciones de uso del servicio](/docs/running#using-the-service).

**Versiones estables:**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Versiones de prueba** (incluye betas y versiones candidatas):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Ver los repositorios de Cloudsmith**](https://cloudsmith.io/~caddy/repos/)

Si deseas usar los archivos de soporte del paquete (servicios systemd, autocompletado de bash y configuración predeterminada) con una compilación personalizada de Caddy, las instrucciones están [aquí](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


<a id="fedora-redhat-centos"></a>
## Fedora, RedHat, CentOS

Este paquete incluye ambos archivos de unidad de [servicio systemd](/docs/running#linux-service) de Caddy, pero no los habilita por defecto. Se recomienda usar el servicio. Si lo haces, lee las [instrucciones de uso del servicio](/docs/running#using-the-service).

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Ver el Caddy COPR**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


<a id="arch-linux-manjaro-parabola"></a>
## Arch Linux, Manjaro, Parabola

Este paquete incluye versiones fuertemente modificadas de ambos archivos de unidad de [servicio systemd](/docs/running#linux-service) de Caddy, pero no los habilita por defecto.
Esas modificaciones incluyen un comportamiento personalizado de inicio/parada y banderas adicionales de sandboxing que se explican en la [documentación de systemd exec](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing), lo que puede hacer que algunos directorios del host no estén disponibles para el proceso de Caddy.

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Ver Caddy en los repositorios de Arch Linux**](https://archlinux.org/packages/extra/x86_64/caddy/) y [**la wiki de Arch Linux**](https://wiki.archlinux.org/title/Caddy)

<a id="docker"></a>
## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Ver en Docker Hub**](https://hub.docker.com/_/caddy)

Consulta nuestra [configuración recomendada de Docker Compose](/docs/running#docker-compose) y las instrucciones de uso.


<a id="railway"></a>
## Railway

Gracias al patrocinio de [Railway](https://railway.com), ofrecemos soporte oficial para esta plantilla:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


<a id="gentoo"></a>
## Gentoo

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Ver el paquete de Gentoo**](https://packages.gentoo.org/packages/www-servers/caddy)



<a id="homebrew-mac"></a>
## Homebrew (Mac)

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Ver la fórmula de Homebrew**](https://formulae.brew.sh/formula/caddy)



<a id="chocolatey-windows"></a>
## Chocolatey (Windows)

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd">choco install caddy</code></pre>

[**Ver el paquete de Chocolatey**](https://chocolatey.org/packages/caddy)



<a id="scoop-windows"></a>
## Scoop (Windows)

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd">scoop install caddy</code></pre>

[**Ver el manifiesto de Scoop**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



<a id="webi"></a>
## Webi

_Nota: Este es un método de instalación mantenido por la comunidad._

Linux y macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Es posible que debas ajustar las reglas del firewall de Windows para permitir conexiones entrantes que no sean localhost.

[**Ver en Webi**](https://webinstall.dev/caddy)



<a id="ansible"></a>
## Ansible

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Ver el repositorio del rol de Ansible**](https://github.com/nvjacobo/caddy)



<a id="termux"></a>
## Termux

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd">pkg install caddy</code></pre>

[**Ver el archivo `build.sh` de Termux**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



<a id="nixnixpkgsnixos"></a>
## Nix/Nixpkgs/NixOS

_Nota: Este es un método de instalación mantenido por la comunidad._

- Nombre del paquete: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- Módulo de NixOS: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Ver Caddy en la búsqueda de Nixpkgs**](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) y [**la búsqueda de opciones de NixOS**](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)



<a id="unikraft"></a>
## Unikraft

_Nota: Este es un método de instalación mantenido por la comunidad._

Primero instala la herramienta auxiliar de Unikraft, [`kraft`](https://unikraft.org/docs/cli):

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Luego ejecuta Caddy con Unikraft usando:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Para permitir conexiones entrantes que no sean de localhost, necesitas [conectar la instancia unikernel a una red](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Ver el catálogo de aplicaciones de Unikraft**](https://github.com/unikraft/catalog/tree/main/examples/caddy) y [**los ejemplos de plataforma KraftCloud (con Unikraft)**](https://github.com/kraftcloud/examples/tree/main/caddy).



<a id="opnsense"></a>
## OPNsense

_Nota: Este es un método de instalación mantenido por la comunidad._

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**Ver el makefile `caddy-custom` de FreeBSD**](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) y [**el código fuente del plugin `os-caddy`**](https://github.com/opnsense/plugins/tree/master/www/caddy)

<a id="mise"></a>
## Mise

_Nota: Este es un método de instalación mantenido por la comunidad._

Si usas [mise](https://github.com/jdx/mise), el administrador de versiones multilenguaje, puedes usar un comando como este para instalar la última versión:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
