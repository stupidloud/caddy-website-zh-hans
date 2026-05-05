---
title: handle (Caddyfile directive)
---

# handle

同じネスト階層にある他の `handle` block と相互排他的に、directive のグループを評価します。

言い換えると、複数の `handle` directive が連続して現れる場合、最初に *matching* した `handle` block だけが評価されます。matcher のない handle は *fallback* route として動作します。

`handle` directive は、matcher に基づいて [directive sorting algorithm](/docs/caddyfile/directives#sorting-algorithm) に従って並べ替えられます。[`handle_path`](handle_path) directive は特殊なケースで、path matcher を持つ `handle` と同じ優先度で sort されます。

必要であれば handle block はネストできます。handle block 内で使えるのは HTTP handler directive だけです。

<a id="syntax"></a>
## 構文

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** は HTTP handler directive または directive block のリストです。handle block の外で使う場合と同じく、1 行に 1 つずつ書きます。



<a id="similar-directives"></a>
## 類似 directive

HTTP handler directive を wrap できる他の directive もありますが、表したい動作に応じて用途が異なります。

- [`handle_path`](handle_path) は `handle` と同じことを行いますが、handler を実行する前にリクエストから prefix を strip します。

- [`handle_errors`](handle_errors) は `handle` に似ていますが、Caddy がリクエスト処理中にエラーに遭遇した場合だけ呼び出されます。

- [`route`](route) は `handle` と同様に他の directive を wrap しますが、2 つの違いがあります。
  1. route block 同士は相互排他的ではありません。
  2. route 内の directive は [re-ordered](/docs/caddyfile/directives#directive-order) されないため、必要に応じてより細かく制御できます。



<a id="examples"></a>
## 例

`/foo/` 内のリクエストは静的ファイルサーバーで処理し、それ以外のリクエストは reverse proxy で処理します。

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

同じサイト内で `handle` と [`handle_path`](handle_path) を混在させることができ、それらは互いに相互排他的なままです。

```caddy
example.com {
	handle_path /foo/* {
		# path は "/foo" prefix が strip されています
	}

	handle /bar/* {
		# path は "/bar" を保持したままです
	}
}
```

`handle` block をネストして、より複雑な routing logic を作成できます。

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# この block は /foo/bar 配下の path だけに一致します
		}

		handle {
			# この block は /foo/ 配下のその他すべてに一致します
		}
	}

	handle {
		# この block はその他すべてに一致します（fallback として動作）
	}
}
```
