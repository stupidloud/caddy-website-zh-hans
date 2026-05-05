---
title: push (Caddyfile directive)
---

# push

HTTP/2 server push を使って、サーバーがクライアントへ先行してリソースを送信するよう設定します。

レスポンスの Link header を指定することで、server push の対象リソースをリンクできます。このディレクティブは、upstream の Link header によって記述されたリソースを、次の形式で自動的に push します。

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

ここで `<resource>` は forward slash `/` で始まります（つまり同じ host の URI path です）。push できるのは同じ host のリソースだけです。リンクされたリソースが外部リソースである場合、または `nopush` 属性を持つ場合は push されません。

デフォルトでは、push リクエストには元のリクエストからコピーしても安全とみなされるいくつかの header が含まれます。

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

これらの header がないと多くのリクエストが失敗すると想定されるため、手動で設定する必要はありません。

push リクエストは内部で仮想化されるため、非常に軽量です。


<a id="syntax"></a>
## 構文

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** は push する対象の URI path です。ブロック内で使う場合は、任意で method（GET または POST。デフォルトは GET）を前に置けます。
- **&lt;headers&gt;** は、[`header` ディレクティブ](/docs/caddyfile/directives/header)と同じ構文で push リクエストの header を操作します。一部の header はデフォルトで引き継がれるため、明示的に設定する必要はありません（上記参照）。



<a id="examples"></a>
## 例

レスポンス内の `Link` header で記述された任意のリソースを push します。

```caddy-d
push
```

同じ動作に加えて、すべてのリクエストで `/resources/style.css` も push します。

```caddy-d
push * /resources/style.css
```

クライアントが `/foo.html` をリクエストした場合に限り、`/foo.jpg` を push します。

```caddy-d
push /foo.html /foo.jpg
```
