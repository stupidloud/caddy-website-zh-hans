---
title: Caddyfile-Direktiven
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

<a id="caddyfile-directives"></a>
# Caddyfile-Direktiven

Direktiven sind funktionale Schlüsselwörter, die innerhalb von Site-[Blöcken](/docs/caddyfile/concepts#blocks) erscheinen. Manchmal öffnen sie eigene Blöcke, die *Subdirektiven* enthalten können, aber Direktiven können **nicht** innerhalb anderer Direktiven verwendet werden, sofern dies nicht ausdrücklich dokumentiert ist. Zum Beispiel können Sie `basic_auth` nicht innerhalb eines `file_server`-Blocks verwenden, weil `file_server` nicht weiß, wie Authentifizierung ausgeführt wird. Sie *dürfen* jedoch manche Direktiven innerhalb spezieller Direktivenblöcke wie `handle` und `route` verwenden, weil diese gezielt dafür entworfen sind, HTTP-Handler-Direktiven zu gruppieren.

- [Syntax](#syntax)
- [Direktivenreihenfolge](#directive-order)
- [Sortieralgorithmus](#sorting-algorithm)

Die folgenden Direktiven sind standardmäßig in Caddy enthalten und können im HTTP-Caddyfile verwendet werden:

<div id="directive-table">

Direktive | Beschreibung
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Bricht den HTTP-Request ab
**[acme_server](/docs/caddyfile/directives/acme_server)** | Ein eingebetteter ACME-Server
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Erzwingt HTTP Basic Authentication
**[bind](/docs/caddyfile/directives/bind)** | Passt die Socket-Adresse des Servers an
**[encode](/docs/caddyfile/directives/encode)** | Kodiert (meist komprimiert) Responses
**[error](/docs/caddyfile/directives/error)** | Löst einen Fehler aus
**[file_server](/docs/caddyfile/directives/file_server)** | Liefert Dateien von der Festplatte aus
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Delegiert Authentifizierung an einen externen Dienst
**[fs](/docs/caddyfile/directives/fs)** | Legt das Dateisystem für Datei-I/O fest
**[handle](/docs/caddyfile/directives/handle)** | Eine gegenseitig exklusive Gruppe von Direktiven
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Definiert Routes zur Fehlerbehandlung
**[handle_path](/docs/caddyfile/directives/handle_path)** | Wie handle, entfernt aber ein Pfadpräfix
**[header](/docs/caddyfile/directives/header)** | Setzt oder entfernt Response-Header
**[import](/docs/caddyfile/directives/import)** | Bindet Snippets oder Dateien ein
**[intercept](/docs/caddyfile/directives/intercept)** | Fängt von anderen Handlern geschriebene Responses ab
**[invoke](/docs/caddyfile/directives/invoke)** | Ruft eine benannte Route auf
**[log](/docs/caddyfile/directives/log)** | Aktiviert Access-/Request-Logging
**[log_append](/docs/caddyfile/directives/log_append)** | Hängt ein Feld an das Access Log an
**[log_skip](/docs/caddyfile/directives/log_skip)** | Überspringt Access Logging für gematchte Requests
**[log_name](/docs/caddyfile/directives/log_name)** | Überschreibt die Logger-Namen, in die geschrieben wird
**[map](/docs/caddyfile/directives/map)** | Ordnet einen Eingabewert einem oder mehreren Ausgabewerten zu
**[method](/docs/caddyfile/directives/method)** | Ändert intern die HTTP-Methode
**[metrics](/docs/caddyfile/directives/metrics)** | Konfiguriert den Prometheus-Metrics-Exposition-Endpunkt
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Liefert PHP-Sites über FastCGI aus
**[push](/docs/caddyfile/directives/push)** | Pusht Inhalt per HTTP/2 Server Push zum Client
**[redir](/docs/caddyfile/directives/redir)** | Sendet einen HTTP-Redirect an den Client
**[request_body](/docs/caddyfile/directives/request_body)** | Manipuliert den Request-Body
**[request_header](/docs/caddyfile/directives/request_header)** | Manipuliert Request-Header
**[respond](/docs/caddyfile/directives/respond)** | Schreibt eine fest kodierte Response an den Client
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Ein leistungsfähiger und erweiterbarer Reverse Proxy
**[rewrite](/docs/caddyfile/directives/rewrite)** | Schreibt den Request intern um
**[root](/docs/caddyfile/directives/root)** | Legt den Pfad zum Site-Root fest
**[route](/docs/caddyfile/directives/route)** | Eine Gruppe von Direktiven, die wörtlich als einzelne Einheit behandelt wird
**[templates](/docs/caddyfile/directives/templates)** | Führt Templates auf der Response aus
**[tls](/docs/caddyfile/directives/tls)** | Passt TLS-Einstellungen an
**[tracing](/docs/caddyfile/directives/tracing)** | Integration mit OpenTelemetry Tracing
**[try_files](/docs/caddyfile/directives/try_files)** | Rewrite, der von Dateiexistenz abhängt
**[uri](/docs/caddyfile/directives/uri)** | Manipuliert die URI
**[vars](/docs/caddyfile/directives/vars)** | Setzt beliebige Variablen

</div>

<a id="syntax"></a>
## Syntax

Die Syntax jeder Direktive sieht ungefähr so aus:

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

Die `<spitzen Klammern>` kennzeichnen Tokens, die durch tatsächliche Werte ersetzt werden.

Die `[eckigen Klammern]` kennzeichnen optionale Parameter.

Die Auslassungspunkte `...` kennzeichnen eine Fortsetzung, d. h. einen oder mehrere Parameter oder Zeilen.

Subdirektiven sind normalerweise optional, sofern nicht anders dokumentiert, auch wenn sie nicht in `[eckigen Klammern]` erscheinen.


### Matcher

Die meisten, aber nicht alle, Direktiven akzeptieren [Matcher-Tokens](/docs/caddyfile/matchers#syntax), mit denen Sie Requests filtern können. Matcher-Tokens sind normalerweise optional. Direktiven unterstützen Matcher, wenn Sie dies in der Syntax der Direktive sehen:

```caddy-d
[<matcher>]
```

Da Matcher-Tokens alle gleich funktionieren, werden die verschiedenen Möglichkeiten für das Matcher-Token nicht auf jeder Seite beschrieben, um Wiederholung zu vermeiden. Lesen Sie stattdessen die [Matcher-Dokumentation](/docs/caddyfile/matchers) für eine detaillierte Erklärung der Syntax.


<a id="directive-order"></a>
## Direktivenreihenfolge

Viele Direktiven manipulieren die HTTP-Handler-Kette. Die Reihenfolge, in der diese Direktiven ausgewertet werden, ist wichtig; deshalb ist in Caddy eine Standardreihenfolge fest kodiert.

Sie können diese Reihenfolge mit der [globalen Option `order`](/docs/caddyfile/options#order) oder der Direktive [`route`](/docs/caddyfile/directives/route) überschreiben bzw. anpassen.

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # nur im handle_response-Block von reverse_proxy
request_body

redir

# Manipulation eingehender Requests
method
rewrite
uri
try_files

# Middleware-Handler; einige umschließen Responses
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# spezielle Routing- und Dispatching-Direktiven
invoke
handle
handle_path
route

# Handler, die typischerweise auf Requests antworten
abort
error
copy_response # nur im handle_response-Block von reverse_proxy
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## Sortieralgorithmus

Zur einfacheren Nutzung sortiert der Caddyfile-Adapter Direktiven nach den folgenden Regeln:

- Unterschiedlich benannte Direktiven werden nach ihrer Position in der [Standardreihenfolge](#directive-order) sortiert. Die Standardreihenfolge kann mit der [globalen Option `order`](/docs/caddyfile/options) überschrieben werden. Direktiven aus Plugins haben *keine* Reihenfolge, daher sollte die globale Option [`order`](/docs/caddyfile/options) oder die Direktive [`route`](/docs/caddyfile/directives/route) verwendet werden, um eine festzulegen.

- Gleich benannte Direktiven werden nach ihren [Matchern](/docs/caddyfile/matchers#syntax) sortiert.

  - Die höchste Priorität hat eine Direktive mit einem einzelnen [Path-Matcher](/docs/caddyfile/matchers#path-matchers).

    Path-Matcher werden nach Spezifität sortiert, von am spezifischsten zu am wenigsten spezifisch.
	
	Im Allgemeinen geschieht dies durch Sortierung nach der Länge des Path-Matchers. Es gibt eine Ausnahme: Wenn der Pfad mit `*` endet und die Pfade der zwei Matcher ansonsten gleich sind, gilt der Matcher ohne `*` als spezifischer und wird höher einsortiert.

    Zum Beispiel:
    - `/foobar` ist spezifischer als `/foo`
    - `/foo` ist spezifischer als `/foo*`
    - `/foo/*` ist spezifischer als `/foo*`

  - Eine Direktive mit einem beliebigen anderen Matcher wird als Nächstes sortiert, in der Reihenfolge, in der sie im Caddyfile erscheint.

    Dazu gehören Path-Matcher mit mehreren Werten und [benannte Matcher](/docs/caddyfile/matchers#named-matchers).

  - Eine Direktive ohne Matcher (d. h. passend auf alle Requests) wird zuletzt sortiert.

- Die Direktive [`vars`](/docs/caddyfile/directives/vars) hat ihre Sortierung nach Matcher umgekehrt, weil sie Werte setzt, die einander überschreiben können; daher sollte der spezifischste Matcher zuletzt ausgewertet werden.

- Der Inhalt der Direktive [`route`](/docs/caddyfile/directives/route) ignoriert alle obigen Regeln und behält die Reihenfolge bei, in der die Direktiven darin erscheinen.
