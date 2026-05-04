---
title: "root（Caddyfile 指令）"
---

# root

设置站点的根路径，供访问文件系统的各种匹配器和指令使用。如果未设置，则默认站点根目录为当前工作目录。

具体来说，此指令设置了 `{http.vars.root}` 占位符。它与其他 `root` 指令互斥，因此可以安全地定义多个匹配条件存在交集的根路径：它们不会级联并相互覆盖。

该指令不会自动启用静态文件的提供，因此通常与[`file_server`指令](file_server)或[`php_fastcgi`指令](php_fastcgi)配合使用。


## 语法

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** 是网站根目录的路径。

在 v2.8.0 之前， `<path>` 参数若以 `/`，因此必须指定一个通配符匹配器标记（`*`).


## 示例

将网站根目录设置为 `/home/bob/public_html` （假设 Caddy 是以该用户身份运行的） `bob`):

<aside class="tip">

如果您将 Caddy 作为 systemd 服务运行，从 `/home` 将无法正常工作，因为 `caddy` 用户对 `/home` （这是目录遍历所必需的）。建议您将文件放置在 `/srv` 或 `/var/www/html` 目录中。

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

请注意，在 v2.8.0 之前，此处必须使用[通配符匹配器](/docs/caddyfile/matchers#wildcard-matchers)，因为第一个参数与[路径匹配器](/docs/caddyfile/matchers#path-matchers)存在歧义，即 `root * /srv`，但现在可以简化为 `root /srv`.

</aside>


将网站根目录设置为 `public_html` （相对于当前工作目录）作为所有请求的站点根目录：

```caddy-d
root public_html
```

仅对以下请求更改网站根目录： `/foo/*`:

```caddy-d
root /foo/* /home/user/public_html/foo
```

该 `root` 指令通常与[`file_server`](file_server)配合使用以提供静态文件，或与[`php_fastcgi`](php_fastcgi)配合使用以提供PHP网站：

```caddy
example.com {
	root /srv
	file_server
}
```
