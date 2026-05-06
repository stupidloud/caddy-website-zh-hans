---
title: method (директива Caddyfile)
---

# method

Изменяет HTTP method в запросе.


<a id="syntax"></a>
## Синтаксис

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** — HTTP method, на который нужно изменить запрос.


<a id="examples"></a>
## Примеры

Изменить method для всех запросов под `/api` на `POST`:

```caddy-d
method /api* POST
```
