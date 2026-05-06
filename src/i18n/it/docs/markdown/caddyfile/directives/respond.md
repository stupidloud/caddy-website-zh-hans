---
title: respond (direttiva del Caddyfile)
---

# respond

Scrive una risposta fissa/statica al client.

Se il corpo non è vuoto, questa direttiva imposta l'header `Content-Type` se non è già impostato. Il valore predefinito è `text/plain; utf-8` a meno che il corpo non sia un oggetto o un array JSON valido, nel qual caso viene impostato su `application/json`. Per tutti gli altri tipi di contenuto, impostate il Content-Type corretto esplicitamente usando la [direttiva `header`](/docs/caddyfile/directives/header).


## Sintassi

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** è il codice di stato HTTP da scrivere.

  Se `103` (Early Hints), la risposta verrà scritta senza un corpo e la catena degli handler proseguirà. (Le risposte HTTP `1xx` sono informative, non definitive.)
  
  Predefinito: `200`

- **&lt;body&gt;** è il corpo della risposta da scrivere.

- **body** è un modo alternativo per fornire un corpo; comodo se è su più righe.

- **close** chiuderà la connessione del client al server dopo aver scritto la risposta.

Per chiarire, il primo argomento non-matcher può essere o un codice di stato a 3 cifre o una stringa del corpo della risposta. Se è un corpo, l'argomento successivo può essere il codice di stato.

<aside class="tip">

Rispondere con un codice di stato di errore è diverso dal restituire un errore nella catena degli handler, che invoca internamente gli handler degli errori.

</aside>


## Esempi

Scrive uno stato 200 vuoto con un corpo vuoto per tutti i controlli sanitari (health checks), e un semplice corpo della risposta per tutte le altre richieste:

```caddy
example.com {
	respond /health-check 200
	respond "Ciao, mondo!"
}
```

Scrive una risposta di errore e chiude la connessione:

<aside class="tip">

Potreste preferire l'uso della [direttiva `error`](error) al suo posto, la quale innesca un errore che può essere gestito con la [direttiva `handle_errors`](handle_errors).

</aside>

```caddy
example.com {
	respond /secret/* "Accesso negato" 403 {
		close
	}
}
```

Scrive una risposta HTML, usando la [sintassi heredoc](/docs/caddyfile/concepts#heredocs) per controllare gli spazi bianchi, e impostando anche l'header `Content-Type` affinché corrisponda al corpo della risposta:

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
