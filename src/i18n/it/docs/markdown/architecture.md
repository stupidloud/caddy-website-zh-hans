---
title: Architettura
---

Architettura
============

Caddy è un binario singolo, autonomo e statico, senza dipendenze esterne, poiché è scritto in Go. Questi valori rappresentano parti importanti della visione del progetto perché semplificano la distribuzione e riducono le noiose operazioni di risoluzione dei problemi negli ambienti di produzione.

Se non c'è collegamento dinamico, allora come può essere esteso? Caddy sfoggia una novel architettura a plugin che espande le sue capacità ben oltre quelle di qualsiasi altro server web, anche di quelli con dipendenze esterne (collegate dinamicamente).

La nostra filosofia di "meno parti mobili" si traduce in definitiva in siti più affidabili, più gestibili e meno costosi&mdash;specialmente su larga scala. Questo documento semi-tecnico descrive come raggiungiamo tale obiettivo attraverso l'ingegneria del software.


## Panoramica

Caddy è composto da un comando, una libreria core e dei moduli.

Il **comando** fornisce l'[interfaccia a riga di comando](/docs/command-line) con cui speriamo abbiate familiarità. È il modo in cui si lancia il processo dal proprio sistema operativo. La quantità di codice e logica qui è piuttosto minima e contiene solo ciò che è necessario per avviare il core nel modo desiderato dall'utente. Evitiamo intenzionalmente l'uso di flag e variabili d'ambiente per la configurazione, se non per quanto riguarda l'avvio della configurazione stessa.


<aside class="tip">
	I moduli possono aggiungere sottocomandi all'interfaccia a riga di comando! Ad esempio, è da lì che proviene il comando [`caddy file-server`](/docs/command-line#caddy-file-server). Questi comandi aggiuntivi possono avere qualsiasi flag o usare qualsiasi variabile d'ambiente desiderino, anche se i comandi core di Caddy ne riducono al minimo l'uso.
</aside>


La **[libreria core](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**, o "core" di Caddy, gestisce principalmente la configurazione. Può eseguire ([`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run)) una nuova configurazione o fermare ([`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop)) una configurazione in esecuzione. Fornisce inoltre varie utility, tipi e valori che i moduli possono utilizzare.

I **Moduli** fanno tutto il resto. Molti moduli sono integrati in Caddy e vengono chiamati *moduli standard*. Questi sono stati determinati come i più utili per la maggior parte degli utenti.


<aside class="tip">
	A volte i termini *modulo*, *plugin* ed *estensione* vengono usati in modo intercambiabile, e di solito va bene così. Tecnicamente, tutti i moduli sono plugin, ma non tutti i plugin sono moduli. I moduli sono specificamente un tipo di plugin che estende la [struttura di configurazione](/docs/json/) di Caddy.
</aside>




## Caddy core

Nel suo nucleo, Caddy si limita a caricare una configurazione iniziale ("config") o, se non ce n'è una, apre un socket per accettare una nuova configurazione in seguito.

Una [configurazione di Caddy](/docs/json/) è un documento JSON, con alcuni campi al suo livello superiore:

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

Il core di Caddy sa come lavorare nativamente con alcuni di questi campi: 

- [`admin`](/docs/json/admin/) in modo da poter configurare l'[API di amministrazione](/docs/api) e gestire il processo
- [`logging`](/docs/json/logging/) in modo da poter [emettere i log](/docs/logging)

Ma altri campi di primo livello (come [`apps`](/docs/json/apps/)) sono opachi per il core di Caddy. In effetti, tutto ciò che Caddy sa fare con i byte in `apps` è deserializzarli in un tipo interfaccia su cui può chiamare due metodi:

1. `Start()`
2. `Stop()`

... e questo è tutto. Chiama `Start()` su ogni app quando viene caricata una configurazione e `Stop()` su ogni app quando una configurazione viene scaricata.

Quando viene avviato un modulo app, viene avviato il ciclo di vita del modulo dell'app.


<aside class="tip">
	Se sei un programmatore che sta creando moduli per Caddy, puoi trovare informazioni analoghe nella nostra guida [Estendere Caddy](/docs/extending-caddy), ma con una maggiore attenzione al codice.
</aside>


## Ciclo di vita del modulo

Esistono due tipi di moduli: *moduli host* e *moduli guest*.

I **Moduli host** (o moduli "padre") sono quelli che caricano altri moduli.

I **Moduli guest** (o moduli "figlio") sono quelli che vengono caricati. Tutti i moduli sono moduli guest &mdash; anche i moduli app.

I moduli vengono caricati, predisposti e validati, utilizzati e infine ripuliti, in questa sequenza:

1. Caricamento
2. Predisposizione (provision) e validazione
3. Utilizzo
4. Pulizia (cleanup)

Caddy avvia il ciclo di vita del modulo quando viene caricata una configurazione, inizializzando per primi tutti i moduli app configurati. Da lì, è una gerarchia a cascata man mano che ogni modulo app gestisce il resto del percorso.

### Fase di caricamento (Load)

Il caricamento di un modulo comporta la deserializzazione dei suoi byte JSON in un valore tipizzato in memoria. È... fondamentalmente tutto qui. Si tratta solo di decodificare il JSON in un valore.

### Fase di predisposizione (Provision)

Questa fase è quella in cui viene svolta la maggior parte del lavoro di configurazione. Tutti i moduli hanno la possibilità di predisporsi dopo essere stati caricati.

Poiché tutte le proprietà derivanti dalla codifica JSON saranno già state decodificate, qui deve avvenire solo l'ulteriore configurazione necessaria. Il compito più comune durante la predisposizione è la configurazione dei moduli guest. In altre parole, la predisposizione di un modulo host comporta anche la predisposizione dei suoi moduli guest, ricorsivamente.

Potete farvi un'idea di questo [esplorando la struttura JSON di Caddy nella nostra documentazione](/docs/json/). Ovunque vediate `{•••}` è il punto in cui possono essere usati i moduli guest; cliccando su uno di essi, potrete continuare l'esplorazione fino a quando non ci saranno più moduli guest.

Altri compiti comuni di predisposizione sono l'impostazione di valori interni che verranno utilizzati durante la vita del modulo o la standardizzazione degli input. Ad esempio, il modulo [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) utilizza la fase di predisposizione per analizzare i valori CIDR dalle stringhe di input ricevute dal JSON. In questo modo, non deve farlo durante ogni richiesta HTTP, risultando più efficiente.

Anche la validazione può avvenire nella fase di predisposizione. Se la configurazione risultante di un modulo non è valida, qui può essere restituito un errore che interrompe l'intero processo di caricamento della configurazione.

### Fase di utilizzo (Use)

Una volta che un modulo guest è stato predisposto e validato, può essere utilizzato dal suo modulo host. Cosa significhi esattamente dipende da ciascun modulo host.

Ogni modulo ha un ID, composto da un namespace e da un nome in quel namespace. Ad esempio, [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) è un gestore HTTP perché si trova nel namespace `http.handlers` e il suo nome è `reverse_proxy`. Tutti i moduli nel namespace `http.handlers` soddisfano la stessa interfaccia, nota al modulo host. Pertanto, l'app `http` sa come caricare e utilizzare questo tipo di moduli.

### Fase di pulizia (Cleanup)

Quando è il momento di fermare una configurazione, tutti i moduli vengono scaricati. Se un modulo ha allocato risorse che dovrebbero essere liberate, ha l'opportunità di farlo nella fase di pulizia.


## Collegamento (Plugging in)

Un modulo &mdash; o qualsiasi plugin di Caddy &mdash; viene "collegato" a Caddy aggiungendo un `import` per il pacchetto del modulo. Importando il pacchetto, [il modulo si registra](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) con il core di Caddy, in modo che all'avvio del processo Caddy conosca ogni modulo per nome. Può persino associare tra valori dei moduli e nomi, e viceversa.


<aside class="tip">
	I plugin possono essere aggiunti senza modificare affatto la base di codice di Caddy. Ci sono istruzioni [nel readme](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins) per farlo!
</aside>


## Gestione della configurazione

Cambiare la configurazione attiva di un server in esecuzione (spesso chiamato "reload") può essere complicato a causa degli alti livelli di concorrenza e delle migliaia di parametri richiesti dai server. Caddy risolve questo problema elegantemente utilizzando un design che offre molti vantaggi:

- Nessuna interruzione dei servizi in esecuzione
- Sono possibili modifiche granulari alla configurazione
- È richiesto un solo lock (in background)
- Tutti i ricaricamenti sono atomici, coerenti, isolati e perlopiù durevoli ("ACID")
- Stato globale minimo

Potete [guardare un video sul design di Caddy 2 qui](https://www.youtube.com/watch?v=EhJO8giOqQs).

Un ricaricamento della configurazione funziona predisponendo i nuovi moduli e, se tutti hanno successo, quelli vecchi vengono ripuliti. Per un breve periodo, due configurazioni sono operative contemporaneamente.

Ogni configurazione è associata a un [contesto](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) che contiene tutto lo stato del modulo, quindi la maggior parte dello stato non esce mai dall'ambito di una configurazione. Questa è un'ottima notizia per la correttezza, le prestazioni e la semplicità!

Tuttavia, a volte è necessario uno stato realmente globale. Ad esempio, il reverse proxy può tenere traccia dello stato di salute dei suoi upstream; poiché esiste un solo upstream globalmente, sarebbe un male se se ne dimenticasse ogni volta che viene apportata una piccola modifica alla configurazione. Fortunatamente, Caddy [fornisce strutture](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool) simili al garbage collector di un runtime di linguaggio per mantenere pulito lo stato globale.

Un approccio ovvio agli aggiornamenti della configurazione online è quello di sincronizzare l'accesso a ogni singolo parametro di configurazione, anche nei percorsi critici (hot paths). Questo è incredibilmente negativo in termini di prestazioni e complessità &mdash; specialmente su larga scala &mdash; quindi Caddy non utilizza questo approccio.

Invece, le configurazioni sono trattate come unità immutabili e atomiche: o l'intera cosa viene sostituita, o non viene cambiato nulla. Gli [endpoint dell'API di amministrazione](/docs/api) &mdash; che permettono modifiche granulari esplorando la struttura &mdash; mutano solo una rappresentazione in memoria della configurazione, dalla quale viene generato e caricato un intero nuovo documento di configurazione. Questo approccio ha enormi vantaggi in termini di semplicità, prestazioni e coerenza. Poiché esiste un solo lock, è facile per Caddy elaborare ricaricamenti rapidi.
