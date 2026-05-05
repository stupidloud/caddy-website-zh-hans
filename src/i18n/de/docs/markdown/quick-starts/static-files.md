---
title: Quick-start für statische Dateien
---

<a id="static-files-quick-start"></a>
# Quick-start für statische Dateien

Diese Anleitung zeigt dir, wie du schnell einen produktionsreifen Server für statische Dateien einrichtest und startest.

**Voraussetzungen:**
- Grundkenntnisse im Terminal / in der Kommandozeile
- `caddy` in deinem PATH
- Ein Ordner mit deiner Website

---

Es gibt zwei einfache Wege, schnell einen Dateiserver zu starten.

<a id="command-line"></a>
## Kommandozeile

Wechsle in deinem Terminal in das Stammverzeichnis deiner Website und führe aus:

<pre><code class="cmd bash">caddy file-server</code></pre>

Wenn du einen Berechtigungsfehler bekommst, bedeutet das wahrscheinlich, dass dein Betriebssystem das Binden an niedrige Ports nicht erlaubt. Verwende dann stattdessen einen hohen Port:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Öffne anschließend [localhost](http://localhost) oder [localhost:2015](http://localhost:2015) in deinem Browser, um deine Website zu sehen.

Wenn du keine Indexdatei hast, aber eine Dateiliste anzeigen möchtest, verwende die Option `--browse`:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

Du kannst auch einen anderen Ordner als Website-Wurzel verwenden:

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



## Caddyfile

Erstelle im Stammverzeichnis deiner Website eine Datei namens `Caddyfile` mit folgendem Inhalt:

```caddy
localhost

file_server
```

Wenn du keine Berechtigung hast, an niedrige Ports zu binden, ersetze `localhost` durch `localhost:2015` oder einen anderen hohen Port.

Führe dann aus demselben Verzeichnis aus:

<pre><code class="cmd bash">caddy run</code></pre>

Danach kannst du [localhost](https://localhost) oder die Adresse aus deiner Konfiguration laden, um deine Website zu sehen.

Die [`file_server`-Direktive](/docs/caddyfile/directives/file_server) bietet weitere Optionen, mit denen du deine Website anpassen kannst. Vergiss nicht, Caddy nach Änderungen am Caddyfile neu zu [laden](/docs/command-line#caddy-reload) oder zu stoppen und wieder zu starten.

Wenn du keine Indexdatei hast, aber eine Dateiliste anzeigen möchtest, verwende das Argument `browse`:

```caddy
localhost

file_server browse
```

Du kannst auch einen anderen Ordner als Website-Wurzel verwenden:

```caddy
localhost

root /var/www/mysite
file_server
```
