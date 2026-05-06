---
title: "Tutorial sull'API"
---

# Tutorial sull'API

Questo tutorial vi mostrerà come utilizzare l'[API di amministrazione](/docs/api) di Caddy, che consente l'automazione in modo programmabile.

**Obiettivi:**
- 🔲 Eseguire il demone
- 🔲 Fornire una configurazione a Caddy
- 🔲 Testare la configurazione
- 🔲 Sostituire la configurazione attiva
- 🔲 Esplorare la configurazione
- 🔲 Usare i tag `@id`

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- Esperienza di base con il JSON
- `caddy` e `curl` nel vostro PATH

---

Per avviare il demone Caddy, usate il sottocomando `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Eseguire il demone</aside>

Questo comando blocca il terminale a tempo indeterminato, ma cosa sta facendo? Al momento... nulla. Per impostazione predefinita, la configurazione ("config") di Caddy è vuota. Possiamo verificarlo usando l'[API di amministrazione](/docs/api) in un altro terminale:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Possiamo rendere Caddy utile fornendogli una configurazione. Un modo per farlo è effettuare una richiesta POST all'endpoint [/load](/docs/api#post-load). Proprio come ogni richiesta HTTP, ci sono molti modi per farlo, ma in questo tutorial useremo `curl`.

## La vostra prima configurazione

Per preparare la nostra richiesta, dobbiamo creare una configurazione. La configurazione di Caddy è semplicemente un [documento JSON](/docs/json/) (o [qualsiasi cosa che si converta in JSON](/docs/config-adapters)).

<aside class="tip">
	I file di configurazione non sono obbligatori. L'API di configurazione può sempre essere utilizzata senza file, il che è comodo quando si automatizzano le cose. Questo tutorial usa un file perché è più pratico per la modifica manuale.
</aside>

Salvate questo contenuto in un file JSON:

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

Quindi caricatela:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Assicuratevi di non dimenticare la @ davanti al nome del file; questo indica a curl che state inviando un file.
</aside>

<aside class="complete">Fornire una configurazione a Caddy</aside>

Possiamo verificare che Caddy abbia applicato la nostra nuova configurazione con un'altra richiesta GET:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Verificate che funzioni andando su [localhost:2015](http://localhost:2015) nel vostro browser o usando `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">Testare la configurazione</aside>

Se vedete _Hello, world!_, congratulazioni -- funziona! È sempre una buona idea assicurarsi che la configurazione funzioni come previsto, specialmente prima di passare alla produzione.

Cambiamo il nostro messaggio di benvenuto da "Hello world!" a qualcosa di un po' più motivazionale: "I can do hard things." (Posso fare cose difficili). Apportate questa modifica nel vostro file di configurazione, in modo che l'oggetto handler appaia ora così:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

Salvate il file di configurazione, quindi aggiornate la configurazione attiva di Caddy eseguendo nuovamente la stessa richiesta POST:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Sostituire la configurazione attiva</aside>

Per sicurezza, verificate che la configurazione sia stata aggiornata:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Verificatelo ricaricando la pagina nel vostro browser (o eseguendo nuovamente `curl`) e vedrete un messaggio d'ispirazione!


## Esplorazione della configurazione (Config traversal)

Invece di caricare l'intero file di configurazione per una piccola modifica, utilizziamo una potente funzionalità dell'API di Caddy per effettuare il cambiamento senza mai toccare il nostro file di configurazione.

<aside class="tip">
	Effettuare piccole modifiche ai server di produzione sostituendo l'intera configurazione come abbiamo fatto sopra può essere pericoloso; è come avere l'accesso root a un file system. L'API di Caddy vi consente di limitare l'ambito delle modifiche per garantire che altre parti della configurazione non vengano modificate accidentalmente.
</aside>

Usando il percorso dell'URI della richiesta, possiamo esplorare la struttura della configurazione e aggiornare solo la stringa del messaggio (assicuratevi di scorrere a destra se il testo è tagliato):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">
	Ogni volta che cambiate la configurazione usando l'API, Caddy mantiene una copia della nuova configurazione in modo da poterla [**riprendere (--resume)** più tardi](/docs/command-line#caddy-run)!
</aside>


Potete verificare che abbia funzionato con una richiesta GET simile, ad esempio:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Dovreste vedere:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">
	Potete usare il [comando `jq` <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) per abbellire l'output JSON: **`curl ... | jq`**
</aside>


<aside class="complete">Esplorare la configurazione</aside>

**Nota importante:** Dovrebbe essere ovvio, ma una volta utilizzata l'API per effettuare una modifica che non è nel file di configurazione originale, il vostro file di configurazione diventa obsoleto. Ci sono alcuni modi per gestire questa situazione:

- Usate il flag `--resume` del comando [caddy run](/docs/command-line#caddy-run) per utilizzare l'ultima configurazione attiva.
- Non mescolate l'uso dei file di configurazione con le modifiche via API; mantenete un'unica fonte di verità.
- [Esportate la nuova configurazione di Caddy](/docs/api#get-configpath) con una successiva richiesta GET (opzione meno raccomandata rispetto alle prime due).



## Uso di `@id` in JSON

L'esplorazione della configurazione è certamente utile, ma i percorsi sono un po' lunghi, non trovate?

Possiamo assegnare al nostro oggetto handler un [tag `@id`](/docs/api#using-id-in-json) per renderlo più facile da raggiungere:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Questo aggiunge una proprietà al nostro oggetto handler: `"@id": "msg"`, che ora appare così:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">
	I tag **@id** possono essere inseriti in qualsiasi oggetto e possono avere qualsiasi valore primitivo (solitamente una stringa). [Saperne di più](/docs/api#using-id-in-json)
</aside>


Possiamo quindi accedervi direttamente:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

E ora possiamo cambiare il messaggio con un percorso più breve:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

E controllarlo di nuovo:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">Usare i tag <code>@id</code></aside>
