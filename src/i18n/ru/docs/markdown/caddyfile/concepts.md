---
title: Основные понятия Caddyfile
---

<a id="caddyfile-concepts"></a>
# Основные понятия Caddyfile

Этот документ поможет подробно разобраться в HTTP Caddyfile.

1. [Структура](#structure)
	- [Блоки](#blocks)
	- [Директивы](#directives)
	- [Токены и кавычки](#tokens-and-quotes)
2. [Глобальные параметры](#global-options)
3. [Адреса](#addresses)
4. [Matchers](#matchers)
5. [Placeholders](#placeholders)
6. [Snippets](#snippets)
7. [Named Routes](#named-routes)
8. [Комментарии](#comments)
9. [Переменные окружения](#environment-variables)



<a id="structure"></a>
## Структура

Структуру Caddyfile можно описать визуально:

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
				<div class="struct-legend-title">Легенда</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Блок глобальных параметров</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Блок сайта</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Определение matcher</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Имя параметра</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Значение параметра</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Комментарий</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Адрес сайта</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Директива</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Matcher token</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Аргумент</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Subdirective</div></div>
			</div>
		</div>
	</div>
</div>

Ключевые моменты:

- Необязательный [**блок глобальных параметров**](#global-options) может быть самым первым элементом файла.

- Затем могут необязательно идти [snippets](#snippets) или [named routes](#named-routes).

- Иначе первая строка Caddyfile — **всегда** [адрес(а)](#addresses) сайта, который нужно обслуживать.

- Все [директивы](#directives) и [matchers](#matchers) **должны** находиться в блоке сайта. Global scope или inheritance между блоками сайтов нет.

- Если есть только один блок сайта, фигурные скобки `{ }` необязательны.

Caddyfile состоит как минимум из одного или нескольких блоков сайтов, которые всегда начинаются с одного или нескольких [адресов](#addresses) сайта. Любые директивы перед адресом запутают parser.


<a id="blocks"></a>
### Блоки

Открытие и закрытие **блока** выполняется фигурными скобками:

```
... {
	...
}
```

- Открывающая фигурная скобка `{` должна быть в конце своей строки, перед ней должен быть пробел.

- Закрывающая фигурная скобка `}` должна быть на отдельной строке.

Когда есть только один блок сайта, фигурные скобки (и отступы) необязательны. Это удобно для быстрого определения одного сайта; например, это:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

эквивалентно:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

если у вас только один блок сайта; это вопрос предпочтения.

Чтобы настроить несколько сайтов в одном Caddyfile, вы **должны** использовать фигурные скобки вокруг каждого, чтобы разделить их конфигурации:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Если request совпадает с несколькими блоками сайтов, выбирается блок сайта с наиболее specific matching address. Requests не cascade в другие blocks сайтов.


<a id="directives"></a>
### Директивы

[**Директивы**](/docs/caddyfile/directives) — функциональные ключевые слова, которые настраивают, как обслуживается сайт. Они **должны** находиться внутри blocks сайтов. Например, полная config файлового сервера может выглядеть так:

```caddy
localhost {
	file_server
}
```

Или reverse proxy:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

В этих примерах [`file_server`](/docs/caddyfile/directives/file_server) и [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) — directives. Directives являются первым словом в строке внутри site block.

Во втором примере `localhost:9000` — **argument**, потому что он находится в той же строке после directive.

Иногда directives могут открывать собственные blocks. **Subdirectives** находятся в начале каждой строки внутри directive blocks:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Здесь `lb_policy` — subdirective для [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) (она задает используемую load balancing policy между backends).

**Если явно не задокументировано иное, directives нельзя использовать внутри других directive blocks.** Например, [`basic_auth`](/docs/caddyfile/directives/basic_auth) нельзя использовать внутри [`file_server`](/docs/caddyfile/directives/file_server), потому что file server не умеет выполнять authentication; но directives можно использовать внутри blocks [`route`](/docs/caddyfile/directives/route), [`handle`](/docs/caddyfile/directives/handle) и [`handle_path`](/docs/caddyfile/directives/handle_path), потому что они специально предназначены для группировки directives.

Обратите внимание: когда HTTP Caddyfile адаптируется, HTTP handler directives сортируются по определенному default [directive order](/docs/caddyfile/directives#directive-order), если они не находятся в block [`route`](/docs/caddyfile/directives/route), поэтому порядок появления directives не важен, кроме blocks `route`.


<a id="tokens-and-quotes"></a>
### Токены и кавычки

Caddyfile разбивается на tokens перед parsing. Whitespace значим в Caddyfile, потому что tokens разделяются whitespace.

Часто directives ожидают определенное количество arguments; если один argument имеет value с whitespace, он будет разбит на два отдельных tokens:

```caddy-d
directive abc def
```

Это может вызвать проблемы и вернуть errors или unexpected behavior.

Если `abc def` должен быть value одного argument, его нужно заключить в quotes:

```caddy-d
directive "abc def"
```

Quotes можно escape, если нужно использовать quotes внутри quoted tokens:

```caddy-d
directive "\"abc def\""
```

Чтобы не escape quotes, можно вместо этого использовать backticks <code>\` \`</code> для заключения tokens; например:

```caddy-d
directive `{"foo": "bar"}`
```

Внутри quoted tokens все остальные characters трактуются literally, включая spaces, tabs и newlines. Поэтому multi-line tokens возможны:

```caddy-d
directive "first line
	second line"
```

Heredocs <span id="heredocs"/> также поддерживаются:

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

Открывающий heredoc marker должен начинаться с `<<`, за которым следует любой text (рекомендуются uppercase letters). Закрывающий heredoc marker должен быть тем же text (в примере выше, `HTML`). Открывающий marker можно escape как `\<<`, чтобы при необходимости предотвратить heredoc parsing.

Закрывающий marker может иметь indentation, из-за чего с каждой строки text удаляется такой же indentation (вдохновлено [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)), что удобно для readability внутри [blocks](#blocks) и при этом дает хороший контроль whitespace в token text. Trailing newline также удаляется, но его можно сохранить, добавив дополнительную пустую строку перед closing marker.

После closing marker могут идти дополнительные tokens как arguments directive (например, status code `200` в примере выше).


<a id="global-options"></a>
## Глобальные параметры

Caddyfile может необязательно начинаться со специального блока без keys, который называется [global options block](/docs/caddyfile/options):

```caddy
{
	...
}
```

Если он есть, он должен быть самым первым block в config.

Он используется для задания options, которые применяются globally или не относятся к какому-либо одному site. Внутри можно задавать только global options; regular site directives использовать нельзя.

Например, чтобы включить global option `debug`, часто используемый для verbose logs при troubleshooting:

```caddy
{
	debug
}
```

**[Прочитайте страницу Global Options](/docs/caddyfile/options), чтобы узнать больше.**



<a id="addresses"></a>
## Адреса

Адрес всегда находится в начале site block и обычно является первым элементом Caddyfile.

Примеры допустимых адресов:

| Address              | Effect                            |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS с managed [publicly-trusted certificate](/docs/automatic-https#hostname-requirements) |
| `*.example.com`      | HTTPS с managed [wildcard publicly-trusted certificate](/docs/caddyfile/patterns#wildcard-certificates) |
| `localhost`          | HTTPS с managed [locally-trusted certificate](/docs/automatic-https#local-https) |
| `http://`            | HTTP catch-all, зависит от [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS catch-all, зависит от [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | Явно HTTP, с matcher `Host` |
| `example.com:443`    | HTTPS из-за совпадения с default [`https_port`](/docs/caddyfile/options#http-port) |
| `:443`               | HTTPS catch-all из-за совпадения с default [`https_port`](/docs/caddyfile/options#http-port) |
| `:8080`              | HTTP на нестандартном port, без matcher `Host` |
| `localhost:8080`     | HTTPS на нестандартном port, потому что есть valid domain |
| `https://example.com:443` | HTTPS, но одновременно `https://` и `:443` избыточны |
| `127.0.0.1` | HTTPS, с locally-trusted IP certificate |
| `http://127.0.0.1` | HTTP, с IP address matcher `Host` (rejects `localhost`) |


<aside class="tip">

[Automatic HTTPS](/docs/automatic-https) включается, если address вашего site содержит hostname или IP address. Однако это поведение purely implicit, поэтому оно никогда не переопределяет explicit configuration.

Например, если address сайта `http://example.com`, auto-HTTPS не активируется, потому что scheme явно `http://`.

</aside>


Из address Caddy потенциально может infer scheme, host и port вашего site. Если address без port, Caddyfile выберет port, matching scheme, если она указана, или будет предполагать default port 443.

Если вы указываете hostname, будут обслуживаться только requests с matching header `Host`. Иными словами, если site address — `localhost`, Caddy не будет match requests к `127.0.0.1`.

Wildcards (`*`) можно использовать, но только чтобы представлять ровно один label hostname. Например, `*.example.com` match `foo.example.com`, но не `foo.bar.example.com`, а `*` match `localhost`, но не `example.com`. Практический пример смотрите в [pattern wildcard certificates](/docs/caddyfile/patterns#wildcard-certificates).

Чтобы catch all hosts, опустите host portion address, например просто `https://`. Это полезно при использовании [On-Demand TLS](/docs/automatic-https#on-demand-tls), когда вы заранее не знаете domains.

Если несколько sites используют одно и то же definition, можно перечислить их вместе, разделяя spaces и commas (нужен как минимум один space). Следующие три примера эквивалентны:

```caddy
# Comma separated site addresses
localhost:8080, example.com, www.example.com {
	...
}
```

или

```caddy
# Space separated site addresses
localhost:8080 example.com www.example.com {
	...
}
```

или

```caddy
# Comma and new-line separated site addresses
localhost:8080,
example.com,
www.example.com {
	...
}
```

Address должен быть unique; нельзя указывать один и тот же address больше одного раза.

[Placeholders](#placeholders) **нельзя** использовать в addresses, но можно использовать Caddyfile-style [environment variables](#environment-variables):

```caddy
{$DOMAIN:localhost} {
	...
}
```

По умолчанию sites bind на всех network interfaces. Если хотите override это, используйте директиву [`bind`](/docs/caddyfile/directives/bind) или global option [`default_bind`](/docs/caddyfile/options#default-bind).



<a id="matchers"></a>
## Matchers

HTTP handler [directives](#directives) по умолчанию применяются ко всем requests (если не задокументировано иное).

[Request matchers](/docs/caddyfile/matchers) можно использовать для классификации requests по заданным criteria. С matchers можно точно указать, к каким requests применяется определенная directive.

Для directives, которые поддерживают matchers, первый argument после directive — это **matcher token**. Вот несколько примеров:

```caddy-d
root *           /var/www  # matcher token: *
root /index.html /var/www  # matcher token: /index.html
root @post       /var/www  # matcher token: @post
```

Matcher tokens можно полностью опустить для match всех requests; например, `*` не нужно указывать, если следующий argument не похож на path matcher.

**[Прочитайте страницу Request Matchers](/docs/caddyfile/matchers), чтобы узнать больше.**




<a id="placeholders"></a>
## Placeholders

[Placeholders](/docs/conventions#placeholders) — простой способ вставлять dynamic values в static configuration. Их можно использовать как arguments для directives и subdirectives.

Placeholders ограничены с обеих сторон фигурными скобками `{ }` и содержат identifier внутри, например: `{foo.bar}`. Открывающую placeholder brace можно escape как `\{like.this}`, чтобы предотвратить replacement. Placeholder identifiers обычно namespaced через dots, чтобы избежать collisions между modules.

Доступность placeholders зависит от context. Не все placeholders доступны во всех частях config. Например, [HTTP app задает placeholders](/docs/json/apps/http/#docs), доступные только в областях config, связанных с handling HTTP requests (то есть в HTTP handler [directives](#directives) и [matchers](#matchers), но *не* в configuration [`tls`](/docs/caddyfile/directives/tls)). Некоторые directives или matchers тоже могут задавать собственные placeholders, которые можно использовать всем, что идет после них. Некоторые placeholders [доступны global](/docs/conventions#placeholders).

В Caddyfile можно использовать любые placeholders, но для удобства также можно использовать некоторые из этих equivalent shorthands, которые expanded при parsing Caddyfile:

| Caddyfile        | Replaces                            |
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

Не все config fields поддерживают placeholders, но большинство поддерживают там, где вы этого ожидаете. Поддержка placeholders должна быть явно добавлена в эти fields. Plugin authors могут [прочитать эту статью](/docs/extending-caddy/placeholders), чтобы узнать, как добавить поддержку placeholders в собственных modules.




<a id="snippets"></a>
## Snippets

Можно определять специальные blocks, называемые snippets, задавая им имя в parentheses:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Затем их можно reuse где угодно с помощью специальной directive [`import`](/docs/caddyfile/directives/import):

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

Directive [`import`](/docs/caddyfile/directives/import) также можно использовать, чтобы include другие files на ее месте. Если argument не совпадает с defined snippet, он будет tried как file. Она также поддерживает globs для import нескольких files. В особом случае она может появляться где угодно внутри Caddyfile (кроме как argument другой directive), включая вне site blocks:

```caddy
{
	email admin@example.com
}

import sites/*
```

Можно передавать arguments в imported configuration (snippets или files) и использовать их так:

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

Также можно передать optional block в imported snippet и использовать его следующим образом.

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

**[Прочитайте страницу directive `import`](/docs/caddyfile/directives/import), чтобы узнать больше.**


<a id="named-routes"></a>
## Named Routes

⚠️ <i>Experimental</i>

Named routes используют syntax, похожий на [snippets](#snippets); это special block, defined вне site blocks, с префиксом `&(` и окончанием `)`, а name находится между ними.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Затем эту named route можно reuse внутри любого site:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Это особенно полезно для уменьшения memory usage, если одна и та же route нужна во многих разных sites, или если для invoke одной и той же route нужно несколько разных matcher conditions.

**[Прочитайте страницу directive `invoke`](/docs/caddyfile/directives/invoke), чтобы узнать больше.**



<a id="comments"></a>
## Комментарии

Comments начинаются с `#` и продолжаются до конца строки:

```caddy-d
# Comments can start a line
directive  # or go at the end
```

Hash character `#` для comment не может находиться в середине token (то есть перед ним должен быть space или он должен быть в начале строки). Это позволяет использовать hashes внутри URIs или других values без необходимости quoting.



<a id="environment-variables"></a>
## Переменные окружения

Если ваша configuration зависит от environment variables, их можно использовать в Caddyfile:

```caddy
{$ENV}
```

Environment variables в этой форме подставляются **до начала parsing Caddyfile**, поэтому они могут expand в пустые values (то есть `""`), partial tokens, complete tokens или даже multiple tokens and lines.

Например, environment variable `UPSTREAMS="app1:8080 app2:8080 app3:8080"` expanded в несколько [tokens](#tokens-and-quotes):

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

Default value можно указать на случай, если environment variable не найдена, используя `:` как delimiter между variable name и default value:

```caddy
{$DOMAIN:localhost} {

}
```

Если вы хотите **defer substitution** environment variable до runtime, можно использовать [стандартные placeholders `{env.*}`](/docs/conventions#placeholders). Обратите внимание, что не все config parameters поддерживают эти placeholders, потому что module developers должны добавить строку code для выполнения replacement. Если кажется, что это не работает, откройте issue с запросом support.

Например, если у вас установлен plugin [`caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) и вы хотите настроить [DNS challenge](/docs/automatic-https#dns-challenge), можно передать environment variable `CLOUDFLARE_API_TOKEN` в plugin так:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Если вы запускаете Caddy как systemd service, смотрите [эти инструкции](/docs/running#overrides) по setting service overrides для определения environment variables.
