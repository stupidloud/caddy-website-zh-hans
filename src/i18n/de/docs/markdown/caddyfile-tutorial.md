---
title: Caddyfile-Tutorial
---

<a id="caddyfile-tutorial"></a>
# Caddyfile-Tutorial

Dieses Tutorial vermittelt dir die Grundlagen des [HTTP-Caddyfile](/docs/caddyfile), damit du schnell und einfach gut lesbare, funktionale Site-configs erstellen kannst.

**Ziele:**
- 🔲 Erste Site
- 🔲 Statischer Dateiserver
- 🔲 Templates
- 🔲 Komprimierung
- 🔲 Mehrere Sites
- 🔲 Matcher
- 🔲 Umgebungsvariablen
- 🔲 Kommentare

**Voraussetzungen:**
- Grundkenntnisse im Terminal / auf der Kommandozeile
- Grundkenntnisse mit einem Texteditor
- `caddy` in deinem `PATH`

---

Erstelle eine neue Textdatei namens `Caddyfile` (ohne Erweiterung).

Als Erstes solltest du die [Adresse](/docs/caddyfile/concepts#addresses) deiner Site eingeben:

```caddy
localhost
```

<aside class="tip">

Wenn die HTTP- und HTTPS-Ports (80 beziehungsweise 443) auf deinem Betriebssystem privilegierte Ports sind, musst du entweder mit erhöhten Rechten laufen oder einen höheren Port verwenden. Um einen höheren Port zu verwenden, ändere die Adresse einfach zu etwas wie `localhost:2015` und ändere den HTTP-Port über die Caddyfile-Option [http_port](/docs/caddyfile/options).

</aside>


Drücke dann Enter und gib ein, was Caddy tun soll. Für dieses Tutorial soll dein Caddyfile so aussehen:

```caddy
localhost

respond "Hello, world!"
```

Speichere das und führe Caddy aus (da dies ein Übungstutorial ist, verwenden wir das Flag `--watch`, damit Änderungen am Caddyfile automatisch angewendet werden):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Wenn du Berechtigungsfehler bekommst, versuche einen höheren Port in deiner Adresse zu verwenden (z. B. `localhost:2015`) und [den HTTP-Port zu ändern](/docs/caddyfile/options), oder führe Caddy mit erhöhten Rechten aus.

</aside>


Beim ersten Mal wirst du nach deinem Passwort gefragt. Das ist nötig, damit Caddy deine Site über HTTPS ausliefern kann.

<aside class="tip">

Caddy liefert standardmäßig alle Sites über HTTPS aus, solange ein Host oder eine IP Teil der Site-Adresse ist. [Automatic HTTPS](/docs/automatic-https) kann deaktiviert werden, indem der Adresse explizit `http://` vorangestellt wird.

</aside>


<aside class="complete">Erste Site</aside>

Öffne [localhost](https://localhost) in deinem Browser und sieh deinen Webserver arbeiten, inklusive HTTPS.

<aside class="tip">
	Möglicherweise musst du deinen Browser neu starten, falls du beim ersten Mal einen Zertifikatsfehler bekommst.
</aside>

Das ist noch nicht besonders spannend, also ändern wir unsere statische Response zu einem [Dateiserver](/docs/caddyfile/directives/file_server) mit aktivierten Verzeichnislisten:

```caddy
localhost

file_server browse
```

Speichere dein Caddyfile und aktualisiere dann deinen Browser-Tab. Du solltest entweder eine Dateiliste sehen oder eine HTML-Seite, falls sich im aktuellen Verzeichnis eine Indexdatei befindet.

<aside class="complete">Statischer Dateiserver</aside>

<a id="adding-functionality"></a>
## Funktionalität hinzufügen

Machen wir etwas Interessantes mit unserem Dateiserver: Wir liefern eine Seite mit Template aus. Erstelle eine neue Datei und füge Folgendes ein:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Speichere sie als `caddy.html` im aktuellen Verzeichnis und lade sie im Browser: [https://localhost/caddy.html](https://localhost/caddy.html)

Die Ausgabe ist:

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Moment. Wir sollten das heutige Datum sehen. Warum funktioniert es nicht? Weil der Server noch nicht so konfiguriert ist, dass er Templates auswertet. Leicht zu beheben: Füge eine Zeile zum Caddyfile hinzu, sodass es so aussieht:

```caddy
localhost

templates
file_server browse
```

Speichere das und lade den Browser-Tab neu. Du solltest sehen:

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Mit Caddys [templates module](/docs/modules/http.handlers.templates) kannst du viele nützliche Dinge mit statischen Dateien tun, etwa andere HTML-Dateien einbinden, Sub-Requests machen, Response-Header setzen, mit Datenstrukturen arbeiten und mehr.

<aside class="complete">Templates</aside>

Es ist gute Praxis, Responses mit einem schnellen und modernen Kompressionsalgorithmus zu komprimieren. Aktivieren wir Gzip- und Zstandard-Unterstützung mit der Direktive [`encode`](/docs/caddyfile/directives/encode):

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Komprimierung</aside>

Das ist der grundlegende Ablauf, um eine halbwegs fortgeschrittene, produktionsreife Site zum Laufen zu bringen.

Wenn du bereit bist, [automatic HTTPS](/docs/automatic-https) zu aktivieren, ersetze einfach die Adresse deiner Site (`localhost` in unserem Tutorial) durch deinen Domainnamen. Weitere Informationen findest du in unserem [HTTPS-Schnellstart](/docs/quick-starts/https).

<a id="multiple-sites"></a>
## Mehrere Sites

Mit unserem aktuellen Caddyfile können wir nur eine Site-Definition haben. Nur die erste Zeile kann die Adresse(n) der Site enthalten, und der gesamte Rest der Datei muss Direktiven für diese Site enthalten.

Aber es ist einfach, die Datei so umzubauen, dass wir weitere Sites hinzufügen können.

Unser bisheriges Caddyfile:

```caddy
localhost

encode
templates
file_server browse
```

ist äquivalent zu diesem:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

nur erlaubt die zweite Variante, weitere Sites hinzuzufügen.

Indem wir unseren Site-Block in geschweifte Klammern `{ }` einschließen, können wir mehrere, unterschiedliche Sites im selben Caddyfile definieren.

Zum Beispiel:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

Wenn Site-Blöcke in geschweifte Klammern eingeschlossen werden, stehen nur [Adressen](/docs/caddyfile/concepts#addresses) außerhalb der Klammern und nur [Direktiven](/docs/caddyfile/directives) innerhalb.

Für mehrere Sites, die dieselbe Konfiguration teilen, kannst du weitere Adressen hinzufügen, zum Beispiel:

```caddy
:8080, :8081 {
	...
}
```

Du kannst dann so viele unterschiedliche Sites definieren, wie du möchtest, solange jede Adresse eindeutig ist.

<aside class="complete">Mehrere Sites</aside>


<a id="matchers"></a>
## Matcher

Manchmal möchten wir Direktiven nur auf bestimmte Requests anwenden. Angenommen, wir wollen sowohl einen Dateiserver als auch einen reverse proxy haben, aber offensichtlich nicht beides für jeden Request. Entweder schreibt der Dateiserver eine Response mit einer statischen Datei, oder der reverse proxy gibt den Request an ein Backend weiter und schreibt dessen Response zurück.

Diese config funktioniert nicht so, wie wir es wollen (`reverse_proxy` hat aufgrund der [Direktivenreihenfolge](/docs/caddyfile/directives#directive-order) Vorrang):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

In der Praxis wollen wir den reverse proxy vielleicht nur für API-Requests verwenden, also Requests mit Basispfad `/api/`. Das ist einfach, indem wir ein [Matcher-Token](/docs/caddyfile/matchers#syntax) hinzufügen:

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

So; jetzt wird der reverse proxy für alle Requests priorisiert, die mit `/api/` beginnen.

Der gerade hinzugefügte Teil `/api/*` heißt **Matcher-Token**. Du erkennst es daran, dass es mit einem Schrägstrich `/` beginnt und direkt nach der Direktive steht (du kannst aber immer in der [Dokumentation der Direktive](/docs/caddyfile/directives) nachsehen, um sicherzugehen).

Matcher sind sehr mächtig. Du kannst benannte Matcher deklarieren und sie wie `@name` verwenden, um auf mehr als nur den Request-Pfad zu matchen. Nimm dir einen Moment, um [mehr über Matcher zu lernen](/docs/caddyfile/matchers), bevor du weitermachst.

<aside class="complete">Matcher</aside>

<a id="environment-variables"></a>
## Umgebungsvariablen

Der Caddyfile-Adapter erlaubt das Ersetzen von [Umgebungsvariablen](/docs/caddyfile/concepts#environment-variables), bevor das Caddyfile geparst wird.

Setze zuerst eine Umgebungsvariable (in derselben Shell, die Caddy ausführt):

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Dann kannst du sie im Caddyfile so verwenden:

```caddy
{$SITE_ADDRESS}

file_server
```

Bevor das Caddyfile geparst wird, wird es expandiert zu:

```caddy
localhost:9055

file_server
```

Du kannst Umgebungsvariablen überall im Caddyfile verwenden, für beliebig viele Tokens.

<aside class="complete">Umgebungsvariablen</aside>


<a id="comments"></a>
## Kommentare

Eine letzte Sache, die du sehr hilfreich finden wirst: Wenn du in deinem Caddyfile etwas anmerken oder notieren möchtest, kannst du Kommentare verwenden, beginnend mit `#`:

```caddy
# this starts a comment
```

<aside class="complete">Kommentare</aside>

<a id="further-reading"></a>
## Weiterführende Lektüre

- [Caddyfile-Konzepte](/docs/caddyfile/concepts)
- [Direktiven](/docs/caddyfile/directives)
- [Gängige Muster](/docs/caddyfile/patterns)
