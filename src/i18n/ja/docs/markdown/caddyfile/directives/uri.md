---
title: uri (Caddyfile directive)
---

# uri

リクエストの URI を操作します。path の prefix/suffix を取り除くか、URI 全体の部分文字列を置換できます。

このディレクティブは [`rewrite`](rewrite) とは異なります。`uri` は `rewrite` のように URI をまったく別のものへリセットするのではなく、URI を *差分的に* 変更します。`rewrite` は内部 redirect として特別に扱われますが、`uri` は単なる middleware の 1 つです。


<a id="syntax"></a>
## 構文

複数の異なる操作がサポートされています。

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

最初の（non-matcher）引数が操作を指定します。

- **strip_prefix** は path から prefix を取り除きます。

- **strip_suffix** は path から suffix を取り除きます。

- **replace** は URI 全体に対して部分文字列置換を行います。

	- **&lt;target&gt;** は prefix、suffix、または検索文字列/正規表現です。prefix の場合、path は常に forward slash で始まるため、先頭の forward slash は省略できます。

	- **&lt;replacement&gt;** は置換文字列です。`$name` または `${name}` 構文、または `$1` のような index 番号で capture group を使用できます。詳細は [Go documentation](https://golang.org/pkg/regexp/#Regexp.Expand) を参照してください。置換値が `""` の場合、一致した text は値から削除されます。

	- **&lt;limit&gt;** は、置換回数の最大数を制限する任意の値です。

- **path_regexp** は URI の path 部分に対して正規表現置換を行います。

	- **&lt;target&gt;** は prefix、suffix、または検索文字列/正規表現です。prefix の場合、path は常に forward slash で始まるため、先頭の forward slash は省略できます。

	- **&lt;replacement&gt;** は置換文字列です。`$name` または `${name}` 構文、または `$1` のような index 番号で capture group を使用できます。詳細は [Go documentation](https://golang.org/pkg/regexp/#Regexp.Expand) を参照してください。置換値が `""` の場合、一致した text は値から削除されます。

- **query** は URI query を操作します。mode は parameter 名の prefix または引数の数によって決まります。ブロックを使うと複数の操作をまとめて指定でき、rename 🡒 set 🡒 append 🡒 replace 🡒 delete の順にグループ化されて実行されます。

	- prefix がない場合、query 内で parameter が指定値に設定されます。
	
	  たとえば、`uri query foo bar` は `foo` param の値を `bar` に設定します。

	- `-` を prefix に付けると、query から parameter を削除します。
	
	  たとえば、`uri query -foo` は query から `foo` parameter を削除します。

	- `+` を prefix に付けると、指定値を持つ parameter を query に追加します。これは同じ名前の既存 parameter を上書き*しません*（上書きするには `+` を省略します）。
	
	  たとえば、`uri query +foo bar` は query に `foo=bar` を追加します。

	- `>` を中置した param は、parameter を `>` の後の値へ rename します。
	
	  たとえば、`uri query foo>bar` は `foo` parameter を `bar` に rename します。

	- 引数が 3 つの場合、query 値の正規表現置換が行われます。最初の引数は query param 名、2 番目は検索値、3 番目は置換値です。最初の引数（param 名）は、すべての query param に対して置換を行うために `*` にできます。
	
	  `$name` または `${name}` 構文、または `$1` のような index 番号で capture group を使用できます。詳細は [Go documentation](https://golang.org/pkg/regexp/#Regexp.Expand) を参照してください。置換値が `""` の場合、一致した text は値から削除されます。
	
	  たとえば、`uri query foo ^(ba)r $1z` は、値が `bar` で始まる `foo` param の値を置換し、その結果値は `baz` になります。

URI の変更は、正規化済みまたは unescaped 形式の URI に対して行われます。ただし、prefix または suffix pattern 内では escape sequence を使い、リクエスト path 内のその位置にある literal escape だけに一致させることができます。たとえば、`uri strip_prefix /a/b` は `/a/b/c` と `/a%2Fb/c` の両方を `/c` に rewrite します。また `uri strip_prefix /a%2Fb` は `/a%2Fb/c` を `/c` に rewrite しますが、`/a/b/c` には一致しません。

URI path は、変更前に directory traversal dot が取り除かれます。さらに、`<target>` 自体に複数の slash が含まれていない限り、`//` などの複数 slash は統合されます。

<a id="similar-directives"></a>
## 類似ディレクティブ

リクエスト URI を操作できる他のディレクティブもあります。

- [`rewrite`](rewrite) は、値を部分的に変更するのではなく、path と query 全体を新しい値へ変更します。

- [`handle_path`](handle_path) は [`handle`](handle) と同じですが、handler を実行する前にリクエストから prefix を取り除きます。多くの場合、`uri strip_prefix` の代わりに使うことで、設定を 1 行減らせます。


<a id="examples"></a>
## 例

すべてのリクエスト path の先頭から `/api` を取り除きます。

```caddy-d
uri strip_prefix /api
```

すべてのリクエスト path の末尾から `.php` を取り除きます。

```caddy-d
uri strip_suffix .php
```

任意のリクエスト URI 内の "/docs/" を "/v1/docs/" に置換します。

```caddy-d
uri replace /docs/ /v1/docs/
```

リクエスト path 内のすべての連続 slash（ただし request query は除く）を単一の slash にまとめます。

```caddy-d
uri path_regexp /{2,} /
```

`foo` query parameter の値を `bar` に設定します。

```caddy-d
uri query foo bar
```

query から `foo` parameter を削除します。

```caddy-d
uri query -foo
```

`foo` query parameter を `bar` に rename します。

```caddy-d
uri query foo>bar
```

`bar` parameter を query に追加します。

```caddy-d
uri query +foo bar
```

値が `bar` で始まる `foo` query parameter の値を `baz` に置換します。

```caddy-d
uri query foo ^(ba)r $1z
```

複数の query 操作をまとめて実行します。

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
