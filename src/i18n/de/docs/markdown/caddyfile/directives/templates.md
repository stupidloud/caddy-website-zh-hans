---
title: templates (Caddyfile directive)
---

# templates

Führt den Antwortbody als [template](/docs/modules/http.handlers.templates)-Dokument aus. Templates stellen funktionale Grundbausteine bereit, um einfache dynamische Seiten zu erstellen. Zu den Funktionen gehören HTTP-Subrequests, HTML-Datei-Includes, Markdown-Rendering, JSON-Parsing, einfache Datenstrukturen, Zufall, Zeit und mehr.

<aside class="tip">

Templates können auf dem Antwortbody von *beliebiger* Herkunft ausgeführt werden – egal ob es sich um eine statische Datei auf der Festplatte oder einen über Proxy bereitgestellten Webdienst handelt. Es ist ratsam, die Template-Auswertung nur für Inhalte zu aktivieren, denen du vertraust, die du kontrollierst und/oder bereinigst! Eine Fehlkonfiguration kann zu Sicherheitslücken führen. Wenn beispielsweise eine über Proxy bereitgestellte App Benutzern erlaubt, Inhalte zu schreiben/zu veröffentlichen, und diese Inhalte Text enthalten, der wie Template-Aktionen aussieht, könnten beliebige Benutzer Templates auswerten und potenziell auf die Umgebung, lokale Dateien und das Netzwerk zugreifen. Aktiviere Templates nicht für nutzergenerierte Inhalte (ohne sie zu bereinigen).

</aside>


<a id="syntax"></a>
## Syntax

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** sind die MIME-Typen, auf die die templates-Middleware angewendet wird; Antworten ohne passenden `Content-Type` werden nicht als Templates ausgewertet.

  Standard: `text/html text/plain`.

- **between** sind die öffnenden und schließenden Begrenzungszeichen für Template-Aktionen. Sie können sie ändern, wenn sie mit dem Rest Ihres Dokuments kollidieren.

  Standard: `{{printf "{{ }}"}}`.

- **root** ist das Site-Root, wenn Funktionen verwendet werden, die auf das Dateisystem zugreifen.

  Standardmäßig wird das von der Direktive [`root`](root) gesetzte Site-Root verwendet, oder das aktuelle Arbeitsverzeichnis, wenn es nicht gesetzt ist.

- **extensions** erlaubt, benutzerdefinierte Template-Funktionen zu registrieren, die von Modulen im Namespace `http.handlers.templates.functions.*` bereitgestellt werden.

  Jede Unterdirektive im Block entspricht einem Modulnamen. Diese Module können der Template-Funktionsmap benutzerdefinierte Funktionen hinzufügen, typischerweise zur Implementierung wiederverwendbarer Komponenten. Diese Funktion ist hauptsächlich für Plugins gedacht.

Dokumentation zu den eingebauten Template-Funktionen finden Sie im [templates-Modul](/docs/modules/http.handlers.templates#docs).



<a id="examples"></a>
## Beispiele

Ein vollständiges Beispiel einer Site, die Templates zum Ausliefern von Markdown verwendet, finden Sie im Quellcode [dieser Website](https://github.com/caddyserver/website)! Sehen Sie sich insbesondere das [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) und [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html) an.

Templates für eine statische Site aktivieren:

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

Um eine einfache statische Antwort mit einem Template auszuliefern, stellen Sie sicher, dass `Content-Type` gesetzt ist:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Eine Template-Erweiterung (Plugin) verwenden:

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# Erfordert das Plugin caddy-hitcounter:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
