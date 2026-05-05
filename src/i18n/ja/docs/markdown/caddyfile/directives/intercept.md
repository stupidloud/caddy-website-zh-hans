---
title: intercept (Caddyfile directive)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Response matchers
	const nameMatchers = Array.from($$_('pre.chroma .nd')).filter(item => item.innerText.includes('@name'));
	if (nameMatchers.length > 0) {
		const first = nameMatchers[0];
		const span = document.createElement('span');
		span.className = 'nd';
		first.parentNode.insertBefore(span, first);
		span.appendChild(first);
		span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;">@name</a>';
	}
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText === 'status') {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;">status</a>';
		}
	});
	
	const headerElements = $$_('pre.chroma .k');
	for (let item of headerElements) {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;">header</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# intercept

[`reverse_proxy` ディレクティブ](reverse_proxy)の[レスポンス傍受](reverse_proxy#intercepting-responses)機能を、より汎用化した抽象化です。[FrankenPHP](https://frankenphp.dev/) の `php_server` のようなプラグインを含め、レスポンスを生成する任意の handler と組み合わせて使えます。

このディレクティブでは[レスポンスをマッチ](/docs/caddyfile/response-matchers)でき、最初にマッチした `handle_response` route または `replace_status` が呼び出されます。呼び出されると、元のレスポンスボディは保留され、その route が別のレスポンスボディ、新しいステータスコード、または必要なレスポンス header 操作を書き込めます。その route が新しいレスポンスボディを書き込ま*ない*場合は、代わりに元のレスポンスボディが書き込まれます。


<a id="syntax"></a>
## 構文

```caddy-d
intercept [<matcher>] {
	@name {
		status <code...>
		header <field> [<value>]
	}

	replace_status [<response_matcher>] <code>

	handle_response [<response_matcher>] {
		<directives...>
	}
}
```

- **@name** は名前付きの [response matcher](/docs/caddyfile/response-matchers) ブロックです。各 response matcher の名前が一意であれば、複数の matcher を定義できます。レスポンスは、ステータスコードとレスポンス header の存在または値でマッチできます。

- **replace_status** <span id="replace_status"/> は、指定された matcher にマッチしたレスポンスのステータスコードを単純に変更します。

- **handle_response** <span id="handle_response"/> は、元のレスポンスが指定された response matcher にマッチしたときに実行する route を定義します。matcher を省略すると、すべてのレスポンスが傍受されます。複数の `handle_response` ブロックが定義されている場合、最初にマッチしたブロックが適用されます。ブロック内では、他のすべての[ディレクティブ](/docs/caddyfile/directives)を使えます。

`handle_response` route 内では、元のレスポンスから情報を取り出すために次の placeholder を使えます。

- `{resp.status_code}` 元のレスポンスのステータスコード。

- `{resp.header.*}` 元のレスポンスの header。


<a id="examples"></a>
## 例

[FrankenPHP](https://frankenphp.dev/) の `php_server` を使う場合、`intercept` で `X-Accel-Redirect` サポートを実装し、PHP アプリが要求した静的ファイルを配信できます。

```caddy
localhost {
	root /srv

	intercept {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}

	php_server
}
```
