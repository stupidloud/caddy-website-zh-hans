---
title: tls (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# tls

Configura il TLS per il sito.

**Le impostazioni TLS predefinite di Caddy sono sicure. Cambiate queste impostazioni solo se avete una buona ragione e ne comprendete le implicazioni.** L'uso più comune di questa direttiva sarà specificare un indirizzo email per l'account ACME, cambiare l'endpoint della CA ACME o fornire i propri certificati.

Nota sulla compatibilità: A causa della sua natura sensibile come protocollo di sicurezza, potrebbero essere apportate regolazioni deliberate ai valori predefiniti del TLS nelle nuove release minor o patch. Vecchie versioni TLS, cifrari, funzionalità, ecc. non sicuri o obsoleti potrebbero essere rimossi in qualsiasi momento. Se il vostro deployment è estremamente sensibile ai cambiamenti, dovreste specificare esplicitamente i valori che devono rimanere costanti ed essere vigili sugli aggiornamenti. In quasi tutti i casi, raccomandiamo di usare le impostazioni predefinite.


## Sintassi

```caddy-d
tls [internal|force_automate|<email>] | [<file_cert> <file_chiave>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <valori...>
	load      <percorsi...>
	ca        <url_directory_ca>
	ca_root   <file_pem>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <nome_provider> [<parametri...>]
	propagation_timeout <durata>
	propagation_delay   <durata>
	dns_ttl             <durata>
	dns_challenge_override_domain <dominio>
	resolvers <server_dns...>
	eab       <id_chiave> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             &lt;modulo&gt;
		verifier 			   &lt;modulo&gt;
	}
	issuer          <nome_emittente>  [<parametri...>]
	get_certificate <nome_manager> [<parametri...>]
	insecure_secrets_log <file_log>
	renewal_window_ratio <rapporto>
	force_automate
}
```

- **internal** significa utilizzare la CA interna di Caddy, fidata localmente, per produrre i certificati per questo sito. Per configurare ulteriormente l'emittente [`internal`](#internal), usate la sottodirettiva [`issuer`](#issuer).

- **force_automate** costringe Caddy ad automatizzare i certificati per il sito, anche se si applicano altri certificati gestiti.

- **&lt;email&gt;** è l'indirizzo email da usare per l'account ACME che gestisce i certificati del sito. Potreste preferire l'uso dell'[opzione globale `email`](/docs/caddyfile/options#email) per configurarlo per tutti i vostri siti contemporaneamente.

<aside class="tip">
	Tenete presente che Let's Encrypt potrebbe inviarvi delle email riguardo all'imminente scadenza del vostro certificato, ma questo potrebbe trarvi in inganno perché Caddy potrebbe aver scelto di usare un emittente diverso (es. ZeroSSL) durante il rinnovo. Controllate i vostri log e/o il certificato stesso (nel vostro browser, ad esempio) per vedere quale emittente è stato usato e se la sua scadenza è ancora valida; in tal caso, potete tranquillamente ignorare l'email di Let's Encrypt.
</aside>

- **&lt;file_cert&gt;** e **&lt;file_chiave&gt;** sono i percorsi dei file PEM del certificato e della chiave privata. Specificare solo uno dei due non è valido.

- **protocols** <span id="protocols"/> specifica le versioni minima e massima del protocollo. NON cambiate questi valori a meno che non sappiate cosa state facendo. La configurazione di questo valore è raramente necessaria, perché Caddy userà sempre valori predefiniti moderni.
  
  Minimo predefinito: `tls1.2`, Massimo predefinito: `tls1.3`

- **ciphers** <span id="ciphers"/> specifica l'elenco dei nomi delle suite di cifratura in ordine decrescente di preferenza. NON cambiate questi valori a meno che non sappiate cosa state facendo. Si noti che le suite di cifratura non sono personalizzabili per TLS 1.3; inoltre non tutti i cifrari TLS 1.2 sono abilitati per impostazione predefinita. I nomi supportati sono (in ordine di preferenza della libreria standard di Go):
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> specifica l'elenco dei gruppi EC da supportare. Si raccomanda di non cambiare i valori predefiniti. I valori supportati sono:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> è l'elenco dei valori da pubblicizzare nell'[estensione ALPN <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) dell'handshake TLS.

- **load** <span id="load"/> specifica un elenco di cartelle da cui caricare i file PEM che sono pacchetti di certificato+chiave.

- **ca** <span id="ca"/> cambia l'endpoint della CA ACME. Viene usato più spesso per impostare l'[endpoint di staging di Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) durante i test, o un server ACME interno. (Per cambiare questo valore per l'intero Caddyfile, usate invece l'[opzione globale `acme_ca`](/docs/caddyfile/options).)

- **ca_root** <span id="ca_root"/> specifica un file PEM che contiene un certificato root affidabile per l'endpoint della CA ACME, se non presente nell'archivio di fiducia del sistema.

- **key_type** <span id="key_type"/> è il tipo di chiave da usare durante la generazione dei CSR. Impostate questo valore solo se avete un requisito specifico.

- **dns** <span id="dns"/> abilita la [sfida DNS](/docs/automatic-https#sfida-dns) utilizzando il plugin del provider specificato, che deve essere installato da uno dei repository [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Ogni plugin del provider potrebbe avere la propria sintassi dopo il nome; fate riferimento alla loro documentazione per i dettagli. Mantenere il supporto per ogni provider DNS è uno sforzo della comunità. [Imparate come abilitare la sfida DNS per il vostro provider sul nostro wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> è un [valore di durata](/docs/conventions#durate) che imposta il tempo massimo di attesa affinché i record DNS TXT appaiano quando si usa la sfida DNS. Impostate a `-1` per disabilitare i controlli di propagazione. Predefinito: 2 minuti.

- **propagation_delay** <span id="propagation_delay"/> è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo attendere prima di iniziare i controlli di propagazione dei record DNS TXT quando si usa la sfida DNS. Predefinito: `0` (nessuna attesa).

- **dns_ttl** <span id="dns_ttl"/> è un [valore di durata](/docs/conventions#durate) che imposta il TTL del record `TXT` usato per la sfida DNS. Raramente necessario.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> sovrascrive il dominio da usare per la sfida DNS. Questo serve per delegare la sfida a un dominio diverso.

  Potreste voler usare questa opzione se il provider DNS del vostro dominio primario non ha un [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) disponibile. Potete invece aggiungere un record `CNAME` con sottodominio `_acme-challenge` al vostro dominio primario, che punti a un dominio secondario per il quale *avete* un plugin. Questa opzione *non richiede* supporto speciale dal plugin.
  
  Quando gli emittenti ACME tentano di risolvere la sfida DNS per il vostro dominio primario, seguiranno il `CNAME` verso il vostro dominio secondario per trovare il record `TXT`.

  **Nota:** Usate il nome canonico completo dal record CNAME come valore qui &mdash; il sottodominio `_acme-challenge` non verrà anteposto automaticamente.

- **resolvers** <span id="resolvers"/> personalizza i risolutori DNS usati durante l'esecuzione della sfida DNS; questi hanno la precedenza sui risolutori di sistema o su quelli predefiniti. Se impostati qui, i risolutori si propagheranno a tutti gli emittenti di certificati configurati.

  Tipicamente si tratta di un elenco di indirizzi IP. Ad esempio, per usare [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> configura l'External Account Binding (EAB) ACME per questo sito, usando l'ID della chiave e la chiave MAC forniti dalla vostra CA.

- **on_demand** <span id="on_demand"/> abilita il [TLS on-demand](/docs/automatic-https#tls-on-demand) per gli hostname indicati negli indirizzi del blocco sito. **Avviso di sicurezza:** Farlo in produzione non è sicuro a meno che non si configuri anche l'[opzione globale `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) per mitigare gli abusi.

- **reuse_private_keys** <span id="reuse_private_keys"/> abilita il riutilizzo delle chiavi private durante il rinnovo dei certificati. Per impostazione predefinita, viene creata una nuova chiave per ogni nuovo certificato per mitigare il pinning e ridurre la portata della compromissione della chiave. Il key pinning è contrario alle migliori pratiche del settore. Questa opzione non è raccomandata a meno che non abbiate un motivo specifico per usarla; potrebbe essere rimossa in una versione futura.

- **client_auth** <span id="client_auth"/> abilita e configura l'autenticazione del client TLS:
  - **mode** <span id="mode"/> è la modalità per l'autenticazione del client. I valori ammessi sono:

    | Modalità | Descrizione |
    | --- | --- |
    | request | Chiede un certificato ai client, ma lo consente anche se non presente; non lo verifica |
    | require | Richiede ai client di presentare un certificato, ma non lo verifica |
    | verify_if_given | Chiede un certificato ai client; lo consente anche se non presente, ma lo verifica se presente |
    | require_and_verify | Richiede ai client di presentare un certificato valido che viene verificato |

    Predefinito: `require_and_verify` se il modulo `trust_pool` è fornito; altrimenti, `require`.
	
  - **trust_pool** <span id="trust_pool"/> configura la sorgente delle autorità di certificazione (CA) che forniscono i certificati rispetto ai quali validare i certificati dei client.
	
	L'autorità di certificazione usata che fornisce il pool di certificati fidi e la configurazione all'interno del segmento dipendono dal modulo della sorgente del pool di fiducia configurato. I moduli standard disponibili in Caddy sono [elencati di seguito](#trust-pool-providers). L'elenco completo dei moduli, inclusi quelli di terze parti, è indicato nella [documentazione JSON di `trust_pool`](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Possono essere usate più direttive `trusted_*` per specificare più CA o certificati foglia. I certificati client che non sono elencati come uno dei certificati foglia o firmati da una delle CA specificate verranno rifiutati in base alla **modalità**.

  - **verifier** <span id="verifier"/> abilita l'uso di un modulo verifificatore di certificati client personalizzato. Questi possono eseguire controlli di autenticazione client personalizzati, come assicurarsi che il certificato non sia revocato.

- **issuer** <span id="issuer"/> configura un emittente di certificati personalizzato, o una sorgente da cui ottenere i certificati.

  Quale emittente venga usato e le opzioni che seguono in questo segmento dipendono dai [moduli emittente](#issuers) disponibili. Alcune delle altre sottodirettive come `ca` e `dns` sono in realtà scorciatoie per la configurazione dell'emittente `acme` (e questa sottodirettiva è stata aggiunta successivamente), quindi specificare questa direttiva insieme ad alcune delle altre è fonte di confusione e pertanto proibito.
  
  Questa sottodirettiva può essere specificata più volte per configurare emittenti multipli e ridondanti; se uno fallisce nell'emettere un certificato, verrà provato il successivo.

- **get_certificate** <span id="get_certificate"/> abilita l'ottenimento dei certificati da un [modulo manager](#certificate-managers) al momento dell'handshake.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> abilita il logging dei segreti TLS in un file. Questo è noto anche come `SSLKEYLOGFILE`. Utilizza il formato key log di NSS, che può essere analizzato da Wireshark o altri strumenti. ⚠️ **Avviso di sicurezza:** Questo non è sicuro in quanto consente ad altri programmi o strumenti di decriptare le connessioni TLS, compromettendo quindi completamente la sicurezza. Tuttavia, questa capacità può essere utile per il debugging e la risoluzione dei problemi.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> è un rapporto tra 0 e 1 che determina la durata residua del certificato prima che Caddy tenti di rinnovarlo. Ad esempio, se un certificato ha una durata di 90 giorni, e questo rapporto è `0.3333` (il valore predefinito), allora Caddy tenterà continuamente di rinnovare il certificato quando mancano 30 giorni o meno alla scadenza. Può essere impostato anche globalmente con l'[opzione globale `renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio).

  Dovreste avere bisogno di cambiare questo valore raramente, ma può essere utile per rinnovare più tardi nella vita del certificato se la vostra CA ha tempi di emissione molto lunghi.

  Tenete a mente che questo è un suggerimento, poiché gli emittenti ACME possono implementare l'[estensione ARI](https://datatracker.ietf.org/doc/rfc9773/). ARI detta una finestra in cui il client ACME (Caddy in questo caso) dovrebbe tentare il rinnovo, e tale finestra potrebbe non allinearsi con questo rapporto.

- **force_automate** è lo stesso di specificarlo inline (vedi sopra).

### Trust Pool Providers

Questi sono i provider di pool di fiducia standard che possono essere usati nella sottodirettiva `trust_pool`:

#### inline

Il modulo `inline` analizza i certificati root fidi elencati direttamente nel Caddyfile in formato DER codificato in base64. La direttiva `trust_der` può essere ripetuta più volte.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> è un certificato della CA codificato in base64 DER rispetto al quale validare i certificati dei client.

#### file

Il modulo `file` legge i certificati root fidi dai file PEM su disco. La direttiva `pem_file` può accettare più percorsi di file sulla stessa riga e può essere ripetuta più volte.

```caddy-d
... file [<file_pem>...] {
	pem_file <file_pem>...
}
```

- **pem_file** <span id="pem_file"/> è un percorso verso un file di certificato CA in formato PEM rispetto al quale validare i certificati dei client.

#### pki_root

Il modulo `pki_root` ottiene i certificati *root* e fidi dall'autorità di certificazione definita nell'[app PKI](/docs/caddyfile/options#opzioni-pki). La direttiva `authority` può accettare più autorità contemporaneamente e può essere ripetuta più volte.

```caddy-d
... pki_root [<nome_ca>...] {
	authority <nome_ca>...
}
```

- **authority** <span id="authority"/> è il nome dell'autorità di certificazione configurata nell'app PKI.

#### pki_intermediate

Il modulo `pki_intermediate` ottiene i certificati *intermedi* e fidi dall'autorità di certificazione definita nell'[app PKI](/docs/caddyfile/options#opzioni-pki). La direttiva `authority` può accettare più autorità contemporaneamente e può essere ripetuta più volte.

```caddy-d
... pki_intermediate [<nome_ca>...] {
	authority <nome_ca>...
}
```

- **authority** <span id="authority"/> è il nome dell'autorità di certificazione configurata nell'app PKI.

#### storage

Il modulo `storage` estrae i certificati root fidi dallo [storage](/docs/caddyfile/options#storage) di Caddy. La direttiva `authority` può accettare più autorità contemporaneamente e può essere ripetuta più volte.

```caddy-d
... storage [<chiavi_storage>...] {
	storage <modulo_storage>
	keys    <chiavi_storage>...
}
```

- **storage** <span id="storage"/> è un modulo di storage opzionale da usare. Se non specificato, verrà usato il modulo di storage predefinito. Se specificato, può essere indicato solo una volta.

- **keys** <span id="keys"/> è l'elenco delle chiavi di storage presso le quali sono memorizzati i file PEM dei certificati. La direttiva accetta più valori sulla stessa riga e può essere specificata più volte.

#### http

Il modulo `http` ottiene i certificati fidi dagli endpoint HTTP. La direttiva `endpoints` può accettare più endpoint contemporaneamente e può essere ripetuta più volte.

```caddy-d
... http [<endpoint...>] {
	endpoints   <endpoint...>
	tls         <config_tls>
}
```

- **endpoints** <span id="endpoints"/> è l'elenco di endpoint HTTP dai quali ottenere i certificati. La direttiva accetta più valori sulla stessa riga e può essere specificata più volte.

- **tls** <span id="tls"/> è una configurazione TLS opzionale da usare quando ci si connette all'endpoint HTTP. L'analisi del segmento è definita nella [sezione seguente](#tls-1).

##### TLS

```caddy-d
... {
	ca                    <modulo_ca>
	insecure_skip_verify
	handshake_timeout     <durata>
	server_name           &lt;nome&gt;
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> è una direttiva opzionale per definire il provider del pool di fiducia. La configurazione segue lo stesso comportamento di [`trust_pool`](#trust-pool). Se specificata, può essere indicata solo una volta.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> disattiva la verifica dell'handshake TLS, rendendo la connessione insicura e vulnerabile agli attacchi man-in-the-middle. *Non usare in produzione.* La verifica viene eseguita rispetto alle autorità di certificazione considerate fide dal sistema o come determinato dalla direttiva [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> è la [durata](/docs/conventions#durate) massima di attesa per il completamento dell'handshake TLS. Predefinito: nessun timeout.

- **server_name** <span id="server_name"/> imposta il nome del server usato durante la verifica del certificato ricevuto nell'handshake TLS. Per impostazione predefinita, verrà usata la parte host dell'indirizzo dell'upstream.

- **renegotiation** <span id="renegotiation"/> imposta il livello di rinegoziazione TLS. La rinegoziazione TLS è l'atto di eseguire handshake successivi dopo il primo. Il livello può essere uno di:
  - `never` (predefinito) disabilita la rinegoziazione.
  - `once` permette a un server remoto di richiedere la rinegoziazione una volta per connessione.
  - `freely` permette a un server remoto di richiedere ripetutamente la rinegoziazione.

### Verificatori

I moduli verificatori di certificati client vengono eseguiti dopo aver validato che sono stati emessi da un'autorità di certificazione fidata, se `trust_pool` è configurato. L'unico verificatore attualmente incluso nella distribuzione standard di Caddy è `leaf`.

#### Leaf

Il verificatore `leaf` controlla se il certificato del client è uno dei certificati appartenenti a un set definito di certificati permessi. Il set di certificati viene caricato utilizzando i moduli [loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders).

##### Loader

La distribuzione standard di Caddy include 4 loader, 3 dei quali sono disponibili nel Caddyfile.

###### File

Il loader `file` carica il set di certificati dai file PEM specificati.

```caddy-d
... file <file_pem...>
```

###### Folder

Il loader `folder` attraversa ricorsivamente le directory indicate alla ricerca di file PEM da caricare come certificati client accettati.

```caddy-d
... folder <cartelle...>
```

###### PEM

Il loader `pem` accetta i certificati inseriti inline nel Caddyfile in formato PEM.

```caddy-d
... pem <stringhe_pem...>
```

### Emittenti

Questi emittenti sono forniti di serie con la direttiva `tls`:

#### acme

Ottiene i certificati utilizzando il protocollo ACME. Si noti che `acme` è un emittente predefinito (utilizzando Let's Encrypt), quindi configurarlo esplicitamente è solitamente non necessario.

```caddy-d
... acme [<url_directory>] {
	dir      <url_directory>
	test_dir <url_directory_test>
	email    <email>
	timeout  <durata>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <porta>
	alt_tlsalpn_port <porta>
	eab <id_chiave> <mac_key>
	trusted_roots <file_pem...>
	dns [<nome_provider> [<opzioni>]]
	propagation_timeout <durata>
	propagation_delay   <durata>
	dns_ttl             <durata>
	dns_challenge_override_domain <dominio>
	resolvers <server_dns...>
	preferred_chains [smallest] {
		root_common_name <nomi_comuni...>
		any_common_name  <nomi_comuni...>
	}
	profile &lt;nome&gt;
}
```

- **dir** <span id="dir"/> è l'URL della directory della CA ACME.
  
  Predefinito: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> è una directory di fallback opzionale da usare quando si riprovano le sfide; se tutte le sfide falliscono, questo endpoint verrà usato durante i tentativi successivi; utile se una CA ha un endpoint di staging dove si vogliono evitare i rate limit del loro endpoint di produzione.

  Predefinito: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> è l'indirizzo email di contatto dell'account ACME.

- **timeout** <span id="timeout"/> è un [valore di durata](/docs/conventions#durate) che imposta quanto attendere prima di mandare in timeout un'operazione ACME.

- **disable_http_challenge** <span id="disable_http_challenge"/> disabiliterà la sfida HTTP.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> disabiliterà la sfida TLS-ALPN.

- **alt_http_port** <span id="alt_http_port"/> è una porta alternativa su cui servire la sfida HTTP; deve avvenire sulla porta 80, quindi dovete inoltrare i pacchetti verso questa porta alternativa.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> è una porta alternativa su cui servire la sfida TLS-ALPN; deve avvenire sulla porta 443, quindi dovete inoltrare i pacchetti verso questa porta alternativa.

- **eab** <span id="eab"/> specifica un External Account Binding che potrebbe essere richiesto da alcune CA ACME.

- **trusted_roots** <span id="trusted_roots"/> sono uno o più certificati root (come nomi di file PEM) da considerare affidabili quando ci si connette al server della CA ACME.

- **dns** <span id="dns"/> configura la sfida DNS. Qui deve essere configurato un provider, a meno che l'[opzione globale `dns`](/docs/caddyfile/options#dns) non specifichi un modulo provider DNS applicabile globalmente.

- **propagation_timeout** <span id="propagation_timeout"/> è un [valore di durata](/docs/conventions#durate) che imposta il tempo massimo di attesa affinché i record DNS TXT appaiano quando si usa la sfida DNS. Impostate a `-1` per disabilitare i controlli di propagazione. Predefinito: 2 minuti.

- **propagation_delay** <span id="propagation_delay"/> è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo attendere prima di iniziare i controlli di propagazione dei record DNS TXT quando si usa la sfida DNS. Predefinito: 0 (nessuna attesa).

- **dns_ttl** <span id="dns_ttl"/> è un [valore di durata](/docs/conventions#durate) che imposta il TTL del record `TXT` usato per la sfida DNS. Raramente necessario.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> sovrascrive il dominio da usare per la sfida DNS. Questo serve per delegare la sfida a un dominio diverso.

  Potreste voler usare questa opzione se il provider DNS del vostro dominio primario non ha un [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) disponibile. Potete invece aggiungere un record `CNAME` con sottodominio `_acme-challenge` al vostro dominio primario, che punti a un dominio secondario per il quale *avete* un plugin. Questa opzione *non richiede* supporto speciale dal plugin.
  
  Quando gli emittenti ACME tentano di risolvere la sfida DNS per il vostro dominio primario, seguiranno il `CNAME` verso il vostro dominio secondario per trovare il record `TXT`.

  **Nota:** Usate il nome canonico completo dal record CNAME come valore qui &mdash; il sottodominio `_acme-challenge` non verrà anteposto automaticamente.

- **resolvers** <span id="resolvers"/> personalizza i risolutori DNS usati durante l'esecuzione della sfida DNS; questi hanno la precedenza sui risolutori di sistema o su quelli predefiniti. Se impostati qui, i risolutori si propagheranno a tutti gli emittenti di certificati configurati.

  Tipicamente si tratta di un elenco di indirizzi IP. Ad esempio, per usare [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> specifica quali catene di certificati Caddy dovrebbe preferire; utile se la vostra CA fornisce più catene. Usate una delle seguenti opzioni:
	- **smallest** <span id="smallest"/> dirà a Caddy di preferire le catene con il minor numero di byte.

	- **root_common_name** <span id="root_common_name"/> è un elenco di uno o più nomi comuni; Caddy sceglierà la prima catena che ha una root che corrisponde ad almeno uno dei nomi comuni specificati.

	- **any_common_name** <span id="any_common_name"/> è un elenco di uno o più nomi comuni; Caddy sceglierà la prima catena che ha un emittente che corrisponde ad almeno uno dei nomi comuni specificati.

- **profile** è il nome del [profilo ACME](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) da applicare quando si ordinano i certificati. Se ne specificate uno, tutte le CA configurate (implicitamente o meno) devono supportare questo profilo. Fate riferimento alla documentazione della vostra CA per i profili disponibili; alcune CA potrebbero non supportare i profili. SPERIMENTALE: La specifica del profilo ACME è ancora in stato di bozza, quindi questa funzione/funzionalità è soggetta a modifiche o rimozione.


#### zerossl

Ottiene i certificati utilizzando l'[API proprietaria di emissione certificati di ZeroSSL](https://zerossl.com/documentation/api/). È richiesta una chiave API e potrebbe essere richiesto un pagamento a seconda del vostro piano. Si noti che questo emittente è distinto dall'[endpoint ACME di ZeroSSL](https://zerossl.com/documentation/acme/). Per usare l'endpoint ACME di ZeroSSL, usate l'emittente `acme` descritto sopra configurato con l'endpoint della directory ACME di ZeroSSL.

```caddy-d
... zerossl <chiave_api> {
	validity_days <giorni>
	alt_http_port <porta>
	dns <nome_provider> ...
	propagation_delay <durata>
	propagation_timeout <durata>
	resolvers <elenco...>
	dns_ttl <durata>
}
```

- **validity_days** <span id="validity_days"/> definisce la durata del certificato. Solo alcuni valori sono accettati; consultate la [documentazione di ZeroSSL](https://zerossl.com/documentation/api/create-certificate/) per i dettagli.
<!--   
  Predefinito: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> è la porta da usare per completare la validazione HTTP di ZeroSSL, se non è la porta 80.
- **dns** <span id="zerossl_dns"/> abilita il metodo di validazione CNAME utilizzando il provider DNS nominato con la configurazione data per la predisposizione automatica dei record. Il plugin del provider DNS deve essere installato dai repository [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Ogni plugin del provider potrebbe avere la propria sintassi dopo il nome; fate riferimento alla loro documentazione per i dettagli. Mantenere il supporto per ogni provider DNS è uno sforzo della comunità.
- **propagation_delay** <span id="zerossl_propagation_delay"/> è quanto tempo attendere prima di controllare la propagazione del record CNAME.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> è quanto tempo attendere per la propagazione del record CNAME prima di rinunciare.
- **resolvers** <span id="zerossl_resolvers"/> definisce risolutori DNS personalizzati da usare durante il controllo della propagazione del record CNAME.
- **dns_ttl** <span id="zerossl_dns_ttl"/> configura il TTL per i record CNAME creati come parte del processo di validazione.



#### internal

Ottiene i certificati da un'autorità di certificazione interna.

```caddy-d
... internal {
	ca       &lt;nome&gt;
	lifetime <durata>
	sign_with_root
}
```

- **ca** <span id="ca"/> è il nome della CA interna da usare. Predefinito: `local`. Consultate le [opzioni globali dell'app PKI](/docs/caddyfile/options#opzioni-pki) per configurare la CA `local`, o per creare CA alternative.

  Per impostazione predefinita, il certificato della root CA ha una durata di `3600d` (10 anni) e quello intermedio una durata di `7d` (7 giorni).

  Caddy tenterà di installare il certificato della root CA nell'archivio di fiducia del sistema, ma l'operazione potrebbe fallire quando Caddy viene eseguito come utente non privilegiato, o all'interno di un container Docker. In tal caso, il certificato della root CA dovrà essere installato manualmente, o utilizzando il comando [`caddy trust`](/docs/command-line#caddy-trust), o [copiandolo fuori dal container](/docs/running#utilizzo).

- **lifetime** <span id="lifetime"/> è un [valore di durata](/docs/conventions#durate) che imposta il periodo di validità per i certificati foglia emessi internamente. Predefinito: `12h`. Si SCONSIGLIA di cambiare questo valore, a meno che non sia assolutamente necessario. Deve essere inferiore alla durata dell'intermedio.

- **sign_with_root** <span id="sign_with_root"/> forza l'uso della root come emittente invece dell'intermedio. Questo NON È RACCOMANDATO e dovrebbe essere usato solo quando i dispositivi/client non validano correttamente le catene di certificati (molto raro).



### Certificate Managers

I moduli manager di certificati sono distinti dai moduli emittenti in quanto l'uso dei moduli manager implica che uno strumento o servizio esterno stia mantenendo rinnovato il certificato, mentre un modulo emittente implica che Caddy stesso stia gestendo il certificato. (I moduli emittenti prendono come input una Certificate Signing Request (CSR), mentre i moduli manager di certificati prendono come input un TLS ClientHello.)

Questi moduli manager sono forniti di serie con la direttiva `tls`:

#### tailscale

Ottiene i certificati da un'istanza [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) in esecuzione locale. L'[HTTPS deve essere abilitato nel vostro account Tailscale](https://tailscale.com/kb/1153/enabling-https/) (o nel vostro server open source [Headscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)); inoltre il processo Caddy deve essere eseguito come root oppure dovete configurare `tailscaled` per fornire al vostro utente Caddy il [permesso di recuperare i certificati](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).

_**NOTA: Questo è solitamente non necessario!** Caddy usa automaticamente Tailscale per tutti i domini `*.ts.net` senza alcuna configurazione extra._

```caddy-d
get_certificate tailscale  # spesso non necessario!
```


#### http

Ottiene i certificati effettuando una richiesta HTTP(S). La risposta deve avere un codice di stato `200` e il corpo deve contenere una catena PEM che include il certificato completo (con intermedi) così come la chiave privata.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> è l'URL completo al quale effettuare la richiesta. È caldamente consigliato che si tratti di un endpoint locale per ragioni prestazionali. L'URL verrà integrato con i seguenti parametri della stringa di query: 

  - `server_name`: valore SNI
  - `signature_schemes`: elenco separato da virgole di ID esadecimali degli algoritmi di firma
  - `cipher_suites`: elenco separato da virgole di ID esadecimali delle suite di cifratura
  - `local_ip`: indirizzo IP al quale il client ha effettuato la richiesta



## Esempi

Uso di un certificato e di una chiave personalizzati. Il certificato dovrebbe avere dei [SAN](https://it.wikipedia.org/wiki/Subject_Alternative_Name) che corrispondano all'indirizzo del sito:

```caddy
example.com {
	tls cert.pem key.pem
}
```

Uso di certificati [fidi localmente](/docs/automatic-https#https-locale) per tutti gli host nell'attuale blocco sito, anziché certificati pubblici tramite ACME / Let's Encrypt (utile in ambienti di sviluppo):

```caddy
example.com {
	tls internal
}
```

Uso di certificati fidi localmente, ma gestiti [On-Demand](/docs/automatic-https#tls-on-demand) anziché in background. Questo vi permette di puntare qualsiasi dominio alla vostra istanza di Caddy e far sì che essa predisponga automaticamente un certificato per voi. Questo NON DOVREBBE essere usato se la vostra istanza di Caddy è accessibile pubblicamente, poiché un attaccante potrebbe usarla per esaurire le risorse del vostro server:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Uso di opzioni personalizzate per la CA interna (non è possibile usare la scorciatoia `tls internal`):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Specifica di un indirizzo email per il vostro account ACME (ma se viene usato un solo indirizzo email per tutti i siti, raccomandiamo invece l'[opzione globale `email`](/docs/caddyfile/options#email)):

```caddy
example.com {
	tls vostro@email.com
}
```

Abilitazione della sfida DNS per un dominio gestito su Cloudflare con le credenziali dell'account in una variabile d'ambiente. Questo sblocca il supporto ai certificati wildcard, che richiedono la validazione DNS:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Ottenimento della catena di certificati via HTTP, invece di lasciare che sia Caddy a gestirla. Si noti che [`get_certificate`](#certificate-managers) implica che [`on_demand`](#on_demand) sia abilitato, recuperando i certificati tramite un modulo anziché innescare l'emissione ACME:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Abilitazione dell'autenticazione client TLS e richiesta ai client di presentare un certificato valido che venga verificato rispetto a tutte le CA fornite tramite il provider `file` di [`trust_pool`](#trust_pool):

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
