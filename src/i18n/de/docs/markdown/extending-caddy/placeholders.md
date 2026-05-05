---
title: "Placeholder-Unterstützung"
---

<a id="placeholders"></a>
# Placeholders

In Caddy werden placeholders von jedem einzelnen plugin nach Bedarf verarbeitet; sie funktionieren nicht automatisch überall.

Das bedeutet: Wenn dein plugin placeholders unterstützen soll, musst du diese Unterstützung ausdrücklich hinzufügen.

Wenn du mit placeholders noch nicht vertraut bist, lies zuerst [diesen Abschnitt](/docs/conventions#placeholders).

<a id="placeholders-overview"></a>
## Überblick über placeholders

[Placeholders](/docs/conventions#placeholders) sind Zeichenketten im Format `{foo.bar}`, die als dynamische Konfigurationswerte verwendet und später zur Laufzeit ausgewertet werden.

Caddyfile-[Ersetzungen von Umgebungsvariablen](/docs/caddyfile/concepts#environment-variables), die mit einem Dollarzeichen beginnen, etwa `{$FOO}`, werden beim Parsen des Caddyfile ausgewertet und müssen von deinem plugin nicht behandelt werden. Das sind *keine* placeholders, auch wenn sie dieselbe `{ }`-Syntax verwenden.

Deshalb ist wichtig zu verstehen, dass `{env.HOST}` (ein [global placeholder](/docs/conventions#placeholders)) grundsätzlich etwas anderes ist als `{$HOST}` (eine Caddyfile env-var substitution).

Sieh dir als Beispiel dieses Caddyfile an:
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Wenn du dieses Caddyfile mit `HOST=example caddy adapt` nach JSON anpasst, erhältst du:

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

Achte insbesondere auf das Feld `"body"` in `srv0` und `srv1`.

Da `srv0` `{$HOST}` verwendet hat (Caddyfile env-var substitution), wurde der Wert zu `example`, weil er während des Parsens des Caddyfile bei der Erzeugung der JSON-Konfiguration verarbeitet wurde.

Da `srv1` `{env.HOST}` verwendet hat (einen global placeholder), bleibt der Wert beim Anpassen nach JSON unverändert.

Das bedeutet allerdings, dass Benutzer, die JSON-Konfiguration schreiben (ohne Caddyfile), die Syntax `{$ENV}` nicht verwenden können. Deshalb ist es wichtig, dass plugin authors Unterstützung zum Ersetzen von placeholders implementieren, wenn die Konfiguration provisioned wird. Das wird unten erklärt.


<a id="implementing-placeholder-support"></a>
## Placeholder-Unterstützung implementieren

Du solltest placeholders nicht in [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile) verarbeiten. Stattdessen sollten placeholders später ersetzt werden, entweder im Schritt [`Provision()`](/docs/extending-caddy#provisioning) oder während der Ausführung deines modules (z. B. `ServeHTTP()` für HTTP handlers, `Match()` für matchers usw.), mit einem `caddy.Replacer`.


<a id="examples"></a>
### Beispiele

Hier verwenden wir einen neu konstruierten replacer, um placeholders zu verarbeiten. Er hat Zugriff auf [global placeholders](/docs/conventions#placeholders) wie `{env.HOST}`, aber *nicht* auf HTTP placeholders wie `{http.request.uri}`, weil provisioning beim Laden der Konfiguration passiert und nicht während eines Requests.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Hier holen wir den replacer während `ServeHTTP` aus dem Request-Kontext `r.Context()`. Dieser replacer hat Zugriff sowohl auf global placeholders *als auch* auf HTTP placeholders pro Request, etwa `{http.request.uri}`.

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
