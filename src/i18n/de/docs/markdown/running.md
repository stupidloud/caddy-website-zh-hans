---
title: Caddy am Laufen halten
---

<a id="keep-caddy-running"></a>
# Caddy am Laufen halten

Caddy kann zwar direkt über seine [Befehlszeilenschnittstelle](/docs/command-line) ausgeführt werden, aber ein Service Manager bietet zahlreiche Vorteile, etwa automatisches Starten beim Systemneustart und das Erfassen von stdout/stderr-Logs.


- [Linux-Dienst](#linux-service)
  - [Unit-Dateien](#unit-files)
  - [Manuelle Installation](#manual-installation)
  - [Den Dienst verwenden](#using-the-service)
  - [Lokales HTTPS](#local-https-with-systemd)
  - [Overrides](#overrides)
	- [Umgebungsvariablen](#environment-variables)
	- [`run`- und `reload`-Override](#run-and-reload-override)
	- [Neustart bei Crash](#restart-on-crash)
  - [SELinux-Hinweise](#selinux-considerations)
- [Windows-Dienst](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Einrichtung](#setup)
  - [Nutzung](#usage)
  - [Lokales HTTPS](#local-https-with-docker)


<a id="linux-service"></a>
## Linux-Dienst

Die empfohlene Methode, Caddy auf Linux-Distributionen mit systemd auszuführen, sind unsere offiziellen systemd-Unit-Dateien.


<a id="unit-files"></a>
### Unit-Dateien

Wir stellen zwei verschiedene systemd-Unit-Dateien bereit, zwischen denen du je nach Anwendungsfall wählen kannst:

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service), wenn du Caddy mit einem [Caddyfile](/docs/caddyfile) konfigurierst. Wenn du lieber einen anderen config adapter oder eine JSON-config-Datei verwendest, kannst du die Befehle `ExecStart` und `ExecReload` [überschreiben](#overrides).

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service), wenn du Caddy ausschließlich über seine [API](/docs/api) konfigurierst. Dieser Dienst verwendet die Option [`--resume`](/docs/command-line#caddy-run), wodurch Caddy mit der `autosave.json` startet, die standardmäßig [persistiert](/docs/json/admin/config/) wird.

Sie sind sehr ähnlich, unterscheiden sich aber in den Befehlen `ExecStart` und `ExecReload`, um die jeweiligen Workflows zu unterstützen.

Wenn du zwischen den Diensten wechseln musst, solltest du den vorherigen Dienst deaktivieren und stoppen, bevor du den anderen aktivierst und startest. Zum Beispiel, um vom Dienst `caddy` zum Dienst `caddy-api` zu wechseln:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### Manuelle Installation

Einige [Installationsmethoden](/docs/install) richten Caddy automatisch als Dienst ein. Wenn du eine Methode gewählt hast, die das nicht tut, kannst du diesen Anweisungen folgen:

**Anforderungen:**

- `caddy`-Binary, das du [heruntergeladen](/download) oder [aus dem Quellcode gebaut](/docs/build) hast
- `systemctl --version` 232 oder neuer
- `sudo`-Rechte

Verschiebe das caddy-Binary in deinen `$PATH`, zum Beispiel:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Teste, ob es funktioniert hat:
<pre><code class="cmd bash">caddy version</code></pre>

Erstelle eine Gruppe namens `caddy`:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Erstelle einen Benutzer namens `caddy` mit einem beschreibbaren Home-Verzeichnis:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Wenn du eine config-Datei verwendest, stelle sicher, dass sie für den gerade erstellten Benutzer `caddy` lesbar ist.

Wähle als Nächstes eine [systemd-Unit-Datei](#unit-files) passend zu deinem Anwendungsfall.

**Prüfe die Direktiven `ExecStart` und `ExecReload` sorgfältig.** Stelle sicher, dass der Pfad zum Binary und die Kommandozeilenargumente zu deiner Installation passen. Wenn du zum Beispiel eine config-Datei verwendest, ändere den `--config`-Pfad, falls er von den Standardwerten abweicht.

Der übliche Speicherort für die Service-Datei ist: `/etc/systemd/system/caddy.service`

Nachdem du die Service-Datei gespeichert hast, kannst du den Dienst zum ersten Mal mit dem üblichen systemctl-Ablauf starten:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Prüfe, dass er läuft:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Jetzt kannst du [den Dienst verwenden](#using-the-service).



<a id="using-the-service"></a>
### Den Dienst verwenden

Wenn du ein Caddyfile verwendest, kannst du deine Konfiguration mit `nano`, `vi` oder deinem bevorzugten Editor bearbeiten:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Du kannst deine statischen Site-Dateien entweder in `/var/www/html` oder in `/srv` ablegen. Stelle sicher, dass der Benutzer `caddy` Leserechte für die Dateien hat.

Um zu prüfen, ob der Dienst läuft:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
Der Statusbefehl zeigt auch den Speicherort der aktuell laufenden Service-Datei an.

Wenn Caddy mit unserer offiziellen Service-Datei läuft, wird Caddys Ausgabe zu `journalctl` umgeleitet. Um deine vollständigen Logs zu lesen und abgeschnittene Zeilen zu vermeiden:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Wenn du eine config-Datei verwendest, kannst du Caddy nach Änderungen graceful neu laden:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Du kannst den Dienst stoppen mit:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Stoppe den Dienst nicht, um Caddys Konfiguration zu ändern. Das Stoppen des Servers verursacht Downtime. Verwende stattdessen den reload-Befehl.

</aside>

Der Caddy-Prozess läuft als Benutzer `caddy`, dessen `$HOME` auf `/var/lib/caddy` gesetzt ist. Das bedeutet:
- Der standardmäßige [Datenspeicherort](/docs/conventions#data-directory) (für Zertifikate und andere Zustandsinformationen) liegt in `/var/lib/caddy/.local/share/caddy`.
- Der standardmäßige [config-Speicherort](/docs/conventions#configuration-directory) (für die automatisch gespeicherte JSON-config, hauptsächlich nützlich für den Dienst `caddy-api`) liegt in `/var/lib/caddy/.config/caddy`.


<a id="local-https-with-systemd"></a>
### Lokales HTTPS mit systemd

Wenn du Caddy für lokale Entwicklung mit HTTPS verwendest, nutzt du vielleicht einen [Hostnamen](/docs/caddyfile/concepts#addresses) wie `localhost` oder `app.localhost`. Das aktiviert [Local HTTPS](/docs/automatic-https#local-https), bei dem Caddys lokale CA Zertifikate ausstellt.

Da Caddy als Benutzer `caddy` läuft, wenn es als Dienst ausgeführt wird, hat es keine Berechtigung, sein Root-CA-Zertifikat im Trust Store des Systems zu installieren. Führe dafür [`sudo caddy trust`](/docs/command-line#caddy-trust) aus, um die Installation vorzunehmen.

Wenn andere Geräte sich mit deinem Server verbinden sollen, während du den [`internal` issuer](/docs/caddyfile/directives/tls#internal) verwendest, musst du das Root-CA-Zertifikat auch auf diesen Geräten installieren. Du findest das Root-CA-Zertifikat unter `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. Viele Webbrowser verwenden inzwischen ihren eigenen Trust Store (und ignorieren den Trust Store des Systems), sodass du das Zertifikat möglicherweise auch dort manuell installieren musst.


<a id="overrides"></a>
### Overrides

Der beste Weg, Aspekte der Service-Dateien zu überschreiben, ist dieser Befehl:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Dadurch öffnet sich eine leere Datei in deinem Standard-Terminaleditor, in der du Direktiven der Unit-Definition überschreiben oder ergänzen kannst. Das wird eine "drop-in"-Datei genannt.

<a id="environment-variables"></a>
#### Umgebungsvariablen

Wenn du Umgebungsvariablen für deine config definieren musst, kannst du das so tun:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

Wenn du die Umgebungsvariablen lieber in einer separaten Datei pflegst (envfile), kannst du die Direktive [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) so verwenden:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Dann kann deine Datei `/etc/caddy/.env` so aussehen (verwende keine `"`-Anführungszeichen um die Werte):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### `run`- und `reload`-Override

Wenn du die config-Datei vom Standard-Caddyfile auf eine JSON-Datei ändern musst (beachte, dass `Exec*`-Direktiven [zuerst mit leeren Strings zurückgesetzt werden müssen](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=), bevor ein neuer Wert gesetzt wird):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### Neustart bei Crash

Wenn Caddy sich nach 5s selbst neu starten soll, falls es unerwartet crasht:
```systemd
[Service]
# Automatically restart caddy if it crashes except if the exit code was 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Speichere die Datei, verlasse den Texteditor und starte den Dienst neu, damit die Änderung wirksam wird:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### SELinux-Hinweise

Auf Systemen mit aktiviertem SELinux hast du zwei Optionen:
1. Installiere Caddy über das [COPR-Repo](/docs/install#fedora-redhat-centos). Deine systemd-Datei und dein caddy-Binary werden bereits korrekt erstellt und gelabelt (du kannst diesen Abschnitt dann ignorieren). Wenn du einen eigenen Caddy-Build verwenden willst, musst du die ausführbare Datei wie unten beschrieben labeln.

2. [Lade Caddy von dieser Site herunter](/download) oder kompiliere es mit [`xcaddy`](https://github.com/caddyserver/xcaddy). In beiden Fällen musst du die Dateien selbst labeln.

Systemd-Unit-Dateien und ihre ausführbaren Dateien werden nur ausgeführt, wenn sie mit `systemd_unit_file_t` beziehungsweise `bin_t` gelabelt sind.

Das Label `systemd_unit_file_t` wird automatisch auf Dateien angewendet, die in `/etc/systemd/...` erstellt werden; lege deine `caddy.service`-Datei daher dort an, wie in den Anweisungen zur [manuellen Installation](#manual-installation) beschrieben.

Um das `caddy`-Binary zu taggen, kannst du folgenden Befehl verwenden:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Windows-Dienst

Es gibt zwei Wege, Caddy unter Windows als Dienst auszuführen: [sc.exe](#scexe) oder [WinSW](#winsw).

<a id="scexe"></a>
### sc.exe

Um den Dienst zu erstellen, führe aus:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

(ersetze `YOURPATH` durch den tatsächlichen Pfad zu deiner `caddy.exe`)

Starten:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Stoppen:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


<a id="winsw"></a>
### WinSW

Installiere Caddy mit diesen Anweisungen als Dienst unter Windows.

**Anforderungen:**

- `caddy.exe`-Binary, das du [heruntergeladen](/download) oder [aus dem Quellcode gebaut](/docs/build) hast
- Eine beliebige `.exe` aus dem neuesten Release des
  [WinSW](https://github.com/winsw/winsw/releases/latest)-Service-Wrappers (die folgende Service-config ist für v2.x-Releases geschrieben)

Lege alle Dateien in ein Dienstverzeichnis. In den folgenden Beispielen verwenden wir `C:\caddy`.

Benenne die Datei `WinSW-x64.exe` in `caddy-service.exe` um.

Füge im selben Verzeichnis eine `caddy-service.xml` hinzu:

```xml
<service>
  <id>caddy</id>
  <!-- Display name of the service -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Service description -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

Du kannst den Dienst jetzt installieren mit:
<pre><code class="cmd bash">caddy-service install</code></pre>

Vielleicht möchtest du die Windows Services Console öffnen, um zu sehen, ob der Dienst korrekt läuft:
<pre><code class="cmd bash">services.msc</code></pre>

Beachte, dass Windows-Dienste nicht neu geladen werden können; du musst Caddy daher direkt zum Reload anweisen:
<pre><code class="cmd bash">caddy reload</code></pre>

Ein Neustart ist über die normalen Windows-Dienstbefehle möglich, zum Beispiel über den Tab "Services" im Task Manager.

Zur Anpassung des Service-Wrappers siehe die [WinSW-Dokumentation](https://github.com/winsw/winsw/tree/master#usage)


<a id="docker-compose"></a>
## Docker Compose

Der einfachste Weg, mit Docker loszulegen, ist Docker Compose. Weitere Details zum offiziellen Caddy-Docker-Image findest du in der Dokumentation auf [Docker Hub](https://hub.docker.com/_/caddy).

<aside class="tip">

Dies setzt voraus, dass du [Docker Compose V2](https://docs.docker.com/compose/reference/) verwendest, bei dem der Befehl jetzt `docker compose` (mit Leerzeichen) heißt, statt `docker-compose` (mit Bindestrich) wie in V1.

</aside>

<a id="setup"></a>
### Einrichtung

Erstelle zuerst eine Datei `compose.yml` (oder füge diesen Dienst zu deiner bestehenden Datei hinzu):

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

Ersetze `<version>` durch die neueste Versionsnummer, die du auf [Docker Hub](https://hub.docker.com/_/caddy) im Abschnitt "Tags" findest.

Was das tut:

- Verwendet die Restart-Policy `unless-stopped`, damit der Caddy-Container automatisch neu gestartet wird, wenn deine Maschine rebootet.
- Bindet an die Ports `80` und `443` für HTTP beziehungsweise HTTPS, plus `443/udp` für HTTP/3.
- Bind-mountet das Verzeichnis `conf`, das deine Caddyfile-Konfiguration enthält.
- Bind-mountet das Verzeichnis `site`, um statische Dateien deiner Site aus `/srv` auszuliefern.
- Named volumes für `/data` und `/config`, um [wichtige Informationen zu persistieren](/docs/conventions#file-locations).

Erstelle dann eine Datei namens `Caddyfile` als einzige Datei im Verzeichnis `conf` und schreibe deine [Caddyfile](/docs/caddyfile/concepts)-config.

Wenn du statische Dateien ausliefern willst, kannst du sie in einem Verzeichnis `site/` neben den configs ablegen und dann [`root`](/docs/caddyfile/directives/root) mit `root /srv` setzen. Wenn nicht, kannst du den `/srv`-Volume-Mount entfernen.

<aside class="tip">

Wenn du Caddy verwendest, um per [reverse proxy](/docs/caddyfile/directives/reverse_proxy) zu einem anderen Container zu leiten, denke daran: In Docker-Netzwerken bedeutet `localhost` "dieser Container", nicht "diese Maschine". Verwende zum Beispiel nicht `reverse_proxy localhost:8080`, sondern `reverse_proxy other-container:8080`.

</aside>

Wenn du einen eigenen Caddy-Build mit Plugins brauchst, folge den [Docker-Build-Anweisungen](/docs/build#docker), um ein eigenes Docker-Image zu erstellen. Erstelle das `Dockerfile` neben deiner `compose.yml` und ersetze dann die Zeile `image:` in deiner `compose.yml` durch `build: .`.



<a id="usage"></a>
### Nutzung

Dann kannst du den Container starten:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Um Caddy nach Änderungen an deinem Caddyfile neu zu laden:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Seit v2.11.0 kannst du mit `SIGUSR1` neu laden, sofern Caddy mit `caddy run` und einer config-Datei gestartet wurde:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Um Caddys 1000 neueste Logs zu sehen und mit `f` neue Einträge live zu verfolgen:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### Lokales HTTPS mit Docker

Wenn du Docker für lokale Entwicklung mit HTTPS verwendest, nutzt du vielleicht einen [Hostnamen](/docs/caddyfile/concepts#addresses) wie `localhost` oder `app.localhost`. Das aktiviert [Local HTTPS](/docs/automatic-https#local-https), bei dem Caddys lokale CA Zertifikate ausstellt. Das bedeutet, dass HTTP-Clients außerhalb des Containers dem von Caddy ausgelieferten TLS-Zertifikat nicht vertrauen. Um das zu lösen, kannst du Caddys Root-CA-Zertifikat im Trust Store deiner Host-Maschine installieren:

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

Viele Webbrowser verwenden inzwischen ihren eigenen Trust Store (und ignorieren den Trust Store des Systems), sodass du das Zertifikat möglicherweise auch dort manuell installieren musst, indem du die oben aus dem Container kopierte Datei `root.crt` verwendest.

- Für Firefox: Gehe zu Preferences > Privacy & Security > Certificates > View Certificates > Authorities > Import und wähle die Datei `root.crt` aus.

- Für Chrome: Gehe zu Settings > Privacy and security > Security > Manage certificates > Authorities > Import und wähle die Datei `root.crt` aus.
