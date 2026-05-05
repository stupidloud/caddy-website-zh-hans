---
title: HTTPS quick-start
---

<a id="https-quick-start"></a>
# HTTPS quick-start

Diese Anleitung zeigt dir, wie du in kürzester Zeit mit [vollständig verwaltetem HTTPS](/docs/automatic-https) startest.

<aside class="tip">
	Caddy verwendet standardmäßig HTTPS für alle Websites, sofern in der Konfiguration ein Hostname angegeben ist. Dieses Tutorial geht davon aus, dass du eine öffentlich vertrauenswürdige Website, also nicht „localhost“, über HTTPS bereitstellen möchtest. Deshalb verwenden wir einen öffentlichen Domainnamen und externe Ports.
</aside>

**Voraussetzungen:**
- Grundkenntnisse im Terminal / in der Kommandozeile
- Grundverständnis von DNS
- Ein registrierter öffentlicher Domainname
- Externer Zugriff auf die Ports 80 und 443
- `caddy` und `curl` in deinem PATH

---

Ersetze in diesem Tutorial `example.com` durch deinen tatsächlichen Domainnamen.

Setze die A/AAAA-Einträge deiner Domain so, dass sie auf deinen Server zeigen. Das kannst du tun, indem du dich bei deinem DNS-Anbieter anmeldest und deinen Domainnamen verwaltest.

Bevor du fortfährst, prüfe die korrekten Einträge mit einer autoritativen Abfrage. Ersetze `example.com` durch deinen Domainnamen; wenn du IPv6 verwendest, ersetze `type=A` durch `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

Stelle außerdem sicher, dass dein Server von einer öffentlichen Schnittstelle aus auf den Ports 80 und 443 extern erreichbar ist.

<aside class="tip">
	Wenn du dich in deinem Heimnetzwerk oder einem anderen eingeschränkten Netzwerk befindest, musst du möglicherweise Ports weiterleiten oder Firewall-Einstellungen anpassen.
</aside>

Alles, was wir tun müssen, ist Caddy mit deinem Domainnamen in der Konfiguration zu starten. Dafür gibt es mehrere Wege.

## Caddyfile

Das ist der gängigste Weg, HTTPS zu erhalten.

Erstelle eine Datei namens `Caddyfile` ohne Endung, deren erste Zeile dein Domainname ist, zum Beispiel:

```caddy
example.com

respond "Hello, privacy!"
```

Führe dann aus demselben Verzeichnis aus:

<pre><code class="cmd bash">caddy run</code></pre>

Du wirst sehen, wie Caddy ein TLS-Zertifikat bereitstellt und deine Website über HTTPS ausliefert. Das war möglich, weil die Website-Adresse im Caddyfile einen Domainnamen enthielt.


<a id="the-file-server-command"></a>
## Der `file-server`-Befehl

Wenn du nur statische Dateien über HTTPS bereitstellen musst, führe diesen Befehl aus und ersetze dabei deinen Domainnamen:

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Du wirst sehen, wie Caddy ein TLS-Zertifikat bereitstellt und deine Website über HTTPS ausliefert.


<a id="the-reverse-proxy-command"></a>
## Der `reverse-proxy`-Befehl

Wenn du nur einen einfachen Reverse Proxy über HTTPS brauchst, also als TLS-Terminierung, führe diesen Befehl aus und ersetze dabei deinen Domainnamen sowie die tatsächliche Backend-Adresse:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Du wirst sehen, wie Caddy ein TLS-Zertifikat bereitstellt und deine Website über HTTPS ausliefert.


<a id="json-config"></a>
## JSON-Konfiguration

Als Faustregel gilt: Jeder [host matcher](/docs/json/apps/http/servers/routes/match/host/) löst automatisches HTTPS aus.

Eine JSON-Konfiguration wie die folgende aktiviert daher produktionsreifes [automatic HTTPS](/docs/automatic-https):

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
