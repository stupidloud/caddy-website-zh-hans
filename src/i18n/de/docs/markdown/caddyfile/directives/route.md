---
title: route (Caddyfile directive)
---

# route

Wertet eine Gruppe von Direktiven wörtlich und als eine Einheit aus.

Direktiven in einem route-Block werden nicht [intern neu sortiert](/docs/caddyfile/directives#directive-order). In einem route-Block können nur HTTP-Handler-Direktiven verwendet werden (Direktiven, die Handler oder Middleware zur Kette hinzufügen).

Diese Direktive ist ein Sonderfall, weil ihre Unterdirektiven ebenfalls normale Direktiven sind.


<a id="syntax"></a>
## Syntax

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** ist eine Liste von Direktiven oder Direktivenblöcken, eine pro Zeile, genau wie außerhalb eines route-Blocks; diese Direktiven werden jedoch nicht neu sortiert. Es können nur HTTP-Handler-Direktiven verwendet werden.



<a id="utility"></a>
## Nutzen

Die Direktive `route` ist in bestimmten fortgeschrittenen Anwendungsfällen oder Randfällen hilfreich, um die absolute Kontrolle über Teile der HTTP-Handlerkette zu übernehmen.

Da die Reihenfolge der Auswertung von HTTP-Middleware wichtig ist, sortiert Caddyfile Direktiven nach dem Parsen normalerweise neu, damit das Caddyfile einfacher zu verwenden ist; Sie müssen sich nicht darum kümmern, in welcher Reihenfolge Sie Dinge tippen.

Die [eingebaute Reihenfolge](/docs/caddyfile/directives#directive-order) ist zwar mit den meisten Sites kompatibel, aber manchmal müssen Sie die Reihenfolge manuell kontrollieren, entweder für die ganze Site oder nur für einen Teil davon. Genau dafür ist die Direktive `route` gedacht.

Betrachten wir zur Veranschaulichung zwei terminierende Handler: [`redir`](redir) und [`file_server`](file_server). Beide schreiben die Antwort an den Client und rufen den nächsten Handler in der Kette nicht auf; für eine bestimmte Anfrage wird also nur einer von beiden ausgeführt. Welcher kommt zuerst? Normalerweise wird `redir` vor `file_server` ausgeführt, weil man üblicherweise nur in bestimmten Fällen einen Redirect ausgeben und im allgemeinen Fall Dateien ausliefern möchte.

Es kann jedoch Situationen geben, in denen die erste Direktive (`file_server`) einen spezifischeren Matcher hat als die zweite (`redir`). Anders gesagt: Sie möchten im allgemeinen Fall umleiten und nur eine bestimmte Datei ausliefern.

Dann könnten Sie ein Caddyfile wie dieses versuchen (aber es funktioniert nicht wie erwartet!):

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

Das Problem ist, dass `redir` nach dem [Sortieren der Direktiven](/docs/caddyfile/directives#sorting-algorithm) vor `file_server` kommt.

In diesem Fall ist der Matcher für `redir` (ein implizites [`*`](/docs/caddyfile/matchers#wildcard-matchers)) aber eine Obermenge des Matchers für `file_server` (`*` ist eine Obermenge von `/specific.html`).

Glücklicherweise ist die Lösung einfach: Packen Sie diese beiden Direktiven in einen `route`-Block, um sicherzustellen, dass `file_server` vor `redir` ausgeführt wird:

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

Eine andere Möglichkeit wäre, die beiden Matcher gegenseitig exklusiv zu machen. Das kann jedoch schnell komplex werden, wenn es mehr als eine oder zwei Bedingungen gibt. Mit der Direktive `route` ist die gegenseitige Exklusivität der beiden Handler implizit, weil beide terminale Handler sind.

</aside>

Jetzt wird `file_server` vor `redir` in die Kette eingefügt, weil die Reihenfolge wörtlich übernommen wird.



<a id="similar-directives"></a>
## Ähnliche Direktiven

Es gibt weitere Direktiven, die HTTP-Handler-Direktiven umschließen können. Jede hat ihren Nutzen, abhängig davon, welches Verhalten Sie ausdrücken möchten:

- [`handle`](handle) umschließt andere Direktiven wie `route`, aber mit zwei Unterschieden: 1) handle-Blöcke sind untereinander gegenseitig exklusiv, und 2) Direktiven innerhalb eines handle werden normal [neu sortiert](/docs/caddyfile/directives#directive-order).

- [`handle_path`](handle_path) macht dasselbe wie `handle`, entfernt aber ein Präfix von der Anfrage, bevor die Handler ausgeführt werden.

- [`handle_errors`](handle_errors) ist wie `handle`, wird aber nur aufgerufen, wenn Caddy während der Anfrageverarbeitung auf einen Fehler stößt.



<a id="examples"></a>
## Beispiele

Anfragen an `/api` unverändert per Proxy weiterleiten und alle anderen Anfragen anhand dessen umschreiben, ob sie einer Datei auf der Festplatte entsprechen, andernfalls nach `/index.html`. Anschließend wird diese Datei ausgeliefert.

Da [`try_files`](try_files) eine höhere Direktivenreihenfolge als [`reverse_proxy`](reverse_proxy) hat, würde es normalerweise höher einsortiert und zuerst ausgeführt. Dadurch würden alle API-Anfragen nach `/index.html` umgeschrieben und nicht mehr auf `/api*` passen; keine davon würde per Proxy weitergeleitet, sondern stattdessen in einem `404` von [`file_server`](file_server) enden. Alles in `route` einzuschließen stellt sicher, dass `reverse_proxy` immer zuerst ausgeführt wird, bevor die Anfrage umgeschrieben wird.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Das ist nicht die einzige Lösung für dieses Problem. Sie könnten auch ein Paar [`handle`](handle)-Blöcke verwenden, wobei der erste auf `/api*` passt und zu `reverse_proxy` führt, während der zweite als Fallback dient und die Dateien ausliefert. Siehe [dieses Beispiel](/docs/caddyfile/patterns#single-page-apps-spas) einer SPA.

</aside>
