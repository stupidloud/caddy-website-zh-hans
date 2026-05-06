---
title: handle_path (Caddyfile directive)
---

<script>
ready(function() {
	// Adiciona um link para [<path_matcher>] como caso especial desta diretiva.
	// O texto do matcher inclui caracteres <> que são analisados como HTML,
	// então precisamos usar text() para alterar o texto do link.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Matcher token">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

Funciona da mesma forma que a diretiva [`handle`](handle), mas usa implicitamente [`uri strip_prefix`](uri) para remover o prefixo de caminho correspondente.

Tratar uma requisição que corresponda a um determinado caminho, ao mesmo tempo removendo esse caminho do URI da requisição, é um caso de uso comum o suficiente para ter sua própria diretiva por conveniência.


<a id="syntax"></a>
## Sintaxe

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** é uma lista de diretivas de handler HTTP ou blocos de diretivas, uma por linha, exatamente como seria usado fora de um bloco `handle_path`.

Apenas um [path matcher](/docs/caddyfile/matchers#path-matchers) é aceito, e ele é obrigatório; você não pode usar matchers nomeados com `handle_path`.

<a id="examples"></a>
## Exemplos

Esta configuração:

```caddy-d
handle_path /prefix/* {
	...
}
```

é efetivamente o mesmo que isto abaixo, mas a forma `handle_path` é um pouco mais sucinta:

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

Um exemplo completo de Caddyfile, onde `handle_path` e `handle` são mutuamente exclusivos; porém, tenha em mente o [problema de subpasta <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# Serve sua API, removendo o prefixo /api
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Serve seu site estático
	handle {
		root /srv
		file_server
	}
}
```
