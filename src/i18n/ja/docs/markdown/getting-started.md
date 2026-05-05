---
title: "はじめに"
---

<a id="getting-started"></a>
# はじめに

Caddy へようこそ。このチュートリアルでは、Caddy の基本的な使い方を確認し、全体像に慣れていきます。

**目標:**
- 🔲 デーモンを実行する
- 🔲 API を試す
- 🔲 Caddy に設定を渡す
- 🔲 設定をテストする
- 🔲 Caddyfile を作る
- 🔲 config adapter を使う
- 🔲 初期設定で起動する
- 🔲 JSON と Caddyfile を比較する
- 🔲 API と設定ファイルを比較する
- 🔲 バックグラウンドで実行する
- 🔲 ダウンタイムなしで設定をリロードする

**前提条件:**
- 基本的なターミナル / コマンドラインの知識
- 基本的なテキストエディタの知識
- PATH に `caddy` と `curl` があること

---

**パッケージマネージャーから [Caddy をインストール](/docs/install)した場合、Caddy はすでにサービスとして実行されている可能性があります。その場合は、このチュートリアルを始める前にサービスを停止してください。**

まず実行してみましょう。

<pre><code class="cmd bash">caddy</code></pre>

おっと。サブコマンドなしでは、`caddy` コマンドはヘルプテキストを表示するだけです。何をすればよいか忘れたときは、いつでもこれを使えます。

Caddy をデーモンとして起動するには、`run` サブコマンドを使います。

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">デーモンを実行する</aside>

これはずっとブロックします。では、何をしているのでしょうか。今のところは何もしていません。デフォルトでは、Caddy の設定（"config"）は空です。別のターミナルで [admin API](/docs/api) を使うと確認できます。

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

これはあなたの Web サイトでは**ありません**。localhost:2019 の管理エンドポイントは Caddy を制御するために使われ、デフォルトでは localhost に制限されています。

</aside>


<aside class="complete">API を試す</aside>

Caddy を役立つものにするには、設定を渡します。方法はいくつもありますが、次のセクションでは `curl` を使って [/load](/docs/api#post-load) エンドポイントへ POST リクエストを送るところから始めます。



<a id="your-first-config"></a>
## 最初の設定

リクエストを準備するため、設定を作る必要があります。Caddy の設定は、中核的には単なる [JSON ドキュメント](/docs/json/) です。

これを JSON ファイル（例: `caddy.json`）として保存してください。

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

<aside class="tip">

設定ファイルを使う必要はありませんが、このチュートリアルでは使います。Caddy の [admin API](/docs/api) は、他のプログラムやスクリプトから使うように設計されています。

</aside>


次にアップロードします。

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Caddy に設定を渡す</aside>

別の GET リクエストで、Caddy が新しい設定を適用したことを確認できます。

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

ブラウザで [localhost:2015](http://localhost:2015) を開くか、`curl` を使って動作をテストします。

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

*Hello, world!* が表示されれば成功です。動いています。特に本番環境へデプロイする前には、設定が期待どおりに動作することを確認するのが常によい習慣です。

<aside class="complete">設定をテストする</aside>


<a id="your-first-caddyfile"></a>
## 最初の Caddyfile

Hello World のためだけに、これは*少し手間がかかりすぎ*でした。

Caddy を設定するもう 1 つの方法は [**Caddyfile**](/docs/caddyfile) です。上で JSON として書いたものと同じ設定は、次のように簡単に表せます。

```caddy
:2015

respond "Hello, world!"
```


これを現在のディレクトリに `Caddyfile`（拡張子なし）という名前で保存します。

<aside class="complete">Caddyfile を作る</aside>

Caddy がすでに実行中なら停止し（<kbd>Ctrl</kbd>+<kbd>C</kbd>）、次を実行します。

<pre><code class="cmd bash">caddy adapt</code></pre>

または、Caddyfile を別の場所に置いた場合や、`Caddyfile` 以外の名前にした場合は次のようにします。

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

JSON 出力が表示されます。ここで何が起きたのでしょうか。

今は [*config adapter*](/docs/config-adapters) を使って、Caddyfile を Caddy のネイティブな JSON 構造へ変換しました。

<aside class="complete">config adapter を使う</aside>

その出力を使って別の API リクエストを送ることもできますが、その手順はすべて省略できます。`caddy` コマンドが代わりに実行できるからです。現在のディレクトリに Caddyfile というファイルがあり、他の設定が指定されていなければ、Caddy は Caddyfile を読み込み、変換し、すぐに実行します。

現在のフォルダーに Caddyfile があるので、もう一度 `caddy run` してみましょう。

<pre><code class="cmd bash">caddy run</code></pre>

または、Caddyfile が別の場所にある場合は次のようにします。

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

（別の名前で、かつ "Caddyfile" で始まらない場合は、`--adapter caddyfile` を指定する必要があります。）

もう一度サイトを読み込むと、動作していることがわかります。

<aside class="complete">初期設定で起動する</aside>

ここまで見たように、初期設定付きで Caddy を起動する方法はいくつかあります。

- 現在のディレクトリにある Caddyfile という名前のファイル
- `--config` フラグ（必要に応じて `--adapter` フラグも）
- `--resume` フラグ（以前に設定が読み込まれていた場合）


<a id="json-vs-caddyfile"></a>
## JSON と Caddyfile

これで、Caddyfile は自動的に JSON へ変換されるだけだとわかりました。

Caddyfile は JSON より簡単に見えますが、常に使うべきでしょうか。それぞれに長所と短所があります。答えは要件とユースケースによって変わります。

JSON | Caddyfile
-----|----------
生成しやすい | 手作業で書きやすい
プログラムから扱いやすい | 自動化しにくい
非常に表現力が高い | ほどほどに表現力がある
Caddy の機能をすべて使える | Caddy の機能の大半を使える
設定をたどれる | Caddyfile 内をたどれない
部分的な設定変更ができる | 設定全体の変更のみ
エクスポートできる | エクスポートできない
すべての API エンドポイントに対応 | 一部の API エンドポイントに対応
ドキュメントが自動生成される | ドキュメントは手書き
広く使われている | ニッチ
より効率的 | より計算が必要
少し退屈 | 少し楽しい
**詳しく見る: [JSON structure](/docs/json/)** | **詳しく見る: [Caddyfile docs](/docs/caddyfile)**

自分のユースケースに最適なものを選ぶ必要があります。

JSON と Caddyfile（および [その他の対応済み config adapter](/docs/config-adapters)）はいずれも [Caddy の API](/docs/api) と一緒に使える、という点は重要です。ただし、Caddy の機能と API 機能をすべて使うには JSON を使います。config adapter を使う場合、API で設定を読み込んだり変更したりする唯一の方法は [/load endpoint](/docs/api#post-load) です。

<aside class="complete">JSON と Caddyfile を比較する</aside>


<a id="api-vs-config-files"></a>
## API と設定ファイル

<aside class="tip">

内部的には、設定ファイルでさえ Caddy の API エンドポイントを通ります。`caddy` コマンドは、その API 呼び出しをまとめて実行しているだけです。

</aside>


ワークフローを API ベースにするか CLI ベースにするかも決める必要があります。（同じサーバーで API と設定ファイルの両方を使うことは*できます*が、おすすめしません。信頼できる唯一の情報源を 1 つにするのが最善です。）

API | 設定ファイル
----|-------------
HTTP リクエストで設定を変更する | shell コマンドで設定を変更する
スケールしやすい | スケールしにくい
手作業では管理しにくい | 手作業で管理しやすい
かなり楽しい | こちらも楽しい
**詳しく見る: [API tutorial](/docs/api-tutorial)** | **詳しく見る: [Caddyfile tutorial](/docs/caddyfile-tutorial)**

<aside class="tip">
	適切なツールがあれば、API でサーバー設定を手動管理することは十分可能です。たとえば、任意の REST クライアントアプリケーションを使えます。
</aside>

API または設定ファイルのワークフローを選ぶことと、config adapter を使うことは直交しています。JSON を使いながらファイルに保存してコマンドラインインターフェイスで使うこともできます。逆に、Caddyfile を API と一緒に使うこともできます。

ただし、多くの人は JSON+API または Caddyfile+CLI の組み合わせを使うでしょう。

このように、Caddy は幅広いユースケースとデプロイに適しています。

<aside class="complete">API と設定ファイルを比較する</aside>



<a id="start-stop-run"></a>
## start、stop、run

Caddy はサーバーなので、無期限に実行されます。つまり、`caddy run` を実行したあと、プロセスが終了するまで（通常は <kbd>Ctrl</kbd>+<kbd>C</kbd>）ターミナルは戻ってきません。

`caddy run` が最も一般的で、通常は推奨されます（特にシステムサービスを作る場合）。一方で、`caddy start` を使って Caddy を起動し、バックグラウンドで実行させることもできます。

<pre><code class="cmd bash">caddy start</code></pre>

これによりターミナルを再び使えるようになります。一部の対話的なヘッドレス環境では便利です。

その場合、<kbd>Ctrl</kbd>+<kbd>C</kbd> では停止できないため、自分でプロセスを停止する必要があります。

<pre><code class="cmd bash">caddy stop</code></pre>

または API の [the /stop endpoint](/docs/api#post-stop) を使います。

<aside class="complete">バックグラウンドで実行する</aside>


<a id="reloading-config"></a>
## 設定のリロード

サーバーは、ダウンタイムなしで設定をリロード / 変更できます。

設定を読み込む、または変更するすべての [API endpoints](/docs/api) は graceful で、ダウンタイムはありません。

ただしコマンドラインを使っている場合、新しい設定を反映するために <kbd>Ctrl</kbd>+<kbd>C</kbd> でサーバーを停止してから再起動したくなるかもしれません。これは避けてください。サーバーの停止と起動は設定変更とは別の操作であり、ダウンタイムを発生させます。

<aside class="tip">
	サーバーを停止すると、サーバーは停止状態になります。
</aside>

代わりに、[`caddy reload`](/docs/command-line#caddy-reload) コマンドを使って graceful に設定を変更します。

<pre><code class="cmd bash">caddy reload</code></pre>

これは実際には内部で API を使っているだけです。設定ファイルを読み込み、必要に応じて JSON へ変換し、アクティブな設定をダウンタイムなしで graceful に置き換えます。

新しい設定の読み込み中にエラーが発生した場合、Caddy は最後に動作していた設定へロールバックします。

<aside class="tip">
	技術的には、古い設定が停止される前に新しい設定が開始されるため、ごく短い間は両方の設定が動作しています。新しい設定が失敗した場合はエラーで中止され、古い設定は単に停止されません。
</aside>

<aside class="complete">ダウンタイムなしで設定をリロードする</aside>
