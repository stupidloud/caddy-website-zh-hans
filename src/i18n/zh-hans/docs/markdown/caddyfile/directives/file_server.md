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

# file_server

一个支持真实文件系统和虚拟文件系统的静态文件服务器。它通过将请求的 URI 路径追加到[站点根路径](root)来构造文件路径。

默认情况下，它会强制标准化 URI；也就是说，对目录请求会发起重定向以补齐末尾斜杠，对带有末尾斜杠的文件请求会重定向去掉该斜杠。但如果内部重写修改了路径的最后一个元素（文件名），则不再触发这些重定向。

`file_server` 指令通常与 [`root`](root) 指令配合使用，用于为整个站点设置文件根目录。本指令也有一个 `root` 子指令（见下文），仅对该处理器生效（不推荐）。需要注意，站点根目录并不提供沙箱级别的安全保障：文件服务器会阻止路径组件中的目录穿越，但根目录内的符号链接仍可能允许访问根目录外的路径。

当出现错误（例如 404 文件未找到、403 权限不足）时，将触发错误路由。使用 [`handle_errors`](handle_errors) 指令可定义错误路由，并展示自定义错误页。

当使用 `browse` 时，默认输出由 HTML 模板生成。客户端可通过请求头 `Accept: application/json` 或 `Accept: text/plain` 分别以 JSON 或纯文本获取目录列表。JSON 输出适合脚本处理，纯文本输出更适合在终端人工查看。

## Syntax

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

- **fs** <span id="fs"/> 指定要使用的替代（可能是虚拟）文件系统。此处可使用 `caddy.fs` 命名空间中的任意 Caddy 模块。根路径/前缀仍会应用到替代文件系统模块。默认使用本地磁盘。

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 引入了 [`--embed` 标志](https://github.com/caddyserver/xcaddy#custom-builds)，用于将文件系统树内嵌到自定义 Caddy 构建中，并注册了名为 `embedded` 的 `fs` 模块，使你的静态站点可以作为 Caddy 可执行文件分发。

- **root** <span id="root"/> 设置站点根路径。它与 [`root`](root) 指令类似，但只作用于该 file_server 实例，并会覆盖可能已定义的其他站点根。默认值：`{http.vars.root}` 或当前工作目录。注意：该子指令仅修改此处理器的根路径。若要让其他指令（如 [`try_files`](try_files) 或 [`templates`](templates)）共享同一站点根，请改用 [`root`](root) 指令。

- **hide** <span id="hide"/> 是一组要隐藏的文件或文件夹；在请求这些路径时，文件服务器会伪装成它们不存在。支持占位符和 glob 模式。注意这里使用的是*文件系统路径*，不是请求路径。也就是说，未带路径分隔符的相对路径以当前工作目录为基准，而不是站点根；并且在比较前会先将路径转换为绝对路径（若可转换）。提供仅包含文件名或模式时，会隐藏所有同名文件；否则会先尝试路径前缀匹配，再尝试 glob 匹配。由于这是 Caddyfile 配置，默认会把活动配置文件路径也加入隐藏项。隐藏比较是区分大小写的；在大小写不敏感的文件系统上，不同大小写的请求路径可能仍映射到同一实际路径，因此 `hide` 不应被当作敏感路径的安全边界。

- **index** <span id="index"/> 是要查找为索引文件的文件名列表。默认值：`index.html index.txt`

- **browse** <span id="browse"/> 为没有索引文件的目录请求启用目录列表。

  - **<template_file>** <span id="template_file"/> 可选的自定义模板文件，用于目录列表。默认模板可通过 `caddy file-server export-template` 命令导出，该命令会将默认模板输出到标准输出。你也可以在源码中找到嵌入模板 [（GitHub 源码） ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html)。目录列表模板也可使用[标准模板模块](/docs/modules/http.handlers.templates#docs)的动作。

  - **reveal_symlinks** <span id="reveal_symlinks"/> 在目录列表中展示符号链接目标。默认情况下，默认隐藏符号链接目标，仅显示链接文件本身。

  - **sort** <span id="sort"/> 修改目录列表的默认排序。第一个参数为排序字段/列：`name`、`namedirfirst`、`size` 或 `time`。可选的第二参数是方向：`asc` 或 `desc`。例如 `sort name desc` 按名称降序排列。

  - **file_limit** <span id="file_limit"/> 设置目录列表中显示文件的最大数量。默认值：`10000`。当文件数量超过该限制时，只显示前 N 个文件（N 为指定值）。

- **precompressed** <span id="precompressed"/> 是用于查找预压缩 sidecar 文件的编码格式列表。参数是要查找的编码格式有序列表，支持 `gzip`（`.gz`）、`zstd`（`.zst`）和 `br`（`.br`）。如果未指定格式，默认顺序是 `br zstd gzip`。

  所有文件查找会先尝试未压缩文件。一旦找到，Caddy 再按启用格式顺序查找对应的 sidecar 文件。若找到预压缩 sidecar 文件，Caddy 会返回该文件，并设置适当的 `Content-Encoding` 响应头。否则仍按常规返回未压缩文件。如果启用了 [`encode`](encode) 指令，则在没有预压缩文件时可能按需进行压缩。

- **status** <span id="status"/> 是写响应时可选的状态码覆盖值。对返回[自定义错误页](handle_errors)很有帮助。可用 3 位状态码，例如：`404`。支持占位符。默认返回的状态码通常是 `200`，或在返回部分内容时是 `206`。

- **disable_canonical_uris** <span id="disable_canonical_uris"/> 禁用默认的标准化重定向行为（当请求路径为目录但未带末尾斜杠时补齐；当请求路径为文件但带末尾斜杠时移除）。默认情况下，如果请求路径的最后一个元素（文件名）已经经过内部重写，为避免隐式行为覆盖显式重写，也不会执行标准化。

- **pass_thru** <span id="pass_thru"/> 启用 pass-thru 模式：如果请求的文件不存在，则继续执行路由中的下一个 HTTP 处理器，而不是触发 `404` 错误（调用 [`handle_errors`](handle_errors) 路由）。实际上，这通常只在包含 `file_server` 的 [`route`](route) 块中、并且后面还有其他处理器时才有意义，因为该指令的执行顺序等效于[最后处理](/docs/caddyfile/directives#directive-order)。


## Examples

从当前目录提供静态文件：

```caddy-d
file_server
```

开启目录列表：

```caddy-d
file_server browse
```

仅在 `/static` 目录下提供静态文件：

```caddy-d
file_server /static/*
```

`file_server` 通常与 [`root`](root) 指令一起使用，设置文件服务的根路径：

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

如果你将 Caddy 作为 systemd 服务运行，直接从 `/home` 读取文件会失败，因为 `caddy` 用户在 `/home` 目录没有“可执行”权限（这是遍历目录所必需的）。建议改为放在 `/srv` 或 `/var/www/html`。

</aside>


隐藏所有 `.git` 文件夹及其内容：

```caddy-d
file_server {
	hide .git
}
```

若客户端支持（`Accept-Encoding` 头）则会检测请求文件旁边的预压缩文件。例如请求 `/path/to/file` 时，会按顺序检查 `/path/to/file.br`、`/path/to/file.zst` 和 `/path/to/file.gz`，并返回第一个可用文件及其对应的 `Content-Encoding`：

```caddy-d
file_server {
	precompressed
}
```
