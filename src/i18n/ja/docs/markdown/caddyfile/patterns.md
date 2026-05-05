---
title: "よく使われる Caddyfile パターン"
---

<a id="common-caddyfile-patterns"></a>
# よく使われる Caddyfile パターン

このページでは、よくあるユースケース向けに、完全で最小限の Caddyfile 設定例をいくつか示します。自分の Caddyfile を作るときの出発点として役立ちます。

これらはそのまま貼り付けて使うための解決策ではありません。ドメイン名、ポートや socket、ディレクトリパスなどは自分の環境に合わせて変更する必要があります。ここでの目的は、特によく使われる設定パターンを示すことです。

- [静的ファイルサーバー](#static-file-server)
- [Reverse proxy](#reverse-proxy)
- [PHP](#php)
- [`www.` サブドメインのリダイレクト](#redirect-www-subdomain)
- [末尾スラッシュ](#trailing-slashes)
- [ワイルドカード証明書](#wildcard-certificates)
- [Single-page apps (SPAs)](#single-page-apps-spas)
- [別の Caddy へ proxy する Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## 静的ファイルサーバー

```caddy
example.com {
	root /var/www
	file_server
}
```

通常どおり、最初の行はサイトアドレスです。[`root` directive](/docs/caddyfile/directives/root) はサイト root のパスを指定します（`*` はすべてのリクエストに match することを意味し、[path matcher](/docs/caddyfile/matchers#path-matchers) と区別するために使います）&mdash;現在の作業ディレクトリでない場合は、自分のサイトに合わせてパスを変更してください。最後に、[static file server](/docs/caddyfile/directives/file_server) を有効にします。



<a id="reverse-proxy"></a>
## Reverse proxy

すべてのリクエストを proxy します。

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

`/api/` で始まる path のリクエストだけを proxy し、それ以外は静的ファイルとして配信します。

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

これは [request matcher](/docs/caddyfile/matchers#syntax) を使って、`/api/` で始まるリクエストだけに match させ、それらを backend へ proxy します。それ以外のリクエストは、サイトの [`root`](/docs/caddyfile/directives/root) から [static file server](/docs/caddyfile/directives/file_server) で配信されます。また、これは `reverse_proxy` が [directive order](/docs/caddyfile/directives#directive-order) 上で `file_server` より高い位置にあることにも依存しています。

さらに多くの [`reverse_proxy` の例はこちら](/docs/caddyfile/directives/reverse_proxy#examples)にあります。



<a id="php"></a>
## PHP

<a id="php-fpm"></a>
### PHP-FPM

PHP FastCGI サービスが動作している場合、ほとんどのモダンな PHP アプリでは次のような設定が使えます。

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

サイト root は適宜変更してください。この例では、PHP アプリの webroot が `public` ディレクトリ内にあると仮定しています&mdash;ディスク上に存在するファイルへのリクエストは [`file_server`](/docs/caddyfile/directives/file_server) で配信され、それ以外は PHP アプリで処理するため `index.php` へ route されます。

PHP-FPM へ接続するために unix socket を使うこともあります。

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`php_fastcgi` directive](/docs/caddyfile/directives/php_fastcgi) は、実際には[いくつかの設定](/docs/caddyfile/directives/php_fastcgi#expanded-form)へのショートカットです。


<a id="frankenphp"></a>
### FrankenPHP

別の選択肢として、[FrankenPHP](https://frankenphp.dev/) を使うこともできます。これは CGO（Go to C bindings）で PHP を直接呼び出す Caddy ディストリビューションです。PHP-FPM より最大 4 倍高速になることがあり、worker mode を使える場合はさらに効果的です。

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-www-subdomain"></a>
## `www.` サブドメインのリダイレクト

HTTP リダイレクトで `www.` サブドメインを**追加**するには:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


**削除**するには:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


**複数ドメイン**でまとめて削除するには、`{labels.*}` placeholder を使います。これはホスト名の各部分で、右から `0` 始まりで番号が付きます（例: `0`=`com`, `1`=`example-one`, `2`=`www`）。

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## 末尾スラッシュ

通常、自分でこれを設定する必要はありません。[`file_server` directive](/docs/caddyfile/directives/file_server) は、要求されたリソースがディレクトリかファイルかに応じて、HTTP リダイレクトによりリクエストの末尾スラッシュを自動的に追加または削除します。

ただし必要であれば、設定で末尾スラッシュを強制できます。方法は 2 つあります。内部的に行う方法と、外部的に行う方法です。

<a id="internal-enforcement"></a>
### 内部的な強制

これは [`rewrite`](/docs/caddyfile/directives/rewrite) directive を使います。Caddy は URI を内部的に rewrite して、末尾スラッシュを追加または削除します。

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

rewrite を使う場合、末尾スラッシュがあるリクエストとないリクエストは同じものとして扱われます。


<a id="external-enforcement"></a>
### 外部的な強制

これは [`redir`](/docs/caddyfile/directives/redir) directive を使います。Caddy はブラウザに対し、URI を変更して末尾スラッシュを追加または削除するよう要求します。

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

redirect を使う場合、クライアントはリクエストを再送する必要があり、そのリソースに対して受け入れられる URI を 1 つに強制できます。



<a id="wildcard-certificates"></a>
## ワイルドカード証明書

Let's Encrypt を含むほとんどの issuer では、Caddy にワイルドカード証明書を自動化させるには [ACME DNS challenge](/docs/automatic-https#dns-challenge) を有効にする必要があります。

DNS challenge が有効な場合、Caddy 2.10 以降では、サブドメイン用に別個の証明書を管理する前に、すでに設定または管理されている適用可能なワイルドカード証明書を優先します。



同じワイルドカード証明書で複数のサブドメインを配信する必要がある場合は、[`handle` directive](/docs/caddyfile/directives/handle) と [`host` matchers](/docs/caddyfile/matchers#host) を使い、次のような Caddyfile にするのが最も扱いやすい方法です。

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# それ以外の未処理ドメインの fallback
	handle {
		abort
	}
}
```

Caddy にワイルドカード証明書を自動管理させるには、[ACME DNS challenge](/docs/automatic-https#dns-challenge) を有効にする必要があります。



<a id="single-page-apps-spas"></a>
## Single-page apps (SPAs)

Web ページが自前で routing を行う場合、サーバー側には存在しないページへのリクエストが多数届くことがあります。しかし、単一の index ファイルを代わりに配信すれば、クライアント側で描画できます。このような構成の Web アプリケーションは SPA、つまり single-page app と呼ばれます。

基本的な考え方は、要求されたファイルがサーバー側に存在するかを "try files" で確認し、存在しなければ、クライアントが routing を行う index ファイル（通常はクライアント側 JavaScript）へ fallback することです。

典型的な SPA 設定は、通常次のようになります。

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

SPA が API やその他のサーバー側専用 endpoint と組み合わさっている場合は、それらを排他的に扱うため `handle` ブロックを使うとよいでしょう。

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

`index.html` が hash 付きファイル名の JS/CSS アセットを参照している場合、クライアントにそれを cache *しない* よう指示するため、`Cache-Control` header の追加を検討するとよいでしょう（アセットが変わったときにブラウザが新しいものを取得できるためです）。`try_files` rewrite は、ディスク上の他のファイルに match しない任意の path から `index.html` を配信するために使われるので、`try_files` を `route` で囲むと、`header` handler を rewrite の*後*に実行できます（通常は [directive order](/docs/caddyfile/directives#directive-order) により前に実行されます）。

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## 別の Caddy へ proxy する Caddy

公開アクセス可能な Caddy インスタンス（ここでは "front" と呼びます）と、プライベートネットワーク内で実際のアプリを配信する別の Caddy インスタンス（ここでは "back" と呼びます）がある場合、[`reverse_proxy` directive](/docs/caddyfile/directives/reverse_proxy) を使ってリクエストを通過させられます。

Front インスタンス:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Back インスタンス:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- この例では 2 つの異なるドメインを配信し、どちらも同じ back Caddy インスタンスのポート `80` へ proxy しています。back インスタンスは 2 つのドメインを別々の方法で配信するため、2 つの独立した site block として設定されています。

- back 側では、ポート `80` の HTTP を受け付けるために [`http://`](/docs/caddyfile/concepts#addresses) を使っています。front インスタンスが TLS を終端し、front と back の間の通信はプライベートネットワーク上なので、再暗号化する必要はありません。

- 必要であれば、back インスタンスで `8080` のような別ポートを使えます。その場合は back 側設定の各サイトアドレスに `:8080` を追加するか、[`http_port` global option](/docs/caddyfile/options#http_port) を `8080` に設定します。

- back 側では、[`trusted_proxies` global option](/docs/caddyfile/options#trusted_proxies) を使って、front インスタンスを proxy として信頼するよう Caddy に伝えます。これにより、実際のクライアント IP が保持されます。

- さらに進めるなら、複数の back インスタンスを用意して、それらの間で [load balance](/docs/caddyfile/directives/reverse_proxy#load-balancing) できます。front インスタンスの [`acme_server`](/docs/caddyfile/directives/acme_server) を使って mTLS（mutual TLS）を構成し、front インスタンスを back インスタンスの CA のように動作させることもできます（front と back の間の通信が信頼できないネットワークを通る場合に有用です）。
