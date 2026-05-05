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

Eine verallgemeinerte Abstraktion des Features [Response Interception](reverse_proxy#intercepting-responses) aus der Direktive [`reverse_proxy`](reverse_proxy). Sie kann mit jedem Handler verwendet werden, der Responses erzeugt, einschließlich Handlern aus Plugins wie [FrankenPHP](https://frankenphp.dev/)s `php_server`.

Mit dieser Direktive können Sie [Responses matchen](/docs/caddyfile/response-matchers); die erste passende `handle_response`-Route oder `replace_status` wird aufgerufen. Beim Aufruf wird der ursprüngliche Response-Body zurückgehalten, sodass diese Route die Möglichkeit hat, einen anderen Response-Body zu schreiben, mit neuem Statuscode oder mit den nötigen Response-Header-Manipulationen. Wenn die Route *keinen* neuen Response-Body schreibt, wird stattdessen der ursprüngliche Response-Body geschrieben.


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

- **@name** ist ein benannter [Response-Matcher](/docs/caddyfile/response-matchers)-Block. Solange jeder Response-Matcher einen eindeutigen Namen hat, können mehrere Matcher definiert werden. Eine Response kann anhand des Statuscodes und anhand der Existenz oder des Werts eines Response-Headers gematcht werden.

- **replace_status** <span id="replace_status"/> ändert schlicht den Statuscode der Response, wenn sie vom angegebenen Matcher gematcht wird.

- **handle_response** <span id="handle_response"/> definiert die Route, die ausgeführt wird, wenn die ursprüngliche Response vom angegebenen Response-Matcher gematcht wird. Wird ein Matcher weggelassen, werden alle Responses abgefangen. Wenn mehrere `handle_response`-Blöcke definiert sind, wird der erste passende Block angewendet. Innerhalb des Blocks können alle anderen [Direktiven](/docs/caddyfile/directives) verwendet werden.

Innerhalb von `handle_response`-Routes sind die folgenden Platzhalter verfügbar, um Informationen aus der ursprünglichen Response zu beziehen:

- `{resp.status_code}` Der Statuscode der ursprünglichen Response.

- `{resp.header.*}` Die Header der ursprünglichen Response.


<a id="examples"></a>
## Beispiele

Wenn Sie [FrankenPHP](https://frankenphp.dev/)s `php_server` verwenden, können Sie mit `intercept` Unterstützung für `X-Accel-Redirect` implementieren und statische Dateien ausliefern, die von der PHP-App angefordert werden:

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
