---
title: invoke (Caddyfile directive)
---

# invoke

<i>⚠️ Experimental</i>

[named route](/docs/caddyfile/concepts#named-routes) を呼び出します。

これは、独自のインメモリ状態を持つ HTTP handler ディレクティブや、ロード時の provision コストが高いディレクティブと組み合わせると便利です。数百以上の site がある場合、named route を呼び出すことでメモリ使用量を削減できます。

<aside class="tip">
	
[`import`](/docs/caddyfile/directives/import) とは異なり、`invoke` は引数をサポートしません。ただし、[`vars`](/docs/caddyfile/directives/vars) を使って、named route 内で使える変数を定義できます。

</aside>

<a id="syntax"></a>
## 構文

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** は、呼び出す事前定義済み route の名前です。route が見つからない場合はエラーになります。


<a id="examples"></a>
## 例

複数の site で再利用できる [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) を持つ [named route](/docs/caddyfile/concepts#named-routes) を定義します。各 site で同じインメモリのロードバランシング状態が再利用されます。

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Apex domain では /app サブパス経由でアプリにアクセスでき、
# それ以外ではメイン site を提供します。
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

# アプリは subdomain からもアクセスできます。
app.example.com {
	invoke app-proxy
}
```
