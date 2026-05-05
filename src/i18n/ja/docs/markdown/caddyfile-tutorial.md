---
title: "Caddyfile チュートリアル"
---

<a id="caddyfile-tutorial"></a>
# Caddyfile チュートリアル

このチュートリアルでは、見やすく実用的なサイト設定をすばやく簡単に作れるように、[HTTP Caddyfile](/docs/caddyfile) の基本を学びます。

**目標:**
- 🔲 最初のサイト
- 🔲 静的ファイルサーバー
- 🔲 Templates
- 🔲 圧縮
- 🔲 複数サイト
- 🔲 Matchers
- 🔲 環境変数
- 🔲 コメント

**前提条件:**
- 基本的なターミナル / コマンドライン操作
- 基本的なテキストエディタ操作
- PATH に `caddy` があること

---

`Caddyfile`（拡張子なし）という名前の新しいテキストファイルを作成します。

最初に書くのは、サイトの[アドレス](/docs/caddyfile/concepts#addresses)です。

```caddy
localhost
```

<aside class="tip">

HTTP と HTTPS のポート（それぞれ 80 と 443）が OS 上で特権ポートになっている場合は、権限を上げて実行するか、より大きなポート番号を使う必要があります。大きなポートを使うには、アドレスを `localhost:2015` のように変更し、Caddyfile オプションの [http_port](/docs/caddyfile/options) で HTTP ポートを変更します。

</aside>


次に Enter を押して、何をさせたいかを書きます。このチュートリアルでは、Caddyfile を次のようにします。

```caddy
localhost

respond "Hello, world!"
```

保存して Caddy を実行します（これは練習用チュートリアルなので、Caddyfile の変更が自動的に適用されるように `--watch` フラグを使います）。

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

権限エラーが出る場合は、アドレスで `localhost:2015` のような大きなポートを使い、[HTTP ポートを変更](/docs/caddyfile/options)するか、権限を上げて実行してください。

</aside>


初回はパスワードを求められます。これは、Caddy が HTTPS でサイトを配信できるようにするためです。

<aside class="tip">

Caddy は、サイトのアドレスにホスト名または IP が含まれている限り、デフォルトですべてのサイトを HTTPS で配信します。[Automatic HTTPS](/docs/automatic-https) は、アドレスの先頭に明示的に `http://` を付けることで無効化できます。

</aside>


<aside class="complete">最初のサイト</aside>

ブラウザで [localhost](https://localhost) を開き、HTTPS 対応の Web サーバーが動作していることを確認します。

<aside class="tip">
	最初に証明書エラーが出る場合は、ブラウザの再起動が必要なことがあります。
</aside>

これだけでは特に面白くないので、静的レスポンスを、ディレクトリ一覧を有効にした [file server](/docs/caddyfile/directives/file_server) に変更してみます。

```caddy
localhost

file_server browse
```

Caddyfile を保存し、ブラウザのタブを更新します。現在のディレクトリに index ファイルがあれば HTML ページが表示され、なければファイル一覧が表示されるはずです。

<aside class="complete">静的ファイルサーバー</aside>

<a id="adding-functionality"></a>
## 機能を追加する

ファイルサーバーで少し面白いことをしてみましょう。template を使ったページを配信します。新しいファイルを作成し、次の内容を貼り付けます。

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

これを現在のディレクトリに `caddy.html` として保存し、ブラウザで [https://localhost/caddy.html](https://localhost/caddy.html) を開きます。

出力は次のようになります。

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

少し待ってください。本来は今日の日付が表示されるはずです。なぜ動かなかったのでしょうか。サーバーがまだ templates を評価するように設定されていないからです。修正は簡単で、Caddyfile に 1 行追加して次のようにします。

```caddy
localhost

templates
file_server browse
```

保存してブラウザのタブを再読み込みします。次のように表示されるはずです。

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Caddy の [templates module](/docs/modules/http.handlers.templates) を使うと、他の HTML ファイルの include、サブリクエスト、レスポンス header の設定、データ構造の扱いなど、静的ファイルで便利なことを数多く実現できます。

<aside class="complete">Templates</aside>

レスポンスは高速でモダンな圧縮アルゴリズムで圧縮するのがよい習慣です。[`encode`](/docs/caddyfile/directives/encode) ディレクティブを使って、Gzip と Zstandard のサポートを有効にします。

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">圧縮</aside>

これで、ある程度高度で本番投入可能なサイトを立ち上げる基本的な流れは完了です。

[automatic HTTPS](/docs/automatic-https) を有効にする準備ができたら、このチュートリアルで使ったサイトアドレス（`localhost`）を自分のドメイン名に置き換えるだけです。詳しくは [HTTPS クイックスタートガイド](/docs/quick-starts/https) を参照してください。

<a id="multiple-sites"></a>
## 複数サイト

現在の Caddyfile では、サイト定義を 1 つしか持てません。最初の行だけがサイトのアドレスで、それ以降の行はすべてそのサイトのディレクティブになります。

しかし、複数のサイトを追加できるようにするのは簡単です。

ここまでの Caddyfile は次のとおりです。

```caddy
localhost

encode
templates
file_server browse
```

これは次の Caddyfile と同等です。

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

違いは、後者ならさらにサイトを追加できることです。

サイトブロックを波括弧 `{ }` で囲むことで、同じ Caddyfile の中に複数の異なるサイトを定義できます。

例:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

サイトブロックを波括弧で囲む場合、波括弧の外には [addresses](/docs/caddyfile/concepts#addresses) だけを書き、内側には [directives](/docs/caddyfile/directives) だけを書きます。

同じ設定を共有する複数サイトでは、次のようにアドレスを追加できます。

```caddy
:8080, :8081 {
	...
}
```

各アドレスが一意である限り、必要なだけ異なるサイトを定義できます。

<aside class="complete">複数サイト</aside>


<a id="matchers"></a>
## Matchers

一部のディレクティブだけを特定のリクエストに適用したいことがあります。たとえば、file server と reverse proxy の両方を持ちたいが、すべてのリクエストで両方を実行することは当然できない、という場合です。file server が静的ファイルでレスポンスを書くか、reverse proxy がリクエストを backend に渡してそのレスポンスを書き戻すかのどちらかになります。

次の設定は、望むようには動きません（[directive order](/docs/caddyfile/directives#directive-order) により `reverse_proxy` が優先されます）。

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

実際には、reverse proxy を API リクエスト、つまり base path が `/api/` のリクエストだけに使いたいことがあります。これは [matcher token](/docs/caddyfile/matchers#syntax) を追加すれば簡単です。

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

これで、`/api/` で始まるすべてのリクエストでは reverse proxy が優先されます。

追加した `/api/*` の部分は **matcher token** と呼ばれます。スラッシュ `/` で始まり、ディレクティブの直後に現れるので matcher token だとわかります（確実に知りたい場合は、いつでも[ディレクティブのドキュメント](/docs/caddyfile/directives)で確認できます）。

Matcher は非常に強力です。named matcher を宣言し、`@name` のように使うことで、リクエストパス以外にもさまざまな条件で match できます。続ける前に、少し時間を取って [matchers について詳しく学んで](/docs/caddyfile/matchers)ください。

<aside class="complete">Matchers</aside>

<a id="environment-variables"></a>
## 環境変数

Caddyfile adapter は、Caddyfile が解析される前に[環境変数](/docs/caddyfile/concepts#environment-variables)を置換できます。

まず、環境変数を設定します（Caddy を実行するのと同じ shell で行います）。

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

その後、Caddyfile で次のように使えます。

```caddy
{$SITE_ADDRESS}

file_server
```

Caddyfile が解析される前に、これは次のように展開されます。

```caddy
localhost:9055

file_server
```

Caddyfile の任意の場所で、任意の数の token に対して環境変数を使えます。

<aside class="complete">環境変数</aside>


<a id="comments"></a>
## コメント

最後に、とても便利な機能を 1 つ紹介します。Caddyfile にメモや注釈を書きたい場合は、`#` で始まるコメントを使えます。

```caddy
# これはコメントを開始します
```

<aside class="complete">コメント</aside>

<a id="further-reading"></a>
## さらに読む

- [Caddyfile の概念](/docs/caddyfile/concepts)
- [ディレクティブ](/docs/caddyfile/directives)
- [よく使われるパターン](/docs/caddyfile/patterns)
