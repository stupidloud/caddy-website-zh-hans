---
title: log (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Corregge > nei blocchi di codice
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Salta se termina con >
			if (item.textContent.trim().endsWith('>')) return;
			// Sostituisce > con <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# log

Abilita e configura il logging delle richieste HTTP (noto anche come log degli accessi).

<aside class="tip">

Per configurare i log di runtime di Caddy, consultate invece l'[opzione globale `log`](/docs/caddyfile/options#log).

</aside>


La direttiva `log` si applica agli hostname del blocco sito in cui appare, a meno che non venga sovrascritta con la sottodirettiva `hostnames`.

Una volta configurata, per impostazione predefinita tutte le richieste al sito verranno loggate. Per saltare condizionalmente alcune richieste dal logging, usate la [direttiva `log_skip`](log_skip).

Per aggiungere campi personalizzati alle voci di log, usate la [direttiva `log_append`](log_append).


- [Sintassi](#syntax)
- [Moduli di output](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [Moduli di formato](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [Esempi](#examples)

Per impostazione predefinita, gli header con informazioni potenzialmente sensibili (`Cookie`, `Set-Cookie`, `Authorization` e `Proxy-Authorization`) verranno loggati come `REDACTED` nei log degli accessi. Questo comportamento può essere disabilitato con l'opzione globale del server [`log_credentials`](/docs/caddyfile/options#log-credentials).


## Sintassi

<a id="syntax"></a>
```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> è una sovrascrittura opzionale del nome del logger per questo sito.

  Per impostazione predefinita, viene generato automaticamente un nome del logger, es. `log0`, `log1`, e così via a seconda dell'ordine dei siti nel Caddyfile. Questo è utile solo se desiderate fare riferimento in modo affidabile all'output di questo logger da un altro logger definito nelle opzioni globali. Consultate [un esempio](#multiple-outputs) di seguito.

- **hostnames** <span id="hostnames"/> è una sovrascrittura opzionale degli hostname a cui si applica questo logger.

  Per impostazione predefinita, il logger si applica agli hostname del blocco sito in cui appare, ovvero gli indirizzi del sito. Questo è utile se desiderate definire diversi logger per sottodominio in un [blocco sito wildcard](/docs/caddyfile/patterns#wildcard-certificates). Consultate [un esempio](#wildcard-logs) di seguito.

- **no_hostname** <span id="no_hostname"/> impedisce al logger di essere associato a uno qualsiasi degli hostname del blocco sito. Per impostazione predefinita, il logger è associato all'[indirizzo del sito](/docs/caddyfile/concepts#indirizzi) in cui appare la direttiva `log`.

  Questo è utile quando si desidera loggare le richieste in file diversi in base a qualche condizione, come il percorso della richiesta o il metodo, usando la [direttiva `log_name`](/docs/caddyfile/directives/log_name).

- **output** <span id="output"/> configura dove scrivere i log. Consultate i [moduli `output`](#output-modules) di seguito.

  Predefinito: `stderr`.

- **format** <span id="format"/> descrive come codificare, o formattare, i log. Consultate i [moduli `format`](#format-modules) di seguito.

  Predefinito: `console` se viene rilevato che `stderr` è un terminale, `json` altrimenti.

- **level** <span id="level"/> è il livello minimo della voce da loggare. Predefinito: `INFO`.

  Si noti che i log degli accessi attualmente emettono solo log di livello `INFO` ed `ERROR`.

- **sampling** <span id="sampling"/> configura il campionamento dei log per ridurne il volume. Se viene specificato sampling, allora viene abilitato, con i valori predefiniti riportati di seguito. L'omissione disabilita il campionamento.

  - **interval** è la [finestra di durata](/docs/conventions#durate) sulla quale condurre il campionamento. Predefinito: `1s` (disabilitato).

  - **first** è il numero di log da conservare per un dato livello e messaggio per ogni intervallo. Predefinito: `100`.

  - **thereafter** è il numero di log da saltare in ogni intervallo dopo i primi log conservati. Predefinito: `100`.

  Ad esempio, con `interval 1s`, `first 5`, e `thereafter 10`, in ogni intervallo di 1 secondo verranno conservate le prime 5 voci di log, dopodiché verrà lasciata passare ogni 10ª voce di log con lo stesso livello e messaggio all'interno di quel secondo.


### Moduli di output

<a id="output-modules"></a>
La sottodirettiva **output** permette di personalizzare dove vengono scritti i log.

#### stderr

Standard error (console, è l'impostazione predefinita).
<a id="stderr"></a>

```caddy-d
output stderr
```

#### stdout

Standard output (console).
<a id="stdout"></a>

```caddy-d
output stdout
```

#### discard

Nessun output.
<a id="discard"></a>

```caddy-d
output discard
```

#### file

Un file. Per impostazione predefinita, i file di log vengono ruotati ("rolled") in base alla dimensione per prevenire l'esaurimento dello spazio su disco.
<a id="file"></a>

La rotazione dei log è fornita da [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack)

<aside class="tip">

**Una nota sul ricaricamento delle opzioni dei file di log:** È richiesto un riavvio del server per applicare le modifiche alla configurazione a un dato file di output.
Le modifiche non verranno applicate al momento del ricaricamento (reload) del server, a meno che non si aggiunga un nuovo nome di file di log.

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** è il percorso del file di log.

  Quando ruotati, i file vengono rinominati utilizzando il template `<nome>-<timestamp>-<motivo>.log`. Il timestamp è formattato secondo l'opzione [`backup_time_format`](#backup_time_format). Il motivo è o `size` o `time`, a seconda di cosa ha innescato la rotazione. Se il file viene compresso, `.gz` viene aggiunto al nome del file.

   Ad esempio, se il nome del file è `access.log`, un file ruotato potrebbe chiamarsi `access-2026-01-30T22-15-42.123-size.log` se è stato ruotato a causa della dimensione, o `access-2025-01-30T00-00-00.000-time.log` se è stato ruotato a causa del tempo.

- **mode** <span id="mode"/> è la modalità file Unix/permessi da usare per il file di log. La modalità consiste in un numero da 1 a 4 cifre ottali (lo stesso formato numerico accettato dal comando Unix [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod), eccetto che una modalità tutta a zero viene interpretata come la modalità predefinita `600`).

  Ad esempio: `0600` imposterebbe la modalità a `rw-,---,---` (accesso in lettura/scrittura al proprietario del file di log, e nessun accesso a chiunque altro); `0640` imposterebbe la modalità a `rw-,r--,---` (accesso in lettura/scrittura al proprietario del file, solo accesso in lettura al gruppo); `644` imposta la modalità a `rw-,r--,r--` fornendo accesso in lettura/scrittura al proprietario del file di log, ma solo accesso in lettura al proprietario del gruppo e agli altri utenti.

- **roll_disabled** <span id="roll_disabled"/> disabilita la rotazione dei log. Questo può portare all'esaurimento dello spazio su disco, quindi usatelo solo se i vostri file di log sono gestiti in altro modo.

- **roll_size** <span id="roll_size"/> è la dimensione alla quale ruotare il file di log. L'attuale implementazione supporta la risoluzione in megabyte; i valori frazionari vengono arrotondati per eccesso al megabyte intero successivo. Ad esempio, `1.1MiB` viene arrotondato a `2MiB`.

  Questa opzione è sempre abilitata. Se una scrittura nei log causa il superamento della dimensione specificata da parte del file, il log verrà immediatamente ruotato. Il nome del file di backup includerà `size` come motivo.

  Predefinito: `100MiB`

- **roll_interval** <span id="roll_interval"/> è la durata massima tra le rotazioni dei log. Il valore è una [stringa di durata](/docs/conventions#durate) dopo la quale ruotare il file di log.

  Quando abilitata, il file viene ruotato alla successiva scrittura nei log dopo che è trascorsa questa durata dall'ultima rotazione. Il nome del file di backup includerà `time` come motivo.

  Si noti che se impostato a `24h`, non ruota necessariamente a mezzanotte, ma piuttosto allo scoccare delle 24 ore dall'ultima rotazione. Se la rotazione avviene a causa della dimensione, allora il tempo della rotazione successiva verrebbe sfalsato rispetto alla rotazione precedente. Potete usare le opzioni `roll_at` o `roll_minutes` per ruotare a orari specifici invece.

  Predefinito: disabilitato

- **roll_minutes** <span id="roll_minutes"/> è un elenco di valori di minuti (0-59) ai quali ruotare il file di log. Ad esempio, `10 40` ruoterebbe il file di log ogni 30 minuti ai minuti `xx:10` e `xx:40` di ogni ora. Le rotazioni sono allineate al minuto dell'orologio (secondo 0).

  L'abilitazione di questa opzione genera un timer goroutine che innesca una rotazione del log ai valori dei minuti specificati (ovvero introduce una piccola quantità di elaborazione in background). Questo opera in aggiunta a `roll_interval` e `roll_size`. Il nome del file di backup includerà `time` come motivo.

  Predefinito: disabilitato

- **roll_at** <span id="roll_at"/> è un elenco di valori orari (in formato 24 ore) ai quali ruotare il file di log. Ad esempio, `00:00 12:00` ruoterebbe il file di log due volte al giorno, a mezzanotte e a mezzogiorno. Le rotazioni sono allineate al minuto dell'orologio (secondo 0).

  L'abilitazione di questa opzione genera un timer goroutine che innesca una rotazione del log agli orari specificati (ovvero introduce una piccola quantità di elaborazione in background). Questo opera in aggiunta a `roll_interval` e `roll_size`. Il nome del file di backup includerà `time` come motivo.

  Predefinito: disabilitato

- **roll_uncompressed** <span id="roll_uncompressed"/> disattiva la compressione gzip dei log.

  Predefinito: la compressione `gzip` è abilitata.

- **roll_local_time** <span id="roll_local_time"/> imposta la rotazione affinché usi i timestamp locali nei nomi dei file. 
  Predefinito: usa l'ora UTC.

- **roll_keep** <span id="roll_keep"/> è il numero di file di log da conservare prima di eliminare quelli più vecchi. Si attiva quando viene creato un nuovo file di log.

  Predefinito: `10`

- **roll_keep_for** <span id="roll_keep_for"/> è quanto a lungo conservare i file ruotati come una [stringa di durata](/docs/conventions#durate). Si attiva quando viene creato un nuovo file di log.
  L'attuale implementazione supporta la risoluzione in giorni; i valori frazionari vengono arrotondati per eccesso al giorno intero successivo. Ad esempio, `36h` (1.5 giorni) viene arrotondato a `48h` (2 giorni).
  
  Predefinito: `2160h` (90 giorni)

- **backup_time_format** <span id="backup_time_format"/> è il formato dell'ora da usare nei nomi dei file di backup. Deve essere una stringa di layout dell'ora valida; consultate la [documentazione di Go](https://pkg.go.dev/time#pkg-constants) per i dettagli completi.

  Predefinito: `2006-01-02T15-04-05`


#### net

Un socket di rete. Se il socket cade, scaricherà i log su stderr mentre tenta di riconnettersi.
<a id="net"></a>

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** è l'[indirizzo](/docs/conventions#indirizzi-di-rete) a cui scrivere i log.

- **dial_timeout** <span id="dial_timeout"/> è quanto tempo attendere per una connessione riuscita al socket del log. Le emissioni di log potrebbero essere bloccate per un massimo di questo tempo se il socket cade.

- **soft_start** <span id="soft_start"/> ignorerà gli errori durante la connessione al socket, permettendovi di caricare la vostra configurazione anche se il servizio di log remoto è giù. I log verranno invece emessi su stderr.


### Moduli di formato

<a id="format-modules"></a>
La sottodirettiva **format** permette di personalizzare il modo in cui i log vengono codificati (formattati). Appare all'interno di un blocco `log`.

<aside class="tip">

**Una nota sul Common Log Format (CLF):** Il CLF si scontra con i moderni log strutturati. Per trasformare i vostri log degli accessi nel deprecato Common Log Format, usate il [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder).

</aside>


In aggiunta alla sintassi per ogni singolo encoder, queste proprietà comuni possono essere impostate sulla maggior parte degli encoder:

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> La chiave per il campo del messaggio della voce di log. Predefinito: `msg`

- **level_key** <span id="level_key"/> La chiave per il campo del livello della voce di log. Predefinito: `level`

- **time_key** <span id="time_key"/> La chiave per il campo dell'ora della voce di log. Predefinito: `ts`
- **name_key** <span id="name_key"/> La chiave per il campo del nome della voce di log. Predefinito: `name`

- **caller_key** <span id="caller_key"/> La chiave per il campo del chiamante della voce di log.

- **stacktrace_key** <span id="stacktrace_key"/> La chiave per il campo dello stacktrace della voce di log.

- **line_ending** <span id="line_ending"/> I finali di riga da usare.

- **time_format** <span id="time_format"/> Il formato per i timestamp.
  Predefinito: `wall_milli` se il formato è di default a `console`, `unix_seconds_float` altrimenti.
  
  Può essere uno di:
  - `unix_seconds_float` Numero in virgola mobile di secondi dall'epoca Unix.
  - `unix_milli_float` Numero in virgola mobile di millisecondi dall'epoca Unix.
  - `unix_nano` Numero intero di nanosecondi dall'epoca Unix.
  - `iso8601` Esempio: `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` Esempio: `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` Esempio: `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` Esempio: `2006/01/02 15:04:05`
  - `wall_milli` Esempio: `2006/01/02 15:04:05.000`
  - `wall_nano` Esempio: `2006/01/02 15:04:05.000000000`
  - `common_log` Esempio: `02/Jan/2006:15:04:05 -0700`
  - Oppure, qualsiasi stringa di layout dell'ora compatibile; consultate la [documentazione di Go](https://pkg.go.dev/time#pkg-constants) per i dettagli completi.
  
  Si noti che le parti della stringa di formato sono costanti speciali per il layout; quindi `2006` è l'anno, `01` è il mese, `Jan` è il mese come stringa, `02` è il giorno. Non usate i numeri effettivi della data corrente nella stringa di formato.

- **time_local** <span id="time_local"/> Logga con l'ora locale del sistema invece che con l'ora UTC predefinita.

- **duration_format** <span id="duration_format"/> Il formato per le durate.

  Predefinito: `seconds`.
  
  Può essere uno di:
  - `s`, `second` o `seconds` Numero in virgola mobile di secondi trascorsi.
  - `ms`, `milli` o `millis` Numero in virgola mobile di millisecondi trascorsi.
  - `ns`, `nano` o `nanos` Numero intero di nanosecondi trascorsi.
  - `string` Utilizzando il formato stringa integrato di Go, ad esempio `1m32.05s` o `6.31ms`.

- **level_format** <span id="level_format"/> Il formato per i livelli.

  Predefinito: `color` se il formato è di default a `console`, `lower` altrimenti.
  
  Può essere uno di:
  - `lower` Minuscolo.
  - `upper` Maiuscolo.
  - `color` Maiuscolo, con colori ANSI.
  

#### console

L'encoder console formatta la voce di log per la leggibilità umana pur preservando una certa struttura.
<a id="console"></a>

```caddy-d
format console
```

#### json

Formatta ogni voce di log come un oggetto JSON.
<a id="json"></a>

```caddy-d
format json
```


#### filter

Permette il filtraggio per campo.
<a id="filter"></a>

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

I campi nidificati possono essere referenziati rappresentando un livello di nidificazione con `>`. In altri termini, per un oggetto come `{"a":{"b":0}}`, il campo interno può essere referenziato come `a>b`.

I seguenti campi sono fondamentali per il log e non possono essere filtrati perché aggiunti dalla libreria di logging sottostante come casi speciali: `ts`, `level`, `logger`, e `msg`.

Specificare `wrap` è opzionale; se omesso, viene scelto un valore predefinito a seconda che l'attuale modulo di output sia [`stderr`](#stderr) o [`stdout`](#stdout), ed è un terminale interattivo, nel qual caso viene scelto [`console`](#console), altrimenti viene scelto [`json`](#json).

Come scorciatoia, il blocco `fields` può essere omesso e i filtri possono essere specificati direttamente all'interno del blocco `filter`.


Questi sono i filtri disponibili:

##### delete
<a id="delete"></a>

Contrassegna un campo affinché venga saltato durante la codifica.

```caddy-d
<field> delete
```


##### rename
<a id="rename"></a>

Rinomina la chiave di un campo di log.

```caddy-d
<field> rename <key>
```


##### replace
<a id="replace"></a>

Contrassegna un campo affinché venga sostituito con la stringa fornita al momento della codifica.

```caddy-d
<field> replace <replacement>
```


##### ip_mask
<a id="ip-mask"></a>

Maschera gli indirizzi IP nel campo usando una maschera CIDR, ovvero il numero di bit dell'IP da mantenere, partendo dal lato sinistro. Se il campo è un array di stringhe (es. header HTTP), ogni valore nell'array viene mascherato. Il valore può essere una stringa di indirizzi IP separati da virgole.

Esiste una configurazione separata per gli indirizzi IPv4 e IPv6, poiché hanno un numero totale di bit differente.

Più comunemente, i campi da filtrare sarebbero:
- `request>remote_ip` per il client che si connette direttamente
- `request>client_ip` per l'IP reale analizzato quando [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) è configurato
- `request>headers>X-Forwarded-For` se dietro un reverse proxy

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query
<a id="query"></a>

Contrassegna un campo affinché vengano eseguite una o più azioni per manipolare la parte della query di un campo URL. Più comunemente, il campo da filtrare sarebbe `request>uri`.

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

Le azioni disponibili sono:

- **delete** rimuove la chiave fornita dalla query.

- **replace** sostituisce il valore della chiave di query fornita con **replacement**. Utile per inserire un placeholder di oscuramento; vedrete che la chiave di query era nell'URL, ma il valore è nascosto.

- **hash** sostituisce il valore della chiave di query fornita con i primi 4 byte dell'hash SHA-256 del valore, in esadecimale minuscolo. Utile per oscurare il valore se è sensibile, pur potendo notare se ogni richiesta aveva un valore diverso.


##### cookie
<a id="cookie"></a>

Contrassegna un campo affinché vengano eseguite una o più azioni per manipolare il valore di un header HTTP `Cookie`. Più comunemente, il campo da filtrare sarebbe `request>headers>Cookie`.

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

Le azioni disponibili sono:

- **delete** rimuove il cookie fornito per nome dall'header.

- **replace** sostituisce il valore del cookie fornito con **replacement**. Utile per inserire un placeholder di oscuramento; vedrete che il cookie era nell'header, ma il valore è nascosto.

- **hash** sostituisce il valore del cookie fornito con i primi 4 byte dell'hash SHA-256 del valore, in esadecimale minuscolo. Utile per oscurare il valore se è sensibile, pur potendo notare se ogni richiesta aveva un valore diverso.

Se vengono definite molte azioni per lo stesso nome di cookie, verrà applicata solo la prima azione.


##### regexp
<a id="regexp"></a>

Contrassegna un campo affinché venga applicata una sostituzione tramite espressione regolare al momento della codifica. Se il campo è un array di stringhe (es. header HTTP), ogni valore nell'array subisce le sostituzioni.

```caddy-d
<field> regexp <pattern> <replacement>
```

Il linguaggio delle espressioni regolari utilizzato è RE2, incluso in Go. Consultate il [riferimento alla sintassi RE2](https://github.com/google/re2/wiki/Syntax) e la [panoramica della sintassi regexp di Go](https://pkg.go.dev/regexp/syntax).

Nella stringa di sostituzione, i gruppi di cattura possono essere referenziati con `${group}` dove `group` è il nome o il numero del gruppo di cattura nell'espressione. Il gruppo di cattura `0` è l'intera corrispondenza regexp, `1` è il primo gruppo di cattura, `2` il secondo, e così via.


##### hash
<a id="hash"></a>

Contrassegna un campo affinché venga sostituito con i primi 4 byte (8 caratteri esadecimali) dell'hash SHA-256 del valore al momento della codifica. Se il campo è un array di stringhe (es. header HTTP), ogni valore nell'array viene hashato.

Utile per oscurare il valore se è sensibile, pur potendo notare se ogni richiesta aveva un valore diverso.

```caddy-d
<field> hash
```

#### append
<a id="append"></a>

Aggiunge campo/i a tutte le voci di log.

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

È molto utile per aggiungere informazioni sull'istanza di Caddy che sta producendo le voci di log, possibilmente tramite una variabile d'ambiente. I valori dei campi possono essere placeholder globali (es. `{env.*}`), ma *non* placeholder per singola richiesta a causa del fatto che i log vengono scritti al di fuori del contesto della richiesta HTTP.

Specificare `wrap` è opzionale; se omesso, viene scelto un valore predefinito a seconda che l'attuale modulo di output sia [`stderr`](#stderr) o [`stdout`](#stdout), ed è un terminale interattivo, nel qual caso viene scelto [`console`](#console), altrimenti viene scelto [`json`](#json).

Il blocco `fields` può essere omesso e i campi possono essere specificati direttamente all'interno del blocco `append`.



## Esempi

<a id="examples"></a>
Abilita il logging degli accessi verso il logger predefinito.

In altre parole, per impostazione predefinita questo logga su `stderr`, ma questo può essere cambiato riconfigurando il logger `default` con l'[opzione globale `log`](/docs/caddyfile/options#log):

```caddy
example.com {
	log
}
```


Scrive i log in un file (con la rotazione dei log, che è abilitata per impostazione predefinita):

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


Personalizza la rotazione dei log, ruotando giornalmente a mezzanotte o quando il file di log raggiunge 1 GB (a seconda di quale evento si verifichi per primo), e conservando 5 file ruotati o 30 giorni di log:

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


Elimina l'header di richiesta `User-Agent` dai log:

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


Oscura molteplici cookie sensibili. (Si noti che alcuni header sensibili vengono loggati con valori vuoti per impostazione predefinita; consultate l'[opzione globale `log_credentials`](/docs/caddyfile/options#log-credentials) per abilitare il logging dei valori dell'header `Cookie`):

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


Maschera l'indirizzo remoto dalla richiesta, mantenendo i primi 16 bit (ovvero 255.255.0.0) per gli indirizzi IPv4, e i primi 32 bit per gli indirizzi IPv6.

Si noti che a partire da Caddy v2.7, vengono loggati sia `remote_ip` che `client_ip`, dove `client_ip` è l'"IP reale" quando [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) è configurato:

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


Per aggiungere un ID server da una variabile d'ambiente a tutte le voci di log, e concatenarlo con un `filter` per eliminare un header:

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<a id="wildcard-logs"></a> Per scrivere file di log separati per ogni sottodominio in un [blocco sito wildcard](/docs/caddyfile/patterns#wildcard-certificates), sovrascrivendo `hostnames` per ogni logger. Questo utilizza uno [snippet](/docs/caddyfile/concepts#snippet) per evitare ripetizioni:

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<a id="multiple-outputs"></a> Per scrivere i log degli accessi per un particolare sottodominio in due file diversi, con formati diversi (uno con il [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) e l'altro con [`json`](#json)). 

Questo funziona sovrascrivendo il nome del logger come `foo` nel blocco sito, e poi includendo i log degli accessi prodotti da quel logger nei due logger nelle opzioni globali con `include http.log.access.foo`:

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<a id="sampling-example"></a> Per ridurre il volume dei log con il campionamento (sampling), ad esempio per conservare le prime 5 richieste al secondo, e poi 1 richiesta ogni 10 successivamente:

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
