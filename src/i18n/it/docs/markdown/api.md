---
title: "API"
---

# API

Caddy viene configurato tramite un endpoint di amministrazione a cui è possibile accedere via HTTP utilizzando un'API [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://it.wikipedia.org/wiki/Representational_state_transfer). È possibile [configurare questo endpoint](/docs/json/admin/) nella configurazione di Caddy.

**Indirizzo predefinito: `localhost:2019`**

L'indirizzo predefinito può essere modificato impostando la variabile d'ambiente `CADDY_ADMIN`. Alcuni metodi di installazione potrebbero impostarlo su un valore diverso. L'indirizzo nella configurazione di Caddy ha sempre la precedenza sul valore predefinito.

<aside class="tip">
	Se state eseguendo codice non attendibile sul vostro server (attenzione! 😬), assicuratevi di proteggere il vostro endpoint di amministrazione isolando i processi, applicando patch ai programmi vulnerabili e configurando l'endpoint affinché si colleghi a un socket unix con permessi limitati.
</aside>

L'ultima configurazione verrà salvata su disco dopo ogni modifica (a meno che non sia [disabilitata](/docs/json/admin/config/)). È possibile riprendere l'ultima configurazione funzionante dopo un riavvio con [`caddy run --resume`](/docs/command-line#caddy-run), garantendo la persistenza della configurazione in caso di interruzioni di corrente o simili.

Per iniziare con l'API, provate il nostro [tutorial sull'API](/docs/api-tutorial) o, se avete solo un minuto, la nostra [guida rapida all'API](/docs/quick-starts/api).

---

- **[POST /load](#post-load)**
  Imposta o sostituisce la configurazione attiva

- **[POST /stop](#post-stop)**
  Ferma la configurazione attiva ed esce dal processo

- **[GET /config/[path]](#get-configpath)**
  Esporta la configurazione al percorso indicato

- **[POST /config/[path]](#post-configpath)**
  Imposta o sostituisce un oggetto; aggiunge a un array
  
- **[PUT /config/[path]](#put-configpath)**
  Crea un nuovo oggetto; inserisce in un array

- **[PATCH /config/[path]](#patch-configpath)**
  Sostituisce un oggetto esistente o un elemento di un array

- **[DELETE /config/[path]](#delete-configpath)**
  Elimina il valore al percorso indicato

- **[Uso di `@id` in JSON](#uso-di-id-in-json)**
  Esplora facilmente la struttura della configurazione

- **[Modifiche alla configurazione concorrenti](#modifiche-alla-configurazione-concorrenti)**
  Evita collisioni quando si apportano modifiche non sincronizzate alla configurazione

- **[POST /adapt](#post-adapt)**
  Adatta una configurazione in JSON senza eseguirla

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Restituisce informazioni su una particolare CA dell'[app PKI](/docs/json/apps/pki/)

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Restituisce la catena di certificati di una particolare CA dell'[app PKI](/docs/json/apps/pki/)

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Restituisce lo stato attuale degli upstream proxy configurati


## POST /load

Imposta la configurazione di Caddy, sovrascrivendo qualsiasi configurazione precedente. L'operazione è bloccante finché il ricaricamento non è completato o fallisce. Le modifiche alla configurazione sono leggere, efficienti e non comportano tempi di inattività. Se la nuova configurazione fallisce per qualsiasi motivo, viene ripristinata la vecchia configurazione senza interruzioni.

Questo endpoint supporta diversi formati di configurazione tramite gli adattatori. L'header Content-Type della richiesta indica il formato utilizzato nel corpo della richiesta. Di solito dovrebbe essere `application/json`, che rappresenta il formato nativo di Caddy. Per altri formati, specificate il Content-Type appropriato in modo che il valore dopo la barra / sia il nome dell'adattatore da usare. Ad esempio, per inviare un Caddyfile, usate un valore come `text/caddyfile`; per JSON 5, usate `application/json5`; ecc.

Se la nuova configurazione è identica a quella attuale, non avverrà alcun ricaricamento. Forzare il ricaricamento, impostate `Cache-Control: must-revalidate` negli header della richiesta.

### Esempi

Impostare una nuova configurazione attiva:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Nota: il flag `-d` di curl rimuove i ritorni a capo, quindi se il vostro formato di configurazione è sensibile alle interruzioni di riga (es. il Caddyfile), usate invece `--data-binary`:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## POST /stop

Arresta gradualmente il server ed esce dal processo. Per fermare solo la configurazione in esecuzione senza uscire dal processo, usate [DELETE /config/](#delete-configpath).

### Esempio

Arrestare il processo:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


## GET /config/[path]

Esporta la configurazione attuale di Caddy al percorso indicato. Restituisce un corpo JSON.

### Esempi

Esportare l'intera configurazione formattata (pretty-print):

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

Esportare solo gli indirizzi di ascolto:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



## POST /config/[path]

Modifica la configurazione di Caddy al percorso indicato con il corpo JSON della richiesta. Se il valore di destinazione è un array, POST aggiunge (append); se è un oggetto, lo crea o lo sostituisce.

Come caso speciale, è possibile aggiungere più elementi a un array se:

1. il percorso termina con `/...`
2. l'elemento del percorso prima di `/...` si riferisce a un array
3. il payload è un array

In questo caso, gli elementi nell'array del payload verranno espansi e ognuno di essi verrà aggiunto all'array di destinazione. In termini di Go, questo avrebbe lo stesso effetto di:

```go
baseSlice = append(baseSlice, newElems...)
```

### Esempi

Aggiungere un indirizzo di ascolto:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Aggiungere più indirizzi di ascolto:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

## PUT /config/[path]

Modifica la configurazione di Caddy al percorso indicato con il corpo JSON della richiesta. Se il valore di destinazione è una posizione (indice) in un array, PUT inserisce; se è un oggetto, crea rigorosamente un nuovo valore.

### Esempio

Aggiungere un indirizzo di ascolto nella prima posizione:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


## PATCH /config/[path]

Modifica la configurazione di Caddy al percorso indicato con il corpo JSON della richiesta. PATCH sostituisce rigorosamente un valore esistente o un elemento di un array.

### Esempio

Sostituire gli indirizzi di ascolto:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



## DELETE /config/[path]

Rimuove la configurazione di Caddy al percorso indicato. DELETE elimina il valore di destinazione.

### Esempi

Per scaricare l'intera configurazione attuale lasciando però il processo in esecuzione:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Per fermare solo uno dei vostri server HTTP:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


## Uso di `@id` in JSON

<a id="uso-di-id-in-json"></a>
Potete incorporare degli ID nel vostro documento JSON per accedere più facilmente a quelle parti del JSON.

Basta aggiungere un campo chiamato `"@id"` a un oggetto e assegnargli un nome unico. Ad esempio, se avete un handler reverse proxy a cui volete accedere frequentemente:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Per utilizzarlo, effettuate semplicemente una richiesta all'endpoint API `/id/` nello stesso modo in cui fareste con il corrispondente endpoint `/config/`, ma senza l'intero percorso. L'ID porta la richiesta direttamente in quell'ambito della configurazione per voi.

Ad esempio, per accedere agli upstream del reverse proxy senza un ID, il percorso sarebbe qualcosa come:

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

ma con un ID, il percorso diventa:

```
/id/my_proxy/upstreams
```

che è molto più facile da ricordare e scrivere a mano.

## Modifiche alla configurazione concorrenti

<aside class="tip">
	Questa sezione si applica a tutti gli endpoint `/config/`. È sperimentale e soggetta a modifiche.
</aside>

<a id="concurrent-config-changes"></a>
L'API di configurazione di Caddy fornisce [garanzie ACID <img src="/old/resources/images/external-link.svg" class="external-link">](https://it.wikipedia.org/wiki/ACID) per le singole richieste, ma le modifiche che coinvolgono più di una singola richiesta sono soggette a collisioni o perdita di dati se non opportunamente sincronizzate.

Ad esempio, due client potrebbero eseguire `GET /config/foo` contemporaneamente, apportare una modifica in quell'ambito (percorso di configurazione) e poi chiamare `POST|PUT|PATCH|DELETE /config/foo/...` nello stesso momento per applicare le loro modifiche, causando una collisione: uno sovrascriverà l'altro, oppure il secondo potrebbe lasciare la configurazione in uno stato imprevisto poiché applicata a una versione della configurazione diversa da quella su cui è stata preparata. Questo accade perché le modifiche non sono consapevoli l'una dell'altra.

L'API di Caddy non supporta transazioni che si estendono su più richieste e l'HTTP è un protocollo senza stato. Tuttavia, potete usare gli header `Etag` e `If-Match` per rilevare e prevenire le collisioni per qualsiasi modifica, come una sorta di controllo ottimistico della concorrenza. Questo è utile se c'è la possibilità di utilizzare gli endpoint `/config/...` di Caddy contemporaneamente senza sincronizzazione. Tutte le risposte alle richieste `GET /config/...` hanno un header HTTP chiamato `Etag` che contiene il percorso e un hash del contenuto in quell'ambito (es. `Etag: "/config/apps/http/servers 65760b8e"`). Basta impostare l'header `If-Match` in una richiesta di modifica con il valore dell'header `Etag` di una precedente richiesta `GET`.

L'algoritmo di base è il seguente:

1. Eseguire una richiesta `GET` a un qualsiasi ambito `S` all'interno della configurazione. Conservare l'header `Etag` della risposta.
2. Apportare la modifica desiderata sulla configurazione restituita.
3. Eseguire una richiesta `POST|PUT|PATCH|DELETE` nell'ambito `S`, impostando l'header `If-Match` della richiesta al valore `Etag` memorizzato.
4. Se la risposta è HTTP 412 (Precondition Failed), ripetere dal punto 1 o rinunciare dopo troppi tentativi.

Questo algoritmo consente in modo sicuro modifiche multiple e sovrapposte alla configurazione di Caddy senza sincronizzazione esplicita. È progettato affinché le modifiche simultanee a parti diverse della configurazione non richiedano un nuovo tentativo: solo le modifiche che si sovrappongono allo stesso ambito della configurazione possono causar una collisione e quindi richiedere un nuovo tentativo.


## POST /adapt

Adatta una configurazione nel formato JSON di Caddy senza caricarla o eseguirla. In caso di successo, il documento JSON risultante viene restituito nel corpo della risposta.

L'header Content-Type viene utilizzato per specificare il formato della configurazione nello stesso modo in cui funziona [/load](#post-load). Ad esempio, per adattare un Caddyfile, impostate `Content-Type: text/caddyfile`.

Questo endpoint adatterà qualsiasi formato di configurazione, a condizione che l'associato [adattatore](/docs/config-adapters) sia presente nella vostra build di Caddy.

### Esempi

Adattare un Caddyfile in JSON:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## GET /pki/ca/&lt;id&gt;

<a id="get-pkicaltidgt"></a>
Restituisce informazioni su una particolare CA dell'[app PKI](/docs/json/apps/pki/) tramite il suo ID. Se l'ID richiesto è quello predefinito (`local`), la CA verrà creata se non è già presente. Altri ID CA restituiranno un errore se non sono stati precedentemente creati.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


## GET /pki/ca/&lt;id&gt;/certificates

<a id="get-pkicaltidgtcertificates"></a>
Restituisce la catena di certificati di una particolare CA dell'[app PKI](/docs/json/apps/pki/) tramite il suo ID. Se l'ID richiesto è quello predefinito (`local`), la CA verrà creata se non è già presente. Altri ID CA restituiranno un errore se non sono stati precedentemente creati.

Questo endpoint è usato internamente dal comando [`caddy trust`](/docs/command-line#caddy-trust) per consentire l'installazione del certificato root della CA nell'archivio di fiducia del vostro sistema.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


## GET /reverse_proxy/upstreams

<a id="get-reverse-proxyupstreams"></a>
Restituisce lo stato attuale degli upstream (backend) del reverse proxy configurati come documento JSON.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Ogni voce nell'array JSON è un [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/) configurato memorizzato nel pool globale degli upstream.

- **address** è l'indirizzo di connessione dell'upstream.
- **num_requests** è il numero di richieste attive gestite attualmente dall'upstream.
- **fails** è il numero attuale di richieste fallite memorizzate, come configurato dai controlli sanitari passivi.

Se il vostro obiettivo è determinare la disponibilità di un backend, dovrete incrociare le proprietà rilevanti dell'upstream con la configurazione dell'handler che state utilizzando. Ad esempio, se avete abilitato i [controlli sanitari passivi](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) per i vostri proxy, dovete prendere in considerazione anche i valori `fails` e `num_requests` per determinare se un upstream è considerato disponibile: verificate che il numero di `fails` sia inferiore alla quantità massima configurata di fallimenti per il vostro proxy (es. [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)), e che `num_requests` sia inferiore o uguale alla quantità massima configurata di richieste per upstream (es. [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) per l'intero proxy, oppure [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) per i singoli upstream).
