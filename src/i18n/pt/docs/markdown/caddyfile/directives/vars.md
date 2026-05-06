---
title: vars (Caddyfile directive)
---

# vars

Define uma ou mais variáveis para um valor específico, para serem usadas mais tarde na cadeia de tratamento da requisição.

A principal forma de acessar variáveis é com placeholders, que têm a forma `{vars.variable_name}`, ou com os matchers de requisição [`vars`](/docs/caddyfile/matchers#vars) e [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

Você pode usar variáveis com a diretiva [`templates`](templates) usando a função `placeholder`, por exemplo: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

Como caso especial, é possível sobrescrever a variável chamada `http.auth.user.id`, que fica armazenada no replacer, para atualizar o campo `user_id` nos [logs de acesso](log).


<a id="syntax"></a>
## Sintaxe

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** é o nome da variável a definir.

- **&lt;value&gt;** é o valor da variável.

  O valor será convertido de tipo, se possível; `true` e `false` serão convertidos para booleanos, e valores numéricos serão convertidos para inteiro ou float conforme apropriado. Para evitar essa conversão e mantê-los como strings, você pode colocá-los entre [aspas](/docs/caddyfile/concepts#tokens-and-quotes).

<a id="examples"></a>
## Exemplos

Para definir uma única variável, com o valor condicionado pelo caminho da requisição e depois responder com esse valor:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

Para definir várias variáveis, cada uma convertida para o tipo escalar apropriado:

```caddy-d
vars {
	# booleano
	abc true

	# inteiro
	def 1

	# float
	ghi 2.3

	# string
	jkl "example"
}
```
