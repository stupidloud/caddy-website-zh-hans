---
title: "Placeholder Support"
---

<a id="placeholders"></a>
# Placeholders

Caddy では、placeholder は必要に応じて各 plugin が個別に処理します。どこでも自動的に動作するわけではありません。

つまり、自分の plugin で placeholder をサポートしたい場合は、そのサポートを明示的に追加する必要があります。

placeholder にまだ慣れていない場合は、まず[こちら](/docs/conventions#placeholders)を読んでください。

<a id="placeholders-overview"></a>
## Placeholders Overview

[Placeholder](/docs/conventions#placeholders) は `{foo.bar}` 形式の文字列で、動的な設定値として使われ、後で実行時に評価されます。

`{$FOO}` のようにドル記号で始まる Caddyfile の [environment variable substitution](/docs/caddyfile/concepts#environment-variables) は、Caddyfile の parse 時に評価されるため、plugin 側で処理する必要はありません。同じ `{ }` 構文を使っていますが、これらは placeholder では*ありません*。

そのため、`{env.HOST}`（[global placeholder](/docs/conventions#placeholders)）は、`{$HOST}`（Caddyfile の env-var substitution）とは本質的に異なることを理解しておくことが重要です。

例として、次の Caddyfile を見てください。
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

この Caddyfile を `HOST=example caddy adapt` で JSON に adapt すると、次の結果になります。

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":8080"],
          "routes": [
            {
              "handle": [
                {
                  "body": "example",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        },
        "srv1": {
          "listen": [":8081"],
          "routes": [
            {
              "handle": [
                {
                  "body": "{env.HOST}",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

特に、`srv0` と `srv1` の両方にある `"body"` フィールドを見てください。

`srv0` は `{$HOST}`（Caddyfile env-var substitution）を使っているため、JSON 設定を生成する Caddyfile parse 時に処理され、値は `example` になります。

`srv1` は `{env.HOST}`（global placeholder）を使っているため、JSON へ adapt してもそのまま残ります。

これは、JSON 設定を書くユーザー（Caddyfile を使わないユーザー）は `{$ENV}` 構文を使えない、という意味でもあります。そのため plugin 作者は、設定が provision されるときに placeholder を置換するサポートを実装することが重要です。以下で説明します。


<a id="implementing-placeholder-support"></a>
## Placeholder support の実装

[`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile) の中で placeholder を処理しないでください。placeholder は後で、[`Provision()`](/docs/extending-caddy#provisioning) ステップ、または module の実行中（HTTP handler なら `ServeHTTP()`、matcher なら `Match()` など）に、`caddy.Replacer` を使って置換するべきです。


<a id="examples"></a>
### 例

ここでは、新しく構築した replacer を使って placeholder を処理しています。この replacer は `{env.HOST}` のような [global placeholder](/docs/conventions#placeholders) にはアクセスできますが、`{http.request.uri}` のような HTTP placeholder にはアクセス*できません*。provisioning は、request 中ではなく、設定が読み込まれるときに行われるためです。

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

ここでは、`ServeHTTP` の中で request context `r.Context()` から replacer を取得しています。この replacer は global placeholder と、`{http.request.uri}` のような request ごとの HTTP placeholder の両方にアクセスできます。

```go
func (g *Gizmo) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	repl := r.Context().Value(caddy.ReplacerCtxKey).(*caddy.Replacer)
	_, err := w.Write([]byte(repl.ReplaceAll(g.Name,"")))
	if err != nil {
		return err
	}
	return next.ServeHTTP(w, r)
}
```
