---
title: error (Caddyfile directive)
---

# error

Löst einen Fehler in der HTTP-Handler-Kette aus, mit optionaler Meldung und empfohlenem HTTP-Statuscode.

Dieser Handler schreibt keine Response. Stattdessen ist er dafür gedacht, mit der Direktive [`handle_errors`](handle_errors) kombiniert zu werden, um Ihre eigene Fehlerbehandlungslogik aufzurufen.


<a id="syntax"></a>
## Syntax

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** ist der zu schreibende HTTP-Statuscode. Standard ist `500`.
- **&lt;message&gt;** ist die Fehlermeldung. Standardmäßig gibt es keine Fehlermeldung.
- **message** ist eine alternative Möglichkeit, eine Fehlermeldung anzugeben; praktisch, wenn sie mehrere Zeilen umfasst.

Zur Klarstellung: Das erste Nicht-Matcher-Argument kann entweder ein dreistelliger Statuscode oder eine Fehlermeldungszeichenkette sein. Wenn es eine Fehlermeldung ist, kann das nächste Argument der Statuscode sein.


<a id="examples"></a>
## Beispiele

Bei bestimmten Request-Pfaden einen Fehler auslösen und [`handle_errors`](handle_errors) verwenden, um eine Response zu schreiben:

```caddy
example.com {
	root /srv

	# Fehler für bestimmte Pfade auslösen
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Den Fehler behandeln, indem eine HTML-Seite ausgeliefert wird
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
