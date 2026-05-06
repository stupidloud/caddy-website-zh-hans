---
title: intercept (diretiva do Caddyfile)
---

<script>
ready(function() {
	// Corrige os matchers de resposta para renderizarem com a cor certa,
	// e cria links para a seção de matchers de resposta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Matcher de resposta">${text}</a>`;
		}
	});

	// Matchers de resposta
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

	// Vamos adicionar links a todas as subdiretivas se um anchor correspondente for encontrado na página.
	addLinksToSubdirectives();
});
</script>

# intercept

Uma abstração generalizada do recurso de [interceptação de respostas](reverse_proxy#intercepting-responses) da [`diretiva reverse_proxy`](reverse_proxy). Isso pode ser usado com qualquer handler que produza respostas, incluindo aqueles de plugins como o `php_server` do [FrankenPHP](https://frankenphp.dev/).

Esta diretiva permite que você [corresponda respostas](/docs/caddyfile/response-matchers), e a primeira rota `handle_response` ou `replace_status` correspondente será invocada. Quando invocada, o corpo da resposta original é segurado, dando à rota a chance de escrever um corpo de resposta diferente, com um novo código de status ou com qualquer manipulação necessária de cabeçalhos de resposta. Se a rota _não_ escrever um novo corpo de resposta, então o corpo de resposta original será escrito em seu lugar.


## Sintaxe

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

- **@name** é um bloco nomeado de [matcher de resposta](/docs/caddyfile/response-matchers). Desde que cada matcher de resposta tenha um nome único, vários matchers podem ser definidos. Uma resposta pode ser correspondida pelo código de status e pela presença ou valor de um cabeçalho de resposta.

- **replace_status** <span id="replace_status"/> simplesmente altera o código de status da resposta quando ela corresponde ao matcher fornecido.

- **handle_response** <span id="handle_response"/> define a rota a executar quando a resposta original corresponde ao matcher de resposta fornecido. Se um matcher for omitido, todas as respostas serão interceptadas. Quando vários blocos `handle_response` são definidos, o primeiro bloco correspondente será aplicado. Dentro do bloco, todas as outras [diretivas](/docs/caddyfile/directives) podem ser usadas.

Dentro de rotas `handle_response`, os seguintes placeholders ficam disponíveis para extrair informações da resposta original:

- `{resp.status_code}` O código de status da resposta original.

- `{resp.header.*}` Os cabeçalhos da resposta original.


## Exemplos

Ao usar o `php_server` do [FrankenPHP](https://frankenphp.dev/), você pode usar `intercept` para implementar suporte a `X-Accel-Redirect`, servindo arquivos estáticos conforme solicitado pelo app PHP:

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
