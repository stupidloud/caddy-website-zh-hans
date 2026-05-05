---
title: Reverse proxy quick-start
---

<a id="reverse-proxy-quick-start"></a>
# Reverse proxy クイックスタート

このガイドでは、HTTPS の有無にかかわらず、本番運用に適した reverse proxy をすばやく起動する方法を説明します。

**前提条件:**
- 基本的なターミナル / コマンドラインの知識
- PATH に `caddy` があること
- proxy 先として動作中の backend process

---

このチュートリアルでは、backend HTTP service が `127.0.0.1:9000` で実行されているものとします。これらのコマンドは Linux 向けですが、同じ原則は他の OS にも当てはまります。

設定ファイルなしで簡単な reverse proxy を起動することも、より柔軟な設定と制御のために設定ファイルを使うこともできます。


<a id="command-line"></a>
## コマンドライン

自分のマシンで、port 2080 から port 9000 への plaintext HTTP proxy を開始するには:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

次に試します。

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

[`reverse-proxy` command](/docs/command-line#reverse-proxy) は、すばやく簡単な reverse proxy のためのものです。（要件がシンプルであれば、本番環境でも使えます。）

<a id="caddyfile"></a>
## Caddyfile

現在の作業ディレクトリに、次の内容で `Caddyfile` というファイルを作成します。

```caddy
:2080

reverse_proxy :9000
```

この設定ファイルは、上記の `caddy reverse-proxy` command とほぼ同等です。

同じディレクトリから次を実行します。

<pre><code class="cmd bash">caddy run</code></pre>

次に proxy を試します。

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Caddyfile を変更した場合は、必ず Caddy を [reload](/docs/command-line#caddy-reload) してください。

これはシンプルな例でした。[`reverse_proxy` directive](/docs/caddyfile/directives/reverse_proxy) では、さらに多くのことができます。

<a id="https-from-client-to-proxy"></a>
## client から proxy への HTTPS

Caddy は hostname（ドメイン名）を認識している場合、[自動かつデフォルトで HTTPS](/docs/automatic-https) により proxy を提供します。`caddy reverse-proxy` command は、`--from` flag を省略するとデフォルトで `localhost` を使います。または、Caddyfile の最初の行を proxy のドメイン名に置き換えることもできます。

- `localhost` または `.localhost` で終わるドメインを使う場合、Caddy は自動更新される自己署名証明書を使います。初回は、Caddy が CA の root certificate をトラストストアにインストールしようとするため、パスワードの入力が必要になることがあります。
- それ以外のドメイン名を使う場合、Caddy は公開で信頼される証明書の取得を試みます。DNS records が自分のマシンを指しており、ports 80 and 443 が公開され、Caddy に向けられていることを確認してください。

port を指定しない場合、Caddy は HTTPS 用に 443 をデフォルトで使います。その場合、低い番号の port に bind する権限も必要です。Linux でこれを行う方法はいくつかあります。

- root として実行する（例: `sudo -E`）。
- または `sudo setcap cap_net_bind_service=+ep $(which caddy)` を実行し、この特定の capability を Caddy に付与する。

HTTPS を提供する最も基本的な `caddy reverse-proxy` command は次のとおりです。

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

次に試します。

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

`--from` flag を使って hostname をカスタマイズできます。

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

低い番号の port に bind する権限がない場合は、より高い番号の port から proxy できます。

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Caddyfile を使っている場合は、最初の行をドメイン名に変更するだけです。例:

```caddy
example.com

reverse_proxy :9000
```

<a id="https-from-proxy-to-backend"></a>
## proxy から backend への HTTPS

backend が TLS をサポートしている場合、Caddy 自身と backend の間でも HTTPS を使って proxy できます。backend アドレスで `https://` を使うだけです。

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

これには、backend の証明書が Caddy を実行しているシステムに信頼されている必要があります。（明示的に設定しない限り、Caddy は自己署名証明書を信頼しません。）

もちろん、両端で HTTPS を使うこともできます。

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

これは client から proxy まで、そして proxy から backend まで HTTPS を提供します。

proxy 先の hostname が proxy 元と異なる場合は、`--change-host-header` flag を使う必要があります。

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

デフォルトでは、Caddy は `Host` を含むすべての HTTP headers を変更せずに渡し、Host header から TLS ServerName を導出します。`--change-host-header` は Host header を backend のものにリセットし、TLS handshake が正常に完了できるようにします。上の例では、`example.com` から `localhost:9000` に変更されます（TLS handshake では `localhost` が使われます）。
