---
title: "Suporte a placeholders"
---

<a id="placeholders"></a>
# Placeholders

No Caddy, placeholders são processados por cada plugin individual conforme necessário; eles não funcionam automaticamente em todos os lugares.

Isso significa que, se você quer que seu plugin suporte placeholders, precisa adicionar esse suporte explicitamente.

Se você ainda não conhece placeholders, comece [lendo aqui](/docs/conventions#placeholders).

<a id="placeholders-overview"></a>
## Visão geral de placeholders

[Placeholders](/docs/conventions#placeholders) são strings no formato `{foo.bar}` usadas como valores dinâmicos de configuração, que são avaliados posteriormente em tempo de execução.

Substituições de [variáveis de ambiente](/docs/caddyfile/concepts#environment-variables) do Caddyfile que começam com cifrão, como `{$FOO}`, são avaliadas no momento de análise do Caddyfile e não precisam ser tratadas pelo seu plugin. Elas _não_ são placeholders, apesar de compartilharem a mesma sintaxe `{ }`.

Portanto, é importante entender que `{env.HOST}` (um [placeholder global](/docs/conventions#placeholders)) é inerentemente diferente de `{$HOST}` (uma substituição de variável de ambiente do Caddyfile).

Como exemplo, veja o Caddyfile a seguir:

```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Ao adaptar este Caddyfile para JSON com `HOST=example caddy adapt`, você obterá:

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

Em particular, observe o campo `"body"` em `srv0` e `srv1`.

Como `srv0` usou `{$HOST}` (substituição de variável de ambiente do Caddyfile), o valor se tornou `example`, pois foi processado durante a análise do Caddyfile ao produzir a configuração JSON.

Como `srv1` usou `{env.HOST}` (um placeholder global), ele permanece inalterado ao adaptar para JSON.

Isso significa que usuários escrevendo configuração JSON (sem usar Caddyfile) não podem usar a sintaxe `{$ENV}`. Por esse motivo, é importante que autores de plugins implementem suporte para substituir placeholders quando a configuração é provisionada. Isso é explicado abaixo.


<a id="implementing-placeholder-support"></a>
## Implementando suporte a placeholders

Você não deve processar placeholders em [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile). Em vez disso, placeholders devem ser substituídos mais tarde, seja na etapa [`Provision()`](/docs/extending-caddy#provisioning), seja durante a execução do seu módulo (por exemplo, `ServeHTTP()` para handlers HTTP, `Match()` para matchers etc.), usando um `caddy.Replacer`.


<a id="examples"></a>
### Exemplos

Aqui, usamos um replacer recém-criado para processar placeholders. Ele tem acesso a [placeholders globais](/docs/conventions#placeholders), como `{env.HOST}`, mas _não_ a placeholders HTTP, como `{http.request.uri}`, porque o provisionamento acontece quando a configuração é carregada, não durante uma requisição.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Aqui, buscamos o replacer no contexto da requisição `r.Context()` durante `ServeHTTP`. Esse replacer tem acesso tanto a placeholders globais _quanto_ a placeholders HTTP por requisição, como `{http.request.uri}`.

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
