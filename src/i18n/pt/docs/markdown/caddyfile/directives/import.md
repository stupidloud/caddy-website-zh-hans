---
title: import (diretiva do Caddyfile)
---

# import

Inclui um [snippet](/docs/caddyfile/concepts#snippets) ou arquivo, substituindo esta diretiva pelo conteúdo do snippet ou arquivo.

Esta diretiva é um caso especial: ela é avaliada antes de a estrutura ser analisada, e pode aparecer em qualquer lugar do Caddyfile.

## Sintaxe

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** é o nome do arquivo, padrão glob ou nome do [snippet](/docs/caddyfile/concepts#snippets) a incluir. O conteúdo dele substituirá esta linha como se já tivesse aparecido aqui desde o início.

  É um erro se um arquivo específico não puder ser encontrado, mas um padrão glob vazio não é um erro.

  Se importar um arquivo específico, um aviso será emitido se o arquivo estiver vazio.

  Se o padrão for um nome de arquivo ou glob, ele é sempre relativo ao arquivo em que `import` aparece.

  Se usar um padrão glob `*` como o último segmento do caminho, arquivos ocultos (isto é, arquivos que começam com `.`) são ignorados. Para importar arquivos ocultos, use `.*` como segmento final.
- **&lt;args...&gt;** é uma lista opcional de argumentos para passar aos tokens importados. Esse placeholder é um caso especial e é avaliado em tempo de parsing do Caddyfile, não em runtime. Eles podem ser usados em várias formas, de modo semelhante à [sintaxe de slice do Go](https://gobyexample.com/slices):
  - `{args[n]}` onde `n` é o índice posicional baseado em 0 do parâmetro
  - `{args[:]}` onde todos os argumentos são inseridos
  - `{args[:m]}` onde os argumentos antes de `m` são inseridos
  - `{args[n:]}` onde os argumentos começando em `n` são inseridos
  - `{args[n:m]}` onde os argumentos no intervalo entre `n` e `m` são inseridos

  Para as formas que inserem vários tokens, o placeholder **deve** ser um [token](/docs/caddyfile/concepts#tokens-and-quotes) por si só; ele não pode fazer parte de outro token. Em outras palavras, ele precisa ter espaços ao redor e não pode estar entre aspas.

  Note que, antes da v2.7.0, a sintaxe era `{args.N}`, mas essa forma foi descontinuada em favor da sintaxe mais flexível acima.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** é um bloco opcional a ser passado para os tokens importados. Esse placeholder é um caso especial e é avaliado recursivamente em tempo de parsing do Caddyfile, não em runtime. Ele pode ser usado em duas formas:
  - `{block}` onde o conteúdo de todo o bloco fornecido será substituído pelo placeholder
  - `{blocks.key}` onde `key` é o primeiro token de um parâmetro dentro do bloco fornecido


## Exemplos

Importar todos os arquivos em uma pasta adjacente sites-enabled (exceto arquivos ocultos):

```caddy-d
import sites-enabled/*
```

Importar um snippet que define cabeçalhos CORS usando um argumento de import:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Importar um snippet que recebe uma lista de upstreams de proxy como argumentos:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Importar um snippet que cria um proxy com uma regra de rewrite de prefixo como primeiro argumento:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Importar um snippet que responde com uma mensagem "hello world" configurável e content-type:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Importar um snippet que fornece opções extensíveis para um reverse proxy:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Importar um snippet que serve qualquer conjunto de diretivas, mas com um middleware pré-carregado:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
