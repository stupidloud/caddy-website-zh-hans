---
title: "Befehlszeile"
---

<a id="command-line"></a>
# Befehlszeile

Caddy hat eine standardisierte, Unix-artige Befehlszeilenschnittstelle. Die grundlegende Verwendung ist:

```
caddy <command> [<args...>]
```

Die `<carets>` kennzeichnen Parameter, die durch deine Eingaben ersetzt werden.

Die `[brackets]` kennzeichnen optionale Parameter. Die `(brackets)` kennzeichnen erforderliche Parameter.

Die Auslassungspunkte `...` kennzeichnen eine Fortsetzung, also einen oder mehrere Parameter.

Die `--flags` können eine einbuchstabige Kurzform wie `-f` haben.

**Schnellstart: `caddy`, `caddy help` oder `man caddy` (falls installiert)**

---

- **[caddy adapt](#caddy-adapt)**
  Passt ein Konfigurationsdokument an natives JSON an

- **[caddy build-info](#caddy-build-info)**
  Gibt Build-Informationen aus

- **[caddy completion](#caddy-completion)**
  Erzeugt ein Script für Shell-Vervollständigung

- **[caddy environ](#caddy-environ)**
  Gibt die Umgebung aus

- **[caddy file-server](#caddy-file-server)**
  Ein einfacher, aber produktionsreifer Dateiserver

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Hilfsbefehl für den Dateiserver, um die Standardvorlage des Dateibrowsers zu exportieren

- **[caddy fmt](#caddy-fmt)**
  Formatiert ein Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Hasht ein Passwort und gibt base64 aus

- **[caddy help](#caddy-help)**
  Hilfe für caddy-Befehle anzeigen

- **[caddy list-modules](#caddy-list-modules)**
  Listet die installierten Caddy-Module auf

- **[caddy manpage](#caddy-manpage)**
  Erzeugt Manpages

- **[caddy reload](#caddy-reload)**
  Ändert die Konfiguration des laufenden Caddy-Prozesses

- **[caddy respond](#caddy-respond)**
  Ein schneller, sauberer, fest verdrahteter HTTP-Server für Entwicklung und Tests

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Ein einfacher, aber produktionsreifer HTTP(S)-Reverse-Proxy

- **[caddy run](#caddy-run)**
  Startet den Caddy-Prozess im Vordergrund

- **[caddy start](#caddy-start)**
  Startet den Caddy-Prozess im Hintergrund

- **[caddy stop](#caddy-stop)**
  Stoppt den laufenden Caddy-Prozess

- **[caddy storage export](#caddy-storage)**
  Exportiert den Inhalt des konfigurierten Speichers in einen Tarball

- **[caddy storage import](#caddy-storage)**
  Importiert einen zuvor exportierten Tarball in den konfigurierten Speicher

- **[caddy trust](#caddy-trust)**
  Installiert ein Zertifikat in lokale Trust Stores

- **[caddy untrust](#caddy-untrust)**
  Entfernt das Vertrauen in ein Zertifikat aus lokalen Trust Stores

- **[caddy upgrade](#caddy-upgrade)**
  Aktualisiert Caddy auf das neueste Release

- **[caddy add-package](#caddy-add-package)**
  Aktualisiert Caddy auf das neueste Release und fügt zusätzliche Plugins hinzu

- **[caddy remove-package](#caddy-remove-package)**
  Aktualisiert Caddy auf das neueste Release und entfernt einige Plugins

- **[caddy validate](#caddy-validate)**
  Prüft, ob eine Konfigurationsdatei gültig ist

- **[caddy version](#caddy-version)**
  Gibt die Version aus

- **[Signale](#signals)**
  Wie Caddy Signale behandelt

- **[Exit-Codes](#exit-codes)**
  Ausgegeben, wenn der Caddy-Prozess beendet wird

<a id="subcommands"></a>
## Unterbefehle


<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Passt eine Konfiguration an Caddys native JSON-Konfigurationsstruktur an, schreibt die Ausgabe nach stdout, etwaige Warnungen nach stderr, und beendet sich dann.

`--config` ist der Pfad zur Konfigurationsdatei. Wenn es weggelassen wird, wird `Caddyfile` im aktuellen Verzeichnis angenommen, sofern es existiert; andernfalls ist dieses Flag erforderlich. Wenn du stdin statt einer normalen Datei verwenden möchtest, verwende - als Pfad.

`--adapter` gibt den zu verwendenden Konfigurationsadapter an; Standard ist `caddyfile`.

`--pretty` formatiert die Ausgabe mit Einrückung, damit sie für Menschen leichter lesbar ist.

`--validate` lädt und provisioniert die angepasste Konfiguration, um ihre Gültigkeit zu prüfen (startet die Konfiguration aber nicht wirklich).

Beachte, dass eine erfolgreich angepasste Konfiguration trotzdem bei der Validierung fehlschlagen kann. Ein Beispiel dafür ist dieses Caddyfile:

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

Versuche, es anzupassen:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

Das gelingt ohne Fehler. Versuche dann:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

Obwohl dieses Caddyfile fehlerfrei nach JSON angepasst werden kann, existieren die tatsächlichen Zertifikats- und/oder Schlüsseldateien nicht. Deshalb schlägt die Validierung fehl, weil dieser Fehler während der Provisionierungsphase entsteht. Validierung ist daher eine stärkere Fehlerprüfung als bloße Anpassung.

#### Beispiel

Um ein Caddyfile in JSON umzuwandeln, das du leicht lesen und manuell anpassen kannst:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

Gibt von Go bereitgestellte Informationen zum Build aus (Pfad des Hauptmoduls, Paketversionen, Modul-Ersetzungen).




<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Erzeugt Scripts für Shell-Vervollständigung. Damit bekommst du Tab-Vervollständigung oder Autovervollständigung (oder Ähnliches, abhängig von deiner Shell), wenn du `caddy`-Befehle eingibst.

Um Anweisungen zur Installation dieses Scripts in deiner konkreten Shell zu erhalten, führe `caddy help completion` oder `caddy completion -h` aus.



<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

Gibt die Umgebung aus, wie caddy sie sieht, und beendet sich dann. Das kann beim Debuggen von Init-Systemen oder Process-Manager-Units wie systemd nützlich sein.




<a id="caddy-file-server"></a>
### `caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Startet einen einfachen, aber produktionsreifen statischen Dateiserver.

`--root` gibt den Root-Dateipfad an. Standard ist das aktuelle Arbeitsverzeichnis.

`--listen` akzeptiert eine Listener-Adresse. Standard ist `:80`, außer `--domain` wird verwendet; dann ist `:443` der Standard.

`--domain` stellt Dateien nur über diesen Hostnamen bereit, und Caddy versucht, sie über HTTPS auszuliefern. Stelle also bei einem öffentlichen Domainnamen zuerst sicher, dass öffentliches DNS korrekt konfiguriert ist. Der Standardport wird auf 443 geändert.

`--browse` aktiviert Verzeichnislisten, wenn ein Verzeichnis ohne Indexdatei angefordert wird.

`--reveal-symlinks` zeigt in Verzeichnislisten das Ziel symbolischer Links an, wenn `--browse` aktiviert ist.

`--templates` aktiviert Template-Rendering.

`--access-log` aktiviert das Request-/Access-Log.

`--debug` aktiviert ausführliches Logging.

`--file-limit` legt die maximale Anzahl von Dateien fest, die in Verzeichnislisten angezeigt werden. Standard: `10000`. Wenn die Anzahl der Dateien diese Grenze überschreitet, werden nur die ersten N Dateien angezeigt, wobei N die angegebene Grenze ist.

`--no-compress` deaktiviert Komprimierung. Standardmäßig sind Zstandard- und Gzip-Komprimierung aktiviert.

`--precompressed` gibt Encoding-Formate an, nach denen für vorkomprimierte Sidecar-Dateien gesucht wird. Kann für mehrere Formate wiederholt werden. Weitere Informationen findest du in der [file_server-Direktive](/docs/caddyfile/directives/file_server#precompressed).

Dieser Befehl deaktiviert die admin API, damit sich mehrere Instanzen auf einem lokalen Entwicklungsrechner leichter ausführen lassen.


<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Exportiert die Standardvorlage für das Datei-Browsing nach stdout

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Formatiert oder verschönert ein Caddyfile und beendet sich dann. Das Ergebnis wird nach stdout geschrieben, sofern `--overwrite` nicht verwendet wird; der Befehl beendet sich mit Code `1`, wenn es Unterschiede gibt.

`<path>` gibt den Pfad zum Caddyfile an. Bei `-` wird die Eingabe von stdin gelesen. Wird es weggelassen, wird stattdessen eine Datei namens Caddyfile im aktuellen Verzeichnis angenommen.

`--overwrite` sorgt dafür, dass das Ergebnis in die Eingabedatei geschrieben wird, statt im Terminal ausgegeben zu werden. Wenn die Eingabe keine reguläre Datei ist, hat dieses Flag keine Wirkung.

`--diff` vergleicht die Ausgabe mit der Eingabe; abweichende Zeilen werden mit `-` und `+` vorangestellt. Beachte, dass unveränderte Zeilen zur Ausrichtung mit zwei Leerzeichen beginnen und dass dies kein gültiges Patch-Format ist; es ist nur als visuelles Hilfsmittel gedacht.


<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

Bequeme Möglichkeit, ein Klartextpasswort zu hashen. Der resultierende Hash wird nach stdout geschrieben, in einem Format, das direkt in deiner Caddy-Konfiguration verwendbar ist.

`--plaintext`
    Das zu hashende Passwort. Wenn es weggelassen wird, wird es von stdin gelesen.
    Wenn Caddy an ein steuerndes TTY angeschlossen ist, wird die Eingabe nicht ausgegeben.

`--algorithm`
    Wählt den Hashing-Algorithmus aus. Gültige Optionen sind:
      * `argon2id` (für moderne Sicherheit empfohlen)
      * `bcrypt`  (älter, langsamer, konfigurierbarer Cost-Wert, Standard-Cost ist `14`)

bcrypt-spezifische Parameter:

`--bcrypt-cost`
    Legt die bcrypt-Hashing-Schwierigkeit fest. Höhere Werte erhöhen die Sicherheit,
    indem sie die Hash-Berechnung langsamer und CPU-intensiver machen.
    Muss im gültigen Bereich [bcrypt.MinCost, bcrypt.MaxCost] liegen.
    Wenn weggelassen oder ungültig, wird der Standard-Cost verwendet.

Argon2id-spezifische Parameter:

`--argon2id-time`
    Anzahl der auszuführenden Iterationen. Eine Erhöhung macht
    das Hashing langsamer und widerstandsfähiger gegen Brute-Force-Angriffe.

`--argon2id-memory`
    Speichermenge, die während des Hashings verwendet wird.
    Größere Werte erhöhen die Widerstandsfähigkeit gegen GPU-/ASIC-Angriffe.

`--argon2id-threads`
    Anzahl der zu verwendenden CPU-Threads. Auf Mehrkernsystemen erhöhen,
    um das Hashing zu beschleunigen.

`--argon2id-keylen`
    Länge des resultierenden Hashes in Bytes. Längere Schlüssel erhöhen
    die Sicherheit, vergrößern aber den Speicherbedarf leicht.


<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

Gibt CLI-Hilfetext aus, optional für einen bestimmten Unterbefehl, und beendet sich dann.



<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

Gibt die installierten Caddy-Module aus, optional mit Paket- und/oder Versionsinformationen aus den zugehörigen Go-Modulen, und beendet sich dann.

In manchen gescripteten Situationen kann es redundant sein, auch alle Standardmodule auszugeben; mit `--skip-standard` kannst du diese daher aus der Ausgabe auslassen.

`--json` gibt die Modulinformationen im JSON-Format aus, was für programmatische Verarbeitung nützlich sein kann.

HINWEIS: Aufgrund [eines Fehlers in Go](https://github.com/golang/go/issues/29228) sind Versionsinformationen nur verfügbar, wenn Caddy als Abhängigkeit gebaut wird und nicht als Hauptmodul. Verwende [xcaddy](/docs/build#xcaddy), um das zu vereinfachen.



<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Erzeugt Handbuch-/Dokumentationsseiten für Caddy-Befehle und schreibt sie in das Verzeichnis am angegebenen Pfad. Die Ausgabe dieses Befehls kann mit dem `man`-Befehl gelesen werden.

`--directory` (erforderlich) ist der Pfad zu dem Verzeichnis, in das die Manpages geschrieben werden. Es wird erstellt, falls es nicht existiert.

Nach der Erzeugung müssen die Handbuchseiten normalerweise installiert werden. Dieses Verfahren unterscheidet sich je nach Plattform, sieht auf typischen Linux-Systemen aber ungefähr so aus:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Danach kannst du `man caddy` (oder `man caddy-*` für Unterbefehle) ausführen, um die Dokumentation in deinem Terminal zu lesen.

Handbuchseiten sind eine eigene Dokumentation, getrennt von der auf unserer Website. Unsere Website enthält umfassendere Dokumentation, die häufig aktualisiert wird.




<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Gibt der laufenden Caddy-Instanz eine neue Konfiguration. Das hat denselben Effekt wie das POSTen eines Dokuments an den [/load endpoint](/docs/api#post-load), ist aber für einfache Workflows rund um Konfigurationsdateien bequemer. Im Vergleich zu den Befehlen `stop`, `start` und `run` ist dieser einzelne Befehl der korrekte, semantische Weg, die laufende Konfiguration zu ändern bzw. neu zu laden.

Da dieser Befehl die API verwendet, darf der admin endpoint nicht deaktiviert sein.

`--config` ist die anzuwendende Konfigurationsdatei. Bei `-` wird die Konfiguration von stdin gelesen. Wenn nichts angegeben ist, versucht der Befehl eine Datei namens `Caddyfile` im aktuellen Arbeitsverzeichnis zu verwenden und sie, falls vorhanden, mit dem `caddyfile`-Konfigurationsadapter anzupassen; andernfalls ist es ein Fehler, wenn keine Konfigurationsdatei geladen werden kann.

`--adapter` gibt einen zu verwendenden Konfigurationsadapter an, falls nötig. Dieses Flag ist nicht erforderlich, wenn der Dateiname von `--config` mit `Caddyfile` beginnt oder mit `.caddyfile` endet, was den `caddyfile`-Adapter annimmt. Andernfalls ist dieses Flag erforderlich, wenn die angegebene Konfigurationsdatei nicht in Caddys nativem JSON-Format vorliegt.

`--address` muss verwendet werden, wenn der admin endpoint nicht auf der Standardadresse lauscht und wenn sie sich von der Adresse in der angegebenen Konfigurationsdatei unterscheidet.

`--force` erzwingt ein Reload, auch wenn die angegebene Konfiguration identisch mit der bereits laufenden Konfiguration von Caddy ist. Das kann nützlich sein, um Caddy zur erneuten Provisionierung seiner Module zu zwingen, was Nebenwirkungen haben kann, zum Beispiel das erneute Laden manuell geladener TLS-Zertifikate.




<a id="caddy-respond"></a>
### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


Startet einen oder mehrere einfache, fest verdrahtete HTTP-Server, die für Entwicklung, Staging und manche Produktionsfälle nützlich sind. Das kann hilfreich sein, um HTTP-Clients, Scripts oder sogar Load Balancer zu verifizieren oder zu debuggen.

`--status` ist der zurückzugebende HTTP-Statuscode.

`--header` fügt einen HTTP-Header hinzu; das Format `Field: value` wird erwartet. Dieses Flag kann mehrfach verwendet werden.

`--body` gibt den Response Body an. Alternativ kann der Body von stdin gepiped werden.

`--listen` ist die Listener-Adresse, die jede von Caddy erkannte [Netzwerkadresse](/docs/conventions#network-addresses) sein kann und einen Portbereich enthalten darf, um mehrere Server zu starten.

`--debug` aktiviert ausführliches Debug-Logging.

`--access-log` aktiviert Access-/Request-Logging.

Wenn keine Optionen angegeben sind, lauscht dieser Befehl auf einem zufällig verfügbaren Port und beantwortet HTTP-Anfragen mit einer leeren 200-Antwort. Die Listen-Adresse kann mit dem Flag `--listen` angepasst werden und wird immer nach stdout ausgegeben. Wenn die Listen-Adresse einen Portbereich enthält, werden mehrere Server gestartet.

Wenn ein abschließendes, unbenanntes Argument angegeben wird, wird es als Statuscode behandelt (wie das Flag `--status`), wenn es eine dreistellige Zahl ist. Andernfalls wird es als Response Body verwendet (wie das Flag `--body`). Die Flags `--status` und `--body` überschreiben dieses Argument immer.

Ein Body kann auf 3 Arten angegeben werden: als Flag, als abschließendes (und unbenanntes) Argument des Befehls oder über stdin gepiped (wenn Flag und Argument nicht gesetzt sind). Begrenzte [Template-Auswertung](https://pkg.go.dev/text/template) wird für den Body unterstützt, mit den folgenden Variablen:

Variable | Beschreibung
---------|-------------
`.N`       | Servernummer
`.Port`    | Listener-Port
`.Address` | Listener-Adresse


#### Beispiele

Leere 200-Antwort auf einem zufälligen Port:
<pre><code class="cmd bash">caddy respond</code></pre>

HTTP-Antwort mit Body:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Mehrere Server und Templates:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

Eine Wartungsseite hinein-pipen:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




<a id="caddy-reverse-proxy"></a>
### `caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Ein einfacher, aber produktionsreifer Reverse Proxy. Nützlich für schnelle Deployments, Demos und Entwicklung.

Leitet HTTP(S)-Traffic einfach von der Adresse `--from` an die Adresse `--to` weiter. Mehrere `--to`-Adressen können durch Wiederholen des Flags angegeben werden. Mindestens eine `--to`-Adresse ist erforderlich. Die Adresse `--to` darf als Kurzform einen Portbereich enthalten, der zu mehreren Upstreams erweitert wird.

Sofern in den Adressen nichts anderes angegeben ist, wird für die Adresse `--from` HTTPS angenommen, wenn ein Hostname angegeben ist, und für die Adresse `--to` HTTP.

Wenn die Adresse `--from` einen Host oder eine IP enthält, versucht Caddy, den Proxy über HTTPS mit einem Zertifikat bereitzustellen (sofern dies nicht durch das HTTP-Schema oder den Port überschrieben wird).

Beim Bereitstellen von HTTPS:
  - `--disable-redirects` kann verwendet werden, um das Binden an den HTTP-Port zu vermeiden.

  - `--internal-certs` kann verwendet werden, um die Ausstellung von Zertifikaten über die interne CA zu erzwingen, statt zu versuchen, ein öffentliches Zertifikat auszustellen.

Für Proxying:
  - `--header-up` kann verwendet werden, um einen Request Header zu setzen, der an den Upstream gesendet wird.

  - `--header-down` kann verwendet werden, um einen Response Header zu setzen, der zurück an den Client gesendet wird.

  - `--change-host-header` setzt den Host Header der Anfrage auf die Adresse des Upstreams, statt standardmäßig den eingehenden Host Header zu verwenden.

    Dies ist eine Kurzform für `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`

  - `--insecure` deaktiviert die TLS-Verifikation beim Upstream. WARNUNG: DIES DEAKTIVIERT SICHERHEIT, INDEM DAS ZERTIFIKAT DES UPSTREAMS NICHT VERIFIZIERT WIRD.

  - `--debug` aktiviert ausführliches Logging.

Dieser Befehl deaktiviert die admin API, damit sich mehrere Instanzen auf einem lokalen Entwicklungsrechner leichter ausführen lassen.



<a id="caddy-run"></a>
### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Führt Caddy aus und blockiert unbegrenzt; also im "Daemon"-Modus.

`--config` gibt eine initiale Konfigurationsdatei an, die sofort geladen und verwendet wird. Bei `-` wird die Konfiguration von stdin gelesen. Wenn keine Konfiguration angegeben ist, läuft Caddy mit einer leeren Konfiguration und verwendet Standardeinstellungen für die [admin API endpoints](/docs/api), über die neue Konfiguration eingespeist werden kann. Als Sonderfall gilt: Wenn im aktuellen Arbeitsverzeichnis eine Datei namens "Caddyfile" liegt und der `caddyfile`-Konfigurationsadapter eingebunden ist (Standard), wird diese Datei auch ohne Befehlszeilen-Flags geladen und zur Konfiguration von Caddy verwendet.

`--adapter` ist der Name des Konfigurationsadapters, der beim Laden der initialen Konfiguration verwendet werden soll, falls einer benötigt wird. Dieses Flag ist nicht erforderlich, wenn der Dateiname von `--config` mit `Caddyfile` beginnt oder mit `.caddyfile` endet, was den `caddyfile`-Adapter annimmt. Andernfalls ist dieses Flag erforderlich, wenn die angegebene Konfigurationsdatei nicht in Caddys nativem JSON-Format vorliegt. Warnungen werden ins Log geschrieben, aber beachte, dass jede Anpassung ohne Fehler sofort verwendet wird, selbst wenn es Warnungen gibt. Wenn du das Ergebnis der Anpassung zuerst prüfen möchtest, verwende den Unterbefehl [`caddy adapt`](#caddy-adapt).

`--pidfile` schreibt die PID in die angegebene Datei.

`--environ` gibt die Umgebung vor dem Start aus. Das entspricht dem Befehl `caddy environ`, beendet sich nach der Ausgabe aber nicht.

`--envfile` lädt Umgebungsvariablen aus der angegebenen Datei im Format `KEY=VALUE`. Kommentare, die mit `#` beginnen, werden unterstützt; Keys dürfen mit `export` beginnen; Werte dürfen in doppelte Anführungszeichen gesetzt werden (doppelte Anführungszeichen darin können escaped werden); mehrzeilige Werte werden unterstützt.

`--resume` verwendet die zuletzt geladene Konfiguration, die automatisch gespeichert wurde, und überschreibt das Flag `--config` (falls vorhanden). Dieses Flag garantiert Konfigurationsdauerhaftigkeit über Maschinenneustarts oder Prozessneustarts hinweg. Es ist am nützlichsten in [API](/docs/api)-zentrierten Deployments.

`--watch` beobachtet die Konfigurationsdatei und lädt sie automatisch neu, nachdem sie sich geändert hat. ⚠️ Dieses Feature ist nur für lokale Entwicklungsumgebungen gedacht!

<aside class="advice">

Stoppe den Server in Produktion nicht, um die Konfiguration zu ändern! Das führt zu Downtime. (Das sollte offensichtlich sein, aber du wärst überrascht, wie viele Beschwerden wir darüber bekommen.) Verwende stattdessen den Befehl [`caddy reload`](#caddy-reload), oder sende ein `SIGUSR1`-Signal an den Prozess; das hat denselben Effekt wie `caddy reload` mit der aktuell geladenen Konfiguration.

</aside>



<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></code></pre>

Wie [`caddy run`](#caddy-run), aber im Hintergrund. Dieser Befehl blockiert nur, bis der Hintergrundprozess erfolgreich läuft (oder der Start fehlschlägt), und kehrt dann zurück.

Hinweis: Das Flag `--config` unterstützt *nicht* `-`, um die Konfiguration von stdin zu lesen.

Von der Verwendung dieses Befehls mit Systemdiensten oder unter Windows wird abgeraten. Unter Windows bleibt der Kindprozess an das Terminal gebunden; wenn das Fenster geschlossen wird, wird Caddy daher zwangsweise gestoppt, was nicht offensichtlich ist. Ziehe stattdessen in Betracht, Caddy [als Dienst](/docs/running) auszuführen.

Nach dem Start kannst du [`caddy stop`](#caddy-stop) oder den API-Endpunkt [`POST /stop`](/docs/api#post-stop) verwenden, um den Hintergrundprozess zu beenden.



<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

Das Stoppen (und Neustarten) des Servers ist unabhängig von Konfigurationsänderungen. **Verwende den stop-Befehl nicht, um die Konfiguration in Produktion zu ändern, es sei denn, du willst Downtime.** Verwende stattdessen den Befehl [`caddy reload`](#caddy-reload).

</aside>


Stoppt den laufenden Caddy-Prozess (außer dem Prozess des stop-Befehls) geordnet und beendet ihn. Dafür verwendet er den Endpoint [`POST /stop`](/docs/api#post-stop) der admin API, um ein geordnetes Herunterfahren durchzuführen.

Die Adresse dieser Anfrage kann mit dem Flag `--address` angepasst oder aus der angegebenen `--config` übernommen werden, wenn die admin API der laufenden Instanz nicht auf der Standard-Listen-Adresse läuft.

Wenn du die aktuelle Konfiguration stoppen, den Prozess aber nicht beenden möchtest, verwende [`caddy reload`](#caddy-reload) mit einer leeren Konfiguration oder den Endpoint [`DELETE /config/`](/docs/api#delete-configpath).


<a id="caddy-storage"></a>
### `caddy storage`

<i>⚠️ Experimentell</i>

Erlaubt Export und Import des Inhalts von Caddys konfiguriertem Datenspeicher.

Das ist nützlich, wenn du von einem [storage module](/docs/json/storage/) zu einem anderen wechseln musst: aus dem alten exportieren, die Konfiguration aktualisieren und dann in den neuen importieren.

Der folgende Befehl kann verwendet werden, um den Speicher mit alten und neuen Konfigurationen in einem Schritt zwischen verschiedenen Modulen zu kopieren, indem die Ausgabe des export-Befehls in den import-Befehl gepiped wird.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

Bitte beachte: Wenn du [filesystem storage](/docs/conventions#data-directory) verwendest, musst du den export-Befehl als derselbe Benutzer ausführen, unter dem Caddy normalerweise läuft, sonst kann der falsche Speicherort verwendet werden.

Wenn Caddy zum Beispiel als [systemd service](/docs/running#linux-service) läuft, läuft es als Benutzer `caddy`; daher solltest du die export- oder import-Befehle als dieser Benutzer ausführen. Üblicherweise geht das mit `sudo -u caddy <command>`.

</aside>


#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` ist die zu ladende Konfigurationsdatei. Sie ist erforderlich, damit das richtige Speichermodul verbunden wird.

`--output` ist der Dateiname, in den der Tarball geschrieben wird. Bei `-` wird die Ausgabe nach stdout geschrieben.



#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` ist die zu ladende Konfigurationsdatei. Sie ist erforderlich, damit das richtige Speichermodul verbunden wird.

`--input` ist der Dateiname des Tarballs, aus dem gelesen wird. Bei `-` wird die Eingabe von stdin gelesen.


<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Installiert ein Root-Zertifikat für eine von Caddys [PKI app](/docs/json/apps/pki/) verwaltete CA in lokale Trust Stores.

Caddy versucht, seine Root-Zertifikate automatisch in die lokalen Trust Stores zu installieren, wenn sie zum ersten Mal erzeugt werden. Das kann aber fehlschlagen, wenn Caddy nicht die passenden Berechtigungen hat, um in den Trust Store zu schreiben. Dieser Befehl ist nötig, um die Zertifikate vor ihrer Verwendung vorab zu installieren, wenn der Serverprozess als unprivilegierter Benutzer läuft (zum Beispiel über systemd). Auf Unix-Systemen musst du diesen Befehl eventuell mit `sudo` ausführen.

Standardmäßig installiert dieser Befehl das Root-Zertifikat für Caddys Standard-CA (d. h. "local"). Mit dem Flag `--ca` kannst du die ID einer anderen CA angeben.

Dieser Befehl versucht, Caddys [admin API](/docs/api) zu kontaktieren, um das Root-Zertifikat über den Endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates) abzurufen. Du kannst `--address` explizit angeben oder mit dem Flag `--config` die Admin-Adresse aus deiner Konfiguration laden, wenn die admin API der laufenden Instanz nicht auf der Standard-Listen-Adresse läuft.

Du kannst das `caddy`-Binary mit diesem Befehl auch verwenden, um Zertifikate auf anderen Maschinen in deinem Netzwerk zu installieren, wenn die admin API für andere Maschinen zugänglich gemacht wurde -- sei dabei vorsichtig und setze die admin API keinen nicht vertrauenswürdigen Clients aus.


<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Entfernt das Vertrauen in ein Root-Zertifikat aus den lokalen Trust Stores.

Dieser Befehl deinstalliert Vertrauen; er löscht das Root-Zertifikat nicht zwangsläufig vollständig aus Trust Stores. Daher kann wiederholtes Trusten und Untrusten neuer Zertifikate Trust-Datenbanken füllen.

Dieser Befehl löscht oder verändert keine Zertifikatsdateien aus Caddys konfiguriertem Speicher.

Dieser Befehl kann auf eine von zwei Arten verwendet werden:
- Durch Angabe eines direkten Pfads zum Root-Zertifikat, dem mit dem Flag `--cert` nicht mehr vertraut werden soll.
- Durch Abrufen des Root-Zertifikats von der [admin API](/docs/api) über den Endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). Das ist das Standardverhalten, wenn keine Flags angegeben werden.

Wenn die admin API verwendet wird, ist die CA-ID standardmäßig "local". Mit dem Flag `--ca` kannst du die ID einer anderen CA angeben. Du kannst `--address` explizit angeben oder mit dem Flag `--config` die Admin-Adresse aus deiner Konfiguration laden, wenn die admin API der laufenden Instanz nicht auf der Standard-Listen-Adresse läuft.


<a id="caddy-upgrade"></a>
### `caddy upgrade`

<i>⚠️ Experimentell</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Ersetzt das aktuelle Caddy-Binary durch die neueste Version von [unserer Download-Seite](/download), mit denselben installierten Modulen, einschließlich aller Drittanbieter-Plugins, die auf der Caddy-Website registriert sind.

Upgrades unterbrechen laufende Server nicht; aktuell ersetzt der Befehl nur das Binary auf der Festplatte. Das kann sich in Zukunft ändern, wenn wir eine gute Möglichkeit dafür finden.

Der Upgrade-Prozess ist fehlertolerant: Das aktuelle Binary wird zuerst gesichert (neben das aktuelle kopiert) und automatisch wiederhergestellt, wenn etwas schiefgeht. Wenn du das Backup nach Abschluss des Upgrade-Prozesses behalten möchtest, kannst du die Option `--keep-backup` verwenden.

Dieser Befehl kann erhöhte Rechte erfordern, wenn dein Benutzer keine Berechtigung hat, in die ausführbare Datei zu schreiben.



<a id="caddy-add-package"></a>
### `caddy add-package`

<i>⚠️ Experimentell</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Ähnlich wie `caddy upgrade` ersetzt dieser Befehl das aktuelle Caddy-Binary durch die neueste Version mit denselben installierten Modulen, *plus* den als Argumente aufgeführten Paketen im neuen Binary. Die Liste der installierbaren Pakete findest du auf [unserer Download-Seite](/download). Jedes Argument sollte der vollständige Paketname sein.

Zum Beispiel:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



<a id="caddy-remove-package"></a>
### `caddy remove-package`

<i>⚠️ Experimentell</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Ähnlich wie `caddy upgrade` ersetzt dieser Befehl das aktuelle Caddy-Binary durch die neueste Version mit denselben installierten Modulen, aber *ohne* die als Argumente aufgeführten Pakete, falls sie im aktuellen Binary vorhanden waren. Führe `caddy list-modules --packages` aus, um die Liste der Paketnamen nicht standardmäßiger Module im aktuellen Binary zu sehen.



<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

Validiert eine Konfigurationsdatei und beendet sich dann. Dieser Befehl deserialisiert die Konfiguration, lädt und provisioniert anschließend alle ihre Module, als würde die Konfiguration gestartet, startet sie aber nicht tatsächlich. Dadurch werden Fehler in einer Konfiguration sichtbar, die während der Lade- oder Provisionierungsphase entstehen; das ist eine stärkere Fehlerprüfung als bloßes Serialisieren einer Konfiguration als JSON.

`--config` ist die zu validierende Konfigurationsdatei. Bei `-` wird die Konfiguration von stdin gelesen. Standard ist das `Caddyfile` im aktuellen Verzeichnis, falls vorhanden.

`--adapter` ist der Name des zu verwendenden Konfigurationsadapters. Dieses Flag ist nicht erforderlich, wenn der Dateiname von `--config` mit `Caddyfile` beginnt oder mit `.caddyfile` endet, was den `caddyfile`-Adapter annimmt. Andernfalls ist dieses Flag erforderlich, wenn die angegebene Konfigurationsdatei nicht in Caddys nativem JSON-Format vorliegt.

`--envfile` lädt Umgebungsvariablen aus der angegebenen Datei im Format `KEY=VALUE`. Kommentare, die mit `#` beginnen, werden unterstützt; Keys dürfen mit `export` beginnen; Werte dürfen in doppelte Anführungszeichen gesetzt werden (doppelte Anführungszeichen darin können escaped werden); mehrzeilige Werte werden unterstützt.



<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

Gibt die Version aus und beendet sich.



<a id="signals"></a>
## Signale

Caddy fängt bestimmte Signale ab und ignoriert andere. Signale können bestimmtes Prozessverhalten auslösen.

Signal | Verhalten
-------|----------
`SIGINT` | Geordnetes Beenden. Signal erneut senden, um sofortiges Beenden zu erzwingen.
`SIGQUIT` | Beendet Caddy sofort, räumt aber dennoch Locks im Speicher auf, weil das wichtig ist.
`SIGTERM` | Geordnetes Beenden.
`SIGUSR1` | Lädt die Konfigurationsdatei neu, aber nur wenn mit `caddy run` gestartet wurde (ohne `--resume`) und keine Änderungen an der Konfiguration über [die API](/docs/api) vorgenommen wurden (einschließlich [`caddy reload`]#caddy-reload)).
`SIGUSR2` | Ignoriert.
`SIGHUP` | Ignoriert.

Ein geordnetes Beenden bedeutet, dass neue Verbindungen nicht mehr akzeptiert werden und bestehende Verbindungen geleert werden, bevor der Socket geschlossen wird. Eine Grace Period kann gelten (und ist konfigurierbar). Sobald die Grace Period abgelaufen ist, werden Verbindungen zwangsweise beendet. Locks im Speicher und andere Ressourcen, die einzelne Module freigeben müssen, werden während eines geordneten Herunterfahrens aufgeräumt.

Wenn ein Signal zum Neuladen der Konfiguration (`SIGUSR1`) empfangen wird, wirkt es wie ein erzwungenes Konfigurations-Reload (d. h. trotzdem neu laden, auch wenn der Konfigurationstext unverändert ist), wodurch abhängige Dateien wie TLS-Zertifikate von der Festplatte neu geladen werden können.

Signalbasierte Konfigurations-Reloads sind nur aktiviert, wenn Caddy mit `caddy run` und einer Konfigurationsdatei gestartet wurde. Sie werden deaktiviert (Signale werden ignoriert, mit einer Warnung im Log), wenn Caddy mit `--resume` gestartet wird (da dies einen API-Workflow impliziert), wenn irgendeine Konfigurationsänderung über die admin API empfangen wird oder wenn `caddy reload` mit einem *anderen* Dateinamen oder Konfigurationsadapter als beim ursprünglichen Start ausgeführt wird. Dadurch sollen Konflikte zwischen Reload-Methoden vermieden werden.



<a id="exit-codes"></a>
## Exit-Codes

Caddy gibt einen Code zurück, wenn der Prozess beendet wird:

Code | Bedeutung
-----|---------
`0` | Normales Beenden.
`1` | Start fehlgeschlagen. **Den Prozess nicht automatisch neu starten; er wird wahrscheinlich erneut fehlschlagen, sofern keine Änderungen vorgenommen werden.**
`2` | Erzwungenes Beenden. Caddy wurde beendet, ohne Ressourcen aufzuräumen.
`3` | Beenden fehlgeschlagen. Caddy wurde während des Aufräumens mit einigen Fehlern beendet.

In bash kannst du den Exit-Code des letzten Befehls mit `echo $?` abrufen.
