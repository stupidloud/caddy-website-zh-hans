---
title: reverse_proxy (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Corregge i matcher di risposta per renderizzarli con il colore corretto,
	// e collega alla sezione dei matcher di risposta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher di risposta">${text}</a>`;
		}
	});

	// Corregge il placeholder del matcher
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher di risposta">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher di risposta">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher di risposta">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

Effettua il proxy delle richieste a uno o più backend con opzioni configurabili per il trasporto, il bilanciamento del carico, i controlli sanitari (health checks), la manipolazione della richiesta e il buffering.

- [Sintassi](#sintassi)
- [Upstream](#upstreams)
  - [Indirizzi upstream](#upstream-addresses)
  - [Upstream dinamici](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Bilanciamento del carico](#load-balancing)
  - [Controlli sanitari attivi](#active-health-checks)
  - [Controlli sanitari passivi](#passive-health-checks)
  - [Eventi](#eventi)
- [Streaming](#streaming)
- [Header](#headers)
- [Riscritture](#rewrites)
- [Trasporti](#transports)
  - [Il trasporto `http`](#the-http-transport)
  - [Il trasporto `fastcgi`](#the-fastcgi-transport)
- [Intercettare le risposte](#intercepting-responses)
- [Esempi](#examples)



## Sintassi

<a id="sintassi"></a>
```caddy-d
reverse_proxy [<matcher>] [<upstream...>] {
	# backend
	to      <upstream...>
	dynamic &lt;modulo&gt; ...

	# bilanciamento del carico
	lb_policy       &lt;nome&gt; [<opzioni...>]
	lb_retries      <tentativi>
	lb_try_duration <durata>
	lb_try_interval <intervallo>
	lb_retry_match  <matcher-richiesta>

	# controlli sanitari attivi
	health_uri          <uri>
	health_upstream     <ip:porta>
	health_port         <porta>
	health_interval     <intervallo>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <durata>
	health_method       <metodo>
	health_status       <stato>
	health_request_body <corpo>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<campo> [<valori...>]
	}

	# controlli sanitari passivi
	fail_duration     <durata>
	max_fails         <num>
	unhealthy_status  <stato>
	unhealthy_latency <durata>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <durata>
	request_buffers    <dimensione>
	response_buffers   <dimensione>
	stream_timeout     <durata>
	stream_close_delay <durata>

	# manipolazione richiesta/header
	trusted_proxies [private_ranges] <intervalli...>
	header_up   [+|-]<campo> [<valore|regexp> [<sostituzione>]]
	header_down [+|-]<campo> [<valore|regexp> [<sostituzione>]]
	method <metodo>
	rewrite <a_cosa>

	# round trip
	transport &lt;nome&gt; {
		...
	}

	# opzionalmente intercetta le risposte dall'upstream
	@nome {
		status <codice...>
		header <campo> [&lt;valore&gt;]
	}
	replace_status [<matcher>] <codice_stato>
	handle_response [<matcher>] {
		<direttive...>

		# direttive speciali disponibili solo in handle_response
		copy_response [<matcher>] [<stato>] {
			status <stato>
		}
		copy_response_headers [<matcher>] {
			include <campi...>
			exclude <campi...>
		}
	}
}
```



## Upstream

<a id="upstreams"></a>
- **&lt;upstream...&gt;** è un elenco di upstream (backend) verso cui effettuare il proxy.
- **to** <span id="to"/> è un modo alternativo per specificare l'elenco degli upstream, uno (o più) per riga.
- **dynamic** <span id="dynamic"/> configura un modulo di *upstream dinamici*. Ciò consente di ottenere l'elenco degli upstream dinamicamente per ogni richiesta. Consultate [upstream dinamici](#dynamic-upstreams) di seguito per una descrizione dei moduli standard. Gli upstream dinamici vengono recuperati ad ogni iterazione del ciclo del proxy (ovvero, potenzialmente più volte per richiesta se i tentativi di bilanciamento del carico sono abilitati) e avranno la precedenza sugli upstream statici. In caso di errore, il proxy ripiegherà sull'uso di eventuali upstream configurati staticamente.


### Indirizzi upstream

<a id="upstream-addresses"></a>
Static upstream addresses can take the form of a URL that contains only scheme and host/port, or a conventional [indirizzo di rete di Caddy](/docs/conventions#indirizzi-di-rete). Esempi validi:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

Per impostazione predefinita, le connessioni all'upstream vengono effettuate tramite HTTP in chiaro. Quando si usa la forma URL, è possibile usare uno schema come scorciatoia per impostare alcuni valori predefiniti del [`transport`](#trasporti).
- Usare `https://` come schema utilizzerà il [trasporto `http`](#il-trasporto-http) con il [`tls`](#tls) abilitato.

  Inoltre, potrebbe essere necessario sovrascrivere l'header `Host` in modo che corrisponda al valore SNI del TLS, che viene usato dai server per il routing e la selezione del certificato. Consultate la sezione [HTTPS](#https) di seguito per maggiori dettagli.

- Usare `h2c://` come schema utilizzerà il [trasporto `http`](#il-trasporto-http) con le [versioni HTTP](#versioni) impostate per consentire connessioni HTTP/2 in chiaro.

- Usare `http://` come schema è identico all'aver omesso lo schema, poiché l'HTTP è già l'impostazione predefinita. Questa sintassi è inclusa per simmetria con le altre scorciatoie degli schemi.

Schemes cannot be mixed, since they modify the common transport configuration (a TLS-enabled transport cannot carry both HTTPS and plaintext HTTP). Any explicit transport configuration will not be overwritten, and omitting schemes or using other ports will not assume a particular transport.

When using IPv6 with a zone (e.g. link-local addresses with a specific network interface), a scheme **cannot** be used as a shortcut because the `%` will result in a URL-parse error; configure the transport explicitly instead.

Quando si usa la forma dell'[indirizzo di rete](/docs/conventions#indirizzi-di-rete), il tipo di rete è specificato come prefisso all'indirizzo dell'upstream. Questo non può essere combinato con uno schema URL. As a special case, `unix+h2c/` è supportato come scorciatoia per la rete `unix/` più gli stessi effetti dello schema `h2c://`. Gli intervalli di porte sono supportati come scorciatoia, che si espande in più upstream con lo stesso host.

Upstream addresses **non possono** contenere percorsi o stringhe di query, poiché ciò implicherebbe la riscrittura simultanea della richiesta durante il proxying, comportamento che non è definito né supportato. Potete usare la direttiva [`rewrite`](/docs/caddyfile/directives/rewrite) se ne avete necessità.

If l'indirizzo non è un URL (ovvero non ha uno schema), allora [placeholders](/docs/caddyfile/concepts#placeholders) can be used, ma questo rende l'upstream *dinamicamente statico*, il che significa che potenzialmente molti diversi backend agiscono come un unico upstream statico in termini di controlli sanitari e bilanciamento del carico. Raccomandiamo di usare invece un modulo di [upstream dinamici](#dynamic-upstreams), se possibile. Quando si usano i placeholder, la porta **deve** essere inclusa (o tramite la sostituzione del placeholder, o come suffisso statico dell'indirizzo).


### Upstream dinamici

<a id="dynamic-upstreams"></a>
Il reverse proxy di Caddy viene fornito di serie con alcuni moduli di upstream dinamici. Si noti che l'uso di upstream dinamici ha implicazioni per il bilanciamento del carico e i controlli sanitari, a seconda della specifica configurazione della policy: i controlli sanitari attivi non vengono eseguiti per gli upstream dinamici; inoltre il bilanciamento del carico e i controlli sanitari passivi funzionano al meglio se l'elenco degli upstream è relativamente stabile e coerente (specialmente con il round-robin). Idealmente, i moduli di upstream dinamici dovrebbero restituire solo backend sani e utilizzabili.


#### SRV

<a id="srv"></a>
Recupera gli upstream dai record DNS SRV.

```caddy-d
	dynamic srv [<nome_completo>] {
		service   <servizio>
		proto     <proto>
		name      &lt;nome&gt;
		refresh   <intervallo>
		resolvers <ip...>
		dial_timeout        <durata>
		dial_fallback_delay <durata>
	}
```

- **&lt;nome_completo&gt;** è il nome di dominio completo del record da cercare (ovvero `_servizio._proto.nome`).
- **service** è la componente servizio del nome completo.
- **proto** è la componente protocollo del nome completo. O `tcp` o `udp`.
- **name** è la componente nome. Oppure, se `service` e `proto` sono vuoti, il nome di dominio completo su cui eseguire la query.
- **refresh** è la frequenza con cui aggiornare i risultati memorizzati nella cache. Predefinito: `1m`
- **resolvers** è l'elenco dei risolutori DNS per sovrascrivere i risolutori di sistema.
- **dial_timeout** è il timeout per l'esecuzione della query.
- **dial_fallback_delay** è quanto tempo attendere prima di generare una connessione Fast Fallback RFC 6555. Predefinito: `300ms`



#### A/AAAA

<a id="aaaaa"></a>
Recupera gli upstream dai record DNS A/AAAA.

```caddy-d
	dynamic a [&lt;nome&gt; <porta>] {
		name      &lt;nome&gt;
		port      <porta>
		refresh   <intervallo>
		resolvers <ip...>
		dial_timeout        <durata>
		dial_fallback_delay <durata>
		versions ipv4|ipv6
	}
```

- **name** è il nome di dominio su cui eseguire la query.
- **port** è la porta da usare per il backend.
- **refresh** è la frequenza con cui aggiornare i risultati memorizzati nella cache. Predefinito: `1m`
- **resolvers** è l'elenco dei risolutori DNS per sovrascrivere i risolutori di sistema.
- **dial_timeout** è il timeout per l'esecuzione della query.
- **dial_fallback_delay** è quanto tempo attendere prima di generare una connessione Fast Fallback RFC 6555. Predefinito: `300ms`
- **versions** è l'elenco delle versioni IP da risolvere. Predefinito: `ipv4 ipv6` che corrispondono rispettivamente ai record A e AAAA.


#### Multi

<a id="multi"></a>
Aggiunge i risultati di più moduli di upstream dinamici. Utile se desiderate sorgenti ridondanti di upstream, ad esempio: un cluster primario di SRV supportato da un cluster secondario di SRV.

```caddy-d
	dynamic multi {
		<sorgente> [...]
	}
```

- **&lt;sorgente&gt;** è il nome del modulo per gli upstream dinamici, seguito dalla sua configurazione. Ne può essere specificato più di uno.




## Bilanciamento del carico

<a id="load-balancing"></a>
Il bilanciamento del carico viene tipicamente usato per suddividere il traffico tra più upstream. Abilitando i tentativi (retries), può essere usato anche con uno o più upstream per trattenere le richieste finché non viene selezionato un upstream sano (ad esempio per attendere e mitigare gli errori durante il riavvio o la ridistribuzione di un upstream).

Questo è abilitato per impostazione predefinita, con la policy `random`. I tentativi sono disabilitati per impostazione predefinita.

- **lb_policy** <span id="lb_policy"/> è il nome della policy di bilanciamento del carico, insieme a eventuali opzioni. Predefinito: `random`.

  Per le policy che coinvolgono l'hashing, viene usato l'algoritmo [highest-random-weight (HRW)](https://it.wikipedia.org/wiki/Rendezvous_hashing) per garantire che un client o una richiesta con la stessa chiave di hash vengano mappati sullo stesso upstream, anche se l'elenco degli upstream cambia.

  Alcune policy supportano il fallback come opzione, se indicato, nel qual caso accettano un [blocco](/docs/caddyfile/concepts#blocchi) con `fallback <policy>` che accetta un'altra policy di bilanciamento del carico. Per tali policy, il fallback predefinito è `random`. La configurazione di un fallback consente di usare una policy secondaria se la primaria non ne seleziona una, permettendo combinazioni potenti. I fallback possono essere nidificati più volte se desiderato.
  
  Ad esempio, `header` può essere usato come primario per consentire agli sviluppatori di scegliere un upstream specifico, con un fallback di `first` per tutte le altre connessioni per implementare il failover primario/secondario.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` sceglie casualmente un upstream

	- `random_choose <n>` seleziona due o più upstream casualmente, quindi sceglie quello con il carico minore (`n` è solitamente 2)

	- `first` sceglie il primo upstream disponibile, nell'ordine in cui sono definiti nella configurazione, consentendo il failover primario/secondario; ricordate di abilitare i controlli sanitari insieme a questa opzione, altrimenti il failover non avverrà

	- `round_robin` itera su ogni upstream a turno

	- `weighted_round_robin <pesi...>` itera su ogni upstream a turno, rispettando i pesi forniti. Il numero di argomenti peso deve corrispondere al numero di upstream configurati. I pesi devono essere numeri interi non negativi. Ad esempio con due upstream e pesi `5 1`, il primo upstream verrebbe selezionato 5 volte di seguito prima che il secondo upstream venga selezionato una volta, poi il ciclo si ripete. Se viene usato zero come peso, la selezione di quell'upstream per le nuove richieste sarà disabilitata.

	- `least_conn` sceglie l'upstream con il minor numero di richieste attuali; se più di un host ha lo stesso numero minimo di richieste, uno di questi host viene scelto a caso

	- `ip_hash` mappa l'IP remoto (il peer immediato) su un upstream persistente (sticky)

	- `client_ip_hash` mappa l'IP del client su un upstream persistente; questa opzione è meglio accoppiata con l'[opzione globale `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) che abilita l'analisi dell'IP reale del client, altrimenti si comporta come `ip_hash`

	- `uri_hash` mappa l'URI della richiesta (percorso e query) su un upstream persistente

	- `query [chiave]` mappa una query della richiesta su un upstream persistente, eseguendo l'hashing del valore della query; se la chiave specificata non è presente, verrà usata la policy di fallback per selezionare un upstream (`random` per impostazione predefinita)

	- `header [campo]` mappa un header della richiesta su un upstream persistente, eseguendo l'hashing del valore dell'header; se il campo header specificato non è presente, verrà usata la policy di fallback per selezionare un upstream (`random` per impostazione predefinita)

	- `cookie [&lt;nome&gt; [<segreto>]]` alla prima richiesta da parte di un client (quando non c'è alcun cookie), verrà usata la policy di fallback per selezionare un upstream (`random` per impostazione predefinita), e viene aggiunto l'header `Set-Cookie` alla risposta (il nome predefinito del cookie è `lb` se non specificato). Il valore del cookie è l'indirizzo di connessione dell'upstream scelto, hashata con HMAC-SHA256 (usando `<segreto>` come segreto condiviso, stringa vuota se non specificato).
	
	  Sulle richieste successive dove il cookie è presente, il valore del cookie verrà mappato sullo stesso upstream se disponibile; se non disponibile o non trovato, viene selezionato un nuovo upstream con la policy di fallback, e il cookie viene aggiunto alla risposta.

	  If desiderate usare un particolare upstream per scopi di debugging, potete eseguire l'hashing dell'indirizzo dell'upstream con il segreto e impostare il cookie nel vostro client HTTP (browser o altro). Per esempio, con PHP, potreste eseguire quanto segue per calcolare il valore del cookie, dove `10.1.0.10:8080` è l'indirizzo di uno dei vostri upstream e `secret` è il vostro segreto configurato.
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  Potete impostare il cookie nel vostro browser tramite la console Javascript, ad esempio per impostare il cookie chiamato `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> è il numero di volte in cui riprovare a selezionare i backend disponibili per ogni richiesta se l'host successivo disponibile è giù. Per impostazione predefinita, i tentativi sono disabilitati (zero).

  If anche [`lb_try_duration`](#lb_try_duration) è configurato, allora i tentativi potrebbero fermarsi prima se la durata viene raggiunta. In altri termini, la durata del tentativo ha la precedenza sul numero di tentativi.

- **lb_try_duration** <span id="lb_try_duration"/> è un [valore di durata](/docs/conventions#durate) che definisce quanto a lungo provare a selezionare i backend disponibili per ogni richiesta se l'host successivo disponibile è giù. Per impostazione predefinita, i tentativi sono disabilitati (durata zero).

  I client attenderanno fino a questo tempo mentre il bilanciatore di carico tenta di trovare un host upstream disponibile. Un ragionevole punto di partenza potrebbe essere `5s` dato che il timeout di connessione predefinito del trasporto HTTP è `3s`, quindi ciò dovrebbe consentire almeno un tentativo se il primo upstream selezionato non può essere raggiunto; sentitevi però liberi di sperimentare per trovare il giusto equilibrio per il vostro caso d'uso.

- **lb_try_interval** <span id="lb_try_interval"/> è un [valore di durata](/docs/conventions#durate) che definisce quanto attendere tra la selezione dell'host successivo dal pool. Il valore predefinito è `250ms`. Rilevante solo quando una richiesta a un host upstream fallisce. Siate consapevoli che impostare questo valore a `0` con una `lb_try_duration` non nulla può causare un picco di utilizzo della CPU se tutti i backend sono giù e la latenza è molto bassa.

- **lb_retry_match** <span id="lb_retry_match"/> limita le richieste per le quali i tentativi sono consentiti. Una richiesta deve corrispondere a questa condizione per poter essere riprovata se la connessione all'upstream è riuscita ma il round-trip successivo è fallito. Se la connessione all'upstream è fallita, un tentativo è sempre consentito. Per impostazione predefinita, vengono riprovate solo le richieste `GET`.

  La sintassi per questa opzione è la stessa dei [matcher di richiesta con nome](/docs/caddyfile/matchers#matcher-con-nome), ma senza il `@nome`. Se avete bisogno solo di un singolo matcher, potete configurarlo sulla stessa riga. Per più matcher è necessario un blocco.



### Controlli sanitari attivi

<a id="active-health-checks"></a>
I controlli sanitari attivi eseguono il controllo dello stato di salute in background tramite un timer. Per abilitarli, sono richiesti `health_uri` o `health_port`.

- **health_uri** <span id="health_uri"/> è il percorso dell'URI (e query opzionale) per i controlli sanitari attivi.

- **health_upstream** <span id="health_upstream"/> è l'ip:porta da usare per i controlli sanitari attivi, se diverso dall'upstream. Questo dovrebbe essere usato in tandem con `health_header` e `{http.reverse_proxy.active.target_upstream}`.

- **health_port** <span id="health_port"/> è la porta da usare per i controlli sanitari attivi, se diversa dalla porta dell'upstream. Ignorato se viene usato `health_upstream`.

- **health_interval** <span id="health_interval"/> è un [valore di durata](/docs/conventions#durate) che definisce la frequenza con cui eseguire i controlli sanitari attivi. Predefinito: `30s`.

- **health_passes** <span id="health_passes"/> è il numero di controlli sanitari consecutivi riusciti richiesti prima di contrassegnare nuovamente il backend come sano. Predefinito: `1`.

- **health_fails** <span id="health_fails"/> è il numero di controlli sanitari consecutivi falliti richiesti prima di contrassegnare il backend come non sano. Predefinito: `1`.

- **health_timeout** <span id="health_timeout"/> è un [valore di durata](/docs/conventions#durate) che definisce quanto tempo attendere per una risposta prima di contrassegnare il backend come giù. Predefinito: `5s`.

- **health_method** <span id="health_method"/> è il metodo HTTP da usare per il controllo sanitario attivo. Predefinito: `GET`.

- **health_status** <span id="health_status"/> è il codice di stato HTTP da aspettarsi da un backend sano. Può essere un codice di stato a 3 cifre, o una classe di codici di stato che termina in `xx`. Per esempio: `200` (che è il valore predefinito), o `2xx`.

- **health_request_body** <span id="health_request_body"/> è una stringa che rappresenta il corpo della richiesta da inviare con il controllo sanitario attivo.

- **health_body** <span id="health_body"/> è una sottostringa o espressione regolare da confrontare con il corpo della risposta di un controllo sanitario attivo. Se il backend non restituisce un corpo corrispondente, verrà contrassegnato come giù.

- **health_follow_redirects** <span id="health_follow_redirects"/> farà sì che il controllo sanitario segua i reindirizzamenti forniti dall'upstream. Per impostazione predefinita, una risposta di reindirizzamento farebbe contare il controllo sanitario come fallito.

- **health_headers** <span id="health_headers"/> permette di specificare gli header da impostare sulle richieste di controllo sanitario attivo. Questo è utile se avete bisogno di cambiare l'header `Host`, o se dovete fornire dell'autenticazione al vostro backend come parte dei vostri controlli sanitari.



### Controlli sanitari passivi

<a id="passive-health-checks"></a>
I controlli sanitari passivi avvengono in linea con le effettive richieste effettuate tramite proxy. Per abilitarli, è richiesto `fail_duration`.

- **fail_duration** <span id="fail_duration"/> è un [valore di durata](/docs/conventions#durate) che definisce quanto a lungo ricordare una richiesta fallita. Una durata > `0` abilita il controllo sanitario passivo; il valore predefinito è `0` (spento). Un ragionevole punto di partenza potrebbe essere `30s` per bilanciare i tassi di errore con la reattività quando si riporta online un upstream non sano; sentitevi però liberi di sperimentare per trovare il giusto equilibrio per il vostro caso d'uso.

- **max_fails** <span id="max_fails"/> è il numero massimo di richieste fallite all'interno di `fail_duration` necessarie per considerare un backend come giù; deve essere >= `1`; il valore predefinito è `1`.

- **unhealthy_status** <span id="unhealthy_status"/> conta una richiesta come fallita se la risposta ritorna con uno di questi codici di stato. Può essere un codice di stato a 3 cifre o una classe di codici di stato che termina in `xx`, ad esempio: `404` o `5xx`.

- **unhealthy_latency** <span id="unhealthy_latency"/> è un [valore di durata](/docs/conventions#durate) che conta una richiesta come fallita se impiega questo tempo per ottenere una risposta.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> è il numero consentito di richieste simultanee a un backend prima di contrassegnarlo come giù. In altre parole, se un particolare backend sta gestendo attualmente questo numero di richieste, allora è considerato "sovraccarico" e gli altri backend verranno preferiti.

  Questo dovrebbe essere un numero ragionevolmente grande; la configurazione di questo valore significa che il proxy avrà un limite di `unhealthy_request_count × numero_upstream` richieste simultanee totali, e qualsiasi richiesta oltre quel punto risulterà in un errore dovuto alla mancanza di upstream disponibili.


## Eventi

<a id="eventi"></a>
Quando un upstream passa dallo stato di sano a quello di non sano o viceversa, viene emesso [un evento](/docs/caddyfile/options#opzioni-eventi). Questi eventi possono essere usati per innescare altre azioni, come l'invio di una notifica o il logging di un messaggio. Gli eventi sono i seguenti:

- `healthy` viene emesso quando un upstream viene contrassegnato come sano quando precedentemente non lo era
- `unhealthy` viene emesso quando un upstream viene contrassegnato come non sano quando precedentemente lo era

In entrambi i casi, l'`host` è incluso come metadato nell'evento per identificare l'upstream che ha cambiato stato. Può essere usato come placeholder con `{event.data.host}` con l'handler di eventi `exec`, ad esempio.



## Streaming

<a id="streaming"></a>
Per impostazione predefinita, il proxy esegue il buffering parziale della risposta per efficienza di rete.

Il proxy supporta anche le connessioni WebSocket, eseguendo la richiesta di upgrade HTTP e passando poi la connessione a un tunnel bidirezionale.

<aside class="tip">

Per impostazione predefinita, le connessioni WebSocket vengono chiuse forzatamente (con un messaggio di controllo Close inviato sia al client che all'upstream) quando la configurazione viene ricaricata. Ogni richiesta mantiene un riferimento alla configurazione, quindi chiudere le vecchie connessioni è necessario per tenere sotto controllo l'uso della memoria. Questo comportamento di chiusura può essere personalizzato con le opzioni [`stream_timeout`](#stream_timeout) e [`stream_close_delay`](#stream_close_delay).

</aside>

- **flush_interval** <span id="flush_interval"/> è un [valore di durata](/docs/conventions#durate) che regola la frequenza con cui Caddy deve svuotare (flush) il buffer di risposta verso il client. Per impostazione predefinita, non viene eseguito alcuno svuotamento periodico. Un valore negativo (tipicamente -1) suggerisce la "modalità a bassa latenza" che disabilita completamente il buffering della risposta e svuota immediatamente dopo ogni scrittura verso il client, e non annulla la richiesta al backend anche se il client si disconnette in anticipo. Questa opzione viene ignorata e le risposte vengono svuotate immediatamente verso il client se si applica una delle seguenti condizioni dalla risposta:
	- `Content-Type: text/event-stream`
	- `Content-Length` è sconosciuto
	- HTTP/2 su entrambi i lati del proxy, `Content-Length` è sconosciuto e `Accept-Encoding` non è impostato o è "identity"

- **request_buffers** <span id="request_buffers"/> farà sì che il proxy legga fino a `<dimensione>` byte dal corpo della richiesta in un buffer prima di inviarlo all'upstream. Questo è molto inefficiente e dovrebbe essere fatto solo se l'upstream richiede la lettura dei corpi delle richieste senza ritardi (cosa che l'applicazione upstream dovrebbe risolvere). Accetta tutti i formati di dimensione supportati da [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **response_buffers** <span id="response_buffers"/> farà sì che il proxy legga fino a `<dimensione>` byte dal corpo della risposta in un buffer prima che venga restituito al client. Questo dovrebbe essere evitato se possibile per ragioni prestazionali, ma potrebbe essere utile se il backend ha vincoli di memoria più stretti. Accetta tutti i formati di dimensione supportati da [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **stream_timeout** <span id="stream_timeout"/> è un [valore di durata](/docs/conventions#durate) dopo il quale le richieste di streaming come i WebSocket verranno chiuse forzatamente al termine del timeout. Questo essenzialmente annulla le connessioni se rimangono aperte troppo a lungo. Un ragionevole punto di partenza potrebbe essere `24h` per eliminare le connessioni più vecchie di un giorno. Predefinito: nessun timeout.

- **stream_close_delay** <span id="stream_close_delay"/> è un [valore di durata](/docs/conventions#durate) che ritarda la chiusura forzata delle richieste di streaming come i WebSocket quando la configurazione viene scaricata; invece, lo stream rimarrà aperto fino al termine del ritardo. In altri termini, l'abilitazione di questa opzione impedisce agli stream di chiudersi immediatamente quando la configurazione di Caddy viene ricaricata. Abilitare questa opzione può essere una buona idea per evitare un gregge tonante (thundering herd) di client che si riconnettono contemporaneamente dopo che le loro connessioni sono state chiuse dalla chiusura della configurazione precedente. Un ragionevole punto di partenza potrebbe essere qualcosa come `5m` per permettere agli utenti di lasciare la pagina naturalmente dopo un ricaricamento della configurazione. Predefinito: nessun ritardo.



## Header

<a id="headers"></a>
Il proxy può **manipolare gli header** tra se stesso e il backend:

- **header_up** <span id="header_up"/> imposta, aggiunge (con il prefisso `+`), elimina (con il prefisso `-`), o esegue una sostituzione (usando due argomenti, una ricerca e una sostituzione) in un header di richiesta diretto all'upstream verso il backend.

- **header_down** <span id="header_down"/> imposta, aggiunge (con il prefisso `+`), elimina (con il prefisso `-`), o esegue una sostituzione (usando due argomenti, una ricerca e una sostituzione) in un header di risposta proveniente dall'upstream dal backend.

Per esempio, per impostare un header di richiesta, sovrascrivendo eventuali valori esistenti:

```caddy-d
header_up Some-Header "il valore"
```

Per aggiungere un header di risposta; si noti che possono esserci più valori per un campo header:

```caddy-d
header_down +Some-Header "primo valore"
header_down +Some-Header "secondo valore"
```

Per eliminare un header di richiesta, impedendo che raggiunga il backend:

```caddy-d
header_up -Some-Header
```

Per eliminare tutti gli header di richiesta corrispondenti, usando una corrispondenza del suffisso:

```caddy-d
header_up -Some-*
```

Per eliminare *tutti* gli header di richiesta, per poter aggiungere individualmente quelli desiderati (non raccomandato):

```caddy-d
header_up -*
```

Per eseguire una sostituzione tramite espressione regolare su un header di richiesta:

```caddy-d
header_up Some-Header "^prefisso-([A-Za-z0-9]*)$" "sostituito-$1-suffisso"
```

Il linguaggio delle espressioni regolari utilizzato è RE2, incluso in Go. Consultate il [riferimento alla sintassi RE2](https://github.com/google/re2/wiki/Syntax) e la [panoramica della sintassi regexp di Go](https://pkg.go.dev/regexp/syntax). La stringa di sostituzione viene [espansa](https://pkg.go.dev/regexp#Regexp.Expand), consentendo l'uso dei valori catturati, ad esempio `$1` per il primo gruppo di cattura.


### Valori predefiniti

Per impostazione predefinita, Caddy passa gli header in entrata &mdash; incluso `Host` &mdash; al backend senza modifiche, con tre eccezioni:

- Imposta o aumenta il campo header [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Imposta il campo header [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Imposta il campo header [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"/> Per questi header `X-Forwarded-*`, per impostazione predefinita, il proxy ignorerà i loro valori dalle richieste in entrata, per prevenire lo spoofing.

If Caddy non è il primo server a cui i vostri client si connettono (ad esempio quando una CDN è davanti a Caddy), potete configurare `trusted_proxies` con un elenco di intervalli IP (CIDR) dai quali le richieste in entrata sono considerate fide per aver inviato valori corretti per questi header.

Si raccomanda vivamente di configurare questo valore tramite l'[opzione globale `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) anziché nel proxy, in modo che si applichi a tutti gli handler proxy nel vostro server, e ciò ha il vantaggio di abilitare l'analisi dell'IP del client.

<aside class="tip">

Se state usando Cloudflare davanti a Caddy, siate consapevoli che potreste essere vulnerabili allo spoofing dell'header `X-Forwarded-For`. I nostri amici di [Authelia](https://www.authelia.com) hanno documentato una [soluzione alternativa](https://www.authelia.com/integration/proxies/forwarded-headers/) per configurare Cloudflare in modo da ignorare i valori in entrata per questo header.

</aside>

Inoltre, quando si usa il [trasporto `http`](#il-trasporto-http), verrà impostato l'header `Accept-Encoding: gzip`, se mancante nella richiesta del client. Ciò consente all'upstream di servire contenuti compressi se è in grado di farlo. Questo comportamento può essere disabilitato con [`compression off`](#compressione) sul trasporto.


### HTTPS

<a id="https"></a>
Poiché (la maggior parte degli) header mantiene il proprio valore originale quando viene effettuato il proxying, è spesso necessario sovrascrivere l'header `Host` con l'indirizzo dell'upstream configurato quando si effettua il proxy verso l'HTTPS, in modo che l'header `Host` corrisponda al valore SNI del TLS:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Dalla v2.11.0 di Caddy, ciò avviene automaticamente, quindi non è più necessario sovrascrivere esplicitamente l'header `Host` quando si effettua il proxy verso l'HTTPS. Se desiderate rinunciare a questo comportamento, potete impostare l'header `Host` al suo valore originale (ma raramente ha senso farlo):

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

L'header `X-Forwarded-Host` viene comunque passato [per impostazione predefinita](#valori-predefiniti), quindi l'upstream può comunque usarlo se ha bisogno di conoscere il valore originale dell'header `Host`.

Lo stesso vale quando si termina il TLS in Caddy e si effettua il proxy via HTTP, sia verso una porta che verso un socket unix. Infatti, Caddy stesso deve ricevere l'Host corretto, quando è il target di `reverse_proxy`. Nel caso del socket unix, l'`upstream_hostport` sarà il percorso del socket, e l'Host deve essere impostato esplicitamente.



## Riscritture

<a id="rewrites"></a>
Per impostazione predefinita, Caddy esegue la richiesta all'upstream con lo stesso metodo HTTP e lo stesso URI della richiesta in entrata, a meno che non sia stata eseguita una riscrittura nella catena dei middleware prima che raggiunga `reverse_proxy`.

Prima di effettuarne il proxy, la richiesta viene clonata; ciò garantisce che eventuali modifiche apportate alla richiesta durante l'handler non trapelino verso altri handler. Questo è utile in situazioni in cui la gestione deve continuare dopo il proxy.

Oltre alle [manipolazioni degli header](#header), il metodo e l'URI della richiesta possono essere modificati prima di essere inviati all'upstream:

- **method** <span id="method"/> cambia il metodo HTTP della richiesta clonata. Se il metodo viene cambiato in `GET` o `HEAD`, allora il corpo della richiesta in entrata *non* verrà inviato all'upstream da questo handler. Ciò è utile se desiderate consentire a un handler diverso di consumare il corpo della richiesta.
- **rewrite** <span id="rewrite"/> cambia l'URI (percorso e query) della richiesta clonata. Questo è simile alla [direttiva `rewrite`](/docs/caddyfile/directives/rewrite), tranne per il fatto che non rende persistente la riscrittura oltre l'ambito di questo handler.

Queste riscritture sono spesso utili per pattern come le "richieste di pre-controllo", dove una richiesta viene inviata a un altro server per aiutare a decidere come continuare a gestire la richiesta corrente.

Per esempio, la richiesta potrebbe essere inviata a un gateway di autenticazione per decidere se la richiesta proveniva da un utente autenticato (es. la richiesta ha un cookie di sessione) e deve continuare, o se dovrebbe invece essere reindirizzata a una pagina di login. Per questo pattern, Caddy fornisce una direttiva scorciatoia [`forward_auth`](/docs/caddyfile/directives/forward_auth) per saltare la maggior parte del boilerplate della configurazione.




## Trasporti

<a id="transports"></a>
Il **trasporto** del proxy di Caddy è collegabile (pluggable):

- **transport** <span id="transport"/> definisce come comunicare con il backend. Il valore predefinito è `http`.


### Il trasporto `http`

<a id="the-http-transport"></a>
```caddy-d
transport http {
	read_buffer             <dimensione>
	write_buffer            <dimensione>
	max_response_header     <dimensione>
	proxy_protocol          v1|v2
	dial_timeout            <durata>
	dial_fallback_delay     <durata>
	response_header_timeout <durata>
	expect_continue_timeout <durata>
	resolvers <ip...>
	tls
	tls_client_auth <nome_automazione> | <file_cert> <file_chiave>
	tls_insecure_skip_verify
	tls_curves <curve...>
	tls_timeout <durata>
	tls_trust_pool &lt;modulo&gt;
	tls_server_name <nome_server>
	tls_renegotiation <livello>
	tls_except_ports <porte...>
	keepalive [off|<durata>]
	keepalive_interval <intervallo>
	keepalive_idle_conns <conteggio_max>
	keepalive_idle_conns_per_host <conteggio>
	versions <versioni...>
	compression off
	max_conns_per_host <conteggio>
	network_proxy &lt;modulo&gt;
}
```

- **read_buffer** <span id="read_buffer"/> è la dimensione del buffer di lettura in byte. Accetta tutti i formati supportati da [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Predefinito: `4KiB`.

- **write_buffer** <span id="write_buffer"/> è la dimensione del buffer di scrittura in byte. Accetta tutti i formati supportati da [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Predefinito: `4KiB`.

- **max_response_header** <span id="max_response_header"/> è la quantità massima di byte da leggere dagli header di risposta. Accetta tutti i formati supportati da [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Predefinito: `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> abilita il [protocollo PROXY](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (reso popolare da HAProxy) sulla connessione all'upstream, anteponendo i dati dell'IP reale del client. Questa opzione è meglio accoppiata con l'[opzione globale `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) se Caddy è dietro un altro proxy. Sono supportate le versioni `v1` e `v2`. Questa opzione dovrebbe essere usata solo se sapete che il server upstream è in grado di analizzare il protocollo PROXY. Per impostazione predefinita, è disabilitata.

- **dial_timeout** <span id="dial_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa quando ci si connette al socket dell'upstream. Predefinito: `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> è la [durata](/docs/conventions#durate) massima di attesa prima di generare una connessione Fast Fallback RFC 6555. Un valore negativo disabilita questa funzione. Predefinito: `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa per la lettura degli header di risposta dall'upstream. Predefinito: nessun timeout.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa per i primi header di risposta dell'upstream dopo aver scritto completamente gli header della richiesta, se la richiesta ha l'header `Expect: 100-continue`. Predefinito: nessun timeout.

- **read_timeout** <span id="read_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa per la lettura successiva dal backend. Predefinito: nessun timeout.

- **write_timeout** <span id="write_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa per le scritture successive verso il backend. Predefinito: nessun timeout.

- **resolvers** <span id="resolvers"/> è un elenco di risolutori DNS per sovrascrivere i risolutori di sistema.

- **tls** <span id="tls"/> usa l'HTTPS con il backend. Sarà abilitato automaticamente se specificate i backend usando lo schema `https://`, o se una qualsiasi delle opzioni `tls_*` sottostanti è configurata.

- **tls_client_auth** <span id="tls_client_auth"/> abilita l'autenticazione del client TLS in uno di due modi: (1) specificando un nome di dominio per il quale Caddy dovrebbe ottenere un certificato e mantenerlo rinnovato, o (2) specificando un file di certificato e uno di chiave da presentare per l'autenticazione del client TLS con il backend.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> disattiva la verifica dell'handshake TLS, rendendo la connessione insicura e vulnerabile agli attacchi man-in-the-middle. *Non usare in produzione.*

- **tls_curves** <span id="tls_curves"/> è un elenco di curve ellittiche da supportare per la connessione upstream. I valori predefiniti di Caddy sono moderni e sicuri, quindi dovreste configurare questa opzione solo se avete requisiti specifici.

- **tls_timeout** <span id="tls_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa per il completamento dell'handshake TLS. Predefinito: nessun timeout.

- **tls_trust_pool** <span id="tls_trust_pool"/> configures la sorgente delle autorità di certificazione fide in modo simile alla [sottodirettiva `trust_pool`](/docs/caddyfile/directives/tls#trust_pool) descritta nella documentazione della direttiva `tls`. L'elenco delle sorgenti del pool di fiducia disponibili nell'installazione standard di Caddy è disponibile [qui](/docs/caddyfile/directives/tls#trust-pool-providers).

- **tls_server_name** <span id="tls_server_name"/> imposta il nome del server usato durante la verifica del certificato ricevuto nell'handshake TLS. Per impostazione predefinita, verrà usata la parte host dell'indirizzo dell'upstream.

  Dovete sovrascrivere questo valore solo se l'indirizzo dell'vostro upstream non corrisponde al certificato che l'upstream probabilmente utilizzerà. Ad esempio, se l'indirizzo dell'upstream è un indirizzo IP, allora dovrete configurare questo valore con l'hostname servito dal server upstream.

  Può essere usato un placeholder della richiesta, nel qual caso verrà usata una copia della configurazione del trasporto HTTP ad ogni richiesta, il che potrebbe comportare una penalità prestazionale.

- **tls_renegotiation** <span id="tls_renegotiation"/> imposta il livello di rinegoziazione TLS. La rinegoziazione TLS è l'atto di eseguire handshake successivi dopo il primo. Il livello può essere uno di:
  - `never` (predefinito) disabilita la rinegoziazione.
  - `once` permette a un server remoto di richiedere la rinegoziazione una volta per connessione.
  - `freely` permette a un server remoto di richiedere ripetutamente la rinegoziazione.

- **tls_except_ports** <span id="tls_except_ports"/> quando il TLS è abilitato, se il target dell'upstream usa una delle porte fornite, il TLS verrà disabilitato per quelle connessioni. Questo può essere utile quando si configurano upstream dinamici, dove alcuni upstream si aspettano richieste HTTP e altri HTTPS.

- **keepalive** <span id="keepalive"/> è o `off` o un [valore di durata](/docs/conventions#durate) che specifica quanto a lungo mantenere aperte le connessioni (timeout). Predefinito: `2m`.

  ⚠️ Le richieste agli upstream HTTP/1.1 potrebbero fallire a causa di errori "connection reset by peer" se la durata del keepalive supera il timeout di keepalive del server upstream. Le richieste idempotenti verranno riprovate dal trasporto HTTP di Go, ma Caddy risponderà con codice di stato 502 negli altri casi.

- **keepalive_interval** <span id="keepalive_interval"/> è la [durata](/docs/conventions#durate) tra i probe di liveness. Predefinito: `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> definisce il numero massimo di connessioni da mantenere vive. Predefinito: nessun limite.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> se non nullo, controlla il numero massimo di connessioni inattive (keep-alive) da mantenere per ogni host. Predefinito: `32`.

- **versions** <span id="versions"/> permette di personalizzare quali versioni di HTTP supportare.
  
  Le opzioni valide sono: `1.1`, `2`, `h2c`, `3`. 

  Predefinito: `1.1 2`, oppure se lo [schema dell'upstream](#indirizzi-upstream) è `h2c://`, allora il valore predefinito è `h2c 2`.

  `h2c` abilita le connessioni HTTP/2 in chiaro verso l'upstream. Questa è una funzionalità non standard che non usa il trasporto HTTP predefinito di Go, quindi è esclusiva rispetto alle altre funzionalità.

  `3` abilita le connessioni HTTP/3 verso l'upstream. ⚠️ Questa è una funzionalità sperimentale ed è soggetta a cambiamenti.

- **compression** <span id="compressione"/> può essere usato per disabilitare la compressione verso il backend impostandolo su `off`.

- **max_conns_per_host** <span id="max_conns_per_host"/> limita opzionalmente il numero totale di connessioni per host, incluse le connessioni negli stati di composizione, attiva e inattiva. Predefinito: nessun limite.

- **network_proxy** <span id="network_proxy"/> specifica il nome di un modulo proxy di rete da usare per le richieste al server upstream. Se non configurato esplicitamente, Caddy rispetta il proxy configurato tramite le variabili d'ambiente secondo la [libreria standard di Go](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), ovvero `HTTP_PROXY`, `HTTPS_PROXY` e `NO_PROXY`. Quando viene fornito un valore per questo parametro, le richieste fluiranno attraverso il reverse proxy nel seguente ordine: Client (utenti) → `reverse_proxy` → `network_proxy` → upstream. I moduli integrati sono:
	- `none`, che viene usato per ignorare le impostazioni d'ambiente di `HTTP_PROXY`, `HTTPS_PROXY` e `NO_PROXY`.
	- `url <url>`, che viene usato per specificare un singolo URL che sovrascrive la configurazione dell'ambiente.

### Il trasporto `fastcgi`

<a id="the-fastcgi-transport"></a>
```caddy-d
transport fastcgi {
	root  &lt;percorso&gt;
	split <dove>
	env   &lt;chiave&gt; &lt;valore&gt;
	resolve_root_symlink
	dial_timeout  <durata>
	read_timeout  <durata>
	write_timeout <durata>
	capture_stderr
}
```

- **root** <span id="root"/> è la radice del sito. Predefinito: `{http.vars.root}` o la directory di lavoro corrente.

- **split** <span id="split"/> è dove suddividere il percorso per ottenere PATH_INFO alla fine dell'URI.

- **env** <span id="env"/> imposta una variabile d'ambiente extra con il valore fornito. Può essere specificato più di una volta per più variabili d'ambiente.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> abilita la risoluzione della directory `root` al suo valore effettivo valutando un collegamento simbolico, se ne esiste uno.

- **dial_timeout** <span id="dial_timeout"/> è quanto tempo attendere durante la connessione al socket dell'upstream. Accetta [valori di durata](/docs/conventions#durate). Predefinito: `3s`.

- **read_timeout** <span id="read_timeout"/> è quanto tempo attendere durante la lettura dal server FastCGI. Accetta [valori di durata](/docs/conventions#durate). Predefinito: nessun timeout.

- **write_timeout** <span id="write_timeout"/> è quanto tempo attendere durante l'invio al server FastCGI. Accetta [valori di durata](/docs/conventions#durate). Predefinito: nessun timeout.

- **capture_stderr** <span id="capture_stderr"/> abilita la cattura e il logging di qualsiasi messaggio inviato dal server fastcgi upstream su `stderr`. Il logging viene eseguito a livello `WARN` per impostazione predefinita. Se la risposta ha uno stato `4xx` o `5xx`, verrà invece usato il livello `ERROR`. Per impostazione predefinita, lo `stderr` viene ignorato.

<aside class="tip">

Se state cercando di servire una moderna applicazione PHP, potreste cercare la [direttiva `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi), che è una scorciatoia per un proxy che usa la direttiva `fastcgi`, con le riscritture necessarie per usare `index.php` come punto di ingresso per il routing.

</aside>



## Intercettare le risposte

<a id="intercepting-responses"></a>
Il reverse proxy può essere configurato per intercettare le risposte dal backend. Per facilitare ciò, possono essere definiti dei [matcher di risposta](/docs/caddyfile/response-matchers) (simili alla sintassi dei matcher di richiesta) e verrà invocata la prima rotta `handle_response` corrispondente.

Quando viene invocato un gestore di risposta, la risposta dal backend non viene scritta verso il client, e verrà invece eseguita la rotta `handle_response` configurata; spetterà a tale rotta scrivere una risposta. Se la rotta *non* scrive una risposta, allora la gestione della richiesta continuerà con eventuali gestori che sono [ordinati dopo](/docs/caddyfile/directives#ordine-delle-direttive) questo `reverse_proxy`.

- **@nome** è il nome di un [matcher di risposta](/docs/caddyfile/response-matchers). Finché ogni matcher di risposta ha un nome unico, ne possono essere definiti molteplici. Una risposta può essere filtrata in base al codice di stato e alla presenza o al valore di un header di risposta.

- **replace_status** <span id="replace_status"/> cambia semplicemente il codice di stato della risposta quando corrisponde al matcher fornito.

- **handle_response** <span id="handle_response"/> definisce la rotta da eseguire quando corrisponde al matcher fornito (o, se un matcher viene omesso, a tutte le risposte). Verrà applicato il primo blocco corrispondente. All'interno di un blocco `handle_response`, può essere usata qualsiasi altra [direttiva](/docs/caddyfile/directives).

Inoltre, all'interno di `handle_response`, possono essere usate due speciali direttive gestore:

- **copy_response** <span id="copy_response"/> copia il corpo della risposta ricevuto dal backend verso il client. Consente opzionalmente di cambiare il codice di stato della risposta mentre lo si fa. Questa direttiva è [ordinata prima di `respond`](/docs/caddyfile/directives#ordine-delle-direttive).

- **copy_response_headers** <span id="copy_response_headers"/> copia gli header della risposta dal backend verso il client, includendo opzionalmente *OPPURE* escludendo un elenco di campi header (non è possibile specificare sia `include` che `exclude`). Questa direttiva è [ordinata dopo `header`](/docs/caddyfile/directives#ordine-delle-direttive).

Tre placeholder saranno resi disponibili all'interno delle rotte `handle_response`:

- `{rp.status_code}` Il codice di stato dalla risposta del backend.

- `{rp.status_text}` Il testo dello stato dalla risposta del backend.

- `{rp.header.*}` Gli header dalla risposta del backend.

Sebbene il gestore di risposta del reverse proxy possa copiare la nuova risposta ricevuta dal proxy verso il client, non può passare tale nuova risposta a un reverse proxy successivo. Ogni uso di `reverse_proxy` riceve il corpo dalla richiesta originale (o come modificato con un modulo diverso).




## Esempi

<a id="examples"></a>
Reverse proxy per tutte le richieste verso un backend locale:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


[Bilanciare il carico](#load-balancing) di tutte le richieste [tra 3 backend](#upstreams):

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


Lo stesso, ma solo per le richieste all'interno di `/api`, e persistente usando la [policy `cookie`](#lb_policy):

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


Usare i [controlli sanitari attivi](#active-health-checks) per determinare quali backend sono sani, e abilitare i [tentativi](#lb_try_duration) sulle connessioni fallite, trattenendo la richiesta finché non viene trovato un backend sano:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Configurare alcune [opzioni di trasporto](#trasporti):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Reverse proxy verso un [upstream HTTPS](#https) (dalla v2.11.0, Caddy imposterà automaticamente l'header `Host` affinché corrisponda all'host dell'upstream, quindi non è più necessario farlo manualmente):

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Reverse proxy verso un upstream HTTPS, ma [⚠️ disabilitando la verifica TLS](#tls_insecure_skip_verify). Questo NON È RACCOMANDATO, poiché disabilita tutti i controlli di sicurezza offerti dall'HTTPS; il proxying su HTTP in reti private è preferibile se possibile, perché evita il falso senso di sicurezza:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


In alternativa, potete stabilire la fiducia con l'upstream [considerando affidabile il certificato dell'upstream](#tls_trust_pool) in modo esplicito, e (opzionalmente) impostando TLS-SNI affinché corrisponda all'hostname nel certificato dell'upstream:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /percorso/del/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



[Rimuovere un prefisso di percorso](handle_path) prima del proxying; tenete però presente il [problema delle sottocartelle <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575):

```caddy
example.com {
	handle_path /prefisso/* {
		reverse_proxy localhost:9000
	}
}
```


Sostituire un prefisso di percorso prima del proxying, usando una [`rewrite`](/docs/caddyfile/directives/rewrite):

```caddy
example.com {
	handle_path /vecchio-prefisso/* {
		rewrite /nuovo-prefisso{path}
		reverse_proxy localhost:9000
	}
}
```


Supporto a `X-Accel-Redirect`, ovvero servire file statici come richiesto, [intercettando la risposta](#intercepting-responses):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root * /percorso/dei/file/privati
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Pagina di errore personalizzata per gli errori dall'upstream, [intercettando le risposte di errore](#intercepting-responses) tramite il codice di stato:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root * /percorso/delle/pagine/errore
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Ottenere i backend [dinamicamente](#dynamic-upstreams) dalle query DNS dei [record `A`/`AAAA`](#aaaaa):

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Ottenere i backend [dinamicamente](#dynamic-upstreams) dalle query DNS dei [record `SRV`](#srv):

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


L'uso dei [controlli sanitari attivi](#active-health-checks) e di `health_upstream` può essere utile quando si crea un servizio intermedio per eseguire un controllo sanitario più accurato. `{http.reverse_proxy.active.target_upstream}` può quindi essere usato come header per fornire l'upstream originale al servizio di controllo sanitario.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
