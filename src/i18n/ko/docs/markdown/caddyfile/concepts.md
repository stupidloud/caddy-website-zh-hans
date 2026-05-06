---
title: Caddyfile 개념
---

# Caddyfile 개념

이 문서는 HTTP Caddyfile에 대해 자세히 배우는 데 도움이 될 것입니다.

1. [구조](#structure)
	- [블록](#blocks)
	- [지시어](#directives)
	- [토큰과 따옴표](#tokens-and-quotes)
2. [전역 옵션](#global-options)
3. [주소](#addresses)
4. [매처](#matchers)
5. [플레이스홀더](#placeholders)
6. [스니펫](#snippets)
7. [명명된 라우트](#named-routes)
8. [주석](#comments)
9. [환경 변수](#environment-variables)



## 구조 <a id="structure"></a>

Caddyfile의 구조는 시각적으로 다음과 같이 설명할 수 있습니다:

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
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># 이것은 재사용 가능한 스니펫입니다</span></div>
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
				<div class="struct-legend-title">범례</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">전역 옵션 블록</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">스니펫</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">사이트 블록</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">매처 정의</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">옵션 이름</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">옵션 값</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">주석</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">사이트 주소</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">지시어</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">매처 토큰</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">인수</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">하위 지시어</div></div>
			</div>
		</div>
	</div>
</div>

주요 사항:

- 선택 사항인 [**전역 옵션 블록**](#global-options)은 파일의 맨 처음에 올 수 있습니다.

- [스니펫](#snippets) 또는 [명명된 라우트](#named-routes)가 그다음에 선택적으로 올 수 있습니다.

- 그 외의 경우, Caddyfile의 첫 번째 줄은 **항상** 서비스할 사이트의 [주소](#addresses)입니다.

- 모든 [지시어](#directives)와 [매처](#matchers)는 **반드시** 사이트 블록 내에 있어야 합니다. 사이트 블록 간의 전역 스코프나 상속은 없습니다.

- 사이트 블록이 하나만 있는 경우 중괄호 `{ }`는 생략 가능합니다.

Caddyfile은 최소한 하나 이상의 사이트 블록으로 구성되며, 사이트 블록은 항상 사이트의 [주소](#addresses) 중 하나 이상으로 시작합니다. 주소 앞에 지시어가 나타나면 파서가 혼동을 일으킬 것입니다.


### 블록 <a id="blocks"></a>

**블록**을 열고 닫는 것은 중괄호를 사용합니다:

```
... {
	...
}
```

- 여는 중괄호 `{`는 해당 줄의 끝에 있어야 하며 앞에 공백이 있어야 합니다.

- 닫는 중괄호 `}`는 단독으로 한 줄을 차지해야 합니다.

사이트 블록이 하나만 있는 경우 중괄호(및 들여쓰기)는 선택 사항입니다. 이는 단일 사이트를 빠르게 정의하기 위한 편의 기능입니다. 예를 들어, 다음과 같은 설정은:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

사이트 블록이 하나뿐일 때 아래와 동일합니다:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

이는 단순히 선호도의 차이입니다.

동일한 Caddyfile로 여러 사이트를 구성하려면, 각 사이트의 구성을 구분하기 위해 각 사이트마다 중괄호를 **반드시** 사용해야 합니다:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

요청이 여러 사이트 블록과 일치하는 경우, 가장 구체적으로 일치하는 주소를 가진 사이트 블록이 선택됩니다. 요청은 다른 사이트 블록으로 계단식으로 전달(cascade)되지 않습니다.


### 지시어 <a id="directives"></a>

[**지시어(Directives)**](/docs/caddyfile/directives)는 사이트가 서비스되는 방식을 사용자 정의하는 기능적 키워드입니다. 지시어는 **반드시** 사이트 블록 내에 나타나야 합니다. 예를 들어, 완전한 파일 서버 설정은 다음과 같을 수 있습니다:

```caddy
localhost {
	file_server
}
```

또는 역방향 프록시:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

이 예제에서 [`file_server`](/docs/caddyfile/directives/file_server)와 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)는 지시어입니다. 지시어는 사이트 블록 내의 한 줄에서 첫 번째 단어입니다.

두 번째 예제에서 `localhost:9000`은 지시어 뒤의 같은 줄에 나타나므로 **인수(argument)** 입니다.

때때로 지시어는 자체 블록을 열 수 있습니다. **하위 지시어(Subdirectives)** 는 지시어 블록 내의 각 줄 시작 부분에 나타납니다:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

여기서 `lb_policy`는 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)의 하위 지시어입니다 (백엔드 간에 사용할 부하 분산 정책을 설정합니다).

**별도로 문서화되지 않는 한, 지시어는 다른 지시어 블록 내에서 사용할 수 없습니다.** 예를 들어, 파일 서버는 인증 방법을 모르기 때문에 [`basic_auth`](/docs/caddyfile/directives/basic_auth)를 [`file_server`](/docs/caddyfile/directives/file_server) 내에서 사용할 수 없습니다. 하지만 [`route`](/docs/caddyfile/directives/route), [`handle`](/docs/caddyfile/directives/handle), [`handle_path`](/docs/caddyfile/directives/handle_path) 블록은 지시어들을 함께 그룹화하도록 특별히 설계되었으므로 그 안에서 지시어를 사용할 수 있습니다.

HTTP Caddyfile이 변환될 때, HTTP 핸들러 지시어는 [`route`](/docs/caddyfile/directives/route) 블록 내에 있지 않는 한 특정 기본 [지시어 순서](/docs/caddyfile/directives#directive-order)에 따라 정렬되므로, `route` 블록을 제외하고는 지시어의 출현 순서는 중요하지 않습니다.


### 토큰과 따옴표 <a id="tokens-and-quotes"></a>

Caddyfile은 파싱되기 전에 토큰으로 렉싱(lexed)됩니다. 토큰은 공백으로 구분되므로 Caddyfile에서 공백은 중요합니다.

종종 지시어는 특정 개수의 인수를 요구합니다. 단일 인수의 값에 공백이 포함되어 있으면 두 개의 별개 토큰으로 렉싱됩니다:

```caddy-d
directive abc def
```

이는 문제가 될 수 있으며 오류나 예기치 않은 동작을 반환할 수 있습니다.

`abc def`가 단일 인수의 값이어야 한다면, 따옴표로 감싸야 합니다:

```caddy-d
directive "abc def"
```

따옴표가 포함된 토큰 내에서 따옴표를 사용해야 하는 경우 이스케이프할 수 있습니다:

```caddy-d
directive "\"abc def\""
```

따옴표 이스케이프를 피하려면 대신 백틱 <code>\` \`</code>을 사용하여 토큰을 감쌀 수 있습니다. 예:

```caddy-d
directive `{"foo": "bar"}`
```

따옴표로 감싸진 토큰 내에서는 공백, 탭, 줄 바꿈을 포함한 모든 다른 문자가 문자 그대로 처리됩니다. 따라서 여러 줄 토큰이 가능합니다:

```caddy-d
directive "first line
	second line"
```

히어독(Heredocs) <span id="heredocs"/>도 지원됩니다:

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

여는 히어독 마커는 `<<`로 시작해야 하며, 그 뒤에 임의의 텍스트(대문자 권장)가 옵니다. 닫는 히어독 마커는 동일한 텍스트여야 합니다 (위의 예에서는 `HTML`). 필요한 경우 히어독 파싱을 방지하기 위해 여는 마커를 `\<<`로 이스케이프할 수 있습니다.

닫는 마커는 들여쓰기될 수 있으며, 이 경우 텍스트의 모든 줄에서 해당만큼의 들여쓰기가 제거됩니다 ([PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)에서 영감을 얻음). 이는 [블록](#blocks) 내부에서 가독성을 높이면서 토큰 텍스트의 공백을 세밀하게 제어할 수 있게 해줍니다. 마지막 줄 바꿈도 제거되지만, 닫는 마커 앞에 빈 줄을 추가하여 유지할 수 있습니다.

닫는 마커 뒤에 지시어의 인수로 추가 토큰이 올 수 있습니다 (위 예제의 상태 코드 `200`과 같이).


## 전역 옵션 <a id="global-options"></a>

Caddyfile은 선택적으로 키가 없는 특수 블록으로 시작할 수 있는데, 이를 [전역 옵션 블록](/docs/caddyfile/options)이라고 합니다:

```caddy
{
	...
}
```

이 블록이 존재한다면, 반드시 설정의 맨 첫 번째 블록이어야 합니다.

이 블록은 전역적으로 적용되거나 특정 사이트에 국한되지 않는 옵션을 설정하는 데 사용됩니다. 내부에서는 전역 옵션만 설정할 수 있으며, 일반 사이트 지시어는 사용할 수 없습니다.

예를 들어, 문제 해결을 위해 자세한 로그를 생성하는 데 흔히 사용되는 `debug` 전역 옵션을 활성화하려면 다음과 같이 합니다:

```caddy
{
	debug
}
```

**더 자세히 알아보려면 [전역 옵션 페이지](/docs/caddyfile/options)를 읽어보세요.**



## 주소 <a id="addresses"></a>

주소는 항상 사이트 블록의 맨 위에 나타나며, 보통 Caddyfile의 첫 번째 항목입니다.

다음은 유효한 주소의 예입니다:

| 주소                 | 효과                              |
|----------------------|-----------------------------------|
| `example.com`        | 관리되는 [공개적으로 신뢰할 수 있는 인증서](/docs/automatic-https#hostname-requirements)를 사용한 HTTPS |
| `*.example.com`      | 관리되는 [와일드카드 공개 신뢰 인증서](/docs/caddyfile/patterns#wildcard-certificates)를 사용한 HTTPS |
| `localhost`          | 관리되는 [로컬에서 신뢰할 수 있는 인증서](/docs/automatic-https#local-https)를 사용한 HTTPS |
| `http://`            | HTTP catch-all, [`http_port`](/docs/caddyfile/options#http-port)의 영향을 받음 |
| `https://`           | HTTPS catch-all, [`https_port`](/docs/caddyfile/options#http-port)의 영향을 받음 |
| `http://example.com` | `Host` 매처와 함께 명시적으로 HTTP 사용 |
| `example.com:443`    | [`https_port`](/docs/caddyfile/options#http-port) 기본값과 일치하므로 HTTPS |
| `:443`               | [`https_port`](/docs/caddyfile/options#http-port) 기본값과 일치하므로 HTTPS catch-all |
| `:8080`              | 비표준 포트의 HTTP, `Host` 매처 없음 |
| `localhost:8080`     | 유효한 도메인이 있으므로 비표준 포트의 HTTPS |
| `https://example.com:443` | HTTPS지만, `https://`와 `:443`을 모두 사용하는 것은 중복임 |
| `127.0.0.1` | 로컬 신뢰 IP 인증서를 사용한 HTTPS |
| `http://127.0.0.1` | IP 주소 `Host` 매처를 사용한 HTTP (`localhost` 거부) |


<aside class="tip">

사이트 주소에 호스트 이름이나 IP 주소가 포함되어 있으면 [자동 HTTPS](/docs/automatic-https)가 활성화됩니다. 하지만 이 동작은 전적으로 암시적이므로 명시적인 설정을 덮어쓰지는 않습니다.

예를 들어, 사이트 주소가 `http://example.com`이면 스킴이 명시적으로 `http://`이므로 자동 HTTPS가 활성화되지 않습니다.

</aside>


주소로부터 Caddy는 사이트의 스킴, 호스트, 포트를 유추할 수 있습니다. 주소에 포트가 없으면 지정된 경우 스킴과 일치하는 포트를 선택하거나, 기본 포트인 443을 가정합니다.

호스트 이름을 지정하면 일치하는 `Host` 헤더가 있는 요청만 허용됩니다. 즉, 사이트 주소가 `localhost`이면 Caddy는 `127.0.0.1`로의 요청을 매칭하지 않습니다.

와일드카드(`*`)를 사용할 수 있지만, 호스트 이름의 정확히 한 라벨만 나타낼 수 있습니다. 예를 들어, `*.example.com`은 `foo.example.com`과는 일치하지만 `foo.bar.example.com`과는 일치하지 않으며, `*`는 `localhost`와는 일치하지만 `example.com`과는 일치하지 않습니다. 실제 사례는 [와일드카드 인증서 패턴](/docs/caddyfile/patterns#wildcard-certificates)을 참조하세요.

모든 호스트를 잡으려면 주소의 호스트 부분을 생략하십시오. 예: 단순히 `https://`. 이는 도메인을 미리 알 수 없는 [온디맨드(On-Demand) TLS](/docs/automatic-https#on-demand-tls)를 사용할 때 유용합니다.

여러 사이트가 동일한 정의를 공유하는 경우, 공백과 쉼표로 구분하여 한꺼번에 나열할 수 있습니다 (최소한 하나의 공백이 필요합니다). 다음 세 가지 예는 동일합니다:

```caddy
# 쉼표로 구분된 사이트 주소
localhost:8080, example.com, www.example.com {
	...
}
```

또는

```caddy
# 공백으로 구분된 사이트 주소
localhost:8080 example.com www.example.com {
	...
}
```

또는

```caddy
# 쉼표와 줄 바꿈으로 구분된 사이트 주소
localhost:8080,
example.com,
www.example.com {
	...
}
```

주소는 고유해야 합니다. 동일한 주소를 두 번 이상 지정할 수 없습니다.

[플레이스홀더](#placeholders)는 주소에서 사용할 수 **없지만**, Caddyfile 스타일의 [환경 변수](#environment-variables)는 사용할 수 있습니다:

```caddy
{$DOMAIN:localhost} {
	...
}
```

기본적으로 사이트는 모든 네트워크 인터페이스에 바인딩됩니다. 이를 변경하려면 [`bind` 지시어](/docs/caddyfile/directives/bind) 또는 [`default_bind` 전역 옵션](/docs/caddyfile/options#default-bind)을 사용하십시오.



## 매처 <a id="matchers"></a>

HTTP 핸들러 [지시어](#directives)는 별도로 문서화되지 않는 한 기본적으로 모든 요청에 적용됩니다.

[요청 매처(Request matchers)](/docs/caddyfile/matchers)를 사용하여 주어진 기준에 따라 요청을 분류할 수 있습니다. 매처를 사용하면 특정 지시어가 적용될 요청을 정확하게 지정할 수 있습니다.

매처를 지원하는 지시어의 경우, 지시어 뒤의 첫 번째 인수가 **매처 토큰**입니다. 다음은 몇 가지 예입니다:

```caddy-d
root *           /var/www  # 매처 토큰: *
root /index.html /var/www  # 매처 토큰: /index.html
root @post       /var/www  # 매처 토큰: @post
```

매처 토큰을 완전히 생략하여 모든 요청을 매칭할 수 있습니다. 예를 들어, 다음 인수가 경로 매처처럼 보이지 않는다면 `*`를 생략해도 됩니다.

**더 자세히 알아보려면 [요청 매처 페이지](/docs/caddyfile/matchers)를 읽어보세요.**




## 플레이스홀더 <a id="placeholders"></a>

[플레이스홀더(Placeholders)](/docs/conventions#placeholders)는 정적 구성에 동적인 값을 주입하는 간단한 방법입니다. 지시어와 하위 지시어의 인수로 사용할 수 있습니다.

플레이스홀더는 양쪽이 중괄호 `{ }`로 둘러싸여 있으며 내부에 식별자가 포함됩니다. 예: `{foo.bar}`. 여는 중괄호를 이스케이프 `\{like.this}` 처리하여 교체를 방지할 수 있습니다. 플레이스홀더 식별자는 일반적으로 모듈 간의 충돌을 피하기 위해 점으로 구분된 네임스페이스를 가집니다.

어떤 플레이스홀더를 사용할 수 있는지는 문맥(context)에 따라 다릅니다. 모든 플레이스홀더가 설정의 모든 부분에서 사용 가능한 것은 아닙니다. 예를 들어, [HTTP 앱이 설정하는 플레이스홀더](/docs/json/apps/http/#docs)는 HTTP 요청 처리와 관련된 설정 영역(즉, HTTP 핸들러 [지시어](#directives)와 [매처](#matchers))에서만 사용할 수 있으며, [`tls` 구성](/docs/caddyfile/directives/tls)에서는 사용할 수 *없습니다*. 일부 지시어나 매처는 자체 플레이스홀더를 설정할 수도 있으며, 이는 그 뒤에 오는 모든 항목에서 사용할 수 있습니다. 일부 플레이스홀더는 [전역적으로 사용 가능](/docs/conventions#placeholders)합니다.

Caddyfile에서 모든 플레이스홀더를 사용할 수 있지만, 편의를 위해 Caddyfile이 파싱될 때 확장되는 다음과 같은 동등한 축약형을 사용할 수도 있습니다:

| Caddyfile        | 대체 항목                            |
|------------------|-------------------------------------|
| `{cookie.*}`     | `{http.request.cookie.*}`           |
| `{client_ip}`    | `{http.vars.client_ip}`             |
| `{dir}`          | `{http.request.uri.path.dir}`       |
| `{err.*}`        | `{http.error.*}`                    |
| `{file_match.*}` | `{http.matchers.file.*}`            |
| `{file.base}`    | `{http.request.uri.path.file.base}` |
| `{file.ext}`    | `{http.request.uri.path.file.ext}`  |
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

모든 구성 필드가 플레이스홀더를 지원하는 것은 아니지만, 예상되는 대부분의 필드에서는 지원합니다. 플레이스홀더 지원은 해당 필드에 명시적으로 추가되어야 합니다. 플러그인 개발자는 [이 문서](/docs/extending-caddy/placeholders)를 읽고 자신의 모듈에 플레이스홀더 지원을 추가하는 방법을 배울 수 있습니다.




## 스니펫 <a id="snippets"></a>

이름을 괄호로 감싸서 스니펫(snippets)이라고 불리는 특수 블록을 정의할 수 있습니다:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

그런 다음 특수 지시어인 [`import`](/docs/caddyfile/directives/import)를 사용하여 필요한 곳 어디에서나 이를 재사용할 수 있습니다:

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

[`import`](/docs/caddyfile/directives/import) 지시어는 다른 파일을 해당 위치에 포함하는 데에도 사용할 수 있습니다. 인수가 정의된 스니펫과 일치하지 않으면 파일로 간주하여 시도합니다. 또한 여러 파일을 가져오기 위한 와일드카드(globs)를 지원합니다. 특수한 경우로, `import`는 Caddyfile 내 어디에나 나타날 수 있으며(다른 지시어의 인수인 경우 제외), 사이트 블록 외부도 포함됩니다:

```caddy
{
	email admin@example.com
}

import sites/*
```

가져온 구성(스니펫 또는 파일)에 인수를 전달하고 다음과 같이 사용할 수 있습니다:

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

⚠️ *실험적 기능* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

가져온 스니펫에 선택적 블록을 전달하고 다음과 같이 사용할 수도 있습니다.

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

**더 자세히 알아보려면 [`import` 지시어 페이지](/docs/caddyfile/directives/import)를 읽어보세요.**


## 명명된 라우트 <a id="named-routes"></a>

⚠️ *실험적 기능*

명명된 라우트(Named routes)는 [스니펫](#snippets)과 유사한 구문을 사용합니다. 사이트 블록 외부에서 정의되는 특수 블록으로, `&(`로 시작하고 `)`로 끝나며 그 사이에 이름이 들어갑니다.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

그런 다음 모든 사이트 내에서 이 명명된 라우트를 재사용할 수 있습니다:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

이는 많은 다른 사이트에서 동일한 라우트가 필요하거나, 동일한 라우트를 호출하기 위해 여러 다른 매처 조건이 필요한 경우 메모리 사용량을 줄이는 데 특히 유용합니다.

**더 자세히 알아보려면 [`invoke` 지시어 페이지](/docs/caddyfile/directives/invoke)를 읽어보세요.**



## 주석 <a id="comments"></a>

주석은 `#`로 시작하여 줄 끝까지 이어집니다:

```caddy-d
# 주석은 줄의 시작 부분에 올 수 있고
directive  # 또는 끝에 올 수 있습니다
```

주석을 나타내는 해시 문자 `#`는 토큰 중간에 나타날 수 없습니다 (즉, 앞에 공백이 있거나 줄의 맨 처음에 있어야 합니다). 이를 통해 따옴표를 사용하지 않고도 URI나 다른 값 내부에서 해시를 사용할 수 있습니다.



## 환경 변수 <a id="environment-variables"></a>

구성이 환경 변수에 의존하는 경우, Caddyfile에서 이를 사용할 수 있습니다:

```caddy
{$ENV}
```

이 형식의 환경 변수는 **Caddyfile 파싱이 시작되기 전에** 치환되므로, 빈 값(즉, `""`), 부분 토큰, 전체 토큰 또는 여러 토큰과 줄로 확장될 수 있습니다.

예를 들어, 환경 변수 `UPSTREAMS="app1:8080 app2:8080 app3:8080"`은 여러 [토큰](#tokens-and-quotes)으로 확장됩니다:

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

환경 변수를 찾을 수 없을 때 사용할 기본값은 변수 이름과 기본값 사이에 `:`를 구분자로 사용하여 지정할 수 있습니다:

```caddy
{$DOMAIN:localhost} {

}
```

환경 변수의 치환을 런타임까지 **지연**시키고 싶다면 [표준 `{env.*}` 플레이스홀더](/docs/conventions#placeholders)를 사용할 수 있습니다. 단, 모듈 개발자가 해당 필드에 대해 치환 코드를 추가해야 하므로 모든 구성 매개변수가 이 플레이스홀더를 지원하는 것은 아닙니다. 작동하지 않는 경우 지원을 요청하는 이슈를 제기해 주십시오.

예를 들어, [`caddy-dns/cloudflare` 플러그인 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare)이 설치되어 있고 [DNS 챌린지](/docs/automatic-https#dns-challenge)를 구성하려는 경우, 다음과 같이 플러그인에 `CLOUDFLARE_API_TOKEN` 환경 변수를 전달할 수 있습니다:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Caddy를 systemd 서비스로 실행 중인 경우, 환경 변수를 정의하기 위한 서비스 오버라이드 설정은 [이 지침](/docs/running#overrides)을 참조하세요.
