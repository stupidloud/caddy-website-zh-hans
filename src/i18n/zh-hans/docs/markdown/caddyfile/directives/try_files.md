---
title: "try_files（Caddyfile 指令）"
---

# try_files

将请求 URI 路径重写为列表中位于网站根目录下的首个存在文件。如果没有匹配的文件，则不进行重写。


<span id="syntax"/>
## 语法

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** 是要尝试的文件列表。URI 路径将被重写为其中第一个存在的文件。

  要匹配目录，请在路径末尾添加一个正斜杠 `/` 。所有文件路径均相对于网站[根目录](root)，且[通配符模式](https://pkg.go.dev/path/filepath#Match)将被展开。

  每个参数还可以包含一个查询字符串，如果该查询字符串与特定文件匹配，则该查询字符串也会随之更改。

  如果 `try_policy` 是 `first_exist` （默认情况），则列表中的最后一项可以是一个以 `=` （例如 `=404`)，作为备选方案，系统将抛出该代码对应的错误；该错误可通过[`handle_errors`](handle_errors)进行捕获和处理。

- **策略**是指从文件列表中选择文件的规则。

  默认： `first_exist`



<span id="expanded-form"/>
## 展开形式

该 `try_files` 该指令基本上是以下内容的快捷方式：

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

请注意，此指令不支持匹配器标记。如果您需要更复杂的匹配逻辑，请以上文的扩展形式为基础进行实现。

更多详情请参阅 [`file` 匹配器](/docs/caddyfile/matchers#file)。



<span id="examples"/>
## 示例

如果请求与任何静态文件都不匹配，请重写到您的 PHP 索引/路由入口点：

```caddy-d
try_files {path} /index.php
```

同上，但需在查询字符串中添加原始路径（某些旧版 PHP 应用程序有此要求）：

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

同上，但也要匹配目录：

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

如果文件或目录已存在，则尝试重写；否则返回 404 错误（可通过 [`handle_errors`](handle_errors) 捕获并处理）：

```caddy-d
try_files {path} {path}/ =404
```

选择静态文件的最新部署版本（例如，提供 `index.be331df.html` 当 `index.html` 时）：

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
