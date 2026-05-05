---
title: header (Caddyfile directive)
---

# header

Manipuliert HTTP-Response-Header-Felder. Sie kann Header-Werte setzen, hinzufügen und löschen oder Ersetzungen mit regulären Ausdrücken durchführen.

Standardmäßig werden Header-Operationen sofort ausgeführt, außer wenn Header gelöscht werden (`-`-Präfix) oder ein Standardwert gesetzt wird (`?`-Präfix). In diesen Fällen werden die Header-Operationen automatisch bis zu dem Zeitpunkt aufgeschoben, an dem sie an den Client geschrieben werden.

Um HTTP-Request-Header zu manipulieren, können Sie die Direktive [`request_header`](request_header) verwenden.


<a id="syntax"></a>
## Syntax

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# Hinzufügen
	+<field> <value>

	# Setzen
	<field> <value>

	# Mit defer setzen
	><field> <value>

	# Löschen
	-<field>

	# Ersetzen
	<field> <find> <replace>

	# Mit defer ersetzen
	><field> <find> <replace>

	# Standard
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** ist der Name des Header-Felds.

  Ohne Präfix wird das Feld gesetzt (überschrieben).

  Mit dem Präfix `+` wird das Feld hinzugefügt, statt ein vorhandenes Feld zu überschreiben (zu setzen); Header-Felder können in einer Response mehr als einmal vorkommen.

  Mit dem Präfix `-` wird das Feld gelöscht. Das Feld darf Präfix- oder Suffix-Wildcards `*` verwenden, um alle passenden Felder zu löschen.

  Mit dem Präfix `?` wird ein Standardwert für das Feld gesetzt. Das Feld wird nur geschrieben, wenn es noch nicht existiert.

  Mit dem Präfix `>` wird das Feld gesetzt und als Kurzform `defer` aktiviert.

- **&lt;value&gt;** ist der Wert des Header-Felds beim Hinzufügen oder Setzen eines Felds.

- **&lt;find&gt;** ist der reguläre Ausdruck, nach dem gesucht wird. Platzhalter können verwendet werden, um dynamische Eingaben in das Suchmuster einzubauen. Die verwendete Sprache für reguläre Ausdrücke ist RE2, enthalten in Go. Siehe die [RE2-Syntaxreferenz](https://github.com/google/re2/wiki/Syntax) und die [Übersicht zur Go-regexp-Syntax](https://pkg.go.dev/regexp/syntax).

- **&lt;replace&gt;** ist der Ersatzwert; erforderlich, wenn eine Suchen-und-Ersetzen-Operation durchgeführt wird. Verwenden Sie `$1` oder `$2` usw., um Capture Groups aus dem Suchmuster zu referenzieren. Wenn der Ersatzwert `""` ist, wird der passende Text aus dem Wert entfernt. Details finden Sie in der [Go-Dokumentation](https://golang.org/pkg/regexp/#Regexp.Expand).

- **defer** verschiebt die Ausführung von Header-Operationen, bis die Response an den Client gesendet wird. Diese Option wird unter folgenden Bedingungen automatisch aktiviert:
	- Wenn Header-Felder mit `-` gelöscht werden.
	- Wenn mit `?` ein Standardwert gesetzt wird.
	- Wenn das Präfix `>` bei einer Setz- oder Ersetzungsoperation verwendet wird.
	- Wenn eine oder mehrere `match`-Bedingungen vorhanden sind.

- **match** <span id="match"/> ist ein inline [Response-Matcher](/docs/caddyfile/response-matchers). Header-Operationen werden nur auf Responses angewendet, die die angegebenen Bedingungen erfüllen.

Für mehrere Header-Manipulationen können Sie einen Block öffnen und eine Manipulation pro Zeile in derselben Weise angeben.

Wenn das Präfix `?` verwendet wird, um einen Standard-Header-Wert zu setzen, wird es automatisch in einen eigenen `header`-Handler getrennt, falls es sich in einem `header`-Block mit mehreren Header-Operationen befand. [Unter der Haube](/docs/modules/http.handlers.headers#response/require) konfiguriert `?` einen [Response-Matcher](/docs/caddyfile/response-matchers), der auf den gesamten Handler der Direktive angewendet wird; dieser wendet die Header-Operationen (wie `defer`) nur an, wenn das Feld noch nicht gesetzt ist.


<a id="examples"></a>
## Beispiele

Ein eigenes Header-Feld auf allen Responses setzen:

```caddy-d
header Custom-Header "My value"
```

Das Header-Feld "Hidden" entfernen:

```caddy-d
header -Hidden
```

`http://` in jedem Location-Header durch `https://` ersetzen:

```caddy-d
header Location http:// https://
```

Sicherheits- und Datenschutz-Header auf allen Seiten setzen: (**WARNUNG:** nur verwenden, wenn Sie die Auswirkungen verstehen!)

```caddy-d
header {
	# FLoC-Tracking deaktivieren
	Permissions-Policy interest-cohort=()

	# HSTS aktivieren
	Strict-Transport-Security max-age=31536000;

	# Clients daran hindern, den Medientyp zu sniffen
	X-Content-Type-Options nosniff

	# Clickjacking-Schutz
	X-Frame-Options DENY
}
```

Mehrere Header-Direktiven, die gegenseitig exklusiv sein sollen:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Eine Standard-Cache-Ablaufzeit setzen, falls der Upstream keine definiert:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Alle erfolgreichen Responses auf GET-Requests für bis zu eine Stunde als cachebar markieren:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Caching von Fehler-Responses verhindern, falls im Upstream-Server eine Ausnahme auftritt:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Light-Mode-Responses getrennt von Dark-Mode-Responses cachebar markieren, wenn der Upstream-Server Client Hints unterstützt:
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Zu großzügige CORS-Header verhindern, indem Wildcard-Werte durch eine bestimmte Domain ersetzt werden:
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**Hinweis**: Bei Ersetzungsoperationen wird der Wert `<find>` als regulärer Ausdruck interpretiert. Um das Zeichen `*` zu matchen, muss es wie im obigen Beispiel mit einem Backslash escaped werden.

Alternativ können Sie einen [Response-Matcher](/docs/caddyfile/response-matchers) verwenden, um einen Header-Wert wörtlich zu matchen:
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Die Cache-Ablaufzeit überschreiben, die ein Proxy-Upstream für Pfade gesetzt hat, die mit `/no-cache` beginnen; `defer` muss aktiviert sein, damit der Header *nachdem* der Proxy seine Header schreibt gesetzt wird:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Ein verzögertes Update eines `Set-Cookie`-Headers durchführen, um `SameSite=None` hinzuzufügen; eine regexp-Capture wird verwendet, um den vorhandenen Wert zu greifen, und `$1` fügt ihn am Anfang wieder ein, mit der zusätzlichen Option angehängt:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
