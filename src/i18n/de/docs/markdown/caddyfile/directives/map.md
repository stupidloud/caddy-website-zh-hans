---
title: map (Caddyfile directive)
---

# map

Setzt Werte eigener Platzhalter anhand eines Eingabewerts.

Sie vergleicht den Quellwert mit der Eingabeseite der Map und wendet bei einem Treffer die Ausgabewerte auf jedes Ziel an. Ziele werden zu Platzhalternamen. Für jedes Ziel können auch Standardausgabewerte angegeben werden.

Gemappte Platzhalter werden erst ausgewertet, wenn sie verwendet werden; daher ist diese Direktive selbst bei sehr großen Mappings ziemlich effizient.

<a id="syntax"></a>
## Syntax

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** ist der Eingabewert, nach dem umgeschaltet wird. In der Regel ein Platzhalter.

- **&lt;destinations...&gt;** sind die zu erstellenden Platzhalter, welche die Ausgabewerte enthalten.

- **&lt;input&gt;** ist der Eingabewert, auf den gematcht wird. Wenn ihm `~` vorangestellt ist, wird er als regulärer Ausdruck behandelt.

- **&lt;outputs...&gt;** sind ein oder mehrere Ausgabewerte, die im zugehörigen Platzhalter gespeichert werden. Die erste Ausgabe wird in das erste Ziel geschrieben, die zweite Ausgabe in das zweite Ziel usw.

  Als Sonderfall behandelt der Caddyfile-Parser Ausgaben, die ein literaler Bindestrich (`-`) sind, als Null-/nil-Werte. Das ist nützlich, wenn Sie für diese bestimmte Ausgabe bei der gegebenen Eingabe auf einen Standardwert zurückfallen möchten, für andere Ausgaben aber Nicht-Standardwerte verwenden wollen.

  Die Ausgaben werden nach Möglichkeit typkonvertiert; `true` und `false` werden in boolesche Typen konvertiert, und numerische Werte entsprechend in Integer oder Float. Um diese Konvertierung zu vermeiden, können Sie die Ausgabe in [Anführungszeichen](/docs/caddyfile/concepts#tokens-and-quotes) setzen; dann bleibt sie eine Zeichenkette.

  Die Anzahl der Ausgaben für jedes Mapping darf die Anzahl der Ziele nicht überschreiten; der Einfachheit halber dürfen es jedoch weniger Ausgaben als Ziele sein, und fehlende Ausgaben werden implizit aufgefüllt.

  Wenn als Eingabe ein regulärer Ausdruck verwendet wurde, können Capture Groups mit `${group}` referenziert werden, wobei `group` entweder der Name oder die Nummer der Capture Group im Ausdruck ist. Capture Group `0` ist der vollständige regexp-Match, `1` die erste Capture Group, `2` die zweite Capture Group usw.

- **&lt;default&gt;** gibt die Ausgabewerte an, die gespeichert werden, wenn keine Eingaben matchen.


<a id="examples"></a>
## Beispiele

Das folgende Beispiel zeigt die meisten Aspekte dieser Direktive:

```caddy-d
map {host}                {my_placeholder}  {magic_number} {
	example.com           "some value"      3
	foo.example.com       "another value"
	~(.*)\.example\.com$  "${1} subdomain"  5

	~.*\.net$             -                 7
	~.*\.xyz$             -                 15

	default               "unknown domain"  42
}
```

Diese Direktive schaltet anhand des Werts von `{host}` um, also des Domainnamens des Requests.

- Wenn der Request für `example.com` ist, wird `{my_placeholder}` auf `some value` und `{magic_number}` auf `3` gesetzt.
- Andernfalls, wenn der Request für `foo.example.com` ist, wird `{my_placeholder}` auf `another value` gesetzt, und `{magic_number}` fällt auf den Standardwert `42` zurück.
- Andernfalls, wenn der Request für eine beliebige Subdomain von `example.com` ist, wird `{my_placeholder}` auf eine Zeichenkette gesetzt, die den Wert der ersten regexp-Capture Group enthält, also die gesamte Subdomain, und `{magic_number}` wird auf 5 gesetzt.
- Andernfalls, wenn der Request für einen beliebigen Host ist, der auf `.net` oder `.xyz` endet, wird nur `{magic_number}` entsprechend auf `7` oder `15` gesetzt. `{my_placeholder}` bleibt ungesetzt.
- Andernfalls (für alle anderen Hosts) gelten die Standardwerte: `{my_placeholder}` wird auf `unknown domain` gesetzt und `{magic_number}` auf `42`.
