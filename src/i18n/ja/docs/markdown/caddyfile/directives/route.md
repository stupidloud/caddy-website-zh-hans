---
title: route (Caddyfile directive)
---

# route

ディレクティブのグループを、文字どおりの順序で単一の単位として評価します。

route ブロック内のディレクティブは、[内部的に並べ替えられません](/docs/caddyfile/directives#directive-order)。route ブロック内で使えるのは、HTTP handler ディレクティブ（chain に handler または middleware を追加するディレクティブ）だけです。

このディレクティブは特殊なケースであり、そのサブディレクティブも通常のディレクティブです。


<a id="syntax"></a>
## 構文

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** は、route ブロックの外と同じように、1 行に 1 つずつ書くディレクティブまたはディレクティブブロックの一覧です。ただし、これらのディレクティブは並べ替えられません。使用できるのは HTTP handler ディレクティブだけです。



<a id="utility"></a>
## 用途

`route` ディレクティブは、HTTP handler chain の一部を完全に制御したい高度なユースケースや edge case で役立ちます。

HTTP middleware の評価順序は重要なので、Caddyfile は通常、parse 後にディレクティブを並べ替えます。これにより Caddyfile を使いやすくし、どの順番で入力したかを意識しなくてよくなります。

[組み込みの順序](/docs/caddyfile/directives#directive-order)はほとんどの site と互換性がありますが、site 全体または一部について手動で順序を制御する必要がある場合があります。そのためのものが `route` ディレクティブです。

例として、2 つの終端 handler、[`redir`](redir) と [`file_server`](file_server) の場合を考えます。どちらも client にレスポンスを書き込み、chain 内の次の handler を呼び出さないため、特定のリクエストではどちらか一方だけが実行されます。では、どちらが先でしょうか。通常は、特定の場合だけ redirect を発行し、一般の場合はファイルを配信したいことが多いため、`redir` が `file_server` より先に実行されます。

しかし、最初のディレクティブ（`file_server`）が 2 番目（`redir`）より具体的な matcher を持つ場合があります。言い換えると、一般の場合は redirect し、特定のファイルだけを配信したい場合です。

そのため、次のような Caddyfile を試すかもしれません（ただし、これは期待どおりには動作しません）。

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

問題は、[ディレクティブがソートされた](/docs/caddyfile/directives#sorting-algorithm)後、`redir` が `file_server` より前に来ることです。

しかしこの場合、`redir` の matcher（暗黙の [`*`](/docs/caddyfile/matchers#wildcard-matchers)）は `file_server` の matcher（`/specific.html`）の superset です（`*` は `/specific.html` の superset です）。

幸い、解決策は簡単です。この 2 つのディレクティブを `route` ブロックで囲み、`file_server` が `redir` より前に実行されるようにします。

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

別の方法として、2 つの matcher を相互排他的にすることもできます。ただし、条件が 1 つか 2 つを超えるとすぐに複雑になります。`route` ディレクティブでは、2 つの handler がどちらも terminal handler であるため、相互排他性は暗黙的です。

</aside>

これで、順序が文字どおりに扱われるため、`file_server` は `redir` より前に chain されます。



<a id="similar-directives"></a>
## 類似ディレクティブ

HTTP handler ディレクティブをラップできる他のディレクティブもありますが、表したい挙動によって用途が異なります。

- [`handle`](handle) は `route` と同じように他のディレクティブをラップしますが、2 つの違いがあります。1) handle ブロック同士は相互排他的であること、2) handle 内のディレクティブは通常どおり [並べ替えられる](/docs/caddyfile/directives#directive-order)ことです。

- [`handle_path`](handle_path) は `handle` と同じですが、handler を実行する前にリクエストから prefix を取り除きます。

- [`handle_errors`](handle_errors) は `handle` に似ていますが、Caddy がリクエスト処理中にエラーに遭遇した場合にのみ呼び出されます。



<a id="examples"></a>
## 例

`/api` へのリクエストはそのまま proxy し、それ以外のすべてのリクエストは disk 上のファイルに一致するかどうかに基づいて rewrite し、一致しなければ `/index.html` にします。その後、そのファイルを配信します。

[`try_files`](try_files) は [`reverse_proxy`](reverse_proxy) より directive order が高いため、通常はより上位にソートされて先に実行されます。これにより API リクエストもすべて `/index.html` に rewrite され、`/api*` に一致しなくなります。その結果、どれも proxy されず、代わりに [`file_server`](file_server) から `404` が返されます。全体を `route` で囲むことで、リクエストが rewrite される前に、常に `reverse_proxy` が先に実行されることを保証します。

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

これはこの問題に対する唯一の解決策ではありません。[`handle`](handle) ブロックを 2 つ使い、最初を `/api*` に一致させて `reverse_proxy` へ渡し、2 つ目を fallback としてファイル配信に使うこともできます。SPA の [この例](/docs/caddyfile/patterns#single-page-apps-spas) を参照してください。

</aside>
