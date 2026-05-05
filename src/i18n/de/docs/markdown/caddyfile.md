---
title: Das Caddyfile
---

<a id="the-caddyfile"></a>
# Das Caddyfile

Das **Caddyfile** ist ein bequemes Caddy-Konfigurationsformat für Menschen. Für die meisten ist es die bevorzugte Art, Caddy zu verwenden, weil es leicht zu schreiben, leicht zu verstehen und für die meisten Anwendungsfälle ausdrucksstark genug ist.

So sieht es aus:

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(Das ist ein echtes, produktionsbereites Caddyfile, das WordPress mit vollständig verwaltetem HTTPS ausliefert.)

Die Grundidee ist: Zuerst schreibst du die Adresse deiner Site, danach die Features oder Funktionen, die deine Site haben soll. [Weitere gängige Muster ansehen.](/docs/caddyfile/patterns)

<a id="menu"></a>
## Menü

- #### [Schnellstart-Anleitung](/docs/quick-starts/caddyfile)
  Ein guter Einstieg, um mit dem Caddyfile vertraut zu werden.
- #### [Vollständiges Caddyfile-Tutorial](/docs/caddyfile-tutorial)
  Lerne, wie du mit dem Caddyfile verschiedene gängige Aufgaben erledigst.
- #### [Caddyfile-Konzepte](/docs/caddyfile/concepts)
  Pflichtlektüre: Struktur, Site-Adressen, matcher, placeholder und mehr.
- #### [Direktiven](/docs/caddyfile/directives)
  Schlüsselwörter am Zeilenanfang, die Features für deine Sites aktivieren.
- #### [Request matcher](/docs/caddyfile/matchers)
  Filtere Requests, indem du matcher mit deinen Direktiven verwendest.
- #### [Globale Optionen](/docs/caddyfile/options)
  Einstellungen, die für den gesamten Server gelten, nicht nur für einzelne Sites.
- #### [Gängige Muster](/docs/caddyfile/patterns)
  Einfache Wege, häufige Aufgaben zu erledigen.
<!-- - #### [Caddyfile-Spezifikation](/docs/caddyfile/spec) TODO: Finish this -->


<a id="note"></a>
## Hinweis

Das Caddyfile ist nur ein [config adapter](/docs/config-adapters) für Caddy. Es wird normalerweise bevorzugt, wenn Konfigurationen manuell geschrieben werden, ist aber nicht so ausdrucksstark, flexibel oder programmierbar wie Caddys [native JSON-Struktur](/docs/json/). Wenn du deine Caddy-Konfigurationen oder Deployments automatisierst, solltest du vielleicht JSON mit [Caddys API](/docs/api) verwenden. (Du kannst das Caddyfile ebenfalls mit der API verwenden, allerdings nur eingeschränkt.)
