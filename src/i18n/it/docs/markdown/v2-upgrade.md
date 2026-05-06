---
title: Aggiornamento a Caddy 2
---

Guida all'aggiornamento
=======================

Caddy 2 è una base di codice completamente nuova, scritta da zero, per migliorare Caddy 1. Caddy 2 non è retrocompatibile con Caddy 1. Ma non preoccupatevi: per la maggior parte delle configurazioni di base, non molto è cambiato. Questa guida vi aiuterà a effettuare la transizione nel modo più semplice possibile.

Questa guida non approfondirà le nuove funzionalità disponibili &mdash; che sono davvero fantastiche, tra l'altro, dovreste [impararle](/docs/getting-started) &mdash; l'obiettivo qui è solo quello di rendervi operativi su Caddy 2 velocemente.

- [Punti chiave](#high-order-bits)
- [Passaggi](#steps)
- [HTTPS e porte](#https-and-ports)
- [Riga di comando](#command-line)
- [Caddyfile](#caddyfile)
	- [Cambiamenti primari](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [File di servizio](#service-files)
- [Plugin](#plugins)
- [Ottenere aiuto](#getting-help)



## Punti chiave

<a id="high-order-bits"></a>
- "Caddy 2" si chiama ancora semplicemente `caddy`. Potremmo usare "Caddy 2" per chiarire a quale versione ci riferiamo per rendere la transizione meno confusa.
- La maggior parte degli utenti dovrà semplicemente sostituire il binario `caddy` e aggiornare la configurazione del `Caddyfile` (dopo aver verificato che funzioni).
- Potrebbe essere meglio approcciarsi a Caddy 2 senza supposizioni derivanti da Caddy 1.
- Potreste non essere in grado di replicare perfettamente la vostra configurazione di nicchia della v1 in v2. Di solito c'è una buona ragione per questo.
- La riga di comando non viene più utilizzata per la configurazione del server.
- Le variabili d'ambiente non sono più necessarie per la configurazione.
- Il modo principale per fornire a Caddy 2 la sua configurazione è tramite la sua [API](/docs/api), ma può essere utilizzato anche il [comando `caddy`](/docs/command-line).
- Dovreste sapere che il linguaggio di configurazione nativo di Caddy 2 è il [JSON](/docs/json/) e che il Caddyfile è solo un altro [adattatore di configurazione](/docs/config-adapters) che converte il formato in JSON per voi. Casi d'uso estremamente personalizzati/avanzati potrebbero richiedere il JSON, poiché non tutte le configurazioni possibili possono essere espresse dal Caddyfile.
- Il Caddyfile è quasi lo stesso, ma anche molto più potente; le direttive sono cambiate.



## Passaggi

<a id="steps"></a>
1. Familiarizzate con Caddy 2 seguendo il nostro tutorial [Guida introduttiva](/docs/getting-started).
2. Eseguite il passaggio 1 se non l'avete ancora fatto. Seriamente &mdash; non sottolineeremo mai abbastanza quanto sia importante sapere almeno come usare Caddy 2 (è più divertente!).
3. Usate la guida qui sotto per convertire i vostri comandi `caddy`.
4. Usate la guida qui sotto per convertire il vostro Caddyfile.
5. Testate la vostra nuova configurazione localmente o in staging.
6. Testate, testate e testate ancora.
7. Distribuite e divertitevi!



## HTTPS e porte

<a id="https-and-ports"></a>
La porta predefinita di Caddy non è più la `:2015`. La porta predefinita di Caddy 2 è la `:443` o, se non è noto alcun hostname/IP, la porta `:80`. Potete sempre personalizzare le porte nella vostra configurazione.

Il protocollo predefinito di Caddy 2 è [*sempre* HTTPS se è noto un hostname o un IP](/docs/automatic-https#overview). Questo è diverso da Caddy 1, dove solo i domini dall'aspetto pubblico usavano l'HTTPS per impostazione predefinita. Ora, *ogni* sito usa l'HTTPS (a meno che non lo disabilitiate specificando esplicitamente la porta `:80` o `http://`).

Agli indirizzi IP e ai domini localhost verranno emessi certificati da una [CA integrata e fidata localmente](/docs/automatic-https#local-https). Tutti gli altri domini useranno ZeroSSL o Let's Encrypt (tutto questo è configurabile).

La struttura di memorizzazione dei certificati e delle risorse ACME è cambiata. Caddy 2 probabilmente otterrà nuovi certificati per i vostri siti; ma se avete molti certificati potete migrali manualmente se non lo fa per voi. Consultate le issue [#2955](https://github.com/caddyserver/caddy/issues/2955) e [#3124](https://github.com/caddyserver/caddy/issues/3124) per i dettagli.



## Riga di comando

<a id="command-line"></a>
Il comando `caddy` è ora `caddy run`.

Tutti i flag della riga di comando sono diversi. Rimuoveteli; tutta la configurazione del server risiede ora all'interno del documento di configurazione effettivo (solitamente Caddyfile o JSON). Probabilmente troverete ciò di cui avete bisogno nella [struttura JSON](/docs/json/) o nelle [opzioni globali del Caddyfile](/docs/caddyfile/options) per sostituire la maggior parte dei flag da riga di comando della v1.

Un comando come `caddy -conf ../Caddyfile` diventerebbe `caddy run --config ../Caddyfile`.

Come in precedenza, se il vostro Caddyfile si trova nella cartella corrente, Caddy lo troverà e lo userà automaticamente; in tal caso non è necessario usare il flag `--config`.

I segnali sono per lo più gli stessi, tranne per il fatto che USR1 e USR2 non sono più supportati. Usate invece il comando [`caddy reload`](/docs/command-line#caddy-reload) o l'[API](/docs/api) per caricare una nuova configurazione.

Eseguire `caddy` senza alcuna configurazione serviva ad avviare un semplice server di file. L'equivalente in Caddy 2 è [`caddy file-server`](/docs/command-line#caddy-file-server).

Le variabili d'ambiente non sono più rilevanti, eccetto `HOME` (e, opzionalmente, qualsiasi variabile `XDG_*` impostata). La `CADDYPATH` è stata [sostituita dalle convenzioni del sistema operativo](/docs/conventions#file-locations).



## Caddyfile

<a id="caddyfile"></a>
Il [Caddyfile v2](/docs/caddyfile/concepts) è molto simile a quello con cui avete già familiarità. La cosa principale da fare è cambiare le direttive.

⚠️ **Assicuratevi di approfondire le nuove direttive!** Soprattutto se la vostra configurazione è avanzata, ci sono molte sfumature da considerare. Questi suggerimenti vi permetteranno di passare alla nuova versione piuttosto velocemente, ma leggete la documentazione completa per ogni direttiva così da comprendere le implicazioni dell'aggiornamento. E naturalmente, testate sempre accuratamente le vostre configurazioni prima di metterle in produzione.


### Cambiamenti primari

<a id="primary-changes"></a>
- Se state servendo file statici, dovrete aggiungere una [direttiva `file_server`](/docs/caddyfile/directives/file_server), poiché Caddy 2 non lo assume per impostazione predefinita. Caddy 2 non esegue nemmeno lo sniffing del MIME per impostazione predefinita, per ragioni di sicurezza; se manca un Content-Type, potreste dover impostare l'header voi stessi usando la direttiva [header](/docs/caddyfile/directives/header).

- Nella v1, potevate filtrare (o fare il "match") delle direttive solo per percorso della richiesta. Nella v2, il [matching delle richieste](/docs/caddyfile/matchers) è molto più potente. Qualsiasi direttiva v2 che aggiunge un middleware alla catena degli handler HTTP o che manipola la richiesta/risposta HTTP in qualsiasi modo sfrutta questa nuova funzionalità di matching. [Leggete di più sui matcher di richiesta v2.](/docs/caddyfile/matchers) Dovrete conoscerli per dare un senso al Caddyfile v2.

- Sebbene molti [placeholder](/docs/conventions#placeholders) siano rimasti gli stessi, molti sono cambiati e ne esistono ora [molti di nuovi](/docs/modules/http#docs), incluse delle [scorciatoie per il Caddyfile](/docs/caddyfile/concepts#placeholders).

- I log di Caddy 2 sono tutti strutturati e il formato predefinito è JSON. Tutti i livelli di log possono semplicemente andare allo stesso log per essere elaborati (ma potete personalizzarlo se necessario).

- Mentre in Caddy 1 facevate il match delle richieste per prefisso del percorso, il matching del percorso è ora esatto per impostazione predefinita in Caddy 2. Se volete fare il match di un prefisso come `/foo/`, avrete bisogno di `/foo/*` in Caddy 2.

Elencheremo qui alcune delle direttive v1 più comuni e descriveremo come convertirle per l'uso nel Caddyfile v2.

⚠️ **Solo perché una direttiva v1 manca da questa pagina non significa che Caddy 2 non possa farlo!** Alcune direttive v1 non sono necessarie, non si traducono bene o sono soddisfatte in altri modi nella v2. Per alcune personalizzazioni avanzate, potreste dover scendere al livello JSON per ottenere ciò che desiderate. Esplorate la [nostra documentazione](/docs/caddyfile) per trovare ciò di cui avete bisogno!


### basicauth
<a id="basicauth"></a>

L'autenticazione HTTP Basic si configura ancora con la direttiva [`basic_auth`](/docs/caddyfile/directives/basic_auth). Tuttavia, la configurazione di Caddy 2 non accetta password in chiaro. Dovete eseguirne l'hashing, operazione in cui il comando [`caddy hash-password`](/docs/command-line#caddy-hash-password) può aiutarvi.

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


### browse
<a id="browse"></a>

La navigazione dei file è ora abilitata tramite la direttiva [`file_server`](/docs/caddyfile/directives/file_server).

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


### errors
<a id="errors"></a>

Le pagine di errore personalizzate possono essere realizzate con [`handle_errors`](/docs/caddyfile/directives/handle_errors).


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

### ext
<a id="ext"></a>

Le estensioni di file implicite possono essere gestite con [`try_files`](/docs/caddyfile/directives/try_files).

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


### fastcgi
<a id="fastcgi"></a>

Supponendo che stiate servendo PHP, l'equivalente v2 è [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

Notate che la direttiva `fastcgi` della v1 faceva molto "sotto il cofano", incluso provare i file su disco, riscrivere le richieste e persino reindirizzare. Anche la direttiva `php_fastcgi` v2 fa queste cose per voi, ma la documentazione fornisce la sua [forma estesa](/docs/caddyfile/directives/php_fastcgi#expanded-form) che potete modificare se le vostre esigenze sono diverse.

Non è necessario alcun preset `php` nella v2, poiché la direttiva `php_fastcgi` assume PHP per impostazione predefinita. Una riga come `php_fastcgi 127.0.0.1:9000 php` farà pensare al reverse proxy che esista un secondo backend chiamato `php`, portando a errori di connessione.

Le sottodirettive sono diverse nella v2 &mdash; probabilmente non ne avrete bisogno di alcuna per il PHP.


### gzip
<a id="gzip"></a>

Una singola direttiva [`encode`](/docs/caddyfile/directives/encode) viene ora utilizzata per tutte le codifiche di risposta, inclusi molteplici formati di compressione.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

Curiosità: Caddy 2 supporta anche `zstd` (ma nessun browser lo supporta ancora).


### header
<a id="header"></a>

[Quasi invariata](/docs/caddyfile/directives/header), ma ora molto più potente poiché nella v2 può effettuare sostituzioni di sottostringhe.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


### log
<a id="log"></a>

Abilita il logging degli accessi; la direttiva [`log`](/docs/caddyfile/directives/log) può ancora essere utilizzata nella v2, ma tutti i log sono strutturati, codificati come JSON, per impostazione predefinita.

Il modo raccomandato per abilitare il logging degli accessi è semplicemente:

```caddy-d
log
```

che emette log strutturati su stderr (potete anche emettere su un file o su un socket di rete; consultate la documentazione della direttiva [`log`](/docs/caddyfile/directives/log)).

Per impostazione predefinita, i log saranno in formato JSON [strutturato](/docs/logging). Se avete ancora bisogno dei log nel Common Log Format (CLF) per ragioni legacy, potete usare il plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder).


### proxy
<a id="proxy"></a>

L'equivalente v2 è [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

I cambiamenti degni di nota alle sottodirettive sono che `header_upstream` e `header_downstream` sono diventati rispettivamente `header_up` e `header_down`; inoltre le sottodirettive relative al bilanciamento del carico hanno il prefisso `lb_`.

Un'altra differenza significativa è che il proxy v2 passa tutti gli header in entrata per impostazione predefinita (incluso l'header `Host`) e imposta l'header `X-Forwarded-For`. In altre parole, la modalità "transparent" della v1 è praticamente l'impostazione predefinita nella v2 (ma se avete bisogno di altri header come X-Real-IP dovete impostarli voi stessi). Potete ancora sovrascrivere/personalizzare l'header `Host` usando la sottodirettiva `header_up`.

Il proxying dei websocket "funziona e basta" nella v2; non è necessario "abilitare" i websocket come nella v1.

La sottodirettiva `without` è stata rimossa perché gli [stratagemmi di riscrittura](#rewrite) non sono più necessari nella v2 grazie al migliorato supporto dei matcher.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


### redir
<a id="redir"></a>

[Invariata](/docs/caddyfile/directives/redir), eccetto per alcuni dettagli riguardanti l'argomento opzionale del codice di stato. La maggior parte delle configurazioni non avrà bisogno di apportare modifiche.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


### rewrite
<a id="rewrite"></a>

La semantica della riscrittura della richiesta ("reindirizzamento interno") è leggermente cambiata. Se nella v1 usavate i cosiddetti "stratagemmi di riscrittura" (rewrite hack) per far corrispondere le richieste su qualcosa di diverso da un semplice prefisso del percorso, ciò è completamente non necessario nella v2.

La [nuova direttiva `rewrite`](/docs/caddyfile/directives/rewrite) è molto semplice ma molto potente, poiché la maggior parte della sua complessità è gestita dai [matcher](/docs/caddyfile/matchers) nella v2:

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Notate come usiamo semplicemente i normali [token matcher](/docs/caddyfile/matchers) di Caddy 2; non è più un caso speciale per questa direttiva.

Iniziate rimuovendo tutti gli stratagemmi di riscrittura; trasformateli invece in [matcher con nome](/docs/caddyfile/concepts#named-matchers). Valutate ogni `rewrite` della v1 per vedere se è realmente necessario nella v2. Suggerimento: un Caddyfile v1 che usa `rewrite` per aggiungere un prefisso al percorso e poi `proxy` con `without` per rimuovere lo stesso prefisso è uno stratagemma di riscrittura e può essere eliminato.

Potreste trovare utili le nuove direttive [`route`](/docs/caddyfile/directives/route) e [`handle`](/docs/caddyfile/directives/handle) per avere un maggiore controllo sulla logica di routing avanzata.


### root
<a id="root"></a>

[Invariata](/docs/caddyfile/directives/root).

Ricordate di aggiungere una [direttiva `file_server`](/docs/caddyfile/directives/file_server) se servite file statici, poiché Caddy 2 non lo assume per impostazione predefinita, mentre nella v1 era sempre abilitato.


### status
<a id="status"></a>

L'equivalente v2 è [`respond`](/docs/caddyfile/directives/respond), che può anche scrivere un corpo di risposta.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


### templates
<a id="templates"></a>

La sintassi generale della direttiva [`templates`](/docs/caddyfile/directives/templates) è invariata, ma le effettive azioni/funzioni dei template sono diverse e molto migliorate. Ad esempio, i template sono in grado di includere file, renderizzare markdown, effettuare sub-richieste interne, analizzare il front matter e altro ancora!

[Consultate la documentazione](/docs/modules/http.handlers.templates) per i dettagli sulle nuove funzioni.

- **v1:** `templates`
- **v2:** `templates`


### tls
<a id="tls"></a>

I fondamenti della direttiva [`tls`](/docs/caddyfile/directives/tls) non sono cambiati, ad esempio specificando il proprio certificato e chiave:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

But la [logica dell'auto-HTTPS](/docs/automatic-https) di Caddy *è* cambiata, quindi siatene consapevoli!

Anche i nomi delle suite di cifratura sono cambiati.

Una configurazione comune in Caddy 2 è usare `tls internal` per fargli servire un certificato fiduciario locale per un hostname di sviluppo che non sia `localhost` o un indirizzo IP.

La maggior parte dei siti non avrà affatto bisogno di questa direttiva.


## File di servizio

<a id="service-files"></a>
Raccomandiamo di usare [uno dei nostri file di unità systemd ufficiali](/docs/running#linux-service) per le installazioni di Caddy.

Se avete bisogno di un file di servizio personalizzato, basatelo sui nostri. Sono stati accuratamente messi a punto per buone ragioni! Assicuratevi di personalizzare il vostro se necessario.


## Plugin

<a id="plugins"></a>
I plugin scritti per la v1 non sono automaticamente compatibili con la v2. Molti plugin della v1 non sono nemmeno necessari nella v2. D'altra parte, la v2 è molto più facilmente estensibile e flessibile rispetto alla v1!

Se volete scrivere un plugin per Caddy 2, [imparate come scrivere un modulo Caddy](/docs/extending-caddy).


### Compilare Caddy 2 con i plugin

Caddy 2 può essere scaricato con i plugin nella [pagina di download interattiva](/download). In alternativa, potete [compilare Caddy voi stessi](/docs/build) usando `xcaddy` e scegliere quali plugin includere. `xcaddy` automatizza le istruzioni presenti nel file [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) di Caddy.


## Ottenere aiuto

<a id="getting-help"></a>
Se state riscontrando difficoltà a far funzionare Caddy, consultate prima la documentazione sul nostro sito web. Prendetevi il tempo per provare nuove cose e capire cosa sta succedendo &mdash; la v2 è molto diversa dalla v1 in molti modi (ma è anche molto familiare)!

Se avete ancora bisogno di assistenza, diventate parte della [nostra comunità](https://caddy.community)! Scoprirete che aiutare gli altri è il modo migliore per aiutare anche voi stessi.
