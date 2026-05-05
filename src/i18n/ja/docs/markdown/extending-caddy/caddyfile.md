---
title: "Caddyfile Support"
---

<a id="caddyfile-support"></a>
# Caddyfile Support

Caddy module は、[登録](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule)されると、その namespace によって [native JSON config](/docs/json/) へ自動的に追加され、利用可能かつドキュメント化された状態になります。そのため Caddyfile support は完全に任意ですが、Caddyfile を好むユーザーからはよく求められます。

<a id="unmarshaler"></a>
## Unmarshaler

自分の module に Caddyfile support を追加するには、[`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler) インターフェイスを実装するだけです。token をどのように parse するかによって、その module の Caddyfile 構文を自由に決められます。

unmarshaler の仕事は、渡された [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) を使って、たとえばフィールドへ値を入れるなど、module の型をセットアップすることだけです。たとえば `Gizmo` という module type には、次のようなメソッドを持たせられます。

```go
// UnmarshalCaddyfile implements caddyfile.Unmarshaler. Syntax:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // directive 名を消費

	if !d.Args(&g.Name) {
		// 引数が足りない
		return d.ArgErr()
	}
	if d.NextArg() {
		// 任意の引数
		g.Option = d.Val()
	}
	if d.NextArg() {
		// 引数が多すぎる
		return d.ArgErr()
	}

	return nil
}
```

構文は、そのメソッドの godoc comment に書いておくとよいでしょう。Caddyfile の parse について詳しくは、[`caddyfile` package の godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc) を参照してください。

directive 名の token は、単純な `d.Next()` 呼び出しで消費またはスキップできます。

不足している引数や余分な引数は、必ず `d.NextArg()` または `d.RemainingArgs()` で確認してください。単純な「不正なケース」メッセージには `d.ArgErr()` を使い、問題の説明（できれば推奨される解決策も含む）を添えた役立つエラーメッセージを作るには `d.Errf("some message")` を使います。

インターフェイスが正しく満たされていることを保証するため、[interface guard](/docs/extending-caddy#interface-guards) も追加してください。

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### Blocks

1 行に収まらない量の設定を受け付けたい場合は、subdirective を持つ block を許可するとよいでしょう。これは `d.NextBlock()` を使い、元の nesting level に戻るまで反復することで実現できます。

```go
for nesting := d.Nesting(); d.NextBlock(nesting); {
	switch d.Val() {
		case "sub_directive_1":
		// ...
		case "sub_directive_2":
		// ...
	}
}
```

loop の各 iteration が segment（line または block）全体を消費する限り、これは block を扱う上品な方法です。

<a id="http-directives"></a>
## HTTP Directives

HTTP Caddyfile は、Caddy の既定の Caddyfile adapter 構文（または "server type"）です。これは拡張可能で、自分の module 向けに独自の "top-level" directive を[登録](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective)できます。

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

directive が単一の HTTP handler だけを返す場合（よくあるケースです）は、[`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) の方が使いやすいかもしれません。

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

基本的な考え方は、directive に関連付ける [parse function](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) が、1 つ以上の [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue) 値を返す、というものです。（または `RegisterHandlerDirective` を使う場合は、値を入れ終えた `caddyhttp.MiddlewareHandler` 値を直接返します。）各 config value は ["class"](#classes) に関連付けられます。class は、HTTP Caddyfile adapter が最終的な JSON 設定のどの部分でその値を使えるかを判断する助けになります。すべての config value は一箇所に集められ、adapter は最終的な JSON 設定を構築するときにそこから取り出します。

この設計により、directive は認識済みの任意の class に対して任意の config value を返せます。つまり、HTTP Caddyfile adapter が専用 class を持つ設定のどの部分にも影響を与えられます。

すでに `UnmarshalCaddyfile()` メソッドを実装しているなら、parse function は次のように単純にできます。

```go
// parseCaddyfileHandler unmarshals tokens from h into a new middleware handler value.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

`httpcaddyfile.Helper` 型の使い方について詳しくは、[`httpcaddyfile` package godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc) を参照してください。

<a id="handler-order"></a>
### Handler order

HTTP middleware/handler 値を返すすべての directive は、正しい順序で評価される必要があります。たとえば、サイトの root directory を設定する handler は、その root directory にアクセスする handler より前に実行されなければなりません。そうしないと、directory path が分からないためです。

HTTP Caddyfile には、[標準 directive 用のハードコードされた順序](/docs/caddyfile/directives#directive-order)があります。これにより、ユーザーは web server の最も一般的な機能の実装詳細を知る必要がなくなり、正しい設定を書きやすくなります。また、単一のハードコードされたリストは、Caddyfile の拡張可能な性質に由来する非決定性も防ぎます。

**新しい handler directive を登録した場合、（`route` block の外で）使えるようにするには、先にそのリストへ追加する必要があります。** これは次の 3 つの方法のいずれかで行います。

- （推奨）Plugin 作者は directive を登録した後、`init()` の中で [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) を呼び出し、別の[標準 directive](/docs/caddyfile/directives#directive-order) に対する相対位置として directive を order に挿入できます。これにより、ユーザーは追加設定なしで自分の site からその directive を直接使えます。たとえば、`gizmo` directive を `header` handler の後で評価されるように挿入するには、次のようにします。

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- ユーザーは [`order` global option](/docs/caddyfile/options) を追加して、自分の Caddyfile の標準順序を変更できます。例: `order gizmo before respond` は、新しい directive `gizmo` を `respond` handler より前に評価されるよう挿入します。その後、その directive は通常どおり使えます。

- ユーザーは directive を [`route` block](/docs/caddyfile/directives/route) の中に置けます。route block 内の directive は並べ替えられないため、route block で使う directive はリストに載っている必要がありません。

後者 2 つの選択肢のどちらかを選ぶ場合は、ユーザーが正しく使えるよう、あなたの directive はリスト内のどこに order されるべきかについて推奨事項をドキュメント化してください。

<a id="classes"></a>
### Classes

この表は、HTTP Caddyfile adapter が認識する、exported type を持つ各 class を説明します。

Class name | Expected type | 説明
---------- | ------------- | -----------
bind | `[]string` | Server listener bind address
route | `caddyhttp.Route` | HTTP handler route
error_route | `*caddyhttp.Subroute` | HTTP error handling route
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS connection policy
tls.cert_issuer | `certmagic.Issuer` | TLS certificate issuer
tls.cert_loader | `caddytls.CertificateLoader` | TLS certificate loader

<a id="server-types"></a>
## Server Types

構造的には、Caddyfile は単純な形式です。そのため、異なるニーズに合うよう、さまざまな種類の Caddyfile 形式（"server type" と呼ばれることもあります）を持てます。

既定の Caddyfile 形式は HTTP Caddyfile で、おそらくあなたもよく知っているものです。この形式は主に [`http` app](/docs/modules/http) を設定しますが、Caddy 設定構造の他の部分（たとえば証明書の読み込みと自動化を行う `tls` app）にも、必要に応じて少し設定を加えることがあります。

HTTP 以外の app を設定するには、[独自の server type](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter) を使う独自の config adapter を実装するとよいでしょう。Caddyfile adapter は入力を parse し、server block と option の一覧を渡してくれます。その構造を解釈して JSON 設定へ変換するのは、あなたの adapter の役割です。
