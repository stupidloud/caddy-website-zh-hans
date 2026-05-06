---
title: php_fastcgi (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Un'opinione direttiva che effettua il proxy delle richieste verso un server PHP FastCGI come php-fpm.

- [Sintassi](#sintassi)
- [Forma estesa](#expanded-form)
  - [Spiegazione](#explanation)
- [Esempi](#examples)

Il [`reverse_proxy`](reverse_proxy) di Caddy è in grado di servire qualsiasi applicazione FastCGI, ma questa direttiva è studiata specificamente per le app PHP. Questa direttiva è un comodo scorciatoia, che sostituisce una [configurazione più lunga](#expanded-form).

Si aspetta che qualsiasi `index.php` nella root del sito agisca come router. Se ciò non è desiderato, riconfigurate la [sottodirettiva `try_files`](#try_files) per modificare il comportamento predefinito di riscrittura, oppure prendete la [forma estesa](#expanded-form) come base e personalizzatela secondo le vostre necessità.

In aggiunta alle sottodirettive elencate di seguito, questa direttiva supporta anche tutte le sottodirettive di [`reverse_proxy`](reverse_proxy#sintassi). Ad esempio, potete abilitare il bilanciamento del carico e i controlli sanitari.

**La maggior parte delle moderne app PHP funziona bene senza sottodirettive extra o personalizzazioni.** Le sottodirettive vengono solitamente usate solo in alcuni casi limite o con app PHP legacy.

## Sintassi

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **&lt;php-fpm_gateways...&gt;** sono gli [indirizzi](/docs/conventions#indirizzi-di-rete) dei server FastCGI. Tipicamente, o un socket TCP o un file di socket unix.

- **root** <span id="root"/> imposta la cartella radice per il sito. Si raccomanda di usare sempre la [direttiva `root`](root) in combinazione con `php_fastcgi`, ma sovrascrivere questo valore può essere utile quando il vostro upstream PHP-FPM usa una root diversa da Caddy (vedi [un esempio](#docker)). Il valore predefinito è quello della [direttiva `root`](root) se usata, altrimenti è la directory di lavoro corrente di Caddy.

- **split** <span id="split"/> imposta le sottostringhe per suddividere l'URI in due parti. La prima sottostringa corrispondente verrà usata per separare la "path info" dal percorso. Al primo pezzo viene aggiunto il suffisso della sottostringa corrispondente e verrà considerato come il nome effettivo della risorsa (script CGI). Il secondo pezzo verrà impostato come PATH_INFO affinché lo script CGI possa usarlo. Predefinito: `.php`

- **index** <span id="index"/> specifica il nome del file da trattare come file index della directory. Questo influenza il matcher del file nella [forma estesa](#expanded-form). Predefinito: `index.php`. Può essere impostato su `off` per disabilitare il fallback di riscrittura verso `index.php` quando un file corrispondente non viene trovato.

- **try_files** <span id="try_files"/> specifica una sovrascrittura per la riscrittura try-files predefinita. Consultate la [direttiva `try_files`](try_files) per i dettagli. Predefinito: `{path} {path}/index.php index.php`.

- **env** <span id="env"/> imposta una variabile d'ambiente extra con il valore fornito. Può essere specificato più di una volta per più variabili d'ambiente. Per impostazione predefinita, tutte le variabili d'ambiente FastCGI rilevanti sono già impostate (inclusi gli header HTTP), ma potete aggiungere o sovrascrivere variabili secondo necessità. 

- **resolve_root_symlink** <span id="resolve_root_symlink"/> quando la directory [`root`](#root) è un collegamento simbolico (symlink), abilita la risoluzione al suo valore effettivo. Questo viene a volte usato come strategia di distribuzione, semplicemente scambiando il symlink per puntare alla nuova versione in un'altra directory. Disabilitato per impostazione predefinita per evitare chiamate di sistema ripetute.

- **capture_stderr** <span id="capture_stderr"/> abilita la cattura e il logging di qualsiasi messaggio inviato dal server fastcgi upstream su `stderr`. Il logging viene eseguito a livello `WARN` per impostazione predefinita. Se la risposta ha uno stato `4xx` o `5xx`, verrà invece usato il livello `ERROR`. Per impostazione predefinita, lo `stderr` viene ignorato.

- **dial_timeout** <span id="dial_timeout"/> è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo attendere durante la connessione al socket dell'upstream. Predefinito: `3s`.

- **read_timeout** <span id="read_timeout"/> è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo attendere durante la lettura dall'upstream FastCGI. Predefinito: nessun timeout.

- **write_timeout** <span id="write_timeout"/> è un [valore di durata](/docs/conventions#durate) che imposta quanto tempo attendere durante l'invio all'upstream FastCGI. Predefinito: nessun timeout.


Poiché questa direttiva è un wrapper opinionato attorno a un reverse proxy, potete usare qualsiasi sottodirettiva di [`reverse_proxy`](reverse_proxy#sintassi) per personalizzarla.


## Forma estesa

<a id="expanded-form"></a>
La direttiva `php_fastcgi` (senza sottodirettive) è identica alla seguente configurazione. La maggior parte delle moderne app PHP funziona bene con questo preset. Se la vostra non lo fa, sentitevi liberi di prendere spunto da qui e personalizzarlo secondo necessità anziché usare la scorciatoia `php_fastcgi`.

```caddy-d
route {
	# Aggiunge lo slash finale per le richieste verso directory
	# Questa ridirezione è automaticamente disabilitata se "{http.request.uri.path}/index.php"
	# non appare nell'elenco try_files
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Se il file richiesto non esiste, prova i file index e assumi che index.php esista sempre
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# Effettua il proxy dei file PHP verso il responder FastCGI
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

### Spiegazione

<a id="explanation"></a>
- La prima sezione si occupa della canonizzazione del percorso della richiesta. L'obiettivo è garantire che le richieste che mirano a una directory su disco abbiano effettivamente lo slash finale `/` aggiunto al percorso della richiesta, in modo che un solo URL sia valido per le richieste verso tale directory.

  Questa canonizzazione avviene solo se la sottodirettiva `try_files` contiene `{path}/index.php` (il valore predefinito).

  Questo viene eseguito utilizzando un matcher di richiesta che corrisponde solo alle richieste che *non* terminano con uno slash, e che si mappano su una directory su disco che contiene un file `index.php`, e se corrisponde, esegue un reindirizzamento HTTP 308 con lo slash finale aggiunto. Quindi, per esempio, reindirizzerebbe una richiesta con percorso `/foo` a `/foo/` (aggiungendo un `/`, per canonizzare il percorso alla directory), se `/foo/index.php` esiste su disco.

- La sezione successiva si occupa di eseguire le riscritture del percorso in base all'esistenza o meno di un file corrispondente su disco. Questo ha anche l'effetto collaterale di ricordare la parte del percorso dopo `.php` (se il percorso della richiesta conteneva `.php`). Questo è importante affinché Caddy imposti correttamente le variabili d'ambiente FastCGI.

  - Per prima cosa, controlla se `{path}` è un file esistente su disco. In tal caso, riscrive verso quel percorso. Questo essenzialmente interrompe il resto e assicura che le richieste verso file che *esistono* su disco non vengano riscritte in altro modo (vedi passaggi successivi sotto). Quindi, se per esempio avete un file `/js/app.js` su disco, allora la richiesta verso quel percorso rimarrà invariata.

  - In secondo luogo, controlla se `{path}/index.php` è un file esistente su disco. In tal caso, riscrive verso quel percorso. Per le richieste verso una directory come `/foo/` cercherà quindi `/foo//index.php` (che viene normalizzato in `/foo/index.php`), e riscriverà la richiesta verso quel percorso se esiste. Questo comportamento è a volte utile se state eseguendo un'altra app PHP in una sottodirectory della vostra webroot.

  - Infine, riscriverà sempre verso `index.php` (esiste quasi sempre per le moderne app PHP). Questo permette alla vostra app PHP di gestire qualsiasi richiesta per percorsi che *non* si mappano su file su disco, usando lo script `index.php` come suo punto di ingresso.

- E infine, l'ultima sezione è quella che effettivamente esegue il proxy della richiesta verso il vostro servizio PHP FastCGI (o PHP-FPM) per eseguire effettivamente il vostro codice PHP. Il matcher di richiesta corrisponderà solo alle richieste che terminano con `.php`, quindi, qualsiasi file che *non* è uno script PHP e che *esiste* su disco, *non* verrà gestito da questa direttiva e passerà oltre.

La direttiva `php_fastcgi` solitamente non è sufficiente da sola. Dovrebbe essere quasi sempre accoppiata con la [direttiva `root`](root) per impostare la posizione dei vostri file su disco (per le moderne app PHP, questa potrebbe essere `/var/www/html/public`, dove la directory `public` è quella che contiene il vostro `index.php`), e con la [direttiva `file_server`](file_server) per servire i vostri file statici (i vostri JS, CSS, immagini, ecc.) che non vengono altrimenti gestiti da questa direttiva e che sono passati oltre.



## Esempi

<a id="examples"></a>
Reverse proxy per tutte le richieste PHP verso un responder FastCGI in ascolto su `127.0.0.1:9000`:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

Lo stesso, ma solo per le richieste sotto `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

Quando si usa PHP-FPM in ascolto tramite un socket unix:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

La [direttiva `root`](root) è quasi sempre usata per specificare la directory contenente gli script PHP, e la [direttiva `file_server`](file_server) per servire i file statici:

```caddy
example.com {
	root * /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<a id="docker"></a>
Quando servite più app PHP con Caddy, la vostra webroot per ogni app deve essere diversa in modo che Caddy possa leggere e servire i vostri file statici separatamente e rilevare se esistono file PHP.

Se state usando Docker, spesso i vostri container PHP-FPM avranno i file montati sulla stessa root. In tal caso, la soluzione è montare i file nel vostro container Caddy in directory diverse, quindi usare la [sottodirettiva `root`](#root) per impostare la root per ogni container:

```caddy
app1.example.com {
	root * /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root * /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Per un sito PHP che non usa `index.php` come punto di ingresso, potete ripiegare sulla generazione di un errore `404` al suo posto. L'errore può essere intercettato e gestito con la [direttiva `handle_errors`](handle_errors):

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
