---
title: route (diretiva do Caddyfile)
---

# route

Avalia um grupo de diretivas literalmente e como uma única unidade.

Diretivas contidas em um bloco `route` não serão [reordenadas internamente](/docs/caddyfile/directives#directive-order). Apenas diretivas de HTTP handler (diretivas que adicionam handlers ou middleware à cadeia) podem ser usadas em um bloco `route`.

Esta diretiva é um caso especial, pois suas subdiretivas também são diretivas regulares.


## Sintaxe

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** é uma lista de diretivas ou blocos de diretiva, uma por linha, como fora de um bloco `route`; exceto que essas diretivas não serão reordenadas. Apenas diretivas de HTTP handler podem ser usadas.



## Utilidade

A diretiva `route` é útil em alguns casos avançados ou de borda para assumir controle absoluto sobre partes da cadeia de HTTP handlers.

Como a ordem de avaliação dos middlewares HTTP é significativa, o Caddyfile normalmente reordena as diretivas depois do parsing para facilitar o uso; você não precisa se preocupar com a ordem em que as escreve.

Embora a [ordem embutida](/docs/caddyfile/directives#directive-order) seja compatível com a maioria dos sites, às vezes você precisa tomar controle manual da ordem, seja para o site inteiro ou apenas para uma parte dele. É para isso que a diretiva `route` serve.

Para ilustrar, considere o caso de dois handlers terminais: [`redir`](redir) e [`file_server`](file_server). Ambos escrevem a resposta ao cliente e não chamam o próximo handler na cadeia, então apenas um deles será executado para uma requisição específica. Qual vem primeiro? Normalmente, `redir` é executado antes de `file_server` porque, em geral, você quer emitir um redirecionamento apenas em casos específicos e servir arquivos no caso geral.

No entanto, pode haver ocasiões em que a primeira diretiva (`file_server`) tenha um matcher mais específico do que a segunda (`redir`). Em outras palavras, você quer redirecionar no caso geral e servir apenas um arquivo específico.

Então você pode tentar um Caddyfile como este (mas isso não funcionará como esperado!):

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

O problema é que, depois que as [diretivas são ordenadas](/docs/caddyfile/directives#sorting-algorithm), `redir` vem antes de `file_server`.

Mas, neste caso, o matcher de `redir` (um [`*`](/docs/caddyfile/matchers#wildcard-matchers) implícito) é um superconjunto do matcher de `file_server` (`*` é um superconjunto de `/specific.html`).

Felizmente, a solução é fácil: basta envolver as duas diretivas em um bloco `route`, para garantir que `file_server` seja executado antes de `redir`:

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

Outra forma de fazer isso é tornar os dois matchers mutuamente exclusivos, mas isso pode ficar rapidamente complexo se houver mais de uma ou duas condições. Com a diretiva `route`, a exclusividade mútua dos dois handlers é implícita porque ambos são handlers terminais.

</aside>

E agora `file_server` será encadeado antes de `redir`, porque a ordem é tomada literalmente.



## Diretivas semelhantes

Há outras diretivas que podem encapsular diretivas de HTTP handler, mas cada uma tem seu uso dependendo do comportamento que você quer expressar:

- [`handle`](handle) encapsula outras diretivas como `route` faz, mas com duas diferenças: 1) blocos `handle` são mutuamente exclusivos entre si, e 2) diretivas dentro de um `handle` são [reordenadas](/docs/caddyfile/directives#directive-order) normalmente.

- [`handle_path`](handle_path) faz o mesmo que `handle`, mas remove um prefixo da requisição antes de executar seus handlers.

- [`handle_errors`](handle_errors) é como `handle`, mas só é invocada quando o Caddy encontra um erro durante o processamento da requisição.



## Exemplos

Faça proxy de requisições para `/api` como estão, e reescreva todas as outras requisições com base em se elas correspondem a um arquivo no disco, caso contrário `/index.html`. Então esse arquivo é servido.

Como [`try_files`](try_files) tem uma ordem de diretivas mais alta que [`reverse_proxy`](reverse_proxy), normalmente ele seria ordenado acima e executado primeiro; isso faria com que as requisições da API fossem todas reescritas para `/index.html` e falhassem em corresponder a `/api*`, de modo que nenhuma delas seria enviada ao proxy e, em vez disso, resultaria em um `404` do [`file_server`](file_server). Envolver tudo em um `route` garante que `reverse_proxy` sempre execute primeiro, antes de a requisição ser reescrita.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Essa não é a única solução para esse problema. Você também pode usar um par de blocos [`handle`](handle), com o primeiro correspondendo a `/api*` para `reverse_proxy`, e o segundo atuando como fallback e servindo os arquivos. Veja [este exemplo](/docs/caddyfile/patterns#single-page-apps-spas) de uma SPA.

</aside>
