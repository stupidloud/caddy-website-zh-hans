---
title: "Caddyfile 概念"
---

# Caddyfile 概念

本文将帮助您详细了解 HTTP Caddyfile。

1. [结构](#structure)
	- [块](#blocks)
	- [指令](#directives)
	- [标记和引号](#tokens-and-quotes)
2. [全局选项](#global-options)
3. [地址](#addresses)
4. [匹配器](#matchers)
5. [占位符](#placeholders)
6. [代码片段](#snippets)
7. [命名路由](#named-routes)
8. [注释](#comments)
9. [环境变量](#environment-variables)



<a id="structure"></a>
## 结构

Caddyfile 的结构可以通过以下方式直观地描述：

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
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">电子邮件</span>：<span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">服务器</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">受信任代理</span> <span class="struct-arg">静态私有地址范围</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(代码片段) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># 这是一个可重用的代码片段</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">log</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">输出</span><span class="struct-arg">文件</span> <span class="struct-arg">/var/log/access.log</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line"><span class="struct-site-addr">example.com</span> {</div>
						<div class="struct-block matcher">
							<div class="struct-line"><span class="struct-matcher-token">@post</span> {</div>
							<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-arg">POST</span> <span class="struct-matcher-token">方法</span></div>
							<div class="struct-line">}</div>
						</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">reverse_proxy</span> <span class="struct-matcher-token">@post</span> <span class="struct-arg">localhost:9001</span> <span class="struct-arg">localhost:9002</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">lb_policy</span> <span class="struct-arg">优先</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">文件服务器</span> <span class="struct-matcher-token">/static</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">导入</span><span class="struct-arg">代码片段</span></div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line struct-indent"><span class="struct-site-addr">www.example.com</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">重定向</span> <span class="struct-arg">https://example.com{uri}</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">导入</span><span class="struct-arg">代码片段</span></div>
						<div class="struct-line">}</div>
					</div>
				</div>
			</div>
			<div class="struct-legend" aria-hidden="false">
				<div class="struct-legend-title">图例</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">全局选项块</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">代码片段</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">站点块</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">匹配器块</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">选项名</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">选项值</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">注释</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">站点地址</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">指令</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">匹配令牌</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">参数</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">子指令</div></div>
			</div>
		</div>
	</div>
</div>

要点：

- 文件开头可以包含一个可选的[**全局选项块**](#global-options)。

- 接下来可能会显示[代码片段](#snippets)或[命名路由](#named-routes)。

- 否则，Caddyfile 的第一行**总是**要提供服务的站点的[地址](#addresses)。

- 所有指令和[匹配器](#matchers) **必须** 放在站点块中。站点块之间不存在全局作用域或继承关系。

- 如果只有一个站点块，其大括号 `{ }` 是可选的。

一个 Caddyfile 由至少一个或多个站点块组成，每个站点块都以该站点的一个或多个[地址](#addresses)开头。出现在地址之前的任何指令都会导致解析器产生混淆。

<a id="blocks"></a>
### 块

使用大括号来开启和关闭**代码块**：

```
... {
	...
}
```

- 左大括号 `{` 必须位于行尾，且前面需有一个空格。

- 右大括号 `}` 必须独占一行。

当只有一个站点块时，大括号（和缩进）是可选的。这是为了方便快速定义单个站点，例如：

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

等同于：

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

当你只有一个站点块时，这纯粹是个人偏好问题。

若要使用同一个 Caddyfile 配置多个站点，**必须**在每个站点周围使用大括号来分隔其配置：

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

如果一个请求匹配多个站点块，则选择匹配地址最具体的站点块。请求不会级联到其他站点块。

<a id="directives"></a>
### 指令

**[指令](/docs/caddyfile/directives)** 是用于自定义网站服务方式的功能性关键字。它们**必须**出现在站点块内。例如，一个完整的文件服务器配置可能如下所示：

```caddy
localhost {
	file_server
}
```

或者使用反向代理：

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

在这些示例中，[`file_server`](/docs/caddyfile/directives/file_server) 和 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 是指令。指令是网站块中每行开头的第一个单词。

在第二个示例中， `localhost:9000` 是一个**参数**，因为它出现在指令后的同一行上。

有时指令可以开启自己的代码块。**子指令**出现在指令代码块内每行的开头：

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

在此， `lb_policy` 是一个针对[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)的子指令（它用于设置后端之间使用的负载均衡策略）。

**除非另有说明，否则不能在其他指令块内使用指令。** 例如，不能在 [`file_server`](/docs/caddyfile/directives/file_server) 块内使用 [`basic_auth`](/docs/caddyfile/directives/basic_auth)，因为文件服务器不知道如何进行身份验证；但可以在 [`route`](/docs/caddyfile/directives/route)、[`handle`](/docs/caddyfile/directives/handle) 和 [`handle_path`](/docs/caddyfile/directives/handle_path) 块内使用指令，因为这些块正是专门设计来将指令分组使用的。

请注意，当修改 HTTP Caddyfile 时，HTTP 处理程序指令会按照特定的默认[指令顺序](/docs/caddyfile/directives#directive-order)进行排序（除非位于 [`route`](/docs/caddyfile/directives/route) 块中），因此指令出现的顺序并不重要，除非在 `route` 块中，指令的出现顺序并不重要。

<a id="tokens-and-quotes"></a>
### 标记与引号

在解析之前，Caddyfile 会先被词法分析为标记。在 Caddyfile 中，空格具有重要意义，因为标记之间是以空格分隔的。

通常，指令会期望接收一定数量的参数；如果单个参数的值中包含空格，它会被解析为两个独立的词法单元：

```caddy-d
directive abc def
```

这可能会导致问题，并引发错误或出现意外行为。

如果 `abc def` 应为单个参数的值，则需加引号：

```caddy-d
directive "abc def"
```

如果需要在引号标记中使用引号，也可以对引号进行转义：

```caddy-d
directive "\"abc def\""
```

为了避免转义引号，您可以改用反引号 `\<code> \`</code> 来包围标记；例如：

```caddy-d
directive `{"foo": "bar"}`
```

在引号内的标记中，所有其他字符均按字面意义处理，包括空格、制表符和换行符。因此可以使用多行标记：

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

开头的 heredoc 标记必须以 `<<`，后跟任意文本（建议使用大写字母）。闭合 heredoc 标记必须是相同的文本（在上例中， `HTML`）。若需防止 heredoc 解析，可通过 `\<<` 进行转义，以防止 heredoc 解析。

闭合标记可以缩进，这会导致每行文本的缩进量相应减少（受 [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc) 启发），这种设计既能提升[代码块](#blocks)内的可读性，又能对标记文本中的空白进行精细控制。尾随的换行符也会被去除，但如果在闭合标记前添加一个额外的空行，则可以保留该换行符。

闭合标记之后可以跟有其他标记，作为该指令的参数（例如上例中的状态码 `200`).

<a id="global-options"></a>
## 全局选项

Caddyfile 可以选择以一个不包含键的特殊块开头，该块称为[全局选项块](/docs/caddyfile/options)：

```caddy
{
	...
}
```

如果存在，它必须是配置文件中的第一个块。

它用于设置全局适用的选项，而非针对特定站点。在其中，只能设置全局选项；不能使用常规的站点指令。

例如，要启用 `debug` 全局选项，该选项通常用于生成详细日志以供故障排除：

```caddy
{
	debug
}
```

**请[阅读“全球选项”页面](/docs/caddyfile/options)以了解更多信息。**


<a id="addresses"></a>
## 地址

地址总是显示在网站区块的顶部，通常也是 Caddyfile 文件中的第一项。

以下是有效地址的示例：

| 地址              | 效果                            |
|----------------------|-----------------------------------|
| `example.com`        | 采用受托管且[受公众信任的证书](/docs/automatic-https#hostname-requirements)的 HTTPS |
| `*.example.com`      | 采用受托管[通配符公信证书的](/docs/caddyfile/patterns#wildcard-certificates) HTTPS |
| `localhost`          | 采用受管[本地受信任证书](/docs/automatic-https#local-https)的 HTTPS |
| `http://`            | HTTP 通配规则，受 [`http_port`](/docs/caddyfile/options#http-port) 影响 |
| `https://`           | HTTPS 通配规则，受 [`https_port`](/docs/caddyfile/options#http-port) 影响 |
| `http://example.com` | 显式使用 HTTP，配合一个 `Host` 匹配器 |
| `example.com:443`    | 因与 [`https_port`](/docs/caddyfile/options#http-port) 的默认设置匹配，故使用 HTTPS |
| `:443`               | 由于与 [`https_port`](/docs/caddyfile/options#http-port) 的默认设置匹配，因此捕获所有 HTTPS 请求 |
| `:8080`              | HTTP 位于非标准端口，无 `Host` 匹配项 |
| `localhost:8080`     | 由于拥有有效的域名，因此使用非标准端口的 HTTPS |
| `https://example.com:443` | HTTPS，但同时拥有 `https://` 以及 `:443` 是多余的 |
| `127.0.0.1` | HTTPS，使用本地受信任的 IP 证书 |
| `http://127.0.0.1` | HTTP，带 IP 地址 `Host` 匹配器（拒绝 `localhost`) |


<aside class="tip">

如果您的网站地址包含主机名或 IP 地址，则会启用[自动 HTTPS](/docs/automatic-https)。不过，此行为纯属隐式操作，因此绝不会覆盖任何显式配置。

例如，如果网站的地址是 `http://example.com`，则自动 HTTPS 功能不会激活，因为协议是显式指定的 `http://`.

</aside>


根据地址，Caddy 可能推断出您网站的协议、主机名和端口。如果地址中未包含端口号，Caddyfile 会选择与协议匹配的端口（如果已指定），否则将默认使用 443 端口。

如果您指定了主机名，则只有 `Host` 头匹配的请求才会被处理。换句话说，如果网站地址是 `localhost`，那么 Caddy 不会将请求与 `127.0.0.1` 匹配。

通配符（`*`）可以使用，但仅用于表示主机名中的一个标签。例如， `*.example.com` 匹配 `foo.example.com` ，但不匹配 `foo.bar.example.com`，而 `*` 匹配 `localhost` 但不匹配 `example.com`。请参阅[通配符证书模式](/docs/caddyfile/patterns#wildcard-certificates)以获取实际示例。

要捕获所有主机，请省略地址中的主机部分，例如，只需 `https://`。当使用[按需 TLS](/docs/automatic-https#on-demand-tls) 且无法提前知晓域名时，此方法非常有用。

如果有多个站点共享同一个定义，您可以将它们全部列在一起，用空格和逗号分隔（至少需要一个空格）。以下三个示例是等效的：

```caddy
# 逗号分隔的站点地址
localhost:8080, example.com, www.example.com {
	...
}
```

或

```caddy
# 空格分隔的站点地址
localhost:8080 example.com www.example.com {
	...
}
```

或

```caddy
# 逗号和换行分隔的站点地址
localhost:8080,
example.com,
www.example.com {
	...
}
```

地址必须是唯一的；同一地址不能重复指定。

地址中**不能**使用[占位符](#placeholders)，但可以在其中使用类似 Caddyfile [的环境变量](#environment-variables)：

```caddy
{$DOMAIN:localhost} {
	...
}
```

默认情况下，网站会绑定到所有网络接口。若要覆盖此设置，请使用[`bind`指令](/docs/caddyfile/directives/bind)或[`default_bind`全局选项](/docs/caddyfile/options#default-bind)。


<a id="matchers"></a>
## 匹配器

HTTP 处理程序[指令](#directives)默认适用于所有请求（除非另有说明）。

[请求匹配器](/docs/caddyfile/matchers)可用于根据特定条件对请求进行分类。借助匹配器，您可以精确指定某条指令应适用于哪些请求。

对于支持匹配器的指令，指令后的第一个参数是 **匹配器标记**。以下是一些示例：

```caddy-d
root *           /var/www  # matcher token: *
root /index.html /var/www  # matcher token: /index.html
root @post       /var/www  # matcher token: @post
```

匹配器标记可以完全省略以匹配所有请求；例如， `*` 如果下一个参数不像是路径匹配器，则无需提供该参数。

**请[阅读“请求匹配器”页面](/docs/caddyfile/matchers)以了解更多信息。**



<a id="placeholders"></a>
## 占位符

[占位符](/docs/conventions#placeholders)是一种将动态值注入静态配置的简便方法。它们可作为指令和子指令的参数使用。

占位符两侧由大括号包围 `{ }` ，并在其中包含标识符，例如： `{foo.bar}`。可以通过转义开头的占位符大括号 `\{like.this}` 以防止被替换。占位符标识符通常使用点分隔符进行命名空间划分，以避免模块间的冲突。

可用的占位符取决于上下文。并非所有占位符在配置的各个部分都可用。例如，[HTTP 应用程序设置的占位符](/docs/json/apps/http/#docs)仅在与处理 HTTP 请求相关的配置区域中可用（即在 HTTP 处理程序指令和[匹配器](#matchers)中可用，但在 [`tls` 配置](/docs/caddyfile/directives/tls)中不可用）。某些指令或匹配器也可能设置自己的占位符，这些占位符可供其后出现的任何内容使用。部分占位符[在全局范围内可用](/docs/conventions#placeholders)。

您可以在 Caddyfile 中使用任何占位符，但为了方便起见，您也可以使用以下这些等效的简写形式，这些简写会在解析 Caddyfile 时展开：

| Caddyfile        | 替换                            |
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

并非所有配置字段都支持占位符，但在大多数情况下，您期望支持的地方确实支持。这些字段必须已显式添加了对占位符的支持。插件作者可以[阅读这篇文章](/docs/extending-caddy/placeholders)，了解如何在自己的模块中添加对占位符的支持。



<a id="snippets"></a>
## 代码片段

您可以通过将名称用圆括号括起来，来定义称为“代码片段”的特殊代码块：

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

然后，您可以在任何需要的地方重复使用它，只需使用特殊的[`import`](/docs/caddyfile/directives/import)指令：

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

[`import`](/docs/caddyfile/directives/import)指令也可用于在指定位置包含其他文件。如果参数与已定义的代码片段不匹配，系统将尝试将其作为文件加载。该指令还支持通配符以导入多个文件。作为特例，它可以在Caddyfile的任意位置出现（但不能作为其他指令的参数），包括站点块之外的位置：

```caddy
{
	email admin@example.com
}

import sites/*
```

您可以向导入的配置（代码片段或文件）传递参数，并按以下方式使用它们：

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

⚠️ *实验性* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

您还可以向导入的代码片段传递一个可选的代码块，并按以下方式使用它们。

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

**请[阅读`import`指令的说明页面](/docs/caddyfile/directives/import)以了解更多信息。**

<a id="named-routes"></a>
## 命名路由

⚠️ *实验性*

命名路由的语法与[代码片段](#snippets)类似；它们是在站点代码块之外定义的特殊代码块，以 `&(` ，末尾以 `)` ，名称位于其间。

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

然后，你就可以在任何站点中重复使用这个命名路由：

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

如果多个不同站点都需要使用同一个路由，或者需要通过多种不同的匹配条件来调用同一个路由，这种做法对于减少内存占用尤为有用。

**请[阅读`invoke`指令的说明页面](/docs/caddyfile/directives/invoke)以了解更多信息。**


<a id="comments"></a>
## 注释

注释以 `#` ，并持续到行尾：

```caddy-d
# Comments can start a line
directive  # or go at the end
```

井号 `#` 不能出现在标记的中间（即其前必须有一个空格，或出现在行首）。这使得在 URI 或其他值中使用井号时无需进行转义。


<a id="environment-variables"></a>
## 环境变量

如果您的配置依赖于环境变量，可以在 Caddyfile 中使用它们：

```caddy
{$ENV}
```

此形式的环境变量会在**Caddyfile 开始解析之前**进行替换，因此它们可以展开为空值（即 `""`）、部分标记、完整标记，甚至多个标记和行。

例如，一个环境变量 `UPSTREAMS="app1:8080 app2:8080 app3:8080"` 将展开为多个[令牌](#tokens-and-quotes)：

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

当找不到环境变量时，可以使用 `:` 作为变量名与默认值之间的分隔符：

```caddy
{$DOMAIN:localhost} {

}
```

如果您希望将环境变量的**替换操作**推迟到运行时再进行，可以使用[标准的`{env.*}`占位符](/docs/conventions#placeholders)。请注意，并非所有配置参数都支持这些占位符，因为模块开发者需要添加一行代码来执行替换操作。如果该功能似乎无法正常工作，请提交一个问题请求支持。

例如，如果您已安装了 <a href="https://github.com/caddy-dns/cloudflare">`caddy-dns/cloudflare` 插件 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，并希望配置 [DNS 验证](/docs/automatic-https#dns-challenge)，您可以像这样将 `CLOUDFLARE_API_TOKEN` 环境变量传递给插件，方法如下：

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

如果您将 Caddy 作为 systemd 服务运行，请参阅[以下说明](/docs/running#overrides)，了解如何设置服务覆盖规则来定义环境变量。
