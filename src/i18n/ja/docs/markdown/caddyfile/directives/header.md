---
title: header (Caddyfile directive)
---

# header

HTTP response header fields を操作します。header value の設定、追加、削除、または正規表現による置換を実行できます。

デフォルトでは、header 操作は即座に実行されます。ただし、header が削除される場合（`-` prefix）またはデフォルト値を設定する場合（`?` prefix）は例外です。その場合、header 操作はクライアントへ書き込まれる時点まで自動的に defer されます。

HTTP request header を操作するには、[`request_header`](request_header) directive を使えます。


<a id="syntax"></a>
## 構文

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# Add
	+<field> <value>

	# Set
	<field> <value>

	# Set with defer
	><field> <value>

	# Delete
	-<field>

	# Replace
	<field> <find> <replace>

	# Replace with defer
	><field> <find> <replace>

	# Default
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** は header field の名前です。

  prefix がない場合、その field は設定（上書き）されます。

  `+` を prefix すると、field が既に存在する場合に上書き（設定）する代わりに field を追加します。header fields は 1 つのレスポンスに複数回現れることがあります。

  `-` を prefix すると field を削除します。field では、prefix または suffix の `*` wildcard を使って、一致するすべての field を削除できます。

  `?` を prefix すると field のデフォルト値を設定します。その field がまだ存在しない場合にのみ書き込まれます。

  `>` を prefix すると、ショートカットとして field を設定し、`defer` を有効にします。

- **&lt;value&gt;** は、field を追加または設定するときの header field value です。

- **&lt;find&gt;** は検索する正規表現です。placeholder を使って検索 pattern への動的 input を指定できます。使われる正規表現言語は Go に含まれる RE2 です。[RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) と [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax) を参照してください。

- **&lt;replace&gt;** は置換値です。search-and-replace を実行する場合は必須です。検索 pattern の capture group を参照するには `$1` や `$2` などを使います。置換値が `""` の場合、一致したテキストは値から削除されます。詳細は [Go documentation](https://golang.org/pkg/regexp/#Regexp.Expand) を参照してください。

- **defer** は、header 操作の実行をレスポンスがクライアントへ送信される時点まで遅らせます。この option は、次の条件で自動的に有効になります。
	- `-` を使って header fields を削除する場合。
	- `?` でデフォルト値を設定する場合。
	- set または replace 操作で `>` prefix を使う場合。
	- 1 つ以上の `match` 条件が存在する場合。

- **match** <span id="match"/> は inline [response matcher](/docs/caddyfile/response-matchers) です。header 操作は、指定された条件を満たすレスポンスにのみ適用されます。

複数の header 操作を行う場合は、block を開き、同じ方法で 1 行に 1 つの操作を指定できます。

`?` prefix を使ってデフォルト header value を設定する場合、複数の header 操作を含む `header` block 内にあったとしても、自動的に独自の `header` handler に分離されます。[Under the hood](/docs/modules/http.handlers.headers#response/require) では、`?` を使うと [response matcher](/docs/caddyfile/response-matchers) が設定され、directive 全体の handler に適用されます。その handler は header 操作（`defer` など）だけを適用しますが、field がまだ設定されていない場合に限ります。


<a id="examples"></a>
## 例

すべてのレスポンスにカスタム header field を設定します。

```caddy-d
header Custom-Header "My value"
```

"Hidden" header field を取り除きます。

```caddy-d
header -Hidden
```

任意の Location header 内の `http://` を `https://` に置換します。

```caddy-d
header Location http:// https://
```

すべてのページに security と privacy の header を設定します:（**WARNING:** 影響を理解している場合にのみ使ってください！）

```caddy-d
header {
	# FLoC tracking を無効化
	Permissions-Policy interest-cohort=()

	# HSTS を有効化
	Strict-Transport-Security max-age=31536000;

	# client が media type を sniff しないようにする
	X-Content-Type-Options nosniff

	# clickjacking protection
	X-Frame-Options DENY
}
```

相互排他的であることを意図した複数の header directive:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

upstream が定義していない場合にデフォルトの cache expiration を設定します。

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

GET リクエストへのすべての成功レスポンスを、最大 1 時間 cacheable としてマークします。

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

upstream server で例外が発生した場合に、エラーレスポンスが cache されないようにします。

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

upstream server が client hints をサポートしている場合、light mode のレスポンスを dark mode のレスポンスとは別に cacheable としてマークします。
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

wildcard 値を特定のドメインに置換して、過度に許可的な CORS header を防ぎます。
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**Note**: 置換操作では、`<find>` 値は正規表現として解釈されます。`*` 文字に一致させるには、上の例のように backslash で escape する必要があります。

代わりに、[response matcher](/docs/caddyfile/response-matchers) を使って header value にそのまま一致させることもできます。
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

`/no-cache` で始まる path に対して、proxy upstream が設定した cache expiration を上書きします。proxy が header を書き込んだ *after* に header を設定するため、`defer` を有効にする必要があります。

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

`Set-Cookie` header を deferred update して `SameSite=None` を追加します。regexp capture を使って既存の値を取得し、追加 option を付けて `$1` で先頭に再挿入します。

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
