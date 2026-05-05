---
title: redir (Caddyfile directive)
---

# redir

クライアントへ HTTP redirect を返します。

このディレクティブは、マッチしたリクエストをそのままでは拒否し、クライアントに別の URL で再試行させることを意味します。そのため、[directive order](/docs/caddyfile/directives#directive-order) は非常に早い位置にあります。


<a id="syntax"></a>
## 構文

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** はリダイレクト先です。レスポンスの [`Location` header <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location) になります。

- **&lt;code&gt;** は redirect に使う HTTP status code です。次を指定できます。

	- `3xx` 範囲の正の整数、または `401`
	
	- `temporary` は一時的な redirect（`302`、これがデフォルト）
	
	- `permanent` は恒久的な redirect（`301`）
	
	- `html` は HTML ドキュメントで redirect を実行します（ブラウザー向けの redirect には便利ですが、API client には向きません）
	
	- status code 値を持つ placeholder



<a id="examples"></a>
## 例

すべてのリクエストを `https://example.com` へ redirect します。

```caddy
www.example.com {
	redir https://example.com
}
```

同じですが、[`{uri}` placeholder](/docs/caddyfile/concepts#placeholders) を追加して既存の URI を保持します。

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

同じですが、恒久的な redirect にします。

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

古い `/about-us` ページを新しい `/about` ページへ redirect します。

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
