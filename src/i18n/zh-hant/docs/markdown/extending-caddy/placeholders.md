---
title: "Placeholder 支援"
---

<a id="placeholders"></a>
# Placeholders

在 Caddy 中，placeholder 是由各個插件根據需要進行處理的；它們不會自動在所有地方生效。

這意味著如果你希望你的插件支援 placeholder，你必須明確地為其加入支援。

如果你還不熟悉 placeholder，請先從 [這裡閱讀](/docs/conventions#placeholders)！

<a id="placeholders-overview"></a>
## Placeholders 概覽

[Placeholders](/docs/conventions#placeholders) 是格式為 `{foo.bar}` 的字串，用作動態配置值，隨後在運行時進行求值。

Caddyfile [環境變數替換](/docs/caddyfile/concepts#environment-variables) 以美元符號開頭（例如 `{$FOO}`），是在 Caddyfile 解析時進行求值的，不需要由你的插件處理。儘管它們共享相同的 `{ }` 語法，但這些 *不是* placeholder。

因此，理解 `{env.HOST}`（一個 [全域 placeholder](/docs/conventions#placeholders)）與 `{$HOST}`（一個 Caddyfile 環境變數替換）本質上是不同的，這一點非常重要。

舉例來說，請看以下的 Caddyfile：
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

當你使用 `HOST=example caddy adapt` 將此 Caddyfile 適配為 JSON 時，你將得到：

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

特別注意 `srv0` 和 `srv1` 中的 `"body"` 欄位。

由於 `srv0` 使用了 `{$HOST}`（Caddyfile 環境變數替換），該值變成了 `example`，因為它是在產生 JSON 配置的 Caddyfile 解析期間處理的。

由於 `srv1` 使用了 `{env.HOST}`（全域 placeholder），它在適配為 JSON 時保持不變。

這確實意味著編寫 JSON 配置（不使用 Caddyfile）的使用者無法使用 `{$ENV}` 語法。出於這個原因，插件作者在配置 (provisioned) 時實現替換 placeholder 的支援是非常重要的。這將在下面說明。


<a id="implementing-placeholder-support"></a>
## 實現 placeholder 支援

你不應該在 [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile) 中處理 placeholder。相反地，placeholder 應該在稍後被替換，可以是在 [`Provision()`](/docs/extending-caddy#provisioning) 步驟中，或者在模組執行期間（例如 HTTP handler 的 `ServeHTTP()`、matcher 的 `Match()` 等），並使用 `caddy.Replacer`。


<a id="examples"></a>
### 範例

這裡，我們使用新構建的 replacer 來處理 placeholder。它可以存取 [全域 placeholder](/docs/conventions#placeholders)，例如 `{env.HOST}`，但 *不能* 存取 HTTP placeholder（例如 `{http.request.uri}`），因為配置 (provisioning) 發生在配置載入時，而不是在請求期間。

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

這裡，我們在 `ServeHTTP` 期間從請求上下文 `r.Context()` 中獲取 replacer。這個 replacer 既可以存取全域 placeholder，*又* 可以存取每個請求的 HTTP placeholder（例如 `{http.request.uri}`）。

```go
func (g *Gizmo) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	repl := r.Context().Value(caddy.ReplacerCtxKey).(*caddy.Replacer)
	_, err := w.Write([]byte(repl.ReplaceAll(g.Name,"")))
	if err != nil {
		return err
	}
	return next.ServeHTTP(w, r)
}
