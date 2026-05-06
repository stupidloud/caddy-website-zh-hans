---
title: vars (direttiva del Caddyfile)
---

# vars

Imposta una o più variabili su un valore particolare, da utilizzare successivamente nella catena di gestione della richiesta.

Il modo principale per accedere alle variabili è con i placeholder, che hanno la forma `{vars.nome_variabile}`, o con i matcher di richiesta [`vars`](/docs/caddyfile/matchers#vars) e [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

È possibile utilizzare le variabili con la direttiva [`templates`](templates) usando la funzione `placeholder`, ad esempio: `{{ "{{placeholder \"http.vars.nome_variabile\"}}" }}`

Come caso speciale, è possibile sovrascrivere la variabile denominata `http.auth.user.id`, che è memorizzata nel replacer, per aggiornare il campo `user_id` nei [log degli accessi](log).


## Sintassi

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** è il nome della variabile da impostare.

- **&lt;value&gt;** è il valore della variabile.

  Il valore verrà convertito nel tipo appropriato se possibile; `true` e `false` verranno convertiti in tipi booleani, e i valori numerici verranno convertiti rispettivamente in interi o virgola mobile. Per evitare questa conversione e mantenerli come stringhe, potete racchiuderli tra [virgolette](/docs/caddyfile/concepts#token-e-virgolette).

## Esempi

Per impostare una singola variabile, con il valore condizionale in base al percorso della richiesta, per poi rispondere con il valore:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

Per impostare più variabili, ciascuna convertita nel tipo scalare appropriato:

```caddy-d
vars {
	# booleano
	abc true

	# intero
	def 1

	# virgola mobile
	ghi 2.3

	# stringa
	jkl "esempio"
}
```
