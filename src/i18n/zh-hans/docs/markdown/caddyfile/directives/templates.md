---
title: "模板（Caddyfile 指令）"
---

# 模板

将响应正文作为[模板](/docs/modules/http.handlers.templates)文档执行。模板提供了用于创建简单动态页面的基础功能。其功能包括 HTTP 子请求、HTML 文件包含、Markdown 渲染、JSON 解析、基本数据结构、随机数生成、时间处理等。


## 语法

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** 指模板中间件将处理的 MIME 类型；任何不包含符合条件的 `Content-Type` 的响应，都不会被视为模板进行处理。

  默认： `text/html text/plain`.

- **between** 是模板操作的开始和结束分隔符。如果它们与文档的其他部分冲突，您可以进行修改。

  默认： `{{printf "{{ }}"}}`.

- **root** 是网站根目录，在使用访问文件系统的函数时。

  默认使用由[`root`](root)指令设置的站点根目录；如果未设置，则使用当前工作目录。

- **extensions** 允许您注册由位于 `http.handlers.templates.functions.*` 命名空间中。

  块内的每个子指令都对应一个模块名称。这些模块可以向模板函数映射中添加自定义函数，通常用于实现可复用的组件。此功能主要面向插件。

有关内置模板函数的文档，请参见 [templates 模块](/docs/modules/http.handlers.templates#docs)。



## 示例

若想了解一个使用模板来呈现 Markdown 内容的完整网站示例，不妨看看本网站的源代码！具体来说，请查看 [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) 和 [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html)。

为静态网站启用模板：

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

若要使用模板返回简单的静态响应，请确保设置 `Content-Type`:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

使用模板扩展（插件）：

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# 需要 caddy-hitcounter 插件：
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
