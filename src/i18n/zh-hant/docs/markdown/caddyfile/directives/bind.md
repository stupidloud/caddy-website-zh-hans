---
title: bind (Caddyfile 指令)
---

<a id="bind"></a>
# bind

覆蓋伺服器通訊端 (socket) 應該綁定的介面。

通常情況下，接聽程式會綁定到空（通配符）介面。但是，你可以強制接聽程式綁定到另一個主機名或 IP。此指令僅接受主機，不接受連接埠。連接埠由 [站點位址](/docs/caddyfile/concepts#addresses)（預設為 `443`）決定。

請注意，不一致地綁定站點可能會導致意想不到的後果。例如，如果同一連接埠上的兩個站點都解析為 `127.0.0.1`，並且其中只有一個站點配置了 `bind 127.0.0.1`，則只有一個站點可以訪問，因為另一個站點將綁定到沒有特定主機的連接埠；作業系統將選擇更具體的匹配通訊端。（虛擬主機不會在不同的接聽程式之間共享。）

`bind` 接受 [網路位址](/docs/conventions#network-addresses)，但不得包含連接埠。


<a id="syntax"></a>
## Syntax

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** 是要綁定接聽程式的主機介面列表。


<a id="examples"></a>
## Examples

要使通訊端僅在當前機器上可訪問，請綁定到迴環介面 (localhost)：

```caddy
example.com {
	bind 127.0.0.1
}
```

包含 IPv6：

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

綁定到 `10.0.0.1:8080`：

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

綁定到位於 `/run/caddy` 的 Unix 網域通訊端：

```caddy
example.com {
	bind unix//run/caddy
}
```

更改檔案權限為所有使用者可寫入（[預設值](/docs/conventions#network-addresses) 為 `0200`，僅擁有者可寫入）：

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

將一個網域綁定到兩個不同的介面，並提供不同的回應：

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
