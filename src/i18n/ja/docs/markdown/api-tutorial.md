---
title: "API Tutorial"
---

<a id="api-tutorial"></a>
# API Tutorial

このチュートリアルでは、Caddy の [admin API](/docs/api) の使い方を紹介します。admin API を使うと、プログラムから自動化できる形で Caddy を操作できます。

**目標:**
- 🔲 デーモンを実行する
- 🔲 Caddy に設定を渡す
- 🔲 設定をテストする
- 🔲 有効な設定を置き換える
- 🔲 設定をたどる
- 🔲 `@id` タグを使う

**前提条件:**
- 基本的なターミナル / コマンドラインの知識
- 基本的な JSON の経験
- PATH に `caddy` と `curl` があること

---

Caddy デーモンを起動するには、`run` サブコマンドを使います。

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">デーモンを実行する</aside>

これはずっとブロックします。では、何をしているのでしょうか。今のところは何もしていません。デフォルトでは、Caddy の設定（"config"）は空です。別のターミナルで [admin API](/docs/api) を使うと確認できます。

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Caddy を役立つものにするには、設定を渡します。その方法の 1 つは、[/load](/docs/api#post-load) endpoint へ POST リクエストを送ることです。HTTP リクエストと同じく方法はいくつもありますが、このチュートリアルでは `curl` を使います。

<a id="your-first-config"></a>
## 最初の設定

リクエストを準備するには、設定を作る必要があります。Caddy の設定は、単なる [JSON ドキュメント](/docs/json/)（または [JSON に変換できるもの](/docs/config-adapters)）です。

<aside class="tip">
	設定ファイルは必須ではありません。Configuration API は常にファイルなしで使えるため、自動化では便利です。このチュートリアルでは、手で編集しやすいのでファイルを使います。
</aside>

これを JSON ファイルに保存してください。

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
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
```

次にアップロードします。

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	ファイル名の前に @ を付け忘れないでください。これは、ファイルを送信することを curl に伝えます。
</aside>

<aside class="complete">Caddy に設定を渡す</aside>

別の GET リクエストで、Caddy が新しい設定を適用したことを確認できます。

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

ブラウザで [localhost:2015](http://localhost:2015) を開くか、`curl` を使って動作をテストします。

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">設定をテストする</aside>

*Hello, world!* が表示されれば、動作しています。特に production にデプロイする前は、設定が期待どおりに動くことを確認するのが常に良い習慣です。

welcome message を "Hello world!" から、もう少しやる気の出る "I can do hard things." に変えてみましょう。設定ファイル内で変更し、handler object が次のようになるようにします。

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

設定ファイルを保存し、同じ POST リクエストをもう一度実行して Caddy の有効な設定を更新します。

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">有効な設定を置き換える</aside>

念のため、設定が更新されたことを確認します。

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

ブラウザでページを更新する（またはもう一度 `curl` を実行する）と、励ましのメッセージが表示されます。


<a id="config-traversal"></a>
## 設定をたどる

小さな変更のために設定ファイル全体をアップロードする代わりに、Caddy API の強力な機能を使って、設定ファイルに一切触れずに変更してみましょう。

<aside class="tip">
	上で行ったように設定全体を置き換えて production server に小さな変更を加えるのは危険な場合があります。file system の root access を持っているようなものです。Caddy の API を使うと、変更の scope を限定でき、設定の他の部分が誤って変更されないことを保証できます。
</aside>

リクエスト URI の path を使って設定構造の中へ入り、message string だけを更新できます（切れて見える場合は右へスクロールしてください）。

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

API で設定を変更するたびに、Caddy は新しい設定のコピーを永続化するため、あとで [**--resume** できます](/docs/command-line#caddy-run)。

</aside>


たとえば、次のような GET リクエストで動作したことを確認できます。

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

次のように表示されるはずです。

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

[`jq` コマンド <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) を使うと JSON 出力を読みやすく整形できます: **`curl ... | jq`**

</aside>


<aside class="complete">設定をたどる</aside>

**重要な注意:** 当然ですが、API を使って元の設定ファイルにない変更を加えると、その設定ファイルは古くなります。これに対処する方法はいくつかあります。

- [caddy run](/docs/command-line#caddy-run) コマンドの `--resume` を使い、直近の有効な設定を使う。
- 設定ファイルの利用と API 経由の変更を混在させない。信頼できる唯一の source of truth を 1 つにする。
- 後続の GET リクエストで [Caddy の新しい設定をエクスポートする](/docs/api#get-configpath)（最初の 2 つの選択肢よりは推奨度が低い）。



<a id="using-id-in-json"></a>
## `@id` を JSON で使う

設定をたどる機能は確かに便利ですが、path が少し長いと思いませんか。

handler object に [`@id` tag](/docs/api#using-id-in-json) を付けると、アクセスしやすくなります。

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

これにより handler object に `"@id": "msg"` という property が追加され、次のようになります。

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

**@id** tag は任意の object に置くことができ、任意の primitive value（通常は string）を持てます。[詳しく見る](/docs/api#using-id-in-json)

</aside>


これで直接アクセスできます。

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

そして、より短い path で message を変更できます。

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

もう一度確認します。

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete"><code>@id</code> タグを使う</aside>
