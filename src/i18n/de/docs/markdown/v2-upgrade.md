---
title: Upgrade auf Caddy 2
---

<a id="upgrade-guide"></a>
Upgrade-Anleitung
=================

Caddy 2 ist eine vollständig neue Codebasis, von Grund auf neu geschrieben, um Caddy 1 zu verbessern. Caddy 2 ist nicht abwärtskompatibel mit Caddy 1. Keine Sorge: Für die meisten einfachen Setups ist nicht viel anders. Diese Anleitung hilft dir, so einfach wie möglich umzusteigen.

Diese Anleitung geht nicht ausführlich auf die neuen Features ein -- die übrigens wirklich gut sind, du solltest sie [kennenlernen](/docs/getting-started) -- sondern soll dich schnell mit Caddy 2 arbeitsfähig machen.

- [Die wichtigsten Punkte](#high-order-bits)
- [Schritte](#steps)
- [HTTPS und Ports](#https-and-ports)
- [Command line](#command-line)
- [Caddyfile](#caddyfile)
	- [Wichtigste Änderungen](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [Service-Dateien](#service-files)
- [Plugins](#plugins)
- [Hilfe bekommen](#getting-help)



<a id="high-order-bits"></a>
## Die wichtigsten Punkte

- "Caddy 2" heißt weiterhin einfach `caddy`. Wir verwenden "Caddy 2" eventuell zur Klarstellung, damit der Umstieg weniger verwirrend ist.
- Die meisten Benutzer müssen lediglich ihre `caddy`-Binary und ihre aktualisierte `Caddyfile`-Konfiguration ersetzen (nachdem sie getestet haben, dass sie funktioniert).
- Es ist wahrscheinlich am besten, Caddy 2 ohne Annahmen aus Caddy 1 anzugehen.
- Es kann sein, dass du deine sehr spezielle v1-Konfiguration in v2 nicht perfekt nachbauen kannst. Meist gibt es dafür einen guten Grund.
- Die command line wird nicht mehr zur Serverkonfiguration verwendet.
- Umgebungsvariablen werden für die Konfiguration nicht mehr benötigt.
- Der wichtigste Weg, Caddy 2 Konfiguration zu geben, ist seine [API](/docs/api), aber der [`caddy` command](/docs/command-line) kann ebenfalls verwendet werden.
- Du solltest wissen, dass Caddy 2s native Konfigurationssprache [JSON](/docs/json/) ist und das Caddyfile nur ein weiterer [config adapter](/docs/config-adapters), der für dich nach JSON konvertiert. Sehr individuelle oder fortgeschrittene Anwendungsfälle können JSON erfordern, weil nicht jede mögliche Konfiguration im Caddyfile ausgedrückt werden kann.
- Das Caddyfile ist größtenteils gleich geblieben, aber auch deutlich mächtiger; directives haben sich geändert.



<a id="steps"></a>
## Schritte

1. Mach dich mit Caddy 2 vertraut, indem du unser Tutorial [Erste Schritte](/docs/getting-started) durchgehst.
2. Erledige Schritt 1, falls noch nicht geschehen. Wirklich -- wir können nicht genug betonen, wie wichtig es ist, zumindest zu wissen, wie man Caddy 2 verwendet. (Es macht auch mehr Spaß!)
3. Verwende die Anleitung unten, um deine `caddy` commands umzustellen.
4. Verwende die Anleitung unten, um dein Caddyfile umzustellen.
5. Teste deine neue Konfiguration lokal oder in staging.
6. Teste, teste und teste erneut.
7. Deploye und hab Spaß.



<a id="https-and-ports"></a>
## HTTPS und Ports

Caddys Standardport ist nicht mehr `:2015`. Der Standardport von Caddy 2 ist `:443` oder, wenn kein Hostname/keine IP bekannt ist, Port `:80`. Du kannst die Ports in deiner Konfiguration jederzeit anpassen.

Caddy 2s Standardprotokoll ist [*immer* HTTPS, wenn ein Hostname oder eine IP bekannt ist](/docs/automatic-https#overview). Das unterscheidet sich von Caddy 1, wo nur öffentlich wirkende Domains standardmäßig HTTPS verwendeten. Jetzt verwendet *jede* Site HTTPS (außer du deaktivierst es, indem du ausdrücklich Port `:80` oder `http://` angibst).

Für IP-Adressen und localhost-Domains werden Zertifikate von einer [lokal vertrauenswürdigen, eingebetteten CA](/docs/automatic-https#local-https) ausgestellt. Alle anderen Domains verwenden ZeroSSL oder Let's Encrypt. (Das ist alles konfigurierbar.)

Die Speicherstruktur von Zertifikaten und ACME-Ressourcen hat sich geändert. Caddy 2 wird wahrscheinlich neue Zertifikate für deine Sites beziehen; wenn du aber viele Zertifikate hast, kannst du sie manuell migrieren, falls Caddy das nicht für dich tut. Details findest du in den Issues [#2955](https://github.com/caddyserver/caddy/issues/2955) und [#3124](https://github.com/caddyserver/caddy/issues/3124).



<a id="command-line"></a>
## Command line

Der command `caddy` ist jetzt `caddy run`.

Alle command-line flags sind anders. Entferne sie; die gesamte Serverkonfiguration liegt jetzt im eigentlichen config document (normalerweise Caddyfile oder JSON). Was du brauchst, findest du wahrscheinlich in der [JSON-Struktur](/docs/json/) oder in den [globalen Caddyfile-Optionen](/docs/caddyfile/options), um die meisten command-line flags aus v1 zu ersetzen.

Ein command wie `caddy -conf ../Caddyfile` würde zu `caddy run --config ../Caddyfile`.

Wie bisher findet und verwendet Caddy dein Caddyfile automatisch, wenn es im aktuellen Ordner liegt; du musst in diesem Fall das flag `--config` nicht verwenden.

Signale sind größtenteils gleich, außer dass USR1 und USR2 nicht mehr unterstützt werden. Verwende stattdessen den command [`caddy reload`](/docs/command-line#caddy-reload) oder die [API](/docs/api), um neue Konfiguration zu laden.

`caddy` ohne Konfiguration auszuführen, startete früher einen einfachen file server. Das Äquivalent in Caddy 2 ist [`caddy file-server`](/docs/command-line#caddy-file-server).

Umgebungsvariablen sind nicht mehr relevant, außer `HOME` (und optional allen von dir gesetzten `XDG_*`-Variablen). `CADDYPATH` wird durch [OS-Konventionen ersetzt](/docs/conventions#file-locations).



<a id="caddyfile"></a>
## Caddyfile

Das [v2 Caddyfile](/docs/caddyfile/concepts) ist dem, was du bereits kennst, sehr ähnlich. Die wichtigste Aufgabe ist, deine directives zu ändern.

⚠️ **Lies dich unbedingt in die neuen directives ein!** Besonders wenn deine Konfiguration fortgeschrittener ist, gibt es viele Nuancen zu beachten. Diese Tipps bringen dich größtenteils schnell zum Umstieg, aber lies bitte die vollständige Dokumentation zu jeder directive, damit du die Auswirkungen des Upgrades verstehst. Und natürlich: Teste deine Konfigurationen immer gründlich, bevor du sie in Produktion nimmst.


<a id="primary-changes"></a>
### Wichtigste Änderungen

- Wenn du statische Dateien auslieferst, musst du eine [`file_server` directive](/docs/caddyfile/directives/file_server) hinzufügen, weil Caddy 2 das nicht standardmäßig annimmt. Caddy 2 erkennt MIME aus Sicherheitsgründen standardmäßig ebenfalls nicht automatisch; wenn ein Content-Type fehlt, musst du den header eventuell selbst mit der directive [header](/docs/caddyfile/directives/header) setzen.

- In v1 konntest du directives nur nach Request-Pfad filtern (oder "matchen"). In v2 ist [request matching](/docs/caddyfile/matchers) deutlich mächtiger. Alle v2 directives, die middleware zur HTTP handler chain hinzufügen oder den HTTP request/response auf irgendeine Weise manipulieren, nutzen diese neue matching-Funktionalität. [Mehr über v2 request matchers.](/docs/caddyfile/matchers) Du musst sie kennen, um das v2 Caddyfile sinnvoll zu verstehen.

- Obwohl viele [placeholders](/docs/conventions#placeholders) gleich sind, haben sich viele geändert, und es gibt jetzt [viele neue](/docs/modules/http#docs), einschließlich [Kurzformen für das Caddyfile](/docs/caddyfile/concepts#placeholders).

- Caddy 2 logs sind alle strukturiert, und das Standardformat ist JSON. Alle log levels können einfach in dasselbe log geschrieben und dort verarbeitet werden (du kannst das bei Bedarf anpassen).

- Wo du in Caddy 1 Requests nach path prefix gematcht hast, ist path matching in Caddy 2 standardmäßig exakt. Wenn du ein Präfix wie `/foo/` matchen möchtest, brauchst du in Caddy 2 `/foo/*`.

Wir listen hier einige der häufigsten v1 directives auf und beschreiben, wie sie für das v2 Caddyfile konvertiert werden.

⚠️ **Nur weil eine v1 directive auf dieser Seite fehlt, heißt das nicht, dass v2 es nicht kann!** Einige v1 directives werden nicht mehr benötigt, lassen sich nicht gut übersetzen oder werden in v2 anders erfüllt. Für manche fortgeschrittenen Anpassungen musst du eventuell auf JSON ausweichen, um das gewünschte Ergebnis zu erreichen. Durchsuche [unsere Dokumentation](/docs/caddyfile), um zu finden, was du brauchst.


<a id="basicauth"></a>
### basicauth

HTTP Basic Authentication wird weiterhin mit der directive [`basic_auth`](/docs/caddyfile/directives/basic_auth) konfiguriert. Die Caddy 2-Konfiguration akzeptiert jedoch keine Klartextpasswörter. Du musst sie hashen; dabei hilft [`caddy hash-password`](/docs/command-line#caddy-hash-password).

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


<a id="browse"></a>
### browse

File browsing wird jetzt über die directive [`file_server`](/docs/caddyfile/directives/file_server) aktiviert.

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


<a id="errors"></a>
### errors

Eigene Fehlerseiten kannst du mit [`handle_errors`](/docs/caddyfile/directives/handle_errors) umsetzen.


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

<a id="ext"></a>
### ext

Implizite Dateierweiterungen lassen sich mit [`try_files`](/docs/caddyfile/directives/try_files) umsetzen.

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


<a id="fastcgi"></a>
### fastcgi

Wenn du PHP auslieferst, ist das v2-Äquivalent [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

Beachte, dass die v1 directive `fastcgi` unter der Haube viel erledigt hat, einschließlich Dateien auf der Platte zu prüfen, Requests umzuschreiben und sogar Redirects auszuführen. Die v2 directive `php_fastcgi` macht diese Dinge ebenfalls für dich; die Dokumentation zeigt aber ihre [erweiterte Form](/docs/caddyfile/directives/php_fastcgi#expanded-form), die du anpassen kannst, wenn deine Anforderungen anders sind.

In v2 wird kein `php` preset benötigt, weil die directive `php_fastcgi` standardmäßig PHP annimmt. Eine Zeile wie `php_fastcgi 127.0.0.1:9000 php` führt dazu, dass der reverse proxy denkt, es gebe ein zweites Backend namens `php`, was Verbindungsfehler verursacht.

Die subdirectives sind in v2 anders -- für PHP wirst du wahrscheinlich keine benötigen.


<a id="gzip"></a>
### gzip

Eine einzelne directive [`encode`](/docs/caddyfile/directives/encode) wird jetzt für alle response encodings verwendet, einschließlich mehrerer Kompressionsformate.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

Nebenbei: Caddy 2 unterstützt auch `zstd` (aber Browser noch nicht).


<a id="header"></a>
### header

[Größtenteils unverändert](/docs/caddyfile/directives/header), aber jetzt deutlich mächtiger, weil es in v2 substring replacements ausführen kann.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


<a id="log"></a>
### log

Aktiviert access logging; die directive [`log`](/docs/caddyfile/directives/log) kann in v2 weiterhin verwendet werden, aber alle Logs sind standardmäßig strukturiert und als JSON codiert.

Die empfohlene Art, access logging zu aktivieren, ist einfach:

```caddy-d
log
```

Das schreibt strukturierte Logs nach stderr. (Du kannst auch in eine Datei oder einen Netzwerk-Socket schreiben; siehe die Dokumentation zur directive [`log`](/docs/caddyfile/directives/log).)

Standardmäßig liegen Logs im [strukturierten](/docs/logging) JSON-Format vor. Wenn du aus Legacy-Gründen weiterhin Logs im Common Log Format (CLF) brauchst, kannst du das Plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder) verwenden.


<a id="proxy"></a>
### proxy

Das v2-Äquivalent ist [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

Wichtige Änderungen bei subdirectives: `header_upstream` und `header_downstream` wurden zu `header_up` bzw. `header_down`; load-balancing-bezogene subdirectives haben das Präfix `lb_`.

Ein weiterer wichtiger Unterschied ist, dass der v2 proxy standardmäßig alle eingehenden headers weitergibt (einschließlich des `Host`-Headers) und den Header `X-Forwarded-For` setzt. Anders gesagt: Der "transparent"-Modus aus v1 ist in v2 im Grunde der Standard (wenn du aber andere headers wie X-Real-IP brauchst, musst du sie selbst setzen). Du kannst den `Host`-Header weiterhin mit der subdirective `header_up` überschreiben/anpassen.

Websocket proxying funktioniert in v2 einfach so; es ist nicht nötig, Websockets wie in v1 zu "aktivieren".

Die subdirective `without` wurde entfernt, weil [rewrite hacks](#rewrite) in v2 dank verbesserter matcher-Unterstützung nicht mehr nötig sind.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


<a id="redir"></a>
### redir

[Unverändert](/docs/caddyfile/directives/redir), abgesehen von einigen Details zum optionalen status code-Argument. Die meisten Konfigurationen müssen nichts ändern.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


<a id="rewrite"></a>
### rewrite

Die Semantik des request rewriting ("internal redirecting") hat sich leicht geändert. Wenn du in v1 einen sogenannten "rewrite hack" verwendet hast, um Requests nach etwas anderem als einem einfachen path prefix zu matchen, ist das in v2 vollständig unnötig.

Die [neue directive `rewrite`](/docs/caddyfile/directives/rewrite) ist sehr einfach, aber sehr mächtig, weil der größte Teil ihrer Komplexität in v2 von [matchers](/docs/caddyfile/matchers) behandelt wird:

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Beachte, dass wir einfach Caddy 2s normale [matcher tokens](/docs/caddyfile/matchers) verwenden; es ist kein Sonderfall mehr für diese directive.

Beginne damit, alle rewrite hacks zu entfernen; wandle sie stattdessen in [named matchers](/docs/caddyfile/concepts#named-matchers) um. Prüfe jedes v1 `rewrite`, um zu sehen, ob es in v2 wirklich noch nötig ist. Hinweis: Ein v1 Caddyfile, das `rewrite` verwendet, um ein Pfadpräfix hinzuzufügen, und dann `proxy` mit `without`, um dasselbe Präfix wieder zu entfernen, ist ein rewrite hack und kann beseitigt werden.

Die neuen directives [`route`](/docs/caddyfile/directives/route) und [`handle`](/docs/caddyfile/directives/handle) können nützlich sein, wenn du mehr Kontrolle über fortgeschrittene routing logic brauchst.


<a id="root"></a>
### root

[Unverändert](/docs/caddyfile/directives/root).

Denke daran, eine directive [`file_server`](/docs/caddyfile/directives/file_server) hinzuzufügen, wenn du statische Dateien auslieferst, weil Caddy 2 das nicht standardmäßig annimmt, während es in v1 immer aktiviert war.


<a id="status"></a>
### status

Das v2-Äquivalent ist [`respond`](/docs/caddyfile/directives/respond), das auch einen response body schreiben kann.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


<a id="templates"></a>
### templates

Die Gesamtsyntax der directive [`templates`](/docs/caddyfile/directives/templates) ist unverändert, aber die tatsächlichen template actions/functions sind anders und deutlich verbessert. Templates können zum Beispiel Dateien einbinden, Markdown rendern, interne sub-requests ausführen, front matter parsen und mehr.

[Siehe die Dokumentation](/docs/modules/http.handlers.templates) für Details zu den neuen Funktionen.

- **v1:** `templates`
- **v2:** `templates`


<a id="tls"></a>
### tls

Die Grundlagen der directive [`tls`](/docs/caddyfile/directives/tls) haben sich nicht geändert, zum Beispiel wenn du eigenes Zertifikat und eigenen Schlüssel angibst:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

Aber Caddys [auto-HTTPS logic](/docs/automatic-https) *hat* sich geändert; sei dir dessen bewusst.

Auch die Namen der cipher suites haben sich geändert.

Eine gängige Konfiguration in Caddy 2 ist `tls internal`, damit Caddy für einen Entwicklungs-Hostnamen, der nicht `localhost` oder eine IP-Adresse ist, ein lokal vertrauenswürdiges Zertifikat ausliefert.

Die meisten Sites brauchen diese directive gar nicht.


<a id="service-files"></a>
## Service-Dateien

Für Caddy-Deployments empfehlen wir eine [unserer offiziellen systemd service files](/docs/running#linux-service).

Wenn du eine eigene service file brauchst, nimm unsere als Grundlage. Sie wurden aus guten Gründen sorgfältig darauf abgestimmt. Passe deine bei Bedarf unbedingt an.


<a id="plugins"></a>
## Plugins

Für v1 geschriebene Plugins sind nicht automatisch mit v2 kompatibel. Viele v1-Plugins werden in v2 nicht einmal mehr benötigt. Andererseits ist v2 viel einfacher erweiterbar und flexibler als v1.

Wenn du ein Plugin für Caddy 2 schreiben möchtest, [lerne, wie man ein Caddy module schreibt](/docs/extending-caddy).


<a id="building-caddy-2-with-plugins"></a>
### Caddy 2 mit Plugins bauen

Caddy 2 kann auf der [interaktiven Download-Seite](/download) mit Plugins heruntergeladen werden. Alternativ kannst du Caddy mit `xcaddy` [selbst bauen](/docs/build) und auswählen, welche Plugins enthalten sein sollen. `xcaddy` automatisiert die Anweisungen in Caddys Datei [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go).


<a id="getting-help"></a>
## Hilfe bekommen

Wenn du Schwierigkeiten hast, Caddy zum Laufen zu bringen, sieh dir bitte zuerst die Dokumentation auf unserer Website an. Nimm dir Zeit, Neues auszuprobieren und zu verstehen, was passiert - v2 unterscheidet sich in vielerlei Hinsicht stark von v1 (ist aber auch sehr vertraut)!

Wenn du weiterhin Hilfe brauchst, werde Teil [unserer Community](https://caddy.community). Vielleicht stellst du fest, dass anderen zu helfen auch der beste Weg ist, dir selbst zu helfen.
