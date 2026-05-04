---
title: "invoke（Caddyfile 指令）"
---

# 调用

*⚠️ 实验性功能*

调用一个[命名路由](/docs/caddyfile/concepts#named-routes)。

当与具有自身内存状态的 HTTP 处理程序指令配合使用时，或者在加载时配置这些指令会消耗大量资源时，此功能非常有用。如果您拥有数百个或更多网站，调用命名路由有助于减少内存占用。

<aside class="tip">
	
与[`import`](/docs/caddyfile/directives/import)不同， `invoke` 不支持参数，但您可以使用 [`vars`](/docs/caddyfile/directives/vars) 来定义可在命名路由中使用的变量。

</aside>

## 语法

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** 是应调用的先前定义的路由名称。如果找不到该路由，则会触发错误。


## 示例

定义了一个带有[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)的[命名路由](/docs/caddyfile/concepts#named-routes)，该路由可在多个站点中重复使用，且每个站点均复用相同的内存中负载均衡状态。

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# 根域名可通过 /app 子路径访问应用，其他路径访问主站。
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# 应用也可通过子域名访问。
app.example.com {
	invoke app-proxy
}
```
