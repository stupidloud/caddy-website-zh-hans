---
title: Caddyfile 概念
---

<a id="caddyfile-concepts"></a>
# Caddyfile 概念

本文件將幫助你詳細了解 HTTP Caddyfile。

1. [結構](#structure)
	- [區塊](#blocks)
	- [指令](#directives)
	- [標記與引號](#tokens-and-quotes)
2. [全域選項](#global-options)
3. [位址](#addresses)
4. [Matcher](#matchers)
5. [Placeholder](#placeholders)
6. [Snippet](#snippets)
7. [命名路由](#named-routes)
8. [註釋](#comments)
9. [環境變數](#environment-variables)



<a id="structure"></a>
## 結構

Caddyfile 的結構可以用視覺化方式描述：

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
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># this is a reusable snippet</span></div>
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
				<div class="struct-legend-title">圖例</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">全域選項區塊</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">網站區塊</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Matcher 定義</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">選項名稱</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">選項值</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">註釋</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">網站位址</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">指令</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Matcher 標記</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">參數</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">子指令</div></div>
			</div>
		</div>
	</div>
</div>

關鍵點：

- 一個可選的 [**全域選項區塊**](#global-options) 可以是文件中的第一項。

- [Snippet](#snippets) 或 [命名路由](#named-routes) 可以選擇出現在其後。

- 否則，Caddyfile 的第一行 **永遠** 是要提供服務的網站 [位址](#addresses)。

- 所有 [指令](#directives) 和 [matcher](#matchers) **必須** 放在網站區塊中。網站區塊之間沒有全域作用域或繼承關係。

- 如果只有一個網站區塊，其大括號 `{ }` 是可選的。

一個 Caddyfile 由至少一個或多個網站區塊組成，這些區塊始終以一個或多個網站 [位址](#addresses) 開始。出現在位址之前的任何指令都會使解析器感到困惑。


<a id="blocks"></a>
### 區塊

開啟和關閉 **區塊** 是使用大括號完成的：

```
... {
	...
}
```

- 左大括號 `{` 必須位於行尾，且前面有一個空格。

- 右大括號 `}` 必須單獨佔一行。

當只有一個網站區塊時，大括號（和縮排）是可選的。這是為了方便快速定義單個網站，例如，這個：

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

相當於：

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

當你只有一個網站區塊時；這純粹是個人偏好問題。

要使用同一個 Caddyfile 配置多個網站，你 **必須** 在每個網站周圍使用大括號來分隔它們的配置：

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

如果一個請求匹配多個網站區塊，則選擇具有最精確匹配位址的網站區塊。請求不會級聯到其他網站區塊。


<a id="directives"></a>
### 指令

[**指令**](/docs/caddyfile/directives) 是功能關鍵字，用於自定義服務網站的方式。它們 **必須** 出現在網站區塊中。例如，一個完整的文件伺服器配置可能如下所示：

```caddy
localhost {
	file_server
}
```

或者是反向代理：

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

在這些示例中，[`file_server`](/docs/caddyfile/directives/file_server) 和 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 是指令。指令是網站區塊中一行的第一個單詞。

在第二個示例中，`localhost:9000` 是一個 **參數**，因為它出現在指令之後的同一行中。

有時指令可以開啟自己的區塊。**子指令** 出現在指令區塊內每行的開頭：

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

這裡，`lb_policy` 是 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 的子指令（它設置後端之間使用的負載平衡策略）。

**除非另有說明，否則指令不能在其他指令區塊內使用。** 例如，[`basic_auth`](/docs/caddyfile/directives/basic_auth) 不能在 [`file_server`](/docs/caddyfile/directives/file_server) 內使用，因為文件伺服器不知道如何進行身份驗證；但你可以在 [`route`](/docs/caddyfile/directives/route)、[`handle`](/docs/caddyfile/directives/handle) 和 [`handle_path`](/docs/caddyfile/directives/handle_path) 區塊內使用指令，因為它們是專門為指令分組而設計的。

請注意，當 HTTP Caddyfile 被轉換時，HTTP handler 指令會根據特定的預設 [指令順序](/docs/caddyfile/directives#directive-order) 進行排序（除非在 [`route`](/docs/caddyfile/directives/route) 區塊中），因此指令出現的順序無關緊要，除了在 `route` 區塊中。


<a id="tokens-and-quotes"></a>
### 標記與引號

Caddyfile 在解析之前會被分解為標記 (token)。空格在 Caddyfile 中非常重要，因為標記是由空格分隔的。

通常，指令期望一定數量的參數；如果單個參數的值包含空格，它將被解析為兩個單獨的標記：

```caddy-d
directive abc def
```

這可能會產生問題並返回錯誤或意外行為。

如果 `abc def` 應該是單個參數的值，則需要將其用引號括起來：

```caddy-d
directive "abc def"
```

如果你需要在帶引號的標記中使用引號，引號也可以被轉義：

```caddy-d
directive "\"abc def\""
```

為了避免轉義引號，你可以改用反引號 <code>\` \`</code> 來包裹標記；例如：

```caddy-d
directive `{"foo": "bar"}`
```

在帶引號的標記內，所有其他字符都按原樣處理，包括空格、製表符和換行符。因此，多行標記是可能的：

```caddy-d
directive "first line
	second line"
```

也支持 Heredocs <span id="heredocs"/>：

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

起始 heredoc 標記必須以 `<<` 開頭，後跟任何文本（建議使用大寫字母）。結束 heredoc 標記必須是相同的文本（在上面的示例中為 `HTML`）。如果需要，可以使用 `\<<` 轉義起始標記以防止 heredoc 解析。

結束標記可以縮排，這會導致每行文本都去除相應數量的縮排（靈感來自 [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)），這有利於區塊內部的可讀性，同時可以很好地控制標記文本中的空格。尾隨換行符也會被去除，但可以通過在結束標記之前添加一個額外的空行來保留。

其他標記可以跟在結束標記之後作為指令的參數（例如在上面的示例中，狀態碼 `200`）。


<a id="global-options"></a>
## 全域選項

Caddyfile 可以選擇以一個沒有鍵的名為 [全域選項區塊](/docs/caddyfile/options) 的特殊區塊開始：

```caddy
{
	...
}
```

如果存在，它必須是配置中的第一個區塊。

它用於設置全域應用的選項，或者不特別針對任何一個網站的選項。在內部，只能設置全域選項；你不能在其中使用常規網站指令。

例如，要啟用 `debug` 全域選項，該選項通常用於生成詳細日誌以進行故障排除：

```caddy
{
	debug
}
```

**[閱讀全域選項頁面](/docs/caddyfile/options) 以了解更多資訊。**



<a id="addresses"></a>
## 位址

位址始終出現在網站區塊的頂部，通常是 Caddyfile 中的第一項。

以下是有效位址的示例：

| 位址 | 效果 |
|----------------------|-----------------------------------|
| `example.com`        | 使用受管理的 [公信認證證書](/docs/automatic-https#hostname-requirements) 的 HTTPS |
| `*.example.com`      | 使用受管理的 [通配符公信認證證書](/docs/caddyfile/patterns#wildcard-certificates) 的 HTTPS |
| `localhost`          | 使用受管理的 [本地信任證書](/docs/automatic-https#local-https) 的 HTTPS |
| `http://`            | HTTP 全匹配，受 [`http_port`](/docs/caddyfile/options#http-port) 影響 |
| `https://`           | HTTPS 全匹配，受 [`https_port`](/docs/caddyfile/options#http-port) 影響 |
| `http://example.com` | 明確的 HTTP，帶有 `Host` matcher |
| `example.com:443`    | 由於匹配 [`https_port`](/docs/caddyfile/options#http-port) 預設值而使用的 HTTPS |
| `:443`               | 由於匹配 [`https_port`](/docs/caddyfile/options#http-port) 預設值而使用的 HTTPS 全匹配 |
| `:8080`              | 非標準端口上的 HTTP，無 `Host` matcher |
| `localhost:8080`     | 非標準端口上的 HTTPS，因為具有有效的網域 |
| `https://example.com:443` | HTTPS，但同時擁有 `https://` 和 `:443` 是多餘的 |
| `127.0.0.1` | HTTPS，帶有本地信任的 IP 證書 |
| `http://127.0.0.1` | HTTP，帶有 IP 位址 `Host` matcher（拒絕 `localhost`） |


<aside class="tip">

如果你的網站位址包含主機名或 IP 位址，則會啟用 [自動 HTTPS](/docs/automatic-https)。然而，這種行為純粹是隱含的，因此它永遠不會覆蓋任何明確的配置。

例如，如果網站的位址是 `http://example.com`，自動 HTTPS 將不會激活，因為方案明確為 `http://`。

</aside>


從位址中，Caddy 可能可以推斷出網站的方案、主機和端口。如果位址沒有端口，Caddyfile 將選擇與方案匹配的端口（如果已指定），否則將假定預設端口 443。

如果你指定了主機名，則只有具有匹配 `Host` 標頭的請求才會被接受。換句話說，如果網站位址是 `localhost`，那麼 Caddy 將不會匹配對 `127.0.0.1` 的請求。

可以使用通配符 (`*`)，但僅用於精確表示主機名的一個標籤。例如，`*.example.com` 匹配 `foo.example.com` 但不匹配 `foo.bar.example.com`，而 `*` 匹配 `localhost` 但不匹配 `example.com`。有關實際示例，請參見 [通配符證書模式](/docs/caddyfile/patterns#wildcard-certificates)。

要匹配所有主機，請省略位址的主機部分，例如簡單的 `https://`。這在當你事先不知道網域，使用 [On-Demand TLS](/docs/automatic-https#on-demand-tls) 時非常有用。

如果多個網站共享相同的定義，你可以將它們全部列在一起，並用空格和逗號分隔（至少需要一個空格）。以下三個示例是等效的：

```caddy
# 逗號分隔的網站位址
localhost:8080, example.com, www.example.com {
	...
}
```

或

```caddy
# 空格分隔的網站位址
localhost:8080 example.com www.example.com {
	...
}
```

或

```caddy
# 逗號和換行符分隔的網站位址
localhost:8080,
example.com,
www.example.com {
	...
}
```

位址必須是唯一的；你不能多次指定相同的位址。

[Placeholder](#placeholders) **不能** 用於位址，但你可以在其中使用 Caddyfile 風格的 [環境變數](#environment-variables)：

```caddy
{$DOMAIN:localhost} {
	...
}
```

預設情況下，網站綁定在所有網路介面上。如果你希望覆蓋此行為，請使用 [`bind` 指令](/docs/caddyfile/directives/bind) 或 [`default_bind` 全域選項](/docs/caddyfile/options#default-bind) 來執行此操作。



<a id="matchers"></a>
## Matcher

HTTP handler [指令](#directives) 預設應用於所有請求（除非另有說明）。

[請求 matcher](/docs/caddyfile/matchers) 可用於按給定標準對請求進行分類。使用 matcher，你可以精確指定某個指令適用於哪些請求。

對於支持 matcher 的指令，指令後的第一個參數是 **matcher 標記**。以下是一些示例：

```caddy-d
root *           /var/www  # matcher 標記：*
root /index.html /var/www  # matcher 標記：/index.html
root @post       /var/www  # matcher 標記：@post
```

Matcher 標記可以完全省略以匹配所有請求；例如，如果下一個參數看起來不像路徑 matcher，則不需要提供 `*`。

**[閱讀請求 matcher 頁面](/docs/caddyfile/matchers) 以了解更多資訊。**




<a id="placeholders"></a>
## Placeholder

[Placeholder](/docs/conventions#placeholders) 是將動態值注入靜態配置的一種簡單方法。它們可以用作指令和子指令的參數。

Placeholder 兩邊由大括號 `{ }` 包圍，內部包含識別符，例如：`{foo.bar}`。起始 placeholder 大括號可以被轉義 `\{like.this}` 以防止替換。Placeholder 識別符通常使用點分隔命名空間，以避免跨模組衝突。

哪些 placeholder 可用取決於上下文。並非所有 placeholder 在配置的所有部分都可用。例如，[HTTP 應用程式設置的 placeholder](/docs/json/apps/http/#docs) 僅在配置中與處理 HTTP 請求相關的部分可用（即在 HTTP handler [指令](#directives) 和 [matcher](#matchers) 中，但 *不* 在 [`tls` 配置](/docs/caddyfile/directives/tls) 中）。某些指令或 matcher 也可能設置自己的 placeholder，這些 placeholder 可以被其後的任何內容使用。某些 placeholder [是全域可用的](/docs/conventions#placeholders)。

你可以在 Caddyfile 中使用任何 placeholder，但為了方便起見，你也可以使用其中一些等效的簡寫，這些簡寫在解析 Caddyfile 時會被展開：

| Caddyfile | 替換為 |
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

並非所有配置欄位都支持 placeholder，但在你期望的大多數地方都支持。對 placeholder 的支持需要被明確添加到這些欄位中。外掛作者可以 [閱讀這篇文章](/docs/extending-caddy/placeholders) 來了解如何在他們自己的模組中添加對 placeholder 的支持。




<a id="snippets"></a>
## Snippet

你可以通過給特殊的區塊起一個用括號括起來的名稱來定義它們，稱為 snippet：

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

然後你可以在任何需要的地方重複使用它，使用特殊的 [`import`](/docs/caddyfile/directives/import) 指令：

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

[`import`](/docs/caddyfile/directives/import) 指令也可以用於在其位置包含其他文件。如果參數與定義的 snippet 不匹配，則將其作為文件嘗試。它還支持使用通配符導入多個文件。作為特殊情況，它可以出現在 Caddyfile 中的任何位置（除了作為另一個指令的參數），包括網站區塊之外：

```caddy
{
	email admin@example.com
}

import sites/*
```

你可以將參數傳遞給導入的配置（snippet 或文件），並像這樣使用它們：

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

⚠️ *實驗性* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

你還可以將可選區塊傳遞給導入的 snippet，並按如下方式使用它們。

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

**[閱讀 `import` 指令頁面](/docs/caddyfile/directives/import) 以了解更多資訊。**


<a id="named-routes"></a>
## 命名路由

⚠️ *實驗性*

命名路由使用類似於 [snippet](#snippets) 的語法；它們是在網站區塊之外定義的特殊區塊，以 `&(` 開頭並以 `)` 結尾，中間是名稱。

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

然後你可以在任何網站中重複使用此命名路由：

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

如果許多不同的網站需要相同的路由，或者需要多個不同的 matcher 條件來調用相同的路由，這對於減少記憶體使用特別有用。

**[閱讀 `invoke` 指令頁面](/docs/caddyfile/directives/invoke) 以了解更多資訊。**



<a id="comments"></a>
## 註釋

註釋以 `#` 開始，一直持續到行尾：

```caddy-d
# 註釋可以從一行開始
directive  # 或者放在結尾
```

註釋的井號字符 `#` 不能出現在標記的中間（即它必須前面有一個空格或出現在一行的開頭）。這允許在 URI 或其他值中使用井號而不需要加引號。



<a id="environment-variables"></a>
## 環境變數

如果你的配置依賴於環境變數，你可以在 Caddyfile 中使用它們：

```caddy
{$ENV}
```

這種形式的環境變數在 **Caddyfile 解析開始之前** 被替換，因此它們可以展開為空值（即 `""`）、部分標記、完整標記，甚至是多個標記和行。

例如，環境變數 `UPSTREAMS="app1:8080 app2:8080 app3:8080"` 將展開為多個 [標記](#tokens-and-quotes)：

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

當找不到環境變數時，可以通過在變數名和預設值之間使用 `:` 作為分隔符來指定預設值：

```caddy
{$DOMAIN:localhost} {

}
```

如果你想 **延遲環境變數的替換** 直到運行時，可以使用 [標準 `{env.*}` placeholder](/docs/conventions#placeholders)。請注意，並非所有配置參數都支持這些 placeholder，因為模組開發人員需要添加一行代碼來執行替換。如果它似乎不起作用，請提交問題以請求支持。

例如，如果你安裝了 [`caddy-dns/cloudflare` 外掛 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) 並希望配置 [DNS 挑戰](/docs/automatic-https#dns-challenge)，你可以將 `CLOUDFLARE_API_TOKEN` 環境變數傳遞給外掛，如下所示：

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

如果你將 Caddy 作為 systemd 服務運行，請參見 [這些說明](/docs/running#overrides) 以設置服務覆蓋來定義你的環境變數。
