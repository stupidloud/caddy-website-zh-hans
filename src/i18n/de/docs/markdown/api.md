---
title: "API"
---

# API

Caddy wird über einen Administrations-Endpunkt konfiguriert, der per HTTP über eine [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer)-API erreichbar ist. Du kannst [diesen Endpunkt](/docs/json/admin/) in deiner Caddy-config konfigurieren.

**Standardadresse: `localhost:2019`**

Die Standardadresse kann durch Setzen der Umgebungsvariable `CADDY_ADMIN` geändert werden. Manche Installationsmethoden setzen sie möglicherweise anders. Die Adresse in der Caddy-config hat immer Vorrang vor dem Standard.

<aside class="tip">
	Wenn du nicht vertrauenswürdigen Code auf deinem Server ausführst, stelle sicher, dass du deinen Admin-Endpunkt schützt: isoliere Prozesse, patche verwundbare Programme und konfiguriere den Endpunkt so, dass er stattdessen an einen berechtigten Unix-Socket bindet.
</aside>

Die neueste Konfiguration wird nach jeder Änderung auf Festplatte gespeichert (sofern nicht [deaktiviert](/docs/json/admin/config/)). Du kannst die zuletzt funktionierende config nach einem Neustart mit [`caddy run --resume`](/docs/command-line#caddy-run) wieder aufnehmen; das gewährleistet config-Dauerhaftigkeit bei Stromausfällen oder Ähnlichem.

Zum Einstieg in die API probiere unser [API-Tutorial](/docs/api-tutorial) oder, wenn du nur eine Minute hast, unseren [API-Schnellstart](/docs/quick-starts/api).

---

- **[POST /load](#post-load)**
  Setzt oder ersetzt die aktive Konfiguration

- **[POST /stop](#post-stop)**
  Stoppt die aktive Konfiguration und beendet den Prozess

- **[GET /config/[path]](#get-configpath)**
  Exportiert die config am benannten Pfad

- **[POST /config/[path]](#post-configpath)**
  Setzt oder ersetzt ein Objekt; hängt an ein Array an
  
- **[PUT /config/[path]](#put-configpath)**
  Erstellt ein neues Objekt; fügt in ein Array ein

- **[PATCH /config/[path]](#patch-configpath)**
  Ersetzt ein vorhandenes Objekt oder Array-Element

- **[DELETE /config/[path]](#delete-configpath)**
  Löscht den Wert am benannten Pfad

- **[`@id` in JSON verwenden](#using-id-in-json)**
  Einfach in die config-Struktur hinein navigieren

- **[Gleichzeitige config-Änderungen](#concurrent-config-changes)**
  Kollisionen bei unsynchronisierten config-Änderungen vermeiden

- **[POST /adapt](#post-adapt)**
  Passt eine Konfiguration zu JSON an, ohne sie auszuführen

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Gibt Informationen über eine bestimmte CA der [PKI-App](/docs/json/apps/pki/) zurück

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Gibt die Zertifikatskette einer bestimmten CA der [PKI-App](/docs/json/apps/pki/) zurück

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Gibt den aktuellen Status der konfigurierten Proxy-upstreams zurück


<a id="post-load"></a>
## POST /load

Setzt Caddys Konfiguration und überschreibt jede vorherige Konfiguration. Der Request blockiert, bis der Reload abgeschlossen ist oder fehlschlägt. Konfigurationsänderungen sind leichtgewichtig, effizient und verursachen keine Downtime. Wenn die neue config aus irgendeinem Grund fehlschlägt, wird die alte config ohne Downtime wiederhergestellt.

Dieser Endpunkt unterstützt verschiedene config-Formate über config adapters. Der Content-Type-Header des Requests gibt an, welches config-Format im Request-Body verwendet wird. Normalerweise sollte dies `application/json` sein, Caddys natives config-Format. Für ein anderes config-Format gib den passenden Content-Type an, sodass der Wert nach dem Schrägstrich `/` der Name des zu verwendenden config adapters ist. Beim Senden eines Caddyfile verwende zum Beispiel `text/caddyfile`; für JSON 5 etwa `application/json5`; usw.

Wenn die neue config identisch mit der aktuellen ist, findet kein Reload statt. Um einen Reload zu erzwingen, setze `Cache-Control: must-revalidate` in den Request-Headern.

### Beispiele

Eine neue aktive Konfiguration setzen:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Hinweis: Das `-d`-Flag von curl entfernt Zeilenumbrüche. Wenn dein config-Format empfindlich auf Zeilenumbrüche reagiert (z. B. das Caddyfile), verwende stattdessen `--data-binary`:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="post-stop"></a>
## POST /stop

Fährt den Server sauber herunter und beendet den Prozess. Um nur die laufende Konfiguration zu stoppen, ohne den Prozess zu beenden, verwende [DELETE /config/](#delete-configpath).

### Beispiel

Den Prozess stoppen:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


<a id="get-configpath"></a>
## GET /config/[path]

Exportiert Caddys aktuelle Konfiguration am benannten Pfad. Gibt einen JSON-Body zurück.

### Beispiele

Die gesamte config exportieren und hübsch formatieren:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

Nur die Listener-Adressen exportieren:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



<a id="post-configpath"></a>
## POST /config/[path]

Ändert Caddys Konfiguration am benannten Pfad zum JSON-Body des Requests. Wenn der Zielwert ein Array ist, hängt POST an; wenn er ein Objekt ist, erstellt oder ersetzt POST.

Als Sonderfall können viele Elemente zu einem Array hinzugefügt werden, wenn:

1. der Pfad mit `/...` endet
2. das Pfadelement vor `/...` auf ein Array verweist
3. die Payload ein Array ist

In diesem Fall werden die Elemente im Payload-Array expandiert und einzeln an das Ziel-Array angehängt. In Go-Begriffen hätte das denselben Effekt wie:

```go
baseSlice = append(baseSlice, newElems...)
```

### Beispiele

Eine Listener-Adresse hinzufügen:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Mehrere Listener-Adressen hinzufügen:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

<a id="put-configpath"></a>
## PUT /config/[path]

Ändert Caddys Konfiguration am benannten Pfad zum JSON-Body des Requests. Wenn der Zielwert eine Position (Index) in einem Array ist, fügt PUT ein; wenn er ein Objekt ist, erstellt PUT strikt einen neuen Wert.

### Beispiel

Eine Listener-Adresse an erster Stelle hinzufügen:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


<a id="patch-configpath"></a>
## PATCH /config/[path]

Ändert Caddys Konfiguration am benannten Pfad zum JSON-Body des Requests. PATCH ersetzt strikt einen vorhandenen Wert oder ein Array-Element.

### Beispiel

Die Listener-Adressen ersetzen:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



<a id="delete-configpath"></a>
## DELETE /config/[path]

Entfernt Caddys Konfiguration am benannten Pfad. DELETE löscht den Zielwert.

### Beispiele

Die gesamte aktuelle Konfiguration entladen, den Prozess aber weiterlaufen lassen:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Nur einen deiner HTTP-Server stoppen:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## `@id` in JSON verwenden

Du kannst IDs in dein JSON-Dokument einbetten, um leichter direkt auf diese Teile des JSON zuzugreifen.

Füge einem Objekt einfach ein Feld namens `"@id"` hinzu und gib ihm einen eindeutigen Namen. Wenn du zum Beispiel einen reverse proxy handler hast, auf den du häufig zugreifen möchtest:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Um ihn zu verwenden, stelle einfach einen Request an den `/id/`-API-Endpunkt, genauso wie an den entsprechenden `/config/`-Endpunkt, aber ohne den vollständigen Pfad. Die ID führt den Request direkt in diesen Bereich der config.

Zum Beispiel wäre der Pfad zum Zugriff auf die upstreams des reverse proxy ohne ID etwa:

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

mit ID wird der Pfad aber:

```
/id/my_proxy/upstreams
```

Das ist deutlich leichter zu merken und von Hand zu schreiben.

<a id="concurrent-config-changes"></a>
## Gleichzeitige config-Änderungen

<aside class="tip">

Dieser Abschnitt gilt für alle `/config/`-Endpunkte. Er ist experimentell und kann sich ändern.

</aside>


Caddys config-API bietet [ACID-Garantien <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) für einzelne Requests, aber Änderungen, die mehr als einen Request betreffen, können zu Kollisionen oder Datenverlust führen, wenn sie nicht richtig synchronisiert werden.

Zum Beispiel könnten zwei Clients gleichzeitig `GET /config/foo` ausführen, innerhalb dieses Bereichs (config path) eine Änderung machen und dann gleichzeitig `POST|PUT|PATCH|DELETE /config/foo/...` aufrufen, um ihre Änderungen anzuwenden. Das kann zu einer Kollision führen: Entweder überschreibt einer den anderen, oder der zweite hinterlässt die config in einem unbeabsichtigten Zustand, weil er auf eine andere Version der config angewendet wurde als die, gegen die er vorbereitet wurde. Der Grund ist, dass die Änderungen nichts voneinander wissen.

Caddys API unterstützt keine Transaktionen über mehrere Requests hinweg, und HTTP ist ein zustandsloses Protokoll. Du kannst jedoch die Header `Etag` und `If-Match` verwenden, um Kollisionen für beliebige Änderungen als eine Art optimistische Nebenläufigkeitskontrolle zu erkennen und zu verhindern. Das ist nützlich, wenn die Möglichkeit besteht, dass du Caddys `/config/...`-Endpunkte gleichzeitig ohne Synchronisierung nutzt. Alle Antworten auf `GET /config/...`-Requests enthalten einen HTTP-Header namens `Etag`, der den Pfad und einen Hash des Inhalts in diesem Bereich enthält (z. B. `Etag: "/config/apps/http/servers 65760b8e"`). Setze einfach den `If-Match`-Header eines mutierenden Requests auf den Wert eines Etag-Headers aus einem vorherigen `GET`-Request.

Der Grundalgorithmus ist:

1. Führe einen `GET`-Request auf einen beliebigen Bereich `S` innerhalb der config aus. Bewahre den `Etag`-Header der Antwort auf.
2. Nimm deine gewünschte Änderung an der zurückgegebenen config vor.
3. Führe einen `POST|PUT|PATCH|DELETE`-Request innerhalb von Bereich `S` aus und setze den `If-Match`-Request-Header auf den gespeicherten `Etag`-Wert.
4. Wenn die Antwort HTTP 412 (Precondition Failed) ist, wiederhole ab Schritt 1 oder gib nach zu vielen Versuchen auf.

Dieser Algorithmus erlaubt sicher mehrere, sich überschneidende Änderungen an Caddys Konfiguration ohne explizite Synchronisierung. Er ist so entworfen, dass gleichzeitige Änderungen an verschiedenen Teilen der config keinen Retry benötigen: Nur Änderungen, die denselben config-Bereich überschneiden, können eine Kollision verursachen und dadurch einen Retry erfordern.


<a id="post-adapt"></a>
## POST /adapt

Passt eine Konfiguration zu Caddy JSON an, ohne sie zu laden oder auszuführen. Bei Erfolg wird das resultierende JSON-Dokument im Response-Body zurückgegeben.

Der Content-Type-Header gibt das Konfigurationsformat auf dieselbe Weise an wie bei [/load](#post-load). Um zum Beispiel ein Caddyfile anzupassen, setze `Content-Type: text/caddyfile`.

Dieser Endpunkt passt jedes Konfigurationsformat an, solange der zugehörige [config adapter](/docs/config-adapters) in deinen Caddy-Build eingebunden ist.

### Beispiele

Ein Caddyfile zu JSON adaptieren:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="get-pkicaltidgt"></a>
## GET /pki/ca/&lt;id&gt;

Gibt Informationen über eine bestimmte CA der [PKI-App](/docs/json/apps/pki/) anhand ihrer ID zurück. Wenn die angeforderte CA-ID der Standard (`local`) ist, wird die CA provisioniert, falls dies noch nicht geschehen ist. Andere CA-IDs geben einen Fehler zurück, wenn sie zuvor nicht provisioniert wurden.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


<a id="get-pkicaltidgtcertificates"></a>
## GET /pki/ca/&lt;id&gt;/certificates

Gibt die Zertifikatskette einer bestimmten CA der [PKI-App](/docs/json/apps/pki/) anhand ihrer ID zurück. Wenn die angeforderte CA-ID der Standard (`local`) ist, wird die CA provisioniert, falls dies noch nicht geschehen ist. Andere CA-IDs geben einen Fehler zurück, wenn sie zuvor nicht provisioniert wurden.

Dieser Endpunkt wird intern vom Befehl [`caddy trust`](/docs/command-line#caddy-trust) verwendet, damit das Root-Zertifikat der CA im Trust Store deines Systems installiert werden kann.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

Gibt den aktuellen Status der konfigurierten reverse proxy upstreams (Backends) als JSON-Dokument zurück.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Jeder Eintrag im JSON-Array ist ein konfigurierter [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/), der im globalen upstream pool gespeichert ist.

- **address** ist die Dial-Adresse des upstream.
- **num_requests** ist die Anzahl aktiver Requests, die gerade vom upstream verarbeitet werden.
- **fails** ist die aktuelle Anzahl gespeicherter fehlgeschlagener Requests, wie durch passive health checks konfiguriert.

Wenn dein Ziel ist, die Verfügbarkeit eines Backends zu bestimmen, musst du relevante Eigenschaften des upstream mit der von dir verwendeten handler-Konfiguration abgleichen. Wenn du zum Beispiel [passive health checks](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) für deine Proxys aktiviert hast, musst du auch die Werte `fails` und `num_requests` berücksichtigen, um zu bestimmen, ob ein upstream als verfügbar gilt: Prüfe, dass die Anzahl `fails` kleiner ist als die konfigurierte maximale Fehleranzahl für deinen Proxy (d. h. [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)) und dass `num_requests` kleiner oder gleich der konfigurierten maximalen Request-Anzahl pro upstream ist (d. h. [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) für den gesamten Proxy oder [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) für einzelne upstreams).
