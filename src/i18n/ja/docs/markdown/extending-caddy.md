---
title: "Caddy の拡張"
---

<a id="extending-caddy"></a>
# Caddy の拡張

Caddy はモジュール型アーキテクチャのおかげで簡単に拡張できます。Caddy の設定構造を拡張したり接続したりする Caddy 拡張（または plugin）の多くは、*modules* と呼ばれます。念のため明確にすると、Caddy module は [Go modules](https://github.com/golang/go/wiki/Modules) とは別物です（ただし、それらも Go module ではあります）。

**前提条件:**
- [Caddy のアーキテクチャ](/docs/architecture)の基本的な理解
- Go 言語に習熟していること
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Quick Start

Caddy module とは、その package が import されたときに自分自身を Caddy module として登録する任意の named type です。重要なのは、module は常に [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module) インターフェイスを実装することです。このインターフェイスは、module 名と constructor function を提供します。

新しい Go module の Go ファイルに次のテンプレートを貼り付け、package 名、type 名、Caddy module ID を調整してください。

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo is an example; put your own type here.
type Gizmo struct {
}

// CaddyModule returns the Caddy module information.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

次に、プロジェクトの directory からこの command を実行すると、一覧に自分の module が表示されるはずです。

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

[`xcaddy` command](https://github.com/caddyserver/xcaddy) は、すべての module 開発者の workflow において重要な一部です。これは Caddy をあなたの plugin と一緒に compile し、指定された引数で実行します。毎回一時 binary は破棄されます（`go run` に似ています）。

</aside>


これで、あなたの module は Caddy に登録され、同じ namespace の module を使う任意の場所で [Caddy の config document](/docs/json/) から使用できます。

内部では、`xcaddy` は単に新しい Go module を作り、Caddy とあなたの plugin の両方を require し（local development version を使うため適切な `replace` を加えます）、compile に含まれるよう import を追加しています。

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Module Basics

Caddy module は次の条件を満たします。

1. `caddy.Module` インターフェイスを実装し、ID と constructor を提供する
2. 適切な namespace 内で一意の名前を持つ
3. 通常、その namespace の host module にとって意味のある interface を 1 つ以上満たす

**Host modules**（または *parent modules*）は、他の module を読み込み、初期化する module です。通常、guest module 用の namespace を定義します。

**Guest modules**（または *child modules*）は、読み込みまたは初期化される module です。すべての module は guest module です。


<a id="module-ids"></a>
## Module IDs

各 Caddy module には、namespace と name からなる一意の ID があります。

- 完全な ID は `foo.bar.module_name` のような形です
- namespace は `foo.bar` です
- name は `module_name` で、その namespace 内で一意でなければなりません

Module ID には `snake_case` の慣例を使う必要があります。

<a id="namespaces"></a>
### Namespaces

namespace は class のようなものです。つまり、namespace はその中のすべての module に共通する機能を定義します。たとえば、`http.handlers` namespace 内のすべての module は HTTP handler であると期待できます。そのため host module は、その namespace の guest module を `interface{}` 型から、`caddyhttp.MiddlewareHandler` のような、より具体的で便利な型へ type assertion できます。

guest module が host module に認識されるには、適切に namespaced されている必要があります。host module は、自分が必要とする機能を得るために、特定の namespace 内の module を Caddy に問い合わせるからです。たとえば `gizmo` という HTTP handler module を書く場合、その module 名は `http.handlers.gizmo` になります。`http` app は handler を `http.handlers` namespace から探すためです。

別の言い方をすると、Caddy module は module namespace に応じて[特定の interface](/docs/extending-caddy/namespaces) を実装することが期待されます。この慣例により、module 開発者は「`http.handlers` namespace 内のすべての module は HTTP handler です」のように直感的に言えます。より技術的には、これは通常「`http.handlers` namespace 内のすべての module は `caddyhttp.MiddlewareHandler` インターフェイスを実装します」という意味です。その method set が分かっているため、より具体的な型へ assertion して使えます。

**[すべての標準 Caddy namespace と Go 型の対応表を見る。](/docs/extending-caddy/namespaces)**

`caddy` と `admin` namespace は予約されており、app 名にはできません。

3rd-party host module に差し込む module を書く場合は、その module の namespace ドキュメントを参照してください。

<a id="names"></a>
### Names

namespace 内の name は重要で、ユーザーからよく見えます。ただし、一意で、簡潔で、何をするものか分かるものであれば、それ自体は特別に重要ではありません。


<a id="app-modules"></a>
## App Modules

App は空の namespace を持つ module で、慣例的に自分自身の top-level namespace になります。App module は [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App) インターフェイスを実装します。

これらの module は、Caddy 設定の top-level にある [`"apps"`](/docs/json/#apps) property に現れます。

```json
{
	"apps": {}
}
```

[app](/docs/json/apps/) の例は `http` と `tls` です。これらの namespace は空です。

これらの app 向けに書かれる guest module は、app 名から派生した namespace に置くべきです。たとえば HTTP handler は `http.handlers` namespace を使い、TLS certificate loader は `tls.certificates` namespace を使います。

<a id="module-implementation"></a>
## Module Implementation

module は事実上どんな type でもかまいませんが、struct が最も一般的です。user configuration を保持できるためです。


<a id="configuration"></a>
### Configuration

ほとんどの module は何らかの設定を必要とします。あなたの type が JSON と互換である限り、Caddy はこれを自動で処理します。そのため、module が struct type であれば、field に struct tag が必要になります。Caddy の慣例に従い、`snake_casing` を使うべきです。

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

struct tag の `omitempty` option を使うと、その field がその型の zero value である場合、JSON output から省略されます。これは、marshal された JSON config（例: Caddyfile から JSON への adapt）をきれいで簡潔に保つのに役立ちます。

module が初期化される時点で、その設定はすでに埋め込まれています。module 初期化後に、追加の [provisioning](#provisioning) や [validation](#validating) ステップを実行することもできます。


<a id="module-lifecycle"></a>
### Module Lifecycle

module の生涯は、host module に読み込まれたときに始まります。次のことが起こります。

1. [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) が呼び出され、module value の instance を取得します。
2. module の設定がその instance に unmarshal されます。
3. module が [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) であれば、`Provision()` メソッドが呼び出されます。
4. module が [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) であれば、`Validate()` メソッドが呼び出されます。
5. この時点で、host module には読み込まれた guest module が `interface{}` value として渡されます。そのため host module は通常、guest module をより便利な型へ type assertion します。その namespace の guest module に何が必要か、たとえばどのメソッドを実装する必要があるかを知るには、host module のドキュメントを確認してください。
6. module が不要になり、それが [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper) であれば、`Cleanup()` メソッドが呼び出されます。

読み込まれたあなたの module の複数 instance が、ある時点で重なる可能性があることに注意してください。設定変更中は、古い module が停止される前に新しい module が開始されます。global state は慎重に使ってください。module load をまたいで global state を管理するには、[`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) 型が役立ちます。あなたの module が socket を listen する場合は、重複利用をサポートする socket を取得するために `caddy.Listen*()` を使ってください。

<a id="provisioning"></a>
### Provisioning

module の設定は、その値へ自動的に unmarshal されます（JSON config を読み込むとき）。つまり、たとえば struct field は自動で埋められます。

ただし、module が追加の provisioning step を必要とする場合は、任意の [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) インターフェイスを実装できます。

```go
// Provision sets up the module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: set up the module
	return nil
}
```

ここでは、ユーザーが提供しなかった field（zero value のままの field）に既定値を設定します。必須 field であれば、設定されていない場合に error を返せます。数値 field で zero value に意味がある場合（例: timeout duration）には、`0` ではなく `-1` を「off」の意味としてサポートしたいことがあります。その場合、ユーザーが設定しなかったときに default value を設定できます。

通常、host module が guest/child module を読み込むのもここです。

module は `ctx.App()` を呼ぶことで他の app にアクセスできますが、module は循環依存してはいけません。言い換えると、`tls` app によって読み込まれる module が `http` app に依存している場合、`http` app によって読み込まれる module は `tls` app に依存できません。（Go で import cycle を禁止する規則によく似ています。）

また、`Provision` では高コストな操作を避けるべきです。設定の validation だけを行う場合でも provisioning は実行されるためです。provisioning phase では、その module が実際に使われるとは期待しないでください。

<a id="logs"></a>
#### Logs

Caddy で[logging がどのように動作するか](/docs/logging)を参照してください。あなたの module が logging を必要とする場合、Go 標準ライブラリの `log.Print*()` を使わないでください。言い換えると、**Go の global logger を使わないでください**。Caddy は [zap](https://github.com/uber-go/zap) による、高性能で柔軟な structured logging を使います。

log を出力するには、module の Provision method で logger を取得します。

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger is a *zap.Logger
}
```

その後、`g.logger` を使って structured かつ leveled な log を出力できます。詳しくは [zap の godoc](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger) を参照してください。


<a id="validating"></a>
### Validating

設定を検証したい module は、任意の [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) インターフェイスを満たすことで実現できます。

```go
// Validate validates that the module has a usable config.
func (g Gizmo) Validate() error {
	// TODO: validate the module's setup
	return nil
}
```

Validate は read-only function であるべきです。これは `Provision()` メソッドの後に実行されます。


<a id="interface-guards"></a>
### Interface guards

Go interface は暗黙的に満たされるため、Caddy module の挙動も暗黙的です。module の type に正しいメソッドを追加するだけで、その module が正しくなったり壊れたりします。そのため、typo や method signature の誤りは、予期しない（挙動しない）結果につながることがあります。

幸い、正しいメソッドを追加したことを保証するために、code へ追加できる簡単で overhead のない compile-time check があります。これを interface guard と呼びます。

```go
var _ InterfaceName = (*YourType)(nil)
```

`InterfaceName` は満たしたい interface に、`YourType` は module type の名前に置き換えてください。

たとえば static file server のような HTTP handler は、複数の interface を満たすことがあります。

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

これにより、`*FileServer` がそれらの interface を満たしていない場合、program は compile できなくなります。

interface guard がないと、分かりにくい bug が入り込むことがあります。たとえば、module が使われる前に自分自身を provision しなければならないのに、`Provision()` メソッドに誤りがある場合（スペルミスや signature の誤りなど）、provisioning はまったく実行されず、原因が分かりにくい問題になります。interface guard は非常に簡単で、そうした問題を防げます。通常は file の末尾に置きます。


<a id="host-modules"></a>
## Host Modules

module は、自分の guest module を読み込むと host module になります。module の機能の一部を複数の方法で実装できる場合に便利です。

host module はほぼ常に struct です。通常、guest module をサポートするには 2 つの struct field が必要です。1 つは raw JSON を保持する field、もう 1 つは decoded value を保持する field です。

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

最初の field（この例では `GadgetRaw`）には、guest module の raw で unprovisioned な JSON 形式が入ります。

2 つ目の field（`Gadget`）には、最終的に provision された value が保存されます。2 つ目の field は user-facing ではないため、struct tag で JSON から除外します。（他 package から必要とされない場合は unexport することもでき、その場合 struct tag は不要です。）

<a id="caddy-struct-tags"></a>
### Caddy struct tags

raw module field の `caddy` struct tag は、読み込む module の namespace と name（完全な ID を構成するもの）を Caddy が知る助けになります。ドキュメント生成にも使われます。

struct tag の形式は非常に単純です。`key1=val1 key2=val2 ...`

module field の struct tag は次のようになります。

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

`namespace=` 部分は必須です。module を探す namespace を定義します。

`inline_key=` 部分は、module 名が module 自体と同じ場所に *inline* で見つかる場合にだけ使われます。これは、値が object で、その key の 1 つが *inline key* であり、その値が module 名であることを意味します。省略した場合、field type は [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) または `[]caddy.ModuleMap` でなければなりません。この場合、map key が module 名です。


<a id="loading-guest-modules"></a>
### Loading guest modules

guest module を読み込むには、provision phase 中に [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) を呼び出します。

```go
// Provision sets up g and loads its gadget.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	if g.GadgetRaw != nil {
		val, err := ctx.LoadModule(g, "GadgetRaw")
		if err != nil {
			return fmt.Errorf("loading gadget module: %v", err)
		}
		g.Gadget = val.(Gadgeter)
	}
	return nil
}
```

`LoadModule()` 呼び出しは、struct への pointer と field 名を string として受け取る点に注意してください。奇妙に見えますよね。なぜ struct field を直接渡さないのでしょうか。理由は、設定の layout に応じて module を読み込む方法がいくつかあるためです。この method signature により、Caddy は reflection を使って module を読み込む最適な方法を判断でき、何より struct tag を読み取れます。

guest module をユーザーが明示的に設定しなければならない場合は、読み込みを試みる前に Raw field が nil または空であれば error を返すべきです。

読み込まれた module がどのように type assertion されているかに注目してください。`g.Gadget = val.(Gadgeter)` です。これは返される `val` が `interface{}` 型で、そのままではあまり役に立たないためです。ただし、宣言した namespace（この例の struct tag では `foo.gizmo.gadgets`）内のすべての module が `Gadgeter` interface を実装すると期待しているため、この type assertion は安全で、その後はそれを使えます。

host module が新しい namespace を定義する場合は、[ここで行っているように](/docs/extending-caddy/namespaces)、その namespace と Go type の両方を開発者向けに必ずドキュメント化してください。

<a id="module-documentation"></a>
## Module Documentation

新しい Caddy module を module documentation に表示し、http://caddyserver.com/download で利用できるようにするには、module を登録してください。登録は http://caddyserver.com/account で行えます。まだ account がない場合は新規作成し、"Register package" をクリックしてください。

<a id="complete-example"></a>
## Complete Example

HTTP handler module を書くとします。これはデモ用の作為的な middleware で、HTTP request ごとに visitor の IP address を stream へ出力します。

また、Caddyfile から設定できるようにもしたいとします。自動化されていない状況では、多くの人が Caddyfile を好むためです。これを行うには、Caddyfile handler directive を登録します。これは HTTP route に handler を追加できる directive の一種です。また、`caddyfile.Unmarshaler` interface も実装します。これら数行の code を追加するだけで、この module は Caddyfile で設定できるようになります。例: `visitor_ip stdout`

説明コメント付きの module code は次のとおりです。

```go
package visitorip

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/caddyserver/caddy/v2"
	"github.com/caddyserver/caddy/v2/caddyconfig/caddyfile"
	"github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile"
	"github.com/caddyserver/caddy/v2/modules/caddyhttp"
)

func init() {
	caddy.RegisterModule(Middleware{})
	httpcaddyfile.RegisterHandlerDirective("visitor_ip", parseCaddyfile)
}

// Middleware implements an HTTP handler that writes the
// visitor's IP address to a file or stream.
type Middleware struct {
	// 書き込み先の file または stream。"stdout"
	// または "stderr" を指定できます。
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule returns the Caddy module information.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision implements caddy.Provisioner.
func (m *Middleware) Provision(ctx caddy.Context) error {
	switch m.Output {
	case "stdout":
		m.w = os.Stdout
	case "stderr":
		m.w = os.Stderr
	default:
		return fmt.Errorf("an output stream is required")
	}
	return nil
}

// Validate implements caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP implements caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile implements caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // directive 名を消費

	// 引数を必須にする
	if !d.NextArg() {
		return d.ArgErr()
	}

	// 引数を保存
	m.Output = d.Val()
	return nil
}

// parseCaddyfile unmarshals tokens from h into a new Middleware.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Interface guards
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
