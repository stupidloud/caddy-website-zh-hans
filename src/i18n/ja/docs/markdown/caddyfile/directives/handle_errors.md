---
title: handle_errors (Caddyfile directive)
---

# handle_errors

エラーハンドラを設定します。

通常の HTTP request handler がエラーを返すと、通常処理は停止し、error handler が呼び出されます。error handler は通常の route と同じ形の route を構成し、通常の route でできることは何でも実行できます。これにより、HTTP リクエスト中のエラー処理を大きく制御し、柔軟にできます。たとえば、静的エラーページ、template 化されたエラーページ、または別の backend への reverse proxy によってエラーを処理できます。

この directive は、異なる status code に対して異なる処理を行うため、別々の status code で繰り返し使えます。status code を指定しない場合は任意のエラーに一致し、他の error handler が一致しない場合の fallback として動作します。

リクエストの context は error route に引き継がれるため、[site root](root) や [vars](vars) など、request context に設定された値は error handler でも保持されます。さらに、エラー処理中には [new placeholders](#placeholders) が利用可能です。

[`reverse_proxy`](reverse_proxy) など一部の directive は、エラーに分類される HTTP status のレスポンスを書き込むことがありますが、それによって error route が trigger されるわけではない点に注意してください。

独自の routing decision に基づいて明示的にエラーを trigger したい場合は、[`error`](error) directive を使えます。


<a id="syntax"></a>
## 構文

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** は、処理中のエラーと照合する 1 つ以上の HTTP status code です。status code は 3 桁の数字、または `4xx` や `5xx` という特殊な形式にできます。それぞれ 400-499 または 500-599 の範囲のすべての status code に一致します。status code を指定しない場合は任意のエラーに一致し、他の error handler が一致しない場合の fallback として動作します。

- **<directives...>** は HTTP handler [directives](/docs/caddyfile/directives) と [matchers](/docs/caddyfile/matchers) のリストです。1 行に 1 つずつ書きます。


<a id="placeholders"></a>
## Placeholder

エラー処理中は次の placeholder が利用できます。これらは [Caddyfile shorthands](/docs/caddyfile/concepts#placeholders) であり、完全な placeholder は [HTTP server's error routes の JSON docs](/docs/json/apps/http/servers/errors/#routes) にあります。

| Placeholder | 説明 |
|---|---|
| `{err.status_code}` | 推奨 HTTP status code |
| `{err.status_text}` | 推奨 status code に関連付けられた status text |
| `{err.message}` | エラーメッセージ |
| `{err.trace}` | エラーの発生元 |
| `{err.id}` | このエラー発生を表す識別子 |


<a id="examples"></a>
## 例

status code に基づくカスタムエラーページ（つまり、`404` エラー用の `404.html` というページ）。[`file_server`](file_server) は `handle_errors` 内で実行された場合、エラーの HTTP status code を保持する点に注意してください（事前にサイト内で [site root](root) を設定している前提です）。

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

[`templates`](templates) を使ってカスタムエラーメッセージを書き込む単一のエラーページ:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

一部の error code に対してのみカスタムエラーページを提供したい場合は、[`file`](/docs/caddyfile/matchers#file) matcher を使って、事前にカスタムエラーファイルの存在を確認できます。

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

HTTP error の処理とあなたの一日を良くすることに非常に長けたプロ向けサーバーへ reverse proxy します。

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

[`respond`](respond) を使って error code と name を返すだけの例:

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

特定の error code を別々に処理するには:

```caddy-d
handle_errors 404 410 {
	respond "It's a 404 or 410 error!"
}

handle_errors 5xx {
	respond "It's a 5xx error."
}

handle_errors {
	respond "It's another error"
}
```

上の設定は下の設定と同じように動作します。下では、status code に対して [`expression`](/docs/caddyfile/matchers#expression) matcher を使い、相互排他性のために [`handle`](handle) を使っています。

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "It's a 404 or 410 error!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "It's a 5xx error."
	}

	handle {
		respond "It's another error"
	}
}
```
