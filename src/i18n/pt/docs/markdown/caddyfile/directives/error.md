---
title: error (diretiva do Caddyfile)
---

# error

Dispara um erro na cadeia de handlers HTTP, com uma mensagem opcional e um código de status HTTP recomendado.

Este handler não escreve uma resposta. Em vez disso, ele foi feito para ser combinado com a diretiva [`handle_errors`](handle_errors) para invocar sua lógica personalizada de tratamento de erros.


## Sintaxe

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** é o código de status HTTP a ser escrito. Padrão: `500`.
- **&lt;message&gt;** é a mensagem de erro. Padrão: nenhuma mensagem de erro.
- **message** é uma forma alternativa de fornecer uma mensagem de erro; útil se ela tiver várias linhas.

Para esclarecer, o primeiro argumento que não seja matcher pode ser tanto um código de status de 3 dígitos quanto uma string de mensagem de erro. Se for uma mensagem de erro, o próximo argumento pode ser o código de status.


## Exemplos

Dispare um erro em certos caminhos de requisição e use [`handle_errors`](handle_errors) para escrever uma resposta:

```caddy
example.com {
	root /srv

	# Dispara erros para certos caminhos
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Trata o erro servindo uma página HTML
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
