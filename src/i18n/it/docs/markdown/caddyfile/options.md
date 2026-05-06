---
title: Opzioni globali (Caddyfile)
---

<script>
ready(function() {
	// Aggiungeremo dei link alle opzioni nel blocco di codice in alto
	// ai loro tag anchor associati.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Aggiungi link sui commenti alle loro rispettive sezioni
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // lo spazio bianco iniziale
			text = text.slice(text.indexOf('#')); // solo la parte del commento
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Correzione chirurgica di un link duplicato; 'name' appare due volte come link
	// per due diverse sezioni, quindi cambiamo il secondo in #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Correzione chirurgica di `renewal_window_ratio` che appare due volte come link per due diverse sezioni, quindi cambiamo il secondo in #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


# Opzioni globali

Il Caddyfile vi permette di specificare opzioni che si applicano globalmente. Alcune opzioni fungono da valori predefiniti; altre personalizzano i server HTTP e non si applicano a un solo sito particolare; altre ancora personalizzano il comportamento dell'[adattatore](/docs/config-adapters) Caddyfile.

La primissima parte del vostro Caddyfile può essere un **blocco delle opzioni globali**. Questo è un blocco che non ha chiavi:

```caddy
{
	...
}
```

Ce ne può essere al massimo uno e deve essere il primo blocco del Caddyfile.

Le opzioni possibili sono (cliccate su ogni opzione per saltare alla sua documentazione):

```caddy
{
	# Opzioni generali
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# Opzioni TLS
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Server Options
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# File Systems
	filesystem <name> <module> {
		<options...>
	}

	# PKI Options
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Event options
	events {
		on <event> <handler...>
	}
}
```


## Opzioni generali

<a id="general-options"></a>
##### `debug`
<a id="debug"></a>
Abilita la modalità di debug, che imposta il livello di log su `DEBUG` per il [logger predefinito](#log). Ciò rivela maggiori dettagli che possono essere utili durante la risoluzione dei problemi (ed è molto prolisso in produzione). Vi chiediamo di abilitare questa opzione prima di chiedere aiuto nei [forum della comunità](https://caddy.community). Ad esempio, in cima al vostro Caddyfile, se non avete altre opzioni globali:

```caddy
{
	debug
}
```


##### `http_port`
<a id="http-port"></a>
La porta che il server deve usare per l'HTTP.

**Solo per uso interno**; non cambia la porta HTTP per i client. Questa opzione viene tipicamente usata se all'interno della vostra rete interna avete bisogno di inoltrare la porta `80` a una porta diversa (es. `8080`) prima che raggiunga Caddy, per scopi di routing.

Predefinito: `80`


##### `https_port`
<a id="https-port"></a>
La porta che il server deve usare per l'HTTPS.

**Solo per uso interno**; non cambia la porta HTTPS per i client. Questa opzione viene tipicamente usata se all'interno della vostra rete interna avete bisogno di inoltrare la porta `443` a una porta diversa (es. `8443`) prima che raggiunga Caddy, per scopi di routing.

Predefinito: `443`


##### `default_bind`
<a id="default-bind"></a>
L'indirizzo (o gli indirizzi) di associazione (bind) predefiniti da usare per tutti i siti, se la [direttiva `bind`](/docs/caddyfile/directives/bind) non viene usata nel sito. Predefinito: vuoto, il che comporta l'associazione a tutte le interfacce.

<aside class="tip">
	Tenete presente che questo si applicherà solo ai server generati dal Caddyfile; ciò significa che il server HTTP creato dall'[HTTPS automatico](/docs/automatic-https) per i reindirizzamenti HTTP-verso-HTTPS non erediterà questi indirizzi di bind. Per ovviare a questo problema, assicuratevi di dichiarare un sito `http://` (può essere vuoto, senza direttive) in modo che esista quando il Caddyfile viene adattato, per ricevere gli indirizzi di bind.
</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
<a id="order"></a>
Assegna un ordine alle direttive degli handler HTTP. Poiché gli handler HTTP vengono eseguiti in una catena sequenziale, è necessario che vengano eseguiti nell'ordine corretto. Le direttive standard hanno [un ordine predefinito](/docs/caddyfile/directives#ordine-delle-direttive), ma se usate moduli di handler HTTP di terze parti, dovrete definire l'ordine esplicitamente usando questa opzione o inserendo la direttiva in un [blocco `route`](/docs/caddyfile/directives/route). L'ordinamento può essere descritto in modo assoluto (`first` o `last`), o relativo (`before` o `after`) rispetto a un'altra direttiva.

Ad esempio, per usare il [plugin `replace-response`](https://github.com/caddyserver/replace-response), vorrete assicurarvi che la sua direttiva sia ordinata dopo `encode` in modo che possa eseguire le sostituzioni prima che la risposta venga codificata (perché le risposte risalgono la catena degli handler, non la discendono):

```caddy
{
	order replace after encode
}
```


##### `storage`
<a id="storage"></a>
Configura il meccanismo di storage di Caddy. Il valore predefinito è [`file_system`](/docs/json/storage/file_system/). Sono disponibili molti altri [moduli di storage](/docs/json/storage/) forniti come plugin.

Ad esempio, per cambiare la posizione di storage del file system:

```caddy
{
	storage file_system /percorso/della/posizione/personalizzata
}
```

La personalizzazione del modulo di storage è solitamente necessaria quando si sincronizza lo storage di Caddy tra più istanze di Caddy per assicurarsi che tutte usino gli stessi certificati e chiavi. Consultate la [sezione dell'HTTPS automatico sullo storage](/docs/automatic-https#storage) per maggiori dettagli.


##### `storage_clean_interval`
<a id="storage-clean-interval"></a>
Ogni quanto scansionare le unità di storage per cercare asset vecchi o scaduti e rimuoverli. Queste scansioni comportano molte letture (e operazioni di elenco) sul modulo di storage, quindi scegliete un intervallo più lungo per i deployment di grandi dimensioni. Accetta [valori di durata](/docs/conventions#durate).

Lo storage verrà sempre pulito al primo avvio del processo. Successivamente, una nuova pulizia verrà avviata dopo questa durata dall'inizio della pulizia precedente, a condizione che la pulizia precedente sia terminata in meno della metà del tempo di questo intervallo (altrimenti l'avvio successivo verrà saltato).

Predefinito: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
<a id="admin"></a>
Personalizza l'[endpoint dell'API di amministrazione](/docs/api). Accetta i placeholder. Accetta [indirizzi di rete](/docs/conventions#indirizzi-di-rete).

Predefinito: `localhost:2019`, a meno che la variabile d'ambiente `CADDY_ADMIN` non sia impostata.

Se impostato su `off`, l'endpoint di amministrazione verrà disabilitato. Quando disabilitato, **le modifiche alla configurazione saranno impossibili** senza fermare e riavviare il server, poiché il [comando `caddy reload`](/docs/command-line#caddy-reload) usa l'API di amministrazione per inviare la nuova configurazione al server in esecuzione.

Ricordate di usare il flag `--address` della CLI con i [comandi](/docs/command-line) compatibili per specificare l'attuale endpoint di amministrazione, se l'indirizzo del server in esecuzione è stato cambiato rispetto a quello predefinito.

Supporta inoltre queste sotto-opzioni:

- **origins** configures l'elenco delle [origini](https://developer.mozilla.org/en-US/docs/Glossary/Origin) a cui è consentito connettersi all'endpoint.

  Viene scelto intelligentemente un valore predefinito:
  - se l'indirizzo di ascolto è di loopback (es. `localhost` o un IP di loopback, o un socket unix), allora le origini consentite sono `localhost`, `::1` e `127.0.0.1`, unite alla porta dell'indirizzo di ascolto (quindi `localhost:2019` è un'origine valida).
  - se l'indirizzo di ascolto non è di loopback, allora l'origine consentita è la stessa dell'indirizzo di ascolto.

  Se l'host dell'indirizzo di ascolto non è un'interfaccia wildcard (le wildcard includono: stringa vuota, o `0.0.0.0`, o `[::]`), allora viene eseguito il controllo dell'header `Host`. Effettivamente, ciò significa che per impostazione predefinita, l'header `Host` viene validato per essere presente in `origins`, poiché l'interfaccia è `localhost`. Ma per un indirizzo come `:2020` che ha un'interfaccia wildcard, la validazione dell'header `Host` non viene eseguita.

- **enforce_origin** forza il controllo dell'header di richiesta `Origin`. Ciò avviene implicitamente ogni volta che gli header CORS vengono inviati dal client o se il client disabilita esplicitamente il CORS con `Sec-Fetch-Mode: no-cors`. Altrimenti, questa opzione è molto utile quando l'indirizzo di ascolto è un'interfaccia wildcard (poiché `Host` non viene validato) e l'API di amministrazione è esposta alla rete internet pubblica. Abilita i controlli preflight CORS e garantisce che l'header `Origin` venga validato rispetto all'elenco `origins`. Usate questa opzione solo se state eseguendo Caddy sulla vostra macchina di sviluppo e avete bisogno di accedere all'API di amministrazione da un browser web.

Per esempio, per esporre l'API di amministrazione su una porta diversa, su tutte le interfacce &mdash; ⚠️ questa porta **non dovrebbe essere esposta pubblicamente**, altrimenti chiunque potrà controllare il vostro server; considerate di abilitare il controllo dell'origine se avete bisogno che sia pubblica:

```caddy
{
	admin :2020
}
```

Per disattivare l'API di amministrazione &mdash; ⚠️ questo rende **impossibili i ricaricamenti della configurazione** senza fermare e riavviare il server:

```caddy
{
	admin off
}
```

Per usare un [socket unix](/docs/conventions#indirizzi-di-rete) per l'API di amministrazione, consentendo il controllo degli accessi tramite i permessi dei file:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Per consentire solo le richieste con un header `Origin` corrispondente:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`
<a id="persist-config"></a>

Controlla se l'attuale configurazione JSON debba essere resa persistente nella [directory di configurazione](/docs/conventions#directory-di-configurazione), per evitare di perdere le modifiche alla configurazione eseguite tramite l'API di amministrazione. Attualmente è supportata solo l'opzione `off`. Per impostazione predefinita, la configurazione viene resa persistente.

```caddy
{
	persist_config off
}
```



##### `log`
<a id="log"></a>
Configura i logger nominati.

Il nome può essere passato per indicare un logger specifico di cui personalizzare il comportamento. Se non viene specificato alcun nome, viene modificato il comportamento del logger `default`. Potete leggere di più sul logger `default` e una spiegazione di [how logging works in Caddy](/docs/logging).

Multiple loggers con nomi diversi possono essere configurati usando `log` più volte.

Questa opzione differisce dalla [direttiva `log`](/docs/caddyfile/directives/log), che configura solo il logging delle richieste HTTP (noto anche come log degli accessi). L'opzione globale `log` condivide la sua struttura di configurazione con la direttiva (tranne che per `include` ed `exclude`) e la documentazione completa può essere trovata nella pagina della direttiva.

- **output** configures dove scrivere i log.

  Consultate la [direttiva `log`](/docs/caddyfile/directives/log#output-modules) per la documentazione completa.

- **format** descrive come codificare, o formattare, i log.

  Consultate la [direttiva `log`](/docs/caddyfile/directives/log#format-modules) per la documentazione completa.

- **level** è il livello minimo della voce da loggare.

  Predefinito: `INFO`.

  Valori possibili: `DEBUG`, `INFO`, `WARN`, `ERROR` e molto raramente `PANIC`, `FATAL`.

- **include** specifica i nomi dei log da includere in questo logger.

  Per impostazione predefinita, questo elenco è vuoto (ovvero tutti i log sono inclusi).

  Per esempio, per includere solo i log emessi dall'API di amministrazione, includereste `admin.api`.

- **exclude** specifica i nomi dei log da escludere da questo logger.

  Per impostazione predefinita, questo elenco è vuoto (ovvero nessun log è escluso).

  Per esempio, per escludere solo i log degli accessi HTTP, escludereste `http.log.access`.

Logger nomi accepted by `include` ed `exclude` dipendono dai moduli utilizzati e il modo più semplice per scoprirli è dai log precedenti.

Ecco un esempio che logga come json tutti i log degli accessi http e i log di amministrazione su stdout:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
<a id="grace-period"></a>
Definisce il periodo di grazia per lo spegnimento dei server HTTP (ad esempio durante i cambi di configurazione o quando Caddy si ferma).

Durante il periodo di grazia non vengono accettate nuove connessioni, le connessioni inattive (idle) vengono chiuse e si attende con impazienza che le connessioni attive finiscano le loro richieste. Se i client non terminano le loro richieste entro il periodo di grazia, il server verrà interrotto forzatamente per consentire il completamento del ricaricamento e liberare le risorse. Accetta [valori di durata](/docs/conventions#durate).

Per impostazione predefinita, il periodo di grazia è eterno, il che significa che le connessioni non vengono mai chiuse forzatamente.

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
<a id="shutdown-delay"></a>
Definisce una [durata](/docs/conventions#durate)
*prima* del [periodo di grazia](#grace_period) durante la quale un server che sta per essere fermato continua a operare normalmente, eccetto per il fatto che il placeholder `{http.shutting_down}` restituisce `true` e `{http.time_until_shutdown}` restituisce il tempo rimanente all'inizio del periodo di grazia.

Ciò causa un ritardo se un server viene spento come parte di un cambio di configurazione e, di fatto, pianifica il cambiamento per un momento successivo. È utile per annunciare ai controllori dello stato di salute (health checkers) l'imminente fine di questo server e per dare tempo a un bilanciatore di carico di rimuoverlo dalla rotazione; ad esempio:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Ciao, mondo!"
	}
}
```


## Opzioni TLS

<a id="tls-options"></a>
##### `auto_https`
<a id="auto-https"></a>
Configura l'[HTTPS automatico](/docs/automatic-https), che è la funzionalità che consente a Caddy di automatizzare la gestione dei certificati e i reindirizzamenti HTTP-verso-HTTPS per i vostri siti.

Ci sono alcune modalità tra cui scegliere:

- `off`: Disabilita sia l'automazione dei certificati che i reindirizzamenti HTTP-verso-HTTPS.

- `disable_redirects`: Disabilita solo i reindirizzamenti HTTP-verso-HTTPS.

- `disable_certs`: Disabilita solo l'automazione dei certificati.

- `ignore_loaded_certs`: Automatizza i certificati anche per i nomi che appaiono su certificati caricati manualmente. Utile se avete specificato un certificato usando la [direttiva `tls`](/docs/caddyfile/directives/tls) che contiene nomi (o wildcard) che volete invece gestire automaticamente.

<aside class="tip">
	Questa opzione non influisce sul protocollo predefinito di Caddy, che è sempre l'HTTPS quando l'indirizzo di un sito ha un nome di dominio valido. Ciò significa che `auto_https off` non farà sì che il vostro sito venga servito tramite HTTP, ma disabiliterà solo la gestione automatica dei certificati e i reindirizzamenti.

	Questo significa che se desiderate servire il vostro sito tramite HTTP, dovreste cambiare l'[indirizzo del vostro sito](/docs/caddyfile/concepts#indirizzi) in modo che sia preceduto da `http://` o seguito da `:80` (o l'[opzione `http_port`](#http_port)).
</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
<a id="email"></a>
Il vostro indirizzo email. Viene usato principalmente durante la creazione di un account ACME con la vostra CA ed è caldamente raccomandato nel caso in cui ci siano problemi con i vostri certificati.

<aside class="tip">
	Tenete presente che Let's Encrypt potrebbe inviarvi delle email riguardo all'imminente scadenza del vostro certificato, ma questo potrebbe trarvi in inganno perché Caddy potrebbe aver scelto di usare un emittente diverso (es. ZeroSSL) durante il rinnovo. Controllate i vostri log e/o il certificato stesso (nel vostro browser, ad esempio) per vedere quale emittente è stato usato e se la sua scadenza è ancora valida; in tal caso, potete tranquillamente ignorare l'email di Let's Encrypt.
</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
<a id="default-sni"></a>
Imposta un ServerName TLS predefinito per quando i client non usano l'SNI nel loro ClientHello.

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
<a id="fallback-sni"></a>
⚠️ <i>Sperimentale</i>

Se configurato, il valore di fallback diventa il ServerName TLS nel ClientHello se il ServerName originale non corrisponde a nessun certificato nella cache.

Gli utilizzi di questa opzione sono molto specifici; tipicamente se un client è una CDN e passa il ServerName dell'handshake a valle ma può accettare un certificato con l'hostname dell'origine al suo posto, allora impostate questo valore come l'hostname della vostra origine. Notate che Caddy deve gestire un certificato per questo nome.

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
<a id="local-certs"></a>
Fa sì che **tutti** i certificati vengano emessi internamente per impostazione predefinita, anziché tramite una CA ACME (pubblica) come Let's Encrypt. È utile come commutatore rapido negli ambienti di sviluppo.

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
<a id="skip-install-trust"></a>
Salta i tentativi di installare la root della CA locale nell'archivio di fiducia del sistema, così come negli archivi di fiducia di Java e Mozilla Firefox.

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
<a id="acme-ca"></a>
Specifica l'URL della directory della CA ACME. È caldamente raccomandato impostare questo valore sull'[endpoint di staging <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) di Let's Encrypt per test o sviluppo. Predefinito: gli endpoint di produzione di ZeroSSL e Let's Encrypt.

Si noti che una CA ACME configurata globalmente potrebbe non applicarsi a tutti i siti; vedere i [requisiti del nome host](/docs/automatic-https#requisiti-del-nome-host) per l'uso dell'emittente (o degli emittenti) ACME predefiniti.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
<a id="acme-ca-root"></a>
Specifica un file PEM che contiene un certificato root affidabile per gli endpoint della CA ACME, se non presente nell'archivio di fiducia del sistema.

```caddy
{
	acme_ca_root /percorso/della/ca/root.pem
}
```


##### `acme_eab`
<a id="acme-eab"></a>
Specifica un External Account Binding da usare per tutte le transazioni ACME.

Per esempio, con credenziali ZeroSSL fittizie:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
<a id="acme-dns"></a>
Configura il provider della [sfida ACME DNS](/docs/automatic-https#sfida-dns) da usare per tutte le transazioni ACME.

Richiede una build personalizzata di Caddy con un plugin per il vostro provider DNS.

I token che seguono il nome del provider impostano il provider nello stesso modo in cui verrebbero specificati nell'[emittente `acme` della direttiva `tls`](/docs/caddyfile/directives/tls#acme).

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
<a id="dns"></a>
Configura un provider DNS predefinito da usare quando nessun altro viene specificato localmente in un contesto rilevante. Ad esempio, se la sfida ACME DNS è abilitata ma non ha un provider DNS configurato, verrà usato questo valore predefinito globale. Viene applicato anche per la pubblicazione delle configurazioni Encrypted ClientHello (ECH).

Il vostro binario Caddy deve essere compilato con il modulo del provider DNS specificato affinché funzioni.

Esempio, usando le credenziali da una variabile d'ambiente:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Richiede Caddy 2.10 beta 1 o superiore.)


##### `ech`
<a id="ech"></a>
Abilita l'Encrypted ClientHello (ECH) utilizzando il nome (o i nomi) di dominio pubblico specificato come nome server in chiaro (SNI) negli handshake TLS. Date le giuste condizioni, l'ECH può aiutare a proteggere i nomi di dominio dei vostri siti sulla rete durante le connessioni. Caddy genererà e pubblicherà una configurazione ECH per ogni nome pubblico specificato. La pubblicazione è il modo in cui i client compatibili (come i moderni browser correttamente configurati) sanno di dover usare l'ECH per accedere ai vostri siti.

Affinché funzioni correttamente, le configurazioni ECH devono essere pubblicate nel modo in cui i client si aspettano. La maggior parte dei browser (con DNS-over-HTTPS or DNS-over-TLS abilitati) si aspetta che le configurazioni ECH siano pubblicate nei record DNS di tipo HTTPS. Caddy esegue questo tipo di pubblicazione automaticamente, ma dovete specificare un provider DNS o con la sotto-opzione `dns`, o globalmente con l'[opzione globale `dns`](#dns), e il vostro binario Caddy deve essere compilato con il modulo del provider DNS specificato (le build personalizzate sono disponibili nella nostra [pagina di download](/download)).

**Note sulla privacy:**

- È generalmente consigliabile **massimizzare la dimensione del vostro [_anonymity set_](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction)**. Pertanto, raccomandiamo solitamente alla maggior parte degli utenti di configurare *un solo* nome di dominio pubblico per proteggere tutti i propri siti.
- **Il vostro server dovrebbe essere autoritativo per il nome (o i nomi) di dominio pubblico specificato** (ovvero dovrebbero puntare al vostro server) perché Caddy otterrà un certificato per essi. Questi certificati sono vitali per aiutare i client conformi alle specifiche a connettersi in modo affidabile e sicuro con l'ECH in alcuni casi. Vengono usati solo per facilitare un handshake ECH corretto, non per i dati applicativi (i vostri siti &mdash; a meno che non definiate un sito che è uguale al vostro nome di dominio pubblico).
- Ogni circostanza può essere diversa. Raccomandiamo di consultare degli esperti per **rivedere il vostro modello di minaccia** se la posta in gioco è alta, poiché l'ECH non è una soluzione valida per tutti i casi.

Esempio che usa le credenziali da una variabile d'ambiente per la pubblicazione su nameserver parcheggiati su Cloudflare:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Ciò dovrebbe far sì che i client compatibili carichino tutti i vostri siti con `ech.example.net`, anziché con i nomi dei singoli siti esposti in chiaro.

La pubblicazione corretta richiede che i domini del vostro sito siano parcheggiati presso il provider DNS configurato e che i record possano essere modificati con le credenziali / configurazione del provider fornite.

(Richiede Caddy 2.10 beta 1 o superiore.)


##### `on_demand_tls`
<a id="on-demand-tls"></a>
Configura il [TLS on-demand](/docs/automatic-https#tls-on-demand) dove è abilitato, ma non lo abilita (per abilitarlo, usate la [sottodirettiva `on_demand` della direttiva `tls`](/docs/caddyfile/directives/tls#syntax)). Obbligatorio per l'uso in ambienti di produzione, per prevenire gli abusi.

- **ask** farà sì che Caddy effettui una richiesta HTTP all'URL fornito, chiedendo se a un dominio è consentito avere un certificato emesso.

  La richiesta ha una stringa di query `?domain=` contenente il valore del nome di dominio.

  Se l'endpoint restituisce un codice di stato `2xx`, Caddy sarà autorizzato a ottenere un certificato per quel nome. Qualsiasi altro codice di stato comporterà l'annullamento dell'emissione del certificato e l'errore dell'handshake TLS.

<aside class="tip">
	L'endpoint "ask" dovrebbe rispondere *il più velocemente possibile*, idealmente in pochi millisecondi. Tipicamente, il vostro endpoint dovrebbe eseguire una ricerca in tempo costante in un database con un indice per nome di dominio; evitate i cicli. Evitate di eseguire query DNS o altre richieste di rete.
</aside>

- **permission** consente l'uso di moduli personalizzati per determinare se un certificato debba essere emesso per un determinato nome. Il modulo deve implementare l'[interfaccia `caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission). È incluso un modulo di permessi `http`, che è ciò che usa l'opzione `ask`, e rimane come scorciatoia per compatibilità retroattiva.

- ⚠️ Le opzioni di rate limiting **interval** e **burst** erano disponibili, ma NON sono raccomandate. Rimuovetele dalla vostra configurazione se le avete ancora.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
<a id="key-type"></a>
Specifica il tipo di chiave da generare per i certificati TLS; cambiate questo valore solo se avete una specifica necessità di personalizzarlo.

I valori possibili sono: `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
<a id="cert-issuer"></a>
Definisce l'emittente (o la sorgente) dei certificati TLS.

Ciò consente di configurare gli emittenti globalmente, invece che per ogni singolo sito come si farebbe con la [sottodirettiva `issuer` della direttiva `tls`](/docs/caddyfile/directives/tls#issuer).

Può essere ripetuta se desiderate configurare più di un emittente da provare. Saranno provati nell'ordine in cui sono definiti.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
<a id="renew-interval"></a>
Ogni quanto scansionare tutti i certificati gestiti e caricati per verificarne la scadenza e attivare il rinnovo se scaduti.

Predefinito: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
<a id="cert-lifetime"></a>
Il periodo di validità da chiedere alla CA per l'emissione di un certificato.

Questo valore viene usato per calcolare il campo `notAfter` dell'ordine ACME; pertanto il sistema deve avere un orologio ragionevolmente sincronizzato. NOTA: Non tutte le CA lo supportano. Consultate la documentazione ACME della vostra CA per vedere se è consentito e quali valori possono essere usati.

Predefinito: `0` (la CA sceglie la durata, solitamente 90 giorni)

⚠️ Questa è una funzionalità sperimentale. Soggetta a cambiamenti o rimozione.

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
<a id="ocsp-interval"></a>
Ogni quanto controllare se gli [OCSP staple <img src="/old/resources/images/external-link.svg" class="external-link">](https://it.wikipedia.org/wiki/OCSP_stapling) necessitano di un aggiornamento.

Predefinito: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
<a id="ocsp-stapling"></a>
Può essere impostato su `off` per disabilitare l'OCSP stapling. Utile in ambienti dove i responder non sono raggiungibili a causa dei firewall.

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
<a id="renewal-window-ratio"></a>
Il rapporto (tra 0 e 1) della durata del certificato che deve rimanere prima che Caddy tenti di rinnovarlo. Ad esempio, se un certificato ha una durata di 90 giorni e questo rapporto è `0.3333` (il valore predefinito), allora Caddy tenterà continuamente di rinnovare il certificato quando mancano 30 giorni o meno alla scadenza. Può essere impostato anche per ogni sito con la [sottodirettiva `renewal_window_ratio` della direttiva `tls`](/docs/caddyfile/directives/tls#renewal_window_ratio).

Dovreste avere bisogno di cambiare questo valore raramente, ma può essere utile per rinnovare più tardi nella vita del certificato se la vostra CA ha tempi di emissione molto lunghi.

Tenete a mente che questo è un suggerimento, poiché gli emittenti ACME possono implementare l'[estensione ARI](https://datatracker.ietf.org/doc/rfc9773/). ARI detta una finestra in cui il client ACME (Caddy in questo caso) dovrebbe tentare il rinnovo, e tale finestra potrebbe non allinearsi con questo rapporto.

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
<a id="preferred-chains"></a>
Se la vostra CA fornisce più catene di certificati, potete usare questa opzione per specificare quale catena Caddy debba preferire. Impostate una delle seguenti opzioni:

- **smallest** dirà a Caddy di preferire le catene con il minor numero di byte.

- **root_common_name** è un elenco di uno o più nomi comuni; Caddy sceglierà la prima catena che ha una root che corrisponde ad almeno uno dei nomi comuni specificati.

- **any_common_name** è un elenco di uno o più nomi comuni; Caddy sceglierà la prima catena che ha un emittente che corrisponde ad almeno uno dei nomi comuni specificati.

Si noti che specificare `preferred_chains` come opzione globale influenzerà tutti gli emittenti se non c'è una [configurazione a livello di emittente che la sovrascrive](/docs/caddyfile/directives/tls#acme).

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


## Opzioni del server

<a id="server-options"></a>
Personalizza i [server HTTP](/docs/json/apps/http/servers/) con impostazioni che potenzialmente abbracciano più siti e che quindi non possono essere configurate correttamente nei blocchi dei siti. Queste opzioni influenzano il listener/socket o altre funzionalità sotto il livello HTTP.

Può essere specificata più di una volta con diversi valori di `listener_address` per configurare diverse opzioni per ogni server. Ad esempio, `servers :443` si applicherà solo al server che è associato all'indirizzo di ascolto `:443`. Omettendo l'indirizzo di ascolto, le opzioni si applicheranno a qualsiasi server rimanente.

<aside class="tip">
	Usate il comando [`caddy adapt`](/docs/command-line#caddy-adapt) per trovare l'indirizzo di ascolto per i server nel vostro Caddyfile.
</aside>


Per esempio, per configurare diverse opzioni per i server sulle porte `:80` e `:443`, specifichereste due blocchi `servers`:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

Quando si usa `servers`, si applicherà **solo** ai server che **appaiono effettivamente** nel vostro Caddyfile (ovvero che sono prodotti da un blocco sito). Ricordate, l'[HTTPS automatico](/docs/automatic-https) creerà un server in ascolto sulla porta `80` (o sull'[opzione `http_port`](#http_port)) per servire i reindirizzamenti HTTP->HTTPS e per risolvere la sfida ACME HTTP; ciò accade a runtime, ovvero *dopo* che l'adattatore Caddyfile ha applicato `servers`. In altri termini, questo significa che `servers` **non si applicherà** a `:80` a meno che non dichiariate esplicitamente un blocco sito come `http://` o `:80`.


<aside class="tip">
	Se state usando la [direttiva `bind`](/docs/caddyfile/directives/bind) o l'[opzione globale `default_bind`](/docs/caddyfile/options#default-bind), il `listener_address` *DEVE* corrispondere all'indirizzo di bind combinato con la porta del blocco sito, altrimenti le impostazioni non verranno applicate. Ad esempio:

```caddy
{
	# Questo NON corrisponderà al server, indirizzo di bind mancante
	servers :8080 {
		name private
	}

	# Questo funzionerà perché è una corrispondenza esatta
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`
<a id="name"></a>

Un nome personalizzato da assegnare a questo server. Solitamente utile per identificare un server dal suo nome nei log e nelle metriche. Se non impostato, Caddy lo definirà dinamicamente usando un pattern `srvX`, dove `X` parte da `0` e incrementa in base al numero di server nella configurazione.

Tenete a mente che solo ai server prodotti dai blocchi dei siti nella vostra configurazione verranno applicate le impostazioni. L'[HTTPS automatico](/docs/automatic-https) crea un server `:80` (o `http_port`) a runtime, quindi se volete rinominarlo, avrete bisogno almeno di un blocco sito `http://` vuoto.

Ad esempio:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```



##### `listener_wrappers`
<a id="listener-wrappers"></a>

Permette di configurare i [listener wrapper](/docs/json/apps/http/servers/listener_wrappers/), che possono modificare il comportamento del listener del socket. Vengono applicati nell'ordine indicato.

###### `tls`

Il listener wrapper `tls` è un listener wrapper no-op che segna dove il listener TLS dovrebbe trovarsi in una catena di listener wrapper. Dovrebbe essere usato solo se un altro listener wrapper deve essere posizionato davanti all'handshake TLS.

###### `http_redirect`

Il [`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) fornisce reindirizzamenti HTTP->HTTPS per le connessioni che arrivano sulla porta TLS come richiesta HTTP, rilevando dai primi byte che non si tratta di un handshake TLS, ma invece di una richiesta HTTP. Ciò è utilissimo quando si serve HTTPS su una porta non standard (diversa dalla `443`), poiché i browser proveranno l'HTTP a meno che lo schema non sia specificato. Deve essere posizionato *prima* del listener wrapper `tls`. Ecco un esempio:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

Il listener wrapper [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) (prima della v2.7.0 era disponibile solo tramite plugin) abilita l'analisi del [protocollo PROXY](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (reso popolare da HAProxy). Deve essere usato *prima* del listener wrapper `tls` poiché analizza i dati in chiaro all'inizio della connessione.

Siate consapevoli che i metadati dal protocollo PROXY potrebbero essere applicati alla connessione prima della valutazione dei matcher o di [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies). L'indirizzo IP del peer immediato andrà perso per le valutazioni successive.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidr...>
	deny <cidr...>
	fallback_policy <policy>
}
```

- **timeout** specifica la durata massima dell'attesa per l'header PROXY. Il valore predefinito è `5s`.

- **allow** è un elenco di intervalli CIDR di sorgenti fidate da cui ricevere gli header PROXY. I socket Unix sono fidati per impostazione predefinita e non fanno parte di questa opzione.

- **deny** è un elenco di intervalli CIDR di sorgenti fidate da cui rifiutare gli header PROXY.

- **fallback_policy** è l'azione da intraprendere se l'header PROXY proviene da un indirizzo che non è in nessuno dei due elenchi allow/deny. La policy di fallback predefinita è `ignore`. I valori accettati per `fallback_policy` sono:
	- `ignore`: indirizzo dall'header PROXY, ma accetta la connessione
	- `use`: indirizzo dall'header PROXY
	- `reject`: rifiuta la connessione quando viene inviato l'header PROXY
	- `require`: richiede alla connessione di inviare l'header PROXY, rifiuta se non presente
	- `skip`: accetta una connessione senza richiedere l'header PROXY.


Ad esempio, per un server HTTPS (che necessita del listener wrapper `tls`) che accetta gli header PROXY da un intervallo specifico di indirizzi IP e rifiuta gli header PROXY da un intervallo diverso, con un timeout di 2 secondi:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`
<a id="timeouts"></a>

- **read_body** è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo consentire per la lettura dall'upload di un client. Impostare questo valore a un tempo breve e non nullo può mitigare gli attacchi slowloris, ma può anche influenzare i client legittimamente lenti. Per impostazione predefinita non c'è timeout.

- **read_header** è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo consentire per la lettura dagli header della richiesta di un client. Per impostazione predefinita non c'è timeout.

- **write** è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo consentire per la scrittura verso un client. Si noti che impostare questo valore a un tempo piccolo quando si servono file di grandi dimensioni può influenzare negativamente i client legittimamente lenti. Per impostazione predefinita non c'è timeout.

- **idle** è un [valore di durata](/docs/conventions#durate) che imposta il tempo massimo di attesa per la richiesta successiva quando i keep-alive sono abilitati. Il valore predefinito è 5 minuti per aiutare a evitare l'esaurimento delle risorse.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`
<a id="keepalive-interval"></a>

L'intervallo con cui vengono inviati i pacchetti keepalive TCP per mantenere la connessione attiva al livello TCP quando non vengono trasmessi altri dati. Il valore predefinito è `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`
<a id="keepalive-idle"></a>

La durata per cui una connessione deve essere inattiva prima che vengano inviati i pacchetti keepalive TCP quando non vengono trasmessi altri dati. Il valore predefinito è `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`
<a id="keepalive-count"></a>

Il numero massimo di pacchetti keepalive TCP da inviare prima di considerare la connessione morta. Il valore predefinito è `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`
<a id="0rtt"></a>

Per impostazione predefinita, lo 0-RTT (early data) è abilitato per i listener QUIC (ovvero HTTP/3) per consentire ai client di inviare dati nel primo round trip dell'handshake TLS, il che può migliorare le prestazioni per le connessioni ripetute.

Potete impostare questa opzione su `off` per disabilitare lo 0-RTT per i listener QUIC. Un motivo per disabilitare lo 0-RTT è se viene usato un [matcher `remote_ip`](/docs/caddyfile/matchers#remote-ip), il che introduce una dipendenza dalla verifica dell'indirizzo remoto se il routing avviene prima che l'handshake TLS sia completato. In tal caso viene scritta una risposta HTTP 425, ma alcuni client (browser) possono comportarsi male e non eseguire un nuovo tentativo, quindi disabilitare lo 0-RTT può garantire che le risposte 425 non vengano visualizzate dagli utenti, al costo di perdere i benefici prestazionali dello 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`
<a id="trusted-proxies"></a>

Permette di configurare gli intervalli IP (CIDR) dei server proxy dai quali le richieste dovrebbero essere considerate fidate. Per impostazione predefinita, nessun proxy è fidato.

Abilitare questa opzione fa sì che per le richieste fidate l'IP *reale* del client venga analizzato dagli header HTTP (per impostazione predefinita `X-Forwarded-For`; consultate [`client_ip_headers`](#client-ip-headers) per configurare altri header). Se fidata, l'IP del client viene aggiunto ai [log degli accessi](/docs/caddyfile/directives/log), è disponibile come [placeholder](/docs/caddyfile/concepts#placeholder) `{client_ip}` e consente l'uso del [matcher `client_ip`](/docs/caddyfile/matchers#client-ip). Se la richiesta non proviene da un proxy fidato, allora l'IP del client viene impostato sull'indirizzo IP remoto della connessione in entrata diretta o all'indirizzo impostato dal [protocollo PROXY](/docs/caddyfile/options#proxy-protocol) se utilizzato. Per impostazione predefinita, gli IP negli header vengono analizzati da sinistra a destra. Consultate [`trusted_proxies_strict`](#trusted-proxies-strict) per modificare questo comportamento.

Alcuni matcher o handler possono usare lo stato di fiducia della richiesta per prendere decisioni. Ad esempio, se fidata, l'handler [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#valori-predefiniti) effettuerà il proxying e integrerà i sensibili header di richiesta `X-Forwarded-*`.

Attualmente, solo il modulo sorgente IP `static` è incluso nella distribuzione standard di Caddy, ma questo può essere [esteso](/docs/extending-caddy) con i plugin per mantenere un elenco dinamico di intervalli IP.


###### `static`

Accetta un elenco statico (invariabile) di intervalli IP (CIDR) di cui fidarsi.

Come scorciatoia, `private_ranges` può essere usato per far corrispondere tutti gli intervalli privati IPv4 e IPv6. Equivale a specificare tutti questi intervalli: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

La sintassi è la seguente:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

Ecco un esempio completo, che considera fidi un esempio di intervallo IPv4 e uno IPv6:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`
<a id="trusted-proxies-strict"></a>

Quando [`trusted_proxies`](#trusted-proxies) è abilitato, gli IP negli header (configurati da [`client_ip_headers`](#client-ip-headers)) vengono analizzati da sinistra a destra per impostazione predefinita. Il primo indirizzo IP non fidato trovato diventa l'indirizzo reale del client. Dalla v2.8, potete scegliere l'analisi da destra a sinistra di questi header con `trusted_proxies_strict`. Per impostazione predefinita, questa opzione è disabilitata per compatibilità retroattiva.

I proxy a monte come HAProxy, CloudFlare, AWS ALB, CloudFront, ecc. aggiungeranno ogni nuovo indirizzo remoto di connessione alla destra di `X-Forwarded-For`. È raccomandato abilitare `trusted_proxies_strict` quando si lavora con questi, poiché l'indirizzo IP più a sinistra potrebbe essere contraffatto dal client.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">
	Specificamente nel caso di AWS ALB, vorrete certamente abilitare questa opzione. [Secondo la loro documentazione](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15) potete identificare l'IP reale del client solo impostando la modalità XFF su `append`. Questo IP verrà aggiunto alla destra di `X-Forwarded-For` e potrà essere estratto in sicurezza solo tramite `trusted_proxies_strict`.
</aside>

##### `trusted_proxies_unix`
<a id="trusted-proxies-unix"></a>

L'opzione `trusted_proxies_unix` permette di considerare fide tutte le connessioni che provengono da socket Unix, il che è utile quando Caddy è dietro un reverse proxy (probabilmente un'altra istanza di Caddy) che si connette ad esso tramite un socket Unix (ovvero la [direttiva `bind`](/docs/caddyfile/directives/bind) è impostata su un socket unix). Questa opzione è disabilitata per impostazione predefinita.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`
<a id="client-ip-headers"></a>

In coppia con [`trusted_proxies`](#trusted-proxies), permette di configurare quali header usare per determinare l'indirizzo IP del client. Per impostazione predefinita, viene considerato solo `X-Forwarded-For`. Possono essere specificati più campi header, nel qual caso viene usato il primo valore header non vuoto.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`
<a id="metrics"></a>

Abilita la raccolta delle metriche; necessario prima dello scraping delle metriche o dell'invio con OTLP. Si noti che le metriche riducono le prestazioni sui server molto carichi. (La nostra comunità sta lavorando per migliorare questo aspetto. Partecipate!)

```caddy
{
	metrics
}
```

Potete aggiungere l'opzione `per_host` per etichettare le metriche con il nome host della metrica.

```caddy
{
	metrics {
		per_host
	}
}
```

A causa del potenziale di cardinalità infinita nell'osservare tutti i possibili host che potrebbero essere inviati dai client, Caddy registrerà solo le metriche per gli host configurati, mentre tutti gli altri host (es. attacker.com) saranno aggregati sotto l'etichetta "_other". Per forzare l'osservazione di tutti gli host, e dove il potenziale di cardinalità infinita è un rischio accettabile, aggiungete `observe_catchall_hosts`. Si noti che aggiungere `observe_catchall_hosts` non abiliterà `per_host`. Tuttavia, questa opzione è abilitata automaticamente per i server HTTPS (poiché i certificati offrono una certa protezione contro la cardinalità illimitata), ma disabilitata per i server HTTP per impostazione predefinita per prevenire attacchi di cardinalità da header Host arbitrari.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Potete aggiungere l'opzione `otlp` per inviare le stesse metriche a un endpoint OpenTelemetry Protocol (OTLP). L'esportatore viene configurato dalle variabili d'ambiente standard OpenTelemetry `OTEL_*`, come `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` e `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Ad esempio:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Consultate [Monitoraggio di Caddy con le metriche](/docs/metrics) per maggiori dettagli.

##### `trace`
<a id="trace"></a>

Logga ogni singolo handler che viene invocato. Richiede che il log emetta a livello `DEBUG` (potete farlo con l'[opzione globale `debug`](#debug)).

NOTA: Questo potrebbe loggare la configurazione dei vostri moduli handler HTTP; non abilitatela in contesti non sicuri quando ci sono dati sensibili nella configurazione.

⚠️ Questa è una funzionalità sperimentale. Soggetta a cambiamenti o rimozione.

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`
<a id="max-header-size"></a>

La dimensione massima da analizzare dagli header della richiesta HTTP di un client. Se il limite viene superato, il server risponderà con lo stato HTTP `431 Request Header Fields Too Large`. Accetta tutti i formati supportati da [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Per impostazione predefinita, il limite è `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`
<a id="enable-full-duplex"></a>

Abilita la comunicazione full-duplex per le richieste HTTP/1.

Per le richieste HTTP/1, il server HTTP di Go per impostazione predefinita consuma qualsiasi porzione non letta del corpo della richiesta prima di iniziare a scrivere la risposta, impedendo agli handler di leggere simultaneamente dalla richiesta e scrivere la risposta. Abilitare questa opzione disabilita questo comportamento e permette agli handler di continuare a leggere dalla richiesta mentre scrivono simultaneamente la risposta.

Per le richieste HTTP/2+, il server HTTP di Go permette sempre letture e risposte simultanee, quindi questa opzione non ha effetto.

Testate accuratamente con i vostri client HTTP, poiché alcuni client più vecchi potrebbero non supportare l'HTTP/1 full-duplex, il che può causare il loro deadlock. Consultate [golang/go#57786](https://github.com/golang/go/issues/57786) per maggiori info.

⚠️ Questa è una funzionalità sperimentale. Soggetta a cambiamenti o rimozione.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`
<a id="log-credentials"></a>

Per impostazione predefinita, i log degli accessi (abilitati con la [direttiva `log`](/docs/caddyfile/directives/log)) con header che contengono informazioni potenzialmente sensibili (`Cookie`, `Set-Cookie`, `Authorization` e `Proxy-Authorization`) verranno loggati come `REDACTED`.

Se desiderate che questi header *non* vengano oscurati, potete abilitare l'opzione `log_credentials`.

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`
<a id="protocols"></a>

L'elenco separato da spazi dei protocolli HTTP da supportare.

Predefinito: `h1 h2 h3`

I valori accettati sono:
- `h1` per HTTP/1.1
- `h2` per HTTP/2
- `h2c` per HTTP/2 su testo in chiaro
- `h3` per HTTP/3

Attualmente, abilitare l'HTTP/2 (incluso H2C) implica necessariamente l'abilitazione dell'HTTP/1.1 perché la libreria standard di Go non ci permette di disabilitare l'HTTP/1.1 quando usiamo il suo server HTTP. Tuttavia, sia l'HTTP/1.1 che l'HTTP/3 possono essere abilitati indipendentemente.

Si noti che l'H2C ("Cleartext HTTP/2" o "H2 su TCP") e l'HTTP/3 non sono implementati dalla libreria standard di Go, quindi alcune funzionalità o caratteristiche potrebbero essere limitate. Sconsigliamo l'abilitazione dell'H2C a meno che non sia assolutamente necessario per la vostra applicazione.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`
<a id="strict-sni-host"></a>

Abilitare questa opzione richiede che l'header `Host` di una richiesta corrisponda al valore del `ServerName` inviato dal ClientHello TLS del client, una salvaguardia necessaria quando si usa l'autenticazione del client TLS. In caso di discrepanza, viene scritta al client una risposta con stato HTTP `421 Misdirected Request`.

Questa opzione verrà attivata automaticamente se viene configurata l'[autenticazione del client](/docs/caddyfile/directives/tls#client_auth). Ciò impedisce l'aggiramento dell'autenticazione client TLS (domain fronting) che potrebbe altrimenti essere sfruttato inviando un valore SNI non protetto durante un handshake TLS, per poi inserire un dominio protetto nell'header Host dopo aver stabilito la connessione. Questo comportamento è un'impostazione predefinita sicura, ma potete disattivarlo esplicitamente con `insecure_off`; ad esempio nel caso in cui eseguiate un proxy dove il domain fronting è desiderato e l'accesso non è limitato in base all'hostname.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



## File System

<a id="file-systems"></a>
L'opzione globale `filesystem` permette di dichiarare uno o più file system che possono essere usati per l'I/O dei file.
<a id="filesystem"></a>

Ciò potrebbe permettervi di connettervi a un filesystem remoto in esecuzione nel cloud, o a un database con un'interfaccia di tipo file, o persino di leggere file incorporati all'interno del binario Caddy.

I file system sono dichiarati con un nome per identificarli. Ciò significa che potete connettervi a più di un file system dello stesso tipo, se necessario.

Per impostazione predefinita, Caddy non ha moduli di file system, quindi dovrete compilare Caddy con un plugin per il file system che volete usare.

#### Esempio

Usando un immaginario modulo di file system `custom`, potreste dichiarare due file system:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



## Opzioni PKI

<a id="pki-options"></a>
L'app PKI (Public Key Infrastructure) è la base per le funzionalità di [HTTPS locale](/docs/automatic-https#https-locale) e del [server ACME](/docs/caddyfile/directives/acme_server) di Caddy. L'app definisce le autorità di certificazione (CA) che sono in grado di firmare i certificati.
<a id="pki"></a>

L'ID della CA predefinita è `local`. Se l'ID viene omesso quando si configura la `ca`, viene assunto `local`.
<a id="ca"></a>

##### `name`
<a id="name-1"></a>
Il nome rivolto all'utente dell'autorità di certificazione.

Predefinito: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "La mia CA locale"
		}
	}
}
```

##### `root_cn`
<a id="root-cn"></a>
Il nome da inserire nel campo CommonName del certificato root.

Predefinito: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "La mia CA locale - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
<a id="intermediate-cn"></a>
Il nome da inserire nel campo CommonName dei certificati intermedi.

Predefinito: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "La mia CA locale - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
<a id="intermediate-lifetime"></a>
La [durata](/docs/conventions#durate) per cui i certificati intermedi sono validi. Questo valore **deve** essere inferiore alla durata del certificato root (`3600d` o 10 anni).

Predefinito: `7d`. Si *sconsiglia* di cambiare questo valore, a meno che non sia assolutamente necessario.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
<a id="maintenance-interval"></a>
La [durata](/docs/conventions#durate) della frequenza con cui controllare se i certificati intermedi (e root, quando applicabile) necessitano di rinnovo.

Predefinito: `10m`. Si *sconsiglia* di cambiare questo valore, a meno che non sia assolutamente necessario.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
<a id="renewal-window-ratio-1"></a>
Il rapporto (tra 0 e 1) della durata del certificato che deve rimanere prima che Caddy tenti di rinnovare i certificati. Ad esempio, se un certificato ha una durata di 1 anno e questo rapporto è `0.2` (il valore predefinito), allora Caddy tenterà continuamente di rinnovare il certificato quando mancano 73 giorni o meno alla scadenza.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
<a id="root"></a>
Una coppia di chiavi (certificato e chiave privata) da usare come root per la CA. Se non specificata, ne verrà generata e gestita una automaticamente.

- **format** è il formato in cui sono forniti il certificato e la chiave privata. Attualmente è supportato solo `pem_file`, che è il valore predefinito, quindi questo campo è opzionale.
- **cert** è il certificato. Questo dovrebbe essere il percorso di un file PEM, quando si usa il formato `pem_file`.
- **key** è la chiave privata. Questo dovrebbe essere il percorso di un file PEM, quando si usa il formato `pem_file`.

##### `intermediate`
<a id="intermediate"></a>
Una coppia di chiavi (certificato e chiave privata) da usare come intermedio per la CA. Se non specificata, ne verrà generata e gestita una automaticamente.

- **format** è il formato in cui sono forniti il certificato e la chiave privata. Attualmente è supportato solo `pem_file`, che è il valore predefinito, quindi questo campo è opzionale.
- **cert** è il certificato. Questo dovrebbe essere il percorso di un file PEM, quando si usa il formato `pem_file`.
- **key** è la chiave privata. Questo dovrebbe essere il percorso di un file PEM, quando si usa il formato `pem_file`.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /percorso/della/root.pem
				key /percorso/della/root.key
			}
			intermediate {
				format pem_file
				cert /percorso/della/intermediate.pem
				key /percorso/della/intermediate.key
			}
		}
	}
}
```


## Opzioni Eventi

<a id="event-options"></a>
I moduli Caddy emettono eventi quando accadono cose interessanti (o stanno per accadere).
<a id="events"></a>

Gli eventi includono tipicamente un payload di metadati. Il modo migliore per conoscere gli eventi e i loro payload è dalla documentazione di ogni modulo, ma potete anche vedere gli eventi e i loro payload di dati abilitando l'[opzione globale `debug`](#debug) e leggendo i log.

##### `on`
<a id="on"></a>

Associa un handler di eventi all'evento nominato. Specificate il nome del modulo dell'handler di eventi, seguito dalla sua configurazione.

Ad esempio, per eseguire un comando dopo che un certificato è stato ottenuto (richiesto un [plugin di terze parti <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec)), con una parte del payload dell'evento passata allo script tramite un placeholder:

```caddy
{
	events {
		on cert_obtained exec ./mio-script.sh {event.data.certificate_path}
	}
}
```

### Eventi

Questi eventi standard sono emessi da Caddy:

- [eventi `tls` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [eventi `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#eventi)

Anche i plugin possono emettere eventi, quindi controllate la loro documentazione per i dettagli.
