---
title: "Guida introduttiva"
---

# Guida introduttiva

Benvenuti in Caddy! Questo tutorial esplorerà le basi dell'uso di Caddy e vi aiuterà a familiarizzare con esso a un livello generale.

**Obiettivi:**
- 🔲 Eseguire il demone
- 🔲 Provare l'API
- 🔲 Fornire una configurazione a Caddy
- 🔲 Testare la configurazione
- 🔲 Creare un Caddyfile
- 🔲 Usare l'adattatore di configurazione
- 🔲 Avviare con una configurazione iniziale
- 🔲 Confrontare JSON e Caddyfile
- 🔲 Confrontare API e file di configurazione
- 🔲 Eseguire in background
- 🔲 Ricaricamento della configurazione senza tempi di inattività

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- Competenze di base con editor di testo
- `caddy` e `curl` nel vostro PATH

---

**Se avete [installato Caddy](/docs/install) da un gestore di pacchetti, Caddy potrebbe essere già in esecuzione come servizio. In tal caso, interrompete il servizio prima di seguire questo tutorial.**

Iniziamo eseguendolo:

<pre><code class="cmd bash">caddy</code></pre>

Oops; senza un sottocomando, il comando `caddy` visualizza solo il testo di aiuto. Potete usarlo ogni volta che dimenticate cosa fare.

Per avviare Caddy come demone, usate il sottocomando `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Eseguire il demone</aside>

Questo comando blocca il terminale a tempo indeterminato, ma cosa sta facendo? Al momento... nulla. Per impostazione predefinita, la configurazione ("config") di Caddy è vuota. Possiamo verificarlo usando l'[API di amministrazione](/docs/api) in un altro terminale:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

Questo **non** è il vostro sito web: l'endpoint di amministrazione su localhost:2019 viene utilizzato per controllare Caddy ed è limitato a localhost per impostazione predefinita.

</aside>


<aside class="complete">Provare l'API</aside>

Possiamo rendere Caddy utile fornendogli una configurazione. Questo può essere fatto in molti modi, ma inizieremo effettuando una richiesta POST all'endpoint [/load](/docs/api#post-load) usando `curl` nella sezione successiva.



## La vostra prima configurazione

Per preparare la nostra richiesta, dobbiamo creare una configurazione. Nel suo nucleo, la configurazione di Caddy è semplicemente un [documento JSON](/docs/json/).

Salvate questo contenuto in un file JSON (es. `caddy.json`):

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

<aside class="tip">

Non è obbligatorio usare file di configurazione, ma lo faremo per questo tutorial. L'[API di amministrazione](/docs/api) di Caddy è progettata per essere utilizzata da altri programmi o script.

</aside>


Quindi caricatela:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Fornire una configurazione a Caddy</aside>

Possiamo verificare che Caddy abbia applicato la nostra nuova configurazione con un'altra richiesta GET:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Verificate che funzioni andando su [localhost:2015](http://localhost:2015) nel vostro browser o usando `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Se vedete _Hello, world!_, congratulazioni -- funziona! È sempre una buona idea assicurarsi che la configurazione funzioni come previsto, specialmente prima di passare alla produzione.

<aside class="complete">Testare la configurazione</aside>


## Il vostro primo Caddyfile

È stato _un bel po' di lavoro_ solo per un Hello World.

Un altro modo per configurare Caddy è con il [**Caddyfile**](/docs/caddyfile). La stessa configurazione che abbiamo scritto sopra in JSON può essere espressa semplicemente come:

```caddy
:2015

respond "Hello, world!"
```


Salvate questo contenuto in un file chiamato `Caddyfile` (senza estensione) nella directory corrente.

<aside class="complete">Creare un Caddyfile</aside>

Fermate Caddy se è già in esecuzione (<kbd>Ctrl</kbd>+<kbd>C</kbd>), quindi eseguite:

<pre><code class="cmd bash">caddy adapt</code></pre>

O se avete salvato il Caddyfile altrove o lo avete chiamato in modo diverso da `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /percorso/del/Caddyfile</code></pre>

Vedrete un output JSON! Cosa è successo?

Abbiamo appena usato un [_adattatore di configurazione_](/docs/config-adapters) per convertire il nostro Caddyfile nella struttura JSON nativa di Caddy.

<aside class="complete">Usare l'adattatore di configurazione</aside>

Anche se potremmo prendere quell'output ed effettuare un'altra richiesta API, possiamo saltare tutti questi passaggi perché il comando `caddy` può farlo per noi. Se nella directory corrente è presente un file chiamato Caddyfile e non è specificata altra configurazione, Caddy caricherà il Caddyfile, lo adatterà per noi e lo eseguirà immediatamente.

Ora che c'è un Caddyfile nella cartella corrente, eseguiamo di nuovo `caddy run`:

<pre><code class="cmd bash">caddy run</code></pre>

O se il vostro Caddyfile è altrove:

<pre><code class="cmd bash">caddy run --config /percorso/del/Caddyfile</code></pre>

(Se si chiama in un altro modo che non inizia con "Caddyfile", dovrete specificare `--adapter caddyfile`.)

Potete ora provare a caricare nuovamente il vostro sito e vedrete che funziona!

<aside class="complete">Avviare con una configurazione iniziale</aside>

Come potete vedere, ci sono diversi modi per avviare Caddy con una configurazione iniziale:

- Un file chiamato Caddyfile nella directory corrente
- Il flag `--config` (opzionalmente con il flag `--adapter`)
- Il flag `--resume` (se una configurazione è stata caricata in precedenza)


## JSON vs. Caddyfile

Ora sapete che il Caddyfile viene semplicemente convertito in JSON per voi.

Il Caddyfile sembra più facile del JSON, ma dovreste usarlo sempre? Ci sono pro e contro per ogni approccio. La risposta dipende dalle vostre esigenze e dal caso d'uso.

JSON | Caddyfile
-----|----------
Facile da generare | Facile da creare a mano
Facilmente programmabile | Scomodo da automatizzare
Estremamente espressivo | Moderatamente espressivo
Gamma completa di funzionalità Caddy | La maggior parte delle funzionalità Caddy
Permette l'esplorazione della configurazione | Non è possibile esplorare all'interno del Caddyfile
Modifiche parziali alla configurazione | Solo modifiche all'intera configurazione
Può essere esportato | Non può essere esportato
Compatibile con tutti gli endpoint API | Compatibile con alcuni endpoint API
Documentazione generata automaticamente | Documentazione scritta a mano
Ubiquo | Di nicchia
Più efficiente | Richiede più calcolo
Un po' noioso | Più divertente
**Saperne di più: [Struttura JSON](/docs/json/)** | **Saperne di più: [Documentazione Caddyfile](/docs/caddyfile)**

Dovrete decidere quale sia il migliore per il vostro caso d'uso.

È importante notare che sia JSON che il Caddyfile (e [qualsiasi altro adattatore di configurazione supportato](/docs/config-adapters)) possono essere utilizzati con l'[API di Caddy](/docs/api). Tuttavia, ottenete l'intera gamma di funzionalità e caratteristiche API di Caddy se utilizzate JSON. Se utilizzate un adattatore di configurazione, l'unico modo per caricare o modificare la configurazione con l'API è l'[endpoint /load](/docs/api#post-load).

<aside class="complete">Confrontare JSON e Caddyfile</aside>


## API vs. File di configurazione

<aside class="tip">

Sotto il cofano, anche i file di configurazione passano attraverso gli endpoint API di Caddy; il comando `caddy` si occupa solo di impacchettare quelle chiamate API per voi.

</aside>


Dovrete anche decidere se il vostro flusso di lavoro debba essere basato su API o su CLI. (È *possibile* usare sia l'API che i file di configurazione sullo stesso server, ma non lo raccomandiamo: meglio avere un'unica fonte di verità.)

API | File di configurazione
----|-------------
Modifiche alla configurazione con richieste HTTP | Modifiche alla configurazione con comandi shell
Facile da scalare | Difficile da scalare
Difficile da gestire a mano | Facile da gestire a mano
Molto divertente | Anche divertente
**Saperne di più: [Tutorial API](/docs/api-tutorial)** | **Saperne di più: [Tutorial Caddyfile](/docs/caddyfile-tutorial)**

<aside class="tip">
	Gestire manualmente la configurazione di un server con l'API è assolutamente fattibile con strumenti adeguati, ad esempio: qualsiasi applicazione client REST.
</aside>

La scelta tra flusso di lavoro API o file di configurazione è ortogonale all'uso degli adattatori di configurazione: potete usare JSON ma memorizzarlo in un file e usare l'interfaccia a riga di comando; viceversa, potete anche usare il Caddyfile con l'API.

Ma la maggior parte delle persone userà le combinazioni JSON+API o Caddyfile+CLI.

Come potete vedere, Caddy è adatto per un'ampia varietà di casi d'uso e distribuzioni!

<aside class="complete">Confrontare API e file di configurazione</aside>



## Start, stop, run

Dato che Caddy è un server, viene eseguito a tempo indeterminato. Ciò significa che il vostro terminale non si sbloccherà dopo aver eseguito `caddy run` finché il processo non viene terminato (solitamente con <kbd>Ctrl</kbd>+<kbd>C</kbd>).

Sebbene `caddy run` sia il più comune e solitamente raccomandato (specialmente quando si crea un servizio di sistema!), potete in alternativa usare `caddy start` per avviare Caddy e farlo girare in background:

<pre><code class="cmd bash">caddy start</code></pre>

Questo vi permetterà di usare nuovamente il terminale, il che è comodo in alcuni ambienti interattivi headless.

Dovrete poi interrompere il processo voi stessi, dato che <kbd>Ctrl</kbd>+<kbd>C</kbd> non lo fermerà per voi:

<pre><code class="cmd bash">caddy stop</code></pre>

Oppure usate l'[endpoint /stop](/docs/api#post-stop) dell'API.

<aside class="complete">Eseguire in background</aside>


## Ricaricamento della configurazione

Il vostro server può eseguire ricaricamenti/modifiche della configurazione senza tempi di inattività (zero-downtime).

Tutti gli [endpoint API](/docs/api) che caricano o modificano la configurazione sono sicuri e senza interruzioni.

Quando usate la riga di comando, tuttavia, potreste essere tentati di usare <kbd>Ctrl</kbd>+<kbd>C</kbd> per fermare il server e poi riavviarlo per applicare la nuova configurazione. Non fatelo: fermare e avviare il server è ortogonale alle modifiche della configurazione e comporterà tempi di inattività.

<aside class="tip">
	Fermare il server ne causerà l'interruzione del servizio.
</aside>

Invece, usate il comando [`caddy reload`](/docs/command-line#caddy-reload) per una modifica della configurazione senza interruzioni:

<pre><code class="cmd bash">caddy reload</code></pre>

Questo comando in realtà utilizza semplicemente l'API sotto il cofano. Caricherà e, se necessario, adatterà il vostro file di configurazione in JSON, quindi sostituirà gradualmente la configurazione attiva senza tempi di inattività.

Se si verificano errori nel caricamento della nuova configurazione, Caddy ripristina l'ultima configurazione funzionante.

<aside class="tip">
	Tecnicamente, la nuova configurazione viene avviata prima che la vecchia venga fermata, quindi per un breve periodo entrambe le configurazioni sono in esecuzione! Se la nuova configurazione fallisce, l'operazione viene interrotta con un errore, mentre quella vecchia semplicemente non viene fermata.
</aside>

<aside class="complete">Ricaricamento della configurazione senza tempi di inattività</aside>
