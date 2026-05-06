---
title: header (direttiva del Caddyfile)
---

# header

Manipola i campi dell'header della risposta HTTP. Può impostare, aggiungere ed eliminare i valori dell'header, o eseguire sostituzioni utilizzando espressioni regolari.

Per impostazione predefinita, le operazioni sugli header vengono eseguite immediatamente, a meno che uno degli header non venga eliminato (prefisso `-`) o non venga impostato un valore predefinito (prefisso `?`). In tali casi, le operazioni sugli header vengono posticipate automaticamente fino al momento in cui vengono scritte al client.

Per manipolare gli header delle richieste HTTP, potete usare la direttiva [`request_header`](request_header).


## Sintassi

```caddy-d
header [<matcher>] [[+|-|?|>]<campo> [<valore>|<ricerca>] [<sostituzione>]] {
	# Aggiunta
	+<campo> <valore>

	# Impostazione
	<campo> <valore>

	# Impostazione con posticipazione (defer)
	><campo> <valore>

	# Eliminazione
	-<campo>

	# Sostituzione
	<campo> <ricerca> <sostituzione>

	# Sostituzione con posticipazione (defer)
	><campo> <ricerca> <sostituzione>

	# Valore predefinito (Default)
	?<campo> <valore>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;campo&gt;** è il nome del campo header.

  Senza prefisso, il campo viene impostato (sovrascritto).

  Prefisso con `+` per aggiungere il campo invece di sovrascriverlo se esiste già; i campi header possono apparire più di una volta in una risposta.

  Prefisso con `-` per eliminare il campo. Il campo può usare le wildcard `*` all'inizio o alla fine per eliminare tutti i campi corrispondenti.

  Prefisso con `?` per impostare un valore predefinito per il campo. Il campo viene scritto solo se non esiste ancora.

  Prefisso con `>` per impostare il campo e abilitare `defer`, come scorciatoia.

- **&lt;valore&gt;** è il valore del campo dell'header, quando si aggiunge o si imposta un campo.

- **&lt;ricerca&gt;** è l'espressione regolare da cercare. Possono essere usati i placeholder per un input dinamico nel pattern di ricerca. Il linguaggio delle espressioni regolari utilizzato è RE2, incluso in Go. Consultate il [riferimento alla sintassi RE2](https://github.com/google/re2/wiki/Syntax) e la [panoramica della sintassi regexp di Go](https://pkg.go.dev/regexp/syntax).

- **&lt;sostituzione&gt;** è il valore di sostituzione; obbligatorio se si esegue una ricerca e sostituzione. Usate `$1` o `$2` e così via per fare riferimento ai gruppi di cattura dal pattern di ricerca. Se il valore di sostituzione è `""`, il testo corrispondente viene rimosso dal valore. Consultate la [documentazione di Go](https://golang.org/pkg/regexp/#Regexp.Expand) per i dettagli.

- **defer** posticipa l'esecuzione delle operazioni sugli header fino a quando la risposta non viene inviata al client. Questa opzione viene abilitata automaticamente nelle seguenti condizioni:
	- Quando qualsiasi campo header viene eliminato usando `-`.
	- Quando si imposta un valore predefinito con `?`.
	- Quando si usa il prefisso `>` su un'operazione di impostazione o sostituzione.
	- Quando sono presenti una o più condizioni `match`.

- **match** <span id="match"/> è un [matcher di risposta](/docs/caddyfile/response-matchers) inline. Le operazioni sugli header vengono applicate solo alle risposte che soddisfano le condizioni specificate.

Per manipolazioni multiple degli header, potete aprire un blocco e specificare una manipolazione per riga allo stesso modo.

Quando si usa il prefisso `?` per impostare un valore predefinito dell'header, questo viene automaticamente separato nel proprio handler `header`, se si trovava in un blocco `header` con più operazioni. [Sotto il cofano](/docs/modules/http.handlers.headers#response/require), l'uso di `?` configura un [matcher di risposta](/docs/caddyfile/response-matchers) che si applica all'intero handler della direttiva, che applica solo le operazioni sull'header (come `defer`), ma solo se il campo non è ancora impostato.


## Esempi

Imposta un campo header personalizzato su tutte le risposte:

```caddy-d
header Custom-Header "Mio valore"
```

Rimuove il campo header "Hidden":

```caddy-d
header -Hidden
```

Sostituisce `http://` con `https://` in qualsiasi header Location:

```caddy-d
header Location http:// https://
```

Imposta gli header di sicurezza e privacy su tutte le pagine: (**ATTENZIONE:** usare solo se se ne comprendono le implicazioni!)

```caddy-d
header {
	# disabilita il tracciamento FLoC
	Permissions-Policy interest-cohort=()

	# abilita HSTS
	Strict-Transport-Security max-age=31536000;

	# impedisce ai client di eseguire lo sniffing del tipo di media
	X-Content-Type-Options nosniff

	# protezione dal clickjacking
	X-Frame-Options DENY
}
```

Direttive header multiple intese come mutualmente esclusive:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Imposta una scadenza predefinita della cache se l'upstream non ne definisce una:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Contrassegna tutte le risposte positive alle richieste GET come memorizzabili in cache fino a un'ora:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Impedisce la memorizzazione in cache delle risposte di errore in caso di eccezione nel server upstream:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Contrassegna le risposte in modalità chiara come memorizzabili in cache separatamente dalle risposte in modalità scura se il server upstream supporta i client hint:
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Previene header CORS eccessivamente permissivi sostituendo i valori wildcard con un dominio specifico:
```caddy-d
header >Access-Control-Allow-Origin "\*" "partner-consentito.com"
reverse_proxy upstream:443
```
**Nota**: Nelle operazioni di sostituzione, il valore `<ricerca>` viene interpretato come un'espressione regolare. Per far corrispondere il carattere `*`, deve essere preceduto da un backslash come mostrato nell'esempio sopra.

In alternativa, potete usare un [matcher di risposta](/docs/caddyfile/response-matchers) per far corrispondere un valore di header letterale:
```caddy-d
header Access-Control-Allow-Origin "partner-consentito.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Per sovrascrivere la scadenza della cache che un upstream proxy aveva impostato per i percorsi che iniziano con `/no-cache`; è necessario abilitare `defer` per garantire che l'header venga impostato *dopo* che il proxy ha scritto i suoi header:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Per eseguire un aggiornamento posticipato di un header `Set-Cookie` per aggiungere `SameSite=None`; viene usata una cattura regexp per prelevare il valore esistente, e `$1` lo reinserisce all'inizio con l'opzione aggiuntiva in append:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
