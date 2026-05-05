---
title: rewrite (Caddyfile directive)
---

# rewrite

リクエスト URI を内部的に書き換えます。

rewrite は、リクエスト URI の一部または全体を変更します。URI には scheme や authority（host と port）は含まれず、通常 client は fragment を送信しないことに注意してください。そのため、このディレクティブは主に **path** と **query** 文字列の操作に使われます。

`rewrite` ディレクティブは、変更を加えたうえでリクエストを受け付ける意図を表します。

同じブロック内の他の `rewrite` ディレクティブとは相互排他的です。そのため、本来なら互いに cascade してしまう rewrite を定義しても、最初に一致した rewrite だけが実行されるので安全です。

`rewrite` の前にリクエストに一致していた [request matcher](/docs/caddyfile/matchers) は、`rewrite` 後の同じリクエストには一致しない可能性があります。`rewrite` を他の handler と同じ route で共有したい場合は、[`route`](route) または [`handle`](handle) ディレクティブを使用してください。


<a id="syntax"></a>
## 構文

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** は、リクエストの書き換え先 URI です。rewrite で指定された URI の構成要素（path または query 文字列）だけが操作されます。URI path は `?` より前の任意の部分文字列です。`?` を省略した場合、token 全体が path とみなされます。

v2.8.0 より前では、`<to>` 引数が `/` で始まる場合、parser が [matcher token](/docs/caddyfile/matchers#syntax) と混同する可能性があったため、ワイルドカード matcher token（`*`）を指定する必要がありました。


<a id="similar-directives"></a>
## 類似ディレクティブ

rewrite を行う他のディレクティブもありますが、意図が異なるか、URI を完全に置き換えずに rewrite します。

- [`uri`](uri) は URI を操作します（prefix、suffix、または部分文字列の置換）。

- [`try_files`](try_files) は、ファイルの存在に基づいてリクエストを書き換えます。



<a id="examples"></a>
## 例

すべてのリクエストを `index.html` に書き換え、query 文字列は変更しません。

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

v2.8.0 より前では、最初の引数が [path matcher](/docs/caddyfile/matchers#path-matchers) と曖昧になるため、ここでは [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers) が必要でした。つまり `rewrite * /foo` のように書く必要がありましたが、現在は `rewrite /foo` に簡略化できます。

</aside>

すべてのリクエストに `/api` を prefix として付け、URI の残りを保持したうえで、app に reverse proxy します。

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

API リクエストの query 文字列を `a=b` に置き換え、path は変更しません。

```caddy
example.com {
	rewrite ?a=b
}
```

`/api/` へのリクエストだけ、既存の query 文字列を保持しつつ key-value ペアを追加します。

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

path と query 文字列の両方を変更し、元の query 文字列を保持しながら、元の path を `p` パラメータとして追加します。

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
