---
title: "Erste Schritte"
---

<a id="getting-started"></a>
# Erste Schritte

Willkommen bei Caddy! Dieses Tutorial erklärt die Grundlagen der Nutzung von Caddy und hilft dir, dich auf hohem Niveau damit vertraut zu machen.

**Ziele:**
- 🔲 Daemon ausführen
- 🔲 API ausprobieren
- 🔲 Caddy eine config geben
- 🔲 config testen
- 🔲 Caddyfile erstellen
- 🔲 config adapter verwenden
- 🔲 Mit einer Anfangs-config starten
- 🔲 JSON und Caddyfile vergleichen
- 🔲 API und config-Dateien vergleichen
- 🔲 Im Hintergrund ausführen
- 🔲 Config-Reload ohne Downtime

**Voraussetzungen:**
- Grundkenntnisse im Terminal / auf der Kommandozeile
- Grundkenntnisse mit einem Texteditor
- `caddy` und `curl` in deinem `PATH`

---

**Wenn du [Caddy installiert](/docs/install) hast, etwa über einen Paketmanager, läuft Caddy möglicherweise bereits als Dienst. Falls ja, stoppe bitte den Dienst, bevor du dieses Tutorial machst.**

Beginnen wir damit, Caddy auszuführen:

<pre><code class="cmd bash">caddy</code></pre>

Ups; ohne Unterbefehl zeigt der Befehl `caddy` nur Hilfetext an. Das kannst du jederzeit nutzen, wenn du vergessen hast, was zu tun ist.

Um Caddy als Daemon zu starten, verwende den Unterbefehl `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Daemon ausführen</aside>

Dieser Befehl blockiert dauerhaft, aber was tut er? Im Moment ... nichts. Standardmäßig ist Caddys Konfiguration ("config") leer. Das können wir in einem anderen Terminal über die [Admin-API](/docs/api) prüfen:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

Das ist **nicht** deine Website: Der Administrations-Endpunkt auf localhost:2019 wird zur Steuerung von Caddy verwendet und ist standardmäßig auf localhost beschränkt.

</aside>


<aside class="complete">API ausprobieren</aside>

Wir können Caddy nützlich machen, indem wir ihm eine config geben. Das geht auf viele Arten; im nächsten Abschnitt beginnen wir mit einem POST-Request an den [/load](/docs/api#post-load)-Endpunkt mit `curl`.



<a id="your-first-config"></a>
## Deine erste config

Zur Vorbereitung unseres Requests brauchen wir eine config. Im Kern ist Caddys Konfiguration einfach ein [JSON-Dokument](/docs/json/).

Speichere dies in einer JSON-Datei (z. B. `caddy.json`):

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

<aside class="tip">

Du musst keine config-Dateien verwenden, aber für dieses Tutorial tun wir es. Caddys [Admin-API](/docs/api) ist für die Nutzung durch andere Programme oder Skripte entworfen.

</aside>


Dann lade sie hoch:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Caddy eine config geben</aside>

Wir können mit einem weiteren GET-Request prüfen, dass Caddy unsere neue config angewendet hat:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Teste, ob sie funktioniert, indem du [localhost:2015](http://localhost:2015) im Browser öffnest oder `curl` verwendest:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Wenn du *Hello, world!* siehst, funktioniert es. Es ist immer sinnvoll zu prüfen, dass deine config wie erwartet arbeitet, besonders bevor du sie in Produktion einsetzt.

<aside class="complete">config testen</aside>


<a id="your-first-caddyfile"></a>
## Dein erstes Caddyfile

Das war *ziemlich viel Arbeit* nur für Hello World.

Eine andere Möglichkeit, Caddy zu konfigurieren, ist das [**Caddyfile**](/docs/caddyfile). Dieselbe config, die wir oben in JSON geschrieben haben, lässt sich einfach so ausdrücken:

```caddy
:2015

respond "Hello, world!"
```


Speichere das in einer Datei namens `Caddyfile` (ohne Erweiterung) im aktuellen Verzeichnis.

<aside class="complete">Caddyfile erstellen</aside>

Stoppe Caddy, falls es bereits läuft (<kbd>Ctrl</kbd>+<kbd>C</kbd>), und führe dann aus:

<pre><code class="cmd bash">caddy adapt</code></pre>

Oder, falls dein Caddyfile anderswo liegt oder anders heißt als `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

Du wirst JSON-Ausgabe sehen. Was ist passiert?

Wir haben gerade einen [_config adapter_](/docs/config-adapters) verwendet, um unser Caddyfile in Caddys native JSON-Struktur zu konvertieren.

<aside class="complete">config adapter verwenden</aside>

Wir könnten diese Ausgabe nehmen und einen weiteren API-Request machen, aber wir können all diese Schritte überspringen, weil der Befehl `caddy` das für uns erledigen kann. Wenn im aktuellen Verzeichnis eine Datei namens Caddyfile liegt und keine andere config angegeben ist, lädt Caddy das Caddyfile, adaptiert es für uns und führt es sofort aus.

Da es nun ein Caddyfile im aktuellen Ordner gibt, führen wir wieder `caddy run` aus:

<pre><code class="cmd bash">caddy run</code></pre>

Oder, falls dein Caddyfile anderswo liegt:

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

(Wenn es anders heißt und nicht mit "Caddyfile" beginnt, musst du `--adapter caddyfile` angeben.)

Du kannst deine Site jetzt erneut laden und wirst sehen, dass sie funktioniert.

<aside class="complete">Mit einer Anfangs-config starten</aside>

Wie du siehst, gibt es mehrere Wege, Caddy mit einer Anfangs-config zu starten:

- Eine Datei namens Caddyfile im aktuellen Verzeichnis
- Das `--config`-Flag (optional mit dem `--adapter`-Flag)
- Das `--resume`-Flag (wenn zuvor eine config geladen wurde)


<a id="json-vs-caddyfile"></a>
## JSON vs. Caddyfile

Jetzt weißt du, dass das Caddyfile für dich zu JSON konvertiert wird.

Das Caddyfile wirkt einfacher als JSON, aber solltest du es immer verwenden? Beide Ansätze haben Vor- und Nachteile. Die Antwort hängt von deinen Anforderungen und deinem Anwendungsfall ab.

JSON | Caddyfile
-----|----------
Leicht zu generieren | Leicht von Hand zu schreiben
Leicht programmierbar | Umständlich zu automatisieren
Extrem ausdrucksstark | Mäßig ausdrucksstark
Voller Umfang der Caddy-Funktionalität | Größter Teil der Caddy-Funktionalität
Erlaubt config traversal | Kein Traversal innerhalb des Caddyfile
Teilweise config-Änderungen | Nur Änderungen der ganzen config
Kann exportiert werden | Kann nicht exportiert werden
Kompatibel mit allen API-Endpunkten | Kompatibel mit einigen API-Endpunkten
Dokumentation automatisch generiert | Dokumentation von Hand geschrieben
Allgegenwärtig | Nische
Effizienter | Rechenintensiver
Etwas langweilig | Etwas spaßig
**Mehr erfahren: [JSON-Struktur](/docs/json/)** | **Mehr erfahren: [Caddyfile-Dokumentation](/docs/caddyfile)**

Du musst entscheiden, was am besten zu deinem Anwendungsfall passt.

Wichtig ist, dass sowohl JSON als auch das Caddyfile (und [jeder andere unterstützte config adapter](/docs/config-adapters)) mit [Caddys API](/docs/api) verwendet werden können. Den vollen Umfang von Caddys Funktionalität und API-Features bekommst du jedoch, wenn du JSON verwendest. Wenn du einen config adapter nutzt, kannst du die config über die API nur über den [/load-Endpunkt](/docs/api#post-load) laden oder ändern.

<aside class="complete">JSON und Caddyfile vergleichen</aside>


<a id="api-vs-config-files"></a>
## API vs. config-Dateien

<aside class="tip">

Unter der Haube laufen sogar config-Dateien über Caddys API-Endpunkte; der Befehl `caddy` verpackt diese API-Aufrufe nur für dich.

</aside>


Du solltest außerdem entscheiden, ob dein Workflow API-basiert oder CLI-basiert ist. (Du *kannst* API und config-Dateien auf demselben Server verwenden, aber wir empfehlen es nicht: Am besten gibt es eine einzige Quelle der Wahrheit.)

API | Config files
----|-------------
Config-Änderungen mit HTTP-Requests vornehmen | Config-Änderungen mit Shell-Befehlen vornehmen
Leicht zu skalieren | Schwer zu skalieren
Schwer von Hand zu verwalten | Leicht von Hand zu verwalten
Wirklich spaßig | Auch spaßig
**Mehr erfahren: [API-Tutorial](/docs/api-tutorial)** | **Mehr erfahren: [Caddyfile-Tutorial](/docs/caddyfile-tutorial)**

<aside class="tip">
	Die manuelle Verwaltung der Serverkonfiguration über die API ist mit passenden Werkzeugen durchaus machbar, zum Beispiel mit jeder REST-Client-Anwendung.
</aside>

Die Wahl zwischen API- oder config-Datei-Workflow ist unabhängig von der Nutzung von config adapters: Du kannst JSON verwenden, es aber in einer Datei speichern und über die Kommandozeile nutzen; umgekehrt kannst du auch das Caddyfile mit der API verwenden.

Die meisten Menschen werden jedoch Kombinationen aus JSON+API oder Caddyfile+CLI verwenden.

Wie du siehst, eignet sich Caddy gut für eine große Vielfalt von Anwendungsfällen und Deployments.

<aside class="complete">API und config-Dateien vergleichen</aside>



<a id="start-stop-run"></a>
## Start, stop, run

Da Caddy ein Server ist, läuft er unbegrenzt. Das bedeutet, dass dein Terminal nach `caddy run` nicht wieder freigegeben wird, bis der Prozess beendet wird (normalerweise mit <kbd>Ctrl</kbd>+<kbd>C</kbd>).

Obwohl `caddy run` am häufigsten ist und meist empfohlen wird (besonders beim Erstellen eines Systemdienstes), kannst du alternativ `caddy start` verwenden, um Caddy zu starten und im Hintergrund laufen zu lassen:

<pre><code class="cmd bash">caddy start</code></pre>

Das gibt dir dein Terminal zurück, was in manchen interaktiven headless-Umgebungen praktisch ist.

Du musst den Prozess dann selbst stoppen, da <kbd>Ctrl</kbd>+<kbd>C</kbd> ihn nicht für dich stoppt:

<pre><code class="cmd bash">caddy stop</code></pre>

Oder verwende den [/stop-Endpunkt](/docs/api#post-stop) der API.

<aside class="complete">Im Hintergrund ausführen</aside>


<a id="reloading-config"></a>
## config neu laden

Dein Server kann config-Reloads/-Änderungen ohne Downtime durchführen.

Alle [API-Endpunkte](/docs/api), die config laden oder ändern, sind graceful und verursachen keine Downtime.

Bei der Kommandozeile kann es jedoch verlockend sein, den Server mit <kbd>Ctrl</kbd>+<kbd>C</kbd> zu stoppen und dann neu zu starten, um die neue Konfiguration zu übernehmen. Tu das nicht: Server stoppen/starten ist unabhängig von config-Änderungen und führt zu Downtime.

<aside class="tip">
	Das Stoppen deines Servers führt dazu, dass der Server nicht verfügbar ist.
</aside>

Verwende stattdessen den Befehl [`caddy reload`](/docs/command-line#caddy-reload) für eine graceful config-Änderung:

<pre><code class="cmd bash">caddy reload</code></pre>

Das nutzt unter der Haube eigentlich nur die API. Der Befehl lädt deine config-Datei, passt sie bei Bedarf zu JSON an und ersetzt dann die aktive Konfiguration graceful ohne Downtime.

Wenn beim Laden der neuen config Fehler auftreten, rollt Caddy auf die letzte funktionierende config zurück.

<aside class="tip">
	Technisch wird die neue config gestartet, bevor die alte config gestoppt wird; für kurze Zeit laufen also beide configs. Wenn die neue config fehlschlägt, bricht sie mit einem Fehler ab, während die alte einfach nicht gestoppt wird.
</aside>

<aside class="complete">Config-Reload ohne Downtime</aside>
