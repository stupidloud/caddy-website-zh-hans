---
title: Profiling di Caddy
---

Profiling di Caddy
==================

Un **profilo di un programma** è un'istantanea dell'uso delle risorse da parte di un programma durante la sua esecuzione. I profili possono essere estremamente utili per identificare aree problematiche, risolvere bug e crash e ottimizzare il codice.

Caddy utilizza gli strumenti di Go per l'acquisizione dei profili, chiamati [pprof](https://github.com/google/pprof), che sono integrati nel comando `go`.

I profili riportano informazioni sul consumo di CPU e memoria, mostrano i tracciamenti dello stack (stack trace) dei goroutine e aiutano a rintracciare deadlock o primitive di sincronizzazione con alta contesa.

In caso di segnalazione di alcuni bug in Caddy, potremmo richiedervi un profilo. Questo articolo può esservi d'aiuto: descrive sia come ottenere i profili con Caddy, sia come utilizzare e interpretare i profili pprof in generale.


Due cose da sapere prima di iniziare:

1. **I profili di Caddy NON contengono dati sensibili per la sicurezza.** Contengono letture tecniche innocue, non il contenuto della memoria. Non concedono l'accesso ai sistemi. Sono sicuri da condividere.
2. **I profili sono leggeri e possono essere raccolti in produzione.** In effetti, questa è una pratica consigliata per molti utenti; consultate la parte finale di questo articolo.

## Ottenere i profili

I profili sono disponibili tramite l'[interfaccia di amministrazione](/docs/api) all'indirizzo `/debug/pprof/`. Su una macchina su cui è in esecuzione Caddy, apritelo nel browser:

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	Per impostazione predefinita, l'API di amministrazione è accessibile solo localmente. Se eseguite Caddy in remoto, in VM o in container, consultate la sezione successiva per sapere come accedere a questo endpoint.
</aside>

Noterete una semplice tabella di conteggi e collegamenti, come questa:

Conteggio | Profilo
--------- | --------------------
79        | allocs
0         | block
0         | cmdline
22        | goroutine
79        | heap
0         | mutex
0         | profile
29        | threadcreate
0         | trace
|         | full goroutine stack dump

I conteggi sono un modo pratico per identificare rapidamente eventuali perdite (leak). Se sospettate una perdita, aggiornate ripetutamente la pagina: vedrete uno o più di questi conteggi aumentare costantemente. Se aumenta il conteggio della heap, potrebbe esserci una perdita di memoria; se aumenta quello dei goroutine, potrebbe esserci una perdita di goroutine.

Cliccate sui profili per vedere come appaiono. Alcuni potrebbero essere vuoti, il che è normale per la maggior parte del tempo. I più comuni sono **goroutine** (stack delle funzioni), **heap** (memoria) e **profile** (CPU). Altri profili sono utili per risolvere contese sui mutex o deadlock.

In fondo alla pagina c'è una breve descrizione di ciascun profilo:

- **allocs:** Un campionamento di tutte le passate allocazioni di memoria.
- **block:** Tracciamenti dello stack che hanno portato al blocco su primitive di sincronizzazione.
- **cmdline:** L'invocazione da riga di comando del programma corrente.
- **goroutine:** Tracciamenti dello stack di tutti i goroutine attuali. Usate `debug=2` come parametro di query per esportare nello stesso formato di un panic non recuperato.
- **heap:** Un campionamento delle allocazioni di memoria degli oggetti vivi. Potete specificare il parametro GET `gc` per eseguire il GC prima di prelevare il campione della heap.
- **mutex:** Tracciamenti dello stack dei possessori di mutex contesi.
- **profile:** Profilo della CPU. Potete specificare la durata nel parametro GET `seconds`. Dopo aver ottenuto il file del profilo, usate il comando `go tool pprof` per analizzarlo.
- **threadcreate:** Tracciamenti dello stack che hanno portato alla creazione di nuovi thread del sistema operativo.
- **trace:** Una traccia dell'esecuzione del programma corrente. Potete specificare la durata nel parametro GET `seconds`. Dopo aver ottenuto il file della traccia, usate il comando `go tool trace` per analizzarlo.

<aside class="tip">
	La differenza tra "goroutine" e "full goroutine stack dump" è il parametro `?debug=2`: il dump completo dello stack è simile all'output che vedreste dopo un panic; è più prolisso e, in particolare, non raggruppa i goroutine identici.
</aside>


### Scaricare i profili

Cliccando sui link nella pagina indice di pprof sopra descritta, otterrete i profili in formato testo. Questo è utile per il debugging ed è ciò che preferiamo noi del team di Caddy perché possiamo analizzarlo per cercare indizi evidenti senza bisogno di strumenti aggiuntivi.

Tuttavia, il binario è in realtà il formato predefinito. I link HTML aggiungono il parametro della stringa di query `?debug=` per formattarli come testo, ad eccezione del link "profile" (CPU), che non ha una rappresentazione testuale.

Questi sono i parametri della stringa di query che potete impostare (dalla [documentazione di Go](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (tutti i profili eccetto cpu):** formato della risposta: N = 0: binario (predefinito), N > 0: testo semplice.
- **`gc=N` (profilo heap):** N > 0: esegue un ciclo di garbage collection prima del profiling.
- **`seconds=N` (profili allocs, block, goroutine, heap, mutex, threadcreate):** restituisce un profilo delta.
- **`seconds=N` (profili cpu, trace):** effettua il profilo per la durata data.

Trattandosi di endpoint HTTP, potete usare anche qualsiasi client HTTP come curl o wget per scaricare i profili.

Una volta scaricati i profili, potete caricarli in un commento a una issue di GitHub o usare un sito come [pprof.me](https://pprof.me/). Specificamente per i profili della CPU, un'altra opzione è [flamegraph.com](https://flamegraph.com/).


## Accesso remoto

*Se riuscite già ad accedere all'API di amministrazione localmente, saltate questa sezione.*

Per impostazione predefinita, l'API di amministrazione di Caddy è accessibile solo tramite il socket di loopback. Tuttavia, esistono almeno 3 modi per accedere all'endpoint `/debug/pprof` di Caddy da remoto:

### Reverse proxy tramite il vostro sito

Un'opzione semplice è creare un reverse proxy verso di esso dal vostro sito:

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Questo, ovviamente, renderà i profili disponibili a chiunque possa connettersi al vostro sito. Se ciò non è desiderato, potete aggiungere dell'autenticazione usando un modulo di autenticazione HTTP a vostra scelta.

(Non dimenticate il matcher `/debug/pprof/*`, altrimenti farete il proxy dell'intera API di amministrazione!)


### Tunnel SSH

Un altro modo è usare un tunnel SSH. Si tratta di una connessione crittografata che utilizza il protocollo SSH tra il vostro computer e il server. Eseguite un comando come questo sul vostro computer:

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Questo crea un tunnel da `localhost:8123` (sulla vostra macchina locale) a `localhost:2019` su `example.com`. Assicuratevi di sostituire `username`, `example.com` e le porte secondo necessità.

<aside class="tip">
	Questo comando verrà eseguito in primo piano. Tenete presente che se provate a mettere il processo in background con <kbd>Ctrl</kbd>+<kbd>Z</kbd>, il tunnel verrà messo in pausa e le connessioni che lo utilizzano falliranno.
</aside>

Quindi in un altro terminale potete eseguire `curl` in questo modo:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Potete evitare la necessità di `-H "Host: ..."` usando la porta `2019` su entrambi i lati del tunnel (ma questo richiede che la porta `2019` non sia già occupata sul vostro computer, ovvero che non abbiate Caddy in esecuzione localmente).

Finché il tunnel è attivo, potete accedere a tutta l'API di amministrazione. Digitate <kbd>Ctrl</kbd>+<kbd>C</kbd> sul comando `ssh` per chiudere il tunnel.

#### Tunnel a lunga durata

L'esecuzione di un tunnel con il comando sopra riportato richiede di mantenere il terminale aperto. Se volete eseguire il tunnel in background, potete avviarlo così:

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Questo si avvierà in background e creerà un socket di controllo in `/tmp/caddy-tunnel.sock`. Potrete quindi usare il socket di controllo per chiudere il tunnel quando avrete finito:

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


### API di amministrazione remota

Potete anche configurare l'API di amministrazione per accettare connessioni remote da client autorizzati.

(TODO: Scrivere un articolo al riguardo.)



## Profili dei goroutine

Il dump dei goroutine è utile per sapere quali goroutine esistono e quali sono i loro tracciamenti dello stack (call stack). In altre parole, ci dà un'idea del codice che è attualmente in esecuzione o che è bloccato/in attesa.

Se cliccate su "goroutines" o andate su `/debug/pprof/goroutine?debug=1`, vedrete un elenco di goroutine e i loro stack di chiamata. Ad esempio:

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
#	0x4e1326	internal/poll.(*pollDesc).wait+0x26			internal/poll/fd_poll_runtime.go:84
#	0x4e2619	internal/poll.(*pollDesc).waitRead+0x279		internal/poll/fd_poll_runtime.go:89
#	0x4e2607	internal/poll.(*FD).Read+0x267				internal/poll/fd_unix.go:164
#	0x545a64	net.(*netFD).Read+0x24					net/fd_posix.go:55
#	0x5590c4	net.(*conn).Read+0x44					net/net.go:179
#	0x6b2e9a	crypto/tls.(*atLeastReader).Read+0x3a			crypto/tls/conn.go:805
#	0x50ddb7	bytes.(*Buffer).ReadFrom+0x97				bytes/buffer.go:211
#	0x6b307d	crypto/tls.(*Conn).readFromUntil+0xdd			crypto/tls/conn.go:827
#	0x6b064f	crypto/tls.(*Conn).readRecordOrCCS+0x24f		crypto/tls/conn.go:625
#	0x6b6917	crypto/tls.(*Conn).readRecord+0x157			crypto/tls/conn.go:587
#	0x6b6920	crypto/tls.(*Conn).Read+0x160				crypto/tls/conn.go:1369
#	0x4b856f	io.ReadAtLeast+0x8f					io/io.go:335
#	0xb11a04	io.ReadFull+0x64					io/io.go:354
#	0xb119d3	golang.org/x/net/http2.readFrameHeader+0x33		golang.org/x/net@v0.14.0/http2/frame.go:237
#	0xb12144	golang.org/x/net/http2.(*Framer).ReadFrame+0x84		golang.org/x/net@v0.14.0/http2/frame.go:498
#	0xb1d086	golang.org/x/net/http2.(*serverConn).readFrames+0x86	golang.org/x/net@v0.14.0/http2/server.go:818

1 @ 0x43e50e 0x44e286 0xafeeb3 0xb0af86 0x5c29fc 0x5c3225 0xb0365b 0xb03650 0x15cb6af 0x43e09b 0x4719c1
#	0xafeeb2	github.com/caddyserver/caddy/v2/cmd.cmdRun+0xcd2					github.com/caddyserver/caddy/v2@v2.7.4/cmd/commandfuncs.go:277
#	0xb0af85	github.com/caddyserver/caddy/v2/cmd.init.1.func2.WrapCommandFuncForCobra.func1+0x25	github.com/caddyserver/caddy/v2@v2.7.4/cmd/cobra.go:126
#	0x5c29fb	github.com/spf13/cobra.(*Command).execute+0x87b						github.com/spf13/cobra@v1.7.0/command.go:940
#	0x5c3224	github.com/spf13/cobra.(*Command).ExecuteC+0x3a4					github.com/spf13/cobra@v1.7.0/command.go:1068
#	0xb0365a	github.com/spf13/cobra.(*Command).Execute+0x5a						github.com/spf13/cobra@v1.7.0/command.go:992
#	0xb0364f	github.com/caddyserver/caddy/v2/cmd.Main+0x4f						github.com/caddyserver/caddy/v2@v2.7.4/cmd/main.go:65
#	0x15cb6ae	main.main+0xe										caddy/main.go:11
#	0x43e09a	runtime.main+0x2ba									runtime/proc.go:267

1 @ 0x43e50e 0x44e9c5 0x8ec085 0x4719c1
#	0x8ec084	github.com/caddyserver/certmagic.(*Cache).maintainAssets+0x304	github.com/caddyserver/certmagic@v0.19.2/maintain.go:67

...
```

La prima riga, `goroutine profile: total 88`, ci dice cosa stiamo guardando e quanti goroutine ci sono.

Segue l'elenco dei goroutine. Sono raggruppati in base ai loro stack di chiamata in ordine decrescente di frequenza.

Una riga di goroutine ha questa sintassi: `<conteggio> @ <indirizzi...>`

La riga inizia con un conteggio dei goroutine che hanno lo stack di chiamata associato. Il simbolo `@` indica l'inizio degli indirizzi delle istruzioni di chiamata, ovvero i puntatori a funzione, che hanno originato il goroutine. Ogni puntatore è una chiamata di funzione, o frame di chiamata (call frame).

Noterete che molti dei vostri goroutine condividono lo stesso primo indirizzo di chiamata. Questo è il main del vostro programma, o il suo punto di ingresso. Alcuni goroutine non originano lì perché i programmi hanno varie funzioni `init()` e anche il runtime di Go può generare dei goroutine.

Le righe che seguono iniziano con `#` e sono in realtà solo commenti a beneficio del lettore. Contengono l'attuale stack trace del goroutine. La parte superiore rappresenta la cima dello stack, ovvero la riga di codice corrente in esecuzione. La parte inferiore rappresenta la base dello stack, ovvero il codice che il goroutine ha iniziato a eseguire inizialmente.

Lo stack trace ha questo formato:

```
<indirizzo> <pacchetto/funzione>+<offset> <nome_file>:<riga>
```

L'indirizzo è il puntatore alla funzione, poi vedrete il pacchetto Go e il nome della funzione (con il nome del tipo associato se si tratta di un metodo) e l'offset dell'istruzione all'interno della funzione. Poi, forse l'informazione più utile, il file e il numero di riga si trovano alla fine.

### Dump completo dello stack dei goroutine

Se cambiamo il parametro della stringa di query in `?debug=2`, otteniamo un dump completo. Questo include uno stack trace prolisso di ogni singolo goroutine, e i goroutine identici non vengono raggruppati. Questo output può essere molto grande su server molto carichi, ma contiene informazioni interessanti!

Guardiamone uno che corrisponde al primo stack di chiamata sopra (troncato):

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

Nonostante la sua prolissità, le informazioni più utili fornite unicamente da questo dump sono la prima e l'ultima riga di ogni goroutine.

La prima riga contiene il numero del goroutine (61961905), lo stato ("IO wait") e la durata ("1 minutes"):

- **Numero del goroutine:** Sì, i goroutine hanno numeri! Ma non sono esposti al nostro codice. Questi numeri sono però molto utili in uno stack trace, perché possiamo vedere quale goroutine ha generato quello attuale (vedi alla fine: "created by ... in goroutine 61961902"). Gli strumenti mostrati di seguito ci aiutano a tracciare grafici visivi di questo.

- **Stato:** Ci dice cosa sta facendo attualmente il goroutine. Ecco alcuni stati possibili:
	- `running`: Esecuzione di codice - ottimo!
	- `IO wait`: In attesa della rete. Non consuma un thread del sistema operativo perché è parcheggiato su un poller di rete non bloccante.
	- `sleep`: Tutti ne abbiamo bisogno.
	- `select`: Bloccato su una `select`; in attesa che un caso diventi disponibile.
	- `select (no cases)`: Bloccato specificamente su una `select` vuota `select {}`. Caddy ne usa uno nel suo main per rimanere in esecuzione perché gli arresti sono avviati da altri goroutine.
	- `chan receive`: Bloccato sulla ricezione da un canale (`<-ch`).
	- `semacquire`: In attesa di acquisire un semaforo (primitiva di sincronizzazione di basso livello).
	- `syscall`: Esecuzione di una chiamata di sistema. Consuma un thread del sistema operativo.

- **Durata:** Da quanto tempo esiste il goroutine. Utile per trovare bug come le perdite di goroutine. Ad esempio, se ci aspettiamo che tutte le connessioni di rete vengano chiuse dopo pochi minuti, cosa significa quando troviamo molti goroutine `netconn` attivi da ore?

### Interpretazione dei dump dei goroutine

Senza guardare il codice, cosa possiamo imparare sul goroutine sopra descritto?

È stato creato solo un minuto fa, è in attesa di dati su un socket di rete e il suo numero di goroutine è molto grande (61961905).

Dal primo dump (debug=1), sappiamo che il suo stack di chiamata viene eseguito con relativa frequenza, e l'alto numero del goroutine combinato con la breve durata suggerisce che ci sono stati decine di milioni di questi goroutine a vita relativamente breve. Si trova in una funzione chiamata `pollWait` e la sua storia di chiamate include la lettura di frame HTTP/2 da una connessione di rete crittografata che utilizza TLS.

Quindi, possiamo dedurre che questo goroutine sta servendo una richiesta HTTP/2! È in attesa di dati dal client. Inoltre, sappiamo che il goroutine che lo ha generato non è uno dei primi del processo perché anch'esso ha un numero alto; cercandolo nel dump si scopre che è stato generato per gestire un nuovo stream HTTP/2 durante una richiesta esistente. Al contrario, altri goroutine con numeri alti potrebbero essere generati da un goroutine con numero basso (come il 32), indicando una nuovissima connessione appena uscita da una chiamata `Accept()` dal socket.

Ogni programma è diverso, ma nel debugging di Caddy questi pattern tendono ad essere veri.

## Profili di memoria

I profili di memoria (o heap) tracciano le allocazioni della heap, che sono i principali consumatori di memoria in un sistema. Le allocazioni sono anche le solite sospette per problemi di prestazioni, poiché l'allocazione di memoria richiede chiamate di sistema, che possono essere lente.

I profili heap appaiono simili ai profili goroutine quasi in tutto, tranne che per l'inizio della prima riga. Ecco un esempio:

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
#	0xb1fc4c	golang.org/x/net/http2.glob..func8+0x6c				golang.org/x/net@v0.17.0/http2/http2.go:263
#	0x48d8d0	sync.(*Pool).Get+0xb0						sync/pool.go:151
#	0xb1fce5	golang.org/x/net/http2.(*bufferedWriter).Write+0x45		golang.org/x/net@v0.17.0/http2/http2.go:276
#	0xb184c6	golang.org/x/net/http2.(*Framer).endWrite+0xc6			golang.org/x/net@v0.17.0/http2/frame.go:371
#	0xb1bc8d	golang.org/x/net/http2.(*Framer).WriteHeaders+0x48d		golang.org/x/net@v0.17.0/http2/frame.go:1131
#	0xb41652	golang.org/x/net/http2.(*writeResHeaders).writeHeaderBlock+0xd2	golang.org/x/net@v0.17.0/http2/write.go:239
#	0xb4105b	golang.org/x/net/http2.splitHeaderBlock+0xbb			golang.org/x/net@v0.17.0/http2/write.go:169
#	0xb4151c	golang.org/x/net/http2.(*writeResHeaders).writeFrame+0x1dc	golang.org/x/net@v0.17.0/http2/write.go:234
#	0xb23b13	golang.org/x/net/http2.(*serverConn).writeFrameAsync+0x73	golang.org/x/net@v0.17.0/http2/server.go:851
```

Il formato della prima riga è il seguente:

```
<oggetti_vivi> <memoria_viva> [<allocazioni>: <memoria_allocata>] @ <indirizzi...>
```

Nell'esempio sopra, abbiamo una singola allocazione effettuata da `bufio.NewWriterSize()` ma attualmente nessun oggetto vivo da questo stack di chiamata.

È interessante notare che possiamo dedurre da quello stack di chiamata che il pacchetto `http2` ha usato un pool da 4 KB per scrivere uno o più frame HTTP/2 al client. Vedrete spesso oggetti in pool nei profili di memoria di Go se i percorsi critici sono stati ottimizzati per riutilizzare le allocazioni. Questo riduce le nuove allocazioni e il profilo heap può aiutarvi a sapere se il pool viene utilizzato correttamente!

## Profili della CPU

I profili della CPU vi aiutano a capire dove il programma Go sta trascorrendo la maggior parte del suo tempo pianificato sul processore.

Tuttavia, non esiste una forma in testo semplice per questi, quindi nella sezione successiva useremo i comandi `go tool pprof` per aiutarci a leggerli.

Per scaricare un profilo CPU, effettuate una richiesta a `/debug/pprof/profile?seconds=N`, dove N è il numero di secondi durante i quali volete raccogliere il profilo. Durante la raccolta del profilo CPU, le prestazioni del programma potrebbero essere lievemente influenzate. (Altri profili non hanno praticamente alcun impatto prestazionale.)

Al termine, dovrebbe essere scaricato un file binario, appropriatamente chiamato `profile`. Successivamente dobbiamo esaminarlo.

## `go tool pprof`

Useremo l'analizzatore di profili integrato di Go per leggere il profilo della CPU come esempio, ma potete usarlo con qualsiasi tipo di profilo.

Eseguite questo comando (sostituendo "profile" con il percorso effettivo del file se diverso), che apre un prompt interattivo:

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">
	Potete usare questo comando per esaminare qualsiasi tipo di profilo, non solo quelli della CPU. I principi sono gli stessi per gli altri profili e i concetti si trasferiscono.
</aside>

È qualcosa che potete esplorare. Digitando `help` otterrete un elenco di comandi e `o` mostrerà le opzioni correnti. Digitando `help <comando>` potrete ottenere informazioni su un comando specifico.

Ci sono molti comandi, ma alcuni tra i più comuni sono:

- `top`: Mostra cosa ha usato di più la CPU. Potete aggiungere un numero come `top 20` per vederne di più, o una regex per "concentrarvi" o ignorare determinati elementi.
- `web`: Apre il grafico delle chiamate nel vostro browser web. È un ottimo modo per visualizzare l'uso della CPU.
- `svg`: Genera un'immagine SVG del grafico delle chiamate. È identico a `web` tranne per il fatto che non apre il browser web e l'SVG viene salvato localmente.
- `tree`: Una vista tabellare dello stack delle chiamate.

Iniziamo con `top`. Vediamo un output simile a questo:

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
     5.03s  7.17% 32.22%      5.34s  7.62%  runtime.(*lfstack).pop (inline)
     3.69s  5.26% 37.48%     11.02s 15.72%  runtime.scanobject
     2.42s  3.45% 40.94%      2.42s  3.45%  runtime.(*lfstack).push
     2.26s  3.22% 44.16%      2.30s  3.28%  runtime.pageIndexOf (inline)
     2.11s  3.01% 47.17%      2.56s  3.65%  runtime.findObject
     2.03s  2.90% 50.06%      2.03s  2.90%  runtime.markBits.isMarked (inline)
     1.69s  2.41% 52.47%      1.69s  2.41%  runtime.memclrNoHeapPointers
     1.57s  2.24% 54.71%      1.57s  2.24%  runtime.epollwait
```

I primi 10 consumatori della CPU erano tutti nel runtime di Go &mdash; in particolare, molta garbage collection (ricordate che le chiamate di sistema sono usate per liberare e allocare memoria). Questo è un indizio del fatto che potremmo ridurre le allocazioni per migliorare le prestazioni, e un profilo heap varrebbe la pena.

OK, ma se volessimo vedere l'utilizzo della CPU dal nostro codice? Possiamo ignorare i pattern contenenti "runtime" in questo modo:

```
(pprof) top -runtime  
Active filters:
   ignore=runtime
Showing nodes accounting for 0.92s, 1.31% of 70.11s total
Dropped 160 nodes (cum <= 0.35s)
Showing top 10 nodes out of 243
      flat  flat%   sum%        cum   cum%
     0.17s  0.24%  0.24%      0.28s   0.4%  sync.(*Pool).getSlow
     0.11s  0.16%   0.4%      0.11s  0.16%  github.com/prometheus/client_golang/prometheus.(*histogram).observe (inline)
     0.10s  0.14%  0.54%      0.23s  0.33%  github.com/prometheus/client_golang/prometheus.(*MetricVec).hashLabels
     0.10s  0.14%  0.68%      0.12s  0.17%  net/textproto.CanonicalMIMEHeaderKey
     0.10s  0.14%  0.83%      0.10s  0.14%  sync.(*poolChain).popTail
     0.08s  0.11%  0.94%      0.26s  0.37%  github.com/prometheus/client_golang/prometheus.(*histogram).Observe
     0.07s   0.1%  1.04%      0.07s   0.1%  internal/poll.(*fdMutex).rwlock
     0.07s   0.1%  1.14%      0.10s  0.14%  path/filepath.Clean
     0.06s 0.086%  1.23%      0.06s 0.086%  context.value
     0.06s 0.086%  1.31%      0.06s 0.086%  go.uber.org/zap/buffer.(*Buffer).AppendByte
```

Ebbene, è chiaro che le metriche di Prometheus sono un altro dei principali consumatori, ma noterete che cumulativamente ammontano a ordini di grandezza inferiori rispetto al GC visto sopra. La netta differenza suggerisce che dovremmo concentrarci sulla riduzione del GC.

<aside class="tip">
	È importante notare che i profili CPU ottengono le loro misurazioni da campionamenti intermittenti, e i campioni non verranno mai catturati più frequentemente della frequenza di campionamento, che è di 10ms per impostazione predefinita. Ecco perché non vedrete durate di tempo cumulative inferiori a 10ms (probabilmente sono inferiori, ma arrotondate per eccesso). Per tempistiche più specifiche, potete eseguire un trace di esecuzione, che non utilizza il campionamento. (TODO: Aggiungere sezione sul tracing.)
</aside>

Usiamo `q` per uscire da questo profilo e usiamo lo stesso comando sul profilo heap:

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
Showing top 10 nodes out of 102
      flat  flat%   sum%        cum   cum%
   12300kB 44.92% 44.92%    12300kB 44.92%  runtime.allocm
 2570.01kB  9.39% 54.31%  2570.01kB  9.39%  bufio.NewReaderSize
 2048.81kB  7.48% 61.79%  2048.81kB  7.48%  runtime.malg
 1542.01kB  5.63% 67.42%  1542.01kB  5.63%  bufio.NewWriterSize
 ...
 ```

Bingo. Quasi metà della memoria è allocata rigorosamente per i buffer di lettura e scrittura dal nostro uso del pacchetto `bufio`. Pertanto, possiamo dedurre che ottimizzare il nostro codice per ridurre il buffering sarebbe molto vantaggioso (la [relativa patch in Caddy](https://github.com/caddyserver/caddy/pull/4978) fa proprio questo).

### Visualizzazioni

Se invece eseguiamo i comandi `svg` o `web`, otterremo una visualizzazione del profilo:

![Visualizzazione profilo CPU](/old/resources/images/profile.png)

Questo è un profilo CPU, ma grafici simili sono disponibili per altri tipi di profilo.

Per imparare a leggere questi grafici, consultate la [documentazione di pprof](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).


### Confronto tra profili (Diffing)

Dopo aver apportato una modifica al codice, potete confrontare il "prima" e il "dopo" utilizzando un'analisi differenziale ("diff"). Ecco un diff della heap:

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
File: caddy
Type: inuse_space
Time: Aug 29, 2022 at 1:21am (MDT)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
Dropped 10 nodes (cum <= 0.27MB)
Showing top 10 nodes out of 137
      flat  flat%   sum%        cum   cum%
  -27.04MB 49.45% 49.45%   -27.04MB 49.45%  bufio.NewWriterSize
      -2MB  3.66% 53.11%       -2MB  3.66%  runtime.allocm
    1.06MB  1.93% 51.18%     1.06MB  1.93%  github.com/yuin/goldmark/util.init
    1.03MB  1.89% 49.29%     1.03MB  1.89%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.glob..func2
       1MB  1.84% 47.46%        1MB  1.84%  bufio.NewReaderSize
      -1MB  1.83% 49.29%       -1MB  1.83%  runtime.malg
       1MB  1.83% 47.46%        1MB  1.83%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.cloneRequest
      -1MB  1.83% 49.29%       -1MB  1.83%  net/http.(*Server).newConn
   -0.55MB  1.00% 50.29%    -0.55MB  1.00%  html.populateMaps
    0.53MB  0.97% 49.32%     0.53MB  0.97%  github.com/alecthomas/chroma.TypeRemappingLexer</code></pre>

Come potete vedere, abbiamo ridotto le allocazioni di memoria di circa la metà!

Anche i diff possono essere visualizzati:

![Visualizzazione profilo CPU](/old/resources/images/profile-diff.png)

Questo rende molto evidente come i cambiamenti abbiano influenzato le prestazioni di determinate parti del programma.

## Letture consigliate

C'è molto da imparare sul profiling dei programmi e abbiamo solo grattato la superficie.

Per diventare dei veri "pro" del "profiling", considerate queste risorse:

- [Documentazione pprof](https://github.com/google/pprof/blob/main/doc/README.md)
- [Un uso reale dei profili con Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Prestazioni sul wiki di Go](https://github.com/golang/go/wiki/Performance)
- [Il pacchetto `net/http/pprof`](https://pkg.go.dev/net/http/pprof)
