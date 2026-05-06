---
title: root (Caddyfile 指令)
---

# root

設定網站的根路徑，供各種存取檔案系統的 matcher 和指令使用。如果未設定，預設的網站根目錄為目前的工作目錄。

具體而言，此指令會設定 `{http.vars.root}` placeholder。它與同一個區塊中的其他 `root` 指令互斥，因此可以安全地使用相交的 matcher 定義多個根目錄：它們不會串聯並互相覆寫。

此指令不會自動啟用靜態檔案服務，因此通常與 [`file_server` 指令](file_server) 或 [`php_fastcgi` 指令](php_fastcgi) 配合使用。


<a id="syntax"></a>
## 語法

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** 是網站根目錄要使用的路徑。

在 v2.8.0 之前，如果 `<path>` 參數以 `/` 開頭，解析器可能會將其誤認為 [matcher 標記](/docs/caddyfile/matchers#syntax)，因此必須指定萬用字元 matcher 標記 (`*`)。


<a id="examples"></a>
## 範例

將網站根目錄設定為 `/home/bob/public_html` (假設 Caddy 以使用者 `bob` 的身份執行)：

<aside class="tip">

如果你是以 systemd 服務執行 Caddy，從 `/home` 讀取檔案將無法運作，因為 `caddy` 使用者對 `/home` 目錄沒有「執行」權限 (這是走訪目錄所必需的)。建議將檔案放在 `/srv` 或 `/var/www/html` 中。

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

請注意，在 v2.8.0 之前，此處需要 [萬用字元 matcher](/docs/caddyfile/matchers#wildcard-matchers)，因為第一個參數與 [路徑 matcher](/docs/caddyfile/matchers#path-matchers) 有歧義，例如 `root * /srv`，但現在可以簡化為 `root /srv`。

</aside>


為所有請求將網站根目錄設定為 `public_html` (相對於目前的工作目錄)：

```caddy-d
root public_html
```

僅針對 `/foo/*` 中的請求更改網站根目錄：

```caddy-d
root /foo/* /home/user/public_html/foo
```

`root` 指令通常與 [`file_server`](file_server) 搭配使用以提供靜態檔案服務，及/或與 [`php_fastcgi`](php_fastcgi) 搭配使用以提供 PHP 網站：

```caddy
example.com {
	root /srv
	file_server
}
```
