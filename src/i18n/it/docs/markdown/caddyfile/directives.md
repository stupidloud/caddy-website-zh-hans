---
title: Direttive del Caddyfile
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

# Direttive del Caddyfile

Le direttive sono parole chiave funzionali che appaiono all'interno dei [blocchi](/docs/caddyfile/concepts#blocchi) dei siti. A volte, possono aprire dei blocchi propri che possono contenere delle *sottodirettive*, ma le direttive **non possono** essere usate all'interno di altre direttive, a meno che non sia indicato diversamente. Ad esempio, non potete usare `basic_auth` all'interno di un blocco `file_server`, poiché `file_server` non sa come gestire l'autenticazione. Tuttavia, *potete* usare alcune direttive all'interno di speciali blocchi direttiva come `handle` e `route`, poiché sono specificamente progettati per raggruppare le direttive degli handler HTTP.

- [Sintassi](#sintassi)
- [Ordine delle direttive](#ordine-delle-direttive)
- [Algoritmo di ordinamento](#algoritmo-di-ordinamento)

Le seguenti direttive sono fornite di serie con Caddy e possono essere utilizzate nell'HTTP Caddyfile:

<div id="directive-table">

Direttiva | Descrizione
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Interrompe la richiesta HTTP
**[acme_server](/docs/caddyfile/directives/acme_server)** | Un server ACME integrato
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Impone l'autenticazione HTTP Basic
**[bind](/docs/caddyfile/directives/bind)** | Personalizza l'indirizzo del socket del server
**[encode](/docs/caddyfile/directives/encode)** | Codifica (solitamente comprime) le risposte
**[error](/docs/caddyfile/directives/error)** | Genera un errore
**[file_server](/docs/caddyfile/directives/file_server)** | Serve file dal disco
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Delega l'autenticazione a un servizio esterno
**[fs](/docs/caddyfile/directives/fs)** | Imposta il file system da usare per l'I/O dei file
**[handle](/docs/caddyfile/directives/handle)** | Un gruppo di direttive mutualmente esclusive
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Definisce le rotte per la gestione degli errori
**[handle_path](/docs/caddyfile/directives/handle_path)** | Come handle, ma rimuove il prefisso del percorso
**[header](/docs/caddyfile/directives/header)** | Imposta o rimuove gli header di risposta
**[import](/docs/caddyfile/directives/import)** | Include snippet o file
**[intercept](/docs/caddyfile/directives/intercept)** | Intercetta le risposte scritte da altri handler
**[invoke](/docs/caddyfile/directives/invoke)** | Invoca una rotta nominata
**[log](/docs/caddyfile/directives/log)** | Abilita il logging degli accessi/richieste
**[log_append](/docs/caddyfile/directives/log_append)** | Aggiunge un campo al log degli accessi
**[log_skip](/docs/caddyfile/directives/log_skip)** | Salta il logging degli accessi per le richieste corrispondenti
**[log_name](/docs/caddyfile/directives/log_name)** | Sovrascrive i nomi dei logger su cui scrivere
**[map](/docs/caddyfile/directives/map)** | Mappa un valore di input su uno o più output
**[method](/docs/caddyfile/directives/method)** | Cambia internamente il metodo HTTP
**[metrics](/docs/caddyfile/directives/metrics)** | Configura l'endpoint di esposizione delle metriche di Prometheus
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Serve siti PHP tramite FastCGI
**[push](/docs/caddyfile/directives/push)** | Invia contenuti al client utilizzando il server push di HTTP/2
**[redir](/docs/caddyfile/directives/redir)** | Invia un reindirizzamento HTTP al client
**[request_body](/docs/caddyfile/directives/request_body)** | Manipola il corpo della richiesta
**[request_header](/docs/caddyfile/directives/request_header)** | Manipola gli header della richiesta
**[respond](/docs/caddyfile/directives/respond)** | Invia una risposta fissa al client
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Un reverse proxy potente ed estensibile
**[rewrite](/docs/caddyfile/directives/rewrite)** | Riscrive internamente la richiesta
**[root](/docs/caddyfile/directives/root)** | Imposta il percorso della radice del sito
**[route](/docs/caddyfile/directives/route)** | Un gruppo di direttive trattate letteralmente come una singola unità
**[templates](/docs/caddyfile/directives/templates)** | Esegue template sulla risposta
**[tls](/docs/caddyfile/directives/tls)** | Personalizza le impostazioni TLS
**[tracing](/docs/caddyfile/directives/tracing)** | Integrazione con il tracciamento di OpenTelemetry
**[try_files](/docs/caddyfile/directives/try_files)** | Riscrittura che dipende dall'esistenza dei file
**[uri](/docs/caddyfile/directives/uri)** | Manipola l'URI
**[vars](/docs/caddyfile/directives/vars)** | Imposta variabili arbitrarie

</div>

## Sintassi

La sintassi di ogni direttiva apparirà più o meno così:

```caddy-d
direttiva [<matcher>] <argomenti...> {
	sottodirettiva [<argomenti...>]
}
```

I simboli `<carets>` indicano i token da sostituire con i valori effettivi.

Le `[parentesi quadre]` indicano parametri opzionali.

I puntini di sospensione `...` indicano una continuazione, ovvero uno o più parametri o righe.

Le sottodirettive sono tipicamente opzionali se non diversamente documentato, anche se non appaiono tra `[parentesi quadre]`.


### Matcher

La maggior parte &mdash; ma non tutte &mdash; delle direttive accetta [token matcher](/docs/caddyfile/matchers#sintassi), che vi permettono di filtrare le richieste. I token matcher sono solitamente opzionali. Le direttive supportano i matcher se vedete questo nella sintassi di una direttiva:

```caddy-d
[<matcher>]
```

Poiché i token matcher funzionano tutti allo stesso modo, le varie possibilità per il token matcher non verranno descritte in ogni pagina, per ridurre le duplicazioni. Fate invece riferimento alla [documentazione dei matcher](/docs/caddyfile/matchers) per una spiegazione dettagliata della sintassi.


## Ordine delle direttive

Molte direttive manipolano la catena degli handler HTTP. L'ordine in cui tali direttive vengono valutate è importante, quindi un ordine predefinito è cablato all'interno di Caddy.

Potete sovrascrivere/personalizzare questo ordinamento usando l'[opzione globale `order`](/docs/caddyfile/options#order) o la [direttiva `route`](/docs/caddyfile/directives/route).

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # solo nel blocco handle_response di reverse_proxy
request_body

redir

# manipolazione della richiesta in entrata
method
rewrite
uri
try_files

# handler middleware; alcuni avvolgono le risposte
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# direttive speciali per il routing e il dispacciamento
invoke
handle
handle_path
route

# handler che tipicamente rispondono alle richieste
abort
error
copy_response # solo nel blocco handle_response di reverse_proxy
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



## Algoritmo di ordinamento

Per facilità d'uso, l'adattatore Caddyfile ordina le direttive secondo le seguenti regole:

- Le direttive con nomi diversi sono ordinate in base alla loro posizione nell'[ordine predefinito](#ordine-delle-direttive). L'ordine predefinito può essere sovrascritto con l'[opzione globale `order`](/docs/caddyfile/options). Le direttive provenienti dai plugin *non hanno* un ordine, quindi l'opzione globale [`order`](/docs/caddyfile/options) o la direttiva [`route`](/docs/caddyfile/directives/route) dovrebbero essere usate per impostarne uno.

- Le direttive con lo stesso nome sono ordinate in base ai loro [matcher](/docs/caddyfile/matchers#sintassi).

  - La priorità più alta è data a una direttiva con un singolo [matcher di percorso](/docs/caddyfile/matchers#matcher-di-percorso).

    I matcher di percorso sono ordinati per specificità, dal più specifico al meno specifico.
	
	In generale, questo viene eseguito ordinando per la lunghezza del matcher di percorso. C'è un'eccezione: se il percorso termina con un `*` e i percorsi dei due matcher sono altrimenti uguali, il matcher senza `*` è considerato più specifico e ordinato più in alto.

    Ad esempio:
    - `/foobar` è più specifico di `/foo`
    - `/foo` è più specifico di `/foo*`
    - `/foo/*` è più specifico di `/foo*`

  - Una direttiva con qualsiasi altro matcher viene ordinata successivamente, nell'ordine in cui appare nel Caddyfile.

    Questo include i matcher di percorso con più valori e i [matcher con nome](/docs/caddyfile/matchers#matcher-con-nome).

  - Una direttiva senza matcher (che quindi corrisponde a tutte le richieste) viene ordinata per ultima.

- La direttiva [`vars`](/docs/caddyfile/directives/vars) ha l'ordinamento per matcher invertito, perché comporta l'impostazione di valori che possono sovrascriversi a vicenda, quindi il matcher più specifico dovrebbe essere valutato per ultimo.

- Il contenuto della direttiva [`route`](/docs/caddyfile/directives/route) ignora tutte le regole sopra citate e preserva l'ordine in cui le direttive appaiono al suo interno.
