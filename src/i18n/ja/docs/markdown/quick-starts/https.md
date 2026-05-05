---
title: HTTPS quick-start
---

<a id="https-quick-start"></a>
# HTTPS クイックスタート

このガイドでは、[完全管理の HTTPS](/docs/automatic-https) をすばやく使い始める方法を説明します。

<aside class="tip">
	Caddy は、設定にホスト名が指定されている限り、デフォルトですべてのサイトに HTTPS を使います。このチュートリアルでは、公開で信頼されるサイト（つまり "localhost" ではないサイト）を HTTPS で立ち上げたいものとして、公開ドメイン名と外部ポートを使います。
</aside>

**前提条件:**
- 基本的なターミナル / コマンドラインの知識
- DNS の基本的な理解
- 登録済みの公開ドメイン名
- ポート 80 と 443 への外部アクセス
- PATH に `caddy` と `curl` があること

---

このチュートリアルでは、`example.com` を実際のドメイン名に置き換えてください。

ドメインの A/AAAA レコードがサーバーを指すように設定します。これは DNS プロバイダーにログインしてドメイン名を管理することで行えます。

続行する前に、権威 lookup で正しいレコードを確認します。`example.com` を自分のドメイン名に置き換え、IPv6 を使っている場合は `type=A` を `type=AAAA` に置き換えてください。

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

また、サーバーが公開インターフェースからポート 80 と 443 で外部到達可能であることも確認してください。

<aside class="tip">
	自宅ネットワークやその他の制限されたネットワーク上にいる場合は、ポートフォワーディングやファイアウォール設定の調整が必要になることがあります。
</aside>

やることは、設定にドメイン名を入れて Caddy を起動するだけです。これにはいくつかの方法があります。

<a id="caddyfile"></a>
## Caddyfile

これは HTTPS を始める最も一般的な方法です。

最初の行にドメイン名を書いた `Caddyfile`（拡張子なし）を作成します。例:

```caddy
example.com

respond "Hello, privacy!"
```

同じディレクトリから次を実行します。

<pre><code class="cmd bash">caddy run</code></pre>

Caddy が TLS 証明書を発行し、サイトを HTTPS で提供する様子が表示されます。これは、Caddyfile 内のサイトアドレスにドメイン名が含まれているため可能です。


<a id="the-file-server-command"></a>
## `file-server` コマンド

必要なのが HTTPS で静的ファイルを配信することだけなら、次のコマンドを実行します（ドメイン名は置き換えてください）。

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Caddy が TLS 証明書を発行し、サイトを HTTPS で提供する様子が表示されます。


<a id="the-reverse-proxy-command"></a>
## `reverse-proxy` コマンド

必要なのが HTTPS のシンプルな reverse proxy（TLS terminator として）だけなら、次のコマンドを実行します（ドメイン名と実際の backend アドレスは置き換えてください）。

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Caddy が TLS 証明書を発行し、サイトを HTTPS で提供する様子が表示されます。


<a id="json-config"></a>
## JSON 設定

一般的な目安として、任意の [host matcher](/docs/json/apps/http/servers/routes/match/host/) は automatic HTTPS をトリガーします。

そのため、次のような JSON 設定では、本番運用に適した [automatic HTTPS](/docs/automatic-https) が有効になります。

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
