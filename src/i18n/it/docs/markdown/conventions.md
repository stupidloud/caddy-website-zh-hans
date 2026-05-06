---
title: Convenzioni
---

# Convenzioni

L'ecosistema di Caddy aderisce ad alcune convenzioni per rendere le cose coerenti e intuitive in tutta la piattaforma.


- [Indirizzi di rete](#indirizzi-di-rete)
- [Placeholder](#placeholder)
- [Posizione dei file](#posizione-dei-file)
  - [Directory dei dati](#directory-dei-dati)
  - [Directory di configurazione](#directory-di-configurazione)
- [Durate](#durate)



## Indirizzi di rete

Quando si specifica un indirizzo di rete a cui connettersi o da associare, Caddy accetta una stringa nel seguente formato:

```
network/address
```

La parte relativa alla rete (network) è opzionale (il valore predefinito è `tcp`) ed è qualsiasi valore riconosciuto dalla [funzione `net.Dial` di Go](https://pkg.go.dev/net#Dial). Se viene specificata una rete, una singola barra in avanti `/` deve separare le parti relative alla rete e all'indirizzo.

La rete può essere una delle seguenti; quelle con il suffisso `4` o `6` sono rispettivamente solo IPv4 o IPv6:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

La parte relativa all'indirizzo può assumere una di queste forme:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/percorso/del/socket/unix`
- `/percorso/del/socket/unix|0200`

L'host può essere un qualsiasi hostname, un nome di dominio risolvibile o un indirizzo IP.

Nel caso di indirizzi IPv6, l'indirizzo deve essere racchiuso tra parentesi quadre `[]`. L'identificatore di zona (che inizia con `%`) è opzionale (spesso usato per indirizzi link-local).

La porta può essere un singolo valore (`:8080`) o un intervallo inclusivo (`:8080-8085`). Un intervallo di porte verrà moltiplicato in indirizzi singoli. Non tutti i campi di configurazione accettano intervalli di porte. La porta speciale `:0` indica qualsiasi porta disponibile.

Un percorso di socket unix è accettabile solo quando si utilizza un tipo di rete `unix*`. La barra in avanti che separa la rete e l'indirizzo non è considerata parte del percorso.

Quando un socket unix viene usato come indirizzo di associazione (bind), è possibile opzionalmente specificare una modalità di permesso del file dopo il percorso, separata da un carattere pipe `|`. Il valore predefinito è `0200` (ottale), ovvero `u=w,g=,o=` (simbolico). Lo `0` iniziale è opzionale.

Esempi validi:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//percorso/del/socket
unix//percorso/del/socket|0200
```

<aside class="tip">
	Gli indirizzi di rete di Caddy non sono URL. Gli URL accoppiano i livelli inferiore e superiore del [modello OSI <img src="/old/resources/images/external-link.svg" class="external-link">](https://it.wikipedia.org/wiki/Modello_OSI#Architettura_a_livelli), ma Caddy spesso usa gli indirizzi di rete indipendentemente da una specifica applicazione, quindi combinarli sarebbe problematico. In Caddy, gli indirizzi di rete si riferiscono precisamente alle risorse a cui è possibile connettersi o che possono essere associate ai livelli L3-L5, mentre gli URL combinano i livelli L3-L7, il che è troppo. Un indirizzo di rete richiede che host+porta e percorso siano mutualmente esclusivi, mentre gli URL no. Gli indirizzi di rete a volte supportano intervalli di porte, mentre gli URL no.
</aside>




## Placeholder

La configurazione di Caddy supporta l'uso dei *placeholder* (segnaposto). L'uso dei placeholder è un modo semplice per iniettare valori dinamici in una configurazione statica.

<aside class="tip">
	I placeholder sono un'idea simile alle variabili in altri software. Ad esempio, [nginx ha delle variabili <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) come `$uri` e `$document_root`, mentre l'equivalente di Caddy sarebbe [`{http.request.uri}`](/docs/json/apps/http/#docs) e [`{http.vars.root}`](/docs/caddyfile/directives/root).
</aside>


I placeholder sono delimitati da entrambi i lati da parentesi graffe `{ }` e contengono l'identificatore all'interno, ad esempio: `{foo.bar}`. La parentesi graffa di apertura del placeholder può essere preceduta da un carattere di escape `\{cosi.qui}` per evitarne la sostituzione. Gli identificatori dei placeholder sono tipicamente organizzati in namespace con punti per evitare collisioni tra i moduli.

Quali placeholder siano disponibili dipende dal contesto. Non tutti i placeholder sono disponibili in tutte le parti della configurazione. Ad esempio, [l'app HTTP imposta dei placeholder](/docs/json/apps/http/#docs) che sono disponibili solo nelle aree della configurazione relative alla gestione delle richieste HTTP. Quando una richiesta passa attraverso l'[handler `reverse_proxy`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs), l'handler imposta diversi placeholder specifici per il proxy. Questi placeholder possono essere richiamati sia durante il proxying che successivamente (in `handle_response`), ad esempio quando si impostano gli header di risposta o si arricchiscono i log di accesso.

I seguenti placeholder sono sempre disponibili (globali):

Placeholder | Descrizione
------------|-------------
`{env.*}` | Variabile d'ambiente; esempio: `{env.HOME}`
`{file.*}` | Contenuto di un file; esempio: `{file./percorso/del/segreto.txt}`
`{system.hostname}` | L'hostname locale del sistema
`{system.slash}` | Il separatore del percorso dei file del sistema
`{system.os}` | Il sistema operativo (OS) del sistema
`{system.arch}` | L'architettura del sistema
`{system.wd}` | La directory di lavoro corrente
`{time.now}` | L'ora corrente come struttura Time di Go
`{time.now.http}` | L'ora corrente nel formato usato negli [header HTTP <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)
`{time.now.unix}` | L'ora corrente come timestamp unix in secondi
`{time.now.unix_ms}` | L'ora corrente come timestamp unix in millisecondi
`{time.now.common_log}` | L'ora corrente nel formato Common Log Format
`{time.now.year}` | L'anno corrente nel formato YYYY

Non tutti i campi di configurazione supportano i placeholder, ma la maggior parte lo fa dove ci si aspetterebbe. Il supporto per i placeholder deve essere stato aggiunto esplicitamente a quei campi. Gli autori di plugin possono [leggere questo articolo](/docs/extending-caddy/placeholders) per imparare come aggiungere il supporto per i placeholder nei propri moduli.




## Posizione dei file

Questa sezione contiene informazioni su dove trovare i vari file. I percorsi di file e directory descritti qui sono, nel migliore dei casi, dei valori predefiniti; alcuni possono essere sovrascritti.

### I vostri file di configurazione

Non esiste un unico luogo convenzionale dove mettere i propri file di configurazione. Metteteli dove ha più senso per voi.

<aside class="tip">
	L'unica eccezione potrebbe essere un file chiamato `Caddyfile` nella directory di lavoro corrente, che il comando caddy prova a usare per comodità se non viene specificato nessun altro file di configurazione.
</aside>


Le distribuzioni che includono un file di configurazione predefinito dovrebbero documentare dove si trova tale file, anche se potrebbe essere ovvio per i manutentori del pacchetto o della distribuzione. Per la maggior parte delle installazioni Linux, il Caddyfile si troverà in `/etc/caddy/Caddyfile`.


### Directory dei dati

Caddy memorizza i certificati TLS e altri asset importanti in una directory dei dati, che è supportata dal [modulo di storage configurato](/docs/json/storage/) (valore predefinito: file system locale).

Se la variabile d'ambiente `XDG_DATA_HOME` è impostata, il percorso è `$XDG_DATA_HOME/caddy`.

In caso contrario, il suo percorso varia a seconda della piattaforma, aderendo alle convenzioni del sistema operativo:

OS | Percorso della directory dei dati
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (o `/sdcard/caddy`)

Tutti gli altri sistemi operativi utilizzano il percorso della directory di Linux/BSD.

**La directory dei dati non deve essere trattata come una cache.** Il suo contenuto **non** è effimero o destinato esclusivamente alle prestazioni. Caddy memorizza nella directory dei dati i certificati TLS, le chiavi private, gli OCSP staple e altre informazioni necessarie. Non dovrebbe essere cancellata senza averne compreso le implicazioni.

È fondamentale che questa directory sia persistente e scrivibile da Caddy.


### Directory di configurazione

È qui che Caddy può memorizzare alcune configurazioni su disco. In particolare, in questa cartella viene mantenuta l'ultima configurazione attiva (per impostazione predefinita) per facilitarne la ripresa successiva tramite [`caddy run --resume`](/docs/command-line#caddy-run).

<aside class="tip">
	La directory di configurazione *non* è il luogo dove è necessario memorizzare i [propri file di configurazione](#i-vostri-file-di-configurazione). (Sebbene sia permesso farlo.)
</aside>


Se la variabile d'ambiente `XDG_CONFIG_HOME` è impostata, il percorso è `$XDG_CONFIG_HOME/caddy`.

In caso contrario, il suo percorso varia a seconda della piattaforma, aderendo alle convenzioni del sistema operativo:


OS | Percorso della directory di configurazione
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Tutti gli altri sistemi operativi utilizzano il percorso della directory di Linux/BSD.

È fondamentale che questa directory sia persistente e scrivibile da Caddy.


## Durate

Le stringhe di durata sono comunemente usate in tutta la configurazione di Caddy. Adottano lo stesso formato della [sintassi `time.ParseDuration` di Go](https://golang.org/pkg/time/#ParseDuration), con la differenza che è possibile utilizzare anche `d` per giorno (per semplicità assumiamo 1 giorno = 24 ore). Le unità valide sono:

- `ns` (nanosecondo)
- `us`/`µs` (microsecondo)
- `ms` (millisecondo)
- `s` (secondo)
- `m` (minuto)
- `h` (ora)
- `d` (giorno)

Esempi:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

Nella [configurazione JSON](/docs/json/), i valori di durata possono anche essere numeri interi che rappresentano i nanosecondi.
