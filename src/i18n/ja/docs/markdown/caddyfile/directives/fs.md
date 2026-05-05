---
title: fs (Caddyfile directive)
---

# fs

ファイル I/O の実行に使うファイルシステムを設定します。

これにより、クラウド上で動作するリモートファイルシステム、ファイルのような interface を持つデータベース、または Caddy binary に埋め込まれたファイルからの読み取りにも接続できます。

まず [`filesystem` global option](/docs/caddyfile/options#filesystem) を使ってファイルシステム名を宣言する必要があります。その後、この directive を使って使用するファイルシステムを指定できます。

この directive は、静的ファイルを提供するために [`file_server` directive](file_server) と組み合わせて使われることが多く、ファイルの存在に基づいて rewrite を行うために [`try_files` directive](try_files) と組み合わせることもあります。通常は、ファイルシステム内の root path を設定するために [`root` directive](root) とも併用されます。


<a id="syntax"></a>
## 構文

```caddy-d
fs [<matcher>] <filesystem>
```

<a id="examples"></a>
## 例

`foo` という名前のファイルシステムを使います。これは、認証が必要かもしれない `custom` という架空の module を使っています。

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

`foo` ファイルシステムからは画像だけを提供し、それ以外はデフォルトファイルシステムから提供します。

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
