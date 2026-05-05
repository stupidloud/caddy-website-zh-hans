---
title: Caddyfile Quick-start
---

<a id="caddyfile-quick-start"></a>
# Caddyfile Quick-start

Erstelle eine neue Textdatei namens `Caddyfile` ohne Dateiendung.

Das Erste, was du in ein Caddyfile schreibst, ist die Adresse deiner Website:

```caddy
localhost
```

<aside class="tip">

Wenn die HTTP- und HTTPS-Ports, also 80 und 443, auf deinem Betriebssystem privilegierte Ports sind, musst du Caddy entweder mit erhöhten Rechten ausführen oder höhere Ports verwenden. Um die Berechtigung zu erhalten, führe Caddy als root mit `sudo -E` aus oder verwende `sudo setcap cap_net_bind_service=+ep $(which caddy)`. Alternativ kannst du für höhere Ports die Adresse einfach zu etwas wie `localhost:2080` ändern und den HTTP-Port mit der Caddyfile-Option [`http_port`](/docs/caddyfile/options) anpassen.

</aside>

Drücke dann Enter und schreibe, was Caddy tun soll, sodass es so aussieht:

```caddy
localhost

respond "Hello, world!"
```

Speichere die Datei und starte Caddy aus demselben Ordner, in dem dein Caddyfile liegt:

<pre><code class="cmd bash">caddy start</code></pre>

Du wirst wahrscheinlich nach deinem Passwort gefragt, weil Caddy standardmäßig alle Websites, auch lokale, über HTTPS bereitstellt. Die Passwortabfrage sollte nur beim ersten Mal erscheinen.

<aside class="tip">

Für lokales HTTPS erzeugt Caddy automatisch Zertifikate und eindeutige private Schlüssel für dich. Das Root-Zertifikat wird dem Trust Store deines Systems hinzugefügt; deshalb ist die Passwortabfrage nötig. So kannst du lokal über HTTPS entwickeln, ohne Zertifikatsfehler zu bekommen.

</aside>

Wenn du Berechtigungsfehler bekommst, musst du Caddy möglicherweise mit erhöhten Rechten ausführen oder einen Port über 1023 wählen.

Öffne entweder [localhost](http://localhost) im Browser oder rufe es mit `curl` ab:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

Du kannst mehrere Websites in einem Caddyfile definieren, indem du sie in geschweifte Klammern `{ }` setzt. Ändere dein Caddyfile zu:

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

Du kannst Caddy die aktualisierte Konfiguration auf zwei Arten geben, entweder direkt über die API:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

oder mit dem reload-Befehl, der denselben API-Request für dich ausführt:

<pre><code class="cmd bash">caddy reload</code></pre>

Teste deinen neuen „goodbye“-Endpunkt [im Browser](https://localhost:2016) oder mit `curl`, um sicherzugehen, dass er funktioniert:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Wenn du mit Caddy fertig bist, stoppe ihn:

<pre><code class="cmd bash">caddy stop</code></pre>

<a id="further-reading"></a>
## Weitere Lektüre

- [Caddyfile-Konzepte](/docs/caddyfile/concepts)
- [Direktiven](/docs/caddyfile/directives)
- [Gängige Muster](/docs/caddyfile/patterns)
