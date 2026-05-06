---
title: basic_auth (diretiva do Caddyfile)
---

# basic_auth

Habilita HTTP Basic Authentication, que pode ser usada para proteger diretórios e arquivos com um nome de usuário e uma senha com hash.

**Observe que basic auth não é segura sobre HTTP puro.** Use critério ao decidir o que proteger com HTTP Basic Authentication.

Quando um usuário solicita um recurso protegido, o navegador pedirá um nome de usuário e uma senha se ele ainda não tiver fornecido um. Se as credenciais corretas estiverem presentes no cabeçalho Authorization, o servidor concederá acesso ao recurso. Se o cabeçalho estiver ausente ou as credenciais estiverem incorretas, o servidor responderá com HTTP 401 Unauthorized.

A configuração do Caddy não aceita senhas em texto puro; você **DEVE** fazer hash delas antes de colocá-las na configuração. O comando [`caddy hash-password`](/docs/command-line#caddy-hash-password) pode ajudar com isso.

Após uma autenticação bem-sucedida, o placeholder `{http.auth.user.id}` ficará disponível, contendo o nome de usuário autenticado.

Antes da v2.8.0, esta diretiva se chamava `basicauth`, mas foi renomeada para consistência com outras diretivas.


## Sintaxe

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** especifica o algoritmo de hash de senha (ou função de derivação de chave) usado para os hashes nesta configuração. As opções disponíveis incluem `argon2id`; o padrão é `bcrypt`.

- **&lt;realm&gt;** é um nome de realm personalizado.

- **&lt;username&gt;** é um nome de usuário ou ID de usuário.

- **&lt;hashed_password&gt;** é o hash da senha.


## Exemplos

Exigir autenticação para todas as requisições para `example.com`:

```caddy
example.com {
	basic_auth {
		# Usuário "Bob", senha "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Bem-vindo, {http.auth.user.id}" 200
}
```

Proteger arquivos em `/secret/` para que apenas `Bob` possa acessá-los (e qualquer pessoa possa ver outros caminhos):

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# Usuário "Bob", senha "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

Exemplo com `argon2id`

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# Usuário "Bob", senha "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
