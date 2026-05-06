---
title: respond (diretiva do Caddyfile)
---

# respond

Escreve uma resposta estática/fixa para o cliente.

Se o corpo não estiver vazio, esta diretiva define o cabeçalho `Content-Type` se ele ainda não estiver definido. O valor padrão é `text/plain; utf-8`, a menos que o corpo seja um objeto ou array JSON válido, caso em que ele é definido como `application/json`. Para todos os outros tipos de conteúdo, defina o `Content-Type` correto explicitamente usando a [`diretiva header`](/docs/caddyfile/directives/header).


## Sintaxe

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** é o código de status HTTP a ser escrito.

  Se for `103` (Early Hints), a resposta será escrita sem corpo e a cadeia de handlers continuará. (Respostas HTTP `1xx` são informativas, não finais.)
  
  Padrão: `200`

- **&lt;body&gt;** é o corpo da resposta a ser escrito.

- **body** é uma forma alternativa de fornecer um corpo; útil se ele tiver várias linhas.

- **close** fecha a conexão do cliente com o servidor depois de escrever a resposta.

Para esclarecer, o primeiro argumento que não seja matcher pode ser tanto um código de status de 3 dígitos quanto uma string de corpo de resposta. Se for um corpo, o próximo argumento pode ser o código de status.

<aside class="tip">

Responder com um código de status de erro é diferente de retornar um erro na cadeia de handlers, que invoca tratadores de erro internamente.

</aside>


## Exemplos

Escrever um 200 vazio com um corpo vazio para todos os health checks, e um corpo de resposta simples para todas as outras requisições:

```caddy
example.com {
	respond /health-check 200
	respond "Olá, mundo!"
}
```

Escrever uma resposta de erro e fechar a conexão:

<aside class="tip">

Talvez você prefira usar a [`diretiva error`](error) em vez disso, que dispara um erro que pode ser tratado com a [`diretiva handle_errors`](handle_errors).

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

Escrever uma resposta HTML, usando [sintaxe heredoc](/docs/caddyfile/concepts#heredocs) para controlar o whitespace, e também definir o cabeçalho `Content-Type` para corresponder ao corpo da resposta:

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
