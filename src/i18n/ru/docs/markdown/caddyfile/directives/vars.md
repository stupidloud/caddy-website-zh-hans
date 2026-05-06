---
title: vars (директива Caddyfile)
---

# vars

Устанавливает одну или несколько variables в конкретное значение для дальнейшего использования в request handling chain.

Основной способ доступа к variables — placeholders вида `{vars.variable_name}` или request matchers [`vars`](/docs/caddyfile/matchers#vars) и [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

Variables можно использовать с директивой [`templates`](templates) через функцию `placeholder`, например: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

В качестве особого случая можно переопределить variable с именем `http.auth.user.id`, которая хранится в replacer, чтобы обновить поле `user_id` в [access logs](log).


<a id="syntax"></a>
## Синтаксис

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** — имя variable, которое нужно установить.

- **&lt;value&gt;** — значение variable.

  Значение будет преобразовано по типу, если это возможно; `true` и `false` будут преобразованы в boolean types, а числовые значения — в integer или float соответственно. Чтобы избежать этого преобразования и сохранить их как strings, можно обернуть их [кавычками](/docs/caddyfile/concepts#tokens-and-quotes).

<a id="examples"></a>
## Примеры

Установить одну variable, значение которой зависит от request path, затем ответить этим значением:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

Установить несколько variables, каждая из которых преобразуется в подходящий scalar type:

```caddy-d
vars {
	# boolean
	abc true

	# integer
	def 1

	# float
	ghi 2.3

	# string
	jkl "example"
}
```
