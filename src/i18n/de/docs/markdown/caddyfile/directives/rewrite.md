---
title: rewrite (Caddyfile directive)
---

# rewrite

Schreibt die Anfrage-URI intern um.

Ein Rewrite ändert Teile oder die gesamte Anfrage-URI. Beachten Sie, dass die URI weder Schema noch Authority (Host & Port) enthält und Clients üblicherweise keine Fragmente senden. Daher wird diese Direktive hauptsächlich zur Manipulation von **Pfad** und **Query String** verwendet.

Die Direktive `rewrite` drückt aus, dass die Anfrage akzeptiert werden soll, aber mit Änderungen.

Sie ist gegenseitig exklusiv zu anderen `rewrite`-Direktiven im selben Block. Dadurch ist es sicher, Rewrites zu definieren, die sonst ineinander übergehen würden, weil nur der erste passende Rewrite ausgeführt wird.

Ein [Request Matcher](/docs/caddyfile/matchers), der vor dem `rewrite` auf eine Anfrage passt, passt nach dem `rewrite` möglicherweise nicht mehr auf dieselbe Anfrage. Wenn Ihr `rewrite` eine Route mit anderen Handlern teilen soll, verwenden Sie die Direktiven [`route`](route) oder [`handle`](handle).


<a id="syntax"></a>
## Syntax

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** ist die URI, auf die die Anfrage umgeschrieben wird. Nur die Komponenten der URI (Pfad oder Query String), die im Rewrite angegeben werden, werden bearbeitet. Der URI-Pfad ist jeder Teilstring vor `?`. Wird `?` weggelassen, gilt das gesamte Token als Pfad.

Vor v2.8.0 konnte das Argument `<to>` vom Parser mit einem [Matcher-Token](/docs/caddyfile/matchers#syntax) verwechselt werden, wenn es mit `/` begann. Deshalb musste ein Wildcard-Matcher-Token (`*`) angegeben werden.


<a id="similar-directives"></a>
## Ähnliche Direktiven

Es gibt weitere Direktiven, die Rewrites durchführen, aber eine andere Absicht ausdrücken oder die URI ohne vollständigen Austausch umschreiben:

- [`uri`](uri) manipuliert eine URI (Präfix/Suffix entfernen oder Teilstring ersetzen).

- [`try_files`](try_files) schreibt die Anfrage anhand der Existenz von Dateien um.



<a id="examples"></a>
## Beispiele

Alle Anfragen nach `index.html` umschreiben und den Query String unverändert lassen:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Beachten Sie, dass vor v2.8.0 hier ein [Wildcard Matcher](/docs/caddyfile/matchers#wildcard-matchers) erforderlich war, weil das erste Argument mit einem [Path Matcher](/docs/caddyfile/matchers#path-matchers) mehrdeutig ist, also `rewrite * /foo`. Heute kann dies zu `rewrite /foo` vereinfacht werden.

</aside>

Alle Anfragen mit `/api` präfixen, den Rest der URI beibehalten und dann per Reverse Proxy an eine App weiterleiten:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Den Query String bei API-Anfragen durch `a=b` ersetzen und den Pfad unverändert lassen:

```caddy
example.com {
	rewrite ?a=b
}
```

Nur für Anfragen an `/api/` den bestehenden Query String beibehalten und ein Key-Value-Paar hinzufügen:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Sowohl Pfad als auch Query String ändern, dabei den ursprünglichen Query String beibehalten und den ursprünglichen Pfad als Parameter `p` hinzufügen:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
