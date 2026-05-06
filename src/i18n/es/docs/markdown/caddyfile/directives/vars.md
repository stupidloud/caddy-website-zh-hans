---
title: vars (directiva de Caddyfile)
---

# vars

Establece una o más variables a un valor concreto para usarlas más tarde en la cadena de manejo de la solicitud.

La forma principal de acceder a las variables es mediante placeholders, con la forma `{vars.variable_name}`, o con los request matchers [`vars`](/docs/caddyfile/matchers#vars) y [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

Puedes usar variables con la directiva [`templates`](templates) usando la función `placeholder`, por ejemplo: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

Como caso especial, es posible sobrescribir la variable llamada `http.auth.user.id`, que se almacena en el replacer, para actualizar el campo `user_id` en los [logs de acceso](log).


## Sintaxis

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** es el nombre de la variable a establecer.

- **&lt;value&gt;** es el valor de la variable.

  El valor se convertirá de tipo si es posible; `true` y `false` se convertirán a tipos booleanos, y los valores numéricos se convertirán a entero o float según corresponda. Para evitar esta conversión y mantenerlos como cadenas, puedes envolverlos con [comillas](/docs/caddyfile/concepts#tokens-and-quotes).

## Ejemplos

Para establecer una sola variable, con valor condicional según la ruta de solicitud, y luego responder con el valor:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

Para establecer múltiples variables, cada una convertida al tipo escalar apropiado:

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
