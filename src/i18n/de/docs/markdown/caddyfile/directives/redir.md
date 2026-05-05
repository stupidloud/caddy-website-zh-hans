---
title: redir (Caddyfile directive)
---

# redir

Gibt eine HTTP-Weiterleitung an den Client aus.

Diese Direktive bedeutet, dass ein gematchter Request in seiner aktuellen Form abgelehnt wird und der Client es unter einer anderen URL erneut versuchen soll. Aus diesem Grund liegt ihre [Direktivenreihenfolge](/docs/caddyfile/directives#directive-order) sehr früh.


<a id="syntax"></a>
## Syntax

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** ist das Ziel. Es wird zum [`Location`-Header der Response <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location).

- **&lt;code&gt;** ist der HTTP-Statuscode, der für die Weiterleitung verwendet wird. Kann Folgendes sein:

	- Eine positive ganze Zahl im Bereich `3xx` oder `401`

	- `temporary` für eine temporäre Weiterleitung (`302`, dies ist der Standard)

	- `permanent` für eine permanente Weiterleitung (`301`)

	- `html`, um ein HTML-Dokument zur Durchführung der Weiterleitung zu verwenden (nützlich für Browser-Weiterleitungen, aber nicht für API-Clients)

	- Ein Platzhalter mit einem Statuscode-Wert



<a id="examples"></a>
## Beispiele

Alle Requests auf `https://example.com` weiterleiten:

```caddy
www.example.com {
	redir https://example.com
}
```

Dasselbe, aber die vorhandene URI beibehalten, indem der [`{uri}`-Platzhalter](/docs/caddyfile/concepts#placeholders) angehängt wird:

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

Dasselbe, aber permanent:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Ihre alte Seite `/about-us` auf Ihre neue Seite `/about` weiterleiten:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
