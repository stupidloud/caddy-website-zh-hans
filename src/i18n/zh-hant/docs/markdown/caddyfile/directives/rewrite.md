---
title: rewrite (Caddyfile 指令)
---

<a id="rewrite"></a>
# rewrite

在內部重寫請求的 URI。

重寫會更改部分或全部的請求 URI。請注意，URI 不包括 scheme 或 authority（主機和連接埠），且用戶端通常不會發送 fragments。因此，此指令主要用於 **path** 和 **query** 字串的操作。

`rewrite` 指令暗示了接受請求的意圖，但會進行修改。

它與同一個區塊中的其他 `rewrite` 指令互斥，因此定義那些本來會級聯到彼此的重寫是安全的，因為只有第一個比對成功的 `rewrite` 會被執行。

在 `rewrite` 之前比對請求的 [request matcher](/docs/caddyfile/matchers) 可能在 `rewrite` 之後不再比對到相同的請求。如果您希望 `rewrite` 與其他 handler 共享一個 route，請使用 [`route`](route) 或 [`handle`](handle) 指令。


<a id="syntax"></a>
## 語法

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** 是要將請求重寫到的 URI。只有在 rewrite 中指定的 URI 組件（path 或查詢字串）才會被操作。URI path 是任何出現在 `?` 之前的子字串。如果省略了 `?`，則整個 token 都會被視為 path。

在 v2.8.0 之前，如果 &lt;to&gt; 參數以 `/` 開頭，解析器可能會將其與 [matcher token](/docs/caddyfile/matchers#syntax) 混淆，因此必須指定一個萬用字元 matcher token (`*`)。


<a id="similar-directives"></a>
## 類似指令

還有其他執行重寫的指令，但暗示了不同的意圖，或者在不完全替換 URI 的情況下進行重寫：

- [`uri`](uri) 操作 URI（去除前綴、後綴或進行子字串替換）。

- [`try_files`](try_files) 根據檔案是否存在來重寫請求。



<a id="examples"></a>
## 範例

將所有請求重寫為 `index.html`，保持任何查詢字串不變：

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

請注意，在 v2.8.0 之前，這裡需要一個 [萬用字元 matcher](/docs/caddyfile/matchers#wildcard-matchers)，因為第一個參數與 [路徑 matcher](/docs/caddyfile/matchers#path-matchers) 產生歧義，例如 `rewrite * /foo`，但現在可以簡化為 `rewrite /foo`。

</aside>

在所有請求前加上 `/api` 前綴，保留 URI 的其餘部分，然後反向代理到應用程式：

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

將 API 請求的查詢字串替換為 `a=b`，保持路徑不變：

```caddy
example.com {
	rewrite ?a=b
}
```

僅針對 `/api/` 的請求，保留現有的查詢字串並添加一個鍵值對：

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

同時更改路徑和查詢字串，保留原始查詢字串，同時將原始路徑添加為 `p` 參數：

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
