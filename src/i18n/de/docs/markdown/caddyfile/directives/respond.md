---
title: respond (Caddyfile directive)
---

# respond

Schreibt eine hartcodierte/statische Response an den Client.

Wenn der Body nicht leer ist, setzt diese Direktive den `Content-Type`-Header, falls er noch nicht gesetzt ist. Der Standardwert ist `text/plain; utf-8`, außer der Body ist ein gültiges JSON-Objekt oder -Array; in diesem Fall wird er auf `application/json` gesetzt. Für alle anderen Inhaltstypen setzen Sie den passenden Content-Type explizit mit der [`header`-Direktive](/docs/caddyfile/directives/header).


<a id="syntax"></a>
## Syntax

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** ist der zu schreibende HTTP-Statuscode.

  Wenn `103` (Early Hints), wird die Response ohne Body geschrieben und die Handler-Kette läuft weiter. (HTTP-Responses vom Typ `1xx` sind informativ, nicht final.)

  Standard: `200`

- **&lt;body&gt;** ist der zu schreibende Response-Body.

- **body** ist eine alternative Möglichkeit, einen Body anzugeben; praktisch, wenn er mehrere Zeilen umfasst.

- **close** schließt die Verbindung des Clients zum Server, nachdem die Response geschrieben wurde.

Zur Klarstellung: Das erste Nicht-Matcher-Argument kann entweder ein dreistelliger Statuscode oder eine Response-Body-Zeichenkette sein. Wenn es ein Body ist, kann das nächste Argument der Statuscode sein.

<aside class="tip">

Mit einem Fehlerstatuscode zu antworten ist etwas anderes, als in der Handler-Kette einen Fehler zurückzugeben, wodurch intern Fehler-Handler aufgerufen werden.

</aside>


<a id="examples"></a>
## Beispiele

Einen leeren 200-Status mit leerem Body für alle Health Checks schreiben und einen einfachen Response-Body für alle anderen Requests:

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

Eine Fehler-Response schreiben und die Verbindung schließen:

<aside class="tip">

Möglicherweise bevorzugen Sie stattdessen die Direktive [`error`](error), die einen Fehler auslöst, der mit der Direktive [`handle_errors`](handle_errors) behandelt werden kann.

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

Eine HTML-Response schreiben, mit [heredoc-Syntax](/docs/caddyfile/concepts#heredocs) zur Kontrolle von Whitespace, und zusätzlich den `Content-Type`-Header passend zum Response-Body setzen:

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
