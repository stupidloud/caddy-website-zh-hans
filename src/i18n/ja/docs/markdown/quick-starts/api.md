---
title: API Quick-start
---

<a id="api-quick-start"></a>
# API クイックスタート

**前提条件:**
- 基本的なターミナル / コマンドラインの知識
- PATH に `caddy` と `curl` があること

---

まず Caddy を起動します。

<pre><code class="cmd bash">caddy start</code></pre>

現在 Caddy はアイドル状態（空の設定）で実行されています。`curl` で簡単な設定を渡します。

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
                        "listen": [":2015"],
                        "routes": [
                            {
                                "handle": [{
                                    "handler": "static_response",
                                    "body": "Hello, world!"
                                }]
                            }
                        ]
                    }
                }
            }
        }
    }
EOF</code></pre>

[Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) で POST body を渡すのは手間がかかることがあります。ファイルを使いたい場合は、JSON を `caddy.json` というファイルに保存し、代わりに次のコマンドを使ってください。

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

ブラウザで [localhost:2015](http://localhost:2015) を開くか、`curl` を使います。

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

次の JSON を使うと、異なるインターフェース上に複数のサイトも定義できます。

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

JSON を更新してから、もう一度 API リクエストを実行します。

新しい "goodbye" エンドポイントを [ブラウザ](http://localhost:2016) または `curl` で試し、動作することを確認してください。

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Caddy を使い終わったら、必ず停止してください。

<pre><code class="cmd bash">caddy stop</code></pre>

API では、設定のエクスポートや、設定全体を更新するのではなく細かい変更を加えることなど、ほかにも多くのことができます。詳しくは [完全な API チュートリアル](/docs/api-tutorial) を読んでください。

<a id="further-reading"></a>
## 参考資料

- [完全な API チュートリアル](/docs/api-tutorial)
- [API ドキュメント](/docs/api)
