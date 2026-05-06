---
title: Maintenir Caddy en exécution
---

# Maintenir Caddy en exécution

Bien que Caddy puisse être lancé directement via son [interface en ligne de commande](/docs/command-line), l'utilisation d'un gestionnaire de services présente de nombreux avantages, comme assurer son démarrage automatique au redémarrage du système et capturer les journaux stdout/stderr.


- [Service Linux](#linux-service)
  - [Fichiers d'unité (Unit Files)](#unit-files)
  - [Installation manuelle](#manual-installation)
  - [Utilisation du service](#using-the-service)
  - [HTTPS local](#local-https-with-systemd)
  - [Surcharges (Overrides)](#overrides)
	- [Variables d'environnement](#environment-variables)
	- [Surcharge de `run` et `reload`](#run-and-reload-override)
	- [Redémarrage après crash](#restart-on-crash)
  - [Considérations SELinux](#selinux-considerations)
- [Service Windows](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Installation](#setup)
  - [Utilisation](#usage)
  - [HTTPS local](#local-https-with-docker)


<a id="linux-service"></a>
## Service Linux

La méthode recommandée pour faire tourner Caddy sur les distributions Linux disposant de systemd est d'utiliser nos fichiers d'unité systemd officiels.


<a id="unit-files"></a>
### Fichiers d'unité (Unit Files)

Nous fournissons deux fichiers d'unité systemd différents, à choisir selon votre cas d'utilisation :

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service) si vous configurez Caddy avec un [Caddyfile](/docs/caddyfile). Si vous préférez utiliser un autre adaptateur de configuration ou un fichier JSON, vous pouvez [surcharger](#overrides) les commandes `ExecStart` et `ExecReload`.

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service) si vous configurez Caddy uniquement via son [API](/docs/api). Ce service utilise l'option [`--resume`](/docs/command-line#caddy-run) qui démarrera Caddy en utilisant le fichier `autosave.json` [persisté](/docs/json/admin/config/) par défaut.

Ils sont très similaires mais diffèrent dans les commandes `ExecStart` et `ExecReload` pour s'adapter aux flux de travail respectifs.

Si vous devez basculer entre les deux services, vous devriez désactiver et arrêter le précédent avant d'activer et démarrer l'autre. Par exemple, pour passer du service `caddy` au service `caddy-api` :
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### Installation manuelle

Certaines [méthodes d'installation](/docs/install) configurent automatiquement Caddy comme un service. Si ce n'est pas le cas de la méthode que vous avez choisie, vous pouvez suivre ces instructions :

**Prérequis :**

- Le binaire `caddy` que vous avez [téléchargé](/download) ou [compilé](/docs/build)
- `systemctl --version` 232 ou plus récent
- Privilèges `sudo`

Déplacez le binaire caddy dans votre `$PATH`, par exemple :
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Vérifiez que cela fonctionne :
<pre><code class="cmd bash">caddy version</code></pre>

Créez un groupe nommé `caddy` :
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Créez un utilisateur nommé `caddy` avec un répertoire personnel (home) accessible en écriture :
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Si vous utilisez un fichier de configuration, assurez-vous qu'il soit lisible par l'utilisateur `caddy` que vous venez de créer.

Ensuite, [choisissez un fichier d'unité systemd](#unit-files) selon votre cas.

**Vérifiez bien les directives `ExecStart` et `ExecReload`.** Assurez-vous que l'emplacement du binaire et les arguments de ligne de commande sont corrects pour votre installation ! Par exemple : si vous utilisez un fichier de configuration, modifiez le chemin `--config` s'il diffère des valeurs par défaut.

L'emplacement habituel pour sauvegarder le fichier de service est : `/etc/systemd/system/caddy.service`

Après avoir sauvegardé votre fichier de service, vous pouvez démarrer le service pour la première fois avec les commandes systemctl habituelles :

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Vérifiez qu'il tourne :
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Vous êtes maintenant prêt à [utiliser le service](#using-the-service) !



<a id="using-the-service"></a>
### Utilisation du service

Si vous utilisez un Caddyfile, vous pouvez éditer votre configuration avec `nano`, `vi` ou votre éditeur préféré :
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Vous pouvez placer les fichiers de votre site statique dans `/var/www/html` ou `/srv`. Assurez-vous que l'utilisateur `caddy` a la permission de lire les fichiers.

Pour vérifier que le service fonctionne :
<pre><code class="cmd bash">systemctl status caddy</code></pre>
La commande status affichera également l'emplacement du fichier de service actuellement utilisé.

Lors de l'utilisation de notre fichier de service officiel, la sortie de Caddy est redirigée vers `journalctl`. Pour lire l'intégralité de vos journaux et éviter que les lignes ne soient tronquées :
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Si vous utilisez un fichier de configuration, vous pouvez recharger Caddy proprement après toute modification :
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Vous pouvez arrêter le service avec :
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

N'arrêtez pas le service pour changer la configuration de Caddy. Arrêter le serveur provoquera une interruption de service. Utilisez plutôt la commande reload.

</aside>

Le processus Caddy tournera en tant qu'utilisateur `caddy`, dont le `$HOME` est défini sur `/var/lib/caddy`. Cela signifie que :
- L'[emplacement de stockage des données](/docs/conventions#data-directory) par défaut (pour les certificats et autres informations d'état) sera `/var/lib/caddy/.local/share/caddy`.
- L'[emplacement de stockage de la configuration](/docs/conventions#configuration-directory) par défaut (pour le JSON sauvegardé automatiquement, principalement utile pour le service `caddy-api`) sera `/var/lib/caddy/.config/caddy`.


<a id="local-https-with-systemd"></a>
### HTTPS local avec systemd

Lors de l'utilisation de Caddy pour du développement local avec HTTPS, vous pourriez utiliser un [nom d'hôte](/docs/caddyfile/concepts#addresses) comme `localhost` ou `app.localhost`. Cela active le [HTTPS local](/docs/automatic-https#local-https) en utilisant la CA locale de Caddy pour émettre des certificats. 

Comme Caddy tourne en tant qu'utilisateur `caddy` lorsqu'il est lancé en tant que service, il n'aura pas la permission d'installer son certificat CA racine dans le magasin de confiance du système. Pour ce faire, lancez [`sudo caddy trust`](/docs/command-line#caddy-trust) pour effectuer l'installation.

Si vous voulez que d'autres appareils se connectent à votre serveur lors de l'utilisation de l'émetteur [`internal`](/docs/caddyfile/directives/tls#internal), vous devrez également installer le certificat CA racine sur ces appareils. Vous trouverez le certificat CA racine dans `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. De nombreux navigateurs web utilisent désormais leur propre magasin de confiance (ignorant celui du système), vous devrez donc peut-être y installer le certificat manuellement également.


<a id="overrides"></a>
### Surcharges (Overrides)

Le meilleur moyen de surcharger des aspects des fichiers de service est d'utiliser cette commande :
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Cela ouvrira un fichier vide dans votre éditeur de texte par défaut, dans lequel vous pourrez surcharger ou ajouter des directives à la définition de l'unité. C'est ce qu'on appelle un fichier "drop-in".

<a id="environment-variables"></a>
#### Variables d'environnement

Si vous avez besoin de définir des variables d'environnement pour votre configuration, vous pouvez le faire ainsi :
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

De même, si vous préférez conserver les variables d'environnement dans un fichier séparé (envfile), vous pouvez utiliser la directive [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) :
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Votre fichier `/etc/caddy/.env` pourrait alors ressembler à ceci (ne pas utiliser de guillemets `"` autour des valeurs) :

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### Surcharge de `run` et `reload`

Si vous devez changer le fichier de configuration par défaut (Caddyfile) pour utiliser un fichier JSON à la place (notez que les directives `Exec*` [doivent être réinitialisées avec des chaînes vides](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=) avant de définir une nouvelle valeur) :
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### Redémarrage après crash

Si vous voulez que Caddy se redémarre automatiquement après 5s s'il crash de manière inattendue :
```systemd
[Service]
# Redémarrer automatiquement Caddy s'il crash, sauf si le code de sortie est 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Enregistrez ensuite le fichier, quittez l'éditeur et redémarrez le service pour appliquer les changements :
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### Considérations SELinux

Sur les systèmes où SELinux est activé, vous avez deux options :
1. Installer Caddy via le [dépôt COPR](/docs/install#fedora-redhat-centos). Votre fichier systemd et le binaire caddy seront déjà créés et étiquetés (labellisés) correctement (vous pouvez donc ignorer cette section). Si vous souhaitez utiliser un build personnalisé de Caddy, vous devrez étiqueter l'exécutable comme décrit ci-dessous.

2. [Télécharger Caddy depuis ce site](/download) ou le compiler avec [`xcaddy`](https://github.com/caddyserver/xcaddy). Dans les deux cas, vous devrez étiqueter les fichiers vous-même.

Les fichiers d'unité systemd et leurs exécutables ne seront pas lancés s'ils ne sont pas étiquetés respectivement avec `systemd_unit_file_t` et `bin_t`.

L'étiquette `systemd_unit_file_t` est automatiquement appliquée aux fichiers créés dans `/etc/systemd/...`, assurez-vous donc de créer votre fichier `caddy.service` à cet endroit, conformément aux instructions d'[installation manuelle](#manual-installation).

Pour étiqueter le binaire `caddy`, vous pouvez utiliser la commande suivante :
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Service Windows

Il existe deux façons de faire tourner Caddy en tant que service sous Windows : [sc.exe](#scexe) ou [WinSW](#winsw).

<a id="scexe"></a>
### sc.exe

Pour créer le service, lancez :

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "VOTRECHEMIN\caddy.exe run"</code></pre>

(remplacez `VOTRECHEMIN` par le chemin réel vers votre `caddy.exe`)

Pour démarrer :

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Pour arrêter :

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


<a id="winsw"></a>
### WinSW

Installez Caddy en tant que service sous Windows en suivant ces instructions.

**Prérequis :**

- Le binaire `caddy.exe` que vous avez [téléchargé](/download) ou [compilé](/docs/build)
- N'importe quel `.exe` provenant de la dernière release du wrapper de service [WinSW](https://github.com/winsw/winsw/releases/latest) (la configuration de service ci-dessous est écrite pour les versions v2.x)

Placez tous les fichiers dans un répertoire de service. Dans les exemples suivants, nous utilisons `C:\caddy`.

Renommez le fichier `WinSW-x64.exe` en `caddy-service.exe`.

Ajoutez un fichier `caddy-service.xml` dans le même répertoire :

```xml
<service>
  <id>caddy</id>
  <!-- Nom d'affichage du service -->
  <name>Caddy Web Server (propulsé par WinSW)</name>
  <!-- Description du service -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

Vous pouvez maintenant installer le service en utilisant :
<pre><code class="cmd bash">caddy-service install</code></pre>

Vous pouvez ouvrir la Console des Services Windows pour vérifier si le service tourne correctement :
<pre><code class="cmd bash">services.msc</code></pre>

Sachez que les services Windows ne peuvent pas être rechargés (reload), vous devez donc dire directement à Caddy de se recharger :
<pre><code class="cmd bash">caddy reload</code></pre>

Le redémarrage est possible via les commandes habituelles des services Windows, par exemple via l'onglet "Services" du Gestionnaire des tâches.

Pour personnaliser le wrapper de service, consultez la [documentation de WinSW](https://github.com/winsw/winsw/tree/master#usage).


<a id="docker-compose"></a>
## Docker Compose

La manière la plus simple de démarrer avec Docker est d'utiliser Docker Compose. Consultez la documentation sur le [Docker Hub](https://hub.docker.com/_/caddy) pour plus de détails sur l'image Docker officielle de Caddy.

<aside class="tip">

Ceci suppose que vous utilisez [Docker Compose V2](https://docs.docker.com/compose/reference/), où la commande est désormais `docker compose` (espace) au lieu de `docker-compose` (tiret) pour la V1.

</aside>

<a id="setup"></a>
### Installation

Tout d'abord, créez un fichier `compose.yml` (ou ajoutez ce service à votre fichier existant) :

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Assurez-vous de remplacer `<version>` par le numéro de la dernière version, que vous trouverez sur le [Docker Hub](https://hub.docker.com/_/caddy) sous la section "Tags".

Ce que cela fait :

- Utilise la politique de redémarrage `unless-stopped` pour s'assurer que le conteneur Caddy redémarre automatiquement au redémarrage de votre machine.
- Lie les ports `80` et `443` pour le HTTP et le HTTPS respectivement, plus le `443/udp` pour le HTTP/3.
- Lie et monte le répertoire `conf` qui contient votre configuration Caddyfile.
- Lie et monte le répertoire `site` pour servir les fichiers statiques de votre site depuis `/srv`.
- Utilise des volumes nommés pour `/data` et `/config` afin de [persister les informations importantes](/docs/conventions#file-locations).

Ensuite, créez un fichier nommé `Caddyfile` comme seul fichier dans le répertoire `conf`, et écrivez votre configuration [Caddyfile](/docs/caddyfile/concepts).

Si vous avez des fichiers statiques à servir, vous pouvez les placer dans un répertoire `site/` à côté des configurations, puis définir la racine via [`root`](/docs/caddyfile/directives/root) avec `root /srv`. Sinon, vous pouvez supprimer le montage du volume `/srv`.

<aside class="tip">

Si vous utilisez Caddy comme [proxy inverse](/docs/caddyfile/directives/reverse_proxy) vers un autre conteneur, rappelez-vous que dans le réseau Docker, `localhost` signifie "ce conteneur", pas "cette machine". Ainsi, n'utilisez pas `reverse_proxy localhost:8080`, mais plutôt `reverse_proxy autre-conteneur:8080`.

</aside>

Si vous avez besoin d'un build personnalisé de Caddy with plugins, follow the [Docker build instructions](/docs/build#docker) to create a custom Docker image. Create the `Dockerfile` beside your `compose.yml`, then replace the `image:` line in your `compose.yml` with `build: .` instead.



<a id="usage"></a>
### Utilisation

Ensuite, vous pouvez lancer le conteneur :
<pre><code class="cmd bash">docker compose up -d</code></pre>

Pour recharger Caddy après avoir modifié votre Caddyfile :
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Depuis la v2.11.0, vous pouvez recharger en utilisant `SIGUSR1`, à condition que Caddy ait été lancé avec `caddy run` et un fichier de configuration :
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Pour voir les 1000 derniers journaux de Caddy, et utiliser `-f` pour voir les nouveaux arriver en flux continu :
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### HTTPS local avec Docker

Lors de l'utilisation de Docker pour du développement local avec HTTPS, vous pourriez utiliser un [nom d'hôte](/docs/caddyfile/concepts#addresses) comme `localhost` ou `app.localhost`. Cela active le [HTTPS local](/docs/automatic-https#local-https) en utilisant la CA locale de Caddy pour émettre des certificats. Cela signifie que les clients HTTP à l'extérieur du conteneur ne feront pas confiance au certificat TLS servi par Caddy. Pour résoudre cela, vous pouvez installer le certificat CA racine de Caddy dans le magasin de confiance de votre machine hôte :

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

De nombreux navigateurs web utilisent désormais leur propre magasin de confiance (ignorant celui du système), vous devrez donc peut-être y installer le certificat manuellement également, en utilisant le fichier `root.crt` copié depuis le conteneur dans la commande ci-dessus.

- Pour Firefox, allez dans Préférences > Vie privée et sécurité > Certificats > Afficher les certificats > Autorités > Importer, et sélectionnez le fichier `root.crt`.

- Pour Chrome, allez dans Paramètres > Confidentialité et sécurité > Sécurité > Gérer les certificats > Autorités > Importer, et sélectionnez le fichier `root.crt`.
