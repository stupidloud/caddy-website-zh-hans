---
title: request_header (Caddyfile 指令)
---

<a id="request-header"></a>
# request_header

操作請求中的 HTTP 標頭欄位。它可以設定、新增和刪除標頭值，或使用正規表達式進行替換。

如果您打算針對代理操作標頭，請改用 `reverse_proxy` 的 [`header_up` 子指令](/docs/caddyfile/directives/reverse_proxy#header_up)，因為這些操作是感知代理的。

若要操作 HTTP 回應標頭，您可以使用 [`header`](header) 指令。


<a id="syntax"></a>
## 語法

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** 是標頭欄位的名稱。

  如果不加前綴，則設定（覆寫）該欄位。

  加上前綴 `+` 以新增欄位，而不是在欄位已存在時進行覆寫（設定）；標頭欄位在請求中可以出現多次。

  加上前綴 `-` 以刪除欄位。欄位可以使用前綴或後綴 `*` 通配符來刪除所有相應的欄位。

- **&lt;value&gt;** 是標頭欄位的值（如果要新增或設定欄位）。

- **&lt;find&gt;** 是要搜尋的子字串或正規表達式。

- **&lt;replace&gt;** 是替換值；如果執行搜尋並替換，則為必填。


<a id="examples"></a>
## 範例

從請求中移除 Referer 標頭：

```caddy-d
request_header -Referer
```

從請求中刪除所有包含底線的標頭：

```caddy-d
request_header -*_*
```
