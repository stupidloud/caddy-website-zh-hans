---
title: handle (Caddyfile 指令)
---

<a id="handle"></a>
# handle

在同一層級的巢狀結構中，以互斥的方式評估一組指令，使其與其他 `handle` 區塊區分開來。

換句話說，當多個 `handle` 指令按順序出現時，只有第一個 *匹配* 的 `handle` 區塊會被評估。沒有 matcher 的 handle 作用類似於 *回退* (fallback) 路由。

`handle` 指令會根據其 matcher 按照 [指令排序演算法](/docs/caddyfile/directives#sorting-algorithm) 進行排序。[`handle_path`](handle_path) 指令是一個特殊情況，其排序優先級與具有路徑 matcher 的 `handle` 相同。

如果需要，handle 區塊可以巢狀使用。只有 HTTP handler 指令可以在 handle 區塊內使用。

<a id="syntax"></a>
## Syntax

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** 是一組 HTTP handler 指令或指令區塊的列表，每行一個，就像在 handle 區塊之外使用一樣。



<a id="similar-directives"></a>
## Similar directives

還有其他可以包裝 HTTP handler 指令的指令，但每種指令都有其特定的用途，取決於你想要傳達的行為：

- [`handle_path`](handle_path) 的作用與 `handle` 相同，但在執行其 handler 之前會從請求中移除前綴。

- [`handle_errors`](handle_errors) 與 `handle` 類似，但僅在 Caddy 在處理請求期間遇到錯誤時才被呼叫。

- [`route`](route) 像 `handle` 一樣包裝其他指令，但有兩個區別：
  1. route 區塊之間不是互斥的，
  2. route 內的指令不會 [重新排序](/docs/caddyfile/directives#directive-order)，如果需要，這可以讓你擁有更多控制權。



<a id="examples"></a>
## Examples

使用靜態檔案伺服器處理 `/foo/` 的請求，並使用 reverse proxy 處理其他請求：

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

你可以在同一個站點中混合使用 `handle` 和 [`handle_path`](handle_path)，它們仍然會彼此互斥：

```caddy
example.com {
	handle_path /foo/* {
		# "/foo" 前綴已被移除
	}

	handle /bar/* {
		# 路徑仍然保留 "/bar"
	}
}
```

你可以巢狀使用 `handle` 區塊來建立更複雜的路由邏輯：

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# 此區塊僅匹配 /foo/bar 下的路徑
		}

		handle {
			# 此區塊匹配 /foo/ 下的所有其他請求
		}
	}

	handle {
		# 此區塊匹配所有其他請求（作為回退）
	}
}
```
