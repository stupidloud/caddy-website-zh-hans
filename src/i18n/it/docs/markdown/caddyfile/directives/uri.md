---
title: uri (direttiva del Caddyfile)
---

# uri

Manipola l'URI di una richiesta. Può rimuovere prefissi/suffissi del percorso o sostituire sottostringhe sull'intero URI.

Questa direttiva è distinta da [`rewrite`](rewrite) in quanto `uri` modifica l'URI in modo *differenziato*, anziché resettarlo a qualcosa di completamente diverso come fa `rewrite`. Mentre `rewrite` è trattato specialmente come un reindirizzamento interno, `uri` è semplicemente un altro middleware.


## Sintassi

Sono supportate diverse operazioni:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

Il primo argomento (non-matcher) specifica l'operazione:

- **strip_prefix** rimuove il prefisso dal percorso.

- **strip_suffix** rimuove il suffisso dal percorso.

- **replace** esegue una sostituzione di sottostringa sull'intero URI.

	- **&lt;target&gt;** è il prefisso, il suffisso, o la stringa di ricerca/espressione regolare. Se è un prefisso, la barra in avanti iniziale può essere omessa, poiché i percorsi iniziano sempre con una barra in avanti.

	- **&lt;replacement&gt;** è la stringa di sostituzione. Supporta l'uso di gruppi di cattura con la sintassi `$name` o `${name}`, o con un numero per l'indice, come `$1`. Consultate la [documentazione di Go](https://golang.org/pkg/regexp/#Regexp.Expand) per i dettagli. Se il valore di sostituzione è `""`, il testo corrispondente viene rimosso dal valore.

	- **&lt;limit&gt;** è un limite opzionale al numero massimo di sostituzioni.

- **path_regexp** esegue una sostituzione tramite espressione regolare sulla porzione di percorso dell'URI.

	- **&lt;target&gt;** è il prefisso, il suffisso, o la stringa di ricerca/espressione regolare. Se è un prefisso, la barra in avanti iniziale può essere omessa, poiché i percorsi iniziano sempre con una barra in avanti.

	- **&lt;replacement&gt;** è la stringa di sostituzione. Supporta l'uso di gruppi di cattura con la sintassi `$name` o `${name}`, o con un numero per l'indice, come `$1`. Consultate la [documentazione di Go](https://golang.org/pkg/regexp/#Regexp.Expand) per i dettagli. Se il valore di sostituzione è `""`, il testo corrispondente viene rimosso dal valore.

- **query** esegue manipolazioni sulla query dell'URI, con la modalità che dipende dal prefisso al nome del parametro o dal numero di argomenti. Un blocco può essere usato per specificare più operazioni contemporaneamente, raggruppate ed eseguite in questo ordine: rinomina 🡒 impostazione 🡒 aggiunta 🡒 sostituzione 🡒 eliminazione.

	- Senza prefisso, il parametro viene impostato con il valore fornito nella query.
	
	  Per esempio, `uri query foo bar` imposterà il valore del parametro `foo` su `bar`.

	- Prefisso con `-` per rimuovere il parametro dalla query.
	
	  Per esempio, `uri query -foo` eliminerà il parametro `foo` dalla query.

	- Prefisso con `+` per aggiungere un parametro alla query, con il valore fornito. Questo *non* sovrascriverà un parametro esistente con lo stesso nome (omettete il `+` per sovrascrivere).
	
	  Per esempio, `uri query +foo bar` aggiungerà `foo=bar` alla query.

	- Un parametro con `>` come infisso rinominerà il parametro al valore dopo il `>`. 
	
	  Per esempio, `uri query foo>bar` rinominerà il parametro `foo` in `bar`.

	- Con tre argomenti, viene eseguita la sostituzione tramite espressione regolare del valore della query, dove il primo argomento è il nome del parametro di query, il secondo è il valore di ricerca e il terzo è la sostituzione. Il primo argomento (nome parametro) può essere `*` per eseguire la sostituzione su tutti i parametri di query.
	
	  Supporta l'uso di gruppi di cattura con la sintassi `$name` o `${name}`, o con un numero per l'indice, come `$1`. Consultate la [documentazione di Go](https://golang.org/pkg/regexp/#Regexp.Expand) per i dettagli. Se il valore di sostituzione è `""`, il testo corrispondente viene rimosso dal valore.
	
	  Per esempio, `uri query foo ^(ba)r $1z` sostituirebbe il valore del parametro `foo`, dove il valore inizierebbe con `bar` facendo sì che il valore diventi `baz`.

Le mutazioni dell'URI avvengono sulla forma normalizzata o unescaped dell'URI. Tuttavia, le sequenze di escape possono essere utilizzate nei pattern di prefisso o suffisso per far corrispondere solo quegli escape letterali in quelle posizioni nel percorso della richiesta. Ad esempio, `uri strip_prefix /a/b` riscriverà sia `/a/b/c` che `/a%2Fb/c` in `/c`; e `uri strip_prefix /a%2Fb` riscriverà `/a%2Fb/c` in `/c`, ma non corrisponderà a `/a/b/c`.

Il percorso dell'URI viene pulito dai punti di attraversamento delle directory prima delle modifiche. Inoltre, le barre multiple (come `//`) vengono unite a meno che il `<target>` non contenga anch'esso barre multiple.

## Direttive simili

Altre direttive possono manipolare l'URI della richiesta.

- [`rewrite`](rewrite) cambia l'intero percorso e la query in un nuovo valore invece di cambiare parzialmente il valore.

- [`handle_path`](handle_path) fa lo stesso di [`handle`](handle), ma rimuove un prefisso dalla richiesta prima di eseguire i suoi handler. Può essere usato al posto di `uri strip_prefix` per eliminare una riga extra di configurazione in molti casi.


## Esempi

Rimuove `/api` dall'inizio di tutti i percorsi delle richieste:

```caddy-d
uri strip_prefix /api
```

Rimuove `.php` dalla fine di tutti i percorsi delle richieste:

```caddy-d
uri strip_suffix .php
```

Sostituisce "/docs/" con "/v1/docs/" in qualsiasi URI di richiesta:

```caddy-d
uri replace /docs/ /v1/docs/
```

Comprime tutte le barre ripetute nel percorso della richiesta (ma non nella query della richiesta) in una singola barra:

```caddy-d
uri path_regexp /{2,} /
```

Imposta il valore del parametro di query `foo` su `bar`:

```caddy-d
uri query foo bar
```

Rimuove il parametro `foo` dalla query:

```caddy-d
uri query -foo
```

Rinomina il parametro di query `foo` in `bar`:

```caddy-d
uri query foo>bar
```

Aggiunge il parametro `bar` alla query:

```caddy-d
uri query +foo bar
```

Sostituisce il valore del parametro di query `foo` dove il valore inizia con `bar` con `baz`:

```caddy-d
uri query foo ^(ba)r $1z
```

Esegue più operazioni sulla query contemporaneamente:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	rinominaquesto>rinominato
}
```
