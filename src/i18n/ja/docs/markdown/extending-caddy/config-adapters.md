---
title: "Config Adapter の作成"
---

<a id="writing-config-adapters"></a>
# Config Adapter の作成

さまざまな理由で、[JSON](/docs/json/) ではない形式を使って Caddy を設定したい場合があります。Caddy は [config adapter](/docs/config-adapters) によって、これを第一級の機能としてサポートしています。

好みの言語、構文、形式向けの adapter がまだ存在しない場合は、自分で作成できます。

<a id="template"></a>
## テンプレート

出発点として使えるテンプレートは次のとおりです。

```go
package myadapter

import (
	"fmt"

	"github.com/caddyserver/caddy/v2/caddyconfig"
)

func init() {
	caddyconfig.RegisterAdapter("adapter_name", MyAdapter{})
}

// MyAdapter adapts ____ to Caddy JSON.
type MyAdapter struct{
}

// Adapt adapts the body to Caddy JSON.
func (a MyAdapter) Adapt(body []byte, options map[string]interface{}) ([]byte, []caddyconfig.Warning, error) {
	// TODO: parse body and convert it to JSON
	return nil, nil, fmt.Errorf("not implemented")
}
```

- [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter) の godoc を参照してください
- [`Adapter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter) インターフェイスの godoc を参照してください

返す JSON は **インデントしない** でください。常にコンパクトな形式にする必要があります。呼び出し側は、必要であればいつでも整形できます。

config adapter は Caddy の *plugins* ですが、Caddy の *modules* ではない点に注意してください。設定の一部へ統合されるわけではないためです（ただし利便性のため、`list-modules` には表示されます）。そのため、`Provision()` や `Validate()` メソッドはなく、残りの module lifecycle にも従いません。`Adapter` インターフェイスを実装し、adapter として登録するだけで十分です。

`json.RawMessage` 型の設定フィールド（つまり module フィールド）へ値を入れるときは、`JSON()` 関数と `JSONModuleObject()` 関数を使います。

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) は、module 名を埋め込まずに module 値を marshal するためのものです。（module 名が map の key になる ModuleMap フィールドでよく使われます。）
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) は、module 名を object に追加したうえで module 値を marshal するためのものです。（それ以外のほぼすべての場所で使われます。）


<a id="caddyfile-server-types"></a>
## Caddyfile Server Types

独自の Caddyfile 形式を実装することも可能です。Caddyfile adapter は単一の adapter 実装で、既定の "server type" は HTTP ですが、登録時に別の "server type" もサポートできます。たとえば、HTTP Caddyfile は次のように登録されています。

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

[`caddyfile.ServerType` インターフェイス](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType)を実装し、それに応じて独自の adapter を登録します。
