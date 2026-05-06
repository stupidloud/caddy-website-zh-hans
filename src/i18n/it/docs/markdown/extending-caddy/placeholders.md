---
title: "Supporto ai placeholder"
---

# Placeholder

In Caddy, i placeholder vengono elaborati da ogni singolo plugin secondo necessità; non funzionano automaticamente ovunque.

Ciò significa che se desiderate che il vostro plugin supporti i placeholder, dovrete aggiungervi esplicitamente il supporto.

Se non avete ancora familiarità con i placeholder, iniziate [leggendo qui](/docs/conventions#placeholder)!

## Panoramica sui placeholder

I [placeholder](/docs/conventions#placeholder) sono stringhe nel formato `{foo.bar}` usate come valori di configurazione dinamici, che vengono valutati successivamente a runtime.

Le [sostituzioni delle variabili d'ambiente](/docs/caddyfile/concepts#variabili-dambiente) del Caddyfile che iniziano con un segno di dollaro come `{$FOO}` vengono valutate al momento dell'analisi (parsing) del Caddyfile e non devono essere gestite dal vostro plugin. Questi *non* sono placeholder, nonostante condividano la stessa sintassi `{ }`.

È quindi importante capire che `{env.HOST}` (un [placeholder globale](/docs/conventions#placeholder)) è intrinsecamente diverso da `{$HOST}` (una sostituzione di variabile d'ambiente del Caddyfile).

Come esempio, osservate il seguente Caddyfile:
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Quando adattate questo Caddyfile in JSON con `HOST=esempio caddy adapt` otterrete:

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
                  "body": "esempio",
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

In particolare, guardate il campo `"body"` sia in `srv0` che in `srv1`.

Poiché `srv0` ha usato `{$HOST}` (sostituzione var-env del Caddyfile), il valore è diventato `esempio`, in quanto è stato elaborato durante l'analisi del Caddyfile nella produzione della configurazione JSON.

Poiché `srv1` ha usato `{env.HOST}` (un placeholder globale), rimane invariato durante l'adattamento in JSON.

Ciò significa che gli utenti che scrivono la configurazione JSON (senza usare il Caddyfile) non possono usare la sintassi `{$ENV}`. Per tale ragione, è importante che gli autori dei plugin implementino il supporto per la sostituzione dei placeholder quando la configurazione viene predisposta. Questo viene spiegato di seguito.


## Implementare il supporto ai placeholder

Non dovreste elaborare i placeholder in [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile). Invece, i placeholder dovrebbero essere sostituiti successivamente, o nella fase di [`Provision()`](/docs/extending-caddy#predisposizione-provisioning), o durante l'esecuzione del vostro modulo (es. `ServeHTTP()` per i gestori HTTP, `Match()` per i matcher, ecc.), utilizzando un `caddy.Replacer`.


### Esempi

Qui stiamo usando un replacer appena costruito per elaborare i placeholder. Esso ha accesso ai [placeholder globali](/docs/conventions#placeholder) come `{env.HOST}`, ma *non* ai placeholder HTTP come `{http.request.uri}` perché la predisposizione avviene quando la configurazione viene caricata, e non durante una richiesta.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Qui recuperiamo il replacer dal contesto della richiesta `r.Context()` durante `ServeHTTP`. Questo replacer ha accesso sia ai placeholder globali *che* ai placeholder HTTP per singola richiesta come `{http.request.uri}`.

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
