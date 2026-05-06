---
title: redir (diretiva do Caddyfile)
---

# redir

Emite um redirecionamento HTTP para o cliente.

Esta diretiva implica que uma requisição correspondente deve ser rejeitada como está, e o cliente deve tentar novamente em outra URL. Por isso, sua [ordem de diretivas](/docs/caddyfile/directives#directive-order) é bem precoce.


## Sintaxe

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** é o local de destino. Torna-se o [`cabeçalho Location` <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location) da resposta.

- **&lt;code&gt;** é o código de status HTTP a usar para o redirecionamento. Pode ser:

	- Um inteiro positivo na faixa `3xx`, ou `401`
	
	- `temporary` para um redirecionamento temporário (`302`, este é o padrão)
	
	- `permanent` para um redirecionamento permanente (`301`)
	
	- `html` para usar um documento HTML para executar o redirecionamento (útil para redirecionar navegadores, mas não clientes de API)
	
	- Um placeholder com um valor de código de status



## Exemplos

Redirecionar todas as requisições para `https://example.com`:

```caddy
www.example.com {
	redir https://example.com
}
```

O mesmo, mas preservando a URI existente ao anexar o [placeholder `{uri}`](/docs/caddyfile/concepts#placeholders):

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

O mesmo, mas permanente:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Redirecionar sua antiga página `/about-us` para sua nova página `/about`:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
