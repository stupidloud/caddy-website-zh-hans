---
title: "API-Tutorial"
---

<a id="api-tutorial"></a>
# API-Tutorial

Dieses Tutorial zeigt dir, wie du Caddys [Admin-API](/docs/api) verwendest, mit der Automatisierung programmierbar möglich wird.

**Ziele:**
- 🔲 Daemon ausführen
- 🔲 Caddy eine config geben
- 🔲 config testen
- 🔲 Aktive config ersetzen
- 🔲 config durchlaufen
- 🔲 `@id`-Tags verwenden

**Voraussetzungen:**
- Grundkenntnisse im Terminal / auf der Kommandozeile
- Grundkenntnisse in JSON
- `caddy` und `curl` in deinem `PATH`

---

Um den Caddy-Daemon zu starten, verwende den Unterbefehl `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Daemon ausführen</aside>

Dieser Befehl blockiert dauerhaft, aber was tut er? Im Moment ... nichts. Standardmäßig ist Caddys Konfiguration ("config") leer. Das können wir in einem anderen Terminal über die [Admin-API](/docs/api) prüfen:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Wir können Caddy nützlich machen, indem wir ihm eine config geben. Eine Möglichkeit ist ein POST-Request an den [/load](/docs/api#post-load)-Endpunkt. Wie bei jedem HTTP-Request gibt es viele Wege dafür; in diesem Tutorial verwenden wir `curl`.

<a id="your-first-config"></a>
## Deine erste config

Zur Vorbereitung unseres Requests brauchen wir eine config. Caddys Konfiguration ist einfach ein [JSON-Dokument](/docs/json/) (oder [etwas, das zu JSON konvertiert wird](/docs/config-adapters)).

<aside class="tip">
	Config-Dateien sind nicht erforderlich. Die Konfigurations-API kann immer ohne Dateien verwendet werden, was für Automatisierung praktisch ist. Dieses Tutorial verwendet eine Datei, weil sie von Hand bequemer zu bearbeiten ist.
</aside>

Speichere dies in einer JSON-Datei:

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Dann lade sie hoch:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Vergiss das @ vor deinem Dateinamen nicht; es sagt curl, dass du eine Datei sendest.
</aside>

<aside class="complete">Caddy eine config geben</aside>

Wir können mit einem weiteren GET-Request prüfen, dass Caddy unsere neue config angewendet hat:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Teste, ob sie funktioniert, indem du [localhost:2015](http://localhost:2015) im Browser öffnest oder `curl` verwendest:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">config testen</aside>

Wenn du *Hello, world!* siehst, funktioniert es. Es ist immer sinnvoll zu prüfen, dass deine config wie erwartet arbeitet, besonders bevor du sie in Produktion einsetzt.

Ändern wir unsere Begrüßung von "Hello world!" zu etwas Motivierenderem: "I can do hard things." Ändere deine config-Datei so, dass das handler-Objekt jetzt so aussieht:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

Speichere die config-Datei und aktualisiere Caddys aktive Konfiguration, indem du denselben POST-Request erneut ausführst:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Aktive config ersetzen</aside>

Prüfe zur Sicherheit, dass die config aktualisiert wurde:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Teste es, indem du die Seite im Browser aktualisierst (oder `curl` erneut ausführst); du wirst eine inspirierende Nachricht sehen.


<a id="config-traversal"></a>
## Config traversal

Anstatt für eine kleine Änderung die gesamte config-Datei hochzuladen, nutzen wir ein mächtiges Feature von Caddys API, um die Änderung vorzunehmen, ohne die config-Datei zu berühren.

<aside class="tip">
	Kleine Änderungen an Produktionsservern vorzunehmen, indem man wie oben die gesamte config ersetzt, kann gefährlich sein; es ähnelt Root-Zugriff auf ein Dateisystem. Caddys API erlaubt dir, den Umfang deiner Änderungen zu begrenzen, sodass andere Teile deiner config garantiert nicht versehentlich geändert werden.
</aside>

Über den Pfad der Request-URI können wir in die config-Struktur hinein navigieren und nur den Nachrichten-String aktualisieren (bei abgeschnittenem Text nach rechts scrollen):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

Jedes Mal, wenn du die config über die API änderst, persistiert Caddy eine Kopie der neuen config, sodass du sie später mit [**--resume**](/docs/command-line#caddy-run) wieder aufnehmen kannst.

</aside>


Du kannst mit einem ähnlichen GET-Request prüfen, ob es funktioniert hat, zum Beispiel:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Du solltest Folgendes sehen:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

Du kannst den Befehl [`jq` <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) verwenden, um JSON-Ausgabe schöner zu formatieren: **`curl ... | jq`**

</aside>


<aside class="complete">config durchlaufen</aside>

**Wichtiger Hinweis:** Das sollte offensichtlich sein, aber sobald du über die API eine Änderung machst, die nicht in deiner ursprünglichen config-Datei steht, ist deine config-Datei veraltet. Es gibt mehrere Wege, damit umzugehen:

- Verwende `--resume` des Befehls [caddy run](/docs/command-line#caddy-run), um die zuletzt aktive config zu nutzen.
- Vermische config-Dateien nicht mit Änderungen über die API; nutze eine einzige Quelle der Wahrheit.
- [Exportiere Caddys neue Konfiguration](/docs/api#get-configpath) mit einem anschließenden GET-Request (weniger empfohlen als die ersten beiden Optionen).



<a id="using-id-in-json"></a>
## `@id` in JSON verwenden

Config traversal ist sicher nützlich, aber die Pfade sind etwas lang, oder?

Wir können unserem handler-Objekt ein [`@id`-Tag](/docs/api#using-id-in-json) geben, damit es leichter erreichbar ist:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Das fügt unserem handler-Objekt eine Eigenschaft hinzu: `"@id": "msg"`; es sieht nun so aus:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

**@id**-Tags können in jedem Objekt stehen und beliebige primitive Werte haben (meist einen String). [Mehr erfahren](/docs/api#using-id-in-json)

</aside>


Dann können wir direkt darauf zugreifen:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

Und jetzt können wir die Nachricht mit einem kürzeren Pfad ändern:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

Und sie erneut prüfen:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete"><code>@id</code>-Tags verwenden</aside>
