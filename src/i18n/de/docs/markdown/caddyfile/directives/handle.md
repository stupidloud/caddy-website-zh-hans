---
title: handle (Caddyfile directive)
---

# handle

Wertet eine Gruppe von Direktiven gegenseitig exklusiv zu anderen `handle`-Blöcken auf derselben Verschachtelungsebene aus.

Mit anderen Worten: Wenn mehrere `handle`-Direktiven nacheinander erscheinen, wird nur der erste *passende* `handle`-Block ausgewertet. Ein `handle` ohne Matcher wirkt wie eine *Fallback*-Route.

Die `handle`-Direktiven werden anhand ihrer Matcher nach dem [Sortieralgorithmus für Direktiven](/docs/caddyfile/directives#sorting-algorithm) sortiert. Die Direktive [`handle_path`](handle_path) ist ein Spezialfall und wird mit derselben Priorität sortiert wie ein `handle` mit einem Path-Matcher.

Handle-Blöcke können bei Bedarf verschachtelt werden. Innerhalb von Handle-Blöcken können nur HTTP-Handler-Direktiven verwendet werden.

<a id="syntax"></a>
## Syntax

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** ist eine Liste von HTTP-Handler-Direktiven oder Direktivenblöcken, eine pro Zeile, genauso wie sie außerhalb eines `handle`-Blocks verwendet würden.



<a id="similar-directives"></a>
## Ähnliche Direktiven

Es gibt weitere Direktiven, die HTTP-Handler-Direktiven umschließen können, aber jede hat ihren eigenen Zweck, abhängig vom gewünschten Verhalten:

- [`handle_path`](handle_path) macht dasselbe wie `handle`, entfernt aber vor dem Ausführen seiner Handler ein Präfix aus dem Request.

- [`handle_errors`](handle_errors) ist wie `handle`, wird aber nur aufgerufen, wenn Caddy während der Request-Verarbeitung auf einen Fehler trifft.

- [`route`](route) umschließt andere Direktiven wie `handle`, aber mit zwei Unterschieden:
  1. route-Blöcke schließen sich gegenseitig nicht aus,
  2. Direktiven innerhalb einer Route werden nicht [neu sortiert](/docs/caddyfile/directives#directive-order), sodass Sie bei Bedarf mehr Kontrolle haben.



<a id="examples"></a>
## Beispiele

Requests in `/foo/` mit dem statischen Dateiserver behandeln und andere Requests mit dem Reverse Proxy:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

Sie können `handle` und [`handle_path`](handle_path) in derselben Site mischen; sie bleiben trotzdem gegenseitig exklusiv:

```caddy
example.com {
	handle_path /foo/* {
		# Das Präfix "/foo" wurde aus dem Pfad entfernt
	}

	handle /bar/* {
		# Der Pfad behält weiterhin "/bar"
	}
}
```

Sie können `handle`-Blöcke verschachteln, um komplexere Routing-Logik zu erstellen:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Dieser Block passt nur auf Pfade unter /foo/bar
		}

		handle {
			# Dieser Block passt auf alles andere unter /foo/
		}
	}

	handle {
		# Dieser Block passt auf alles andere (wirkt als Fallback)
	}
}
```
