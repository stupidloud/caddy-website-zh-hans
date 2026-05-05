---
title: "Caddyfile の概念"
---

<a id="caddyfile-concepts"></a>
# Caddyfile の概念

このドキュメントでは、HTTP Caddyfile について詳しく説明します。

1. [構造](#structure)
	- [ブロック](#blocks)
	- [ディレクティブ](#directives)
	- [トークンと引用符](#tokens-and-quotes)
2. [グローバルオプション](#global-options)
3. [アドレス](#addresses)
4. [Matcher](#matchers)
5. [Placeholder](#placeholders)
6. [Snippet](#snippets)
7. [名前付き route](#named-routes)
8. [コメント](#comments)
9. [環境変数](#environment-variables)



<a id="structure"></a>
## 構造

Caddyfile の構造は、視覚的には次のように表せます。

<style>
	:root {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #edf5fd;
		--struct-bg-2: #f8fbfd;
		--struct-bg-end: 100%;
		--struct-fg: #254048;
		--struct-opt-name-bg: #ffd9dd;
		--struct-opt-name-fg: #7a2a39;
		--struct-opt-value-bg: #f4dec6;
		--struct-opt-value-fg: #5a3723;
		--struct-comment-bg: #d2d7d8;
		--struct-comment-fg: #495456;
		--struct-site-addr-bg: #cbe4f2;
		--struct-site-addr-fg: #1f6f9a;
		--struct-directive-bg: #c8f7d6;
		--struct-directive-fg: #14663a;
		--struct-matcher-token-bg: #ffd6ff;
		--struct-matcher-token-fg: #6f2070;
		--struct-arg-bg: #ded0ff;
		--struct-arg-fg: #4b2f7a;
		--struct-subdir-bg: #dbbca2;
		--struct-subdir-fg: #5b3a25;
	}
	html.dark {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #0d313c;
		--struct-bg-2: transparent;
		--struct-bg-end: 120%;
		--struct-fg: #cbd6da;
		--struct-opt-name-bg: #6b2630;
		--struct-opt-name-fg: #ffd9dd;
		--struct-opt-value-bg: #68412b;
		--struct-opt-value-fg: #f4dec6;
		--struct-comment-bg: #2f424d;
		--struct-comment-fg: #e8eef0;
		--struct-site-addr-bg: #204d59;
		--struct-site-addr-fg: #d6f0ff;
		--struct-directive-bg: #1f4e36;
		--struct-directive-fg: #c8f7d6;
		--struct-matcher-token-bg: #65305a;
		--struct-matcher-token-fg: #ffd6ff;
		--struct-arg-bg: #3b2e46;
		--struct-arg-fg: #ded0ff;
		--struct-subdir-bg: #6a4a2e;
		--struct-subdir-fg: #ebc095;
	}
	/* color variables - easy to tweak */
	.struct-caddyfile-visual-repl {
		display: block;
		margin: 0;
		padding: 0;
	}
	/* default (light) visual background */
	.struct-caddyfile-visual-repl .struct-visual {
		box-sizing: border-box;
		margin: 0 0 1.25rem;
		padding: 14px;
		border-radius: 14px;
		background: linear-gradient(to bottom, var(--struct-bg-1) 0%, var(--struct-bg-2) var(--struct-bg-end));
		color: var(--struct-fg);
		font-family: Inter, 'Source Sans Pro', Arial, system-ui, sans-serif;
		line-height: 1.2;
	}
	/* layout */
	.struct-caddyfile-visual-repl .struct-panel {
		display: flex;
		gap: 18px;
		align-items: flex-start;
		flex-wrap: wrap;
	}
	.struct-caddyfile-visual-repl .struct-diagram {
		flex: 1;
		padding: 8px 8px;
	}
	.struct-caddyfile-visual-repl .struct-legend {
		width: 310px;
		padding: 12px 4px;
	}
	/* code-like box: use normal whitespace so HTML pretty-printing won't leak source indentation */
	.struct-caddyfile-visual-repl .struct-code-box {
		background: transparent;
		border-radius: 8px;
		padding: 6px 6px !important;
		font-family: var(--monospace-fonts);
		font-size: 90%;
		white-space: normal;
	}
	.struct-block {
		border-radius: 8px;
		padding: 10px;
		margin: 0 0 10px 0;
	}
	.struct-block.global {
		border: 4px solid var(--struct-border-global);
	}
	.struct-block.snippet {
		border: 4px solid var(--struct-border-snippet);
	}
	.struct-block.site {
		border: 4px solid var(--struct-border-site);
	}
	.struct-block.matcher {
		border: 4px solid var(--struct-border-matcher);
		margin: 8px 8px 10px 10px;
		padding: 8px;
		border-radius: 6px;
	}
	.struct-token, .struct-opt-name, .struct-opt-value, .struct-comment, .struct-site-addr, .struct-directive, .struct-matcher-token, .struct-arg, .struct-subdir {
		display: inline !important;
		padding: .03rem .18rem !important;
		border-radius: 6px;
		font-family: var(--monospace-fonts);
		font-size: 95%;
		vertical-align: middle;
	}
	.struct-opt-name {
		background: var(--struct-opt-name-bg);
		color: var(--struct-opt-name-fg);
	}
	.struct-opt-value {
		background: var(--struct-opt-value-bg);
		color: var(--struct-opt-value-fg);
	}
	.struct-comment {
		background: var(--struct-comment-bg);
		color: var(--struct-comment-fg);
	}
	.struct-site-addr {
		background: var(--struct-site-addr-bg);
		color: var(--struct-site-addr-fg);
	}
	.struct-directive {
		background: var(--struct-directive-bg);
		color: var(--struct-directive-fg);
	}
	.struct-matcher-token {
		background: var(--struct-matcher-token-bg);
		color: var(--struct-matcher-token-fg);
	}
	.struct-arg {
		background: var(--struct-arg-bg);
		color: var(--struct-arg-fg);
	}
	.struct-subdir {
		background: var(--struct-subdir-bg);
		color: var(--struct-subdir-fg);
	}
	.struct-legend .struct-legend-title {
		font-weight: 700;
		font-size: 1.6rem;
	}
	.struct-legend .struct-item {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 16px 0;
	}
	.struct-legend .struct-item-spacer {
		height: 8px;
	}
	/* swatch for border-based legend items (blocks) */
	.struct-legend .struct-swatch-border {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		border: 4px solid transparent;
		background: transparent;
	}
	/* swatch for filled legend items (text backgrounds) */
	.struct-legend .struct-swatch-fill {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		background: transparent;
	}
	.struct-legend .struct-label {
		font-size: 90%;
		color: inherit;
	}
	.struct-caddyfile-visual-repl .struct-visual, .struct-caddyfile-visual-repl .struct-panel, .struct-caddyfile-visual-repl .struct-diagram, .struct-caddyfile-visual-repl .struct-legend, .struct-caddyfile-visual-repl .struct-code-box {
		margin: 0;
	}
	/* force compact vertical rhythm and explicit indenting so global CSS can't leak in
		NOTE: use normal whitespace so server-side HTML formatting doesn't create visible gaps */
	.struct-line {
		display: block !important;
		margin: 0 !important;
		padding: 2px 0 !important;
		line-height: 1.2 !important;
		white-space: normal !important;
	}
	/* helper to visually indent lines (do not rely on source file whitespace)
		use an explicit spacer element so HTML formatting won't affect alignment */
	.struct-line.struct-indent {
		padding-left: 0 !important;
	}
	.struct-indent-spacer {
		display: inline-block;
		width: 1.2rem;
		height: 1px;
		margin-right: 0.18rem;
	}
	/* smaller spacer for sub-directive / nested lines */
	.struct-subindent-spacer {
		display: inline-block;
		width: 0.9rem;
		height: 1px;
		margin-right: 0.12rem;
	}
</style>

<div class="struct-caddyfile-visual-repl fullwidth">
	<div class="struct-visual">
		<div class="struct-panel">
			<div class="struct-diagram">
				<div class="struct-code-box">
					<div class="struct-block global">
						<div class="struct-line">{</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># 再利用できる snippet</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">log</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">output</span> <span class="struct-arg">file</span> <span class="struct-arg">/var/log/access.log</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line"><span class="struct-site-addr">example.com</span> {</div>
						<div class="struct-block matcher">
							<div class="struct-line"><span class="struct-matcher-token">@post</span> {</div>
							<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-matcher-token">method</span> <span class="struct-arg">POST</span></div>
							<div class="struct-line">}</div>
						</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">reverse_proxy</span> <span class="struct-matcher-token">@post</span> <span class="struct-arg">localhost:9001</span> <span class="struct-arg">localhost:9002</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">lb_policy</span> <span class="struct-arg">first</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">file_server</span> <span class="struct-matcher-token">/static</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line struct-indent"><span class="struct-site-addr">www.example.com</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">redir</span> <span class="struct-arg">https://example.com{uri}</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
				</div>
			</div>
			<div class="struct-legend" aria-hidden="false">
				<div class="struct-legend-title">凡例</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">グローバルオプションブロック</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">サイトブロック</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Matcher 定義</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">オプション名</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">オプション値</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">コメント</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">サイトアドレス</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">ディレクティブ</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Matcher トークン</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">引数</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">サブディレクティブ</div></div>
			</div>
		</div>
	</div>
</div>

要点:

- 任意の [**グローバルオプションブロック**](#global-options) は、ファイルの先頭にだけ置けます。

- [Snippet](#snippets) または [名前付き route](#named-routes) は、その次に任意で置けます。

- それ以外の場合、Caddyfile の最初の行は **必ず** 配信するサイトの [アドレス](#addresses) です。

- すべての [ディレクティブ](#directives) と [matcher](#matchers) は、**必ず** サイトブロック内に置きます。サイトブロックをまたぐグローバルスコープや継承はありません。

- サイトブロックが 1 つだけの場合、その波括弧 `{ }` は省略できます。

Caddyfile は 1 つ以上のサイトブロックで構成されます。サイトブロックは必ず、そのサイト用の 1 つ以上の [アドレス](#addresses) から始まります。アドレスより前にディレクティブを書くと、parser を混乱させます。


<a id="blocks"></a>
### ブロック

**ブロック** は波括弧で開閉します。

```
... {
	...
}
```

- 開き波括弧 `{` は行末に置き、その前にスペースが必要です。

- 閉じ波括弧 `}` は単独の行に置く必要があります。

サイトブロックが 1 つだけの場合、波括弧（とインデント）は省略できます。単一サイトをすばやく定義するための便宜です。たとえば、これは:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

次と同等です。

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

サイトブロックが 1 つだけなら、どちらを選ぶかは好みです。

同じ Caddyfile で複数サイトを設定する場合は、それぞれの設定を分けるために、各サイトを **必ず** 波括弧で囲みます。

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

リクエストが複数のサイトブロックに match する場合、もっとも具体的に match するアドレスを持つサイトブロックが選ばれます。リクエストが他のサイトブロックへ cascade することはありません。


<a id="directives"></a>
### ディレクティブ

[**ディレクティブ**](/docs/caddyfile/directives) は、サイトの配信方法をカスタマイズする機能的なキーワードです。ディレクティブは **必ず** サイトブロック内に置きます。たとえば、完全なファイルサーバー設定は次のようになります。

```caddy
localhost {
	file_server
}
```

reverse proxy の例:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

これらの例では、[`file_server`](/docs/caddyfile/directives/file_server) と [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) がディレクティブです。ディレクティブは、サイトブロック内の行の最初の単語です。

2 つ目の例では、`localhost:9000` はディレクティブの後ろの同じ行にあるため **引数** です。

ディレクティブが独自のブロックを開ける場合もあります。**サブディレクティブ** は、ディレクティブブロック内の各行の先頭に現れます。

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

ここで `lb_policy` は [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) のサブディレクティブです（backend 間で使う load balancing policy を設定します）。

**明示的にドキュメント化されていない限り、ディレクティブを他のディレクティブブロック内で使うことはできません。** たとえば、[`basic_auth`](/docs/caddyfile/directives/basic_auth) は [`file_server`](/docs/caddyfile/directives/file_server) 内では使えません。ファイルサーバーは認証の方法を知らないためです。一方で、[`route`](/docs/caddyfile/directives/route)、[`handle`](/docs/caddyfile/directives/handle)、[`handle_path`](/docs/caddyfile/directives/handle_path) のブロック内ではディレクティブを使えます。これらはディレクティブをまとめるために設計されているからです。

HTTP Caddyfile が adapt されるとき、HTTP handler ディレクティブは [`route`](/docs/caddyfile/directives/route) ブロック内でない限り、特定のデフォルト [ディレクティブ順序](/docs/caddyfile/directives#directive-order) に従って並べ替えられます。そのため、`route` ブロック内を除き、ディレクティブの記述順は重要ではありません。


<a id="tokens-and-quotes"></a>
### トークンと引用符

Caddyfile は parse される前にトークンへ lex されます。Caddyfile では空白が意味を持ちます。トークンは空白で区切られるためです。

多くの場合、ディレクティブは決まった数の引数を期待します。1 つの引数の値に空白が含まれていると、それは 2 つの別々のトークンとして lex されます。

```caddy-d
directive abc def
```

これは問題になり、エラーや予期しない動作を返すことがあります。

`abc def` が 1 つの引数の値であるべきなら、引用符で囲む必要があります。

```caddy-d
directive "abc def"
```

引用符付きトークンの中で引用符を使う必要がある場合、引用符を escape できます。

```caddy-d
directive "\"abc def\""
```

引用符の escape を避けたい場合は、代わりにバッククォート <code>\` \`</code> でトークンを囲めます。例:

```caddy-d
directive `{"foo": "bar"}`
```

引用符付きトークン内では、スペース、タブ、改行を含むすべての他の文字が literal として扱われます。そのため、複数行のトークンも可能です。

```caddy-d
directive "first line
	second line"
```

Heredoc <span id="heredocs"/> もサポートされています。

```caddy
example.com {
	respond <<HTML
		<html>
		  <head><title>Foo</title></head>
		  <body>Foo</body>
		</html>
		HTML 200
}
```

開始 heredoc marker は `<<` で始まり、その後に任意のテキストを続けます（大文字を推奨）。終了 heredoc marker は同じテキストでなければなりません（上の例では `HTML`）。必要なら、開始 marker を `\<<` と escape して heredoc parsing を防げます。

終了 marker はインデントできます。その場合、すべてのテキスト行から同じ量のインデントが削除されます（[PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc) に着想を得ています）。これにより、[ブロック](#blocks) 内で読みやすさを保ちながら、トークンテキストの空白を細かく制御できます。末尾の改行も削除されますが、終了 marker の前に空行を 1 つ追加すれば保持できます。

終了 marker の後ろには、そのディレクティブへの追加引数を続けられます（上の例の status code `200` など）。


<a id="global-options"></a>
## グローバルオプション

Caddyfile は、キーを持たない特別なブロックから任意で始められます。これは [グローバルオプションブロック](/docs/caddyfile/options) と呼ばれます。

```caddy
{
	...
}
```

存在する場合、これは設定内の最初のブロックでなければなりません。

これは、グローバルに適用されるオプション、または特定の 1 つのサイトに属さないオプションを設定するために使います。中ではグローバルオプションだけを設定できます。通常のサイトディレクティブは使えません。

たとえば、トラブルシューティング用の詳細ログを出すためによく使われる `debug` グローバルオプションを有効にするには、次のようにします。

```caddy
{
	debug
}
```

**詳しくは [グローバルオプションのページ](/docs/caddyfile/options) を読んでください。**



<a id="addresses"></a>
## アドレス

アドレスは常にサイトブロックの先頭に現れ、通常は Caddyfile の最初の要素です。

有効なアドレスの例:

| アドレス              | 効果                            |
|----------------------|-----------------------------------|
| `example.com`        | 管理された [公的に信頼される証明書](/docs/automatic-https#hostname-requirements) による HTTPS |
| `*.example.com`      | 管理された [ワイルドカードの公的に信頼される証明書](/docs/caddyfile/patterns#wildcard-certificates) による HTTPS |
| `localhost`          | 管理された [ローカルで信頼される証明書](/docs/automatic-https#local-https) による HTTPS |
| `http://`            | HTTP catch-all。[`http_port`](/docs/caddyfile/options#http-port) の影響を受ける |
| `https://`           | HTTPS catch-all。[`https_port`](/docs/caddyfile/options#http-port) の影響を受ける |
| `http://example.com` | 明示的な HTTP。`Host` matcher 付き |
| `example.com:443`    | デフォルトの [`https_port`](/docs/caddyfile/options#http-port) と match するため HTTPS |
| `:443`               | デフォルトの [`https_port`](/docs/caddyfile/options#http-port) と match するため HTTPS catch-all |
| `:8080`              | 非標準ポート上の HTTP。`Host` matcher なし |
| `localhost:8080`     | 有効なドメインを持つため、非標準ポート上の HTTPS |
| `https://example.com:443` | HTTPS。ただし `https://` と `:443` の両方を持つのは冗長 |
| `127.0.0.1` | ローカルで信頼される IP 証明書による HTTPS |
| `http://127.0.0.1` | HTTP。IP アドレスの `Host` matcher 付き（`localhost` は拒否） |

<aside class="tip">

サイトのアドレスに hostname または IP アドレスが含まれている場合、[Automatic HTTPS](/docs/automatic-https) が有効になります。ただし、この動作は完全に暗黙的なものなので、明示的な設定を上書きすることはありません。

たとえば、サイトのアドレスが `http://example.com` の場合、scheme が明示的に `http://` であるため、auto-HTTPS は有効になりません。

</aside>


アドレスから、Caddy はサイトの scheme、host、port を推測できる場合があります。アドレスに port がない場合、Caddyfile は scheme が指定されていればそれに対応する port を選び、指定されていなければデフォルトの port 443 を仮定します。

hostname を指定した場合、match する `Host` header を持つリクエストだけが受け入れられます。つまり、サイトアドレスが `localhost` の場合、Caddy は `127.0.0.1` 宛てのリクエストには match しません。

ワイルドカード（`*`）も使えますが、hostname のちょうど 1 つの label を表す場合に限られます。たとえば、`*.example.com` は `foo.example.com` には match しますが、`foo.bar.example.com` には match しません。また、`*` は `localhost` には match しますが、`example.com` には match しません。実用例は [ワイルドカード証明書パターン](/docs/caddyfile/patterns#wildcard-certificates) を参照してください。

すべての host を受けるには、アドレスの host 部分を省略します。たとえば単に `https://` とします。これは、事前にドメインが分からない [On-Demand TLS](/docs/automatic-https#on-demand-tls) を使うときに便利です。

複数のサイトが同じ定義を共有する場合、スペースとカンマで区切ってまとめて列挙できます（少なくとも 1 つのスペースが必要です）。次の 3 つの例は同等です。

```caddy
# カンマ区切りのサイトアドレス
localhost:8080, example.com, www.example.com {
	...
}
```

または

```caddy
# スペース区切りのサイトアドレス
localhost:8080 example.com www.example.com {
	...
}
```

または

```caddy
# カンマと改行で区切ったサイトアドレス
localhost:8080,
example.com,
www.example.com {
	...
}
```

アドレスは一意でなければなりません。同じアドレスを複数回指定することはできません。

[Placeholder](#placeholders) はアドレスでは使えませんが、Caddyfile 形式の [環境変数](#environment-variables) は使えます。

```caddy
{$DOMAIN:localhost} {
	...
}
```

デフォルトでは、サイトはすべてのネットワークインターフェイスに bind します。これを上書きしたい場合は、[`bind` ディレクティブ](/docs/caddyfile/directives/bind) または [`default_bind` グローバルオプション](/docs/caddyfile/options#default-bind) を使ってください。



<a id="matchers"></a>
## Matcher

HTTP handler [ディレクティブ](#directives) は、デフォルトではすべてのリクエストに適用されます（別途ドキュメント化されていない限り）。

[Request matcher](/docs/caddyfile/matchers) は、指定した条件でリクエストを分類するために使えます。matcher を使うと、特定のディレクティブをどのリクエストに適用するかを正確に指定できます。

matcher をサポートするディレクティブでは、ディレクティブの後ろの最初の引数が **matcher token** です。例:

```caddy-d
root *           /var/www  # matcher token: *
root /index.html /var/www  # matcher token: /index.html
root @post       /var/www  # matcher token: @post
```

すべてのリクエストに match させる場合、matcher token は完全に省略できます。たとえば、次の引数が path matcher のように見えないなら、`*` を指定する必要はありません。

**詳しくは [Request Matchers ページ](/docs/caddyfile/matchers) を読んでください。**




<a id="placeholders"></a>
## Placeholder

[Placeholder](/docs/conventions#placeholders) は、静的な設定に動的な値を注入するためのシンプルな方法です。ディレクティブやサブディレクティブの引数として使えます。

placeholder は両側を波括弧 `{ }` で囲み、その中に識別子を含めます。例: `{foo.bar}`。置換を防ぎたい場合、開始 placeholder brace は `\{like.this}` のように escape できます。placeholder 識別子は通常、モジュール間の衝突を避けるためにドットで namespace 化されます。

利用できる placeholder は context によって異なります。すべての placeholder が設定内のあらゆる場所で使えるわけではありません。たとえば、[HTTP app が設定する placeholder](/docs/json/apps/http/#docs) は、HTTP リクエスト処理に関連する設定領域でのみ利用できます（つまり HTTP handler [ディレクティブ](#directives) と [matcher](#matchers) 内では使えますが、[`tls` 設定](/docs/caddyfile/directives/tls) 内では *使えません*）。一部のディレクティブや matcher も独自の placeholder を設定することがあり、それらは後続の処理で使えます。一部の placeholder は [グローバルに利用できます](/docs/conventions#placeholders)。

Caddyfile では任意の placeholder を使えますが、利便性のために、Caddyfile の parse 時に展開される次の同等の短縮形も使えます。

| Caddyfile        | 置換先                            |
|------------------|-------------------------------------|
| `{cookie.*}`     | `{http.request.cookie.*}`           |
| `{client_ip}`    | `{http.vars.client_ip}`             |
| `{dir}`          | `{http.request.uri.path.dir}`       |
| `{err.*}`        | `{http.error.*}`                    |
| `{file_match.*}` | `{http.matchers.file.*}`            |
| `{file.base}`    | `{http.request.uri.path.file.base}` |
| `{file.ext}`     | `{http.request.uri.path.file.ext}`  |
| `{file}`         | `{http.request.uri.path.file}`      |
| `{header.*}`     | `{http.request.header.*}`           |
| `{host}`         | `{http.request.host}`               |
| `{hostport}`     | `{http.request.hostport}`           |
| `{labels.*}`     | `{http.request.host.labels.*}`      |
| `{method}`       | `{http.request.method}`             |
| `{orig_method}`  | `{http.request.orig_method}`        |
| `{orig_uri}`     | `{http.request.orig_uri}`           |
| `{orig_path}`    | `{http.request.orig_uri.path}`      |
| `{orig_dir}`     | `{http.request.orig_uri.path.dir}`  |
| `{orig_file}`    | `{http.request.orig_uri.path.file}` |
| `{orig_query}`   | `{http.request.orig_uri.query}`     |
| `{orig_?query}`  | `{http.request.orig_uri.prefixed_query}` |
| `{path.*}`       | `{http.request.uri.path.*}`         |
| `{path}`         | `{http.request.uri.path}`           |
| `{%path}`        | `{http.request.uri.path_escaped}`   |
| `{port}`         | `{http.request.port}`               |
| `{query.*}`      | `{http.request.uri.query.*}`        |
| `{query}`        | `{http.request.uri.query}`          |
| `{%query}`       | `{http.request.uri.query_escaped}`  |
| `{?query}`       | `{http.request.uri.prefixed_query}` |
| `{re.*}`         | `{http.regexp.*}`                   |
| `{remote_host}`  | `{http.request.remote.host}`        |
| `{remote_port}`  | `{http.request.remote.port}`        |
| `{remote}`       | `{http.request.remote}`             |
| `{rp.*}`         | `{http.reverse_proxy.*}`            |
| `{resp.*}`       | `{http.intercept.*}`                |
| `{scheme}`       | `{http.request.scheme}`             |
| `{tls_cipher}`   | `{http.request.tls.cipher_suite}`   |
| `{tls_client_certificate_der_base64}` | `{http.request.tls.client.certificate_der_base64}` |
| `{tls_client_certificate_pem}`        | `{http.request.tls.client.certificate_pem}` |
| `{tls_client_fingerprint}`            | `{http.request.tls.client.fingerprint}`     |
| `{tls_client_issuer}`                 | `{http.request.tls.client.issuer}`          |
| `{tls_client_serial}`                 | `{http.request.tls.client.serial}`          |
| `{tls_client_subject}`                | `{http.request.tls.client.subject}`         |
| `{tls_version}`       | `{http.request.tls.version}`             |
| `{upstream_hostport}` | `{http.reverse_proxy.upstream.hostport}` |
| `{uri}`               | `{http.request.uri}`                     |
| `{%uri}`              | `{http.request.uri_escaped}`             |
| `{vars.*}`            | `{http.vars.*}`                          |

すべての設定フィールドが placeholder をサポートしているわけではありませんが、期待される多くの場所ではサポートされています。placeholder のサポートは、そのフィールドに明示的に追加されている必要があります。Plugin 作者は、自分のモジュールで placeholder をサポートする方法を学ぶために [この記事](/docs/extending-caddy/placeholders) を読めます。




<a id="snippets"></a>
## Snippet

名前を括弧で囲むことで、snippet と呼ばれる特別なブロックを定義できます。

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

そして、特別な [`import`](/docs/caddyfile/directives/import) ディレクティブを使って、必要な場所でこれを再利用できます。

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

[`import`](/docs/caddyfile/directives/import) ディレクティブは、別のファイルをその場に取り込むためにも使えます。引数が定義済み snippet に match しない場合、ファイルとして試されます。複数ファイルを import するための glob もサポートします。特例として、Caddyfile 内のどこにでも置けます（他のディレクティブの引数としては不可）。サイトブロックの外にも置けます。

```caddy
{
	email admin@example.com
}

import sites/*
```

import された設定（snippet またはファイル）に引数を渡し、次のように使えます。

```caddy
(snippet) {
	respond "Yahaha! You found {args[0]}!"
}

a.example.com {
	import snippet "Example A"
}

b.example.com {
	import snippet "Example B"
}
```

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

import される snippet に任意のブロックを渡し、次のように使うこともできます。

```caddy
(snippet) {
	{block}
	respond "OK"
}

a.example.com {
	import snippet {
		header +foo bar
	}
}

b.example.com {
	import snippet {
		header +bar foo
	}
}
```

**詳しくは [`import` ディレクティブのページ](/docs/caddyfile/directives/import) を読んでください。**


<a id="named-routes"></a>
## 名前付き route

⚠️ <i>Experimental</i>

名前付き route は [snippet](#snippets) に似た構文を使います。サイトブロックの外で定義される特別なブロックで、`&(` から始まり、途中に名前を挟んで `)` で終わります。

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

そして、この名前付き route を任意のサイト内で再利用できます。

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

これは、同じ route が多数の異なるサイトで必要な場合や、同じ route を呼び出すために複数の異なる matcher 条件が必要な場合に、メモリ使用量を減らすうえで特に便利です。

**詳しくは [`invoke` ディレクティブのページ](/docs/caddyfile/directives/invoke) を読んでください。**



<a id="comments"></a>
## コメント

コメントは `#` で始まり、行末まで続きます。

```caddy-d
# コメントは行頭から始められます
directive  # または行末にも置けます
```

コメントを表す hash 文字 `#` は、トークンの途中には現れません（つまり、その前にスペースがあるか、行頭にある必要があります）。これにより、URI や他の値の中で hash を使う場合に、引用符で囲む必要がありません。



<a id="environment-variables"></a>
## 環境変数

設定が環境変数に依存している場合、Caddyfile 内でそれらを使えます。

```caddy
{$ENV}
```

この形式の環境変数は、**Caddyfile の parsing が始まる前** に置換されます。そのため、空の値（つまり `""`）、部分的なトークン、完全なトークン、さらには複数のトークンや行にも展開できます。

たとえば、環境変数 `UPSTREAMS="app1:8080 app2:8080 app3:8080"` は複数の [トークン](#tokens-and-quotes) に展開されます。

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

環境変数が見つからない場合のデフォルト値は、変数名とデフォルト値の区切りに `:` を使って指定できます。

```caddy
{$DOMAIN:localhost} {

}
```

環境変数の置換を runtime まで **遅延** させたい場合は、標準の [`{env.*}` placeholder](/docs/conventions#placeholders) を使えます。ただし、すべての設定パラメータがこれらの placeholder をサポートしているわけではありません。モジュール開発者が置換を実行するためのコード行を追加する必要があるからです。動作しないように見える場合は、対応を依頼する issue を作成してください。

たとえば、[`caddy-dns/cloudflare` plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) をインストールしていて、[DNS challenge](/docs/automatic-https#dns-challenge) を設定したい場合、次のように `CLOUDFLARE_API_TOKEN` 環境変数を plugin に渡せます。

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Caddy を systemd service として実行している場合は、環境変数を定義する service overrides の設定について [こちらの手順](/docs/running#overrides) を参照してください。
