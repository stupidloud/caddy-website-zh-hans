---
title: invoke (Caddyfile 指令)
---

# invoke

<i>⚠️ 實驗性功能</i>

調用一個 [具名路由 (named route)](/docs/caddyfile/concepts#named-routes)。

當與具有自身記憶體狀態的 HTTP handler 指令配合使用，或者在載入時配置成本較高時，這非常有用。如果你有數百個或更多的站點，調用具名路由可以幫助減少記憶體使用。

<aside class="tip">

與 [`import`](/docs/caddyfile/directives/import) 不同，`invoke` 不支援參數，但你可以使用 [`vars`](/docs/caddyfile/directives/vars) 來定義可在具名路由內使用的變數。

</aside>

<a id="syntax"></a>
## 語法

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** 是先前定義的應被調用的路由名稱。如果找不到該路由，則會觸發錯誤。


<a id="examples"></a>
## 範例

定義一個帶有 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 的 [具名路由 (named route)](/docs/caddyfile/concepts#named-routes)，它可以在多個站點中重複使用，且每個站點都重用相同的記憶體負載平衡狀態。

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Apex 域名允許透過 /app 子路徑訪問應用程式
# 否則訪問主站點。
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# 該應用程式也可以透過子域名訪問。
app.example.com {
	invoke app-proxy
}
```
