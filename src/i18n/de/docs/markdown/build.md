---
title: "Aus Quellcode bauen"
---

<a id="build-from-source"></a>
# Aus Quellcode bauen

Es gibt mehrere Möglichkeiten, Caddy zu bauen, wenn du einen angepassten Build brauchst, zum Beispiel mit Plugins:
- [Git](#git): Aus dem Git-Repository bauen
- [`xcaddy`](#xcaddy): Mit `xcaddy` bauen
- [Docker](#docker): Ein eigenes Docker-Image bauen

Anforderungen:

- [Go](https://golang.org/doc/install) 1.20 oder neuer

Der Abschnitt [Package support files](#package-support-files-for-custom-builds-for-debianubunturaspbian) enthält Anweisungen für Benutzer, die Caddy mit dem APT-Befehl auf einem Debian-abgeleiteten System installiert haben, aber für ihren Betrieb eine angepasste ausführbare Datei benötigen.



## Git

Anforderungen:

- Go installiert (siehe oben)

Klone das Repository:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Wenn du kein git hast, kannst du den Quellcode als Archivdatei [von GitHub](https://github.com/caddyserver/caddy) herunterladen. Jede [Release](https://github.com/caddyserver/caddy/releases) enthält außerdem Quellcode-Snapshots.

Bauen:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

Wegen [eines Bugs in Go](https://github.com/golang/go/issues/29228) betten diese einfachen Schritte keine Versionsinformationen ein. Wenn du die Version brauchst (`caddy version`), musst du Caddy als Abhängigkeit und nicht als Hauptmodul kompilieren. Anweisungen dazu stehen in Caddys Datei [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go). Alternativ kannst du [`xcaddy`](#xcaddy) verwenden, das dies automatisiert.

</aside>

Go-Programme lassen sich leicht für andere Plattformen kompilieren. Setze einfach die abweichenden Umgebungsvariablen `GOOS`, `GOARCH` und/oder `GOARM`. ([Details stehen in der Go-Dokumentation.](https://golang.org/doc/install/source#environment))

Um Caddy zum Beispiel für Windows zu kompilieren, obwohl du nicht auf Windows bist:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

Oder entsprechend für Linux ARMv6, wenn du nicht auf Linux oder nicht auf ARMv6 bist:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## xcaddy

Der [`xcaddy`-Befehl](https://github.com/caddyserver/xcaddy) ist der einfachste Weg, Caddy mit Versionsinformationen und/oder Plugins zu bauen.

Anforderungen:

- Go installiert (siehe oben)
- Stelle sicher, dass [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) in deinem `PATH` liegt

Du musst den Caddy-Quellcode **nicht** herunterladen; `xcaddy` erledigt das für dich.

Dann ist das Bauen von Caddy mit Versionsinformationen so einfach wie:

<pre><code class="cmd bash">xcaddy build</code></pre>

Um mit Plugins zu bauen, verwende `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Wie du siehst, kannst du die Versionen von Plugins mit der `@`-Syntax anpassen. Versionen können ein Tag-Name, ein Commit-SHA oder ein Branch sein.

Plattformübergreifende Kompilierung mit `xcaddy` funktioniert genauso wie mit dem `go`-Befehl. Um zum Beispiel für macOS zu cross-kompilieren:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## Docker

Du kannst das `:builder`-Image als Abkürzung verwenden, um ein neues Caddy-Binary mit eigenen Modulen zu bauen:

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

Ersetze `<version>` zum Einstieg unbedingt durch die neueste Version von Caddy.

Beachte die zweite `FROM`-Anweisung: Sie erzeugt ein deutlich kleineres Image, indem das neu gebaute Binary einfach über das reguläre `caddy`-Image gelegt wird.

Der Builder verwendet `xcaddy`, um Caddy mit den angegebenen Modulen zu bauen, ähnlich wie im oben [beschriebenen Prozess](#xcaddy). Die Optionen `--mount=type=cache,target=/go/pkg/mod` und `--mount=type=cache,target=/root/.cache/go-build` werden verwendet, um die Go-Modulabhängigkeiten beziehungsweise Build-Artefakte zu cachen, was nachfolgende Builds beschleunigt. Das Flag ist [ein Feature von Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), nicht von `xcaddy`.

Wenn du Docker Compose verwenden möchtest, siehe unser empfohlenes [`compose.yml`](/docs/running#docker-compose) und die Nutzungshinweise.



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Package support files für Custom Builds für Debian/Ubuntu/Raspbian

Dieses Verfahren soll das Ausführen eigener `caddy`-Binaries vereinfachen, während die Support-Dateien aus dem `caddy`-Paket erhalten bleiben.

Es ermöglicht Benutzern, die Standardkonfiguration, systemd-Service-Dateien und bash-completion aus dem offiziellen Paket weiter zu nutzen.

Anforderungen:
- Installiere das Paket `caddy` gemäß [diesen Anweisungen](/docs/install#debian-ubuntu-raspbian)
- Baue dein eigenes `caddy`-Binary (siehe die Abschnitte oben) oder [lade](/download) einen Custom Build herunter
- Dein eigenes `caddy`-Binary sollte sich im aktuellen Verzeichnis befinden

Vorgehen:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

Erklärung:

- `dpkg-divert` verschiebt das Binary `/usr/bin/caddy` nach `/usr/bin/caddy.default` und richtet eine Umleitung ein, falls ein Paket später eine Datei an diesem Ort installieren möchte.

- `update-alternatives` erstellt einen Symlink vom gewünschten Caddy-Binary nach `/usr/bin/caddy`.

- `systemctl restart caddy` fährt die Standardversion des Caddy-Servers herunter und startet die angepasste Version.

Du kannst zwischen dem eigenen und dem Standard-`caddy`-Binary wechseln, indem du den folgenden Befehl ausführst und den Informationen auf dem Bildschirm folgst. Starte danach den Caddy-Service neu.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Um Caddy ab diesem Punkt zu aktualisieren, kannst du [`caddy upgrade`](/docs/command-line#caddy-upgrade) ausführen. Der Befehl versucht, einen Build mit denselben Plugins wie dein aktueller Build und der neuesten Caddy-Version [herunterzuladen](/download), und ersetzt dann das aktuelle Binary durch das neue.
