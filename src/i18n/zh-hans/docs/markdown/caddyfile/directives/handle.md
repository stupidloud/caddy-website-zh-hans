---
title: "handle（Caddyfile 指令）"
---

# 处理

将一组指令与其他指令互斥地进行评估 `handle` 块。

换句话说，当多个 `handle` 指令依次出现时，只有第一个*匹配*的 `handle` 块才会被执行。没有匹配器的句柄会像一个*备用*路由一样工作。

这些 `handle` 指令会根据其匹配器，按照[指令排序算法](/docs/caddyfile/directives#sorting-algorithm)进行排序。[`handle_path`](handle_path)指令是一个特例，其排序优先级与 `handle` 具有路径匹配器的指令。

如果需要，处理块可以嵌套。处理块内部只能使用 HTTP 处理程序指令。

<span id="syntax"/>
## 语法

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** 是一组 HTTP 处理程序指令或指令块，每行一个，其用法与在 handle 块外部使用时相同。



<span id="similar-directives"/>
## 类似指令

还有其他指令可以包裹 HTTP 处理程序指令，但每种指令的用途各不相同，具体取决于您希望实现的行为：

- [`handle_path`](handle_path) 的作用与 `handle`，但它会在运行处理程序之前从请求中移除前缀。

- [`handle_errors`](handle_errors) 类似于 `handle`，但仅在 Caddy 处理请求时遇到错误才会被调用。

- [`route`](route) 与 `handle` ，但有两点区别：
  1. 路由块之间并非互斥，
  2. 路由内的指令不会被[重新排序](/docs/caddyfile/directives#directive-order)，这在需要时能为您提供更大的控制权。



<span id="examples"/>
## 示例

在 `/foo/` 使用静态文件服务器处理，其余请求则由反向代理处理：

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

您可以在同一个网站中混合使用 `handle` [`handle_path`](handle_path)，它们在同一个站点中仍会相互排斥：

```caddy
example.com {
	handle_path /foo/* {
		# 路径已去掉 "/foo" 前缀
	}

	handle /bar/* {
		# 路径仍保留 "/bar"
	}
}
```

您可以嵌套 `handle` 块来创建更复杂的路由逻辑：

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# 此块仅匹配 /foo/bar 下的路径
		}

		handle {
			# 此块匹配 /foo/ 下的其他所有路径
		}
	}

	handle {
		# 此块匹配其他所有路径（作为巨益回退）
	}
}
```
