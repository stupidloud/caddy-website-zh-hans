---
title: "vars（Caddyfile 指令）"
---

# 变量

将一个或多个变量设置为特定值，以便在后续的请求处理链中使用。

访问变量的主要方式是使用占位符，其形式为 `{vars.variable_name}`，或者使用[`vars`](/docs/caddyfile/matchers#vars)和[`vars_regexp`](/docs/caddyfile/matchers#vars_regexp)请求匹配器。

您可以使用 `placeholder` 函数，例如： `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

作为一种特例，可以覆盖名为 `http.auth.user.id`（该变量存储在替换器中），从而更新 `user_id` 字段。


## 语法

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** 是要设置的变量名。

- **&lt;value&gt;** 是该变量的值。

  如果可能，该值将进行类型转换； `true` 并且 `false` 将转换为布尔类型，数值将相应地转换为整数或浮点数。若要避免此类转换并保留其字符串形式，可使用[引号](/docs/caddyfile/concepts#tokens-and-quotes)将其包裹起来。

## 示例

要设置一个变量，其值根据请求路径动态确定，然后返回该值：

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

要设置多个变量，并将每个变量转换为相应的标量类型：

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
