---
title: root (Caddyfile directive)
---

# root

file system にアクセスする各種 matcher やディレクティブで使われる、site の root path を設定します。未設定の場合、デフォルトの site root は現在の working directory です。

具体的には、このディレクティブは `{http.vars.root}` placeholder を設定します。同じブロック内の他の `root` ディレクティブとは相互排他的です。そのため、交差する matcher を持つ複数の root を定義しても、cascade して互いを上書きすることはありません。

このディレクティブは静的ファイル配信を自動的には有効にしないため、多くの場合 [`file_server` ディレクティブ](file_server)または [`php_fastcgi` ディレクティブ](php_fastcgi)と組み合わせて使います。


<a id="syntax"></a>
## 構文

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** は site root として使う path です。

v2.8.0 より前では、`<path>` 引数が `/` で始まる場合、parser が [matcher token](/docs/caddyfile/matchers#syntax) と混同する可能性があったため、ワイルドカード matcher token（`*`）を指定する必要がありました。


<a id="examples"></a>
## 例

site root を `/home/bob/public_html` に設定します（Caddy が `bob` ユーザーとして実行されている前提）。

<aside class="tip">

Caddy を systemd service として実行している場合、`/home` からファイルを読み取ることはできません。これは `caddy` ユーザーに `/home` ディレクトリの「実行」権限（traversal に必要）がないためです。代わりに `/srv` または `/var/www/html` にファイルを置くことを推奨します。

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

v2.8.0 より前では、最初の引数が [path matcher](/docs/caddyfile/matchers#path-matchers) と曖昧になるため、ここでは [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers) が必要でした。つまり `root * /srv` のように書く必要がありましたが、現在は `root /srv` に簡略化できます。

</aside>


すべてのリクエストについて、site root を `public_html`（現在の working directory からの相対 path）に設定します。

```caddy-d
root public_html
```

`/foo/*` のリクエストだけ site root を変更します。

```caddy-d
root /foo/* /home/user/public_html/foo
```

`root` ディレクティブは、静的ファイルを配信するために [`file_server`](file_server) と、または PHP site を配信するために [`php_fastcgi`](php_fastcgi) と組み合わせてよく使われます。

```caddy
example.com {
	root /srv
	file_server
}
```
