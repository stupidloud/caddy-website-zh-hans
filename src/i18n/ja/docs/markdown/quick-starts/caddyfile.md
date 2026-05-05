---
title: Caddyfile Quick-start
---

<a id="caddyfile-quick-start"></a>
# Caddyfile クイックスタート

`Caddyfile` という名前の新しいテキストファイルを作成します（拡張子は不要です）。

Caddyfile で最初に書くのは、サイトのアドレスです。

```caddy
localhost
```

<aside class="tip">

HTTP と HTTPS のポート（それぞれ 80 と 443）が使用している OS で特権ポートになっている場合は、昇格権限で実行するか、より高い番号のポートを使う必要があります。権限を得るには、`sudo -E` で root として実行するか、`sudo setcap cap_net_bind_service=+ep $(which caddy)` を使います。別の方法として、より高い番号のポートを使うには、アドレスを `localhost:2080` のように変更し、[`http_port`](/docs/caddyfile/options) Caddyfile オプションで HTTP ポートを変更してください。

</aside>

次に Enter を押して、実行したい内容を書きます。次のようになります。

```caddy
localhost

respond "Hello, world!"
```

これを保存し、Caddyfile がある同じフォルダーから Caddy を実行します。

<pre><code class="cmd bash">caddy start</code></pre>

Caddy はデフォルトですべてのサイト（ローカルのサイトも含む）を HTTPS で提供するため、おそらくパスワードを求められます。（パスワードの入力は初回だけのはずです。）

<aside class="tip">

ローカル HTTPS では、Caddy が証明書と一意の秘密鍵を自動生成します。ルート証明書はシステムのトラストストアに追加されるため、パスワードの入力が必要になります。これにより、証明書エラーなしで HTTPS によるローカル開発ができます。

</aside>

（権限エラーが出る場合は、昇格権限で実行するか、1023 より大きいポートを選ぶ必要があるかもしれません。）

ブラウザで [localhost](http://localhost) を開くか、`curl` でアクセスします。

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

Caddyfile では、中括弧 `{ }` で囲むことで複数のサイトを定義できます。Caddyfile を次のように変更します。

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

更新後の設定は 2 通りの方法で Caddy に渡せます。API を直接使う方法:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

または、同じ API リクエストを代わりに実行してくれる reload コマンドを使う方法です。

<pre><code class="cmd bash">caddy reload</code></pre>

新しい "goodbye" エンドポイントを [ブラウザ](https://localhost:2016) または `curl` で試し、動作することを確認してください。

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Caddy を使い終わったら、必ず停止してください。

<pre><code class="cmd bash">caddy stop</code></pre>

<a id="further-reading"></a>
## 参考資料

- [Caddyfile の概念](/docs/caddyfile/concepts)
- [Directives](/docs/caddyfile/directives)
- [一般的なパターン](/docs/caddyfile/patterns)
