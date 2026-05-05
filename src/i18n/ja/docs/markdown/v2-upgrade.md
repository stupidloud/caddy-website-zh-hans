---
title: Caddy 2 へのアップグレード
---

<a id="upgrade-guide"></a>
アップグレードガイド
=============

Caddy 2 は、Caddy 1 を改善するために一から書き直された、まったく新しい code base です。Caddy 2 は Caddy 1 と後方互換ではありません。ただし心配はいりません。ほとんどの基本的な構成では、大きな違いはありません。このガイドは、できるだけ簡単に移行できるようにするためのものです。

このガイドでは、利用できる新機能には踏み込みません。新機能は本当に便利なので、ぜひ[学んでください](/docs/getting-started)。ここでの目的は、Caddy 2 を素早く動かせるようにすることだけです。

- [重要なポイント](#high-order-bits)
- [手順](#steps)
- [HTTPS と port](#https-and-ports)
- [Command line](#command-line)
- [Caddyfile](#caddyfile)
	- [主な変更点](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [Service file](#service-files)
- [Plugins](#plugins)
- [ヘルプを得る](#getting-help)



<a id="high-order-bits"></a>
## 重要なポイント

- "Caddy 2" は、今でも単に `caddy` と呼ばれます。移行時の混乱を減らすため、どの version を指すかを明確にしたい場合に "Caddy 2" と書くことがあります。
- ほとんどのユーザーは、`caddy` binary と、更新した `Caddyfile` config（動作確認後）を置き換えるだけで済みます。
- Caddy 1 からの前提を持ち込まずに Caddy 2 に向き合うのが最善かもしれません。
- ニッチな v1 設定を v2 で完全に再現できない場合があります。通常、それには妥当な理由があります。
- command line は server configuration には使われなくなりました。
- 設定のために環境変数は不要になりました。
- Caddy 2 に設定を渡す主な方法は [API](/docs/api) ですが、[`caddy` command](/docs/command-line) も使用できます。
- Caddy 2 のネイティブ設定言語は [JSON](/docs/json/) であり、Caddyfile は JSON へ変換するためのもう 1 つの [config adapter](/docs/config-adapters) にすぎない、という点を理解しておいてください。非常に独自性の高い/高度なユースケースでは、JSON が必要になる場合があります。あらゆる設定を Caddyfile で表現できるわけではないためです。
- Caddyfile は大部分で同じですが、はるかに強力にもなっています。ディレクティブは変更されています。



<a id="steps"></a>
## 手順

1. [Getting Started](/docs/getting-started) チュートリアルを実施して、Caddy 2 に慣れてください。
2. まだなら手順 1 を行ってください。本当に重要です。少なくとも Caddy 2 の使い方を知ることがどれだけ重要か、強調しすぎることはありません。（その方が楽しいです。）
3. 下のガイドを使って、`caddy` command を移行してください。
4. 下のガイドを使って、Caddyfile を移行してください。
5. 新しい config をローカルまたは staging でテストしてください。
6. テストし、もう一度テストし、さらにテストしてください。
7. デプロイして楽しんでください。



<a id="https-and-ports"></a>
## HTTPS と port

Caddy のデフォルト port は `:2015` ではなくなりました。Caddy 2 のデフォルト port は `:443`、または hostname/IP が分からない場合は port `:80` です。port はいつでも config 内でカスタマイズできます。

Caddy 2 のデフォルト protocol は、hostname または IP が分かっている場合、[*常に* HTTPS](/docs/automatic-https#overview) です。これは、公開 domain のように見えるものだけがデフォルトで HTTPS だった Caddy 1 とは異なります。現在は、（port `:80` または `http://` を明示して無効にしない限り）*すべての* site が HTTPS を使います。

IP address と localhost domain には、[ローカルで信頼される組み込み CA](/docs/automatic-https#local-https) から certificate が発行されます。その他すべての domain は ZeroSSL または Let's Encrypt を使います。（これはすべて設定可能です。）

certificate と ACME resource の storage 構造は変更されています。Caddy 2 はおそらく site 用に新しい certificate を取得します。ただし certificate が大量にある場合、自動で移行されないなら手動で移行できます。詳細は issue [#2955](https://github.com/caddyserver/caddy/issues/2955) と [#3124](https://github.com/caddyserver/caddy/issues/3124) を参照してください。



<a id="command-line"></a>
## Command line

`caddy` command は `caddy run` になりました。

すべての command line flag は異なります。削除してください。server config はすべて実際の config document（通常は Caddyfile または JSON）の中に存在するようになりました。v1 の command line flag の多くを置き換えるには、[JSON structure](/docs/json/) または [Caddyfile global options](/docs/caddyfile/options) の中に必要なものが見つかるはずです。

`caddy -conf ../Caddyfile` のような command は、`caddy run --config ../Caddyfile` になります。

以前と同様に、Caddyfile が現在の folder にある場合、Caddy は自動的にそれを見つけて使用します。その場合は `--config` flag を使う必要はありません。

signal はほぼ同じですが、USR1 と USR2 はサポートされなくなりました。新しい設定を読み込むには、代わりに [`caddy reload`](/docs/command-line#caddy-reload) command または [API](/docs/api) を使ってください。

以前は、config なしで `caddy` を実行すると単純な file server が起動しました。Caddy 2 での同等機能は [`caddy file-server`](/docs/command-line#caddy-file-server) です。

環境変数は、`HOME`（および任意で設定した `XDG_*` 変数）を除いて、もはや関係ありません。`CADDYPATH` は [OS conventions に置き換えられました](/docs/conventions#file-locations)。



<a id="caddyfile"></a>
## Caddyfile

[v2 Caddyfile](/docs/caddyfile/concepts) は、既に慣れているものと非常によく似ています。主に必要なのは、ディレクティブを変更することです。

⚠️ **新しいディレクティブを必ず読み込んでください。** 特に設定が高度な場合、考慮すべき細かい違いが多数あります。これらの tip により、多くの場合はすばやく移行できますが、upgrade の影響を理解するために各ディレクティブの完全なドキュメントを読んでください。そしてもちろん、本番環境に投入する前に config を十分にテストしてください。


<a id="primary-changes"></a>
### 主な変更点

- static file を配信する場合、[`file_server` ディレクティブ](/docs/caddyfile/directives/file_server)を追加する必要があります。Caddy 2 はこれをデフォルトで仮定しないためです。セキュリティ上の理由から、Caddy 2 はデフォルトで MIME sniff もしません。Content-Type がない場合、[header](/docs/caddyfile/directives/header) ディレクティブを使って自分で header を設定する必要があるかもしれません。

- v1 では、ディレクティブをリクエスト path でしか filter（または "match"）できませんでした。v2 では、[request matching](/docs/caddyfile/matchers) がはるかに強力です。HTTP handler chain に middleware を追加する v2 ディレクティブや、HTTP リクエスト/レスポンスを何らかの形で操作するディレクティブは、この新しい matching 機能を活用します。[v2 request matcher について詳しく読む。](/docs/caddyfile/matchers) v2 Caddyfile を理解するには、これらを知る必要があります。

- 多くの [placeholder](/docs/conventions#placeholders) は同じですが、多くは変更され、[多数の新しいもの](/docs/modules/http#docs)も追加されています。[Caddyfile 用の shorthand](/docs/caddyfile/concepts#placeholders)も含まれます。

- Caddy 2 の log はすべて structured log で、デフォルト形式は JSON です。すべての log level は同じ log に流して処理できます（必要ならカスタマイズできます）。

- Caddy 1 で path prefix によってリクエストを match していた箇所では、Caddy 2 の path matching はデフォルトで exact です。`/foo/` のような prefix に match させたい場合、Caddy 2 では `/foo/*` が必要です。

ここでは、最も一般的な v1 ディレクティブをいくつか挙げ、v2 Caddyfile で使うための変換方法を説明します。

⚠️ **v1 ディレクティブがこのページにないからといって、v2 で実現できないという意味ではありません。** 一部の v1 ディレクティブは不要になったり、うまく対応しなかったり、v2 では別の方法で満たされたりします。高度なカスタマイズでは、目的を達成するために JSON へ降りる必要があるかもしれません。必要なものを見つけるには、[ドキュメント](/docs/caddyfile)を確認してください。


<a id="basicauth"></a>
### basicauth

HTTP Basic Authentication は、引き続き [`basic_auth`](/docs/caddyfile/directives/basic_auth) ディレクティブで設定します。ただし、Caddy 2 の設定は plaintext password を受け付けません。hash 化する必要があり、[`caddy hash-password`](/docs/command-line#caddy-hash-password) が役に立ちます。

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


<a id="browse"></a>
### browse

file browsing は、[`file_server`](/docs/caddyfile/directives/file_server) ディレクティブで有効にします。

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


<a id="errors"></a>
### errors

custom error page は [`handle_errors`](/docs/caddyfile/directives/handle_errors) で実現できます。


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

<a id="ext"></a>
### ext

暗黙の file extension は [`try_files`](/docs/caddyfile/directives/try_files) で実現できます。

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


<a id="fastcgi"></a>
### fastcgi

PHP を配信している前提では、v2 の同等機能は [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) です。

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

v1 の `fastcgi` ディレクティブは、裏側で多くの処理をしていたことに注意してください。ディスク上の file を試す、リクエストを書き換える、redirect する、といった処理も含まれていました。v2 の `php_fastcgi` ディレクティブもこれらを自動で行いますが、要件が異なる場合に変更できる [expanded form](/docs/caddyfile/directives/php_fastcgi#expanded-form) がドキュメントに示されています。

v2 では `php` preset は不要です。`php_fastcgi` ディレクティブはデフォルトで PHP を前提にするためです。`php_fastcgi 127.0.0.1:9000 php` のような行を書くと、reverse proxy は `php` という 2 つ目の backend があると判断し、connection error につながります。

subdirective は v2 では異なります。PHP では、おそらく何も必要ありません。


<a id="gzip"></a>
### gzip

複数の compression format を含むすべての response encoding には、単一の [`encode`](/docs/caddyfile/directives/encode) ディレクティブを使うようになりました。

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

補足: Caddy 2 は `zstd` もサポートしています（ただし、まだ browser はサポートしていません）。


<a id="header"></a>
### header

[ほぼ変更ありません](/docs/caddyfile/directives/header)が、v2 では substring replacement ができるため、はるかに強力になっています。

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


<a id="log"></a>
### log

access logging を有効にします。[`log`](/docs/caddyfile/directives/log) ディレクティブは v2 でも使用できますが、すべての log は structured で、デフォルトでは JSON として encode されます。

access logging を有効にする推奨方法は単純に次のとおりです。

```caddy-d
log
```

これは structured log を stderr に出力します。（file や network socket に出力することもできます。詳しくは [`log`](/docs/caddyfile/directives/log) ディレクティブのドキュメントを参照してください。）

デフォルトでは、log は [structured](/docs/logging) JSON 形式になります。legacy の理由で Common Log Format (CLF) の log が必要な場合は、[`transform-encoder`](https://github.com/caddyserver/transform-encoder) plugin を使えます。


<a id="proxy"></a>
### proxy

v2 の同等機能は [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) です。

注目すべき subdirective の変更として、`header_upstream` と `header_downstream` はそれぞれ `header_up` と `header_down` になりました。また、load balancing 関連の subdirective には `lb_` prefix が付きます。

もう 1 つの重要な違いは、v2 proxy はデフォルトですべての incoming header をそのまま渡し（`Host` header を含む）、`X-Forwarded-For` header を設定することです。言い換えると、v1 の "transparent" mode は v2 では基本的にデフォルトです（ただし X-Real-IP など他の header が必要なら自分で設定する必要があります）。`header_up` subdirective を使って `Host` header を上書き/カスタマイズすることもできます。

Websocket proxying は v2 では「そのまま動きます」。v1 のように websocket を「有効化」する必要はありません。

`without` subdirective は削除されました。v2 では matcher support が改善されたため、[rewrite hack](#rewrite) が不要になったからです。

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


<a id="redir"></a>
### redir

[変更ありません](/docs/caddyfile/directives/redir)。ただし、省略可能な status code argument に関する細部がいくつか変わっています。ほとんどの config では変更不要です。

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


<a id="rewrite"></a>
### rewrite

request rewriting（"internal redirecting"）の semantics は少し変わりました。v1 で単純な path prefix 以外のものに基づいてリクエストを match させる手段として、いわゆる "rewrite hack" を使っていた場合、v2 では完全に不要です。

[新しい `rewrite` ディレクティブ](/docs/caddyfile/directives/rewrite) は非常にシンプルですが、とても強力です。複雑さの大半は v2 の [matcher](/docs/caddyfile/matchers) が扱うためです。

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Caddy 2 の通常の [matcher token](/docs/caddyfile/matchers) を使っているだけである点に注目してください。このディレクティブ専用の特別扱いではなくなりました。

まず、すべての rewrite hack を削除し、代わりに [named matcher](/docs/caddyfile/concepts#named-matchers) へ変換してください。各 v1 `rewrite` を評価し、v2 でも本当に必要か確認してください。ヒント: v1 Caddyfile が `rewrite` で path prefix を追加し、その後 `proxy` の `without` で同じ prefix を削除している場合、それは rewrite hack であり、取り除けます。

高度な routing logic をより細かく制御したい場合は、新しい [`route`](/docs/caddyfile/directives/route) ディレクティブや [`handle`](/docs/caddyfile/directives/handle) ディレクティブが役に立つかもしれません。


<a id="root"></a>
### root

[変更ありません](/docs/caddyfile/directives/root)。

static file を配信する場合は、[`file_server` ディレクティブ](/docs/caddyfile/directives/file_server)を追加することを忘れないでください。Caddy 2 はこれをデフォルトで仮定しません。一方、v1 では常に有効でした。


<a id="status"></a>
### status

v2 の同等機能は [`respond`](/docs/caddyfile/directives/respond) で、response body も書き込めます。

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


<a id="templates"></a>
### templates

[`templates`](/docs/caddyfile/directives/templates) ディレクティブ全体の構文は変わりませんが、実際の template action/function は異なり、大きく改善されています。たとえば、template は file の include、markdown の render、internal sub-request、front matter の parse などを実行できます。

新しい function の詳細は[ドキュメント](/docs/modules/http.handlers.templates)を参照してください。

- **v1:** `templates`
- **v2:** `templates`


<a id="tls"></a>
### tls

[`tls`](/docs/caddyfile/directives/tls) ディレクティブの基本は変わっていません。たとえば、自分の cert と key を指定する場合は次のとおりです。

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

ただし、Caddy の [auto-HTTPS logic](/docs/automatic-https) は*変更されています*。その点に注意してください。

cipher suite 名も変更されています。

Caddy 2 でよくある設定の 1 つは、`localhost` でも IP address でもない開発用 hostname に対してローカルで信頼される certificate を配信するために、`tls internal` を使うことです。

ほとんどの site では、このディレクティブはまったく必要ありません。


<a id="service-files"></a>
## Service file

Caddy deployment には、[公式 systemd service file のいずれか](/docs/running#linux-service)を使うことを推奨します。

custom service file が必要な場合は、公式のものをベースにしてください。これらは、正当な理由に基づいて注意深く調整されています。必要に応じて必ず自分用にカスタマイズしてください。


<a id="plugins"></a>
## Plugins

v1 用に書かれた plugin は、v2 と自動的に互換になるわけではありません。多くの v1 plugin は v2 ではそもそも不要です。一方で、v2 は v1 よりもはるかに簡単に拡張でき、柔軟です。

Caddy 2 用の plugin を書きたい場合は、[Caddy module の書き方を学んでください](/docs/extending-caddy)。


<a id="building-caddy-2-with-plugins"></a>
### plugin 付きで Caddy 2 をビルドする

Caddy 2 は、[interactive download page](/download) から plugin 付きでダウンロードできます。あるいは、`xcaddy` を使って [Caddy を自分で build](/docs/build) し、含める plugin を選べます。`xcaddy` は Caddy の [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) file にある手順を自動化します。


<a id="getting-help"></a>
## ヘルプを得る

Caddy を動かすのに苦戦している場合は、まず Web サイトのドキュメントを確認してください。新しいことを試し、何が起きているのか理解する時間を取ってください。v2 は多くの点で v1 と大きく異なります（ただし、同時にとても馴染みやすくもあります）。

それでも支援が必要な場合は、ぜひ[コミュニティ](https://caddy.community)に参加してください。他の人を助けることが、自分自身を助ける最善の方法になることもあります。
