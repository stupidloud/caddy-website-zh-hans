---
title: "header（Caddyfile 指令）"
---

# 标头

用于操作 HTTP 响应头字段。它可以设置、添加和删除头字段值，或使用正则表达式进行替换。

默认情况下，头部操作会立即执行，除非正在删除任何头部（`-` prefix）或设置默认值（`?` prefix）。在这些情况下，标头操作会自动延迟，直到需要将其写入客户端时才执行。

要操作 HTTP 请求头，您可以使用 [`request_header`](request_header) 指令。


## 语法

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# Add
	+<field> <value>

	# Set
	<field> <value>

	# Set with defer
	><field> <value>

	# Delete
	-<field>

	# Replace
	<field> <find> <replace>

	# Replace with defer
	><field> <find> <replace>

	# Default
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** 是该标头字段的名称。

  如果没有前缀，则设置（覆盖）该字段。

  在字段前添加前缀 `+` 前缀，以添加该字段，而非覆盖（设置）已存在的字段；响应中可以出现多个该字段。

  在字段名前添加 `-` 前缀来删除该字段。该字段可使用前缀或后缀 `*` 通配符来删除所有匹配的字段。

  在字段名前添加 `?` 来为该字段设置默认值。只有当该字段尚未存在时，才会将其写入。

  在 `>` 来设置该字段，并启用 `defer`作为快捷键。

- **&lt;value&gt;** 是添加或设置字段时的标头字段值。

- **&lt;find&gt;** 是用于搜索的正则表达式。搜索模式中可以使用占位符来表示动态输入。所使用的正则表达式语言是 RE2，Go 语言中已包含该语言。请参阅 [RE2 语法参考](https://github.com/google/re2/wiki/Syntax)和 [Go 正则表达式语法概述](https://pkg.go.dev/regexp/syntax)。

- **&lt;replace&gt;** 是替换内容；若进行查找和替换操作，此项为必填。使用 `$1` 或 `$2` 等符号引用搜索模式中的捕获组。如果替换值为 `""`，则匹配的文本将从该值中移除。详情请参阅 [Go 文档](https://golang.org/pkg/regexp/#Regexp.Expand)。

- **defer** 会将标头操作的执行推迟到响应发送给客户端时。在以下情况下，此选项会自动启用：
	- 当使用 `-`.
	- 使用 `?`.
	- 在对集合执行添加或替换操作时，使用 `>` 前缀进行集合或替换操作时。
	- 当存在一个或多个 `match` 条件存在时。

- **match** <span id="match"/> 是一个内联[响应匹配器](/docs/caddyfile/response-matchers)。仅对满足指定条件的响应应用标头操作。

对于多个标头的操作，您可以打开一个代码块，并以同样的方式在每行中指定一项操作。

使用 `?` 前缀来设置默认标头值时，系统会自动将其拆分为独立的 `header` 处理程序中， `header` 块中且包含多个头操作时，该值会自动拆分为独立的处理程序。[在底层实现中](/docs/modules/http.handlers.headers#response/require)，使用 `?` 会配置一个[响应匹配器](/docs/caddyfile/response-matchers)，该匹配器适用于指令的整个处理程序，该处理程序仅执行标头操作（如 `defer`），但仅当该字段尚未设置时才生效。


## 示例

在所有响应中设置自定义标头字段：

```caddy-d
header Custom-Header "My value"
```

移除“Hidden”标头字段：

```caddy-d
header -Hidden
```

替换 `http://` 替换为 `https://` 在任何 Location 标头中：

```caddy-d
header Location http:// https://
```

在所有页面上设置安全和隐私标头：(**警告：** 仅在您了解其影响的情况下使用！)

```caddy-d
header {
	# disable FLoC tracking
	Permissions-Policy interest-cohort=()

	# enable HSTS
	Strict-Transport-Security max-age=31536000;

	# disable clients from sniffing the media type
	X-Content-Type-Options nosniff

	# clickjacking protection
	X-Frame-Options DENY
}
```

以下是若干旨在相互排斥的头文件指令：

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

如果上游未定义缓存过期时间，则设置默认缓存过期时间：

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

将所有对 GET 请求的成功响应标记为可缓存，缓存时长最长为一小时：

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

在上游服务器发生异常时，防止缓存错误响应：

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

如果上游服务器支持客户端提示，请将浅色模式的响应标记为可与深色模式的响应分开缓存：
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

通过将通配符值替换为特定域名，防止 CORS 标头过于宽松：
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**注意**：在替换操作中， `<find>` 值将被解释为正则表达式。若要匹配 `*` 字符，必须像上例所示那样用反斜杠进行转义。

或者，您可以使用[响应匹配器](/docs/caddyfile/response-matchers)来精确匹配头部值：
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

覆盖代理上游为以 `/no-cache`；启用 `defer` ，以确保该标头是在代理写入其标头之后才设置的：

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

要对 `Set-Cookie` 标头以添加 `SameSite=None`；使用正则表达式捕获来获取现有值，并 `$1` 将其重新插入开头，并在后面附加额外选项：

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
