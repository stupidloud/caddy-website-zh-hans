---
title: try_files (Caddyfile directive)
---

# try_files

site root 内に存在する、一覧のうち最初のファイルへリクエスト URI path を書き換えます。一致するファイルがない場合、rewrite は行われません。


<a id="syntax"></a>
## 構文

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** は試行するファイルの一覧です。URI path は、最初に存在するファイルへ書き換えられます。

  directory に一致させるには、path の末尾に forward slash `/` を追加します。すべての file path は site [root](root) からの相対 path であり、[glob patterns](https://pkg.go.dev/path/filepath#Match) は展開されます。

  各引数には query 文字列を含めることもできます。その場合、その特定のファイルに一致したときは query 文字列も変更されます。

  `try_policy` が `first_exist`（デフォルト）の場合、一覧の最後の項目は `=` を prefix にした数値（例: `=404`）にできます。これは fallback として、そのコードのエラーを発生させます。このエラーは [`handle_errors`](handle_errors) で捕捉して処理できます。

- **policy** は、ファイル一覧の中から選ぶための policy です。

  デフォルト: `first_exist`



<a id="expanded-form"></a>
## 展開形

`try_files` ディレクティブは基本的に次のショートカットです。

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

このディレクティブは matcher token を受け付けないことに注意してください。より複雑な matching logic が必要な場合は、上記の展開形を土台として使ってください。

詳細は [`file` matcher](/docs/caddyfile/matchers#file) を参照してください。



<a id="examples"></a>
## 例

リクエストがどの静的ファイルにも一致しない場合、PHP index/router entrypoint に rewrite します。

```caddy-d
try_files {path} /index.php
```

同じですが、元の path を query 文字列に追加します（一部の legacy PHP app で必要です）。

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

同じですが、directory にも一致させます。

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

存在する場合はファイルまたは directory への rewrite を試み、存在しない場合は 404 エラーを発生させます（これは [`handle_errors`](handle_errors) で捕捉して処理できます）。

```caddy-d
try_files {path} {path}/ =404
```

静的ファイルのうち、もっとも最近 deploy された version を選びます（例: `index.html` がリクエストされたときに `index.be331df.html` を配信する）。

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
