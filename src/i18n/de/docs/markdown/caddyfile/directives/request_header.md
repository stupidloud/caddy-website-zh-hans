---
title: request_header (Caddyfile directive)
---

# request_header

Manipuliert HTTP-Header-Felder im Request. Sie kann Header-Werte setzen, hinzufügen und löschen oder Ersetzungen mit regulären Ausdrücken durchführen.

Wenn Sie Header für Proxying manipulieren möchten, verwenden Sie stattdessen die [`header_up`-Subdirektive](/docs/caddyfile/directives/reverse_proxy#header_up) von `reverse_proxy`, da diese Manipulationen proxy-aware sind.

Um HTTP-Response-Header zu manipulieren, können Sie die Direktive [`header`](header) verwenden.


<a id="syntax"></a>
## Syntax

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** ist der Name des Header-Felds.

  Ohne Präfix wird das Feld gesetzt (überschrieben).

  Mit dem Präfix `+` wird das Feld hinzugefügt, statt ein vorhandenes Feld zu überschreiben (zu setzen), falls es bereits existiert; Header-Felder können in einem Request mehr als einmal vorkommen.

  Mit dem Präfix `-` wird das Feld gelöscht. Das Feld darf Präfix- oder Suffix-Wildcards `*` verwenden, um alle passenden Felder zu löschen.

- **&lt;value&gt;** ist der Wert des Header-Felds, wenn ein Feld hinzugefügt oder gesetzt wird.

- **&lt;find&gt;** ist die Teilzeichenkette oder der reguläre Ausdruck, nach der bzw. dem gesucht wird.

- **&lt;replace&gt;** ist der Ersatzwert; erforderlich, wenn eine Suchen-und-Ersetzen-Operation durchgeführt wird.


<a id="examples"></a>
## Beispiele

Den Referer-Header aus dem Request entfernen:

```caddy-d
request_header -Referer
```

Alle Header, die einen Unterstrich enthalten, aus dem Request löschen:

```caddy-d
request_header -*_*
```
