---
title: "HTTPS automatico"
---

# HTTPS automatico

**Caddy è stato il primo server web a utilizzare l'HTTPS automaticamente *e per impostazione predefinita*.**

L'HTTPS automatico predispone i certificati TLS per tutti i vostri siti e li mantiene rinnovati. Inoltre, reindirizza l'HTTP verso l'HTTPS per voi! Caddy utilizza impostazioni predefinite sicure e moderne: non sono richiesti tempi di inattività, configurazioni extra o strumenti separati.

<aside class="tip">
	Caddy ha innovato la tecnologia HTTPS automatica; lo facciamo fin dal primo giorno in cui è stato possibile, nel 2015. La logica di automazione HTTPS di Caddy è la più matura e robusta al mondo.
</aside>

Ecco un video di 28 secondi che ne mostra il funzionamento:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Menu:**

- [Panoramica](#panoramica)
- [Attivazione](#attivazione)
- [Effetti](#effetti)
- [Requisiti del nome host](#requisiti-del-nome-host)
- [HTTPS locale](#https-locale)
- [Test](#test)
- [Sfide ACME](#sfide-acme)
- [TLS on-demand](#tls-on-demand)
- [Errori](#errori)
- [Storage](#storage)
- [Certificati wildcard](#certificati-wildcard)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



## Panoramica

<a id="panoramica"></a>
**Per impostazione predefinita, Caddy serve tutti i siti tramite HTTPS.**

- Caddy serve gli indirizzi IP e gli hostname locali/interni tramite HTTPS utilizzando certificati auto-firmati che vengono automaticamente considerati affidabili a livello locale (se consentito).
	- Esempi: `localhost`, `127.0.0.1`
- Caddy serve i nomi DNS pubblici tramite HTTPS utilizzando certificati di una CA ACME pubblica come [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) o [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com).
	- Esempi: `example.com`, `sub.example.com`, `*.example.com`

Caddy mantiene rinnovati tutti i certificati gestiti e reindirizza automaticamente l'HTTP (porta predefinita `80`) verso l'HTTPS (porta predefinita `443`).

**Per l'HTTPS locale:**

- Caddy potrebbe richiedere una password per installare il suo certificato root univoco nel vostro archivio di fiducia. Ciò accade solo una volta per ogni root; e potete rimuoverlo in qualsiasi momento.
- Qualsiasi client che acceda al sito senza considerare affidabile il certificato root della CA di Caddy visualizzerà errori di sicurezza.

**Per i nomi di dominio pubblici:**

<aside class="tip">
	Questi sono requisiti comuni per qualsiasi sito web di produzione di base, non solo per Caddy. La differenza principale è impostare correttamente i record DNS **prima** di avviare Caddy, in modo che possa predisporre i certificati.
</aside>


- Se i record A/AAAA del vostro dominio puntano al vostro server,
- le porte `80` e `443` sono aperte esternamente,
- Caddy può associarsi a tali porte (*o* tali porte vengono inoltrate a Caddy),
- la vostra [directory dei dati](/docs/conventions#data-directory) è scrivibile e persistente,
- e il vostro nome di dominio appare in qualche punto rilevante della configurazione,

allora i siti verranno serviti automaticamente tramite HTTPS. Non dovrete fare altro. Funziona e basta!

Poiché l'HTTPS utilizza un'infrastruttura pubblica e condivisa, voi in quanto amministratori del server dovreste comprendere il resto delle informazioni in questa pagina per evitare problemi inutili, risolverli quando si verificano e configurare correttamente le distribuzioni avanzate.



## Attivazione

<a id="attivazione"></a>
Caddy attiva implicitamente l'HTTPS automatico quando conosce un nome di dominio (hostname) o un indirizzo IP che sta servendo. Esistono diversi modi per comunicare a Caddy il vostro dominio/IP, a seconda di come eseguite o configurate Caddy:

- Un [indirizzo del sito](/docs/caddyfile/concepts#addresses) nel [Caddyfile](/docs/caddyfile)
- Un [host matcher](/docs/json/apps/http/servers/routes/match/host/) al livello superiore nelle [rotte JSON](/docs/modules/http#servers/routes)
- Flag da riga di comando come [`--domain`](/docs/command-line#caddy-file-server) o [`--from`](/docs/command-line#caddy-reverse-proxy)
- Il caricatore di certificati [automate](/docs/json/apps/tls/certificates/automate/)

Qualsiasi dei seguenti casi impedirà l'attivazione dell'HTTPS automatico, in tutto o in parte:

- Disabilitarlo esplicitamente [via JSON](/docs/json/apps/http/servers/automatic_https/) o [via Caddyfile](/docs/caddyfile/options#auto-https)
- Non fornire alcun hostname o indirizzo IP nella configurazione
- Ascoltare esclusivamente sulla porta HTTP
- Anteporre `http://` all'[indirizzo del sito](/docs/caddyfile/concepts#addresses) nel Caddyfile
- Caricare manualmente i certificati (a meno che non sia impostato [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/))

**Casi speciali:**

- I domini che terminano in `.ts.net` non saranno gestiti da Caddy. Caddy tenterà invece di ottenere automaticamente questi certificati al momento dell'handshake dall'istanza [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) in esecuzione locale. Ciò richiede che l'[HTTPS sia abilitato nel vostro account Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) e il processo Caddy deve essere eseguito come root oppure dovete configurare `tailscaled` per fornire al vostro utente Caddy il [permesso di recuperare i certificati](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).


## Effetti

<a id="effetti"></a>
Quando viene attivato l'HTTPS automatico, avviene quanto segue:

- Vengono ottenuti e rinnovati i certificati per [tutti i nomi host idonei](#requisiti-del-nome-host)
- L'HTTP viene reindirizzato verso l'HTTPS (utilizza la [porta HTTP](/docs/modules/http#http_port) `80`)

L'HTTPS automatico non sovrascrive mai la configurazione esplicita, ma la integra soltanto.

Se avete già un [server](/docs/json/apps/http/servers/) in ascolto sulla porta HTTP, le rotte di reindirizzamento HTTP->HTTPS verranno inserite dopo le vostre rotte con un host matcher, ma prima di una rotta catch-all definita dall'utente.

Potete [personalizzare o disabilitare l'HTTPS automatico](/docs/json/apps/http/servers/automatic_https/) se necessario; ad esempio, potete saltare determinati nomi di dominio o disabilitare i reindirizzamenti (nel Caddyfile, fate questo con le [opzioni globali](/docs/caddyfile/options)).


## Requisiti del nome host

<a id="requisiti-del-nome-host"></a>
Tutti gli hostname (nomi di dominio) sono idonei per i certificati completamente gestiti se:

- non sono vuoti
- consistono solo di caratteri alfanumerici, trattini, punti e wildcard (`*`)
- non iniziano né terminano con un punto ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

Inoltre, gli hostname sono idonei per certificati pubblicamente affidabili se:

- non sono localhost (inclusi i TLD `.localhost`, `.local`, `.internal` e `.home.arpa`)
- non sono un indirizzo IP
- hanno solo una singola wildcard `*` come etichetta più a sinistra


## HTTPS locale

<a id="https-locale"></a>
Caddy utilizza l'HTTPS automaticamente per tutti i siti con un host (dominio, IP o hostname) specificato, inclusi gli host interni e locali. Alcuni host non sono pubblici (es. `127.0.0.1`, `localhost`) o generalmente non sono idonei per certificati pubblicamente affidabili (es. gli indirizzi IP &mdash; è possibile ottenere certificati per essi, ma solo da alcune CA). Questi sono comunque serviti tramite HTTPS a meno che non sia disabilitato.

Per servire i siti non pubblici tramite HTTPS, Caddy genera la propria autorità di certificazione (CA) e la utilizza per firmare i certificati. La catena di fiducia consiste in un certificato root e uno intermedio. I certificati "foglia" (leaf) sono firmati dall'intermedio. Sono memorizzati nella [directory dei dati di Caddy](/docs/conventions#data-directory) in `pki/authorities/local`.

La CA locale di Caddy è alimentata dalle [librerie Smallstep <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/).

L'HTTPS locale non utilizza ACME né esegue alcuna validazione DNS. Funziona solo sulla macchina locale ed è considerato affidabile solo dove è installato il certificato root della CA.

### Root della CA

La chiave privata della root viene generata in modo univoco utilizzando una sorgente pseudocasuale crittograficamente sicura e mantenuta in storage con permessi limitati. Viene caricata in memoria solo per eseguire compiti di firma, dopodiché esce dall'ambito per essere sottoposta a garbage-collection.

Sebbene Caddy possa essere configurato per firmare direttamente con la root (per supportare client non conformi), questa opzione è disabilitata per impostazione predefinita e la chiave root viene utilizzata solo per firmare gli intermedi.

La prima volta che viene usata una chiave root, Caddy tenterà di installarla negli archivi di fiducia locali del sistema. Se non dispone dei permessi per farlo, richiederà una password. Questo comportamento può essere disabilitato con [`skip_install_trust` in un caddyfile](/docs/caddyfile/options#skip-install-trust) o [`"install_trust": false` in una configurazione json](/docs/json/apps/pki/certificate_authorities/install_trust/). Se l'operazione fallisce perché eseguita come un utente non privilegiato, potete eseguire [`caddy trust`](/docs/command-line#caddy-trust) per riprovare l'installazione come utente privilegiato.

<aside class="tip">
	È sicuro considerare affidabile il certificato root di Caddy sulla propria macchina, purché il computer non sia compromesso e la vostra chiave root univoca non venga trapelata.
</aside>

Dopo l'installazione della root CA di Caddy, la vedrete nel vostro archivio di fiducia locale come "Caddy Local Authority" (a meno che non abbiate configurato un nome diverso). Potete disinstallarla in qualsiasi momento se lo desiderate (il comando [`caddy untrust`](/docs/command-line#caddy-untrust) facilita questa operazione).

Note che automaticamente installando il certificato negli archivi di fiducia locali è solo per comodità e non è garantito che funzioni, specialmente se vengono usati container o se Caddy viene eseguito come servizio di sistema non privilegiato. In definitiva, se vi affidate a una PKI interna, è responsabilità dell'amministratore di sistema assicurarsi che la root CA di Caddy sia correttamente aggiunta agli archivi di fiducia necessari (questo esula dagli scopi del server web).


### Intermedi della CA

Verranno generati anche un certificato intermedio e una chiave, che verranno usati per firmare i certificati foglia (dei singoli siti).

A differenza del certificato root, i certificati intermedi hanno una durata molto più breve e verranno rinnovati automaticamente secondo necessità.


## Test

<a id="test"></a>
Per testare o sperimentare con la vostra configurazione di Caddy, assicuratevi di [cambiare l'endpoint ACME](/docs/modules/tls.issuance.acme#ca) con un URL di staging o di sviluppo; in caso contrario, è probabile che colpiate i limiti di frequenza (rate limit), il che può bloccare il vostro accesso all'HTTPS fino a una settimana, a seconda del limite colpito.

Una delle CA predefinite di Caddy è [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), che ha un [endpoint di staging <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) che non è soggetto agli stessi [rate limit <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/):

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

## Sfide ACME

<a id="sfide-acme"></a>
L'ottenimento di un certificato TLS pubblicamente affidabile richiede la validazione da parte di un'autorità terza fidata. Oggigiorno, questo processo di validazione è automatizzato con il [protocollo ACME <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) e può essere eseguito in uno di tre modi ("tipi di sfida"), descritti di seguito.

I primi due tipi di sfida sono abilitati per impostazione predefinita. Se sono abilitate più sfide, Caddy ne sceglie una a caso per evitare la dipendenza accidentale da una particolare sfida. Nel tempo, impara quale tipo di sfida ha più successo e inizierà a preferirlo, ma ripiegherà su altri tipi di sfida disponibili se necessario.


### Sfida HTTP

La sfida HTTP esegue una ricerca DNS autoritativa per il record A/AAAA dell'hostname candidato, quindi richiede una risorsa crittografica temporanea sulla porta `80` tramite HTTP. Se la CA vede la risorsa attesa, viene emesso un certificato.

Questa sfida richiede che la porta `80` sia accessibile esternamente. Se Caddy non può ascoltare sulla porta 80, i pacchetti dalla porta `80` devono essere inoltrati alla [porta HTTP](/docs/json/apps/http/http_port/) di Caddy.

Questa sfida è abilitata per impostazione predefinita e non richiede configurazione esplicita.


### Sfida TLS-ALPN

La sfida TLS-ALPN esegue una ricerca DNS autoritativa per il record A/AAAA dell'hostname candidato, quindi richiede una risorsa crittografica temporanea sulla porta `443` utilizzando un handshake TLS contenente valori ServerName e ALPN speciali. Se la CA vede la risorsa attesa, viene emesso un certificato.

Questa sfida richiede che la porta `443` sia accessibile esternamente. Se Caddy non può ascoltare sulla porta 443, i pacchetti dalla porta `443` devono essere inoltrati alla [porta HTTPS](/docs/json/apps/http/https_port/) di Caddy.

Questa sfida è abilitata per impostazione predefinita e non richiede configurazione esplicita.


### Sfida DNS

La sfida DNS esegue una ricerca DNS autoritativa per i record `TXT` dell'hostname candidato e cerca un record `TXT` speciale con un certo valore. Se la CA vede il valore atteso, viene emesso un certificato.

Questa sfida non richiede alcuna porta aperta e il server che richiede il certificato non deve essere accessibile esternamente. Tuttavia, la sfida DNS richiede configurazione. Caddy deve conoscere le credenziali per accedere al fornitore DNS del vostro dominio in modo da poter impostare (e cancellare) i record `TXT` speciali. Se la sfida DNS è abilitata, le altre sfide sono disabilitate per impostazione predefinita.

Poiché le CA ACME seguono gli standard DNS durante la ricerca dei record `TXT` per la verifica della sfida, potete usare i record CNAME per delegare la risposta alla sfida ad altre zone DNS. Questo può essere usato per delegare il sottodominio `_acme-challenge` a [un'altra zona](/docs/caddyfile/directives/tls#dns_challenge_override_domain). Questo è particolarmente utile se il vostro fornitore DNS non offre un'API o non è supportato da uno dei plugin DNS per Caddy.

Il supporto per i fornitori DNS è uno sforzo della comunità. [Imparate come abilitare la sfida DNS per il vostro fornitore sul nostro wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


## TLS on-demand

<a id="tls-on-demand"></a>
Caddy ha aperto la strada a una nuova tecnologia che chiamiamo **TLS on-demand**, che ottiene dinamicamente un nuovo certificato durante il primo handshake TLS che lo richiede, anziché al caricamento della configurazione. Aspetto cruciale, questo **non** richiede di inserire preventivamente i nomi di dominio nella vostra configurazione.

Molte aziende si affidano a questa caratteristica unica per scalare i propri deployment TLS a costi inferiori e senza grattacapi operativi quando servono decine di migliaia di siti.

Il TLS on-demand è utile se:

- non conoscete tutti i nomi di dominio quando avviate o ricaricate il server,
- i nomi di dominio potrebbero non essere configurati correttamente fin da subito (record DNS non ancora impostati),
- non avete il controllo dei nomi di dominio (es. sono domini dei clienti).

Quando il TLS on-demand è abilitato, non è necessario specificare i nomi di dominio nella configurazione per ottenere i certificati per essi. Invece, quando viene ricevuto un handshake TLS per un nome server (SNI) per il quale Caddy non ha ancora un certificato, l'handshake viene trattenuto mentre Caddy ottiene un certificato da usare per completare l'handshake. Il ritardo è solitamente di soli pochi secondi e solo quell'handshake iniziale è lento. Tutti i futuri handshake sono veloci perché i certificati vengono memorizzati nella cache e riutilizzati, e i rinnovi avvengono in background. Futuri handshake potrebbero innescare la manutenzione per il certificato per mantenerlo rinnovato, ma questa manutenzione avviene in background se il certificato non è ancora scaduto.

### Uso del TLS on-demand

**Il TLS on-demand deve essere sia abilitato che limitato per prevenire abusi.**

L'abilitazione del TLS on-demand avviene nelle [policy di automazione TLS](/docs/json/apps/tls/automation/policies/) se si usa la configurazione JSON, o [nei blocchi del sito con la direttiva `tls`](/docs/caddyfile/directives/tls) se si usa il Caddyfile.

Per prevenire abusi di questa funzione, dovete configurare delle restrizioni. Questo viene fatto nell'[oggetto `automation` della configurazione JSON](/docs/json/apps/tls/automation/on_demand/), o nell'[opzione globale `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) del Caddyfile. Le restrizioni sono "globali" e non sono configurabili per sito o per dominio. La restrizione principale è un endpoint "ask" al quale Caddy invierà una richiesta HTTP per chiedere se ha il permesso di ottenere e gestire un certificato per il dominio nell'handshake. Ciò significa che avrete bisogno di un qualche backend interno che possa, ad esempio, interrogare la tabella degli account del vostro database e vedere se un cliente si è registrato con quel nome di dominio.

Tenete a mente la velocità con cui la vostra CA è in grado di emettere certificati. Se impiega più di qualche secondo, ciò influirà negativamente sull'esperienza utente (solo per il primo client).

A causa della sua natura differita e della configurazione extra richiesta per prevenire abusi, raccomandiamo di abilitare il TLS on-demand solo quando il vostro caso d'uso effettivo è quello sopra descritto.

[Consultate il nostro articolo sul wiki per ulteriori informazioni su come usare efficacemente il TLS on-demand.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

## Errori

<a id="errori"></a>
Caddy fa del suo meglio per continuare se si verificano errori con la gestione dei certificati.

Per impostazione predefinita, la gestione dei certificati viene eseguita in background. Ciò significa che non bloccherà l'avvio né rallenterà i vostri siti. Tuttavia, significa anche che il server sarà in esecuzione prima ancora che tutti i certificati siano disponibili. L'esecuzione in background consente a Caddy di riprovare con un backoff esponenziale su un lungo periodo di tempo.

Ecco cosa succede se si verifica un errore nell'ottenimento o nel rinnovo di un certificato:

1. Caddy riprova una volta dopo una breve pausa, nel caso fosse stato un errore casuale
2. Caddy fa una breve pausa, poi passa al successivo tipo di sfida abilitato
3. Dopo che tutti i tipi di sfida abilitati stati provati, [tenta con l'emittente configurato successivo](#fallback-dell-emittente)
	- Let's Encrypt
	- ZeroSSL
4. Dopo che tutti gli emittenti stati provati, effettua un backoff esponenziale
	- Massimo 1 giorno tra i tentativi
	- Fino a 30 giorni

Durante i tentativi con Let's Encrypt, Caddy passa al loro [ambiente di staging <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) per evitare problemi di rate limit. Questa non è una strategia perfetta, ma in generale è utile.

Le sfide ACME richiedono almeno pochi secondi e il rate limiting interno aiuta a mitigare gli abusi accidentali. Caddy utilizza il rate limiting interno in aggiunta a quello configurato da voi o dalla CA, in modo che possiate consegnare a Caddy un vassoio con un milione di nomi di dominio e lui otterrà gradualmente &mdash; ma il più velocemente possibile &mdash; i certificati per tutti loro. Il rate limit interno di Caddy è attualmente di 10 tentativi per account ACME ogni 10 secondi.

Per evitare perdite di risorse, Caddy interrompe i compiti in corso (incluse le transazioni ACME) quando la configurazione viene cambiata. Sebbene Caddy sia in grado di gestire ricaricamenti di configurazione frequenti, tenete a mente le considerazioni operative come questa e considerate di raggruppare (batching) le modifiche alla configurazione per ridurre i ricaricamenti e dare a Caddy la possibilità di finire effettivamente di ottenere i certificati in background.

### Fallback dell'emittente

Caddy è il primo (e finora l'unico) server a supportare il failover automatico e completamente ridondante verso altre CA nel caso in cui non riesca a ottenere con successo un certificato.

Per impostazione predefinita, Caddy abilita due CA compatibili con ACME: [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) e [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Se Caddy non riesce a ottenere un certificato da Let's Encrypt, proverà con ZeroSSL; se entrambi falliscono, effettuerà un backoff e riproverà più tardi. Nella vostra configurazione, potete personalizzare quali emittenti Caddy deve usare per ottenere i certificati, universalmente o per nomi specifici.


## Storage

<a id="storage"></a>
Caddy memorizzerà i certificati pubblici, le chiavi private e altri asset nella sua [struttura di storage configurata](/docs/json/storage/) (o in quella predefinita, se non configurata &mdash; vedere il link per i dettagli).

**La cosa principale che dovete sapere usando la configurazione predefinita è che la cartella `$HOME` deve essere scrivibile e persistente.** Per aiutarvi nella risoluzione dei problemi, Caddy stampa le sue variabili d'ambiente all'avvio se viene specificato il flag `--environ`.

Tutte le istanze di Caddy configurate per usare lo stesso storage condivideranno automaticamente tali risorse e coordineranno la gestione dei certificati come un cluster.

Prima di tentare qualsiasi transazione ACME, Caddy testerà lo storage configurato per assicurarsi che sia scrivibile e abbia capacità sufficiente. Ciò aiuta a ridurre l'inutile contesa sui lock.


## Certificati wildcard

<a id="certificati-wildcard"></a>
Caddy può ottenere e gestire certificati wildcard quando è configurato per servire un sito con un nome wildcard idoneo. Un nome sito è idoneo per un wildcard se solo la sua etichetta di dominio più a sinistra è un wildcard. Ad esempio, `*.example.com` è idoneo, ma questi non lo sono: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com` e `*.*.example.com` (questa è una restrizione della WebPKI).

Se si usa il Caddyfile, Caddy interpreta i nomi dei siti letteralmente per quanto riguarda i nomi dei soggetti del certificato. In altre parole, un sito definito come `sub.example.com` farà sì che Caddy gestisca un certificato per `sub.example.com`, e un sito definito come `*.example.com` farà sì che Caddy gestisca un certificato wildcard per `*.example.com`. Potete vederlo dimostrato nella nostra pagina [Pattern comuni del Caddyfile](/docs/caddyfile/patterns#wildcard-certificates). Se avete bisogno di un comportamento diverso, la [configurazione JSON](/docs/json/) vi offre un controllo più preciso sui soggetti dei certificati e sui nomi dei siti ("host matcher").

A partire da Caddy 2.10, quando automatizza un certificato wildcard, Caddy userà il certificato wildcard per i singoli sottodomini nella configurazione. Non otterrà certificati per i singoli sottodomini a meno che non sia esplicitamente configurato per farlo (es. con `force_automate`).

I certificati wildcard rappresentano un ampio grado di autorità e dovrebbero essere usati solo quando si hanno così tanti sottodomini che gestire certificati individuali per essi affaticherebbe la PKI o vi farebbe colpire i rate limit imposti dalla CA, o se il compromesso sulla privacy vale il rischio di esporre gran parte della zona DNS in caso di compromissione della chiave. Si noti che i certificati wildcard da soli non offrono la privacy di nascondere sottodomini specifici: sono comunque esposti nei pacchetti TLS ClientHello a meno che non sia abilitato l'Encrypted ClientHello (ECH) (vedi sotto).

**Nota:** [Let's Encrypt richiede <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) la [sfida DNS](#sfida-dns) per ottenere certificati wildcard.


## Encrypted ClientHello (ECH)

<a id="encrypted-clienthello-ech"></a>
Normalmente, gli handshake TLS comportano l'invio del ClientHello, incluso il Server Name Indicator (SNI; il dominio a cui ci si connette), in chiaro. Questo perché contiene i parametri necessari per crittografare la connessione che segue l'handshake. Ciò, ovviamente, espone il nome del dominio, che è la parte più sensibile del ClientHello, a chiunque possa intercettare le connessioni, anche se non si trova nelle immediate vicinanze fisiche. Rivela a quale servizio vi state connettendo quando l'IP di destinazione può servire molti siti diversi, ed è il modo in cui alcuni governi censurano Internet.

Con l'Encrypted ClientHello, il client può proteggere il nome del dominio avvolgendo il vero ClientHello in un ClientHello "esterno" che stabilisce i parametri per decrittografare il ClientHello "interno". Tuttavia, molte parti mobili devono incastrarsi perfettamente affinché ciò funzioni e offra reali benefici in termini di privacy.

Per prima cosa, il client deve sapere quali parametri, o configurazione, usare per crittografare il ClientHello. Queste informazioni includono una chiave pubblica e un dominio "esterno" (il "nome pubblico"), tra le altre cose. Questa configurazione deve essere pubblicata o distribuita in qualche modo in modo affidabile.

Potreste teoricamente scriverla su un pezzo di carta e consegnarla a tutti, ma la maggior parte dei principali browser supporta la ricerca di record DNS di tipo HTTPS contenenti i parametri ECH quando ci si connette a un sito. Di conseguenza, dovrete: (1) generare una configurazione ECH (coppia di chiavi pubblica/privata, tra gli altri parametri) e poi (2) creare un record DNS di tipo HTTPS contenente la configurazione ECH codificata in base64.

Oppure... potresti lasciare che Caddy faccia tutto questo per voi. Caddy è il primo e unico server web in grado di generare, pubblicare e servire automaticamente le configurazioni ECH.

Una volta pubblicato il record HTTPS, i client dovranno eseguire una ricerca DNS per il record HTTPS quando si connettono al vostro sito. Normalmente, le ricerche DNS sono in chiaro, il che compromette la sicurezza degli handshake ECH risultanti, quindi i browser dovranno usare un protocollo DNS sicuro come DNS-over-HTTPS (DoH) o DNS-over-TLS (DoT). A seconda del browser, potrebbe essere necessario abilitarlo manualmente.

Una volta che il client ha scaricato in modo sicuro la configurazione ECH, usa la chiave pubblica incorporata per crittografare il ClientHello e procede alla connessione al vostro sito. Caddy quindi decrittografa il ClientHello interno e procede a servire il vostro sito, senza che il nome del dominio appaia mai in chiaro lungo il cavo.

### Considerazioni sul deployment

L'ECH è una tecnologia complessa. Anche se Caddy automatizza completamente l'ECH, molte cose devono essere considerate per ottenere i massimi benefici in termini di privacy. Dovreste anche essere consapevoli dei vari compromessi. 

#### Pubblicazione

Caddy creerà un record HTTPS per un dominio solo se esiste già un record per quel dominio. Ciò evita di interrompere le ricerche DNS per un sottodominio che potrebbe essere coperto da un wildcard. Assicuratevi che i vostri siti abbiano almeno un record A/AAAA che punti al vostro server. Se usate solo un wildcard per i record DNS, allora il dominio wildcard dovrà apparire anche nella configurazione di Caddy.

Caddy non pubblicherà un record HTTPS per un dominio che ha un record CNAME.

#### ECH GREASE

Se aprite Wireshark e poi vi connettete a un qualsiasi sito (anche uno che non supporta ECH) con una versione moderna di un browser principale come Firefox o Chrome (anche con ECH disabilitato), potreste notare che il suo handshake include l'estensione `encrypted_client_hello`:

![ECH GREASE](/resources/images/ech-grease.png)

Lo scopo è rendere gli handshake ECH reali indistinguibili da quelli in chiaro. Se gli handshake ECH sembrassero diversi da quelli normali, i censori potrebbero semplicemente bloccare gli handshake ECH con un danno collaterale minimo. Ma se bloccassero qualsiasi handshake con una plausibile estensione ECH, essenzialmente spegnerebbero gran parte di Internet (l'obiettivo è aumentare il costo della censura diffusa).

Questo è importante da sapere principalmente durante la risoluzione dei problemi di connessione.

#### Rotazione delle chiavi

Come per le chiavi dei certificati, non è buona norma (e può essere decisamente insicuro) usare la stessa chiave per lungo tempo. Pertanto, le chiavi ECH dovrebbero essere ruotate regolarmente. A differenza dei certificati, le configurazioni ECH non hanno una scadenza rigorosa. Ma i server dovrebbero comunque ruotarle.

La rotazione delle chiavi è però complicata, perché i client devono conoscere le chiavi aggiornate. Se il server sostituisse semplicemente le vecchie chiavi con quelle nuove, tutti gli handshake ECH fallirebbero a meno che i client non venissero immediatamente informati delle nuove chiavi. Ma la semplice pubblicazione delle chiavi aggiornate non è sufficiente. La realtà è che i record DNS hanno dei TTL, i resolver memorizzano le risposte nella cache, ecc. Possono volerci minuti, ore o persino giorni prima che i client interroghino i record HTTPS aggiornati e inizino a usare la nuova configurazione ECH.

Per questo motivo, i server dovrebbero continuare a supportare le vecchie configurazioni ECH per un certo periodo di tempo. Non farlo rischia di esporre i nomi dei server in chiaro *su larga scala*. Caddy ruota le chiavi ogni tanto e supporta le chiavi ruotate per un certo tempo, finché non vengono infine eliminate.

Tuttavia, ciò potrebbe non essere sufficiente. Alcuni client continueranno a non ricevere le chiavi aggiornate per vari motivi e, ogni volta che ciò accade, c'è il rischio di esporre il nome del server. Quindi deve esserci un altro modo per fornire ai client la configurazione aggiornata *in-band* con la connessione. È a questo che serve il *nome esterno* (o *nome pubblico*).

#### Nome pubblico

Il ClientHello "esterno" è un normale ClientHello con due sottili differenze che sono note solo al server di origine:

1. L'estensione SNI è falsa
2. L'estensione ECH è reale

Quell'estensione SNI "esterna" contiene il nome pubblico che protegge i vostri domini reali. Questo nome può essere qualsiasi cosa, ma **il vostro server deve essere autoritativo per il nome pubblico** perché Caddy *otterrà* un certificato per esso.

Se un client tenta di effettuare una connessione ECH ma il server non riesce a decrittografare il ClientHello interno, può effettivamente completare l'handshake usando il ClientHello *esterno* con un certificato per il nome pubblico. Questa connessione sicura viene utilizzata rigorosamente *solo* per inviare al client l'attuale configurazione ECH; ovvero, è una connessione TLS temporanea al solo scopo di completare la connessione TLS iniziale. Non vengono trasmessi dati applicativi: solo la chiave ECH. Una volta che il client ha la chiave aggiornata, può stabilire la connessione TLS come previsto.

In questo modo, il vero nome del server rimane protetto e i client non sincronizzati rimangono in grado di connettersi, elementi entrambi vitali per la sicurezza.

Il nome pubblico può essere uno dei domini del vostro sito, un sottodominio o qualsiasi altro nome di dominio che punti al vostro server. Raccomandiamo di scegliere esattamente un nome generico. Ad esempio, Cloudflare serve milioni di siti dietro `cloudflare-ech.com`. Questo è importante per aumentare la dimensione del vostro set di anonimato.

I nomi pubblici non dovrebbero essere vuoti; ovvero, deve essere configurato un nome pubblico affinché le cose funzionino. Caddy attualmente non lo impone (potrebbe farlo in seguito), ma la specifica ECH richiede che il nome pubblico sia lungo almeno 1 byte. Alcuni software accettano nomi vuoti, altri no. Ciò può portare a comportamenti confusi, come browser che usano l'ECH ma server che lo rifiutano come non valido; o browser che non usano l'ECH (perché non valido) anche se la configurazione è correttamente nel record DNS. È responsabilità del proprietario del sito assicurare la corretta configurazione e pubblicazione dell'ECH per garantire la privacy.


#### Set di anonimato

Per massimizzare i benefici dell'ECH in termini di privacy, sforzatevi di massimizzare la dimensione del vostro *set di anonimato*. In sostanza, questo set è composto da server rivolti ai client che hanno un comportamento identico per gli osservatori. L'idea è che un osservatore non possa facilmente ridurre/dedurre i possibili siti o servizi a cui i client si stanno connettendo.

In pratica, raccomandiamo di avere un solo nome pubblico per tutti i vostri siti (c'è solo 1 nome pubblico per configurazione ECH, quindi questo implica avere solo 1 configurazione ECH attiva in qualsiasi momento). Se gestite Caddy in un cluster, Caddy condivide e coordina automaticamente le configurazioni ECH con altre istanze, occupandosi di questo per voi.

Portato all'estremo, ciò implica che ogni sito su Internet potrebbe o dovrebbe essere dietro un singolo indirizzo IP e un unico nome pubblico...


#### Centralizzazione

... il che ci porta al prossimo argomento: la centralizzazione. Una delle critiche all'ECH è che tende a incentivare la centralizzazione. Lo fa in almeno due modi: (1) spingendo i client a favorire DoH/DoT per le ricerche DNS, il che invia tutte le ricerche DNS attraverso un piccolo manipolo di fornitori, e (2) massimizzando la dimensione del set di anonimato su larga scala.

Quando si usa DoH o DoT, le ricerche DNS passano tutte attraverso il fornitore DoH/DoT. Tra il client e il fornitore, i dati DNS sono crittografati, ma tra il fornitore e il server DNS non lo sono. Il DoH/DoT globale incanala efficacemente tutto l'interessante traffico DNS in chiaro in pochi grandi tubi pronti per l'osservazione... o il guasto.

Allo stesso modo, se massimizzassimo veramente il set di anonimato su larga scala, tutti i siti sarebbero protetti dietro un singolo nome pubblico, come `cloudflare-ech.com`. Questo è positivo per la privacy, ma l'intera Internet sarebbe alla mercé di Cloudflare e di quel singolo nome di dominio. Ora, massimizzare fino a quel punto non è necessario né pratico, ma le implicazioni teorie rimangono valide.

Raccomandiamo che ogni organizzazione o individuo scelga un unico nome per tutti i propri siti e usi quello, e nella maggior parte dei casi ciò dovrebbe offrire una privacy sufficiente. Tuttavia, consultate degli esperti con i vostri modelli di minaccia individuali per il vostro caso specifico.


#### Privacy dei sottodomini

Con l'ECH, è ora teoricamente possibile mantenere segreti/privati i sottodomini dai canali laterali, se implementato correttamente.

La maggior parte dei siti non ne ha bisogno poiché, in linea generale, i sottodomini sono informazioni pubbliche. Sconsigliamo di inserire informazioni sensibili nei nomi di dominio. Detto ciò...

Per evitare la fuga di sottodomini sensibili nei log di Certificate Transparency (CT), usate invece un certificato wildcard. In altre parole, invece di mettere `sub.example.com` nella vostra configurazione, mettete `*.example.com` (consultate [Certificati wildcard](#certificati-wildcard) per informazioni importanti).

Un'altra fonte di fughe è il DNSSEC, che la maggior parte dei server DNS autoritativi usa per impostazione predefinita. Attraverso una pratica chiamata "zone walking", è possibile l'enumerazione dei sottodomini guardando i record NSEC, usati per fornire la negazione dell'esistenza autenticata. Questi puntano al successivo sottodominio disponibile in ordine alfabetico, formando una lista concatenata di tutti i record. Assicuratevi che il vostro dominio utilizzi almeno NSEC3 o, idealmente, un record CNAME wildcard per mitigare questo problema.

Quindi, abilitate l'ECH in Caddy. Un certificato wildcard combinato con l'ECH e un record CNAME wildcard dovrebbe nascondere correttamente i sottodomini, a condizione che ogni client che tenta di connettersi utilizzi l'ECH e abbia un'implementazione solida (siete comunque alla mercé dei client per preservare la privacy).


### Abilitare l'ECH

Poiché il funzionamento dell'ECH richiede la pubblicazione delle configurazioni nei record DNS, avrete bisogno di una build di Caddy con un [modulo caddy-dns](https://github.com/caddy-dns) integrato per il vostro fornitore DNS.

Quindi, con un Caddyfile, specificate la configurazione del vostro fornitore DNS nelle opzioni globali, così come il nome pubblico ECH che volete usare:

```caddy
{
	dns <configurazione fornitore...>
	ech example.com
}
```

Ricordate:

- Il modulo del fornitore DNS deve essere presente e dovete avere la configurazione corretta per il vostro fornitore/account.
- Il nome pubblico ECH dovrebbe puntare al vostro server. Caddy otterrà un certificato per esso. Non deve necessariamente essere uno dei domini del vostro sito.

If usate il JSON, aggiungete queste proprietà all'app `tls`:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<nome fornitore>",
	// configurazione fornitore
}
```

Queste configurazioni abiliteranno l'ECH e pubblicheranno le configurazioni ECH per tutti i vostri siti. La configurazione JSON offre maggiore flessibilità se avete bisogno di personalizzare il comportamento o avete un'impostazione avanzata.

### Verificare l'ECH

Non ci sono ancora molti strumenti relativi all'ECH, quindi al momento della scrittura, il modo migliore e più universale per verificare che funzioni è usare Wireshark e cercare il vostro nome pubblico nel campo ServerName.

Per prima cosa, avviate il server e verificate che i log menzionino qualcosa come "published ECH configuration list" per i vostri domini (se ricevete errori con la pubblicazione, assicuratevi che il vostro modulo del fornitore DNS supporti [libdns 1.0](https://github.com/libdns/libdns) e aprite una issue nel repository del vostro fornitore se riscontrate problemi). Caddy dovrebbe anche ottenere un certificato per il nome pubblico.

Successivamente, assicuratevi che il vostro browser abbia l'ECH abilitato; ciò potrebbe richiedere l'abilitazione di DoH/DoT. È anche una buona idea svuotare la cache DNS del browser (o del sistema), per assicurarsi che rilevi i record HTTPS appena pubblicati. Raccomandiamo anche di chiudere il browser o almeno di aprire una nuova scheda privata per assicurarsi che non riutilizzi connessioni esistenti.

Quindi, aprite Wireshark e iniziate l'ascolto sull'interfaccia di rete appropriata. Mentre Wireshark raccoglie i pacchetti, caricate il vostro sito nel browser. Potete quindi mettere in pausa Wireshark. Trovate il vostro TLS ClientHello e dovreste vedere il *nome pubblico* nel campo ServerName, anziché il nome del dominio effettivo a cui vi siete connessi.

Ricordate: potreste vedere comunque un'estensione `encrypted_client_hello` anche se l'ECH non viene usato. L'indicatore chiave è il valore SNI. Non dovreste mai vedere il vero nome del sito in chiaro con Wireshark se l'ECH funziona correttamente.

Se riscontrate problemi di deployment con l'ECH, chiedete prima nel nostro [forum](https://caddy.community). Se si tratta di un bug, potete [aprire una issue](https://github.com/caddyserver/caddy/issues) su GitHub.


### ECH nello storage

Le configurazioni ECH sono memorizzate nella [directory dei dati](/docs/conventions#data-directory) nel modulo di storage configurato (quello predefinito è il file system) sotto la cartella `ech/configs`.

La cartella successiva è un ID della configurazione ECH; questi ID sono generati casualmente e sono relativamente poco importanti. La casualità è raccomandata dalle specifiche per aiutare a mitigare il fingerprinting/tracciamento.

Un file di metadati "sidecar" aiuta Caddy a tenere traccia di quando sono avvenute le ultime pubblicazioni. Questo evita di martellare il vostro fornitore DNS a ogni ricaricamento della configurazione. Se dovete resettare questo stato, potete eliminare in sicurezza il file dei metadati. Tuttavia, ciò potrebbe resettare anche il momento in cui la chiave verrà ruotata. Potete anche entrare nel file e cancellare solo le informazioni relative alla pubblicazione.
