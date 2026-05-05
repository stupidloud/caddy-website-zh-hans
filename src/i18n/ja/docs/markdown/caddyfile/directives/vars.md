---
title: vars (Caddyfile directive)
---

# vars

リクエスト処理 chain の後段で使うために、1 つ以上の変数を特定の値に設定します。

変数にアクセスする主な方法は、`{vars.variable_name}` 形式の placeholder、または [`vars`](/docs/caddyfile/matchers#vars) と [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp) request matcher です。

[`templates`](templates) ディレクティブでは `placeholder` function を使って変数を使用できます。例: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

特殊なケースとして、replacer に保存される `http.auth.user.id` という名前の変数を上書きし、[access logs](log) の `user_id` フィールドを更新できます。


<a id="syntax"></a>
## 構文

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** は設定する変数名です。

- **&lt;value&gt;** は変数の値です。

  値は可能であれば型変換されます。`true` と `false` は boolean 型に変換され、数値は内容に応じて integer または float に変換されます。この変換を避けて string のまま保持するには、[quotes](/docs/caddyfile/concepts#tokens-and-quotes) で囲んでください。

<a id="examples"></a>
## 例

リクエスト path に応じて値が決まる単一の変数を設定し、その値で応答します。

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

複数の変数を設定し、それぞれを適切な scalar 型へ変換します。

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
