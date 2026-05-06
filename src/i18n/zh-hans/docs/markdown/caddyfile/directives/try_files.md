---
title: "try_files（Caddyfile 指令）"
---

# try_files

将请求 URI 路径重写为站点根中第一个存在的文件路径。如果没有匹配到文件，则不执行重写。

## 语法

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **&lt;files...&gt;** 是要尝试查找的文件列表。URI 路径将被重写到列表中第一个存在的文件。

  若要匹配目录，请在路径末尾追加斜杠 `/`。所有文件路径都相对于站点 [root](root)，且会展开[glob 模式](https://pkg.go.dev/path/filepath#Match)。

  每个参数也可以包含查询字符串；若匹配到该文件，则对应查询字符串也会被改写。

  如果 `try_policy` 是 `first_exist`（默认值），列表最后一项可写作带 `=` 的数字（例如 `=404`），作为兜底时返回该错误码；该错误可由 [`handle_errors`](handle_errors) 捕获和处理。

- **policy** 是从文件列表中选择文件的策略。默认值：`first_exist`


## 扩展写法

`try_files` 指令本质上是以下写法的快捷方式：

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

注意该指令不接受 matcher token。如果需要更复杂的匹配逻辑，可基于上述扩展写法继续实现。

更多细节见 [`file` matcher](/docs/caddyfile/matchers#file)。

## 示例

如果请求不匹配任何静态文件，则重写到 PHP 入口：

```caddy-d
try_files {path} /index.php
```

同上，但将原始路径也追加到查询字符串（某些旧版 PHP 应用需要）：

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

同上，并额外匹配目录：

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

尝试重写到存在的文件或目录；若都不存在则返回 404（可被 [`handle_errors`](handle_errors) 捕获处理）：

```caddy-d
try_files {path} {path}/ =404
```

选择静态文件的最新版本（例如请求 `index.html` 时，返回 `index.be331df.html`）：

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
