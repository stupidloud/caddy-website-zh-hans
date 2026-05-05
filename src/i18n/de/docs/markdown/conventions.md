---
title: Konventionen
---

<a id="conventions"></a>
# Konventionen

Das Caddy-Ökosystem folgt einigen Konventionen, damit Dinge auf der gesamten Plattform konsistent und intuitiv bleiben.


- [Netzwerkadressen](#network-addresses)
- [Platzhalter](#placeholders)
- [Dateispeicherorte](#file-locations)
  - [Datenverzeichnis](#data-directory)
  - [Konfigurationsverzeichnis](#configuration-directory)
- [Dauern](#durations)



<a id="network-addresses"></a>
## Netzwerkadressen

Beim Angeben einer Netzwerkadresse zum Anwählen oder Binden akzeptiert Caddy einen String im folgenden Format:

```
network/address
```

Der Netzwerkteil ist optional (Standard ist `tcp`) und kann alles sein, was Gos Funktion [`net.Dial`](https://pkg.go.dev/net#Dial) erkennt. Wenn ein Netzwerk angegeben wird, muss ein einzelner Schrägstrich `/` Netzwerk- und Adressteil trennen.

Das Netzwerk kann eines der folgenden sein; Varianten mit `4` oder `6` am Ende sind nur IPv4 beziehungsweise nur IPv6:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

Der Adressteil kann eine dieser Formen haben:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

Der Host kann ein beliebiger Hostname, auflösbarer Domainname oder eine IP-Adresse sein.

Bei IPv6-Adressen muss die Adresse in eckige Klammern `[]` eingeschlossen werden. Der Zonenbezeichner (beginnend mit `%`) ist optional und wird oft für link-local-Adressen verwendet.

Der Port kann ein einzelner Wert (`:8080`) oder ein inklusiver Bereich (`:8080-8085`) sein. Ein Portbereich wird in einzelne Adressen expandiert. Nicht alle config-Felder akzeptieren Portbereiche. Der besondere Port `:0` bedeutet einen beliebigen verfügbaren Port.

Ein Unix-Socket-Pfad ist nur akzeptabel, wenn ein `unix*`-Netzwerktyp verwendet wird. Der Schrägstrich, der Netzwerk und Adresse trennt, gilt nicht als Teil des Pfads.

Wenn ein Unix-Socket als Bind-Adresse verwendet wird, kannst du optional nach dem Pfad, getrennt durch eine Pipe `|`, einen Dateiberechtigungsmodus angeben. Standard ist `0200` (oktal), d. h. `u=w,g=,o=` (symbolisch). Die führende `0` ist optional.

Gültige Beispiele:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Caddy-Netzwerkadressen sind keine URLs. URLs koppeln die unteren und höheren Schichten des [OSI-Modells <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture), aber Caddy verwendet Netzwerkadressen oft unabhängig von einer bestimmten Anwendung; sie zu kombinieren wäre daher problematisch. In Caddy beziehen sich Netzwerkadressen präzise auf Ressourcen, die auf L3-L5 angewählt oder gebunden werden können, während URLs L3-L7 kombinieren, was zu viel ist. Eine Netzwerkadresse verlangt, dass Host+Port und Pfad sich gegenseitig ausschließen; URLs tun das nicht. Netzwerkadressen unterstützen manchmal Portbereiche, URLs nicht.

</aside>




<a id="placeholders"></a>
## Platzhalter

Caddys Konfiguration unterstützt die Verwendung von *Platzhaltern*. Platzhalter sind eine einfache Möglichkeit, dynamische Werte in eine statische Konfiguration einzufügen.

<aside class="tip">

Platzhalter ähneln Variablen in anderer Software. Zum Beispiel hat [nginx Variablen <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) wie `$uri` und `$document_root`; Caddys Entsprechungen wären [`{http.request.uri}`](/docs/json/apps/http/#docs) und [`{http.vars.root}`](/docs/caddyfile/directives/root).

</aside>


Platzhalter werden auf beiden Seiten von geschweiften Klammern `{ }` begrenzt und enthalten innen den Bezeichner, zum Beispiel `{foo.bar}`. Die öffnende Platzhalterklammer kann mit `\{like.this}` escaped werden, um Ersetzung zu verhindern. Platzhalterbezeichner sind typischerweise mit Punkten namespaced, um Kollisionen zwischen Modulen zu vermeiden.

Welche Platzhalter verfügbar sind, hängt vom Kontext ab. Nicht alle Platzhalter sind in allen Teilen der config verfügbar. Zum Beispiel setzt [die HTTP-App Platzhalter](/docs/json/apps/http/#docs), die nur in Bereichen der config verfügbar sind, die HTTP-Requests behandeln. Wenn ein Request durch den [`reverse_proxy` handler](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs) läuft, setzt der handler mehrere proxy-spezifische Platzhalter. Diese Platzhalter können während des Proxyings und danach (in `handle_response`) referenziert werden, etwa beim Setzen von Response-Headern oder beim Anreichern von Access Logs.

Die folgenden Platzhalter sind immer verfügbar (global):

Placeholder | Description
------------|-------------
`{env.*}` | Umgebungsvariable; Beispiel: `{env.HOME}`
`{file.*}` | Inhalt aus einer Datei; Beispiel: `{file./path/to/secret.txt}`
`{system.hostname}` | Der lokale Hostname des Systems
`{system.slash}` | Der Dateipfad-Trenner des Systems
`{system.os}` | Das Betriebssystem
`{system.arch}` | Die Architektur des Systems
`{system.wd}` | Das aktuelle Arbeitsverzeichnis
`{time.now}` | Die aktuelle Zeit als Go-Time-Struct
`{time.now.http}` | Die aktuelle Zeit im Format, das in [HTTP-Headern <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified) verwendet wird
`{time.now.unix}` | Die aktuelle Zeit als Unix-Timestamp in Sekunden
`{time.now.unix_ms}` | Die aktuelle Zeit als Unix-Timestamp in Millisekunden
`{time.now.common_log}` | Die aktuelle Zeit im Common Log Format
`{time.now.year}` | Das aktuelle Jahr im Format YYYY

Nicht alle config-Felder unterstützen Platzhalter, aber die meisten dort, wo man es erwarten würde. Unterstützung für Platzhalter muss diesen Feldern explizit hinzugefügt worden sein. Plugin-Autoren können [diesen Artikel](/docs/extending-caddy/placeholders) lesen, um zu lernen, wie sie Unterstützung für Platzhalter in ihren eigenen Modulen hinzufügen.




<a id="file-locations"></a>
## Dateispeicherorte

Dieser Abschnitt enthält Informationen darüber, wo verschiedene Dateien zu finden sind. Die hier beschriebenen Datei- und Verzeichnispfade sind bestenfalls Standardwerte; einige können überschrieben werden.

<a id="your-config-files"></a>
### Deine config-Dateien

Es gibt keinen einzelnen, konventionellen Ort, an dem du deine config-Dateien ablegen musst. Lege sie dort ab, wo es für dich am sinnvollsten ist.

<aside class="tip">

Die einzige Ausnahme könnte eine Datei namens `Caddyfile` im aktuellen Arbeitsverzeichnis sein, die der caddy-Befehl der Bequemlichkeit halber versucht, wenn keine andere config-Datei angegeben ist.

</aside>


Distributionen, die eine Standard-config-Datei mitliefern, sollten dokumentieren, wo sich diese config-Datei befindet, auch wenn es für Paket-/Distro-Maintainer offensichtlich scheint. Bei den meisten Linux-Installationen befindet sich das Caddyfile unter `/etc/caddy/Caddyfile`.


<a id="data-directory"></a>
### Datenverzeichnis

Caddy speichert TLS-Zertifikate und andere wichtige Assets in einem Datenverzeichnis, das vom [konfigurierten Storage-Modul](/docs/json/storage/) gestützt wird (Standard: lokales Dateisystem).

Wenn die Umgebungsvariable `XDG_DATA_HOME` gesetzt ist, ist es `$XDG_DATA_HOME/caddy`.

Andernfalls variiert der Pfad je nach Plattform und folgt OS-Konventionen:

OS | Data directory path
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (oder `/sdcard/caddy`)

Alle anderen Betriebssysteme verwenden den Linux/BSD-Verzeichnispfad.

**Das Datenverzeichnis darf nicht als Cache behandelt werden.** Sein Inhalt ist **nicht** flüchtig und dient nicht bloß der Performance. Caddy speichert TLS-Zertifikate, private Schlüssel, OCSP staples und andere notwendige Informationen im Datenverzeichnis. Es sollte nicht gelöscht werden, ohne die Auswirkungen zu verstehen.

Es ist entscheidend, dass dieses Verzeichnis persistent und für Caddy beschreibbar ist.


<a id="configuration-directory"></a>
### Konfigurationsverzeichnis

Hier kann Caddy bestimmte Konfigurationen auf Festplatte speichern. Vor allem persistiert es standardmäßig die letzte aktive Konfiguration in diesem Ordner, um sie später mit [`caddy run --resume`](/docs/command-line#caddy-run) einfach wieder aufzunehmen.

<aside class="tip">

Das Konfigurationsverzeichnis ist *nicht* der Ort, an dem du [deine config-Dateien](#your-config-files) speichern musst. (Du darfst es aber.)

</aside>


Wenn die Umgebungsvariable `XDG_CONFIG_HOME` gesetzt ist, ist es `$XDG_CONFIG_HOME/caddy`.

Andernfalls variiert der Pfad je nach Plattform und folgt OS-Konventionen:


OS | Config directory path
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Alle anderen Betriebssysteme verwenden den Linux/BSD-Verzeichnispfad.

Es ist entscheidend, dass dieses Verzeichnis persistent und für Caddy beschreibbar ist.


<a id="durations"></a>
## Dauern

Dauer-Strings werden in Caddys Konfiguration häufig verwendet. Sie verwenden dasselbe Format wie Gos [`time.ParseDuration`-Syntax](https://golang.org/pkg/time/#ParseDuration), außer dass du zusätzlich `d` für Tag verwenden kannst (der Einfachheit halber nehmen wir 1 Tag = 24 Stunden an). Gültige Einheiten sind:

- `ns` (Nanosekunde)
- `us`/`µs` (Mikrosekunde)
- `ms` (Millisekunde)
- `s` (Sekunde)
- `m` (Minute)
- `h` (Stunde)
- `d` (Tag)

Beispiele:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

In der [JSON-config](/docs/json/) können Dauerwerte auch Ganzzahlen sein, die Nanosekunden darstellen.
