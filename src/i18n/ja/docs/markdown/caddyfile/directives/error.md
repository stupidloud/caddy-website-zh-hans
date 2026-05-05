---
title: error (Caddyfile directive)
---

# error

HTTP ハンドラチェーン内でエラーを発生させます。任意でメッセージと推奨 HTTP status code を指定できます。

このハンドラはレスポンスを書き込みません。代わりに、[`handle_errors`](handle_errors) directive と組み合わせて、独自のエラーハンドリングロジックを呼び出すためのものです。


<a id="syntax"></a>
## 構文

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** は書き込む HTTP status code です。デフォルトは `500` です。
- **&lt;message&gt;** はエラーメッセージです。デフォルトではエラーメッセージはありません。
- **message** は、エラーメッセージを指定する別の方法です。複数行の場合に便利です。

明確にすると、最初の non-matcher 引数は 3 桁の status code、またはエラーメッセージ文字列のどちらでも構いません。エラーメッセージの場合、次の引数に status code を指定できます。


<a id="examples"></a>
## 例

特定のリクエストパスでエラーを発生させ、[`handle_errors`](handle_errors) を使ってレスポンスを書き込みます。

```caddy
example.com {
	root /srv

	# 特定のパスでエラーを発生させる
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # HTML ページを提供してエラーを処理する
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
