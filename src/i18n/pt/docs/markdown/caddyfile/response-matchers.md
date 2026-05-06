---
title: Matchers de resposta (Caddyfile)
---

<script>
ready(function() {
	// Matchers de resposta
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// Vamos adicionar links a todas as subdiretivas se um anchor correspondente for encontrado na página.
	addLinksToSubdirectives();
});
</script>

<a id="response-matchers"></a>
# Matchers de resposta

**Matchers de resposta** podem ser usados para filtrar (ou classificar) respostas por critérios específicos.

Eles normalmente só aparecem como configuração dentro de certas outras diretivas, para tomar decisões sobre a resposta enquanto ela está sendo enviada ao cliente.

- [Sintaxe](#syntax)
- [Matchers](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## Sintaxe

Se uma diretiva aceitar matchers de resposta, o uso será representado como `[<response_matcher>]` ou `[<inline_response_matcher>]` na documentação da sintaxe.

- O token **<response_matcher>** pode ser o nome de um matcher de resposta nomeado declarado anteriormente. Por exemplo: `@name`.
- O token **<inline_response_matcher>** pode ser o próprio critério da resposta, sem exigir declaração prévia. Por exemplo: `status 200`.

### Named

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
Se apenas um aspecto da resposta for relevante para a diretiva, você pode colocar o nome e o critério na mesma linha:

```caddy-d
@name status <code...>
```

### Inline

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

<a id="matchers"></a>
## Matchers

<a id="status"></a>
### status

```caddy-d
status <code...>
```

Pelo código de status HTTP.

- **&lt;code...&gt;** é uma lista de códigos de status HTTP. Casos especiais são strings como `2xx` e `3xx`, que correspondem a todos os códigos nos intervalos `200`-`299` e `300`-`399`, respectivamente.

#### Exemplo:

```caddy-d
@success status 2xx
```



<a id="header"></a>
### header

```caddy-d
header <field> [<value>]
```

Por campos de cabeçalho da resposta.

- `<field>` é o nome do campo de cabeçalho HTTP a verificar.
	- Se for prefixado com `!`, o campo não deve existir para corresponder (omita o argumento de valor).
- `<value>` é o valor que o campo deve ter para corresponder.
	- Se for prefixado com `*`, faz uma correspondência rápida de sufixo (aparece no final).
	- Se for suffixado com `*`, faz uma correspondência rápida de prefixo (aparece no início).
	- Se estiver entre `*`, faz uma correspondência rápida de substring (aparece em qualquer lugar).
	- Caso contrário, é uma correspondência exata rápida.

Campos diferentes dentro do mesmo conjunto são combinados com AND. Vários valores por campo são combinados com OR.

Observe que campos de cabeçalho podem ser repetidos e ter valores diferentes. Aplicações de backend DEVEM considerar que os valores dos campos de cabeçalho são arrays, não valores singulares, e o Caddy não interpreta significado nessas situações.

#### Exemplo:

Corresponde a respostas com o cabeçalho `Foo` contendo o valor `bar`:

```caddy-d
@upgrade header Foo *bar*
```

Corresponde a respostas com o cabeçalho `Foo` tendo o valor `bar` OU `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Corresponde a respostas que não têm o cabeçalho `Foo`:

```caddy-d
@not_foo header !Foo
```
