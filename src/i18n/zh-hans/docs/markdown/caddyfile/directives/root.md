---
title: "root（Caddyfile 指令）"
---

# root

设置站点的根路径，该路径被多个访问文件系统的 matcher 和指令使用。若未设置，默认站点根为当前工作目录。

更具体地说，该指令会设置 `{http.vars.root}` 占位符。它与同块内其他 `root` 指令互斥，因此即使使用有交集的匹配器定义多个 root，也不会级联覆盖。

该指令不会自动开启静态文件服务，因此常与 [`file_server` 指令](file_server) 或 [`php_fastcgi` 指令](php_fastcgi)配合使用。

## 语法

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** 是要作为站点根的路径。

在 v2.8.0 之前，如果 `<path>` 以 `/` 开头，解析器可能会将其误认为 [匹配器 token](/docs/caddyfile/matchers#syntax)，因此当时需要显式写上通配符匹配器 token（`*`）。

## 示例

将站点根设置为 `/home/bob/public_html`（假设 Caddy 以 `bob` 用户运行）：

<aside class="tip">

如果你以 systemd 服务方式运行 Caddy，直接从 `/home` 读取文件不可行，因为 `caddy` 用户在 `/home` 目录没有“可执行”权限（用于目录遍历时必需）。建议将文件放在 `/srv` 或 `/var/www/html`。

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

注意，在 v2.8.0 之前，这里需要使用 [通配符匹配器](/docs/caddyfile/matchers#wildcard-matchers)，因为第一个参数与 [路径匹配器](/docs/caddyfile/matchers#path-matchers)存在歧义，例如 `root * /srv`，现在可简化为 `root /srv`。

</aside>


将站点根设置为 `public_html`（相对于当前工作目录）以处理所有请求：

```caddy-d
root public_html
```

仅对 `/foo/*` 下的请求更改站点根：

```caddy-d
root /foo/* /home/user/public_html/foo
```

`root` 指令通常与 [`file_server`](file_server) 配合提供静态文件服务，或与 [`php_fastcgi`](php_fastcgi) 配合提供 PHP 站点：

```caddy
example.com {
	root /srv
	file_server
}
```
