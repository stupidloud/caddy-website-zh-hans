---
title: "Compiler depuis les sources"
---

# Compiler depuis les sources

Il existe plusieurs options pour compiler Caddy si vous avez besoin d'un build personnalisé (ex: avec des plugins) :
- [Git](#git) : Compiler depuis le dépôt Git
- [`xcaddy`](#xcaddy) : Compiler en utilisant `xcaddy`
- [Docker](#docker) : Construire une image Docker personnalisée

**Prérequis :**

- [Go](https://golang.org/doc/install) 1.20 ou plus récent

La section [Fichiers de support du paquet](#package-support-files-for-custom-builds-for-debianubunturaspbian) contient des instructions pour les utilisateurs ayant installé Caddy via la commande APT sur un système dérivé de Debian mais ayant besoin d'un exécutable personnalisé pour leurs opérations.



<a id="git"></a>
## Git

**Prérequis :**

- Go installé (voir ci-dessus)

Clonez le dépôt :

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Si vous n'avez pas git, vous pouvez télécharger le code source sous forme d'archive [depuis GitHub](https://github.com/caddyserver/caddy). Chaque [version (release)](https://github.com/caddyserver/caddy/releases) propose également des instantanés du code source.

Compilation :

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

En raison d'un [bug dans Go](https://github.com/golang/go/issues/29228), ces étapes de base n'intègrent pas les informations de version. Si vous souhaitez obtenir la version (`caddy version`), vous devez compiler Caddy en tant que dépendance plutôt qu'en tant que module principal. Les instructions se trouvent dans le fichier [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) de Caddy. Vous pouvez également utiliser [`xcaddy`](#xcaddy) qui automatise cela.

</aside>

Les programmes Go sont faciles à compiler pour d'autres plateformes. Il suffit de définir les variables d'environnement `GOOS`, `GOARCH` et/ou `GOARM` appropriées. ([Consultez la documentation de Go pour plus de détails.](https://golang.org/doc/install/source#environment))

Par exemple, pour compiler Caddy pour Windows depuis un autre système :

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

Ou de la même manière pour Linux ARMv6 :

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



<a id="xcaddy"></a>
## xcaddy

La [commande `xcaddy`](https://github.com/caddyserver/xcaddy) est le moyen le plus simple de compiler Caddy avec les informations de version et/ou des plugins.

**Prérequis :**

- Go installé (voir ci-dessus)
- Assurez-vous que [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) est dans votre `PATH`

Vous n'avez **pas** besoin de télécharger le code source de Caddy (il le fera pour vous).

Compiler Caddy (avec les informations de version) est alors aussi simple que :

<pre><code class="cmd bash">xcaddy build</code></pre>

Pour compiler avec des plugins, utilisez `--with` :

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Comme vous pouvez le voir, vous pouvez personnaliser les versions des plugins avec la syntaxe `@`. Les versions peuvent être un nom de tag, un SHA de commit ou une branche.

La compilation multi-plateforme avec `xcaddy` fonctionne de la même manière qu'avec la commande `go`. Par exemple, pour compiler pour macOS :

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



<a id="docker"></a>
## Docker

Vous pouvez utiliser l'image `:builder` comme raccourci pour compiler un nouveau binaire Caddy avec des modules personnalisés :

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Remplacez `<version>` par la dernière version de Caddy pour commencer.

Notez la seconde instruction `FROM` — elle produit une image beaucoup plus petite en superposant simplement le binaire fraîchement compilé sur l'image `caddy` standard.

Le builder utilise `xcaddy` pour compiler Caddy avec les modules fournis, selon le processus [décrit plus haut](#xcaddy). Les options `--mount=type=cache,target=/go/pkg/mod` et `--mount=type=cache,target=/root/.cache/go-build` servent à mettre en cache respectivement les dépendances des modules Go et les artefacts de compilation, ce qui accélère les builds suivants. Ce drapeau est une [fonctionnalité de Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), pas de `xcaddy`.

Pour utiliser Docker Compose, consultez notre [`compose.yml`](/docs/running#docker-compose) recommandé et ses instructions d'utilisation.



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Fichiers de support du paquet pour les builds personnalisés sur Debian/Ubuntu/Raspbian

Cette procédure vise à simplifier l'exécution de binaires `caddy` personnalisés tout en conservant les fichiers de support du paquet `caddy`.

Elle permet aux utilisateurs de profiter de la configuration par défaut, des fichiers de service systemd et de la complétion bash du paquet officiel.

**Prérequis :**
- Installer le paquet `caddy` selon [ces instructions](/docs/install#debian-ubuntu-raspbian)
- Compiler votre binaire `caddy` personnalisé (voir les sections ci-dessus), ou [télécharger](/download) un build personnalisé
- Votre binaire `caddy` personnalisé doit se trouver dans le répertoire courant

**Procédure :**
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

**Explication :**

- `dpkg-divert` déplace le binaire `/usr/bin/caddy` vers `/usr/bin/caddy.default` et met en place une déviation au cas où un paquet voudrait installer un fichier à cet emplacement.

- `update-alternatives` crée un lien symbolique du binaire caddy souhaité vers `/usr/bin/caddy`.

- `systemctl restart caddy` arrête la version par défaut du serveur Caddy et lance la version personnalisée.

Vous pouvez basculer entre le binaire `caddy` personnalisé et celui par défaut en exécutant la commande ci-dessous et en suivant les informations à l'écran. Redémarrez ensuite le service Caddy.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Pour mettre à jour Caddy par la suite, vous pouvez lancer [`caddy upgrade`](/docs/command-line#caddy-upgrade). Cela tentera de [télécharger](/download) un build avec les mêmes plugins que votre build actuel, dans la dernière version de Caddy, puis remplacera le binaire actuel par le nouveau.
