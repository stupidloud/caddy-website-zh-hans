---
title: "Soporte de placeholders"
---

# Placeholders

En Caddy, los placeholders se procesan por cada plugin individualmente según sea necesario; no funcionan automaticamente en todo.

Esto significa que si quieres que tu plugin soporte placeholders, debes añadir soporte explicitamente.

Si aún no conoces los placeholders, empieza por [leer aquí](/docs/conventions#placeholders)!

## Vista general de los placeholders

Los [placeholders](/docs/conventions#placeholders) son una cadena con formato `{foo.bar}` usada como valores de configuración dinámicos, y se evalúa más tarde en tiempo de ejecución.

Las sustituciones de [variables de entorno del Caddyfile](/docs/caddyfile/concepts#environment-variables) que comienzan con `$` como `{$FOO}` se evalúan en tiempo de parseo del Caddyfile y no necesitan ser manejadas por tu plugin. Estas **no** son placeholders, a pesar de compartir la misma sintaxis `{ }`.

Por eso es importante entender que `{env.HOST}` (un [placeholder global](/docs/conventions#placeholders)) es intrínsecamente distinto de `{$HOST}` (una sustitución de variable de entorno del Caddyfile).

Como ejemplo, mira este Caddyfile:
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Cuando adaptas este Caddyfile a JSON con `HOST=example caddy adapt` obtendrás:

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

En particular, mira el campo `"body"` en `srv0` y `srv1`.

Como `srv0` usó `{$HOST}` (sustitución de variable de entorno del Caddyfile), el valor se convirtió en `example`, porque se procesó durante el tiempo de parseo del Caddyfile al generar la configuración JSON.

Como `srv1` usó `{env.HOST}` (un placeholder global), permanece sin tocar al adaptarse a JSON.

Esto significa que los usuarios que escriban configuración JSON (sin usar Caddyfile) no pueden usar la sintaxis `{$ENV}`. Por eso es importante que los autores de plugins implementen el soporte para reemplazar placeholders cuando la configuración se provisiona. Esto se explica a continuación.


## Implementar soporte de placeholder

No debes procesar placeholders en [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile). En su lugar, los placeholders deben reemplazarse más tarde, ya sea en el paso de [`Provision()`](/docs/extending-caddy#provisioning), o durante la ejecución de tu módulo (por ejemplo `ServeHTTP()` para handlers de HTTP, `Match()` para matchers, etc.), usando un `caddy.Replacer`.


### Ejemplos

Aquí usamos un replacer recién construido para procesar placeholders. Tiene acceso a [placeholders globales](/docs/conventions#placeholders) como `{env.HOST}`, pero *no* a placeholders de HTTP como `{http.request.uri}` porque el provision ocurre cuando se carga la configuración, y no durante una solicitud.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Aquí obtenemos el replacer del contexto de la petición `r.Context()` durante `ServeHTTP`. Este replacer tiene acceso tanto a placeholders globales como a placeholders HTTP por petición como `{http.request.uri}`.

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
