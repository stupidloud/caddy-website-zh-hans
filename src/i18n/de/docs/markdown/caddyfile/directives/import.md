---
title: import (Caddyfile directive)
---

# import

Bindet ein [Snippet](/docs/caddyfile/concepts#snippets) oder eine Datei ein und ersetzt diese Direktive durch den Inhalt des Snippets oder der Datei.

Diese Direktive ist ein Spezialfall: Sie wird ausgewertet, bevor die Struktur geparst wird, und kann überall im Caddyfile erscheinen.

<a id="syntax"></a>
## Syntax

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** ist der Dateiname, das Glob-Muster oder der Name eines einzubindenden [Snippets](/docs/caddyfile/concepts#snippets). Sein Inhalt ersetzt diese Zeile so, als hätte der Dateiinhalt von Anfang an hier gestanden.

  Es ist ein Fehler, wenn eine bestimmte Datei nicht gefunden werden kann; ein leeres Glob-Muster ist jedoch kein Fehler.

  Beim Import einer bestimmten Datei wird eine Warnung ausgegeben, wenn die Datei leer ist.

  Wenn das Muster ein Dateiname oder Glob ist, ist es immer relativ zu der Datei, in der `import` erscheint.

  Wenn ein Glob-Muster `*` als letztes Pfadsegment verwendet, werden versteckte Dateien (d. h. Dateien, die mit `.` beginnen) ignoriert. Um versteckte Dateien zu importieren, verwenden Sie `.*` als letztes Segment.
- **&lt;args...&gt;** ist eine optionale Liste von Argumenten, die an die importierten Tokens übergeben werden. Dieser Platzhalter ist ein Spezialfall und wird zur Caddyfile-Parse-Zeit ausgewertet, nicht zur Laufzeit. Sie können in verschiedenen Formen verwendet werden, ähnlich wie [Gos Slice-Syntax](https://gobyexample.com/slices):
  - `{args[n]}`, wobei `n` der 0-basierte Positionsindex des Parameters ist
  - `{args[:]}`, wobei alle Argumente eingefügt werden
  - `{args[:m]}`, wobei die Argumente vor `m` eingefügt werden
  - `{args[n:]}`, wobei die Argumente ab `n` eingefügt werden
  - `{args[n:m]}`, wobei die Argumente im Bereich zwischen `n` und `m` eingefügt werden

  Bei den Formen, die viele Tokens einfügen, **muss** der Platzhalter ein eigenständiges [Token](/docs/caddyfile/concepts#tokens-and-quotes) sein; er darf nicht Teil eines anderen Tokens sein. Mit anderen Worten: Er muss von Leerzeichen umgeben sein und darf nicht in Anführungszeichen stehen.

  Beachten Sie, dass vor v2.7.0 die Syntax `{args.N}` war; diese Form wurde zugunsten der flexibleren Syntax oben deprecated.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** ist ein optionaler Block, der an die importierten Tokens übergeben wird. Dieser Platzhalter ist ein Spezialfall und wird rekursiv zur Caddyfile-Parse-Zeit ausgewertet, nicht zur Laufzeit. Er kann in zwei Formen verwendet werden:
  - `{block}`, wobei der Inhalt des gesamten bereitgestellten Blocks anstelle des Platzhalters eingesetzt wird
  - `{blocks.key}`, wobei `key` das erste Token eines Parameters innerhalb des bereitgestellten Blocks ist


<a id="examples"></a>
## Beispiele

Alle Dateien in einem benachbarten Ordner sites-enabled importieren (außer versteckten Dateien):

```caddy-d
import sites-enabled/*
```

Ein Snippet importieren, das CORS-Header mithilfe eines Import-Arguments setzt:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Ein Snippet importieren, das eine Liste von Proxy-Upstreams als Argumente annimmt:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Ein Snippet importieren, das einen Proxy mit einer Prefix-Rewrite-Regel als erstem Argument erstellt:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Ein Snippet importieren, das mit einer konfigurierbaren "hello world"-Meldung und einem Content-Type antwortet:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Ein Snippet importieren, das erweiterbare Optionen für einen Reverse Proxy bereitstellt:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Ein Snippet importieren, das beliebige Direktiven bereitstellt, aber mit vorgeladener Middleware:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
