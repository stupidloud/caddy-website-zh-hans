---
title: handle (diretiva do Caddyfile)
---

# handle

Avalia um grupo de diretivas de forma mutuamente exclusiva em relação a outros blocos `handle` no mesmo nível de aninhamento.

Em outras palavras, quando várias diretivas `handle` aparecem em sequência, apenas o primeiro bloco `handle` correspondente será avaliado. Um `handle` sem matcher funciona como uma rota _fallback_.

As diretivas `handle` são ordenadas de acordo com o [algoritmo de ordenação de diretivas](/docs/caddyfile/directives#sorting-algorithm) pelos seus matchers. A diretiva [`handle_path`](handle_path) é um caso especial e fica na mesma prioridade de um `handle` com matcher de caminho.

Blocos `handle` podem ser aninhados, se necessário. Apenas diretivas de HTTP handler podem ser usadas dentro de blocos `handle`.

## Sintaxe

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** é uma lista de diretivas de HTTP handler ou blocos de diretiva, uma por linha, exatamente como seriam usadas fora de um bloco `handle`.



## Diretivas semelhantes

Há outras diretivas que podem encapsular diretivas de HTTP handler, mas cada uma tem sua utilidade dependendo do comportamento que você quer expressar:

- [`handle_path`](handle_path) faz o mesmo que `handle`, mas remove um prefixo da requisição antes de executar seus handlers.

- [`handle_errors`](handle_errors) é como `handle`, mas só é invocada quando o Caddy encontra um erro durante o processamento da requisição.

- [`route`](route) encapsula outras diretivas como `handle` faz, mas com duas diferenças:
  1. blocos `route` não são mutuamente exclusivos entre si,
  2. diretivas dentro de um `route` não são [reordenadas](/docs/caddyfile/directives#directive-order), dando a você mais controle quando necessário.



## Exemplos

Trate requisições em `/foo/` com o servidor de arquivos estáticos, e outras requisições com o reverse proxy:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

Você pode misturar `handle` e [`handle_path`](handle_path) no mesmo site, e eles ainda serão mutuamente exclusivos entre si:

```caddy
example.com {
	handle_path /foo/* {
		# O caminho tem o prefixo "/foo" removido
	}

	handle /bar/* {
		# O caminho ainda mantém "/bar"
	}
}
```

Você pode aninhar blocos `handle` para criar uma lógica de roteamento mais complexa:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Este bloco corresponde apenas a caminhos sob /foo/bar
		}

		handle {
			# Este bloco corresponde a todo o resto sob /foo/
		}
	}

	handle {
		# Este bloco corresponde a todo o resto (funciona como fallback)
	}
}
```
