---
title: "import（Caddyfile 指令）"
---

# 导入

包含一个[代码片段](/docs/caddyfile/concepts#snippets)或文件，并将此指令替换为该代码片段或文件的内容。

该指令属于特例：它会在解析结构之前进行求值，并且可以在 Caddyfile 的任意位置出现。

## 语法

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** 是要包含的文件名、通配符模式或[代码片段](/docs/caddyfile/concepts#snippets)名称。其内容将替换本行，效果如同该文件的内容原本就出现在此处一样。

  如果找不到特定文件，则视为错误；但空的通配符模式不构成错误。

  如果导入特定文件，当该文件为空时，系统会发出警告。

  如果模式是一个文件名或通配符，它总是相对于 `import` 所在的文件。

  如果将通配符模式 `*` 作为路径的最后一段，隐藏文件（即以 `.`）将被忽略。若要导入隐藏文件，请将 `.*` 作为最后一个路径段。
- **&lt;args...&gt;** 是一个可选的参数列表，用于传递给导入的令牌。该占位符属于特殊情况，会在解析 Caddyfile 时进行求值，而非运行时。其用法形式多样，类似于 [Go 语言的切片语法](https://gobyexample.com/slices)：
  - `{args[n]}` 其中 `n` 是该参数的从0开始的索引
  - `{args[:]}` 所有参数插入的位置
  - `{args[:m]}` 其中 `m` 处插入
  - `{args[n:]}` 其中以 `n` 的参数插入的位置
  - `{args[n:m]}` 其中，该范围内的参数 `n` 和 `m` 之间

  对于需要插入多个标记的表单，占位符**必须**本身就是一个[标记](/docs/caddyfile/concepts#tokens-and-quotes)，不能是另一个标记的一部分。换句话说，它周围必须有空格，且不能被引号包围。

  请注意，在 v2.7.0 之前，语法是 `{args.N}` 但该形式已被弃用，建议改用上述更灵活的语法。

⚠️ *实验性* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** 是一个可选的块，用于传递给导入的令牌。该占位符属于特殊情况，会在解析 Caddyfile 时进行递归求值，而非在运行时。它有两种使用形式：
  - `{block}` 其中，占位符将被提供的整个代码块的内容替换
  - `{blocks.key}` 其中 `key` 是所提供代码块中某个参数的第一个标记


## 示例

导入相邻的 sites-enabled 文件夹中的所有文件（隐藏文件除外）：

```caddy-d
import sites-enabled/*
```

导入一个通过导入参数设置 CORS 头部的代码片段：

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

导入一个将代理上游列表作为参数的代码片段：

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

导入一个代码片段，该片段会创建一个代理，并将前缀重写规则作为第一个参数：

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ *实验性* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

导入一个代码片段，该片段返回可配置的“hello world”消息，并指定内容类型：

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

导入一个为反向代理提供可扩展选项的代码片段：

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

导入一个可处理任意指令集的代码片段，但需预先加载中间件：

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
