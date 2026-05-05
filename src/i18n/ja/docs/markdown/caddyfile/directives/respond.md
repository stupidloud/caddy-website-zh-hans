---
title: respond (Caddyfile directive)
---

# respond

ハードコードされた、または静的なレスポンスを client に書き込みます。

body が空でない場合、このディレクティブは `Content-Type` header がまだ設定されていなければ設定します。body が有効な JSON オブジェクトまたは配列でない限り、デフォルト値は `text/plain; utf-8` です。JSON の場合は `application/json` に設定されます。それ以外の種類の内容では、[`header` ディレクティブ](/docs/caddyfile/directives/header)を使って適切な Content-Type を明示的に設定してください。


<a id="syntax"></a>
## 構文

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** は書き込む HTTP ステータスコードです。

  `103`（Early Hints）の場合、レスポンスは body なしで書き込まれ、handler chain は継続します。（HTTP `1xx` レスポンスは情報提供用であり、最終レスポンスではありません。）
  
  デフォルト: `200`

- **&lt;body&gt;** は書き込むレスポンス body です。

- **body** は body を指定する別の方法です。複数行の場合に便利です。

- **close** は、レスポンスを書き込んだ後に client と server の接続を閉じます。

明確にすると、最初の non-matcher 引数は 3 桁のステータスコード、またはレスポンス body 文字列のどちらでもかまいません。body の場合、次の引数にステータスコードを指定できます。

<aside class="tip">

エラーステータスコードで応答することは、handler chain 内でエラーを返して内部的に error handler を呼び出すこととは異なります。

</aside>


<a id="examples"></a>
## 例

すべての health check に空の body を持つ 200 ステータスを書き込み、それ以外のすべてのリクエストには簡単なレスポンス body を返します。

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

エラーレスポンスを書き込み、接続を閉じます。

<aside class="tip">

代わりに [`error` ディレクティブ](error)を使う方がよい場合があります。これは [`handle_errors` ディレクティブ](handle_errors)で処理できるエラーを発生させます。

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

[heredoc 構文](/docs/caddyfile/concepts#heredocs)を使って空白を制御し、さらにレスポンス body に合わせて `Content-Type` header を設定した HTML レスポンスを書き込みます。

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
