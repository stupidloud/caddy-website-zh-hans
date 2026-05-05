---
title: Caddyfile ディレクティブ
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

<a id="caddyfile-directives"></a>
# Caddyfile ディレクティブ

ディレクティブは、サイトの [block](/docs/caddyfile/concepts#blocks) 内に現れる機能キーワードです。ディレクティブ自身が block を開き、その中に *subdirective* を含めることもありますが、明記されていない限り、ディレクティブを別のディレクティブ内で使うことは**できません**。たとえば、`file_server` block 内で `basic_auth` を使うことはできません。`file_server` は認証の方法を知らないためです。ただし、`handle` や `route` のような特殊なディレクティブ block は HTTP handler ディレクティブをまとめるために設計されているので、その中では一部のディレクティブを使えます。

- [構文](#syntax)
- [ディレクティブ順序](#directive-order)
- [並べ替えアルゴリズム](#sorting-algorithm)

次のディレクティブは Caddy に標準で含まれており、HTTP Caddyfile で使用できます。

<div id="directive-table">

Directive | Description
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | HTTP リクエストを中止します
**[acme_server](/docs/caddyfile/directives/acme_server)** | 組み込み ACME server
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | HTTP Basic Authentication を強制します
**[bind](/docs/caddyfile/directives/bind)** | サーバーの socket address をカスタマイズします
**[encode](/docs/caddyfile/directives/encode)** | レスポンスをエンコードします（通常は圧縮）
**[error](/docs/caddyfile/directives/error)** | エラーを発生させます
**[file_server](/docs/caddyfile/directives/file_server)** | ディスク上のファイルを配信します
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | 認証を外部サービスへ委譲します
**[fs](/docs/caddyfile/directives/fs)** | ファイル I/O に使うファイルシステムを設定します
**[handle](/docs/caddyfile/directives/handle)** | 相互に排他的なディレクティブのグループ
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | エラー処理用の route を定義します
**[handle_path](/docs/caddyfile/directives/handle_path)** | handle と同様ですが、path prefix を取り除きます
**[header](/docs/caddyfile/directives/header)** | レスポンス header を設定または削除します
**[import](/docs/caddyfile/directives/import)** | snippet またはファイルを取り込みます
**[intercept](/docs/caddyfile/directives/intercept)** | 他の handler が書き込んだレスポンスを傍受します
**[invoke](/docs/caddyfile/directives/invoke)** | 名前付き route を呼び出します
**[log](/docs/caddyfile/directives/log)** | アクセス/リクエストログを有効にします
**[log_append](/docs/caddyfile/directives/log_append)** | アクセスログにフィールドを追加します
**[log_skip](/docs/caddyfile/directives/log_skip)** | 一致したリクエストのアクセスログをスキップします
**[log_name](/docs/caddyfile/directives/log_name)** | 書き込み先 logger 名を上書きします
**[map](/docs/caddyfile/directives/map)** | 入力値を 1 つ以上の出力へ対応付けます
**[method](/docs/caddyfile/directives/method)** | 内部的に HTTP method を変更します
**[metrics](/docs/caddyfile/directives/metrics)** | Prometheus metrics 公開エンドポイントを設定します
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | FastCGI 経由で PHP サイトを配信します
**[push](/docs/caddyfile/directives/push)** | HTTP/2 server push を使ってコンテンツをクライアントへ push します
**[redir](/docs/caddyfile/directives/redir)** | クライアントへ HTTP redirect を返します
**[request_body](/docs/caddyfile/directives/request_body)** | リクエスト body を操作します
**[request_header](/docs/caddyfile/directives/request_header)** | リクエスト header を操作します
**[respond](/docs/caddyfile/directives/respond)** | 固定レスポンスをクライアントへ書き込みます
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | 強力で拡張性のある reverse proxy
**[rewrite](/docs/caddyfile/directives/rewrite)** | リクエストを内部的に書き換えます
**[root](/docs/caddyfile/directives/root)** | サイト root の path を設定します
**[route](/docs/caddyfile/directives/route)** | 単一ユニットとして文字どおり扱われるディレクティブのグループ
**[templates](/docs/caddyfile/directives/templates)** | レスポンスに対して template を実行します
**[tls](/docs/caddyfile/directives/tls)** | TLS 設定をカスタマイズします
**[tracing](/docs/caddyfile/directives/tracing)** | OpenTelemetry tracing との連携
**[try_files](/docs/caddyfile/directives/try_files)** | ファイルの存在に依存する rewrite
**[uri](/docs/caddyfile/directives/uri)** | URI を操作します
**[vars](/docs/caddyfile/directives/vars)** | 任意の変数を設定します

</div>

<a id="syntax"></a>
## 構文

各ディレクティブの構文は、おおむね次のような形です。

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

`<carets>` は、実際の値に置き換えられる token を示します。

`[brackets]` は、省略可能なパラメーターを示します。

省略記号 `...` は継続、つまり 1 つ以上のパラメーターまたは行を示します。

subdirective は、`[brackets]` で囲まれていなくても、通常は明記されていない限り省略可能です。


<a id="matchers"></a>
### Matcher

多くのディレクティブは、すべてではありませんが、リクエストを絞り込むための [matcher token](/docs/caddyfile/matchers#syntax) を受け付けます。matcher token は通常、省略可能です。ディレクティブの構文に次のような記述があれば、そのディレクティブは matcher をサポートしています。

```caddy-d
[<matcher>]
```

matcher token はすべて同じ仕組みで動作するため、重複を減らす目的で、各ページでは matcher token のさまざまな指定方法を毎回説明しません。構文の詳しい説明は [matcher ドキュメント](/docs/caddyfile/matchers) を参照してください。


<a id="directive-order"></a>
## ディレクティブ順序

多くのディレクティブは HTTP handler chain を操作します。これらのディレクティブが評価される順序は重要なので、Caddy にはデフォルトの順序がハードコードされています。

この順序は、[`order` グローバルオプション](/docs/caddyfile/options#order) または [`route` ディレクティブ](/docs/caddyfile/directives/route) を使って上書き/カスタマイズできます。

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # reverse_proxy の handle_response block 内のみ
request_body

redir

# 受信リクエストの操作
method
rewrite
uri
try_files

# middleware handlers; 一部はレスポンスをラップします
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# 特殊な routing と dispatching ディレクティブ
invoke
handle
handle_path
route

# 通常、リクエストに応答する handler
abort
error
copy_response # reverse_proxy の handle_response block 内のみ
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## 並べ替えアルゴリズム

使いやすくするため、Caddyfile adapter は次のルールに従ってディレクティブを並べ替えます。

- 名前が異なるディレクティブは、[デフォルト順序](#directive-order)での位置に従って並べ替えられます。デフォルト順序は [`order` グローバルオプション](/docs/caddyfile/options)で上書きできます。plugin のディレクティブには順序がないため、[`order`](/docs/caddyfile/options) グローバルオプションまたは [`route`](/docs/caddyfile/directives/route) ディレクティブを使って順序を設定する必要があります。

- 同じ名前のディレクティブは、その [matcher](/docs/caddyfile/matchers#syntax) に従って並べ替えられます。

  - 最も優先度が高いのは、単一の [path matcher](/docs/caddyfile/matchers#path-matchers) を持つディレクティブです。

    path matcher は、具体性が高いものから低いものへ並べ替えられます。

	一般には、path matcher の長さで並べ替えることで実現されます。ただし例外が 1 つあります。path が `*` で終わり、2 つの matcher の path がそれ以外は同じ場合、`*` がない matcher の方がより具体的と見なされ、上位に並べられます。

    例:
    - `/foobar` は `/foo` より具体的です
    - `/foo` は `/foo*` より具体的です
    - `/foo/*` は `/foo*` より具体的です

  - それ以外の matcher を持つディレクティブは、次に Caddyfile に現れた順で並べ替えられます。

    これには、複数の値を持つ path matcher や [named matcher](/docs/caddyfile/matchers#named-matchers) も含まれます。

  - matcher を持たないディレクティブ（つまり、すべてのリクエストに一致するもの）は最後に並べられます。

- [`vars`](/docs/caddyfile/directives/vars) ディレクティブは、matcher による順序が逆になります。値を設定し、互いに上書きし得るため、最も具体的な matcher を最後に評価する必要があるからです。

- [`route`](/docs/caddyfile/directives/route) ディレクティブの内容は、上記すべてのルールを無視し、内部に書かれたディレクティブの順序を保持します。
