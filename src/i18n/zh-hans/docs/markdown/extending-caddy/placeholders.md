---
title: "占位符支持"
---

# 占位符

在 Caddy 中，占位符由各个插件根据需要分别处理；它们不会在所有地方自动生效。

这意味着，如果你希望你的插件支持占位符，就必须明确添加对它们的支持。

如果您还不熟悉占位符，请先[阅读此处](/docs/conventions#placeholders)！

## 占位符概述

[占位符](/docs/conventions#placeholders)是一种格式为 `{foo.bar}` ，用于作为动态配置值，并在后续运行时进行求值。

在 Caddyfile 中，以美元符号开头的[环境变量替换项](/docs/caddyfile/concepts#environment-variables)（如 `{$FOO}` 将在解析 Caddyfile 时进行求值，无需由您的插件处理。尽管它们与占位符具有相同的 `{ }` 语法。

因此，必须明白 `{env.HOST}` ([全局占位符](/docs/conventions#placeholders)) 与 `{$HOST}` （Caddyfile 环境变量替换）。

例如，请参阅以下 Caddyfile：
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

当你将此 Caddyfile 转换为 JSON 时， `HOST=example caddy adapt` ，你会得到：

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

请特别注意 `"body"` 字段 `srv0` 和 `srv1`.

自 `srv0` 使用 `{$HOST}` （Caddyfile 环境变量替换），该值变为 `example`，因为该值是在生成 JSON 配置时，于 Caddyfile 解析阶段被处理的。

自 `srv1` 使用了 `{env.HOST}` （一个全局占位符），因此在转换为 JSON 时它保持不变。

这确实意味着编写 JSON 配置（而非使用 Caddyfile）的用户无法使用 `{$ENV}` 语法。因此，插件作者必须在配置部署时实现对占位符的替换支持。具体说明如下。


## 实现占位符支持

不应在 [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile) 中处理占位符。相反，应在后续步骤中替换占位符，具体可在 [`Provision()`](/docs/extending-caddy#provisioning) 步骤中进行，或在模块执行期间进行（例如 `ServeHTTP()` 对于 HTTP 处理程序， `Match()` 对于匹配器等），使用一个 `caddy.Replacer`.


### 示例

在此，我们使用了一个新构建的替换器来处理占位符。它可以访问[全局占位符](/docs/conventions#placeholders)，例如 `{env.HOST}`，但无法访问诸如 `{http.request.uri}` ，因为配置的初始化是在加载配置时进行的，而非在请求过程中。

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

在此，我们从请求上下文中获取替换器 `r.Context()` 期间 `ServeHTTP`。该替换器既可访问全局占位符，也可访问每请求的 HTTP 占位符，例如 `{http.request.uri}`.

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
