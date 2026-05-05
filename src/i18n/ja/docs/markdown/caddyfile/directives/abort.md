---
title: abort (Caddyfile directive)
---

# abort

HTTP ハンドラチェーンを即座に中断して接続を閉じることで、クライアントへ一切レスポンスを返さないようにします。同じ接続上で並行して処理中のアクティブな HTTP ストリームも中断されます。


<a id="syntax"></a>
## 構文

```caddy-d
abort [<matcher>]
```

<a id="examples"></a>
## 例

ワイルドカード証明書を使っているとき、未知のドメインに対して受けた接続を強制的に閉じます。

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# 処理されなかったドメインはここへフォールスルーしますが、
		# それらのリクエストは受け付けたくありません
        abort
    }
}
```
