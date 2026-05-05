---
title: method (Caddyfile directive)
---

# method

リクエストの HTTP method を変更します。


<a id="syntax"></a>
## 構文

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** は、リクエストを変更する先の HTTP method です。


<a id="examples"></a>
## 例

`/api` 配下のすべてのリクエストの method を `POST` に変更します。

```caddy-d
method /api* POST
```
