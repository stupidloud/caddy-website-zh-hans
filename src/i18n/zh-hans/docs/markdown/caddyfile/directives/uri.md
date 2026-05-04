---
title: "uri（Caddyfile 指令）"
---

# uri

操作请求的 URI。它可以去除路径的前缀/后缀，或替换整个 URI 中的子字符串。

该指令与[`rewrite`](rewrite)的不同之处在于 `uri` 会*可微分地*更改 URI，而非像 `rewrite` 所做的那样将其重置为完全不同的值。而 `rewrite` 被作为内部重定向进行特殊处理， `uri` 它仅仅是另一个中间件。



## 语法

支持多种不同的操作：

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

第一个（非匹配）参数指定操作：

- **strip_prefix** 用于从路径中移除前缀。

- **strip_suffix** 用于从路径中移除后缀。

- **replace** 会在整个 URI 中执行子字符串替换。

	- **&lt;target&gt;** 是前缀、后缀或搜索字符串/正则表达式。如果是前缀，可以省略开头的正斜杠，因为路径总是以正斜杠开头。

	- **&lt;replacement&gt;** 是替换字符串。支持使用捕获组，其中 `$name` 或 `${name}` 语法，或使用数字指定索引，例如 `$1`。详情请参阅 [Go 文档](https://golang.org/pkg/regexp/#Regexp.Expand)。如果替换值为 `""`，则会从该值中移除匹配的文本。

	- **&lt;limit&gt;** 是替换次数上限的可选参数。

- **path_regexp** 对 URI 的路径部分执行正则表达式替换。

	- **&lt;target&gt;** 是前缀、后缀或搜索字符串/正则表达式。如果是前缀，可以省略开头的正斜杠，因为路径总是以正斜杠开头。

	- **&lt;replacement&gt;** 是替换字符串。支持使用捕获组，其中 `$name` 或 `${name}` 语法，或使用数字指定索引，例如 `$1`。详情请参阅 [Go 文档](https://golang.org/pkg/regexp/#Regexp.Expand)。如果替换值为 `""`，则会从该值中移除匹配的文本。

- **query** 对 URI 查询进行操作，其模式取决于参数名前缀或参数个数。可以使用代码块一次性指定多项操作，这些操作将按以下顺序分组并执行：重命名 🡒 设置 🡒 追加 🡒 替换 🡒 删除。

	- 如果没有前缀，则该参数将设置为查询中给定的值。
	
	  例如， `uri query foo bar` 将设置 `foo` 参数的值为 `bar`.

	- 在前缀 `-` 以从查询中移除该参数。
	
	  例如， `uri query -foo` 将删除 `foo` 参数。

	- 在前缀前添加 `+` 可在查询后附加一个参数，并赋予指定值。这将*不会*覆盖同名的现有参数（如需覆盖，请省略 `+` 以进行覆盖）。
	
	  例如，`uri query +foo bar` 将在查询中添加 `foo=bar`。

	- 若将 `>` 作为中缀的参数，参数会被重命名为 `>`。

	  例如，`uri query foo>bar` 将把参数 `foo` 重命名为 `bar`。

	- 若提供三个参数，则会执行查询值正则表达式替换操作，其中第一个参数是查询参数名称，第二个是搜索值，第三个是替换内容。第一个参数（参数名称）可以 `*` 以对所有查询参数执行替换。
	
	  支持使用捕获组与 `$name` 或 `${name}` 语法，或使用数字指定索引，例如 `$1`。详情请参阅 [Go 文档](https://golang.org/pkg/regexp/#Regexp.Expand)。如果替换值为 `""`，则会从该值中移除匹配的文本。
	
	  例如， `uri query foo ^(ba)r $1z` 将替换 `foo` param，其中该值以 `bar` ，从而导致该值变为 `baz`.

URI 变体操作作用于 URI 的规范化或未转义形式。不过，可以在前缀或后缀模式中使用转义序列，以便仅匹配请求路径中这些位置上的字面转义序列。例如， `uri strip_prefix /a/b` 将重写 `/a/b/c` 和 `/a%2Fb/c` 重写为 `/c`；而 `uri strip_prefix /a%2Fb` 将重写 `/a%2Fb/c` 为 `/c`，但不会匹配 `/a/b/c`.

在进行修改之前，会从 URI 路径中移除用于目录遍历的点。此外，除非 `//`）会被合并，除非 `<target>` 本身也包含多个斜杠。


## 类似指令

还有其他一些指令也可以修改请求 URI。

- [`rewrite`](rewrite) 会将整个路径和查询条件替换为新值，而不是仅修改其中部分内容。

- [`handle_path`](handle_path) 的作用与 [`handle`](handle) 相同，但它会在运行处理程序之前从请求中移除前缀。可替代 `uri strip_prefix` ，在许多情况下可省去多余的一行配置。



## 示例

从 `/api` 从所有请求路径的开头移除：

```caddy-d
uri strip_prefix /api
```

从 `.php` 从所有请求路径的末尾移除：

```caddy-d
uri strip_suffix .php
```

在任何请求 URI 中，将“/docs/”替换为“/v1/docs/”：

```caddy-d
uri replace /docs/ /v1/docs/
```

将请求路径（但不包括请求查询）中所有重复的斜杠合并为一个斜杠：

```caddy-d
uri path_regexp /{2,} /
```

设置 `foo` 查询参数的值设置为 `bar`:

```caddy-d
uri query foo bar
```

从查询中移除 `foo` 参数：

```caddy-d
uri query -foo
```

重命名 `foo` 查询参数为 `bar`:

```caddy-d
uri query foo>bar
```

将 `bar` 参数：

```caddy-d
uri query +foo bar
```

将 `foo` 查询参数的值，该值以 `bar` 替换为 `baz`:

```caddy-d
uri query foo ^(ba)r $1z
```

一次执行多个查询操作：

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
