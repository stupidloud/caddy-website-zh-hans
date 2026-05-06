---
title: method (Caddyfile 指令)
---

<a id="method"></a>
# method

更改請求上的 HTTP method。


<a id="syntax"></a>
## 語法

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** 是要將請求更改為的 HTTP method。


<a id="examples"></a>
## 範例

將 /api 下的所有請求的 method 更改為 POST：

```caddy-d
method /api* POST
```
