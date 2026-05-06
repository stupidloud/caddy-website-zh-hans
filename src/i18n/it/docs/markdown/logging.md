---
title: Come funziona il logging
---

Come funziona il logging
========================

Caddy dispone di funzionalità di logging potenti e flessibili, ma potrebbero essere diverse da quelle a cui siete abituati, specialmente se provenite da hosting condivisi più arcaici o da altri server web legacy.


## Panoramica

Ci sono due aspetti principali del logging: emissione e consumo.

**Emissione** significa produrre messaggi. Si compone di tre passaggi:

1. Raccolta delle informazioni rilevanti (contesto)
2. Costruzione di una rappresentazione utile (codifica)
3. Invio di tale rappresentazione a un output (scrittura)

Questa funzionalità è integrata nel core di Caddy, consentendo a qualsiasi parte della base di codice di Caddy o dei moduli (plugin) di emettere log.

**Consumo** è l'acquisizione e l'elaborazione dei messaggi. Per essere utili, i log emessi devono essere consumati. I log che vengono solo scritti ma mai letti non offrono alcun valore. Consumare i log può essere semplice quanto un amministratore che legge l'output della console, o avanzato quanto collegare uno strumento di aggregazione dei log o un servizio cloud per filtrare, contare e indicizzare i messaggi di log.

### Il ruolo di Caddy

*Caddy è un emettitore di log*. Non consuma i log, se non per l'elaborazione minima richiesta per codificarli e scriverli. Questo è importante perché mantiene il core di Caddy più semplice, portando a meno bug e casi limite, riducendo al contempo l'onere di manutenzione. In definitiva, l'elaborazione dei log è al di fuori dell'ambito del core di Caddy.

Tuttavia, c'è sempre la possibilità di un modulo app di Caddy che consumi i log (al momento, per quanto ne sappiamo, non esiste ancora).


## Log strutturati

Come per la maggior parte delle applicazioni moderne, i log di Caddy sono *strutturati*. Ciò significa che l'informazione in un messaggio non è semplicemente una stringa opaca o una sequenza di byte. Al contrario, i dati rimangono fortemente tipizzati e sono associati a singoli *nomi di campo* (field names) fino al momento di codificare il messaggio e scriverlo.

Confrontate i tradizionali log non strutturati &mdash; come l'arcaico Common Log Format (CLF) &mdash; comunemente usati con i server HTTP tradizionali:

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Questo formato "ha una struttura" ma non è "strutturato": può essere usato solo per loggare richieste HTTP. Non c'è un modo (efficiente) per codificarlo diversamente, perché è una stringa opaca di byte. Mancano inoltre molte informazioni. Non include nemmeno l'header Host della richiesta! Questo formato di log è utile solo quando si ospita un singolo sito e per ottenere le informazioni più elementari sulle richieste.

<aside class="tip">
	La mancanza di informazioni sull'host nel CLF è il motivo per cui questi log di solito devono essere scritti in file separati quando si ospita più di un sito: non c'è altro modo per conoscere l'header Host dalla richiesta!
</aside>

Ora confrontate un messaggio di log strutturato equivalente di Caddy, codificato in JSON e formattato per la visualizzazione:

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Potete vedere come il log strutturato sia molto più utile e contenga molte più informazioni. L'abbondanza di informazioni in questo messaggio di log non è solo utile, ma non comporta praticamente alcun sovraccarico prestazionale: i log di Caddy sono "zero-allocation". I log strutturati non hanno restrizioni sui tipi di dati o sul contesto: possono essere usati in qualsiasi percorso del codice e includere qualsiasi tipo di informazione.

Poiché i log sono strutturati e fortemente tipizzati, possono essere codificati in qualsiasi formato. Quindi, se non volete lavorare con il JSON, i log possono essere codificati in qualsiasi altra rappresentazione. Caddy ne supporta altri tramite [moduli encoder di log](/docs/json/logging/logs/encoder/), e ne possono essere aggiunti ancora di più.

**Ancora più importante** nella distinzione tra log strutturati e formati legacy, è che con una penalità prestazionale un log strutturato [può essere trasformato nel formato legacy Common Log Format <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), ma non viceversa. Non è banale (o almeno non è efficiente) passare dal CLF a formati strutturati, ed è impossibile data la mancanza di informazioni.

In sostanza, il logging efficiente e strutturato promuove generalmente queste filosofie:

- Meglio troppi log che troppo pochi
- Filtrare è meglio che scartare
- Rimandare la codifica per una maggiore flessibilità e interoperabilità
 

## Emissione

Nel codice, un'emissione di log somiglia a quanto segue:

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Questa è un'effettiva riga di codice tratta dal reverse proxy di Caddy. Questa riga è ciò che vi permette di ispezionare le richieste agli upstream configurati quando avete abilitato il logging di debug. È un dato inestimabile durante la risoluzione dei problemi!
</aside>

Potete vedere che questa singola chiamata di funzione contiene il livello di log, un messaggio e diversi campi di dati. Tutti questi sono fortemente tipizzati e Caddy usa una libreria di logging zero-allocation, quindi le emissioni di log sono veloci ed efficienti, quasi senza sovraccarico.

La variabile `logger` è un `zap.Logger` che può avere qualsiasi quantità di contesto associata, inclusi sia un nome che campi di dati. Ciò consente ai logger di "ereditare" dai contesti padre in modo molto pulito, abilitando tracciamenti e metriche avanzati.

Da lì, il messaggio viene inviato attraverso una pipeline di elaborazione altamente efficiente dove viene codificato e scritto.


## Pipeline di logging

Come avete visto sopra, i messaggi sono emessi dai **logger**. I messaggi vengono poi inviati ai **log** per l'elaborazione.

Caddy vi permette di [configurare più log](/docs/json/logging/logs/) che possono elaborare i messaggi. Un log è composto da un encoder, un writer, un livello minimo, un rapporto di campionamento e un elenco di logger da includere o escludere. In Caddy c'è sempre un log predefinito chiamato `default`. Potete personalizzarlo specificando un log con chiave `"default"` in [questo oggetto](/docs/json/logging/logs/) nella configurazione.

<aside class="tip">
	Questo sarebbe un buon momento per [esplorare la documentazione del logging di Caddy](/docs/json/logging/) in modo da familiarizzare con la struttura e i parametri di cui stiamo parlando.
</aside>


- **Encoder:** Il formato del log. Trasforma la rappresentazione dei dati in memoria in una sequenza di byte. Gli encoder hanno accesso a tutti i campi di un messaggio di log.
- **Writer:** L'output del log. Può essere qualsiasi modulo writer di log, come un file o un socket di rete. Scrive semplicemente byte.
- **Livello (Level):** I log hanno vari livelli, da DEBUG a FATAL. I messaggi inferiori al livello specificato verranno ignorati dal log.
- **Campionamento (Sampling):** Percorsi estremamente caldi possono emettere più log di quanti ne possano essere elaborati efficacemente; abilitare il campionamento è un modo per ridurre il carico pur ottenendo un campione rappresentativo di messaggi.
- **Includi/escludi (Include/exclude):** Ogni messaggio è emesso da un logger, che ha un nome (solitamente derivato dall'ID del modulo). I log possono includere o escludere messaggi provenienti da determinati logger.

Quando un messaggio di log viene emesso da Caddy:

- Il nome del logger di origine viene controllato rispetto all'elenco include/exclude di ogni log; se incluso (o non escluso), viene ammesso in quel log.
- Se il campionamento è abilitato, un rapido calcolo determina se conservare il messaggio di log.
- Il messaggio viene codificato usando l'encoder configurato del log.
- I byte codificati vengono quindi scritti nel writer configurato del log.

Per impostazione predefinita, tutti i messaggi vanno a tutti i log configurati. Questo aderisce ai valori del logging strutturato descritti sopra. Potete limitare quali messaggi vanno a quali log impostando i loro elenchi include/exclude, ma questo serve principalmente per filtrare messaggi da moduli diversi; non è inteso per essere usato come un servizio di aggregazione dei log. Per mantenere la pipeline di logging di Caddy snella ed efficiente, l'elaborazione avanzata dei messaggi di log è rimandata al consumo.

## Consumo

Dopo che i messaggi sono stati inviati a un output, un consumatore li leggerà, li analizzerà e li gestirà di conseguenza.

Questo è un dominio di problemi molto diverso dall'emissione dei log e il core di Caddy non gestisce il consumo (sebbene un modulo app di Caddy certamente potrebbe farlo). Esistono numerosi strumenti che potete usare per elaborare flussi di messaggi JSON (o altri formati) e visualizzare, filtrare, indicizzare e interrogare i log. Potreste persino scriverne o implementarne uno vostro.

Ad esempio, se eseguite software legacy che richiede CLF separato in file diversi in base a un campo particolare (es. hostname), potreste usare o scrivere un semplice strumento che legge il JSON, chiama `sprintf()` per creare una stringa CLF e poi la scrive in un file in base al valore nel campo `request.host`.

Le funzionalità di logging di Caddy possono essere usate anche per implementare metriche e tracciamento: le metriche contano fondamentalmente i messaggi con determinate caratteristiche, mentre il tracciamento collega più messaggi tra loro in base alle comunanze tra essi.

Ci sono innumerevoli possibilità per ciò che potete fare consumando i log di Caddy!
