---
title: "响应匹配器（Caddyfile）"
---

<script>
ready(function() {
	// Response matchers
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# 响应匹配器

**响应匹配器**可用于根据特定条件过滤（或分类）响应。

这些通常仅作为某些其他指令内部的配置出现，用于在响应写入客户端时做出相关决策。

- [语法](#syntax)
- [匹配器](#matchers)
	- [状态](#status)
	- [标头](#header)
<a id="syntax"></a>
## 语法

如果一个指令支持响应匹配器，其用法可表示为 `[<response_matcher>]` 或 `[<inline_response_matcher>]` 。

- **<response_matcher>** 标记可以是之前声明的命名响应匹配器的名称。例如： `@name`.
- **<inline_response_matcher>** 标记本身即可作为响应条件，无需事先声明。例如： `status 200`.

<a id="named"></a>
### 名称

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
如果响应中只有一个方面与该指令相关，您可以将名称和标准放在同一行：

```caddy-d
@name status <code...>
```

<a id="inline"></a>
### 内联

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

<a id="matchers"></a>
## 匹配器

<a id="status"></a>
### 状态

```caddy-d
status <code...>
```

按 HTTP 状态码。

- **&lt;code...&gt;** 是一组 HTTP 状态码。特殊情况包括类似 `2xx` 和 `3xx`，它们匹配 `200`-`299` 和 `300`-`399`之间的所有状态码。

#### 示例：

```caddy-d
@success status 2xx
```



<a id="header"></a>
### 标头

```caddy-d
header <field> [<value>]
```

通过响应头字段。

- `<field>` 是要检查的 HTTP 头字段的名称。
	- 如果前面加上 `!`，则该字段必须不存在才能匹配（省略值参数）。
- `<value>` 是该字段必须匹配的值。
	- 如果前面加上 `*`，则执行快速后缀匹配（出现在末尾）。
	- 如果后缀为 `*`，则执行快速前缀匹配（出现在开头）。
	- 如果被 `*`，则执行快速子字符串匹配（出现在任何位置）。
	- 否则，这将是一次快速的精确匹配。

同一组内的不同标头字段采用“与”运算。每个字段中的多个值采用“或”运算。

请注意，标头字段可能会重复出现，且具有不同的值。后端应用程序必须将标头字段的值视为数组，而非单个值，而 Caddy 不会对这类情况进行语义解析。

#### 示例：

将响应与 `Foo` 包含该值的标头 `bar`:

```caddy-d
@upgrade header Foo *bar*
```

将响应与 `Foo` 值为 `bar` 或 `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

匹配完全不包含 `Foo` 标头字段的匹配结果：

```caddy-d
@not_foo header !Foo
```
