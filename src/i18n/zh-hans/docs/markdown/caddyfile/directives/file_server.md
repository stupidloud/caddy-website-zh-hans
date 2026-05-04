---
title: "file_server（Caddyfile 指令）"
---

<script>
ready(function() {
	// Fix inline browse arg
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# 文件服务器

一个支持真实和虚拟文件系统的静态文件服务器。它通过将请求的 URI 路径附加到[网站的根路径](root)上来构建文件路径。

默认情况下，它会强制执行规范化 URI；这意味着，对于不以尾部斜杠结尾的目录请求（会添加尾部斜杠），或对于以尾部斜杠结尾的文件请求（会移除尾部斜杠），系统将触发 HTTP 重定向。但是，如果内部重写规则修改了路径的最后一个元素（即文件名），则不会触发重定向。

通常情况下，`file_server` 指令会与[`root`](root)指令配合使用，以设置整个站点的文件根目录。该指令还提供了一个 `root` 子指令（见下文），用于仅为该处理程序设置根目录（不建议使用）。请注意，站点根目录并不具备沙箱保障：文件服务器虽会阻止通过路径组件进行目录遍历，但根目录内的符号链接仍可能允许访问根目录之外的内容。

当发生错误时（例如文件未找到 `404`、权限被拒绝 `403`），将调用错误路由。请使用[`handle_errors`](handle_errors)指令来定义错误路由，并显示自定义错误页面。

使用 `browse` 时，默认输出由 HTML 模板生成。客户端可通过使用 `Accept: application/json` 或 `Accept: text/plain` 请求头分别请求目录列表的 JSON 或纯文本格式。JSON 输出适用于脚本编写，而纯文本输出则适用于终端的人工操作。


## 语法

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> 指定要使用的备用（可能是虚拟）文件系统。 `caddy.fs` 命名空间中的任何 Caddy 模块均可在此处使用。任何根路径/前缀仍适用于替代文件系统模块。默认情况下，使用本地磁盘。

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 引入了 [`--embed` 标志](https://github.com/caddyserver/xcaddy#custom-builds)，用于将文件系统树嵌入自定义的 Caddy 构建中，并注册了一个名为 `embedded` 的 `fs` 模块，可让您的静态网站以 Caddy 可执行程序的形式进行分发。

- **root** <span id="root"/> 用于设置网站根目录的路径。它与 [`root`](root) 指令类似，但仅适用于当前文件服务器实例，并会覆盖任何已定义的其他网站根目录。默认值： `{http.vars.root}` 或当前工作目录。注意：此子指令仅更改当前处理程序的根目录。若要使其他指令（如 [`try_files`](try_files) 或 [`templates`](templates)）使用相同的站点根目录，请改用 [`root`](root) 指令。

- **hide** <span id="hide"/> 是一个待隐藏的文件或文件夹列表；如果有请求匹配这些路径，文件服务器会假装它们不存在。支持占位符和通配符模式。请注意，这些是 *文件系统* 路径，而非请求路径。换句话说，相对路径以当前工作目录为基准，而不是站点根目录；并且在比较之前，所有路径都会尽可能转换为绝对路径。若指定文件名或模式时不包含路径分隔符，则会隐藏所有名称匹配的文件，无论其位置如何；否则，会先尝试路径前缀匹配，再进行通配符匹配。由于这是 Caddyfile 配置，当前有效的配置文件会默认加入。隐藏比较区分大小写；在不区分大小写的文件系统上，大小写不同的请求路径仍可能解析为同一磁盘路径，因此 `hide` 不应被视为敏感路径的安全边界。

- **index** <span id="index"/> 是一份用于查找索引文件的文件名列表。默认值： `index.html index.txt`

- **浏览** <span id="browse"/> 可在请求未设置索引文件的目录时显示文件列表。

  - **<template_file>** <span id="template_file"/> 是一个用于目录列表的可选自定义模板文件。默认使用可通过以下命令提取的模板 `caddy file-server export-template`，该命令将默认模板输出到标准输出。该嵌入式模板也可[在此处](/old/resources/images/external-link.svg)查看[源代码 ![外部链接](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html)。浏览模板还可以使用[标准模板模块](/docs/modules/http.handlers.templates#docs)中的操作。

  - **reveal_symlinks** <span id="reveal_symlinks"/> 可启用在目录列表中显示符号链接目标的功能。默认情况下，符号链接的目标会被隐藏，仅显示链接文件本身。

  - **排序** <span id="sort"/> 可更改目录列表的默认排序方式。第一个参数是用于排序的字段/列： `name`, `namedirfirst`, `size`，或 `time`。第二个参数是可选的排序方向： `asc` 或 `desc`。例如， `sort name desc` 将按名称降序排序。

  - **file_limit** <span id="file_limit"/> 用于设置目录列表中显示的文件最大数量。默认值： `10000`。如果文件数量超过此限制，则仅显示前 N 个文件，其中 N 为指定的限制值。

- **precompressed** <span id="precompressed"/> 是用于搜索预压缩 sidecar 文件的编码格式列表。参数是一个按顺序排列的编码格式列表，用于搜索预压缩 [sidecar 文件](https://en.wikipedia.org/wiki/Sidecar_file)。支持的格式包括 `gzip` (`.gz`)、`zstd` (`.zst`) 和 `br` (`.br`)。若省略格式，则默认使用 `br zstd gzip`（按此顺序）。

  所有文件查询都会先检查未压缩文件是否存在。一旦找到，Caddy 就会查找与每个启用格式对应扩展名的 sidecar 文件。如果找到了预压缩的 sidecar 文件，Caddy 就会返回该预压缩文件，并相应设置 `Content-Encoding` 响应头。否则，Caddy 会照常返回未压缩的文件。如果启用了[`encode`指令](encode)，则在未预压缩的情况下，它可能会对响应进行即时压缩。

- **status** <span id="status"/> 是一个可选的状态码覆盖选项，用于在写入响应时使用。在通过[自定义错误页面](handle_errors)响应请求时特别有用。可以是三位数的状态码，例如： `404`。支持使用占位符。默认情况下，生成的状态码通常为 `200`，或 `206` （用于部分内容）。

- **disable_canonical_uris** <span id="disable_canonical_uris"/> 禁用默认的重定向行为（即当请求路径为目录时添加尾部斜杠，或当请求路径为文件时移除尾部斜杠）。 请注意，默认情况下，如果请求路径的最后一个元素（文件名）经过了内部重写，则不会进行规范化处理，以避免隐式行为覆盖显式重写。

- **pass_thru** <span id="pass_thru"/> 启用直通模式，当请求的文件不存在时，系统会继续处理路由中的下一个 HTTP 处理程序，而不是触发 `404` 错误（调用[`handle_errors`](handle_errors)路由）。实际上，此功能仅在[`route`](route)块内，并且在 `file_server` 后面还有其他处理程序指令时才有用，因为该指令实际上被[排在最后](/docs/caddyfile/directives#directive-order)。


## 示例

位于当前目录之外的静态文件服务器：

```caddy-d
file_server
```

启用文件列表后：

```caddy-d
file_server browse
```

仅在 `/static` 文件夹内：

```caddy-d
file_server /static/*
```

该 `file_server` 该指令通常与[`root`指令](root)配合使用，以设置提供文件的根路径：

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

如果您将 Caddy 作为 systemd 服务运行，从 `/home` 将无法正常工作，因为 `caddy` 用户对 `/home` 目录上没有“可执行”权限（这是目录遍历所必需的）。建议您将文件放置在 `/srv` 或 `/var/www/html` 中。

</aside>


隐藏所有 `.git` 文件夹及其内容：

```caddy-d
file_server {
	hide .git
}
```

如果客户端支持（`Accept-Encoding` 标头），则会检查请求文件所在目录下是否存在预压缩文件。因此，如果请求 `/path/to/file`，则会检查 `/path/to/file.br`、`/path/to/file.zst` 和 `/path/to/file.gz`，并按顺序提供首个可用的文件，同时附带相应的 `Content-Encoding`：

```caddy-d
file_server {
	precompressed
}
```
