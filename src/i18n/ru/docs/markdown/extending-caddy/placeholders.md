---
title: "Поддержка placeholders"
---

<a id="placeholders"></a>
# Placeholders

В Caddy placeholders обрабатываются каждым отдельным plugin по мере необходимости; они не работают автоматически везде.

Это означает, что если вы хотите, чтобы ваш plugin поддерживал placeholders, нужно явно добавить их поддержку.

Если вы еще не знакомы с placeholders, начните с [этого раздела](/docs/conventions#placeholders)!

<a id="placeholders-overview"></a>
## Обзор placeholders

[Placeholders](/docs/conventions#placeholders) — это string формата `{foo.bar}`, используемая как dynamic configuration values и позже вычисляемая во время runtime.

Caddyfile [environment variables substitutions](/docs/caddyfile/concepts#environment-variables), которые начинаются со знака доллара, например `{$FOO}`, вычисляются во время разбора Caddyfile и не должны обрабатываться вашим plugin. Это *не* placeholders, несмотря на общий синтаксис `{ }`.

Поэтому важно понимать, что `{env.HOST}` ([global placeholder](/docs/conventions#placeholders)) принципиально отличается от `{$HOST}` (Caddyfile env-var substitution).

Например, рассмотрим такой Caddyfile:
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Когда вы адаптируете этот Caddyfile в JSON с `HOST=example caddy adapt`, получится:

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

Особенно обратите внимание на field `"body"` в `srv0` и `srv1`.

Поскольку `srv0` использовал `{$HOST}` (Caddyfile env-var substitution), значение стало `example`, так как оно было обработано во время разбора Caddyfile при создании JSON config.

Поскольку `srv1` использовал `{env.HOST}` (global placeholder), он остается нетронутым при адаптации в JSON.

Это означает, что пользователи, пишущие JSON config (без Caddyfile), не могут использовать синтаксис `{$ENV}`. Поэтому важно, чтобы authors plugins реализовали поддержку замены placeholders при provisioning config. Это объясняется ниже.


<a id="implementing-placeholder-support"></a>
## Реализация поддержки placeholders

Не следует обрабатывать placeholders в [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile). Вместо этого placeholders должны заменяться позже — либо на этапе [`Provision()`](/docs/extending-caddy#provisioning), либо во время выполнения module (например, `ServeHTTP()` для HTTP handlers, `Match()` для matchers и т. д.) с использованием `caddy.Replacer`.


<a id="examples"></a>
### Примеры

Здесь мы используем вновь созданный replacer для обработки placeholders. У него есть доступ к [global placeholders](/docs/conventions#placeholders), таким как `{env.HOST}`, но *нет* доступа к HTTP placeholders вроде `{http.request.uri}`, потому что provisioning происходит при загрузке config, а не во время request.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Здесь мы получаем replacer из request context `r.Context()` во время `ServeHTTP`. У этого replacer есть доступ и к global placeholders, и к per-request HTTP placeholders, таким как `{http.request.uri}`.

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
