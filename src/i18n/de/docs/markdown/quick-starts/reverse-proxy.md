---
title: Reverse proxy quick-start
---

<a id="reverse-proxy-quick-start"></a>
# Reverse proxy quick-start

Diese Anleitung zeigt dir, wie du schnell einen produktionsreifen Reverse Proxy mit oder ohne HTTPS einrichtest und startest.

**Voraussetzungen:**
- Grundkenntnisse im Terminal / in der Kommandozeile
- `caddy` in deinem PATH
- Ein laufender Backend-Prozess, zu dem weitergeleitet werden soll

---

Dieses Tutorial geht davon aus, dass ein Backend-HTTP-Dienst unter `127.0.0.1:9000` läuft. Die Befehle sind für Linux, aber dieselben Prinzipien gelten auch für andere Betriebssysteme.

Du kannst einen einfachen Reverse Proxy ohne Konfigurationsdatei starten oder für mehr Flexibilität und Kontrolle eine Konfigurationsdatei verwenden.


<a id="command-line"></a>
## Kommandozeile

Um auf deinem Rechner einen unverschlüsselten HTTP-Proxy von Port 2080 zu Port 9000 zu starten:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Teste ihn dann:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Der [`reverse-proxy`-Befehl](/docs/command-line#reverse-proxy) ist für schnelle und einfache Reverse Proxies gedacht. Du kannst ihn in Produktion verwenden, wenn deine Anforderungen einfach sind.

## Caddyfile

Erstelle im aktuellen Arbeitsverzeichnis eine Datei namens `Caddyfile` mit diesem Inhalt:

```caddy
:2080

reverse_proxy :9000
```

Diese Konfigurationsdatei entspricht grob dem obigen Befehl `caddy reverse-proxy`.

Führe dann aus demselben Verzeichnis aus:

<pre><code class="cmd bash">caddy run</code></pre>

Teste anschließend deinen Proxy:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Wenn du das Caddyfile änderst, stelle sicher, dass du Caddy neu [lädst](/docs/command-line#caddy-reload).

Das war ein einfaches Beispiel. Mit der [`reverse_proxy`-Direktive](/docs/caddyfile/directives/reverse_proxy) kannst du deutlich mehr tun.

<a id="https-from-client-to-proxy"></a>
## HTTPS vom Client zum Proxy

Caddy stellt deinen Proxy [automatisch und standardmäßig über HTTPS](/docs/automatic-https) bereit, wenn er den Hostnamen (Domainnamen) kennt. Der Befehl `caddy reverse-proxy` verwendet standardmäßig `localhost`, wenn du das Flag `--from` weglässt; alternativ kannst du die erste Zeile deines Caddyfile durch den Domainnamen des Proxys ersetzen.

- Wenn du `localhost` oder eine Domain verwendest, die auf `.localhost` endet, nutzt Caddy ein automatisch erneuertes, selbstsigniertes Zertifikat. Beim ersten Mal musst du möglicherweise ein Passwort eingeben, während Caddy versucht, das Root-Zertifikat seiner CA in deinen Trust Store zu installieren.
- Wenn du einen anderen Domainnamen verwendest, versucht Caddy, ein öffentlich vertrauenswürdiges Zertifikat zu erhalten. Stelle sicher, dass deine DNS-Einträge auf deinen Rechner zeigen und dass die Ports 80 und 443 öffentlich erreichbar und an Caddy weitergeleitet sind.

Wenn du keinen Port angibst, verwendet Caddy standardmäßig 443 für HTTPS. In diesem Fall brauchst du außerdem die Berechtigung, an niedrige Ports zu binden. Unter Linux gibt es dafür mehrere Möglichkeiten:

- Als root ausführen, zum Beispiel `sudo -E`.
- Oder `sudo setcap cap_net_bind_service=+ep $(which caddy)` ausführen, um Caddy genau diese Capability zu geben.

Hier ist der einfachste `caddy reverse-proxy`-Befehl, der dir HTTPS gibt:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Teste ihn dann:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Du kannst den Hostnamen mit dem Flag `--from` anpassen:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

Wenn du keine Berechtigung hast, an niedrige Ports zu binden, kannst du von einem höheren Port aus proxien:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Wenn du ein Caddyfile verwendest, ändere einfach die erste Zeile zu deinem Domainnamen, zum Beispiel:

```caddy
example.com

reverse_proxy :9000
```

<a id="https-from-proxy-to-backend"></a>
## HTTPS vom Proxy zum Backend

Caddy kann auch zwischen sich selbst und dem Backend über HTTPS proxien, wenn das Backend TLS unterstützt. Verwende einfach `https://` in der Backend-Adresse:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Dafür muss das Zertifikat des Backends vom System vertrauenswürdig sein, auf dem Caddy läuft. Caddy vertraut selbstsignierten Zertifikaten nicht, sofern dies nicht ausdrücklich konfiguriert ist.

Natürlich kannst du HTTPS auch an beiden Enden verwenden:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

Das stellt HTTPS vom Client zum Proxy und vom Proxy zum Backend bereit.

Wenn der Hostname, zu dem du proxyst, ein anderer ist als der, von dem du proxyst, musst du das Flag `--change-host-header` verwenden:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

Standardmäßig reicht Caddy alle HTTP-Header unverändert weiter, einschließlich `Host`, und Caddy leitet den TLS ServerName aus dem Host-Header ab. `--change-host-header` setzt den Host-Header auf den des Backends zurück, damit der TLS-Handshake erfolgreich abgeschlossen werden kann. Im obigen Beispiel würde er von `example.com` zu `localhost:9000` geändert, und `localhost` würde im TLS-Handshake verwendet.
