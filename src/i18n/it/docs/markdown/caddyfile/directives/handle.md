---
title: handle (direttiva del Caddyfile)
---

# handle

Valuta un gruppo di direttive in modo mutualmente esclusivo rispetto ad altri blocchi `handle` allo stesso livello di nidificazione.

In altre parole, quando più direttive `handle` appaiono in sequenza, verrà valutato solo il primo blocco `handle` *corrispondente*. Un handle senza matcher agisce come una rotta di *fallback*.

Le direttive `handle` sono ordinate secondo l'[algoritmo di ordinamento delle direttive](/docs/caddyfile/directives#algoritmo-di-ordinamento) in base ai loro matcher. La direttiva [`handle_path`](handle_path) è un caso speciale che viene ordinato con la stessa priorità di un `handle` con un matcher di percorso.

I blocchi handle possono essere nidificati se necessario. All'interno dei blocchi handle possono essere utilizzate solo direttive handler HTTP.

## Sintassi

```caddy-d
handle [<matcher>] {
	<direttive...>
}
```

- **&lt;direttive...&gt;** è un elenco di direttive handler HTTP o blocchi direttiva, uno per riga, proprio come verrebbero usati all'esterno di un blocco handle.


## Direttive simili

Esistono altre direttive che possono avvolgere le direttive degli handler HTTP, ma ognuna ha il suo scopo a seconda del comportamento che si desidera ottenere:

- [`handle_path`](handle_path) fa lo stesso di `handle`, ma rimuove un prefisso dalla richiesta prima di eseguire i suoi handler.

- [`handle_errors`](handle_errors) è come `handle`, ma viene invocata solo quando Caddy riscontra un errore durante la gestione della richiesta.

- [`route`](route) avvolge altre direttive come fa `handle`, ma con due distinzioni:
  1. i blocchi route non sono mutualmente esclusivi tra loro,
  2. le direttive all'interno di un route non vengono [riordinate](/docs/caddyfile/directives#ordine-delle-direttive), offrendo maggiore controllo se necessario.



## Esempi

Gestisce le richieste in `/foo/` con il server di file statici, e le altre richieste con il reverse proxy:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

È possibile mescolare `handle` e [`handle_path`](handle_path) nello stesso sito, e rimarranno comunque mutualmente esclusivi tra loro:

```caddy
example.com {
	handle_path /foo/* {
		# Il percorso ha il prefisso "/foo" rimosso
	}

	handle /bar/* {
		# Il percorso mantiene ancora "/bar"
	}
}
```

Potete nidificare i blocchi `handle` per creare una logica di routing più complessa:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Questo blocco corrisponde solo ai percorsi sotto /foo/bar
		}

		handle {
			# Questo blocco corrisponde a tutto il resto sotto /foo/
		}
	}

	handle {
		# Questo blocco corrisponde a tutto il resto (agisce come fallback)
	}
}
```
