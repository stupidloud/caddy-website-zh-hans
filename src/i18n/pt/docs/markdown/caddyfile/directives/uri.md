---
title: uri (Caddyfile directive)
---

# uri

Manipula o URI de uma requisição. Pode remover prefixos/sufixos de caminho ou substituir trechos no URI inteiro.

Esta diretiva é distinta de [`rewrite`](rewrite) porque `uri` altera o URI de forma incremental, em vez de redefini-lo completamente como `rewrite` faz. Enquanto `rewrite` é tratado de modo especial como um redirecionamento interno, `uri` é apenas outro middleware.


<a id="syntax"></a>
## Sintaxe

São suportadas várias operações diferentes:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

O primeiro argumento (fora o matcher) especifica a operação:

- **strip_prefix** remove o prefixo do caminho.

- **strip_suffix** remove o sufixo do caminho.

- **replace** faz uma substituição de substring em todo o URI.

	- **&lt;target&gt;** é o prefixo, o sufixo ou a string/padrão de busca/expressão regular. Se for um prefixo, a barra inicial pode ser omitida, já que os caminhos sempre começam com uma barra.

	- **&lt;replacement&gt;** é a string de substituição. Suporta o uso de grupos de captura com a sintaxe `$name` ou `${name}`, ou com um número para o índice, como `$1`. Veja a [documentação do Go](https://golang.org/pkg/regexp/#Regexp.Expand) para detalhes. Se o valor de substituição for `""`, o texto correspondente será removido do valor.

	- **&lt;limit&gt;** é um limite opcional para o número máximo de substituições.

- **path_regexp** executa uma substituição por expressão regular na parte do caminho do URI.

	- **&lt;target&gt;** é o prefixo, o sufixo ou a string/padrão de busca/expressão regular. Se for um prefixo, a barra inicial pode ser omitida, já que os caminhos sempre começam com uma barra.

	- **&lt;replacement&gt;** é a string de substituição. Suporta o uso de grupos de captura com a sintaxe `$name` ou `${name}`, ou com um número para o índice, como `$1`. Veja a [documentação do Go](https://golang.org/pkg/regexp/#Regexp.Expand) para detalhes. Se o valor de substituição for `""`, o texto correspondente será removido do valor.

- **query** faz manipulações na query do URI, com o modo dependendo do prefixo do nome do parâmetro ou da contagem de argumentos. Um bloco pode ser usado para especificar várias operações de uma vez, agrupadas e executadas nesta ordem: renomear 🡒 definir 🡒 anexar 🡒 substituir 🡒 remover.

	- Sem prefixo, o parâmetro é definido com o valor fornecido na query.
	
	  Por exemplo, `uri query foo bar` definirá o valor do parâmetro `foo` como `bar`.

	- Use o prefixo `-` para remover o parâmetro da query.
	
	  Por exemplo, `uri query -foo` excluirá o parâmetro `foo`.

	- Use o prefixo `+` para anexar um parâmetro à query, com o valor fornecido. Isso _não_ sobrescreverá um parâmetro existente com o mesmo nome (omita o `+` para sobrescrever).
	
	  Por exemplo, `uri query +foo bar` anexará `foo=bar` à query.

	- Um parâmetro com `>` como infixo renomeia o parâmetro para o valor depois do `>`. 
	
	  Por exemplo, `uri query foo>bar` renomeará o parâmetro `foo` para `bar`.

	- Com três argumentos, é feita uma substituição por expressão regular no valor da query, em que o primeiro argumento é o nome do parâmetro, o segundo é o valor a buscar e o terceiro é a substituição. O primeiro argumento (nome do parâmetro) pode ser `*` para aplicar a substituição em todos os parâmetros de query.
	
	  Suporta o uso de grupos de captura com a sintaxe `$name` ou `${name}`, ou com um número para o índice, como `$1`. Veja a [documentação do Go](https://golang.org/pkg/regexp/#Regexp.Expand) para detalhes. Se o valor de substituição for `""`, o texto correspondente será removido do valor.
	
	  Por exemplo, `uri query foo ^(ba)r $1z` substituiria o valor do parâmetro `foo`, quando o valor começasse com `bar`, resultando em `baz`.

As mutações de URI ocorrem na forma normalizada ou sem escape do URI. No entanto, sequências de escape podem ser usadas nos padrões de prefixo ou sufixo para corresponder apenas aos escapes literais nessas posições do caminho da requisição. Por exemplo, `uri strip_prefix /a/b` reescreverá tanto `/a/b/c` quanto `/a%2Fb/c` para `/c`; e `uri strip_prefix /a%2Fb` reescreverá `/a%2Fb/c` para `/c`, mas não corresponderá a `/a/b/c`.

O caminho do URI é limpo de pontos de travessia de diretório antes das modificações. Além disso, múltiplas barras (como `//`) são mescladas, a menos que `<target>` contenha múltiplas barras também.


<a id="similar-directives"></a>
## Diretivas semelhantes

Outras diretivas também podem manipular o URI da requisição.

- [`rewrite`](rewrite) altera o caminho e a query inteiros para um novo valor, em vez de mudar apenas parte do valor.

- [`handle_path`](handle_path) faz o mesmo que [`handle`](handle), mas remove um prefixo da requisição antes de executar seus handlers. Pode ser usado no lugar de `uri strip_prefix` para eliminar uma linha extra de configuração em muitos casos.


<a id="examples"></a>
## Exemplos

Remover `/api` do início de todos os caminhos de requisição:

```caddy-d
uri strip_prefix /api
```

Remover `.php` do fim de todos os caminhos de requisição:

```caddy-d
uri strip_suffix .php
```

Substituir "/docs/" por "/v1/docs/" em qualquer URI de requisição:

```caddy-d
uri replace /docs/ /v1/docs/
```

Compactar todas as barras repetidas no caminho da requisição (mas não na query) para uma única barra:

```caddy-d
uri path_regexp /{2,} /
```

Definir o valor do parâmetro de query `foo` como `bar`:

```caddy-d
uri query foo bar
```

Remover o parâmetro `foo` da query:

```caddy-d
uri query -foo
```

Renomear o parâmetro de query `foo` para `bar`:

```caddy-d
uri query foo>bar
```

Anexar o parâmetro `bar` à query:

```caddy-d
uri query +foo bar
```

Substituir o valor do parâmetro de query `foo` quando o valor começar com `bar`, trocando-o por `baz`:

```caddy-d
uri query foo ^(ba)r $1z
```

Executar várias operações de query de uma vez:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
