---
title: "intercept（Caddyfile 指令）"
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

# 拦截

这是对[`reverse_proxy`指令](reverse_proxy)中[响应拦截](reverse_proxy#intercepting-responses)功能的通用抽象实现。它可与任何生成响应的处理程序配合使用，包括来自 [FrankenPHP](https://frankenphp.dev/) 等插件的处理程序，例如 `php_server`。

此指令允许您[匹配响应](/docs/caddyfile/response-matchers)，并让第一个匹配的 `handle_response` 路由或 `replace_status` 规则被调用。调用时，原始响应正文会被暂存，从而使该路由有机会写入不同的响应正文，包括使用新的状态码或进行任何必要的响应头操作。如果该路由未写入新的响应正文，则将写入原始响应正文。


## 语法

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

- **@name** 是一个命名[响应匹配器](/docs/caddyfile/response-matchers)块。只要每个响应匹配器都有一个唯一的名称，就可以定义多个匹配器。可以通过状态码以及响应头是否存在或其值来匹配响应。

- **replace_status**  仅在匹配到给定的匹配器时更改响应的状态码。

- **handle_response**  用于定义当原始响应与给定的响应匹配器匹配时应执行的路由。如果省略匹配器，则所有响应都会被拦截。当定义了多个 `handle_response` 块时，将应用第一个匹配的块。在该块内部，可以使用所有其他[指令](/docs/caddyfile/directives)。

在 `handle_response` 路由中，可使用以下占位符从原始响应中提取信息：

- `{resp.status_code}` 原始响应的状态码。

- `{resp.header.*}` 原始响应的头部信息。


## 示例

在使用 [FrankenPHP](https://frankenphp.dev/) 的 `php_server` 时，您可以使用 `intercept` 来实现 `X-Accel-Redirect` 支持，根据 PHP 应用程序的要求提供静态文件：

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
