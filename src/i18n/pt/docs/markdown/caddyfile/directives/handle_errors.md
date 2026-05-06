---
title: handle_errors (diretiva do Caddyfile)
---

# handle_errors

Define tratadores de erro.

Quando os handlers normais de requisição HTTP retornam um erro, o processamento normal é interrompido e os tratadores de erro são invocados. Os tratadores de erro formam uma rota que é igual às rotas normais, e podem fazer qualquer coisa que rotas normais podem fazer. Isso oferece grande controle e flexibilidade ao lidar com erros durante requisições HTTP. Por exemplo, você pode servir páginas de erro estáticas, páginas de erro com templates ou fazer reverse proxy para outro backend tratar os erros.

A diretiva pode ser repetida com diferentes códigos de status para tratar erros diferentes de maneiras diferentes. Se nenhum código de status for especificado, ela corresponderá a qualquer erro, funcionando como fallback se nenhum outro tratador de erro corresponder.

O contexto de uma requisição é carregado para as rotas de erro, então quaisquer valores definidos no contexto da requisição, como [site root](root) ou [vars](vars), também serão preservados nos tratadores de erro. Além disso, [novos placeholders](#placeholders) ficam disponíveis ao tratar erros.

Observe que certas diretivas, por exemplo [`reverse_proxy`](reverse_proxy), que podem escrever uma resposta com um status HTTP classificado como erro, _não_ vão disparar as rotas de erro.

Você pode usar a diretiva [`error`](error) para disparar explicitamente um erro com base nas suas próprias decisões de roteamento.


## Sintaxe

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** é um ou mais códigos de status HTTP para comparar com o erro que está sendo tratado. Os códigos podem ser números de 3 dígitos, ou um caso especial `4xx` ou `5xx`, que correspondem a todos os códigos nas faixas 400-499 ou 500-599, respectivamente. Se nenhum código de status for especificado, ele corresponderá a qualquer erro, funcionando como fallback se nenhum outro tratador de erro corresponder.

- **<directives...>** é uma lista de [diretivas](/docs/caddyfile/directives) e [matchers](/docs/caddyfile/matchers) de HTTP handler, uma por linha.


## Placeholders

Os seguintes placeholders ficam disponíveis ao tratar erros. Eles são [atalhos do Caddyfile](/docs/caddyfile/concepts#placeholders) para os placeholders completos que podem ser encontrados [na documentação JSON para rotas de erro de um servidor HTTP](/docs/json/apps/http/servers/errors/#routes).

| Placeholder | Descrição |
|---|---|
| `{err.status_code}` | O código de status HTTP recomendado |
| `{err.status_text}` | O texto de status associado ao código de status recomendado |
| `{err.message}` | A mensagem de erro |
| `{err.trace}` | A origem do erro |
| `{err.id}` | Um identificador para essa ocorrência do erro |


## Exemplos

Páginas de erro personalizadas com base no código de status (isto é, uma página chamada `404.html` para erros `404`). Observe que [`file_server`](file_server) preserva o código de status HTTP do erro quando executado em `handle_errors` (assumindo que você definiu um [site root](root) no seu site antes):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Uma única página de erro que usa [`templates`](templates) para escrever uma mensagem de erro personalizada:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Se você quiser fornecer páginas de erro personalizadas apenas para alguns códigos de erro, pode verificar previamente a existência dos arquivos de erro personalizados com um matcher [`file`](/docs/caddyfile/matchers#file):

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

Faça reverse proxy para um servidor profissional altamente qualificado em lidar com erros HTTP e melhorar seu dia 😸:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Use simplesmente [`respond`](respond) para retornar o código e o nome do erro

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Para tratar códigos de erro específicos de forma diferente:

```caddy-d
handle_errors 404 410 {
	respond "É um erro 404 ou 410!"
}

handle_errors 5xx {
	respond "É um erro 5xx."
}

handle_errors {
	respond "É outro erro"
}
```

O comportamento acima é o mesmo que o abaixo, que usa um matcher [`expression`](/docs/caddyfile/matchers#expression) contra os códigos de status e usa [`handle`](handle) para exclusividade mútua:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "É um erro 404 ou 410!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "É um erro 5xx."
	}

	handle {
		respond "É outro erro"
	}
}
```
