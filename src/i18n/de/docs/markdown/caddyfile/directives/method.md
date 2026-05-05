---
title: method (Caddyfile directive)
---

# method

Ändert die HTTP-Methode des Requests.


<a id="syntax"></a>
## Syntax

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** ist die HTTP-Methode, in die der Request geändert werden soll.


<a id="examples"></a>
## Beispiele

Die Methode für alle Requests unter `/api` auf `POST` ändern:

```caddy-d
method /api* POST
```
