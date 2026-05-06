---
title: Matcher di richiesta (Caddyfile)
---

<script>
ready(function() {
	// Aggiungeremo dei link ai matcher nei blocchi di codice
	// ai loro tag anchor associati.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Collega i token matcher in base al loro contenuto alla sezione sintassi
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Token matcher">${text}</a>`;
	});
});
</script>

# Matcher di richiesta

I **matcher di richiesta** possono essere usati per filtrare (o classificare) le richieste in base a vari criteri.

- [Sintassi](#sintassi)
	- [Esempi](#esempi)
	- [Matcher wildcard](#wildcard-matchers)
	- [Matcher di percorso](#path-matchers)
	- [Matcher con nome](#named-matchers)
- [Matcher standard](#matcher-standard)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


## Sintassi

<a id="sintassi"></a>
Nel Caddyfile, un **token matcher** che segue immediatamente la direttiva può limitarne l'ambito. Il token matcher può assumere una di queste forme:

1. [**`*`**](#wildcard-matchers) per far corrispondere tutte le richieste (wildcard; predefinito).
2. [**`/percorso`**](#path-matchers) iniziare con una barra in avanti per far corrispondere un percorso di richiesta.
3. [**`@nome`**](#named-matchers) per specificare un *matcher con nome*.

If una direttiva supporta i matcher, apparirà come `[<matcher>]` nella documentazione della sua sintassi. I token matcher sono [solitamente opzionali](/docs/caddyfile/directives#syntax), indicati dalle parentesi quadre `[ ]`. Se il token matcher viene omesso, equivale a un matcher wildcard (`*`).


#### Esempi

<a id="esempi"></a>
Questa direttiva si applica a [tutte](#wildcard-matchers) le richieste HTTP:

```caddy-d
reverse_proxy localhost:9000
```

E questo è lo stesso (`*` non è necessario qui):

```caddy-d
reverse_proxy * localhost:9000
```

Ma questa direttiva si applica solo alle richieste con un [percorso](#path-matchers) che inizia con `/api/`:

```caddy-d
reverse_proxy /api/* localhost:9000
```

Per far corrispondere qualsiasi cosa diversa da un percorso, definire un [matcher con nome](#named-matchers) e riferirvisi usando `@nome`:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




### Matcher wildcard

<a id="wildcard-matchers"></a>
Il matcher wildcard (o "catch-all") `*` corrisponde a tutte le richieste ed è necessario solo se è richiesto un token matcher. Ad esempio, se il primo argomento che si desidera fornire a una direttiva capita di essere un percorso, sembrerebbe esattamente un matcher di percorso! Potete quindi usare un matcher wildcard per eliminare l'ambiguità, ad esempio:

```caddy-d
root * /home/www/miosito
```

In caso contrario, questo matcher non viene usato spesso. Raccomandiamo generalmente di ometterlo se la sintassi non lo richiede.


### Matcher di percorso

<a id="path-matchers"></a>
La corrispondenza tramite percorso URI è il modo più comune per filtrare le richieste, quindi il matcher può essere inserito inline, così:

```caddy-d
redir /vecchia.html /nuova.html
```

I token matcher di percorso devono iniziare con una barra in avanti `/`.

**[Il matching del percorso](#path) è una corrispondenza esatta per impostazione predefinita, non per prefisso.** È necessario aggiungere un `*` per una corrispondenza rapida del prefisso. Notate che `/foo*` corrisponderà a `/foo` e `/foo/`, oltre che a `/foobar`; potreste invece volere `/foo/*`.


### Matcher con nome

<a id="named-matchers"></a>
Tutti i matcher che non sono di percorso o wildcard devono essere matcher con nome. Si tratta di matcher definiti all'esterno di qualsiasi particolare direttiva e che possono essere riutilizzati.

Definire un matcher con un nome unico vi offre maggiore flessibilità, consentendovi di combinare [qualsiasi matcher disponibile](#matcher-standard) in un set:

```caddy-d
@nome {
	...
}
```

oppure, se c'è un solo matcher nel set, potete metterlo sulla stessa riga:

```caddy-d
@nome ...
```

Potete quindi usare il matcher in questo modo, specificandolo come primo argomento di una direttiva:

```caddy-d
direttiva @nome
```

Per esempio, questo instrada le richieste websocket HTTP/1.1 verso `localhost:6001` e le altre richieste verso `localhost:8080`. Corrisponde alle richieste che hanno un campo header chiamato `Connection` *contenente* `Upgrade`, **e** un altro campo chiamato `Upgrade` con valore esatto `websocket`:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Se il set di matcher consiste in un solo matcher, funziona anche la sintassi su una riga:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

Come caso speciale, il [matcher `expression`](#expression) può essere usato senza specificarne il nome, purché un argomento [virgolettato](/docs/caddyfile/concepts#tokens-and-quotes) (l'espressione CEL stessa) segua il nome del matcher:

```caddy-d
@not-found `{err.status_code} == 404`
```

Come le direttive, le definizioni dei matcher con nome devono trovarsi all'interno dei [blocchi sito](/docs/caddyfile/concepts#struttura) che li utilizzano.

Una definizione di matcher con nome costituisce un *set di matcher*. I matcher in un set sono uniti dall'operatore logico AND; ovvero, tutti devono corrispondere. Ad esempio, se avete sia un matcher [`header`](#header) che un matcher [`path`](#path) nel set, entrambi devono corrispondere.

Più matcher dello stesso tipo possono essere uniti (es. più matcher [`path`](#path) nello stesso set) utilizzando l'algebra booleana (AND/OR), come descritto nelle rispettive sezioni di seguito.

Per una logica di matching booleana più complessa, si raccomanda il [matcher `expression`](#expression) per scrivere un'espressione CEL, che supporta **and** `&&`, **or** `||` e le **parentesi** `( )`.





## Matcher standard

<a id="standard-matchers"></a>
La documentazione completa dei matcher si trova [nei documenti di ogni rispettivo modulo matcher](/docs/json/apps/http/servers/routes/match/).

Le richieste possono essere filtrate nei seguenti modi:



### client_ip

<a id="client-ip"></a>
```caddy-d
client_ip <intervalli...>

expression client_ip('<intervalli...>')
```

In base all'indirizzo IP del client. Accetta IP esatti o intervalli CIDR. Sono supportate le zone IPv6.

Questo matcher è usato al meglio quando l'[opzione globale `trusted_proxies`](/docs/caddyfile/options#trusted-proxies) è configurata, altrimenti agisce in modo identico al matcher [`remote_ip`](#remote-ip). Solo le richieste provenienti da proxy fidati avranno il loro IP client analizzato all'inizio della richiesta; le richieste non fidate useranno l'indirizzo IP remoto del peer immediato o l'indirizzo impostato tramite il [protocollo PROXY](/docs/caddyfile/options#proxy-protocol).

Come scorciatoia, `private_ranges` può essere usato per far corrispondere tutti gli intervalli privati IPv4 e IPv6. Equivale a specificare tutti questi intervalli: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Possono esserci più matcher `client_ip` per ogni matcher con nome e i loro intervalli verranno uniti in OR tra loro.

#### Esempio:

Far corrispondere le richieste provenienti da indirizzi IPv4 privati:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Questo matcher è comunemente accoppiato al matcher [`not`](#not) per invertire la corrispondenza. Ad esempio, per interrompere tutte le connessioni da indirizzi IPv4 e IPv6 *pubblici* (che è l'inverso di tutti gli intervalli privati):

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Ciao, devi provenire da una rete privata!"
}
```

In una [espressione CEL](#expression), apparirebbe così:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

<a id="expression"></a>
```caddy-d
expression <cel...>
```

In base a qualsiasi espressione [CEL (Common Expression Language)](https://github.com/google/cel-spec) che restituisca `true` o `false`.

La maggior parte degli altri matcher di richiesta può essere usata nelle espressioni come funzioni, il che consente maggiore flessibilità per la logica booleana rispetto alle espressioni esterne. Consultate la documentazione di ciascun matcher per la sintassi supportata all'interno delle espressioni CEL.

I [placeholder](/docs/conventions#placeholders) di Caddy (o le [scorciatoie del Caddyfile](/docs/caddyfile/concepts#placeholders)) possono essere usati in queste espressioni CEL, poiché vengono pre-elaborati e convertiti in normali chiamate di funzione CEL prima di essere interpretati dall'ambiente CEL. Se un placeholder deve essere passato come argomento stringa a una funzione matcher, allora la `{` iniziale dovrebbe essere preceduta da un backslash `\` in modo che non venga pre-elaborata, ad esempio `file('\{path}.md')`.

Per comodità, il nome del matcher può essere omesso se si definisce un matcher con nome composto esclusivamente da un'espressione CEL. L'espressione CEL deve essere [virgolettata](/docs/caddyfile/concepts#tokens-and-quotes) (consigliati backtick o heredoc). Si legge piuttosto bene:

```caddy-d
@mutable `{method}.startsWith("P")`
```

In questo caso si assume il matcher CEL.

#### Esempi:

Far corrispondere le richieste i cui metodi iniziano con `P`, es. `PUT` o `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

Far corrispondere le richieste in cui l'handler ha restituito il codice di stato di errore `404`, da usare in combinazione con la [direttiva `handle_errors`](/docs/caddyfile/directives/handle_errors):

```caddy-d
@404 expression {err.status_code} == 404
```

Far corrispondere le richieste in cui il percorso corrisponde a una di due diverse espressioni regolari; questo è possibile solo usando un'espressione, perché il matcher [`path_regexp`](#path-regexp) può normalmente esistere una sola volta per ogni matcher con nome:

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

O lo stesso, omettendo il nome del matcher e racchiudendolo tra [backtick](/docs/caddyfile/concepts#tokens-and-quotes) in modo che venga analizzato come un unico token:

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

Potete usare la [sintassi heredoc](/docs/caddyfile/concepts#heredocs) per scrivere espressioni CEL su più righe:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Ciao, API!"
```


---
### file

<a id="file"></a>
```caddy-d
file {
	root       <percorso>
	try_files  <file...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delimitatori...>
}
file <file...>

expression `file({
	'root': '<percorso>',
	'try_files': ['<file...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delimitatori...>']
})`
expression file('<file...>')
```

In base ai file.

- `root` definisce la directory in cui cercare i file. Il valore predefinito è la directory di lavoro corrente, o la [variabile](/docs/modules/http.handlers.vars) `root` (`{http.vars.root}`) se impostata (può essere impostata tramite la [direttiva `root`](/docs/caddyfile/directives/root)).

- `try_files` controlla i file nel suo elenco che corrispondono alla try_policy.

  Per far corrispondere una directory, aggiungere una barra in avanti `/` finale al percorso. Tutti i percorsi dei file sono relativi alla [root](/docs/caddyfile/directives/root) del sito e i [pattern glob](https://pkg.go.dev/path/filepath#Match) verranno espansi.

  Se la `try_policy` è `first_exist` (quella predefinita), allora l'ultimo elemento dell'elenco può essere un numero preceduto da `=` (es. `=404`), che come fallback genererà un errore con quel codice; l'errore può essere intercettato e gestito con [`handle_errors`](/docs/caddyfile/directives/handle_errors).



- `try_policy` specifica come scegliere un file. Il valore predefinito è `first_exist`.

	- `first_exist` controlla l'esistenza del file. Viene selezionato il primo file esistente.

	- `first_exist_fallback` è simile a `first_exist`, ma assume che l'ultimo elemento della lista esista sempre per evitare un accesso al disco.

	- `smallest_size` sceglie il file con la dimensione minore.

	- `largest_size` sceglie il file con la dimensione maggiore.

	- `most_recently_modified` sceglie il file modificato più recentemente.

- `split_path` causerà la suddivisione del percorso al primo delimitatore dell'elenco che viene trovato in ogni percorso file da provare. Per ogni valore suddiviso, la parte sinistra della suddivisione, includendo il delimitatore stesso, sarà il percorso file provato. Ad esempio, `/remote.php/dav/` usando il delimitatore `.php` proverebbe il file `/remote.php`. Ogni delimitatore deve apparire alla fine di un componente del percorso URI per essere usato come delimitatore di suddivisione. Questa è un'impostazione di nicchia e viene usata principalmente quando si servono siti PHP.

Poiché `try_files` con la policy `first_exist` è molto comune, esiste una scorciatoia su una sola riga per questo:

```caddy-d
file <file...>
```

Un matcher `file` vuoto (uno senza alcun file elencato dopo di esso) verificherà se il file richiesto &mdash; così com'è dall'URI, relativo alla [root del sito](/docs/caddyfile/directives/root) &mdash; esiste. Equivale a `file {path}`.


<aside class="tip">
	Poiché la riscrittura basata sull'esistenza di un file su disco è molto comune, esiste anche una [direttiva `try_files`](/docs/caddyfile/directives/try_files) che è una scorciatoia del matcher `file` e di un [handler `rewrite`](/docs/caddyfile/directives/rewrite).
</aside>


In caso di corrispondenza, saranno resi disponibili quattro nuovi placeholder:

- `{file_match.relative}` Il percorso del file relativo alla root. È spesso utile per riscrivere le richieste.
- `{file_match.absolute}` Il percorso assoluto del file corrispondente, includendo la root.
- `{file_match.type}` Il tipo di file, `file` o `directory`.
- `{file_match.remainder}` La porzione rimanente dopo la suddivisione del percorso file (se `split_path` è configurato).


#### Esempi:

Far corrispondere le richieste in cui il percorso è un file esistente:

```caddy-d
@file file
```

Far corrispondere le richieste in cui il percorso seguito da `.html` è un file esistente o, in caso contrario, in cui il percorso è un file esistente:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

Lo stesso di sopra, ma usando la scorciatoia su una riga e ripiegando sulla generazione di un errore 404 se il file non viene trovato:

```caddy-d
@html-or-error file {path}.html {path} =404
```

Altri esempi che usano le [espressioni CEL](#expression). Tenete a mente che i placeholder vengono pre-elaborati e convertiti in normali chiamate di funzione CEL prima di essere interpretati dall'ambiente CEL, quindi qui viene usata la concatenazione. Inoltre, deve essere usata la forma estesa se si concatena con dei placeholder a causa delle attuali limitazioni del parser:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

<a id="header"></a>
```caddy-d
header <campo> [<valore> ...]

expression header({'<campo>': '<valore>'})
```

In base ai campi dell'header della richiesta.

- `<campo>` è il nome del campo header HTTP da controllare.
	- Se preceduto da `!`, il campo non deve esistere per corrispondere (omettere l'argomento valore).
- `<valore>` è il valore che il campo deve avere per corrispondere. Ne può essere specificato uno o più.
	- Se preceduto da `*`, esegue una corrispondenza rapida del suffisso (appare alla fine).
	- Se terminante con `*`, esegue una corrispondenza rapida del prefisso (appare all'inizio).
	- Se racchiuso tra `*`, esegue una corrispondenza rapida della sottostringa (appare ovunque).
	- Altrimenti, è una corrispondenza esatta rapida.

Diversi campi header all'interno dello stesso set sono uniti in AND. Più valori per lo stesso campo sono uniti in OR.

Si noti che i campi header possono essere ripetuti e avere valori diversi. Le applicazioni backend DEVONO considerare che i valori dei campi header sono array, non valori singoli, e Caddy non interpreta il significato in tali casi.

#### Esempio:

Far corrispondere le richieste con l'header `Connection` contenente `Upgrade`:

```caddy-d
@upgrade header Connection *Upgrade*
```

Far corrispondere le richieste con l'header `Foo` contenente `bar` OPPURE `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Far corrispondere le richieste che non hanno affatto il campo header `Foo`:

```caddy-d
@not_foo header !Foo
```

Usando una [espressione CEL](#expression), far corrispondere le richieste WebSocket controllando che l'header `Connection` contenga `Upgrade` e l'header `Upgrade` sia uguale a `websocket` (HTTP/2 usa l'header `:protocol` per questo):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
### header_regexp

<a id="header-regexp"></a>
```caddy-d
header_regexp [<nome>] <campo> <regexp>

expression header_regexp('<nome>', '<campo>', '<regexp>')
expression header_regexp('<campo>', '<regexp>')
```

Come [`header`](#header), ma supporta le espressioni regolari.

Il linguaggio delle espressioni regolari utilizzato è RE2, incluso in Go. Consultate il [riferimento alla sintassi RE2](https://github.com/google/re2/wiki/Syntax) e la [panoramica della sintassi regexp di Go](https://pkg.go.dev/regexp/syntax).

A partire dalla v2.8.0, se `nome` *non* viene fornito, il nome verrà preso dal nome del matcher con nome. Ad esempio, un matcher con nome `@foo` farà sì che questo matcher venga chiamato `foo`. Il vantaggio principale di specificare un nome è se più di un matcher regexp (es. `header_regexp` e [`path_regexp`](#path-regexp), o diversi campi header) viene usato nello stesso matcher con nome.

È possibile accedere ai gruppi di cattura tramite [placeholder](/docs/caddyfile/concepts#placeholders) nelle direttive dopo la corrispondenza:
- `{re.<nome>.<gruppo_cattura>}` dove:
  - `<nome>` è il nome dell'espressione regolare,
  - `<gruppo_cattura>` è il nome o il numero del gruppo di cattura nell'espressione.

- `{re.<gruppo_cattura>}` senza nome, è popolato per comodità. L'avvertenza è che se più matcher regexp vengono usati in sequenza, i valori dei placeholder verranno sovrascritti dal matcher successivo.

Il gruppo di cattura `0` è l'intera corrispondenza regexp, `1` è il primo gruppo di cattura, `2` il secondo e così via. Quindi `{re.foo.1}` o `{re.1}` conterranno entrambi il valore del primo gruppo di cattura.

È supportata una sola espressione regolare per campo header, poiché i pattern regexp non possono essere uniti; se ne servono di più, considerate l'uso di un [matcher `expression`](#expression). Le corrispondenze contro più campi header diversi saranno unite in AND.

#### Esempio:

Far corrispondere le richieste in cui l'header Cookie contiene `login_` seguito da una stringa esadecimale, con un gruppo di cattura accessibile con `{re.login.1}` o `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Può essere semplificato omettendo il nome, che verrà dedotto dal matcher con nome:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

O lo stesso, usando un' [espressione CEL](#expression):

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

<a id="host"></a>
```caddy-d
host <host...>

expression host('<host...>')
```

Filtra la richiesta in base al campo header `Host` della richiesta.

Dato che la maggior parte dei blocchi sito indica già gli host nell'indirizzo del sito, questo matcher è più comunemente usato nei blocchi sito che usano un hostname wildcard (vedere il [pattern dei certificati wildcard](/docs/caddyfile/patterns#wildcard-certificates)), ma dove è richiesta una logica specifica per l'hostname.

Più matcher `host` saranno uniti in OR tra loro.

#### Esempio:

Far corrispondere un sottodominio:

```caddy-d
@sub host sub.example.com
```

Far corrispondere il dominio apex e un sottodominio:

```caddy-d
@site host example.com www.example.com
```

Più sottodomini usando un' [espressione CEL](#expression):

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

<a id="method"></a>
```caddy-d
method <verbi...>

expression method('<verbi...>')
```

In base al metodo (verbo) della richiesta HTTP. I verbi dovrebbero essere maiuscoli, come `POST`. Può far corrispondere uno o più metodi.

Più matcher `method` saranno uniti in OR tra loro.

#### Esempi:

Far corrispondere le richieste con il metodo `GET`:

```caddy-d
@get method GET
```

Far corrispondere le richieste con i metodi `PUT` o `DELETE`:

```caddy-d
@put-delete method PUT DELETE
```

Far corrispondere i metodi di sola lettura usando un' [espressione CEL](#expression):

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

<a id="not"></a>
```caddy-d
not <matcher>
```

oppure, per negare più matcher che vengono uniti in AND, aprire un blocco:

```caddy-d
not {
	<matcher...>
}
```

I risultati dei matcher racchiusi saranno negati.

#### Esempi:

Far corrispondere le richieste con percorsi che NON iniziano con `/css/` OPPURE `/js/`.

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

Far corrispondere le richieste che NON HANNO NÉ:
- un prefisso di percorso `/api/`, NÉ
- il metodo di richiesta `POST`

ovvero, non deve esserci nessuno di questi per corrispondere:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

Far corrispondere le richieste che NON HANNO ENTRAMBI:
- un prefisso di percorso `/api/`, E
- il metodo di richiesta `POST`

ovvero, non deve esserci nessuno dei due o solo uno dei due per corrispondere:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

Non esiste una [espressione CEL](#expression) per questo matcher, perché si può usare l'operatore `!` per la negazione. Ad esempio:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

Che è lo stesso di questo, usando le parentesi:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

<a id="path"></a>
```caddy-d
path <percorsi...>

expression path('<percorsi...>')
```

In base al percorso della richiesta (la componente percorso dell'URI della richiesta). Le corrispondenze dei percorsi sono esatte ma non fanno distinzione tra maiuscole e minuscole. È possibile usare le wildcard `*`:

- Solo alla fine, per una corrispondenza del prefisso (`/prefisso/*`)
- Solo all'inizio, per una corrispondenza del suffisso (`*.suffisso`)
- Solo su entrambi i lati, per una corrispondenza della sottostringa (`*/contiene/*`)
- Solo nel mezzo, per una corrispondenza glob (`/account/*/info`)

Le barre sono significative. Ad esempio, `/foo*` corrisponderà a `/foo`, `/foobar`, `/foo/` e `/foo/bar`, ma `/foo/*` *non* corrisponderà a `/foo` o `/foobar`.

I percorsi delle richieste vengono puliti per risolvere i punti di attraversamento delle directory (directory traversal) prima della corrispondenza. Inoltre, più barre vengono unite a meno che il pattern di corrispondenza non abbia più barre. In altre parole, `/foo` corrisponderà a `/foo` e `//foo`, ma `//foo` corrisponderà solo a `//foo`.

Poiché esistono più forme escaped di un dato URI, il percorso della richiesta viene normalizzato (URL-decoded, unescaped) ad eccezione di quelle sequenze di escape in posizioni in cui le sequenze di escape sono presenti anche nel pattern di corrispondenza. Ad esempio, `/foo/bar` corrisponde sia a `/foo/bar` che a `/foo%2Fbar`, ma `/foo%2Fbar` corrisponderà solo a `/foo%2Fbar`, perché la sequenza di escape è esplicitamente indicata nella configurazione.

Lo speciale escape wildcard `%*` può anche essere usato al posto di `*` per lasciare la sua parte corrispondente escaped. Ad esempio, `/band/*/*` non corrisponderà a `/band/AC%2FDC/T.N.T` perché il percorso verrà confrontato nello spazio normalizzato dove appare come `/band/AC/DC/T.N.T`, che non corrisponde al pattern; tuttavia, `/band/%*/*` corrisponderà a `/band/AC%2FDC/T.N.T` perché la parte rappresentata da `%*` verrà confrontata senza decodificare le sequenze di escape.

Più percorsi saranno uniti in OR tra loro.

#### Esempi:

Far corrispondere più directory e il loro contenuto:

```caddy-d
@assets path /js/* /css/* /images/*
```

Far corrispondere un file specifico:

```caddy-d
@favicon path /favicon.ico
```

Far corrispondere estensioni di file:

```caddy-d
@extensions path *.js *.css
```

Con una [espressione CEL](#expression):

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
### path_regexp

<a id="path-regexp"></a>
```caddy-d
path_regexp [<nome>] <regexp>

expression path_regexp('<nome>', '<regexp>')
expression path_regexp('<regexp>')
```

Come [`path`](#path), ma supporta le espressioni regolari. Viene eseguito sul percorso decodificato dall'URI/unescaped.

Il linguaggio delle espressioni regolari utilizzato è RE2, incluso in Go. Consultate il [riferimento alla sintassi RE2](https://github.com/google/re2/wiki/Syntax) e la [panoramica della sintassi regexp di Go](https://pkg.go.dev/regexp/syntax).

A partire dalla v2.8.0, se `nome` *non* viene fornito, il nome verrà preso dal nome del matcher con nome. Ad esempio, un matcher con nome `@foo` farà sì che questo matcher venga chiamato `foo`. Il vantaggio principale di specificare un nome è se più di un matcher regexp (es. `path_regexp` e [`header_regexp`](#header-regexp)) viene usato nello stesso matcher con nome.

È possibile accedere ai gruppi di cattura tramite [placeholder](/docs/caddyfile/concepts#placeholders) nelle direttive dopo la corrispondenza:
- `{re.<nome>.<gruppo_cattura>}` dove:
  - `<nome>` è il nome dell'espressione regolare,
  - `<gruppo_cattura>` è il nome o il numero del gruppo di cattura nell'espressione.

- `{re.<gruppo_cattura>}` senza nome, è popolato per comodità. L'avvertenza è che se più matcher regexp vengono usati in sequenza, i valori dei placeholder verranno sovrascritti dal matcher successivo.

Il gruppo di cattura `0` è l'intera corrispondenza regexp, `1` è il primo gruppo di cattura, `2` il secondo e così via. Quindi `{re.foo.1}` o `{re.1}` conterranno entrambi il valore del primo gruppo di cattura.

Può esserci solo un pattern `path_regexp` per ogni matcher con nome, poiché questo matcher non può essere unito a se stesso; se ne servono di più, considerate l'uso di un [matcher `expression`](#expression).

#### Esempio:

Far corrispondere le richieste in cui il percorso termina con una stringa esadecimale di 6 caratteri seguita da `.css` o `.js` come estensione del file, con gruppi di cattura (parti racchiuse tra `( )`), che possono essere acceduti rispettivamente con `{re.static.1}` e `{re.static.2}` (o `{re.1}` e `{re.2}`):

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Può essere semplificato omettendo il nome, che verrà dedotto dal matcher con nome:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

O lo stesso, usando un' [espressione CEL](#expression), convalidando anche che il [`file`](#file) esista su disco:

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

<a id="protocol"></a>
```caddy-d
protocol http|https|grpc|http/<versione>[+]

expression protocol('http|https|grpc|http/<versione>[+]')
```

In base al protocollo della richiesta. Può essere usato un nome generico di protocollo come `http`, `https` o `grpc`; oppure versioni HTTP specifiche o minime come `http/1.1` o `http/2+`.

Può esserci un solo matcher `protocol` per ogni matcher con nome.

#### Esempio:

Far corrispondere le richieste che usano HTTP/2:

```caddy-d
@http2 protocol http/2+
```

Con una [espressione CEL](#expression):

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

<a id="query"></a>
```caddy-d
query <chiave>=<valore>...
query ""

expression query({'<chiave>': '<valore>'})
expression query({'<chiave>': ['<valori...>']})
```

In base ai parametri della stringa di query. Dovrebbe essere una sequenza di coppie `chiave=valore`, o una stringa vuota "". Le chiavi vengono confrontate esattamente (facendo distinzione tra maiuscole e minuscole) ma supportano anche `*` per far corrispondere qualsiasi valore. I valori possono usare i placeholder. Una stringa vuota fa corrispondere le richieste HTTP senza parametri di query.

Possono esserci più matcher `query` per ogni matcher con nome e le coppie con le stesse chiavi saranno unite in OR tra loro. Chiavi diverse saranno unite in AND. Quindi, tutte le chiavi nel matcher devono avere almeno un valore corrispondente.

Le stringhe di query illegali (sintassi errata, punti e virgola non escaped, ecc.) non verranno analizzate e quindi non corrisponderanno.

**NOTA:** I parametri della stringa di query sono array, non valori singoli. Questo perché le chiavi ripetute sono valide nelle stringhe di query e ognuna può avere un valore diverso. Questo matcher corrisponderà per una chiave se uno qualsiasi dei suoi valori configurati è assegnato nella stringa di query. Le applicazioni backend che utilizzano le stringhe di query DEVONO tenere in considerazione che i valori della stringa di query sono array e possono avere più valori.

#### Esempio:

Far corrispondere un parametro di query `q` con qualsiasi valore:

```caddy-d
@search query q=*
```

Far corrispondere un parametro di query `sort` con il valore `asc` o `desc`:

```caddy-d
@sorted query sort=asc sort=desc
```

Far corrispondere sia `q` che `sort`, con un' [espressione CEL](#expression):

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
### remote_ip

<a id="remote-ip"></a>
```caddy-d
remote_ip <intervalli...>

expression remote_ip('<intervalli...>')
```

In base all'indirizzo IP remoto (ovvero l'indirizzo IP del peer immediato o l'indirizzo impostato tramite il [protocollo PROXY](/docs/caddyfile/options#proxy-protocol)). Accetta IP esatti o intervalli CIDR. Sono supportate le zone IPv6.

Como scorciatoia, `private_ranges` può essere usato per far corrispondere tutti gli intervalli privati IPv4 e IPv6. Equivale a specificare tutti questi intervalli: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Se desiderate far corrispondere l'"IP reale" del client, come analizzato dagli header HTTP, usate invece il matcher [`client_ip`](#client-ip).

Possono esserci più matcher `remote_ip` per ogni matcher con nome e i loro intervalli verranno uniti in OR tra loro.

#### Esempio:

Far corrispondere le richieste provenienti da indirizzi IPv4 privati:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Questo matcher è comunemente accoppiato al matcher [`not`](#not) per invertire la corrispondenza. Ad esempio, per interrompere tutte le connessioni da indirizzi IPv4 e IPv6 *pubblici* (che è l'inverso di tutti gli intervalli privati):

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Ciao, devi provenire da una rete privata!"
}
```

In una [espressione CEL](#expression), apparirebbe così:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

<a id="vars"></a>
```caddy-d
vars <variabile> <valori...>

expression vars({'<variabile>': '<valore>'})
expression vars({'<variabile>': ['<valori...>']})
```

In base al valore di una variabile nel contesto della richiesta, o al valore di un placeholder. Possono essere specificati più valori per far corrispondere uno qualsiasi di tali valori possibili (OR).

L'argomento **&lt;variabile&gt;** può essere un nome di variabile o un placeholder tra parentesi graffe `{ }` (i placeholder non vengono espansi nel primo parametro).

Questo matcher è più utile se accoppiato con la [direttiva `map`](/docs/caddyfile/directives/map) che imposta degli output, con la [direttiva `vars`](/docs/caddyfile/directives/vars) all'interno delle vostre rotte, o con plugin che impostano alcune informazioni nel contesto della richiesta.

#### Esempio:

Far corrispondere un output della [direttiva `map`](/docs/caddyfile/directives/map) chiamato `magic_number` per i valori `3` o `5`:

```caddy-d
vars {magic_number} 3 5
```

Far corrispondere il valore di un placeholder arbitrario, es. l'ID dell'utente autenticato, che sia `Bob` o `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Un esempio completo che usa la [direttiva `vars`](/docs/caddyfile/directives/vars) per impostare una variabile e poi filtrarla con il [matcher `vars`](#vars). Qui combiniamo due header di richiesta in una variabile e filtriamo in base a quella variabile:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "Hai inviato Foo=123 e Bar=456!"
	}
	handle {
		respond "Foo e Bar non erano speciali."
	}
}
```

In una [espressione CEL](#expression), apparirebbe così:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
### vars_regexp

<a id="vars-regexp"></a>
```caddy-d
vars_regexp [<nome>] <variabile> <regexp>

expression vars_regexp('<nome>', '<variabile>', '<regexp>')
expression vars_regexp('<variabile>', '<regexp>')
```

Come [`vars`](#vars), ma supporta le espressioni regolari.

Il linguaggio delle espressioni regolari utilizzato è RE2, incluso in Go. Consultate il [riferimento alla sintassi RE2](https://github.com/google/re2/wiki/Syntax) e la [panoramica della sintassi regexp di Go](https://pkg.go.dev/regexp/syntax).

A partire dalla v2.8.0, se `nome` *non* viene fornito, il nome verrà preso dal nome del matcher con nome. Ad esempio, un matcher con nome `@foo` farà sì che questo matcher venga chiamato `foo`. Il vantaggio principale di specificare un nome è se più di un matcher regexp (es. `vars_regexp` e [`header_regexp`](#header-regexp)) viene usato nello stesso matcher con nome.

È possibile accedere ai gruppi di cattura tramite [placeholder](/docs/caddyfile/concepts#placeholders) nelle direttive dopo la corrispondenza:
- `{re.<nome>.<gruppo_cattura>}` dove:
  - `<nome>` è il nome dell'espressione regolare,
  - `<gruppo_cattura>` è il nome o il numero del gruppo di cattura nell'espressione.

- `{re.<gruppo_cattura>}` senza nome, è popolato per comodità. L'avvertenza è che se più matcher regexp vengono usati in sequenza, i valori dei placeholder verranno sovrascritti dal matcher successivo.

Il gruppo di cattura `0` è l'intera corrispondenza regexp, `1` è il primo gruppo di cattura, `2` il secondo e così via. Quindi `{re.foo.1}` o `{re.1}` conterranno entrambi il valore del primo gruppo di cattura.

È supportata una sola espressione regolare per nome di variabile, poiché i pattern regexp non possono essere uniti; se ne servono di più, considerate l'uso di un [matcher `expression`](#expression). Le corrispondenze contro più variabili diverse saranno unite in AND.

#### Esempio:

Far corrispondere un output della [direttiva `map`](/docs/caddyfile/directives/map) chiamato `magic_number` per un valore che inizia con `4`, catturando il valore in un gruppo di cattura accessibile con `{re.magic.1}` o `{re.1}`:

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Può essere semplificato omettendo il nome, che verrà dedotto dal matcher con nome:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

In una [espressione CEL](#expression), apparirebbe così:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
