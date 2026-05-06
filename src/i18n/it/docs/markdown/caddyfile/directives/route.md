---
title: route (direttiva del Caddyfile)
---

# route

Valuta un gruppo di direttive letteralmente e come una singola unità.

Le direttive contenute in un blocco `route` non verranno [riordinate internamente](/docs/caddyfile/directives#ordine-delle-direttive). Solo le direttive degli handler HTTP (direttive che aggiungono handler o middleware alla catena) possono essere utilizzate in un blocco `route`.

Questa direttiva è un caso speciale in quanto le sue sottodirettive sono anch'esse normali direttive.


## Sintassi

```caddy-d
route [<matcher>] {
	<direttive...>
}
```

- **&lt;direttive...&gt;** è un elenco di direttive o blocchi direttiva, uno per riga, proprio come all'esterno di un blocco `route`; con la differenza che queste direttive non verranno riordinate. Possono essere utilizzate solo le direttive degli handler HTTP.



## Utilità

La direttiva `route` è utile in determinati casi d'uso avanzati o casi limite per assumere il controllo assoluto su parti della catena degli handler HTTP.

Poiché l'ordine di valutazione dei middleware HTTP è significativo, il Caddyfile normalmente riordina le direttive dopo l'analisi per renderlo più facile da usare; non dovete preoccuparvi dell'ordine in cui scrivete le cose.

Sebbene l'[ordine integrato](/docs/caddyfile/directives#ordine-delle-direttive) sia compatibile con la maggior parte dei siti, a volte è necessario assumere il controllo manuale sull'ordine, per l'intero sito o solo per una parte di esso. È a questo che serve la direttiva `route`.

Per illustrare, consideriamo il caso di due handler terminali: [`redir`](redir) e [`file_server`](file_server). Entrambi scrivono la risposta al client e non chiamano l'handler successivo nella catena, quindi solo uno di questi verrà eseguito per una determinata richiesta. Quale viene eseguito per primo? Normalmente, `redir` viene eseguito prima di `file_server` perché solitamente si desidera emettere un reindirizzamento solo in casi specifici e servire i file nel caso generale.

Tuttavia, possono esserci occasioni in cui la prima direttiva (`file_server`) ha un matcher più specifico della seconda (`redir`). In altri termini, volete reindirizzare nel caso generale e servire solo un file specifico.

Potreste quindi provare un Caddyfile come questo (ma non funzionerà come previsto!):

```caddy
example.com {
	file_server /specifico.html
	redir https://altrisito.com{uri}
}
```

Il problema è che dopo che le [direttive sono state ordinate](/docs/caddyfile/directives#algoritmo-di-ordinamento), `redir` viene posizionato prima di `file_server`.

Ma in questo caso il matcher per `redir` (un [`*`](/docs/caddyfile/matchers#wildcard-matchers) implicito) è un superset del matcher per `file_server` (`*` è un superset di `/specifico.html`).

Fortunatamente, la soluzione è semplice: basta avvolgere queste due direttive in un blocco `route`, per garantire che `file_server` venga eseguito prima di `redir`:

```caddy
example.com {
	route {
		file_server /specifico.html
		redir https://altrisito.com{uri}
	}
}
```

<aside class="tip">

Un altro modo per farlo è rendere i due matcher mutualmente esclusivi, ma questo può diventare rapidamente complesso se ci sono più di una o due condizioni. Con la direttiva `route`, la mutua esclusività dei due handler è implicita perché sono entrambi handler terminali.

</aside>

E ora `file_server` verrà concatenato prima di `redir` perché l'ordine viene preso letteralmente.



## Direttive simili

Esistono altre direttive che possono avvolgere le direttive degli handler HTTP, ma ognuna ha il suo scopo a seconda del comportamento che si desidera ottenere:

- [`handle`](handle) avvolge altre direttive come fa `route`, ma con due distinzioni: 1) i blocchi handle sono mutualmente esclusivi tra loro, e 2) le direttive all'interno di un handle vengono [riordinate](/docs/caddyfile/directives#ordine-delle-direttive) normalmente.

- [`handle_path`](handle_path) fa lo stesso di `handle`, ma rimuove un prefisso dalla richiesta prima di eseguire i suoi handler.

- [`handle_errors`](handle_errors) è come `handle`, ma viene invocata solo quando Caddy riscontra un errore durante la gestione della richiesta.



## Esempi

Effettua il proxy delle richieste a `/api` così come sono, e riscrive tutte le altre richieste in base alla corrispondenza con un file su disco, altrimenti verso `/index.html`. Quindi quel file viene servito.

Poiché [`try_files`](try_files) ha un ordine di direttiva superiore rispetto a [`reverse_proxy`](reverse_proxy), verrebbe normalmente ordinato più in alto ed eseguito per primo; ciò causerebbe la riscrittura di tutte le richieste API verso `/index.html` e il mancato matching di `/api*`, quindi nessuna di esse verrebbe passata al proxy e risulterebbe invece in un `404` da [`file_server`](file_server). Avvolgere tutto in un `route` garantisce che `reverse_proxy` venga eseguito sempre per primo, prima che la richiesta venga riscritta.

```caddy
example.com {
	root * /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Questa non è l'unica soluzione al problema. Potreste anche usare una coppia di blocchi [`handle`](handle), con il primo che fa il match di `/api*` verso `reverse_proxy`, e il secondo che agisce come fallback servendo i file. Consultate [questo esempio](/docs/caddyfile/patterns#single-page-app-spa) di una SPA.

</aside>
