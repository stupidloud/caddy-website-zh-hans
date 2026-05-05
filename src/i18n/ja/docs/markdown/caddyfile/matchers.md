---
title: "Request matchers (Caddyfile)"
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

<a id="request-matchers"></a>
# Request Matchers

**Request matchers** は、さまざまな条件でリクエストを絞り込む（または分類する）ために使えます。

- [構文](#syntax)
	- [例](#examples)
	- [ワイルドカード matcher](#wildcard-matchers)
	- [パス matcher](#path-matchers)
	- [名前付き matcher](#named-matchers)
- [標準 matcher](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


<a id="syntax"></a>
## 構文

Caddyfile では、ディレクティブの直後に置く **matcher token** によって、そのディレクティブが適用される範囲を制限できます。matcher token には次の形式があります。

1. [**`*`**](#wildcard-matchers): すべてのリクエストに一致します（ワイルドカード、デフォルト）。
2. [**`/path`**](#path-matchers): スラッシュで始まり、リクエストパスに一致します。
3. [**`@name`**](#named-matchers): *名前付き matcher* を指定します。

ディレクティブが matcher をサポートしている場合、その構文ドキュメントでは `[<matcher>]` と表示されます。matcher token は [通常は任意](/docs/caddyfile/directives#syntax) で、`[ ]` で示されます。matcher token を省略した場合は、ワイルドカード matcher (`*`) と同じです。


<a id="examples"></a>
#### 例

このディレクティブは [すべて](#wildcard-matchers) の HTTP リクエストに適用されます。

```caddy-d
reverse_proxy localhost:9000
```

これは上と同じです（ここでは `*` は不要です）。

```caddy-d
reverse_proxy * localhost:9000
```

一方、このディレクティブは `/api/` で始まる [path](#path-matchers) を持つリクエストだけに適用されます。

```caddy-d
reverse_proxy /api/* localhost:9000
```

path 以外で一致させるには、[名前付き matcher](#named-matchers) を定義し、`@name` で参照します。

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### ワイルドカード matcher

ワイルドカード（または "catch-all"）matcher `*` はすべてのリクエストに一致し、matcher token が必須の場合にだけ必要です。たとえば、ディレクティブに渡したい最初の引数がたまたま path でもある場合、それは path matcher とまったく同じ見た目になります。そのような曖昧さを避けるため、次のようにワイルドカード matcher を使えます。

```caddy-d
root * /home/www/mysite
```

それ以外では、この matcher はあまり使いません。構文上必要でなければ、省略することを一般的に推奨します。


<a id="path-matchers"></a>
### パス matcher

URI path による一致はリクエストを一致させる最も一般的な方法なので、次のように matcher をインラインで書けます。

```caddy-d
redir /old.html /new.html
```

path matcher token はスラッシュ `/` で始まる必要があります。

**[Path matching](#path) はデフォルトでは完全一致であり、prefix match ではありません。** 高速な prefix match を行うには、末尾に `*` を付ける必要があります。`/foo*` は `/foo` と `/foo/` に加えて `/foobar` にも一致します。実際には `/foo/*` が必要な場合があります。


<a id="named-matchers"></a>
### 名前付き matcher

path matcher でもワイルドカード matcher でもない matcher は、すべて名前付き matcher である必要があります。これは特定のディレクティブの外側で定義され、再利用できる matcher です。

一意な名前を持つ matcher を定義すると柔軟性が増し、[利用可能な任意の matcher](#standard-matchers) を組み合わせて 1 つの集合にできます。

```caddy-d
@name {
	...
}
```

または、その集合に matcher が 1 つしかない場合は、同じ行に書けます。

```caddy-d
@name ...
```

その後、ディレクティブの最初の引数として指定することで、次のように matcher を使えます。

```caddy-d
directive @name
```

たとえば次の設定は、HTTP/1.1 websocket リクエストを `localhost:6001` に proxy し、それ以外のリクエストを `localhost:8080` に proxy します。`Connection` という名前の header field が `Upgrade` を *含み*、**かつ** `Upgrade` という別の field が正確に `websocket` であるリクエストに一致します。

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

matcher set が 1 つの matcher だけで構成される場合は、1 行構文も使えます。

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

特別なケースとして、[`expression` matcher](#expression) は matcher 名の後に [引用された](/docs/caddyfile/concepts#tokens-and-quotes) 引数（CEL expression 自体）が 1 つ続く場合、名前を明示せずに使えます。

```caddy-d
@not-found `{err.status_code} == 404`
```

ディレクティブと同様に、名前付き matcher の定義は、それを使う [site blocks](/docs/caddyfile/concepts#structure) の中に置く必要があります。

名前付き matcher の定義は *matcher set* を構成します。集合内の matcher は AND で結合されます。つまり、すべてが一致する必要があります。たとえば、集合内に [`header`](#header) matcher と [`path`](#path) matcher の両方がある場合、両方が一致する必要があります。

同じ型の matcher が複数ある場合（例: 同じ集合内の複数の [`path`](#path) matcher）は、後述の各セクションで説明するように、ブール代数（AND/OR）でマージされることがあります。

より複雑なブール一致ロジックには、[`expression` matcher](#expression) を使って CEL expression を書くことを推奨します。これは **and** `&&`、**or** `||`、**parentheses** `( )` をサポートします。





<a id="standard-matchers"></a>
## 標準 matcher

matcher の完全なドキュメントは、[各 matcher module のドキュメント](/docs/json/apps/http/servers/routes/match/) にあります。

リクエストは次の方法で一致させることができます。



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

client IP address によって一致させます。正確な IP または CIDR range を受け付けます。IPv6 zone もサポートされます。

この matcher は [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) global option が設定されている場合に最も有用です。設定されていない場合は、[`remote_ip`](#remote-ip) matcher と同じように動作します。信頼済み proxy からのリクエストだけが、リクエスト開始時に client IP を解析されます。信頼されていないリクエストでは、直接接続している peer の remote IP address、または [PROXY protocol](/docs/caddyfile/options#proxy-protocol) で設定された address が使われます。

ショートカットとして、`private_ranges` を使うとすべての private IPv4 および IPv6 range に一致できます。これは次のすべての range を指定するのと同じです: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

名前付き matcher ごとに複数の `client_ip` matcher を置くことができ、それらの range はマージされ、OR で結合されます。

<a id="example"></a>
#### 例:

private IPv4 address からのリクエストに一致させます。

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

この matcher は、match を反転するために [`not`](#not) matcher と組み合わせてよく使われます。たとえば、*public* IPv4 および IPv6 address からのすべての接続（すべての private range の逆）を abort するには、次のようにします。

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

[CEL expression](#expression) では、次のように書けます。

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

`true` または `false` を返す任意の [CEL (Common Expression Language)](https://github.com/google/cel-spec) expression によって一致させます。

ほとんどの他の request matcher も expression 内で関数として使えます。これにより、expression の外側よりも柔軟なブールロジックを書けます。CEL expression 内でサポートされる構文については、各 matcher のドキュメントを参照してください。

Caddy [placeholders](/docs/conventions#placeholders)（または [Caddyfile shorthands](/docs/caddyfile/concepts#placeholders)）は、CEL environment によって解釈される前に前処理され、通常の CEL 関数呼び出しへ変換されるため、これらの CEL expression 内で使えます。placeholder を matcher 関数の文字列引数として渡したい場合は、前処理されないように先頭の `{` を backslash `\` でエスケープします。例: `file('\{path}.md')`。

利便性のため、CEL expression だけで構成される名前付き matcher を定義する場合は、matcher 名を省略できます。CEL expression は [引用](/docs/caddyfile/concepts#tokens-and-quotes) されている必要があります（backticks または heredocs を推奨）。これはかなり読みやすくなります。

```caddy-d
@mutable `{method}.startsWith("P")`
```

この場合、CEL matcher が使われるものとみなされます。

<a id="examples-1"></a>
#### 例:

method が `P` で始まるリクエスト、たとえば `PUT` や `POST` に一致させます。

```caddy-d
@methods expression {method}.startsWith("P")
```

handler が error status code `404` を返したリクエストに一致させます。[`handle_errors` directive](/docs/caddyfile/directives/handle_errors) と組み合わせて使います。

```caddy-d
@404 expression {err.status_code} == 404
```

path が 2 つの異なる regular expression のいずれかに一致するリクエストに一致させます。通常、[`path_regexp`](#path-regexp) matcher は名前付き matcher ごとに 1 つしか存在できないため、これは expression を使う場合にだけ書けます。

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

または、matcher 名を省略し、[backticks](/docs/caddyfile/concepts#tokens-and-quotes) で囲んで 1 つの token として解析させると、同じ意味になります。

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

[heredoc syntax](/docs/caddyfile/concepts#heredocs) を使って、複数行の CEL expression を書くこともできます。

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

file によって一致させます。

- `root` は file を探す directory を定義します。デフォルトは現在の working directory、または設定されている場合は `root` [variable](/docs/modules/http.handlers.vars) (`{http.vars.root}`) です（[`root` directive](/docs/caddyfile/directives/root) で設定できます）。

- `try_files` は、その list 内の file を try_policy に従ってチェックします。

  directory に一致させるには、path の末尾にスラッシュ `/` を追加します。すべての file path は site [root](/docs/caddyfile/directives/root) からの相対パスで、[glob patterns](https://pkg.go.dev/path/filepath#Match) は展開されます。

  `try_policy` が `first_exist`（デフォルト）の場合、list の最後の項目は `=` が前置された number（例: `=404`）にできます。これは fallback としてその code の error を発生させます。この error は [`handle_errors`](/docs/caddyfile/directives/handle_errors) で捕捉して処理できます。



- `try_policy` は file の選び方を指定します。デフォルトは `first_exist` です。

	- `first_exist` は file の存在をチェックします。最初に存在する file が選択されます。

	- `first_exist_fallback` は `first_exist` と似ていますが、disk access を避けるため、list の最後の要素は常に存在するとみなします。

	- `smallest_size` は最も小さい size の file を選びます。

	- `largest_size` は最も大きい size の file を選びます。

	- `most_recently_modified` は最も最近変更された file を選びます。

- `split_path` は、試行する各 filepath 内で list 中に最初に見つかった delimiter の位置で path を分割します。分割値ごとに、delimiter 自体を含む左側が試行される filepath になります。たとえば、`.php` を delimiter として `/remote.php/dav/` を使うと、file `/remote.php` が試行されます。delimiter を split delimiter として使うには、URI path component の末尾に現れる必要があります。これはニッチな設定で、主に PHP site を配信するときに使われます。

`first_exist` policy の `try_files` は非常によく使われるため、次の 1 行ショートカットがあります。

```caddy-d
file <files...>
```

空の `file` matcher（後ろに file list がないもの）は、リクエストされた file が、URI からそのまま、[site root](/docs/caddyfile/directives/root) からの相対パスとして存在するかどうかを確認します。これは実質的に `file {path}` と同じです。


<aside class="tip">

disk 上の file の存在に基づいて rewrite することは非常によくあるため、`file` matcher と [`rewrite` handler](/docs/caddyfile/directives/rewrite) のショートカットである [`try_files` directive](/docs/caddyfile/directives/try_files) もあります。

</aside>


一致すると、次の 4 つの新しい placeholder が利用可能になります。

- `{file_match.relative}` file の root-relative path。リクエストを rewrite するときによく役立ちます。
- `{file_match.absolute}` root を含む、matched file の absolute path。
- `{file_match.type}` file の種類。`file` または `directory`。
- `{file_match.remainder}` file path を分割した後に残った部分（`split_path` が設定されている場合）


<a id="examples-2"></a>
#### 例:

path が存在する file であるリクエストに一致させます。

```caddy-d
@file file
```

path に `.html` を付けたものが存在する file であるリクエスト、またはそうでない場合に path 自体が存在する file であるリクエストに一致させます。

```caddy-d
@html file {
	try_files {path}.html {path}
}
```

上と同じですが、1 行ショートカットを使い、file が見つからない場合は fallback として 404 error を発生させます。

```caddy-d
@html-or-error file {path}.html {path} =404
```

[CEL expressions](#expression) を使った例をさらにいくつか示します。placeholder は CEL environment によって解釈される前に前処理され、通常の CEL 関数呼び出しへ変換されるため、ここでは連結を使っている点に注意してください。また、現在の parsing limitation により、placeholder と連結する場合は long-form を使う必要があります。

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

request header field によって一致させます。

- `<field>` はチェックする HTTP header field の名前です。
	- `!` が前置されている場合、一致するにはその field が存在してはいけません（value arg は省略します）。
- `<value>` は、一致するために field が持つ必要がある値です。1 つ以上指定できます。
	- `*` が前置されている場合、高速な suffix match（末尾に現れる）を行います。
	- `*` が後置されている場合、高速な prefix match（先頭に現れる）を行います。
	- `*` で囲まれている場合、高速な substring match（任意の位置に現れる）を行います。
	- それ以外の場合は、高速な exact match です。

同じ集合内の異なる header field は AND で結合されます。field ごとの複数 value は OR で結合されます。

header field は繰り返し出現し、異なる値を持つ可能性がある点に注意してください。backend application は、header field value が単一値ではなく array であることを必ず考慮する必要があります。Caddy はそのような曖昧な状況で意味を解釈しません。

<a id="example-1"></a>
#### 例:

`Connection` header に `Upgrade` を含むリクエストに一致させます。

```caddy-d
@upgrade header Connection *Upgrade*
```

`Foo` header に `bar` または `baz` を含むリクエストに一致させます。

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

`Foo` header field をまったく持たないリクエストに一致させます。

```caddy-d
@not_foo header !Foo
```

[CEL expression](#expression) を使い、`Connection` header に `Upgrade` が含まれ、`Upgrade` header が `websocket` と等しいかどうかを確認して WebSocket リクエストに一致させます（HTTP/2 ではこの用途に `:protocol` header があります）。

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

[`header`](#header) と似ていますが、regular expression をサポートします。

使われる regular expression language は Go に含まれる RE2 です。[RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) と [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax) を参照してください。

v2.8.0 以降、`name` が指定されて*いない*場合、名前は named matcher の名前から取られます。たとえば named matcher `@foo` は、この matcher の名前を `foo` にします。名前を指定する主な利点は、同じ named matcher 内で複数の regexp matcher（例: `header_regexp` と [`path_regexp`](#path-regexp)、または複数の異なる header field）を使う場合です。

capture group は、match 後の directive 内で [placeholder](/docs/caddyfile/concepts#placeholders) としてアクセスできます。
- `{re.<name>.<capture_group>}`。ここで:
  - `<name>` は regular expression の名前です。
  - `<capture_group>` は expression 内の capture group の名前または番号です。

- `{re.<capture_group>}` は、名前なしでも利便性のために設定されます。注意点として、複数の regexp matcher が連続して使われる場合、この placeholder value は次の matcher によって上書きされます。

capture group `0` は regexp match 全体、`1` は最初の capture group、`2` は 2 番目の capture group、以降も同様です。したがって `{re.foo.1}` と `{re.1}` はどちらも最初の capture group の値を保持します。

regexp pattern はマージできないため、header field ごとにサポートされる regular expression は 1 つだけです。さらに必要な場合は、[`expression` matcher](#expression) の使用を検討してください。複数の異なる header field に対する match は AND で結合されます。

<a id="example-2"></a>
#### 例:

Cookie header に `login_` の後へ hex string が続く値を含み、`{re.login.1}` または `{re.1}` でアクセスできる capture group を持つリクエストに一致させます。

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

名前を省略すると、named matcher から推論されるため簡略化できます。

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

または、[CEL expression](#expression) を使って同じことを書けます。

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

リクエストの `Host` header field によって request を一致させます。

ほとんどの site block は site address の中で host をすでに示しているため、この matcher は wildcard hostname を使う site block（[wildcard certificates pattern](/docs/caddyfile/patterns#wildcard-certificates) を参照）で、hostname 固有のロジックが必要な場合によく使われます。

複数の `host` matcher は OR で結合されます。

<a id="example-3"></a>
#### 例:

1 つの subdomain に一致させます。

```caddy-d
@sub host sub.example.com
```

apex domain と subdomain に一致させます。

```caddy-d
@site host example.com www.example.com
```

[CEL expression](#expression) を使って複数の subdomain に一致させます。

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

HTTP request の method（verb）によって一致させます。verb は `POST` のように uppercase にする必要があります。1 つまたは複数の method に一致できます。

複数の `method` matcher は OR で結合されます。

<a id="examples-3"></a>
#### 例:

`GET` method のリクエストに一致させます。

```caddy-d
@get method GET
```

`PUT` または `DELETE` method のリクエストに一致させます。

```caddy-d
@put-delete method PUT DELETE
```

[CEL expression](#expression) を使って read-only method に一致させます。

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

```caddy-d
not <matcher>
```

または、AND で結合される複数の matcher を否定するには、block を開きます。

```caddy-d
not {
	<matchers...>
}
```

囲まれた matcher の結果が否定されます。

<a id="examples-4"></a>
#### 例:

path が `/css/` または `/js/` で始まらないリクエストに一致させます。

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

次のどちらも持たないリクエストに一致させます。
- `/api/` path prefix
- `POST` request method

つまり、一致するにはこれらを 1 つも持っていてはいけません。

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

次の両方を同時には持たないリクエストに一致させます。
- `/api/` path prefix
- `POST` request method

つまり、一致するにはこれらのどちらも持たないか、どちらか一方だけを持つ必要があります。

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

この matcher には [CEL expression](#expression) はありません。代わりに `!` operator を使って否定できるためです。例:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

parentheses を使うと、これは次と同じです。

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

request path（request URI の path component）によって一致させます。path match は exact ですが case-insensitive です。wildcard `*` を使えます。

- 末尾だけに置くと prefix match (`/prefix/*`)
- 先頭だけに置くと suffix match (`*.suffix`)
- 両側だけに置くと substring match (`*/contains/*`)
- 中央だけに置くと globular match (`/accounts/*/info`)

slash は重要です。たとえば `/foo*` は `/foo`、`/foobar`、`/foo/`、`/foo/bar` に一致しますが、`/foo/*` は `/foo` や `/foobar` には*一致しません*。

request path は、matching 前に directory traversal dots を解決するために clean されます。さらに、match pattern に複数の slash が含まれていない限り、複数の slash はマージされます。言い換えると、`/foo` は `/foo` と `//foo` に一致しますが、`//foo` は `//foo` にだけ一致します。

任意の URI には複数の escaped form があるため、request path は正規化（URL-decoded、unescaped）されます。ただし、match pattern にも同じ位置で escape sequence が存在する箇所は除きます。たとえば `/foo/bar` は `/foo/bar` と `/foo%2Fbar` の両方に一致しますが、`/foo%2Fbar` は `/foo%2Fbar` にだけ一致します。これは escape sequence が configuration 内で明示されているためです。

special wildcard escape `%*` を `*` の代わりに使うと、その matching span を escaped のままにできます。たとえば `/bands/*/*` は `/bands/AC%2FDC/T.N.T` に一致しません。path は normalized space で比較され、`/bands/AC/DC/T.N.T` のように見えるため pattern と一致しないからです。一方、`/bands/%*/*` は `/bands/AC%2FDC/T.N.T` に一致します。`%*` が表す span は escape sequence を decode せずに比較されるためです。

複数の path は OR で結合されます。

<a id="examples-5"></a>
#### 例:

複数の directory とその内容に一致させます。

```caddy-d
@assets path /js/* /css/* /images/*
```

特定の file に一致させます。

```caddy-d
@favicon path /favicon.ico
```

file extension に一致させます。

```caddy-d
@extensions path *.js *.css
```

[CEL expression](#expression) を使う場合:

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

[`path`](#path) と似ていますが、regular expression をサポートします。URI-decoded/unescaped path に対して実行されます。

使われる regular expression language は Go に含まれる RE2 です。[RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) と [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax) を参照してください。

v2.8.0 以降、`name` が指定されて*いない*場合、名前は named matcher の名前から取られます。たとえば named matcher `@foo` は、この matcher の名前を `foo` にします。名前を指定する主な利点は、同じ named matcher 内で複数の regexp matcher（例: `path_regexp` と [`header_regexp`](#header-regexp)）を使う場合です。

capture group は、match 後の directive 内で [placeholder](/docs/caddyfile/concepts#placeholders) としてアクセスできます。
- `{re.<name>.<capture_group>}`。ここで:
  - `<name>` は regular expression の名前です。
  - `<capture_group>` は expression 内の capture group の名前または番号です。

- `{re.<capture_group>}` は、名前なしでも利便性のために設定されます。注意点として、複数の regexp matcher が連続して使われる場合、この placeholder value は次の matcher によって上書きされます。

capture group `0` は regexp match 全体、`1` は最初の capture group、`2` は 2 番目の capture group、以降も同様です。したがって `{re.foo.1}` と `{re.1}` はどちらも最初の capture group の値を保持します。

この matcher はそれ自身とマージできないため、named matcher ごとに指定できる `path_regexp` pattern は 1 つだけです。さらに必要な場合は、[`expression` matcher](#expression) の使用を検討してください。

<a id="example-4"></a>
#### 例:

path が 6 文字の hex string で終わり、その後に file extension として `.css` または `.js` が続くリクエストに一致させます。capture group（`( )` で囲まれた部分）は、それぞれ `{re.static.1}` と `{re.static.2}`（または `{re.1}` と `{re.2}`）でアクセスできます。

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

名前を省略すると、named matcher から推論されるため簡略化できます。

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

または、[CEL expression](#expression) を使って同じことを書き、さらに [`file`](#file) が disk 上に存在することも検証できます。

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

request protocol によって一致させます。`http`、`https`、`grpc` のような広い protocol 名を使えます。また、`http/1.1` や `http/2+` のように specific または minimum HTTP version も使えます。

named matcher ごとに指定できる `protocol` matcher は 1 つだけです。

<a id="example-5"></a>
#### 例:

HTTP/2 を使うリクエストに一致させます。

```caddy-d
@http2 protocol http/2+
```

[CEL expression](#expression) を使う場合:

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

query string parameter によって一致させます。`key=value` pair の sequence、または empty string `""` を指定します。key は exact（case-sensitive）に一致しますが、任意の value に一致する `*` もサポートします。value には placeholder を使えます。empty string は query parameter を持たない http request に一致します。

名前付き matcher ごとに複数の `query` matcher を置くことができ、同じ key を持つ pair は OR で結合されます。異なる key は AND で結合されます。つまり、matcher 内のすべての key は、少なくとも 1 つの matching value を持つ必要があります。

不正な query string（不正な構文、escape されていない semicolon など）は parse に失敗するため、一致しません。

**NOTE:** Query string parameter は単一値ではなく array です。これは query string では key の繰り返しが有効であり、それぞれが異なる value を持てるためです。この matcher は、設定された value のいずれかが query string 内で key に割り当てられていれば、その key に一致します。query string を使う backend application は、query string value が array であり、複数の value を持てることを必ず考慮する必要があります。

<a id="example-6"></a>
#### 例:

任意の value を持つ `q` query parameter に一致させます。

```caddy-d
@search query q=*
```

value が `asc` または `desc` の `sort` query parameter に一致させます。

```caddy-d
@sorted query sort=asc sort=desc
```

[CEL expression](#expression) を使って `q` と `sort` の両方に一致させます。

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

remote IP address（つまり直接接続している peer の IP address、または [PROXY protocol](/docs/caddyfile/options#proxy-protocol) で設定された address）によって一致させます。正確な IP または CIDR range を受け付けます。IPv6 zone もサポートされます。

ショートカットとして、`private_ranges` を使うとすべての private IPv4 および IPv6 range に一致できます。これは次のすべての range を指定するのと同じです: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

HTTP header から解析された client の "real IP" に一致させたい場合は、代わりに [`client_ip`](#client-ip) matcher を使ってください。

名前付き matcher ごとに複数の `remote_ip` matcher を置くことができ、それらの range はマージされ、OR で結合されます。

<a id="example-7"></a>
#### 例:

private IPv4 address からのリクエストに一致させます。

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

この matcher は、match を反転するために [`not`](#not) matcher と組み合わせてよく使われます。たとえば、*public* IPv4 および IPv6 address からのすべての接続（すべての private range の逆）を abort するには、次のようにします。

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

[CEL expression](#expression) では、次のように書けます。

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

request context 内の variable の値、または placeholder の値によって一致させます。複数の value を指定すると、それらの可能な value のいずれかに一致します（OR）。

**&lt;variable&gt;** 引数には、variable 名または curly braces `{ }` 内の placeholder を指定できます。（placeholder は最初の parameter では展開されません。）

この matcher は、output を設定する [`map` directive](/docs/caddyfile/directives/map)、route 内の [`vars` directive](/docs/caddyfile/directives/vars)、または request context に情報を設定する plugin と組み合わせると特に有用です。

<a id="example-8"></a>
#### 例:

[`map` directive](/docs/caddyfile/directives/map) の output `magic_number` が `3` または `5` である場合に一致させます。

```caddy-d
vars {magic_number} 3 5
```

任意の placeholder value、つまり authenticated user の ID が `Bob` または `Alice` である場合に一致させます。

```caddy-d
vars {http.auth.user.id} Bob Alice
```

[`vars` directive](/docs/caddyfile/directives/vars) を使って variable を設定し、その後 [`vars` matcher](#vars) でそれに一致させる完全な例です。ここでは 2 つの request header を 1 つの variable に結合し、その variable に一致させます。

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

[CEL expression](#expression) では、次のように書けます。

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

[`vars`](#vars) と似ていますが、regular expression をサポートします。

使われる regular expression language は Go に含まれる RE2 です。[RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) と [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax) を参照してください。

v2.8.0 以降、`name` が指定されて*いない*場合、名前は named matcher の名前から取られます。たとえば named matcher `@foo` は、この matcher の名前を `foo` にします。名前を指定する主な利点は、同じ named matcher 内で複数の regexp matcher（例: `vars_regexp` と [`header_regexp`](#header-regexp)）を使う場合です。

capture group は、match 後の directive 内で [placeholder](/docs/caddyfile/concepts#placeholders) としてアクセスできます。
- `{re.<name>.<capture_group>}`。ここで:
  - `<name>` は regular expression の名前です。
  - `<capture_group>` は expression 内の capture group の名前または番号です。

- `{re.<capture_group>}` は、名前なしでも利便性のために設定されます。注意点として、複数の regexp matcher が連続して使われる場合、この placeholder value は次の matcher によって上書きされます。

capture group `0` は regexp match 全体、`1` は最初の capture group、`2` は 2 番目の capture group、以降も同様です。したがって `{re.foo.1}` と `{re.1}` はどちらも最初の capture group の値を保持します。

regexp pattern はマージできないため、variable name ごとにサポートされる regular expression は 1 つだけです。さらに必要な場合は、[`expression` matcher](#expression) の使用を検討してください。複数の異なる variable に対する match は AND で結合されます。

<a id="example-9"></a>
#### 例:

[`map` directive](/docs/caddyfile/directives/map) の output `magic_number` が `4` で始まる value である場合に一致させ、その value を `{re.magic.1}` または `{re.1}` でアクセスできる capture group に capture します。

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

名前を省略すると、named matcher から推論されるため簡略化できます。

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

[CEL expression](#expression) では、次のように書けます。

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
