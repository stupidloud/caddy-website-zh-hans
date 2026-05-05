---
title: vars (Caddyfile directive)
---

# vars

Setzt eine oder mehrere Variablen auf einen bestimmten Wert, damit sie später in der Anfrageverarbeitungskette verwendet werden können.

Der primäre Weg, auf Variablen zuzugreifen, sind Platzhalter der Form `{vars.variable_name}` oder die Request Matcher [`vars`](/docs/caddyfile/matchers#vars) und [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

Sie können Variablen mit der Direktive [`templates`](templates) über die Funktion `placeholder` verwenden, zum Beispiel: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

Als Sonderfall ist es möglich, die Variable `http.auth.user.id` zu überschreiben, die im Replacer gespeichert ist, um das Feld `user_id` in [Access Logs](log) zu aktualisieren.


<a id="syntax"></a>
## Syntax

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** ist der zu setzende Variablenname.

- **&lt;value&gt;** ist der Wert der Variable.

  Der Wert wird nach Möglichkeit typkonvertiert; `true` und `false` werden in boolesche Typen konvertiert, numerische Werte entsprechend in Integer oder Float. Um diese Konvertierung zu vermeiden und die Werte als Strings zu behalten, können Sie sie in [Anführungszeichen](/docs/caddyfile/concepts#tokens-and-quotes) setzen.

<a id="examples"></a>
## Beispiele

Eine einzelne Variable setzen, deren Wert vom Anfragepfad abhängt, und dann mit dem Wert antworten:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

Mehrere Variablen setzen, jede in den passenden skalaren Typ konvertiert:

```caddy-d
vars {
	# boolean
	abc true

	# integer
	def 1

	# float
	ghi 2.3

	# string
	jkl "example"
}
```
