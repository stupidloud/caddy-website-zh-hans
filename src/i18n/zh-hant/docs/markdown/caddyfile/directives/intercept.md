---
title: intercept (Caddyfile 指令)
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

<a id="intercept"></a>
# intercept

這是一個對 [`reverse_proxy` 指令](reverse_proxy) 中的 [回應攔截 (response interception)](reverse_proxy#intercepting-responses) 功能的通用抽象。它可以與任何產生回應的處理程序 (handler) 一起使用，包括來自 [FrankenPHP](https://frankenphp.dev/) 的 `php_server` 等外掛程式。

此指令允許您 [匹配回應 (match responses)](/docs/caddyfile/response-matchers)，並會調用第一個匹配的 `handle_response` 路由或 `replace_status`。調用時，原始的回應主體會被保留，讓該路由有機會寫入不同的回應主體、使用新的狀態碼或進行任何必要的回應標頭操作。如果路由 **沒有** 寫入新的回應主體，則會改為寫入原始的回應主體。


<a id="syntax"></a>
## Syntax

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

- **@name** 是一個具名的 [response matcher](/docs/caddyfile/response-matchers) 區塊。只要每個 response matcher 都有唯一的名稱，就可以定義多個 matcher。回應可以根據狀態碼以及回應標頭的存在與否或其值來進行匹配。

- **replace_status** <span id="replace_status"/> 當被指定的 matcher 匹配時，僅簡單地更改回應的狀態碼。

- **handle_response** <span id="handle_response"/> 定義當原始回應被指定的 response matcher 匹配時要執行的路由。如果省略 matcher，則所有回應都會被攔截。當定義了多個 `handle_response` 區塊時，將套用第一個匹配的區塊。在區塊內，可以使用所有其他的 [directives](/docs/caddyfile/directives)。

在 `handle_response` 路由中，可以使用以下 placeholder 來從原始回應中獲取資訊：

- `{resp.status_code}` 原始回應的狀態碼。

- `{resp.header.*}` 原始回應的標頭。


<a id="examples"></a>
## Examples

當使用 [FrankenPHP](https://frankenphp.dev/) 的 `php_server` 時，您可以使用 `intercept` 來實現 `X-Accel-Redirect` 支援，根據 PHP 應用程式的要求提供靜態檔案：

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
