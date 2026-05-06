---
title: push (Caddyfile 指令)
---

<a id="push"></a>
# push

設定伺服器使用 HTTP/2 server push 主動向用戶端傳送資源。

可以透過在回應中指定 Link 標頭來連結資源以進行 server push。此指令將自動推送由上游 Link 標頭中以下列格式描述的資源：

- `&lt;resource&gt;; as=script`
- `&lt;resource&gt;; as=script,&lt;resource&gt;; as=style`
- `&lt;resource&gt;; nopush`
- `&lt;resource&gt;;&lt;resource2&gt;;...`

其中 &lt;resource&gt; 以正斜線 `/` 開頭（即具有相同主機的 URI 路徑）。只有相同主機的資源才能被推送。如果連結的資源是外部資源，或者它具有 `nopush` 屬性，則不會被推送。

預設情況下，push 請求將包含一些被認為可以從原始請求中安全複製的標頭：

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

因為假設許多請求在沒有這些標頭的情況下會失敗；這些不需要手動設定。

Push 請求在內部是虛擬化的，因此非常輕量。


<a id="syntax"></a>
## Syntax

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** 是推送的目標 URI 路徑。如果在區塊內使用，可以選擇在前面加上方法（GET 或 POST；預設為 GET）。
- **&lt;headers&gt;** 使用與 [`header` 指令](/docs/caddyfile/directives/header) 相同的語法來操作 push 請求的標頭。某些標頭預設會被繼承，不需要明確設定（見上文）。


<a id="examples"></a>
## Examples

推送回應中由 `Link` 標頭描述的任何資源：

```caddy-d
push
```

同上，但也針對所有請求推送 `/resources/style.css`：

```caddy-d
push * /resources/style.css
```

僅在用戶端請求 `/foo.html` 時推送 `/foo.jpg`：

```caddy-d
push /foo.html /foo.jpg
```
