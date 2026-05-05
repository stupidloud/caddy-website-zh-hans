---
title: php_fastcgi (Caddyfile directive)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

php-fpm などの PHP FastCGI サーバーへリクエストを proxy する、意見を持ったディレクティブです。

- [構文](#syntax)
- [展開形](#expanded-form)
  - [説明](#explanation)
- [例](#examples)

Caddy の [`reverse_proxy`](reverse_proxy) は任意の FastCGI アプリケーションを提供できますが、このディレクティブは PHP アプリ専用に調整されています。このディレクティブは便利なショートカットで、[より長い設定](#expanded-form)を置き換えます。

site root にある任意の `index.php` が router として動作することを想定しています。これが望ましくない場合は、[`try_files` subdirective](#try_files) を再設定してデフォルトの rewrite 動作を変更するか、[展開形](#expanded-form)を土台にして必要に応じてカスタマイズしてください。

以下に示す subdirective に加えて、このディレクティブは [`reverse_proxy`](reverse_proxy#syntax) のすべての subdirective もサポートします。たとえば、load balancing や health check を有効にできます。

**ほとんどの現代的な PHP アプリは、追加の subdirective やカスタマイズなしで問題なく動作します。** subdirective は通常、特定の edge case や legacy PHP アプリでのみ使われます。

<a id="syntax"></a>
## 構文

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** は FastCGI サーバーの [addresses](/docs/conventions#network-addresses) です。通常は TCP socket または unix socket file です。

- **root** <span id="root"/> は site の root フォルダーを設定します。`php_fastcgi` と一緒に常に [`root` ディレクティブ](root)を使うことを推奨します。ただし、PHP-FPM upstream が Caddy と異なる root を使っている場合は、これを上書きすると便利です（[例](#docker)を参照）。[`root` ディレクティブ](root)が使われていればその値がデフォルトになり、そうでなければ Caddy の現在の作業ディレクトリがデフォルトになります。

- **split** <span id="split"/> は URI を 2 つの部分に分割するための substring を設定します。最初にマッチした substring が、path から "path info" を分離するために使われます。最初の部分にはマッチした substring が付与され、実際のリソース（CGI script）名とみなされます。2 番目の部分は CGI script が使う PATH_INFO に設定されます。デフォルト: `.php`

- **index** <span id="index"/> は、directory index file として扱う filename を指定します。これは[展開形](#expanded-form)内の file matcher に影響します。デフォルト: `index.php`。マッチするファイルが見つからない場合の `index.php` への rewrite fallback を無効にするには、`off` に設定できます。

- **try_files** <span id="try_files"/> は、デフォルトの try-files rewrite の上書きを指定します。詳細は [`try_files` ディレクティブ](try_files)を参照してください。デフォルト: `{path} {path}/index.php index.php`。

- **env** <span id="env"/> は、追加の環境変数を指定された値に設定します。複数の環境変数を設定するため、複数回指定できます。デフォルトでは、関連する FastCGI 環境変数（HTTP header を含む）はすべてすでに設定されていますが、必要に応じて変数を追加または上書きできます。

- **resolve_root_symlink** <span id="resolve_root_symlink"/> は、[`root`](#root) ディレクトリが symbolic link（symlink）の場合、それを実体の値へ解決します。これは、symlink の向き先を別ディレクトリ内の新しいバージョンへ差し替えるだけのデプロイ戦略で使われることがあります。繰り返しの system call を避けるため、デフォルトでは無効です。

- **capture_stderr** <span id="capture_stderr"/> は、upstream fastcgi server が `stderr` に送ったメッセージを取得して log に記録します。デフォルトでは `WARN` level で記録されます。レスポンスが `4xx` または `5xx` status の場合は、代わりに `ERROR` level が使われます。デフォルトでは `stderr` は無視されます。

- **dial_timeout** <span id="dial_timeout"/> は upstream socket へ接続するときの待機時間を設定する [duration value](/docs/conventions#durations) です。デフォルト: `3s`。

- **read_timeout** <span id="read_timeout"/> は FastCGI upstream から読み取るときの待機時間を設定する [duration value](/docs/conventions#durations) です。デフォルト: timeout なし。

- **write_timeout** <span id="write_timeout"/> は FastCGI upstream へ送信するときの待機時間を設定する [duration value](/docs/conventions#durations) です。デフォルト: timeout なし。


このディレクティブは reverse proxy の意見を持った wrapper なので、カスタマイズには [`reverse_proxy`](reverse_proxy#syntax) の任意の subdirective を使えます。


<a id="expanded-form"></a>
## 展開形

`php_fastcgi` ディレクティブ（subdirective なし）は、次の設定と同じです。ほとんどの現代的な PHP アプリは、このプリセットでうまく動作します。うまく動作しない場合は、`php_fastcgi` ショートカットを使う代わりに、この設定を借りて必要に応じてカスタマイズしてください。

```caddy-d
route {
	# ディレクトリへのリクエストに trailing slash を追加します
	# try_files リストに "{http.request.uri.path}/index.php" が含まれない場合、
	# この redirection は自動的に無効になります
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# リクエストされたファイルが存在しない場合は index file を試し、
	# index.php が常に存在すると仮定します
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# PHP ファイルを FastCGI responder へ proxy します
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
### 説明

- 最初のセクションは、リクエストパスの canonicalization を扱います。目的は、ディスク上のディレクトリを対象とするリクエストについて、リクエストパスに trailing slash `/` が確実に追加されるようにし、そのディレクトリへの有効な URL を 1 つだけにすることです。

  この canonicalization は、`try_files` subdirective に `{path}/index.php`（デフォルト）が含まれている場合にのみ行われます。

  これは、slash で終わって*いない*リクエストだけにマッチし、かつディスク上の `index.php` ファイルを含むディレクトリに対応する request matcher を使って実行されます。マッチした場合は、trailing slash を追加した HTTP 308 redirect を実行します。たとえば、ディスク上に `/foo/index.php` が存在する場合、path `/foo` のリクエストは `/foo/` へ redirect されます（`/` を追加して、ディレクトリへの path を canonicalize します）。

- 次のセクションは、マッチするファイルがディスク上に存在するかどうかに基づく path rewrite を扱います。これは同時に、リクエストパスに `.php` が含まれていた場合、その後ろの path 部分を覚えておく副作用があります。これは、Caddy が FastCGI 環境変数を正しく設定するために重要です。

  - まず、`{path}` がディスク上に存在するファイルかどうかを確認します。存在する場合、その path へ rewrite します。これは以降の処理を実質的に short-circuit し、ディスク上に*存在する*ファイルへのリクエストが別の形に rewrite されないようにします（次の手順を参照）。たとえば、ディスク上に `/js/app.js` ファイルがある場合、その path へのリクエストはそのまま維持されます。

  - 次に、`{path}/index.php` がディスク上に存在するファイルかどうかを確認します。存在する場合、その path へ rewrite します。`/foo/` のようなディレクトリへのリクエストでは `/foo//index.php` を探し（これは `/foo/index.php` に正規化されます）、存在すればリクエストをその path へ rewrite します。この動作は、webroot のサブディレクトリで別の PHP アプリを実行している場合に便利なことがあります。

  - 最後に、常に `index.php` へ rewrite します（現代的な PHP アプリではほぼ常に存在します）。これにより、ディスク上のファイルに対応*しない* path への任意のリクエストを、PHP アプリが entrypoint として `index.php` script で処理できます。

- 最後のセクションは、PHP コードを実際に実行するために、リクエストを PHP FastCGI（または PHP-FPM）サービスへ proxy する部分です。request matcher は `.php` で終わるリクエストだけにマッチするため、PHP script では*なく*、かつディスク上に*存在する*ファイルは、このディレクティブでは処理されず、そのまま fall through します。

`php_fastcgi` ディレクティブだけでは通常十分ではありません。ほとんどの場合、ディスク上のファイルの場所を設定する [`root` ディレクティブ](root)（現代的な PHP アプリでは `/var/www/html/public` のように、`public` ディレクトリが `index.php` を含む場合があります）と、このディレクティブで処理されずに fall through した静的ファイル（JS、CSS、画像など）を提供する [`file_server` ディレクティブ](file_server)を組み合わせる必要があります。



<a id="examples"></a>
## 例

`127.0.0.1:9000` で待ち受けている FastCGI responder へ、すべての PHP リクエストを proxy します。

```caddy-d
php_fastcgi 127.0.0.1:9000
```

同じですが、`/blog/` 配下のリクエストだけを対象にします。

```caddy-d
php_fastcgi /blog/* localhost:9000
```

unix socket 経由で待ち受ける PHP-FPM を使う場合。

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

PHP script を含むディレクトリを指定するために [`root` ディレクティブ](root)を、静的ファイルを提供するために [`file_server` ディレクティブ](file_server)を使うのがほぼ常です。

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Caddy で複数の PHP アプリを提供する場合、各アプリの webroot は別々でなければなりません。そうすることで、Caddy が静的ファイルを個別に読み取って提供し、PHP ファイルが存在するか検出できます。

Docker を使っている場合、PHP-FPM container では同じ root にファイルが mount されていることがよくあります。その場合の解決策は、Caddy container にはファイルを別々のディレクトリへ mount し、各 container の root を設定するために [`root` subdirective](#root) を使うことです。

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

`index.php` を entrypoint として使わない PHP site では、代わりに `404` error を発生させるよう fallback できます。その error は [`handle_errors` ディレクティブ](handle_errors)で捕捉して処理できます。

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
