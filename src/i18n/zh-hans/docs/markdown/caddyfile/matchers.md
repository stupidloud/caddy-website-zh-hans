---
title: "请求匹配器（Caddyfile）"
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

# 请求匹配器

**请求匹配器**可用于根据各种条件对请求进行过滤（或分类）。

- [语法](#syntax)
	- [示例](#examples)
	- [通配符匹配器](#wildcard-matchers)
	- [路径匹配器](#path-matchers)
	- [命名匹配器](#named-matchers)
- [标准匹配器](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)

<a id="syntax"></a>
## 语法

在 Caddyfile 中，紧跟在指令后面的 **匹配符** 可以限制该指令的作用范围。匹配符可以采用以下任一形式：

1. [**`*`**](#wildcard-matchers)，用于匹配所有请求（通配符；默认）。
2. [**`/path`**](#path-matchers) 以正斜杠开头，用于匹配请求路径。
3. 使用 [**`@name`**](#named-matchers) 来指定一个 *命名匹配器*。

如果某个指令支持匹配器，它将在 `[<matcher>]` 中说明。匹配器标记通常是可选的，用 `[ ]` 表示。如果省略匹配器标记，则等同于通配符匹配器（`*`）。


<a id="examples"></a>
#### 示例

此指令适用于[所有](#wildcard-matchers) HTTP 请求：

```caddy-d
reverse_proxy localhost:9000
```

而且这里也是一样的（此处无需使用 `*`）：

```caddy-d
reverse_proxy * localhost:9000
```

但此指令仅适用于[路径](#path-matchers)以 `/api/` 开头的请求：

```caddy-d
reverse_proxy /api/* localhost:9000
```

若要匹配路径以外的内容，请定义一个[命名匹配器](#named-matchers)，并使用以下方式引用它： `@name`:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```

<a id="wildcard-matchers"></a>
### 通配符匹配器

通配符（或称“通配”）匹配器 `*` 可匹配所有请求，仅在需要匹配器标记时才需使用。例如，若您希望传递给指令的第一个参数恰好也是一个路径，那么它看起来就完全像一个路径匹配器！因此，您可以使用通配符匹配器来消除歧义，例如：

```caddy-d
root * /home/www/mysite
```

否则，该匹配器并不常被使用。如果语法没有要求，我们通常建议省略它。

<a id="path-matchers"></a>
### 路径匹配器

根据 URI 路径进行匹配是处理请求最常见的方式，因此匹配器可以内联，如下所示：

```caddy-d
redir /old.html /new.html
```

路径匹配符必须以正斜杠开头 `/`.

**[路径匹配](#path)默认采用精确匹配，而非前缀匹配。** 您必须在路径末尾添加 `*` 才能实现快速前缀匹配。请注意 `/foo*` 将匹配 `/foo` 和 `/foo/` 以及 `/foobar`；您可能实际上更希望匹配 `/foo/*` 。

<a id="named-matchers"></a>
### 命名匹配器

所有非路径匹配器或通配符匹配器的匹配器都必须是命名匹配器。这种匹配器是在任何特定指令之外定义的，并且可以重复使用。

为匹配器定义一个唯一的名称能提供更大的灵活性，让你可以将[任何可用的匹配器](#standard-matchers)组合成一个集合：

```caddy-d
@name {
	...
}
```

或者，如果集合中只有一个匹配器，你可以将其放在同一行：

```caddy-d
@name ...
```

然后，你可以像这样使用该匹配器，将其作为指令的第一个参数指定：

```caddy-d
directive @name
```

例如，该代理会将 HTTP/1.1 WebSocket 请求转发至 `localhost:6001`，并将其他请求转发至 `localhost:8080`。它匹配那些名为 `Connection` 的标头中包含 `Upgrade`，并且名为 `Upgrade` 的标头值恰好为 `websocket` 的请求：

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

如果匹配器集仅包含一个匹配器，也可以使用一行代码的语法：

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

作为一种特例，只要在匹配器名称后紧跟一个[带引号的](/docs/caddyfile/concepts#tokens-and-quotes)参数（即 CEL 表达式本身），就可以不指定名称直接使用 [`expression` 匹配器](#expression)：

```caddy-d
@not-found `{err.status_code} == 404`
```

与指令一样，命名匹配器的定义必须位于使用它们的[站点代码块](/docs/caddyfile/concepts#structure)内。

一个命名的匹配器定义构成一个“匹配器集”。集中的匹配器之间采用“且”关系；也就是说，所有匹配器都必须匹配。例如，如果集里同时包含[`header`](#header)和[`path`](#path)这两个匹配器，则两者都必须匹配。

同一类型的多个匹配器可以使用布尔代数（AND/OR）进行合并（例如，同一组中的多个[`path`](#path)匹配器），具体方法将在下文各自的章节中进行说明。

对于更复杂的布尔匹配逻辑，建议使用 [`expression` 匹配器](#expression)来编写 CEL 表达式，该表达式支持 **and** `&&`、**或** `||`以及 **括号** `( )`.


<a id="standard-matchers"></a>
## 标准匹配器

完整的匹配器文档可在[各匹配器模块的文档中](/docs/json/apps/http/servers/routes/match/)查阅。

请求可以通过以下方式进行匹配：



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

按客户端 IP 地址。支持精确的 IP 地址或 CIDR 范围。支持 IPv6 区域。

当配置了[`trusted_proxies`](/docs/caddyfile/options#trusted-proxies)全局选项时，该匹配器效果最佳；否则，其行为与[`remote_ip`](#remote-ip)匹配器完全相同。只有来自受信任代理的请求，其客户端IP才会被解析并显示在请求开头；不受信任的请求将使用直接对等方的远程IP地址，或通过[PROXY协议](/docs/caddyfile/options#proxy-protocol)设置的地址。

作为快捷方式， `private_ranges` 可用于匹配所有私有 IPv4 和 IPv6 地址范围。这相当于指定以下所有范围： `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

每个命名匹配器可以包含多个 `client_ip` ，且它们的范围将被合并并进行“或”运算。

#### 示例：

匹配来自私有IPv4地址的请求：

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

该匹配器通常与[`not`](#not)匹配器配合使用，以实现匹配结果的反转。例如，要阻止来自所有公共 IPv4 和 IPv6 地址的连接（这相当于所有私有地址范围的反向）：

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

在 [CEL 表达式](#expression)中，它看起来像这样：

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

按任何返回 `true` 或 `false` 的 CEL 表达式进行匹配。

大多数其他请求匹配器也可以作为函数在表达式中使用，这使得布尔逻辑在表达式内部比在表达式外部具有更大的灵活性。有关在 CEL 表达式中支持的语法，请参阅各匹配器的文档。

在这些 CEL 表达式中可以使用 Caddy [占位符](/docs/conventions#placeholders)（或 [Caddyfile 简写形式](/docs/caddyfile/concepts#placeholders)），因为它们会在被 CEL 环境解释之前经过预处理并转换为常规的 CEL 函数调用。如果某个占位符需要作为字符串参数传递给匹配函数，则其开头的 `{` 应使用反斜杠 `\` ，以防止其被预处理，例如 `file('\{path}.md')`.

为方便起见，如果定义的命名匹配器仅由一个 CEL 表达式组成，则可以省略匹配器名称。CEL 表达式必须[加引号](/docs/caddyfile/concepts#tokens-and-quotes)（建议使用反引号或 heredoc）。这样写起来非常简洁：

```caddy-d
@mutable `{method}.startsWith("P")`
```

在此情况下，默认使用 CEL 匹配器。

#### 示例：

匹配方法以 `P`，例如 `PUT` 或 `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

匹配处理程序返回错误状态码的请求 `404`，应与[`handle_errors`指令](/docs/caddyfile/directives/handle_errors)配合使用：

```caddy-d
@404 expression {err.status_code} == 404
```

匹配路径与两个不同正则表达式中任一个匹配的请求；这只能通过表达式来实现，因为[`path_regexp`](#path-regexp)匹配器通常在每个命名匹配器中只能出现一次：

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

或者，省略匹配器名称，并用[反引号](/docs/caddyfile/concepts#tokens-and-quotes)包裹，使其被解析为单个令牌：

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

您可以使用 [heredoc 语法](/docs/caddyfile/concepts#heredocs)来编写多行 CEL 表达式：

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

按文件分类。

- `root` 定义用于查找文件的目录。默认值为当前工作目录，或 `root` （`{http.vars.root}`）所在的目录（可通过[`root`指令](/docs/caddyfile/directives/root)设置）。

- `try_files` 检查列表中符合 try_policy 的文件。

  要匹配目录，请在路径末尾添加一个正斜杠 `/` 。所有文件路径均相对于网站[根目录](/docs/caddyfile/directives/root)，且[通配符模式](https://pkg.go.dev/path/filepath#Match)将被展开。

  如果 `try_policy` 是 `first_exist` （默认情况），则列表中的最后一项可以是一个以 `=` （例如 `=404`)，作为备选方案，系统将抛出该代码对应的错误；该错误可通过[`handle_errors`](/docs/caddyfile/directives/handle_errors)进行捕获和处理。



- `try_policy` 指定如何选择文件。默认值为 `first_exist`.

	- `first_exist` 检查文件是否存在。选择第一个存在的文件。

	- `first_exist_fallback` 与 `first_exist`，但假设列表中的最后一个元素始终存在，以避免磁盘访问。

	- `smallest_size` 选择文件大小最小的那个。

	- `largest_size` 选择文件大小最大的那个。

	- `most_recently_modified` 选择最近修改过的文件。

- `split_path` 这将导致在尝试的每个文件路径中，使用列表中找到的第一个分隔符对路径进行分割。对于每个分割后的值，包含分隔符本身在内的左侧部分将成为要尝试的文件路径。例如， `/remote.php/dav/` 使用分隔符 `.php` ，将尝试访问文件 `/remote.php`。每个分隔符必须出现在 URI 路径组件的末尾，才能作为拆分分隔符使用。这是一个小众设置，主要用于托管 PHP 网站时。

因为 `try_files` 由于 `first_exist` 非常常见，因此有一个一行代码的快捷方式：

```caddy-d
file <files...>
```

一个空的 `file` 匹配器（即其后未列出任何文件的匹配器）将检查请求的文件——即 URI 中字面指定的、相对于[网站](/docs/caddyfile/directives/root)根目录的文件——是否存在。这实际上与 `file {path}` 相同。


<aside class="tip">

由于基于磁盘上文件是否存在进行重写的情况非常常见，因此还提供了一个[`try_files`指令](/docs/caddyfile/directives/try_files)，它是 `file` 匹配器和[`rewrite`处理程序](/docs/caddyfile/directives/rewrite)的快捷方式。

</aside>


匹配成功后，将提供四个新的占位符：

- `{file_match.relative}` 文件的根目录相对路径。这在重写请求时通常很有用。
- `{file_match.absolute}` 匹配文件的绝对路径，包括根目录。
- `{file_match.type}` 文件类型， `file` 或 `directory`.
- `{file_match.remainder}` 分割文件路径后剩余的部分（如果 `split_path` 已配置）


#### 示例：

匹配路径指向已存在文件的请求：

```caddy-d
@file file
```

匹配路径后跟 `.html` 后面的路径是已存在的文件，或者如果不是，则路径指向已存在的文件：

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

与上文相同，只是使用了单行快捷方式，并且如果找不到文件，则回退到返回 404 错误：

```caddy-d
@html-or-error file {path}.html {path} =404
```

以下是几个使用 [CEL 表达式的](#expression)示例。请注意，占位符在被 CEL 环境解释之前会经过预处理并转换为常规的 CEL 函数调用，因此这里使用了字符串拼接。此外，由于当前解析的限制，如果要与占位符进行拼接，必须使用长格式：

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

根据请求头字段。

- `<field>` 是要检查的 HTTP 头字段的名称。
	- 如果前面加上 `!`，则该字段必须不存在才能匹配（省略值参数）。
- `<value>` 是该字段必须匹配的值。可以指定一个或多个。
	- 如果前面加上 `*`，则执行快速后缀匹配（出现在末尾）。
	- 如果后缀为 `*`，则执行快速前缀匹配（出现在开头）。
	- 如果被 `*`，则执行快速子字符串匹配（出现在任何位置）。
	- 否则，这将是一次快速的精确匹配。

同一组内的不同标头字段将进行“与”运算。每个字段中的多个值将进行“或”运算。

请注意，标头字段可能会重复出现，且具有不同的值。后端应用程序必须将标头字段的值视为数组，而非单个值，而 Caddy 不会对这类情况进行语义解析。

#### 示例：

匹配 `Connection` 标头中包含 `Upgrade` 的请求：

```caddy-d
@upgrade header Connection *Upgrade*
```

匹配 `Foo` 标头值为 `bar` 或 `baz` 的请求：

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

匹配完全不包含 `Foo` 标头字段的请求：

```caddy-d
@not_foo header !Foo
```

使用 [CEL 表达式](#expression)，通过检查 `Connection` 标头中是否包含 `Upgrade` ，以及 `Upgrade` 标头等于 `websocket` （HTTP/2 对此有 `:protocol` 头部用于此目的)：

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

与 [`header`](#header) 类似，但支持正则表达式。

所使用的正则表达式语言是 RE2，该语言已包含在 Go 语言中。请参阅 [RE2 语法参考](https://github.com/google/re2/wiki/Syntax)和 [Go 正则表达式语法概述](https://pkg.go.dev/regexp/syntax)。

从 v2.8.0 版本开始，如果 `name` 未提供，则名称将取自命名匹配器的名称。例如，命名匹配器 `@foo` 将导致该匹配器被命名为 `foo`。指定名称的主要优势在于，当同一个命名匹配器中使用了多个正则表达式匹配器（例如 `header_regexp` 和[`path_regexp`](#path-regexp)，或多个不同的标头字段）时，指定名称能带来显著优势。

匹配完成后，可通过指令中的[占位符](/docs/caddyfile/concepts#placeholders)访问捕获组：
- `{re.<name>.<capture_group>}` 其中：
  - `<name>` 是正则表达式的名称，
  - `<capture_group>` 是表达式中捕获组的名称或编号。

- `{re.<capture_group>}` （未命名）也会被填充，以便于使用。需要注意的是，如果依次使用了多个正则表达式匹配器，则占位符的值会被下一个匹配器覆盖。

捕获组 `0` 是完整的正则表达式匹配， `1` 是第一个捕获组， `2` 是第二个捕获组，以此类推。因此 `{re.foo.1}` 或 `{re.1}` 都将包含第一个捕获组的值。

每个标头字段仅支持一个正则表达式，因为正则表达式模式无法合并；如果需要更多，请考虑使用[`expression`匹配器](#expression)。对多个不同标头字段的匹配结果将进行“与”运算。

#### 示例：

匹配 Cookie 标头中包含 `login_` 后跟一个十六进制字符串的请求，并使用 `{re.login.1}` 或 `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

可以通过省略名称来简化这一过程，名称将从命名匹配器中推导出来：

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

或者，使用 [CEL 表达式](#expression)：

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

根据请求的 `Host` 标头进行匹配。

由于大多数站点块已在站点地址中指定了主机名，因此该匹配器通常用于使用通配符主机名的站点块（参见[通配符证书模式](/docs/caddyfile/patterns#wildcard-certificates)），但在这些情况下仍需执行针对特定主机名的逻辑处理。

多个 `host` 匹配器将通过“或”运算进行组合。

#### 示例：

匹配一个子域名：

```caddy-d
@sub host sub.example.com
```

将顶层域名与子域名进行匹配：

```caddy-d
@site host example.com www.example.com
```

使用 [CEL 表达式](#expression)定义多个子域名：

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

通过 HTTP 请求的方法（动词）。动词应大写，例如 `POST`。可匹配一种或多种方法。

多个 `method` 多个匹配器将通过“或”运算进行组合。

#### 示例：

匹配 `GET` 方法的请求：

```caddy-d
@get method GET
```

匹配 `PUT` 或 `DELETE` 方法的请求：

```caddy-d
@put-delete method PUT DELETE
```

使用 [CEL 表达式](#expression)匹配只读方法：

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

```caddy-d
not <matcher>
```

或者，要否定多个通过“AND”运算连接的匹配器，请打开一个代码块：

```caddy-d
not {
	<matchers...>
}
```

所附匹配器的结果将被否定。

#### 示例：

匹配路径不以 `/css/` 或 `/js/` 开头的请求。

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

匹配不包含以下内容的请求：
- 一个 `/api/` 路径前缀，或
- `POST` 请求方法

即：必须不包含以下任何内容才能匹配：

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

匹配不包含以下两项的请求：
- 一个 `/api/` 路径前缀，且
- `POST` 请求方法

即必须不包含以上两项中的任一项，或两项都包含的情况：

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

此匹配器没有 [CEL 表达式](#expression)，因为您可以使用 `!` 运算符来表示否定。例如：

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

这与以下使用圆括号的写法相同：

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

按请求路径（请求 URI 的路径部分）。路径匹配默认是精确匹配，但 `*` 可用于前缀、后缀、子字符串和通配匹配：

- 仅在结尾处，用于前缀匹配（`/prefix/*`)
- 仅在开头，用于后缀匹配（`*.suffix`)
- 仅限两端，用于子字符串匹配（`*/contains/*`)
- 仅在中间，用于通配匹配（`/accounts/*/info`)

斜杠具有特殊含义。例如， `/foo*` 将匹配 `/foo`, `/foobar`, `/foo/`，以及 `/foo/bar`，但 `/foo/*` 却不会匹配 `/foo` 或 `/foobar`.

在进行匹配之前，会清理请求路径以处理目录遍历中的点号。此外，除非匹配模式中包含多个斜杠，否则多个斜杠会被合并。换句话说， `/foo` 将匹配 `/foo` 和 `//foo`，但 `//foo` 仅匹配 `//foo`.

由于任何给定的 URI 都可能存在多种转义形式，因此请求路径会被规范化（即进行 URL 解码并取消转义），但位于匹配模式中也包含转义序列的位置除外。例如， `/foo/bar` 既匹配 `/foo/bar` 和 `/foo%2Fbar`，但 `/foo%2Fbar` 仅匹配 `/foo%2Fbar`，因为配置中已显式指定了该转义序列。

特殊通配符转义符 `%*` 也可用于替代 `*` ，以使匹配的范围保持未匹配状态。例如， `/bands/*/*` 不会匹配 `/bands/AC%2FDC/T.N.T` ，因为路径将在规范化空间中进行比较，此时它看起来像 `/bands/AC/DC/T.N.T`，这与模式不匹配；然而， `/bands/%*/*` 将匹配 `/bands/AC%2FDC/T.N.T` ，因为由 `%*` 所表示的范围在比较时不会解码转义序列。

多个路径将被进行“或”运算。

#### 示例：

匹配多个目录及其内容：

```caddy-d
@assets path /js/* /css/* /images/*
```

匹配特定文件：

```caddy-d
@favicon path /favicon.ico
```

匹配文件扩展名：

```caddy-d
@extensions path *.js *.css
```

使用 [CEL 表达式](#expression)：

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

与 [`path`](#path) 类似，但支持正则表达式。对经过 URI 解码且未转义的路径进行处理。

所使用的正则表达式语言是 RE2，该语言已包含在 Go 语言中。请参阅 [RE2 语法参考](https://github.com/google/re2/wiki/Syntax)和 [Go 正则表达式语法概述](https://pkg.go.dev/regexp/syntax)。

从 v2.8.0 版本开始，如果 `name` 未提供，则名称将取自命名匹配器的名称。例如，命名匹配器 `@foo` 将导致该匹配器被命名为 `foo`。指定名称的主要优势在于，当多个正则表达式匹配器（例如 `path_regexp` 和[`header_regexp`](#header-regexp)）时，指定名称能带来显著优势。

匹配完成后，可通过指令中的[占位符](/docs/caddyfile/concepts#placeholders)访问捕获组：
- `{re.<name>.<capture_group>}` 其中：
  - `<name>` 是正则表达式的名称，
  - `<capture_group>` 是表达式中捕获组的名称或编号。

- `{re.<capture_group>}` 未命名的占位符也会被填充，以便于使用。需要注意的是，如果依次使用了多个正则表达式匹配器，则占位符的值会被下一个匹配器覆盖。

捕获组 `0` 是完整的正则表达式匹配， `1` 是第一个捕获组， `2` 是第二个捕获组，以此类推。因此 `{re.foo.1}` 或 `{re.1}` 都将包含第一个捕获组的值。

每个命名匹配器只能有一个 `path_regexp` ，因为该匹配器无法与自身合并；若需更多模式，请考虑使用[`expression`匹配器](#expression)。

#### 示例：

匹配路径以 6 个字符的十六进制字符串结尾，后跟 `.css` 或 `.js` 作为文件扩展名的路径，并使用捕获组（用 `( )`) 进行匹配，这些捕获组可通过 `{re.static.1}` 和 `{re.static.2}` (或 `{re.1}` 和 `{re.2}`) 分别访问：

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

可以通过省略名称来简化这一过程，名称将从命名匹配器中推导出来：

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

或者，使用 [CEL 表达式](#expression)，同时验证[`file`](#file)是否存在于磁盘上：

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

按协议匹配请求。例如，一个宽泛的协议名称如 `http`、`https` 或 `grpc`；或者使用具体的或最低的 HTTP 版本，例如 `http/1.1` 或 `http/2+`。

每个命名匹配器只能有一个 `protocol` 匹配器。

#### 示例：

使用 HTTP/2 处理请求：

```caddy-d
@http2 protocol http/2+
```

使用 [CEL 表达式](#expression)：

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

通过查询字符串参数。应为 `key=value` 键值对序列，或空字符串 `""`。键的匹配要求完全一致（区分大小写），但也支持 `*` 匹配任意值。值可以使用占位符。空字符串匹配不包含查询参数的 HTTP 请求。

每个命名匹配器可以包含多个 `query` 匹配器，具有相同键的配对将进行“或”运算，而具有不同键的配对将进行“与”运算。因此，匹配器中的所有键都必须至少有一个匹配的值。

非法的查询字符串（语法错误、未转义的分号等）将无法解析，因此无法匹配。

**注意：** 查询字符串参数是数组，而非单个值。这是因为查询字符串中允许出现重复的键，且每个键可能对应不同的值。如果查询字符串中包含该键的任何一个配置值，此匹配器都会匹配该键。使用查询字符串的后端应用程序必须考虑到，查询字符串的值是数组，且可能包含多个值。

#### 示例：

将 `q` 查询参数与任意值：

```caddy-d
@search query q=*
```

匹配一个 `sort` 查询参数与值 `asc` 或 `desc`:

```caddy-d
@sorted query sort=asc sort=desc
```

同时满足两项条件 `q` 和 `sort`，使用 [CEL 表达式](#expression)：

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

按远程 IP 地址（即直接对等方的 IP 地址或通过 [PROXY 协议](/docs/caddyfile/options#proxy-protocol)设置的地址）。支持精确的 IP 地址或 CIDR 范围。支持 IPv6 区域。

作为一种简便方法， `private_ranges` 可用于匹配所有私有 IPv4 和 IPv6 地址范围。这相当于指定以下所有范围： `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

如果你希望匹配从 HTTP 头部解析出的客户端“真实 IP”，请改用 [`client_ip`](#client-ip) 匹配器。

每个命名匹配器可以包含多个 `remote_ip` ，且它们的范围将被合并并进行“或”运算。

#### 示例：

匹配来自私有IPv4地址的请求：

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

该匹配器通常与[`not`](#not)匹配器配合使用，以实现匹配结果的反转。例如，要阻止来自所有公共 IPv4 和 IPv6 地址的连接（这与所有私有地址范围的匹配结果相反）：

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

在 [CEL 表达式](#expression)中，它看起来像这样：

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

根据请求上下文中变量的值，或占位符的值。可以指定多个值，以匹配这些可能值中的任意一个（按“或”逻辑运算）。

**&lt;variable&gt;** 参数可以是变量名，也可以是花括号中的占位符 `{ }`。（第一个参数中的占位符不会被展开。）

当与用于设置输出的[`map`指令](/docs/caddyfile/directives/map)、路由中的[`vars`指令](/docs/caddyfile/directives/vars)，或是在请求上下文中设置某些信息的插件配合使用时，该匹配器最为实用。

#### 示例：

匹配名为 `magic_number` 的值 `3` 或 `5`:

```caddy-d
vars {magic_number} 3 5
```

匹配任意占位符的值（即经过身份验证的用户的 ID），具体方式如下： `Bob` 或 `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

这是一个完整的示例，演示了如何使用[`vars`指令](/docs/caddyfile/directives/vars)设置变量，然后使用[`vars`匹配器](#vars)对其进行匹配。在此，我们将两个请求头合并为一个变量，并基于该变量进行匹配：

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

在 [CEL 表达式](#expression)中，它将如下所示：

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

与 [`vars`](#vars) 类似，但支持正则表达式。

所使用的正则表达式语言是 RE2，该语言已包含在 Go 语言中。请参阅 [RE2 语法参考](https://github.com/google/re2/wiki/Syntax)和 [Go 正则表达式语法概述](https://pkg.go.dev/regexp/syntax)。

从 v2.8.0 版本开始，如果 `name` 未提供，则名称将取自命名匹配器的名称。例如，命名匹配器 `@foo` 将导致该匹配器被命名为 `foo`。指定名称的主要优势在于，当多个正则表达式匹配器（例如 `vars_regexp` 和[`header_regexp`](#header-regexp)）时，指定名称能带来显著优势。

匹配完成后，可通过指令中的[占位符](/docs/caddyfile/concepts#placeholders)访问捕获组：
- `{re.<name>.<capture_group>}` 其中：
  - `<name>` 是正则表达式的名称，
  - `<capture_group>` 是表达式中捕获组的名称或编号。

- `{re.<capture_group>}` （未命名）也会被填充，以便于使用。需要注意的是，如果依次使用了多个正则表达式匹配器，则占位符的值会被下一个匹配器覆盖。

捕获组 `0` 是完整的正则表达式匹配， `1` 是第一个捕获组， `2` 是第二个捕获组，以此类推。因此 `{re.foo.1}` 或 `{re.1}` 都将包含第一个捕获组的值。

每个变量名仅支持一个正则表达式，因为正则表达式模式无法合并；如果需要更多，请考虑使用[`expression`匹配器](#expression)。对多个不同变量的匹配结果将进行“与”运算。

#### 示例：

匹配名为 `magic_number` 的变量，其值以 `4` 开头，并将该值捕获到一个捕获组中，可通过 `{re.magic.1}` 或 `{re.1}` 访问：

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

可以通过省略名称来简化这一过程，因为名称将从命名匹配器中推导出来：

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

在 [CEL 表达式](#expression)中，它看起来像这样：

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
