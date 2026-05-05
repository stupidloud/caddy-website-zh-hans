---
title: uri (Caddyfile directive)
---

# uri

Manipuliert die URI einer Anfrage. Die Direktive kann Pfadpräfixe/-suffixe entfernen oder Teilstrings in der gesamten URI ersetzen.

Diese Direktive unterscheidet sich von [`rewrite`](rewrite), weil `uri` die URI *differenziell* ändert, statt sie wie `rewrite` auf etwas vollständig anderes zurückzusetzen. Während `rewrite` speziell als interner Redirect behandelt wird, ist `uri` nur eine weitere Middleware.


<a id="syntax"></a>
## Syntax

Mehrere unterschiedliche Operationen werden unterstützt:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

Das erste (Nicht-Matcher-)Argument gibt die Operation an:

- **strip_prefix** entfernt das Präfix aus dem Pfad.

- **strip_suffix** entfernt das Suffix aus dem Pfad.

- **replace** führt eine Teilstring-Ersetzung über die gesamte URI aus.

	- **&lt;target&gt;** ist das Präfix, Suffix oder der Suchstring/reguläre Ausdruck. Bei einem Präfix kann der führende Slash weggelassen werden, da Pfade immer mit einem Slash beginnen.

	- **&lt;replacement&gt;** ist der Ersatzstring. Unterstützt die Verwendung von Capture Groups mit der Syntax `$name` oder `${name}` oder mit einer Zahl für den Index, etwa `$1`. Details finden Sie in der [Go-Dokumentation](https://golang.org/pkg/regexp/#Regexp.Expand). Wenn der Ersatzwert `""` ist, wird der passende Text aus dem Wert entfernt.

	- **&lt;limit&gt;** ist ein optionales Limit für die maximale Anzahl von Ersetzungen.

- **path_regexp** führt eine Ersetzung per regulärem Ausdruck auf dem Pfadteil der URI aus.

	- **&lt;target&gt;** ist das Präfix, Suffix oder der Suchstring/reguläre Ausdruck. Bei einem Präfix kann der führende Slash weggelassen werden, da Pfade immer mit einem Slash beginnen.

	- **&lt;replacement&gt;** ist der Ersatzstring. Unterstützt die Verwendung von Capture Groups mit der Syntax `$name` oder `${name}` oder mit einer Zahl für den Index, etwa `$1`. Details finden Sie in der [Go-Dokumentation](https://golang.org/pkg/regexp/#Regexp.Expand). Wenn der Ersatzwert `""` ist, wird der passende Text aus dem Wert entfernt.

- **query** manipuliert die URI-Query. Der Modus hängt vom Präfix des Parameternamens oder von der Anzahl der Argumente ab. Ein Block kann verwendet werden, um mehrere Operationen auf einmal anzugeben; sie werden gruppiert und in dieser Reihenfolge ausgeführt: umbenennen -> setzen -> anhängen -> ersetzen -> löschen.

	- Ohne Präfix wird der Parameter in der Query auf den angegebenen Wert gesetzt.

	  Zum Beispiel setzt `uri query foo bar` den Wert des Parameters `foo` auf `bar`.

	- Mit dem Präfix `-` wird der Parameter aus der Query entfernt.

	  Zum Beispiel löscht `uri query -foo` den Parameter `foo` aus der Query.

	- Mit dem Präfix `+` wird ein Parameter mit dem angegebenen Wert an die Query angehängt. Ein vorhandener Parameter mit demselben Namen wird dabei *nicht* überschrieben (lassen Sie `+` weg, um zu überschreiben).

	  Zum Beispiel hängt `uri query +foo bar` `foo=bar` an die Query an.

	- Ein Parameter mit `>` als Infix wird auf den Wert nach `>` umbenannt.

	  Zum Beispiel benennt `uri query foo>bar` den Parameter `foo` in `bar` um.

	- Mit drei Argumenten wird eine Ersetzung des Query-Werts per regulärem Ausdruck durchgeführt: Das erste Argument ist der Name des Query-Parameters, das zweite der Suchwert und das dritte der Ersatz. Das erste Argument (Parametername) kann `*` sein, um die Ersetzung auf alle Query-Parameter anzuwenden.

	  Unterstützt die Verwendung von Capture Groups mit der Syntax `$name` oder `${name}` oder mit einer Zahl für den Index, etwa `$1`. Details finden Sie in der [Go-Dokumentation](https://golang.org/pkg/regexp/#Regexp.Expand). Wenn der Ersatzwert `""` ist, wird der passende Text aus dem Wert entfernt.

	  Zum Beispiel würde `uri query foo ^(ba)r $1z` den Wert des Parameters `foo` ersetzen, wenn der Wert mit `bar` beginnt, sodass der Wert zu `baz` wird.

URI-Mutationen erfolgen auf der normalisierten oder nicht escapeten Form der URI. Escape-Sequenzen können jedoch in Präfix- oder Suffixmustern verwendet werden, um nur diese literalen Escapes an diesen Positionen im Anfragepfad abzugleichen. Zum Beispiel schreibt `uri strip_prefix /a/b` sowohl `/a/b/c` als auch `/a%2Fb/c` zu `/c` um; und `uri strip_prefix /a%2Fb` schreibt `/a%2Fb/c` zu `/c` um, passt aber nicht auf `/a/b/c`.

Der URI-Pfad wird vor Änderungen von Directory-Traversal-Punkten bereinigt. Zusätzlich werden mehrere Slashes (wie `//`) zusammengeführt, außer `<target>` enthält ebenfalls mehrere Slashes.

<a id="similar-directives"></a>
## Ähnliche Direktiven

Einige andere Direktiven können ebenfalls die Anfrage-URI manipulieren.

- [`rewrite`](rewrite) ändert den gesamten Pfad und die Query auf einen neuen Wert, statt den Wert nur teilweise zu ändern.

- [`handle_path`](handle_path) macht dasselbe wie [`handle`](handle), entfernt aber ein Präfix aus der Anfrage, bevor seine Handler ausgeführt werden. Es kann in vielen Fällen anstelle von `uri strip_prefix` verwendet werden, um eine zusätzliche Konfigurationszeile zu vermeiden.


<a id="examples"></a>
## Beispiele

`/api` vom Anfang aller Anfragepfade entfernen:

```caddy-d
uri strip_prefix /api
```

`.php` vom Ende aller Anfragepfade entfernen:

```caddy-d
uri strip_suffix .php
```

"/docs/" in jeder Anfrage-URI durch "/v1/docs/" ersetzen:

```caddy-d
uri replace /docs/ /v1/docs/
```

Alle wiederholten Slashes im Anfragepfad (aber nicht in der Anfrage-Query) zu einem einzelnen Slash zusammenfassen:

```caddy-d
uri path_regexp /{2,} /
```

Den Wert des Query-Parameters `foo` auf `bar` setzen:

```caddy-d
uri query foo bar
```

Den Parameter `foo` aus der Query entfernen:

```caddy-d
uri query -foo
```

Den Query-Parameter `foo` in `bar` umbenennen:

```caddy-d
uri query foo>bar
```

Den Parameter `bar` an die Query anhängen:

```caddy-d
uri query +foo bar
```

Den Wert des Query-Parameters `foo`, dessen Wert mit `bar` beginnt, durch `baz` ersetzen:

```caddy-d
uri query foo ^(ba)r $1z
```

Mehrere Query-Operationen auf einmal ausführen:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
