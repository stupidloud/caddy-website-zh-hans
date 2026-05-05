---
title: Static files quick-start
---

<a id="static-files-quick-start"></a>
# 静的ファイル クイックスタート

このガイドでは、本番運用に適した静的ファイルサーバーをすばやく起動する方法を説明します。

**前提条件:**
- 基本的なターミナル / コマンドラインの知識
- PATH に `caddy` があること
- web site を含む folder

---

すばやく file server を起動する簡単な方法が 2 つあります。

<a id="command-line"></a>
## コマンドライン

ターミナルでサイトの root directory に移動し、次を実行します。

<pre><code class="cmd bash">caddy file-server</code></pre>

権限エラーが出る場合、おそらく OS が低い番号の port への bind を許可していません。その場合は、代わりに高い番号の port を使います。

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

次に、ブラウザで [localhost](http://localhost)（または [localhost:2015](http://localhost:2015)）を開き、サイトを確認します。

index file がないが file listing を表示したい場合は、`--browse` option を使います。

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

別の folder を site root として使うこともできます。

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



<a id="caddyfile"></a>
## Caddyfile

サイトの root に、次の内容で `Caddyfile` というファイルを作成します。

```caddy
localhost

file_server
```

低い番号の port に bind する権限がない場合は、`localhost` を `localhost:2015`（または別の高い番号の port）に置き換えます。

同じディレクトリから次を実行します。

<pre><code class="cmd bash">caddy run</code></pre>

その後、[localhost](https://localhost)（または設定内の任意のアドレス）を読み込むと、サイトを確認できます。

[`file_server` directive](/docs/caddyfile/directives/file_server) には、サイトをカスタマイズするための追加 options があります。Caddyfile を変更したら、必ず Caddy を [reload](/docs/command-line#caddy-reload) してください（または停止してから再起動してください）。

index file がないが file listing を表示したい場合は、`browse` argument を使います。

```caddy
localhost

file_server browse
```

別の folder を site root として使うこともできます。

```caddy
localhost

root /var/www/mysite
file_server
```
