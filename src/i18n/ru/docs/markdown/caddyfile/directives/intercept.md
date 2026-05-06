---
title: intercept (директива Caddyfile)
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

Обобщенная абстракция возможности [response interception](reverse_proxy#intercepting-responses) из [директивы `reverse_proxy`](reverse_proxy). Ее можно использовать с любым handler, который создает ответы, включая handlers из plugins, например `php_server` из [FrankenPHP](https://frankenphp.dev/).

Эта директива позволяет [сопоставлять ответы](/docs/caddyfile/response-matchers), после чего вызывается первый совпавший route `handle_response` или `replace_status`. При вызове исходное тело ответа удерживается, что дает этому route возможность записать другое тело ответа, с новым status code или с любыми необходимыми изменениями response header. Если route *не* записывает новое тело ответа, вместо него записывается исходное тело ответа.


<a id="syntax"></a>
## Синтаксис

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

- **@name** — именованный блок [response matcher](/docs/caddyfile/response-matchers). Пока у каждого response matcher уникальное имя, можно определить несколько matchers. Ответ можно сопоставлять по status code и по наличию или значению response header.

- **replace_status** <span id="replace_status"/> просто изменяет status code ответа, если он совпал с заданным matcher.

- **handle_response** <span id="handle_response"/> определяет route, который нужно выполнить, когда исходный ответ совпадает с заданным response matcher. Если matcher опущен, intercept применяется ко всем ответам. Когда определено несколько блоков `handle_response`, применяется первый совпавший блок. Внутри блока можно использовать все остальные [directives](/docs/caddyfile/directives).

Внутри routes `handle_response` доступны следующие placeholders для получения информации из исходного ответа:

- `{resp.status_code}` Status code исходного ответа.

- `{resp.header.*}` Headers из исходного ответа.


<a id="examples"></a>
## Примеры

При использовании `php_server` из [FrankenPHP](https://frankenphp.dev/) можно использовать `intercept`, чтобы реализовать поддержку `X-Accel-Redirect` и отдавать статические файлы по запросу PHP app:

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
