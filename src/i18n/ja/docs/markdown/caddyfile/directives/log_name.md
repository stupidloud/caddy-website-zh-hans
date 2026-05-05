---
title: log_name (Caddyfile directive)
---

# log_name

[`log` ディレクティブ](log)で access log を書き込むときに、リクエストで使う logger name を上書きします。

このディレクティブは、リクエストパスやメソッドなどの条件に応じて、リクエストを別々のファイルへ記録したい場合に便利です。

複数の logger name を指定でき、その場合リクエストの log は一致する複数の logger に送られます。

これは多くの場合、`log` ディレクティブの [`no_hostname`](log#no_hostname) オプションと組み合わせて使います。このオプションは logger が site block の hostnames に関連付けられるのを防ぐため、`log_name` を設定したリクエストだけがその logger に log を送ります。


<a id="syntax"></a>
## 構文

```caddy-d
log_name [<matcher>] <names...>
```


<a id="examples"></a>
## 例

リクエストを別々のファイルへ記録したい場合があります。たとえば、health check をメインの access log とは別のファイルに記録できます。

`log` 内で `no_hostname` を使うと、その logger は site block の hostnames（ここでは `localhost`）に関連付けられません。そのため、その logger の名前に `log_name` が設定されたリクエストだけが log を受け取ります。

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
