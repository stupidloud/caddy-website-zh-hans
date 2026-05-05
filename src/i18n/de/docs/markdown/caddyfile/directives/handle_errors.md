---
title: handle_errors (Caddyfile directive)
---

# handle_errors

Richtet Fehler-Handler ein.

Wenn die normalen HTTP-Request-Handler einen Fehler zurückgeben, stoppt die normale Verarbeitung und die Fehler-Handler werden aufgerufen. Fehler-Handler bilden eine Route, die normalen Routes entspricht, und sie können alles tun, was normale Routes tun können. Das ermöglicht viel Kontrolle und Flexibilität beim Behandeln von Fehlern während HTTP-Requests. Zum Beispiel können Sie statische Fehlerseiten ausliefern, templatisierte Fehlerseiten verwenden oder per Reverse Proxy an ein anderes Backend weiterleiten, das Fehler behandelt.

Die Direktive kann mit verschiedenen Statuscodes wiederholt werden, um unterschiedliche Fehler unterschiedlich zu behandeln. Wenn keine Statuscodes angegeben sind, passt sie auf jeden Fehler und wirkt als Fallback, wenn kein anderer Fehler-Handler passt.

Der Kontext eines Requests wird in Error-Routes übernommen; daher bleiben alle Werte, die im Request-Kontext gesetzt wurden, etwa [Site-Root](root) oder [vars](vars), auch in Fehler-Handlern erhalten. Zusätzlich sind beim Behandeln von Fehlern [neue Platzhalter](#placeholders) verfügbar.

Beachten Sie, dass bestimmte Direktiven, zum Beispiel [`reverse_proxy`](reverse_proxy), die eine Response mit einem HTTP-Status schreiben können, der als Fehler klassifiziert wird, die Error-Routes *nicht* auslösen.

Sie können die Direktive [`error`](error) verwenden, um anhand eigener Routing-Entscheidungen explizit einen Fehler auszulösen.


<a id="syntax"></a>
## Syntax

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** sind ein oder mehrere HTTP-Statuscodes, gegen die der behandelte Fehler abgeglichen wird. Die Statuscodes können dreistellige Zahlen sein oder die Sonderfälle `4xx` beziehungsweise `5xx`, die alle Statuscodes im Bereich 400-499 beziehungsweise 500-599 matchen. Wenn keine Statuscodes angegeben sind, passt die Direktive auf jeden Fehler und wirkt als Fallback, wenn kein anderer Fehler-Handler passt.

- **<directives...>** ist eine Liste von HTTP-Handler-[Direktiven](/docs/caddyfile/directives) und [Matchern](/docs/caddyfile/matchers), eine pro Zeile.


<a id="placeholders"></a>
## Platzhalter

Die folgenden Platzhalter sind während der Fehlerbehandlung verfügbar. Sie sind [Caddyfile-Kurzformen](/docs/caddyfile/concepts#placeholders) für die vollständigen Platzhalter, die in [den JSON-Dokumenten für Error-Routes eines HTTP-Servers](/docs/json/apps/http/servers/errors/#routes) zu finden sind.

| Platzhalter | Beschreibung |
|---|---|
| `{err.status_code}` | Der empfohlene HTTP-Statuscode |
| `{err.status_text}` | Der zum empfohlenen Statuscode gehörende Statustext |
| `{err.message}` | Die Fehlermeldung |
| `{err.trace}` | Der Ursprung des Fehlers |
| `{err.id}` | Eine Kennung für dieses Auftreten des Fehlers |


<a id="examples"></a>
## Beispiele

Eigene Fehlerseiten basierend auf dem Statuscode (d. h. eine Seite namens `404.html` für `404`-Fehler). Beachten Sie, dass [`file_server`](file_server) den HTTP-Statuscode des Fehlers beibehält, wenn es in `handle_errors` ausgeführt wird (setzt voraus, dass Sie vorher einen [Site-Root](root) in Ihrer Site gesetzt haben):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Eine einzelne Fehlerseite, die [`templates`](templates) verwendet, um eine eigene Fehlermeldung zu schreiben:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Wenn Sie eigene Fehlerseiten nur für einige Fehlercodes bereitstellen möchten, können Sie die Existenz der eigenen Fehlerdateien vorher mit einem [`file`](/docs/caddyfile/matchers#file)-Matcher prüfen:

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

Reverse Proxy zu einem professionellen Server, der hochqualifiziert für HTTP-Fehlerbehandlung ist und Ihren Tag verbessert:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Einfach [`respond`](respond) verwenden, um Fehlercode und Namen zurückzugeben

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Bestimmte Fehlercodes unterschiedlich behandeln:

```caddy-d
handle_errors 404 410 {
	respond "It's a 404 or 410 error!"
}

handle_errors 5xx {
	respond "It's a 5xx error."
}

handle_errors {
	respond "It's another error"
}
```

Das obige verhält sich genauso wie das folgende Beispiel, das einen [`expression`](/docs/caddyfile/matchers#expression)-Matcher gegen die Statuscodes verwendet und [`handle`](handle) für gegenseitige Exklusivität nutzt:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "It's a 404 or 410 error!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "It's a 5xx error."
	}

	handle {
		respond "It's another error"
	}
}
```
