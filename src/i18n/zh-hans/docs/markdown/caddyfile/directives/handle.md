---
title: "handle（Caddyfile 指令）"
---

# handle

在同一层级内，彼此互斥地评估一组指令块。

换言之，当多个 `handle` 指令连续出现时，只有第一个**匹配**的 `handle` 块会被执行。没有匹配器的 handle 相当于一个*回退*路由。

`handle` 指令会按[指令排序算法](/docs/caddyfile/directives#sorting-algorithm)依据匹配器排序。[`handle_path`](handle_path) 是一个特殊情况：它的排序优先级与带 path 匹配器的 `handle` 相同。

需要时可以嵌套 `handle` 块。`handle` 块内只能使用 HTTP 处理器指令。

<a id="syntax"></a>
## 语法

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **&lt;directives...&gt;** 是一组 HTTP 处理器指令或指令块，每行一项，与在 `handle` 块外的写法相同。


<a id="similar-directives"></a>
## 类似指令

还有其他指令也能包裹 HTTP 处理器指令，但每个指令适用于的行为表达不同：

- [`handle_path`](handle_path) 与 `handle` 的行为相同，但在运行其处理器前会先去掉请求前缀。

- [`handle_errors`](handle_errors) 与 `handle` 相似，但只在 Caddy 处理请求时遇到错误时被调用。

- [`route`](route) 与 `handle` 一样用于包裹其他指令，但有两点差异：
  1. `route` 块之间不互斥
  2. `route` 内的指令不进行[重排](/docs/caddyfile/directives#directive-order)，当有需求时可提供更多控制权


<a id="examples"></a>
## 示例

在 `/foo/` 下用静态文件服务器处理请求，其它请求则交给反向代理：

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

你可以在同一个站点同时混用 `handle` 和 [`handle_path`](handle_path)，它们之间仍会互斥：

```caddy
example.com {
	handle_path /foo/* {
		# 该路径会先去掉 "/foo" 前缀
	}

	handle /bar/* {
		# 该路径仍保留 "/bar"
	}
}
```

你可以嵌套 `handle` 块以构建更复杂的路由逻辑：

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# 该块仅匹配 /foo/bar 下的路径
		}

		handle {
			# 该块匹配 /foo/ 下的其他所有路径
		}
	}

	handle {
		# 该块匹配所有其他路径（作为回退）
	}
}
```
