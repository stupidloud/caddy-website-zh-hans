---
title: log_append (Caddyfile directive)
---

# log_append

現在のリクエストの access log にフィールドを追加します。

これは、そもそも access logging を有効にするために必要な [`log` ディレクティブ](log) と一緒に使います。

値には静的な文字列、またはリクエスト時点で placeholder の値に置き換えられる [placeholder](/docs/caddyfile/concepts#placeholders) を指定できます。


<a id="syntax"></a>
## 構文

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

デフォルトでは、log フィールドは middleware chain を戻る途中（つまり "late"）で追加されます。これは後続の handler（たとえば [`reverse_proxy`](reverse_proxy)、[`respond`](respond)、[`file_server`](file_server) のようにレスポンスを書き込む handler）がすべて完了した後なので、リクエストとレスポンスの最終状態を記録できます。

key の prefix として `<` を使うと "early" として扱われます。つまり、chain の次の handler を呼び出す*前*に log フィールドが追加されるため、後続の handler によって変更される前のリクエストを読み取れます。

デバッグ目的に限り（本番環境では使用しないでください）、値が `{http.request.body}`、`{http.request.body_base64}`、`{http.response.body}`、`{http.response.body_base64}` のいずれかの placeholder である場合、handler は特殊な処理を行います。リクエストボディの placeholder を使うと "early" モードが暗黙的に有効になり、リクエストボディがバッファリングされます。レスポンスボディの placeholder を使うと、レスポンスボディを取得するためにレスポンスバッファリングが有効になり、レスポンスが書き込まれるときにフィールドが "late" として log に追加されます。


<a id="examples"></a>
## 例

リクエストが site のどの領域から提供されたかを、`static` または `dynamic` として log に表示します。

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

実際に使われた reverse proxy upstream（`node1`、`node2`、`node3` のいずれか）と、upstream への proxy にかかった時間（ミリ秒）、および proxy upstream がレスポンス header を書き込むまでにかかった時間を log に表示します。

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

key に `<` を prefix として付けると、フィールドを "early" に log へ追加できます。これにより、後続の handler で変更される前のリクエスト状態を取得できます。たとえば、rewrite される前の元のリクエストパスを記録できます（元のリクエストパスは通常すでに log に含まれるため、この例は説明用です）。

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

デバッグ目的で、リクエストボディとレスポンスボディを log に追加します（性能を低下させ、log を非常に冗長にするため、本番環境では使用しないでください）。ボディが表示不能文字を含むバイナリデータである可能性がある場合は、代わりに placeholder の base64 版（例: `{http.request.body_base64}` と `{http.response.body_base64}`）を使うと、コピーや確認がしやすくなります。

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
