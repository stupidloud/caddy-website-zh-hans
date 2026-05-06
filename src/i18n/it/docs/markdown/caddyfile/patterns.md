---
title: Pattern comuni del Caddyfile
---

# Pattern comuni del Caddyfile

Questa pagina mostra alcune configurazioni del Caddyfile complete e minimali per i casi d'uso più comuni. Possono essere utili punti di partenza per i vostri documenti Caddyfile.

Queste non sono soluzioni "chiavi in mano"; dovrete personalizzare i nomi di dominio, le porte/socket, i percorsi delle directory, ecc. Sono intese per illustrare alcuni dei pattern di configurazione più comuni.

- [Server di file statici](#static-file-server)
- [Reverse proxy](#reverse-proxy)
- [PHP](#php)
- [Reindirizzamento sottodominio `www.`](#redirect-www-subdomain)
- [Slash finali](#trailing-slashes)
- [Certificati wildcard](#wildcard-certificates)
- [Single-page app (SPA)](#single-page-apps-spas)
- [Caddy che effettua il proxy verso un altro Caddy](#caddy-proxying-to-another-caddy)


## Server di file statici

<a id="static-file-server"></a>
```caddy
example.com {
	root * /var/www
	file_server
}
```

Come al solito, la prima riga è l'indirizzo del sito. La [direttiva `root`](/docs/caddyfile/directives/root) specifica il percorso della radice del sito (il `*` serve a far corrispondere tutte le richieste, così da eliminare l'ambiguità rispetto a un [matcher di percorso](/docs/caddyfile/matchers#matcher-di-percorso)) &mdash; cambiate il percorso del vostro sito se non è la directory di lavoro corrente. Infine, abilitiamo il [server di file statici](/docs/caddyfile/directives/file_server).



## Reverse proxy

<a id="reverse-proxy"></a>
Proxy per tutte le richieste:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Effettuare il proxy solo per le richieste con un percorso che inizia con `/api/` e servire file statici per tutto il resto:

```caddy
example.com {
	root * /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Questo utilizza un [matcher di richiesta](/docs/caddyfile/matchers#sintassi) per far corrispondere solo le richieste che iniziano con `/api/` ed effettuarne il proxy verso il backend. Tutte le altre richieste verranno servite dalla [`root`](/docs/caddyfile/directives/root) del sito con il [server di file statici](/docs/caddyfile/directives/file_server). Ciò dipende anche dal fatto che `reverse_proxy` ha una priorità maggiore nell'[ordine delle direttive](/docs/caddyfile/directives#ordine-delle-direttive) rispetto a `file_server`.

Ci sono molti altri [esempi di `reverse_proxy` qui](/docs/caddyfile/directives/reverse_proxy#esempi).



## PHP

<a id="php"></a>
### PHP-FPM

Con un servizio PHP FastCGI in esecuzione, qualcosa di simile funziona per la maggior parte delle moderne app PHP:

```caddy
example.com {
	root * /srv/public
	encode zstd gzip
	php_fastcgi localhost:9000
	file_server
}
```

Personalizzate la root del sito di conseguenza; questo esempio assume che la webroot della vostra app PHP si trovi all'interno di una directory `public` &mdash; le richieste per i file esistenti su disco verranno servite con [`file_server`](/docs/caddyfile/directives/file_server), e tutto il resto verrà instradato a `index.php` per essere gestito dall'app PHP.

A volte potreste usare un socket unix per connettervi a PHP-FPM:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

La [direttiva `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) è in realtà solo una scorciatoia per [diversi pezzi di configurazione](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

In alternativa, potete usare [FrankenPHP](https://frankenphp.dev/), che è una distribuzione di Caddy che chiama direttamente il PHP usando CGO (binding Go verso C). Può essere fino a 4 volte più veloce rispetto a PHP-FPM, e ancora di più se si utilizza la modalità worker.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root * /srv/public
    encode zstd br gzip
    php_server
}
```


## Reindirizzamento sottodominio `www.`

<a id="redirect-www-subdomain"></a>
Per **aggiungere** il sottodominio `www.` con un reindirizzamento HTTP:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Per **rimuoverlo**:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Per rimuoverlo per **più domini** contemporaneamente; questo utilizza i placeholder `{labels.*}` che sono le parti dell'hostname, indicizzate da `0` partendo da destra (es. `0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



## Trailing slashes

<a id="trailing-slashes"></a>
Di solito non avrete bisogno di configurarlo voi stessi; la [direttiva `file_server`](/docs/caddyfile/directives/file_server) aggiungerà o rimuoverà automaticamente gli slash finali dalle richieste tramite reindirizzamenti HTTP, a seconda che la risorsa richiesta sia rispettivamente una directory o un file.

Tuttavia, se ne avete bisogno, potete comunque imporre gli slash finali con la vostra configurazione. Ci sono due modi per farlo: internamente o esternamente.

### Imposizione interna

Si usa la direttiva [`rewrite`](/docs/caddyfile/directives/rewrite). Caddy riscriverà l'URI internamente per aggiungere o rimuovere lo slash finale:

```caddy
example.com {
	rewrite /aggiungi     /aggiungi/
	rewrite /rimuovi/ /rimuovi
}
```

Usando una riscrittura, le richieste con e senza lo slash finale saranno uguali.


### Imposizione esterna

Si usa la direttiva [`redir`](/docs/caddyfile/directives/redir). Caddy chiederà al browser di cambiare l'URI per aggiungere o rimuovere lo slash finale:

```caddy
example.com {
	redir /aggiungi     /aggiungi/
	redir /rimuovi/ /rimuovi
}
```

Usando un reindirizzamento, il client dovrà riemettere la richiesta, imponendo un unico URI accettabile per una risorsa.



## Certificati wildcard

<a id="wildcard-certificates"></a>
Per la maggior parte degli emittenti, incluso Let's Encrypt, è necessario abilitare la [sfida ACME DNS](/docs/automatic-https#sfida-dns) affinché Caddy possa automatizzare i certificati wildcard.

Con la sfida DNS abilitata, a partire da Caddy 2.10, Caddy preferirà un certificato wildcard applicabile già configurato o gestito prima di gestire un certificato separato per un sottodominio.



Se avete bisogno di servire più sottodomini con lo stesso certificato wildcard, il modo migliore per gestirli è con un Caddyfile come questo, facendo uso della [direttiva `handle`](/docs/caddyfile/directives/handle) e dei [matcher `host`](/docs/caddyfile/matchers#host):

```caddy
*.example.com {
	tls {
		dns <nome_provider> [<parametri...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# Fallback per domini altrimenti non gestiti
	handle {
		abort
	}
}
```

È necessario abilitare la [sfida ACME DNS](/docs/automatic-https#sfida-dns) affinché Caddy possa gestire automaticamente i certificati wildcard.



## Single-page app (SPA)

<a id="single-page-apps-spas"></a>
Quando una pagina web gestisce il proprio routing, i server possono ricevere molte richieste per pagine che non esistono lato server, ma che sono renderizzabili lato client a patto che venga invece servito il singolo file index. Le applicazioni web architettate in questo modo sono note come SPA, o single-page app.

L'idea principale è far sì che il server "provi i file" per vedere se il file richiesto esiste lato server e, in caso contrario, ripieghi su un file index induve il client effettua il routing (solitamente con JavaScript lato client).

Una tipica configurazione SPA di solito appare così:

```caddy
example.com {
	root * /srv
	encode zstd gzip
	try_files {path} /index.html
	file_server
}
```

Se la vostra SPA è accoppiata a un'API o ad altri endpoint esclusivamente lato server, vorrete usare i blocchi `handle` per trattarli in modo esclusivo:

```caddy
example.com {
	encode zstd gzip

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root * /srv
		try_files {path} /index.html
		file_server
	}
}
```

Se il vostro `index.html` contiene riferimenti ai vostri asset JS/CSS con nomi di file hashati, potreste considerare di aggiungere un header `Cache-Control` per istruire i client a *non* metterlo in cache (così che se gli asset cambiano, i browser recuperino quelli nuovi). Poiché la riscrittura `try_files` viene usata per servire il vostro `index.html` da qualsiasi percorso che non corrisponda a un altro file su disco, potete avvolgere `try_files` con un `route` in modo che l'handler `header` venga eseguito *dopo* la riscrittura (normalmente verrebbe eseguito prima a causa dell'[ordine delle direttive](/docs/caddyfile/directives#ordine-delle-direttive)):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


## Caddy che effettua il proxy verso un altro Caddy

<a id="caddy-proxying-to-another-caddy"></a>
If avete un'istanza di Caddy accessibile pubblicamente (chiamiamola "front") e un'altra istanza di Caddy nella vostra rete privata (chiamiamola "back") che serve la vostra app effettiva, potete usare la [direttiva `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) per passare le richieste.

Istanza front:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Istanza back:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Questo esempio serve due domini diversi, effettuando il proxy di entrambi verso la stessa istanza back di Caddy, sulla porta `80`. La vostra istanza back sta servendo i due domini in modi diversi, quindi è configurata con due blocchi sito separati.

- Sul back, viene usato [`http://`](/docs/caddyfile/concepts#indirizzi) per accettare l'HTTP sulla porta `80`. L'istanza front termina il TLS e il traffico tra front e back avviene su una rete privata, quindi non c'è bisogno di crittografarlo nuovamente.

- Potete usare una porta diversa come la `8080` sull'istanza back se necessario; basta aggiungere `:8080` a ogni indirizzo del sito nella configurazione del back, OPPURE impostare l'[opzione globale `http_port`](/docs/caddyfile/options#http_port) su `8080`.

- Sul back, viene usata l'[opzione globale `trusted_proxies`](/docs/caddyfile/options#trusted-proxies) per dire a Caddy di fidarsi dell'istanza front come proxy. Ciò garantisce che l'IP reale del client venga preservato.

- Andando oltre, potreste avere più di un'istanza back tra cui effettuare il [bilanciamento del carico](/docs/caddyfile/directives/reverse_proxy#bilanciamento-del-carico). Potreste impostare il mTLS (mutual TLS) usando l'[`acme_server`](/docs/caddyfile/directives/acme_server) sull'istanza front in modo che agisca come CA per l'istanza back (utile se il traffico tra front e back attraversa reti non fidate).
