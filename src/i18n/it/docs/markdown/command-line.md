---
title: "Riga di comando"
---

# Riga di comando

Caddy ha un'interfaccia a riga di comando standard di tipo unix. L'uso di base è:

```
caddy <comando> [<argomenti...>]
```

I simboli `<carets>` indicano parametri che vengono sostituiti dal vostro input.

Le `[parentesi quadre]` indicano parametri opzionali. Le `(parentesi tonde)` indicano parametri obbligatori.

I puntini di sospensione `...` indicano una continuazione, ovvero uno o più parametri.

I `--flag` possono avere una scorciatoia a singola lettera come `-f`.

**Avvio rapido: `caddy`, `caddy help`, o `man caddy` (se installato)**

---

- **[caddy adapt](#caddy-adapt)**
  Adatta un documento di configurazione nel JSON nativo

- **[caddy build-info](#caddy-build-info)**
  Stampa le informazioni sulla build

- **[caddy completion](#caddy-completion)**
  Genera script di completamento per la shell

- **[caddy environ](#caddy-environ)**
  Stampa l'ambiente

- **[caddy file-server](#caddy-file-server)**
  Un server di file statici semplice ma pronto per la produzione

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Comando ausiliario per il file server per esportare il template predefinito del browser di file

- **[caddy fmt](#caddy-fmt)**
  Formatta un Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Esegue l'hashing di una password e restituisce l'output in base64

- **[caddy help](#caddy-help)**
  Visualizza l'aiuto per i comandi caddy

- **[caddy list-modules](#caddy-list-modules)**
  Elenca i moduli Caddy installati

- **[caddy manpage](#caddy-manpage)**
  Genera le pagine di manuale (manpage)

- **[caddy reload](#caddy-reload)**
  Cambia la configurazione del processo Caddy in esecuzione

- **[caddy respond](#caddy-respond)**
  Un server HTTP rapido e semplice con risposte fisse per sviluppo e test

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Un reverse proxy HTTP(S) semplice ma pronto per la produzione

- **[caddy run](#caddy-run)**
  Avvia il processo Caddy in primo piano

- **[caddy start](#caddy-start)**
  Avvia il processo Caddy in background

- **[caddy stop](#caddy-stop)**
  Ferma il processo Caddy in esecuzione

- **[caddy storage export](#caddy-storage-export)**
  Esporta il contenuto dello storage configurato in un archivio tarball

- **[caddy storage import](#caddy-storage-import)**
  Importa un archivio tarball precedentemente esportato nello storage configurato

- **[caddy trust](#caddy-trust)**
  Installa un certificato negli archivi di fiducia locali

- **[caddy untrust](#caddy-untrust)**
  Rimuove la fiducia a un certificato dagli archivi locali

- **[caddy upgrade](#caddy-upgrade)**
  Aggiorna Caddy all'ultima versione disponibile

- **[caddy add-package](#caddy-add-package)**
  Aggiorna Caddy all'ultima versione, aggiungendo plugin supplementari

- **[caddy remove-package](#caddy-remove-package)**
  Aggiorna Caddy all'ultima versione, rimuovendo alcuni plugin

- **[caddy validate](#caddy-validate)**
  Verifica se un file di configurazione è valido

- **[caddy version](#caddy-version)**
  Stampa la versione

- **[Segnali](#signals)**
  Come Caddy gestisce i segnali di sistema

- **[Codici di uscita](#exit-codes)**
  Emessi quando il processo Caddy termina

## Sottocomandi


### `caddy adapt`

<a id="caddy-adapt"></a>
<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Adatta una configurazione alla struttura JSON nativa di Caddy e scrive l'output su stdout, insieme a eventuali avvisi su stderr, quindi termina.

`--config` è il percorso del file di configurazione. Se omesso, assume `Caddyfile` nella directory corrente se esiste; altrimenti, questo flag è obbligatorio. Se desiderate usare lo stdin invece di un file regolare, usate `-` come percorso.

`--adapter` specifica l'adattatore di configurazione da usare; il valore predefinito è `caddyfile`.

`--pretty` formatterà l'output con l'indentazione per la leggibilità umana.

`--validate` caricherà e predisporrà la configurazione adattata per verificarne la validità (ma non avvierà effettivamente la configurazione).

Si noti che una configurazione adattata con successo può comunque fallire la validazione. Per un esempio, usate questo Caddyfile:

```caddy
localhost

tls cert_non-esiste.pem key_non-exist.pem
```

Provate ad adattarlo:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

L'operazione riesce senza errori. Poi provate:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

Anche se quel Caddyfile può essere adattato in JSON senza errori, i file effettivi del certificato e/o della chiave non esistono, quindi la validazione fallisce perché l'errore sorge durante la fase di predisposizione. Pertanto, la validazione è un controllo degli errori più rigoroso rispetto all'adattamento.

#### Esempio

Per adattare un Caddyfile in un JSON facilmente leggibile e modificabile manualmente:

<pre><code class="cmd bash">caddy adapt --config /percorso/del/Caddyfile --pretty</code></pre>



### `caddy build-info`

<a id="caddy-build-info"></a>
<pre><code class="cmd bash">caddy build-info</code></pre>

Stampa le informazioni fornite da Go sulla build (percorso del modulo principale, versioni dei pacchetti, sostituzioni dei moduli).




### `caddy completion`

<a id="caddy-completion"></a>
<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Genera script di completamento per la shell. Ciò consente di ottenere il tab-completamento o l'auto-completamento (o simili, a seconda della shell) quando si digitano i comandi `caddy`.

Per ottenere istruzioni sull'installazione di questo script nella vostra specifica shell, eseguite `caddy help completion` o `caddy completion -h`.



### `caddy environ`

<a id="caddy-environ"></a>
<pre><code class="cmd bash">caddy environ</code></pre>

Stampa l'ambiente così come visto da caddy, quindi termina. Può essere utile per il debugging di sistemi di init o unità di gestione dei processi come systemd.




### `caddy file-server`

<a id="caddy-file-server"></a>
<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Avvia un server di file statici semplice ma pronto per la produzione.

`--root` specifica il percorso del file radice. Il valore predefinito è la directory di lavoro corrente.

`--listen` accetta un indirizzo di ascolto. Il valore predefinito è `:80`, a meno che non venga usato `--domain`, nel qual caso il valore predefinito sarà `:443`.

`--domain` servirà i file solo attraverso quel nome host e Caddy tenterà di servirli tramite HTTPS; assicuratevi quindi che il DNS pubblico sia configurato correttamente se si tratta di un dominio pubblico. La porta predefinita verrà cambiata in 443.

`--browse` abiliterà l'elenco delle directory se viene richiesta una directory senza un file index.

`--reveal-symlinks` mostrerà la destinazione dei collegamenti simbolici negli elenchi delle directory quando `--browse` è abilitato.

`--templates` abiliterà il rendering dei template.

`--access-log` abilita il log delle richieste/accessi.

`--debug` abilita il logging prolisso.

`--file-limit` imposta un numero massimo di file da mostrare negli elenchi delle directory. Predefinito: `10000`. Se il numero di file supera questo limite, verranno mostrati solo i primi N file, dove N è il limite specificato.

`--no-compress` disabilita la compressione. Per impostazione predefinita, le compressioni Zstandard e Gzip sono abilitate.

`--precompressed` specifica i formati di codifica per cercare i file "sidecar" precompressi. Può essere ripetuto per più formati. Consultate la [direttiva file_server](/docs/caddyfile/directives/file_server#precompressed) per ulteriori informazioni.

Questo comando disabilita l'API di amministrazione, facilitando l'esecuzione di più istanze su una macchina di sviluppo locale.


#### `caddy file-server export-template`

<a id="caddy-file-server-export-template"></a>
<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Esporta su stdout il template predefinito per la navigazione dei file.

### `caddy fmt`

<a id="caddy-fmt"></a>
<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Formatta o abbellisce un Caddyfile, quindi termina. Il risultato viene stampato su stdout a meno che non venga usato `--overwrite`, e uscirà con codice `1` se ci sono differenze.

`<path>` specifica il percorso del Caddyfile. Se `-`, l'input viene letto dallo stdin. Se omesso, viene assunto un file chiamato Caddyfile nella directory corrente.

`--overwrite` fa sì che il risultato venga scritto nel file di input invece di essere stampato sul terminale. Se l'input non è un file regolare, questo flag non ha effetto.

`--diff` fa sì che l'output venga confrontato con l'input e le righe saranno precedute da `-` e `+` dove differiscono. Si noti che le righe invariate sono precedute da due spazi per l'allineamento e che questo non è un formato di patch valido; è inteso solo come strumento visivo.


### `caddy hash-password`

<a id="caddy-hash-password"></a>
<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

Modo conveniente per eseguire l'hashing di una password in chiaro. L'hash risultante viene scritto su stdout in un formato utilizzabile direttamente nella configurazione di Caddy.

`--plaintext`
    La password di cui eseguire l'hashing. Se omessa, verrà letta dallo stdin.
    Se Caddy è collegato a un terminale di controllo (TTY), l'input non verrà visualizzato (echo).

`--algorithm`
    Seleziona l'algoritmo di hashing. Le opzioni valide sono:
      * `argon2id` (raccomandato per la sicurezza moderna)
      * `bcrypt` (legacy, più lento, costo configurabile, il costo predefinito è `14`)

Parametri specifici per bcrypt:

`--bcrypt-cost`
    Imposta la difficoltà dell'hashing bcrypt. Valori più alti aumentano la sicurezza rendendo il calcolo dell'hash più lento e intensivo per la CPU.
    Deve rientrare nell'intervallo valido [bcrypt.MinCost, bcrypt.MaxCost].
    Se omesso o non valido, viene utilizzato il costo predefinito.

Parametri specifici per Argon2id:

`--argon2id-time`
    Numero di iterazioni da eseguire. Aumentare questo valore rende l'hashing più lento e più resistente agli attacchi brute-force.

`--argon2id-memory`
    Quantità di memoria da utilizzare durante l'hashing. Valori più grandi aumentano la resistenza agli attacchi GPU/ASIC.

`--argon2id-threads`
    Numero di thread CPU da utilizzare. Aumentare per un hashing più veloce su sistemi multi-core.

`--argon2id-keylen`
    Lunghezza dell'hash risultante in byte. Chiavi più lunghe aumentano la sicurezza ma aumentano leggermente la dimensione della memoria occupata.


### `caddy help`

<a id="caddy-help"></a>
<pre><code class="cmd bash">caddy help [&lt;comando&gt;]</code></pre>

Stampa il testo di aiuto della CLI, opzionalmente per un sottocomando specifico, quindi termina.



### `caddy list-modules`

<a id="caddy-list-modules"></a>
<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

Stampa i moduli Caddy installati, opzionalmente con informazioni sul pacchetto e/o sulla versione dai loro associati moduli Go, quindi termina.

In alcune situazioni di scripting, potrebbe essere ridondante stampare anche tutti i moduli standard, quindi potete usare `--skip-standard` per ometterli dall'output.

`--json` restituisce le informazioni sui moduli in formato JSON, il che può essere utile per l'elaborazione programmatica.

NOTA: a causa di [un bug in Go](https://github.com/golang/go/issues/29228), le informazioni sulla versione sono disponibili solo se Caddy è compilato come dipendenza e non come modulo principale. Usate [xcaddy](/docs/build#xcaddy) per facilitare l'operazione.



### `caddy manpage`

<a id="caddy-manpage"></a>
<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Genera pagine di manuale/documentazione per i comandi Caddy e le scrive nella directory al percorso specificato. L'output di questo comando può essere letto dal comando `man`.

`--directory` (obbligatorio) è il percorso della directory in cui scrivere le manpage. Verrà creata se non esiste.

Una volta generate, le pagine di manuale devono generalmente essere installate. Questa procedura varia a seconda della piattaforma, ma sui tipici sistemi Linux è qualcosa del genere:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Potrete quindi eseguire `man caddy` (o `man caddy-*` per i sottocomandi) per leggere la documentazione nel vostro terminale.

Le pagine di manuale sono una documentazione separata da quella presente sul nostro sito web. Il nostro sito dispone di una documentazione più completa e aggiornata spesso.




### `caddy reload`

<a id="caddy-reload"></a>
<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Fornisce all'istanza di Caddy in esecuzione una nuova configurazione. Ha lo stesso effetto di inviare un documento tramite POST all'[endpoint /load](/docs/api#post-load), ma questo comando è comodo per flussi di lavoro semplici basati su file di configurazione. Rispetto ai comandi `stop`, `start` e `run`, questo singolo comando è il modo corretto e semantico per cambiare/ricaricare la configurazione in esecuzione.

Poiché questo comando utilizza l'API, l'endpoint di amministrazione non deve essere disabilitato.

`--config` è il file di configurazione da applicare. Se `-`, la configurazione viene letta dallo stdin. Se non specificato, proverà con un file chiamato `Caddyfile` nella directory di lavoro corrente e, se esiste, lo adatterà usando l'adattatore `caddyfile`; in caso contrario, verrà restituito un errore se non c'è alcun file di configurazione da caricare.

`--adapter` specifica un adattatore di configurazione da usare, se presente. Questo flag non è necessario se il nome del file `--config` inizia con `Caddyfile` o termina con `.caddyfile`, il che assume l'adattatore `caddyfile`. Altrimenti, questo flag è obbligatorio se il file di configurazione fornito non è nel formato JSON nativo di Caddy.

`--address` deve essere usato se l'endpoint di amministrazione non è in ascolto sull'indirizzo predefinito e se è diverso dall'indirizzo nel file di configurazione fornito.

`--force` forzerà un ricaricamento anche se la configurazione specificata è identica a quella che Caddy sta già eseguendo. Può essere utile per costringere Caddy a predisporre nuovamente i suoi moduli, il che può avere effetti collaterali, ad esempio: ricaricare i certificati TLS caricati manualmente.




### `caddy respond`

<a id="caddy-respond"></a>
<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


Avvia uno o più server HTTP semplici con risposte fisse, utili per lo sviluppo, il collaudo e alcuni casi d'uso in produzione. Può essere utile per verificare o sottoporre a debug client HTTP, script o persino bilanciatori di carico.

`--status` è il codice di stato HTTP da restituire.

`--header` aggiunge un header HTTP; è previsto il formato `Field: valore`. Questo flag può essere usato più volte.

`--body` specifica il corpo della risposta. In alternativa, il corpo può essere passato tramite pipe dallo stdin.

`--listen` è l'indirizzo di ascolto, che può essere qualsiasi [indirizzo di rete](/docs/conventions#network-addresses) riconosciuto da Caddy, e può includere un intervallo di porte per avviare più server.

`--debug` abilita il logging di debug prolisso.

`--access-log` abilita il logging degli accessi/richieste.

Senza opzioni specificate, questo comando ascolta su una porta casuale disponibile e risponde alle richieste HTTP con una risposta 200 vuota. L'indirizzo di ascolto può essere personalizzato con il flag `--listen` e verrà sempre stampato su stdout. Se l'indirizzo di ascolto include un intervallo di porte, verranno avviati più server.

Se viene fornito un argomento finale senza nome, verrà trattato come un codice di stato (come il flag `--status`) se è un numero di 3 cifre. In caso contrario, verrà usato come corpo della risposta (come il flag `--body`). I flag `--status` e `--body` avranno sempre la precedenza su questo argomento.

Un corpo può essere fornito in 3 modi: tramite flag, come argomento finale (e senza nome) del comando, o tramite pipe allo stdin (if il flag e l'argomento non sono impostati). È supportata una limitata [valutazione dei template](https://pkg.go.dev/text/template) sul corpo, con le seguenti variabili:

Variabile | Descrizione
---------|-------------
`.N`       | Numero del server
`.Port`    | Porta di ascolto
`.Address` | Indirizzo di ascolto


#### Esempi

Risposta 200 vuota su una porta casuale:
<pre><code class="cmd bash">caddy respond</code></pre>

Risposta HTTP con un corpo:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Server multipli e template:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

Passare tramite pipe una pagina di manutenzione:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




### `caddy reverse-proxy`

<a id="caddy-reverse-proxy"></a>
<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Un reverse proxy semplice ma pronto per la produzione. Utile per distribuzioni rapide, demo e sviluppo.

Semplicemente smista il traffico HTTP(S) dall'indirizzo `--from` all'indirizzo `--to`. È possibile specificare più indirizzi `--to` ripetendo il flag. È richiesto almeno un indirizzo `--to`. L'indirizzo `--to` può avere un intervallo di porte come scorciatoia per espandersi a più upstream.

Salvo diversamente specificato negli indirizzi, l'indirizzo `--from` sarà considerato HTTPS se viene fornito un nome host, mentre l'indirizzo `--to` sarà considerato HTTP.

Se l'indirizzo `--from` ha un host o un IP, Caddy tenterà di servire il proxy tramite HTTPS con un certificato (a meno che non venga sovrascritto dallo schema o dalla porta HTTP).

Se serve HTTPS: 
  - `--disable-redirects` può essere usato per evitare l'associazione alla porta HTTP.

  - `--internal-certs` può essere usato per forzare l'emissione di certificati usando la CA interna invece di tentare di emettere un certificato pubblico.

Per il proxying:
  - `--header-up` può essere usato per impostare un header di richiesta da inviare all'upstream.
  
  - `--header-down` può essere usato per impostare un header di risposta da rimandare al client.
  
  - `--change-host-header` imposta l'header Host della richiesta sull'indirizzo dell'upstream, invece di utilizzare come predefinito l'header Host in entrata.

    Questa è una scorciatoia per `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`
  
  - `--insecure` disabilita la verifica TLS con l'upstream. ATTENZIONE: CIÒ DISABILITA LA SICUREZZA NON VERIFICANDO IL CERTIFICATO DELL'UPSTREAM.
  
  - `--debug` abilita il logging prolisso.

Questo comando disabilita l'API di amministrazione in modo che sia più facile eseguire più istanze su una macchina di sviluppo locale.



### `caddy run`

<a id="caddy-run"></a>
<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Esegue Caddy in modo bloccante; ovvero in modalità "demone".

`--config` specifica un file di configurazione iniziale da caricare e usare immediatamente. Se `-`, la configurazione viene letta dallo stdin. Se non viene specificata alcuna configurazione, Caddy verrà eseguito con una configurazione vuota e userà le impostazioni predefinite per gli [endpoint dell'API di amministrazione](/docs/api), che possono essere usati per fornirgli una nuova configurazione. Come caso speciale, se la directory di lavoro corrente contiene un file chiamato "Caddyfile" e l'adattatore di configurazione `caddyfile` è presente (predefinito), allora quel file verrà caricato e usato per configurare Caddy, anche senza flag da riga di comando.

`--adapter` è il nome dell'adattatore di configurazione da usare quando si carica la configurazione iniziale, se presente. Questo flag non è necessario se il nome del file `--config` inizia con `Caddyfile` o termina con `.caddyfile`, il che assume l'adattatore `caddyfile`. Altrimenti, questo flag è obbligatorio se il file di configurazione fornito non è nel formato JSON nativo di Caddy. Eventuali avvisi verranno stampati nel log, ma attenzione: qualsiasi adattamento senza errori verrà immediatamente utilizzato, anche in presenza di avvisi. Se volete prima esaminare i risultati dell'adattamento, usate il sottocomando [`caddy adapt`](#caddy-adapt).

`--pidfile` scrive il PID nel file specificato.

`--environ` stampa l'ambiente prima dell'avvio. È identico al comando `caddy environ`, ma non termina dopo la stampa.

`--envfile` carica le variabili d'ambiente dal file specificato, nel formato `CHIAVE=VALORE`. Sono supportati i commenti che iniziano con `#`; le chiavi possono avere il prefisso `export`; i valori possono essere racchiusi tra virgolette doppie (le virgolette interne possono essere precedute da escape); sono supportati valori su più righe.

`--resume` usa l'ultima configurazione caricata che è stata salvata automaticamente, sovrascrivendo il flag `--config` (se presente). L'uso di questo flag garantisce la persistenza della configurazione attraverso i riavvii della macchina o del processo. È molto utile nelle distribuzioni basate sull'[API](/docs/api).

`--watch` monitorerà il file di configurazione e lo ricaricherà automaticamente dopo ogni modifica. ⚠️ Questa funzione è destinata all'uso solo in ambienti di sviluppo locali!

<aside class="advice">
	Non fermate il server per cambiare configurazione mentre è in esecuzione in produzione! Ciò comporterà tempi di inattività. Usate invece il comando [`caddy reload`](#caddy-reload), oppure inviate un segnale `SIGUSR1` al processo, che ha lo stesso effetto di `caddy reload` con la configurazione attualmente caricata.
</aside>



### `caddy start`

<a id="caddy-start"></a>
<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></pre>

Identico a [`caddy run`](#caddy-run), ma in background. Questo comando si blocca solo finché il processo in background non è in esecuzione con successo (o fallisce l'avvio), quindi ritorna.

Nota: il flag `--config` *non* supporta `-` per leggere la configurazione dallo stdin.

L'uso di questo comando è sconsigliato con i servizi di sistema o su Windows. Su Windows, il processo figlio rimarrà collegato al terminale, quindi la chiusura della finestra fermerà forzatamente Caddy, il che non è scontato. Considerate invece di eseguire Caddy [come servizio](/docs/running).

Una volta avviato, potete usare [`caddy stop`](#caddy-stop) o l'endpoint API [`POST /stop`](/docs/api#post-stop) per terminare il processo in background.



### `caddy stop`

<a id="caddy-stop"></a>
<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">
	L'arresto (e il riavvio) del server è indipendente dalle modifiche alla configurazione. **Non usate il comando stop per cambiare la configurazione in produzione, a meno che non vogliate dei tempi di inattività.** Usate invece il comando [`caddy reload`](#caddy-reload).
</aside>


Arresta gradualmente il processo Caddy in esecuzione (diverso dal processo del comando stop stesso) e ne provoca l'uscita. Utilizza l'endpoint [`POST /stop`](/docs/api#post-stop) dell'API di amministrazione per eseguire un arresto graduale.

L'indirizzo di questa richiesta può essere personalizzato usando il flag `--address`, oppure dal `--config` fornito, se l'API di amministrazione dell'istanza in esecuzione non sta usando l'indirizzo di ascolto predefinito.

Se volete fermare la configurazione corrente ma non volete uscire dal processo, usate [`caddy reload`](#caddy-reload) con una configurazione vuota, o l'endpoint [`DELETE /config/`](/docs/api#delete-configpath).


### `caddy storage`

<a id="caddy-storage"></a>
<i>⚠️ Sperimentale</i>

Consente l'esportazione e l'importazione del contenuto dello storage dei dati configurato di Caddy.

È utile quando è necessario passare da un [modulo di storage](/docs/json/storage/) a un altro, esportando da quello vecchio, aggiornando la configurazione e poi importando in quello nuovo.

Il seguente comando può essere usato per copiare lo storage tra diversi moduli in un colpo solo, usando le vecchie e le nuove configurazioni, passando l'output del comando di esportazione al comando di importazione tramite pipe.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">
	Si noti che quando si utilizza lo [storage su filesystem](/docs/conventions#data-directory), è necessario eseguire il comando di esportazione con lo stesso utente con cui Caddy viene normalmente eseguito, altrimenti potrebbe essere utilizzata la posizione di storage errata.

	Ad esempio, quando si esegue Caddy come [servizio systemd](/docs/running#linux-service), verrà eseguito come utente `caddy`, quindi dovreste eseguire i comandi di esportazione o importazione con tale utente. In genere, questo può essere fatto con `sudo -u caddy <comando>`.
</aside>


#### `caddy storage export`

<a id="caddy-storage-export"></a>
<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` è il file di configurazione da caricare. È obbligatorio affinché venga collegato il modulo di storage corretto.

`--output` è il nome del file in cui scrivere l'archivio tarball. Se `-`, l'output viene scritto su stdout.



#### `caddy storage import`

<a id="caddy-storage-import"></a>
<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` è il file di configurazione da caricare. È obbligatorio affinché venga collegato il modulo di storage corretto.

`--input` è il nome del file tarball da cui leggere. Se `-`, l'input viene letto dallo stdin.


### `caddy trust`

<a id="caddy-trust"></a>
<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Installa negli archivi di fiducia locali un certificato root per una CA gestita dall'[app PKI](/docs/json/apps/pki/) di Caddy. 

Caddy tenterà di installare i suoi certificati root negli archivi di fiducia locali automaticamente quando vengono generati per la prima volta, ma l'operazione potrebbe fallire se Caddy non dispone dei permessi appropriati per scrivere nell'archivio di fiducia. Questo comando è necessario per pre-installare i certificati prima di usarli, se il processo del server viene eseguito come utente non privilegiato (come via systemd). Potrebbe essere necessario eseguire questo comando con `sudo` sui sistemi unix.

Per impostazione predefinita, questo comando installa il certificato root per la CA predefinita di Caddy (ovvero "local"). È possibile specificare l'ID di un'altra CA con il flag `--ca`.

Questo comando tenterà di connettersi all'[API di amministrazione](/docs/api) di Caddy per recuperare il certificato root, utilizzando l'endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates). Potete esplicitamente specificare l'indirizzo con `--address`, oppure usare il flag `--config` per caricare l'indirizzo di amministrazione dalla vostra configurazione, se l'API di amministrazione dell'istanza in esecuzione non sta usando l'indirizzo di ascolto predefinito.

È anche possibile usare il binario `caddy` con questo comando per installare certificati su altre macchine nella rete, se l'API di amministrazione è resa accessibile ad altre macchine &mdash; prestate attenzione se lo fate, per non esporre l'API di amministrazione a client non attendibili.


### `caddy untrust`

<a id="caddy-untrust"></a>
<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Rimuove la fiducia a un certificato root dagli archivi di fiducia locali.

Questo comando disinstalla la fiducia; non elimina necessariamente il certificato root dagli archivi di fiducia in modo completo. Pertanto, dare e togliere ripetutamente la fiducia a nuovi certificati può riempire i database di fiducia.

Questo comando non elimina né modifica i file dei certificati dallo storage configurato di Caddy.

Questo comando può essere usato in uno dei due modi seguenti:
- Specificando un percorso diretto al certificato root a cui togliere la fiducia con il flag `--cert`.
- Recuperando il certificato root dall'[API di amministrazione](/docs/api) usando l'endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). Questo è il comportamento predefinito se non vengono forniti flag.

Se viene usata l'API di amministrazione, l'ID della CA predefinito è "local". È possibile specificare l'ID di un'altra CA con il flag `--ca`. Potete specificare esplicitamente l'indirizzo con `--address`, oppure usare il flag `--config` per caricare l'indirizzo di amministrazione dalla vostra configurazione, se l'API di amministrazione dell'istanza in esecuzione non sta usando l'indirizzo di ascolto predefinito.


### `caddy upgrade`

<a id="caddy-upgrade"></a>
<i>⚠️ Sperimentale</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Sostituisce il binario Caddy corrente con l'ultima versione dalla nostra [pagina di download](/download) con gli stessi moduli installati, inclusi tutti i plugin di terze parti registrati sul sito web di Caddy.

Gli aggiornamenti non interrompono i server in esecuzione; attualmente il comando sostituisce solo il binario su disco. Questo potrebbe cambiare in futuro se riusciremo a trovare un buon modo per farlo.

Il processo di aggiornamento è tollerante ai guasti; il binario corrente viene prima salvato (copiato accanto a quello corrente) e ripristinato automaticamente se qualcosa va storto. Se desiderate conservare il backup al termine del processo di aggiornamento, potete usare l'opzione `--keep-backup`.

Questo comando potrebbe richiedere privilegi elevati se il vostro utente non ha i permessi per scrivere sul file eseguibile.



### `caddy add-package`

<a id="caddy-add-package"></a>
<i>⚠️ Sperimentale</i>

<pre><code class="cmd bash">caddy add-package &lt;pacchetti...&gt;
	[-k, --keep-backup]</code></pre>

In modo simile a `caddy upgrade`, sostituisce il binario Caddy corrente con l'ultima versione con gli stessi moduli installati, *più* i pacchetti elencati come argomenti inclusi nel nuovo binario. Trovate l'elenco dei pacchetti installabili nella nostra [pagina di download](/download). Ogni argomento deve essere il nome completo del pacchetto.

Ad esempio:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



### `caddy remove-package`

<a id="caddy-remove-package"></a>
<i>⚠️ Sperimentale</i>

<pre><code class="cmd bash">caddy remove-package &lt;pacchetti...&gt;
	[-k, --keep-backup]</code></pre>

In modo simile a `caddy upgrade`, sostituisce il binario Caddy corrente con l'ultima versione con gli stessi moduli installati, ma *senza* i pacchetti elencati come argomenti, se esistevano nel binario corrente. Eseguite `caddy list-modules --packages` per vedere l'elenco dei nomi dei pacchetti dei moduli non standard inclusi nel binario corrente.



### `caddy validate`

<a id="caddy-validate"></a>
<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

Valida un file di configurazione, quindi termina. Questo comando deserializza la configurazione, quindi carica e predispone tutti i suoi moduli come per avviare la configurazione, ma quest'ultima non viene effettivamente avviata. Ciò espone gli errori in una configurazione che sorgono durante le fasi di caricamento o predisposizione ed è un controllo degli errori più rigoroso rispetto alla semplice serializzazione di una configurazione in JSON.

`--config` è il file di configurazione da validare. Se `-`, la configurazione viene letta dallo stdin. Il valore predefinito è il `Caddyfile` nella directory corrente, se presente.

`--adapter` è il nome dell'adattatore di configurazione da usare. Questo flag non è necessario se il nome del file `--config` inizia con `Caddyfile` o termina con `.caddyfile`, il che assume l'adattatore `caddyfile`. Altrimenti, questo flag è obbligatorio se il file di configurazione fornito non è nel formato JSON nativo di Caddy.

`--envfile` carica le variabili d'ambiente dal file specificato, nel formato `CHIAVE=VALORE`. Sono supportati i commenti che iniziano con `#`; le chiavi possono avere il prefisso `export`; i valori possono essere racchiusi tra virgolette doppie (le virgolette interne possono essere precedute da escape); sono supportati valori su più righe.



### `caddy version`

<a id="caddy-version"></a>
<pre><code class="cmd bash">caddy version</code></pre>

Stampa la versione e termina.



## Segnali

<a id="signals"></a>
Caddy intercetta alcuni segnali e ne ignora altri. I segnali possono avviare specifici comportamenti del processo.

Segnale | Comportamento
-------|----------
`SIGINT` | Uscita graduale. Inviate nuovamente il segnale per forzare l'uscita immediata.
`SIGQUIT` | Chiude Caddy immediatamente, ma pulisce comunque i lock nello storage perché è importante.
`SIGTERM` | Uscita graduale.
`SIGUSR1` | Ricarica il file di configurazione, ma solo se avviato con `caddy run` (senza `--resume`) e se non sono state apportate modifiche alla configurazione tramite [l'API](/docs/api) (incluso [`caddy reload`](#caddy-reload)).
`SIGUSR2` | Ignorato.
`SIGHUP` | Ignorato.

Un'uscita graduale significa che non vengono più accettate nuove connessioni e le connessioni esistenti verranno esaurite prima che il socket venga chiuso. Può essere applicato un periodo di grazia (ed è configurabile). Una volta terminato il periodo di grazia, le connessioni verranno interrotte forzatamente. I lock nello storage e altre risorse che i singoli moduli devono rilasciare vengono puliti durante un arresto graduale.

Quando viene ricevuto un segnale di ricaricamento della configurazione (`SIGUSR1`), questo agisce come un ricaricamento forzato (ovvero ricarica comunque anche se il testo della configurazione è invariato), il che può ricaricare da disco i file dipendenti come i certificati TLS. 

I ricaricamenti della configurazione basati sui segnali sono abilitati solo se Caddy viene avviato con `caddy run` con un file di configurazione. Diventano disabilitati (segnali ignorati, con un avviso nel log) se Caddy viene avviato con `--resume` (poiché implica un flusso di lavoro basato su API), o se viene ricevuta una qualsiasi modifica alla configurazione tramite l'API di amministrazione, o se viene eseguito `caddy reload` con un nome file o un adattatore di configurazione *diverso* da quello con cui era stato originariamente avviato. Questo per evitare conflitti tra i metodi di ricaricamento.



## Codici di uscita

<a id="exit-codes"></a>
Caddy restituisce un codice quando il processo termina:

Codice | Significato
-----|---------
`0` | Uscita normale.
`1` | Avvio fallito. **Non riavviate automaticamente il processo; probabilmente si verificherà di nuovo un errore a meno che non vengano apportate modifiche.**
`2` | Uscita forzata. Caddy è stato costretto a uscire senza pulire le risorse.
`3` | Uscita fallita. Caddy è uscito con alcuni errori durante la pulizia.

In bash, potete ottenere il codice di uscita dell'ultimo comando con `echo $?`.
