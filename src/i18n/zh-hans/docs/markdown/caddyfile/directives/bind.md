---
title: "bind（Caddyfile 指令）"
---

# bind

覆盖服务器套接字应绑定的接口。

通常情况下，监听器会绑定到空接口（通配符接口）。不过，您可以强制监听器绑定到其他主机名或 IP 地址。该指令仅接受主机名，不接受端口号。端口号由[站点地址](/docs/caddyfile/concepts#addresses)决定（默认值为 `443`).

请注意，如果绑定位置不一致，可能会导致意想不到的后果。例如，如果同一端口上的两个位置解析为 `127.0.0.1` ，且其中仅有一个站点配置了 `bind 127.0.0.1`，则仅有一个站点可访问，因为另一个站点将绑定到该端口但未指定具体主机；操作系统会选择匹配度更高的套接字。（虚拟主机不会在不同的监听器之间共享。）

`bind` 接受[网络地址](/docs/conventions#network-addresses)，但不能包含端口号。


## 语法

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** 是用于指定监听器应绑定的主机接口列表。 


## 示例

若要使套接字仅在当前机器上可用，请将其绑定到回环接口（localhost）：

```caddy
example.com {
	bind 127.0.0.1
}
```

要包含 IPv6：

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

绑定到 `10.0.0.1:8080`:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

要绑定到位于 `/run/caddy`:

```caddy
example.com {
	bind unix//run/caddy
}
```

要将文件权限更改为所有用户均可写入（[默认](/docs/conventions#network-addresses)权限为 `0200`，即仅所有者可写）：

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

要将一个域名绑定到两个不同的接口，并设置不同的响应：

```caddy
example.com {
	bind 10.0.0.1
	respond "One"
}

example.com {
	bind 10.0.0.2
	respond "Two"
}
```
