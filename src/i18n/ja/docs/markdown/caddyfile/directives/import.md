---
title: import (Caddyfile directive)
---

# import

[snippet](/docs/caddyfile/concepts#snippets) またはファイルを取り込み、このディレクティブをその snippet またはファイルの内容で置き換えます。

このディレクティブは特別扱いです。構造がパースされる前に評価され、Caddyfile のどこにでも記述できます。

<a id="syntax"></a>
## 構文

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** は取り込むファイル名、glob パターン、または [snippet](/docs/caddyfile/concepts#snippets) の名前です。その内容は、最初からそのファイルの内容がここに書かれていたかのように、この行を置き換えます。

  特定のファイルが見つからない場合はエラーになりますが、空の glob パターンはエラーではありません。

  特定のファイルを import した場合、そのファイルが空なら警告が出力されます。

  パターンがファイル名または glob の場合、常に `import` が書かれているファイルからの相対パスとして扱われます。

  glob パターン `*` を最後のパスセグメントとして使うと、隠しファイル（つまり `.` で始まるファイル）は無視されます。隠しファイルを取り込むには、最後のセグメントに `.*` を使ってください。
- **&lt;args...&gt;** は、取り込まれるトークンへ渡す任意の引数リストです。この placeholder は特別扱いで、実行時ではなく Caddyfile のパース時に評価されます。[Go の slice 構文](https://gobyexample.com/slices)と同様に、いくつかの形式で使えます。
  - `{args[n]}` は、`n` を 0 始まりの位置インデックスとして引数を挿入します
  - `{args[:]}` は、すべての引数を挿入します
  - `{args[:m]}` は、`m` より前の引数を挿入します
  - `{args[n:]}` は、`n` から始まる引数を挿入します
  - `{args[n:m]}` は、`n` から `m` までの範囲の引数を挿入します

  複数のトークンを挿入する形式では、placeholder は単独の [token](/docs/caddyfile/concepts#tokens-and-quotes) でなければなりません。別のトークンの一部にはできません。つまり、前後に空白が必要で、引用符の中には置けません。

  v2.7.0 より前は `{args.N}` という構文でしたが、この形式は上記のより柔軟な構文を優先するため非推奨になりました。

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** は、取り込まれるトークンへ渡す任意のブロックです。この placeholder は特別扱いで、実行時ではなく Caddyfile のパース時に再帰的に評価されます。次の 2 つの形式で使えます。
  - `{block}` は、渡されたブロック全体の内容を placeholder の位置へ置き換えます
  - `{blocks.key}` は、渡されたブロック内のパラメータの最初のトークンが `key` である内容を参照します


<a id="examples"></a>
## 例

隣接する sites-enabled フォルダー内のすべてのファイル（隠しファイルを除く）を import します。

```caddy-d
import sites-enabled/*
```

import 引数を使って CORS header を設定する snippet を import します。

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

proxy upstream のリストを引数として受け取る snippet を import します。

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

最初の引数を prefix rewrite ルールとして使う proxy を作る snippet を import します。

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

設定可能な "hello world" メッセージと content-type で応答する snippet を import します。

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

reverse proxy の拡張可能なオプションを提供する snippet を import します。

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

事前に読み込まれた middleware とともに、任意のディレクティブ群を提供する snippet を import します。

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
