---
title: "Estendere Caddy"
---

# Estendere Caddy

Caddy è facile da estendere grazie alla sua architettura modulare. La maggior parte dei tipi di estensioni (o plugin) di Caddy sono noti come *moduli* se estendono o si inseriscono nella struttura di configurazione di Caddy. Per chiarezza, i moduli di Caddy sono distinti dai [moduli Go](https://github.com/golang/go/wiki/Modules) (sebbene siano anche moduli Go).

**Prerequisiti:**
- Comprensione di base dell'[architettura di Caddy](/docs/architecture)
- Competenza nel linguaggio Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


## Avvio rapido

Un modulo Caddy è qualsiasi tipo nominato che si registra come modulo Caddy quando il suo pacchetto viene importato. Aspetto fondamentale, un modulo implementa sempre l'interfaccia [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), che fornisce il suo nome e una funzione costruttore.

In un nuovo modulo Go, incollate il seguente template in un file Go e personalizzate il nome del pacchetto, il nome del tipo e l'ID del modulo Caddy:

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo è un esempio; inserisci qui il tuo tipo.
type Gizmo struct {
}

// CaddyModule restituisce le informazioni sul modulo Caddy.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

Quindi eseguite questo comando dalla directory del vostro progetto e dovreste vedere il vostro modulo nell'elenco:

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">
	Il [comando `xcaddy`](https://github.com/caddyserver/xcaddy) è una parte importante del workflow di ogni sviluppatore di moduli. Compila Caddy con il vostro plugin, quindi lo esegue con gli argomenti forniti. Scarta il binario temporaneo ogni volta (similmente a `go run`).
</aside>


Congratulazioni, il vostro modulo si registra con Caddy e può essere utilizzato nel [documento di configurazione di Caddy](/docs/json/) in qualsiasi punto in cui vengano usati moduli nello stesso namespace.

Dietro le quinte, `xcaddy` sta semplicemente creando un nuovo modulo Go che richiede sia Caddy che il vostro plugin (con un `replace` appropriato per usare la vostra versione di sviluppo locale), quindi aggiunge un import per assicurarsi che venga compilato:

```go
import _ "github.com/example/mymodule"
```


## Basi dei moduli

I moduli Caddy:

1. Implementano l'interfaccia `caddy.Module` per fornire un ID e un costruttore.
2. Hanno un nome univoco nel namespace appropriato.
3. Solitamente soddisfano una o più interfacce significative per il modulo host di quel namespace.

**Moduli host** (o *moduli padre*) sono moduli che caricano/inizializzano altri moduli. Solitamente definiscono namespace per i moduli guest.

**Moduli guest** (o *moduli figlio*) sono moduli che vengono caricati o inizializzati. Tutti i moduli sono moduli guest.


## ID dei moduli

Ogni modulo Caddy ha un ID univoco, composto da un namespace e un nome:

- Un ID completo appare come `foo.bar.nome_modulo`.
- Il namespace sarebbe `foo.bar`.
- Il nome sarebbe `nome_modulo`, che deve essere univoco nel suo namespace.

Gli ID dei moduli devono utilizzare la convenzione `snake_case`.

### Namespace

I namespace sono come classi, ovvero un namespace definisce alcune funzionalità comuni a tutti i moduli al suo interno. Ad esempio, possiamo aspettarci che tutti i moduli all'interno del namespace `http.handlers` siano gestori (handler) HTTP. Ne consegue che un modulo host può eseguire il type-assert dei moduli guest in quel namespace da tipi `interface{}` a un tipo più specifico e utile come `caddyhttp.MiddlewareHandler`.

Un modulo guest deve essere inserito nel namespace corretto affinché venga riconosciuto da un modulo host, poiché i moduli host chiederanno a Caddy i moduli all'interno di un determinato namespace per fornire la funzionalità desiderata dal modulo host stesso. Ad esempio, se voleste scrivere un modulo handler HTTP chiamato `gizmo`, il nome del vostro modulo sarebbe `http.handlers.gizmo`, perché l'app `http` cercherà i gestori nel namespace `http.handlers`.

In altri termini, i moduli Caddy sono tenuti a implementare [determinate interfacce](/docs/extending-caddy/namespaces) a seconda del loro namespace. Con questa convenzione, gli sviluppatori di moduli possono dire cose intuitive come: "Tutti i moduli nel namespace `http.handlers` sono gestori HTTP". Più tecnicamente, ciò solitamente significa: "Tutti i moduli nel namespace `http.handlers` implementano l'interfaccia `caddyhttp.MiddlewareHandler`". Poiché tale set di metodi è noto, il tipo più specifico può essere asserito e utilizzato.

**[Visualizzate una tabella che mappa tutti i namespace standard di Caddy ai loro tipi Go.](/docs/extending-caddy/namespaces)**

I namespace `caddy` e `admin` sono riservati e non possono essere nomi di app.

Per scrivere moduli che si collegano a moduli host di terze parti, consultate la documentazione del namespace di tali moduli.

### Nomi

Il nome all'interno di un namespace è significativo e altamente visibile agli utenti, ma non è particolarmente importante, purché sia univoco, conciso e abbia senso per ciò che fa.


## Moduli App

Le app sono moduli con un namespace vuoto e che convenzionalmente diventano il proprio namespace di primo livello. I moduli app implementano l'interfaccia [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Questi moduli appaiono nella proprietà [`"apps"`](/docs/json/#apps) del livello superiore della configurazione di Caddy:

```json
{
	"apps": {}
}
```

Esempi di [app](/docs/json/apps/) sono `http` e `tls`. Il loro è il namespace vuoto.

I moduli guest scritti per queste app dovrebbero trovarsi in un namespace derivato dal nome dell'app. Ad esempio, i gestori HTTP usano il namespace `http.handlers` e i caricatori di certificati TLS usano il namespace `tls.certificates`.

## Implementazione del modulo

Un modulo può essere virtualmente di qualsiasi tipo, ma le struct sono le più comuni perché possono contenere la configurazione dell'utente.


### Configurazione

La maggior parte dei moduli richiede una configurazione. Caddy se ne occupa automaticamente, purché il tipo sia compatibile con il JSON. Pertanto, se un modulo è un tipo struct, avrà bisogno di tag struct sui suoi campi, che dovrebbero usare lo `snake_case` secondo la convenzione di Caddy:

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

L'uso dell'opzione `omitempty` nel tag struct ometterà il campo dall'output JSON se è il valore zero per il suo tipo. Questo è utile per mantenere la configurazione JSON pulita e concisa quando viene serializzata (marshaled), ad esempio adattando da Caddyfile a JSON.

Quando un modulo viene inizializzato, avrà già la sua configurazione compilata. È anche possibile eseguire ulteriori passaggi di [predisposizione](#predisposizione) e [validazione](#validazione) dopo l'inizializzazione di un modulo.


### Ciclo di vita del modulo

La vita di un modulo inizia quando viene caricato da un modulo host. Succede quanto segue:

1. Viene chiamato [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) per ottenere un'istanza del valore del modulo.
2. La configurazione del modulo viene deserializzata (unmarshaled) in quell'istanza.
3. Se il modulo è un [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner), viene chiamato il metodo `Provision()`.
4. Se il modulo è un [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator), viene chiamato il metodo `Validate()`.
5. A questo punto, al modulo host viene consegnato il modulo guest caricato come valore `interface{}`, quindi il modulo host solitamente esegue il type-assert del modulo guest in un tipo più utile. Consultate la documentazione del modulo host per sapere cosa è richiesto a un modulo guest nel suo namespace, ad esempio quali metodi devono essere implementati.
6. Quando un modulo non è più necessario, e se è un [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper), viene chiamato il metodo `Cleanup()`.

Si noti che più istanze caricate del vostro modulo possono sovrapporsi in un dato momento! Durante i cambi di configurazione, i nuovi moduli vengono avviati prima che quelli vecchi vengano fermati. Assicuratevi di usare lo stato globale con attenzione. Usate il tipo [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) per aiutare a gestire lo stato globale attraverso i caricamenti dei moduli. Se il vostro modulo ascolta su un socket, usate `caddy.Listen*()` per ottenere un socket che supporti l'uso sovrapposto.

### Predisposizione (Provisioning)

La configurazione di un modulo verrà deserializzata nel suo valore automaticamente (durante il caricamento della configurazione JSON). Ciò significa, ad esempio, che i campi della struct verranno compilati per voi.

Tuttavia, se il vostro modulo richiede ulteriori passaggi di predisposizione, potete implementare l'interfaccia (opzionale) [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner):

```go
// Provision configura il modulo.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: configurare il modulo
	return nil
}
```

Qui è dove dovreste impostare i valori predefiniti per i campi che non sono stati forniti dall'utente (campi che non sono al loro valore zero). Se un campo è obbligatorio, potete restituire un errore se non è impostato. Per i campi numerici dove il valore zero ha un significato (es. una durata di timeout), potreste voler supportare `-1` per significare "spento" anziché `0`, in modo da poter impostare un valore predefinito se l'utente non lo ha configurato.

Questo è anche solitamente il punto in cui i moduli host caricano i loro moduli guest/figlio.

Un modulo può accedere ad altre app chiamando `ctx.App()`, ma i moduli non devono avere dipendenze circolari. In altre parole, un modulo caricato dall'app `http` non può dipendere dall'app `tls` se un modulo caricato dall'app `tls` dipende dall'app `http` (regola molto simile a quella che vieta i cicli di import in Go).

Inoltre, dovreste evitare di eseguire operazioni costose in `Provision`, poiché la predisposizione viene eseguita anche se una configurazione viene solo validata. Quando vi trovate nella fase di predisposizione, non date per scontato che il modulo verrà effettivamente utilizzato.

#### Log

Consultate [come funziona il logging](/docs/logging) in Caddy. Se il vostro modulo necessita di logging, non usate `log.Print*()` dalla libreria standard di Go. In altre parole, **non usate il logger globale di Go**. Caddy utilizza un logging strutturato ad alte prestazioni e altamente flessibile con [zap](https://github.com/uber-go/zap).

Per emettere log, ottenete un logger nel metodo Provision del vostro modulo:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger è un *zap.Logger
}
```

Quindi potete emettere log strutturati e livellati usando `g.logger`. Consultate il [godoc di zap](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger) per i dettagli.


### Validazione

I moduli che desiderano validare la propria configurazione possono farlo soddisfacendo l'interfaccia (opzionale) [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator):

```go
// Validate convalida che il modulo abbia una configurazione utilizzabile.
func (g Gizmo) Validate() error {
	// TODO: validare la configurazione del modulo
	return nil
}
```

`Validate` dovrebbe essere una funzione di sola lettura. Viene eseguita dopo il metodo `Provision()`.


### Protezioni dell'interfaccia (Interface guards)

Il comportamento dei moduli Caddy è implicito perché le interfacce Go sono soddisfatte implicitamente. La semplice aggiunta dei metodi corretti al tipo del vostro modulo è tutto ciò che serve per decretare la correttezza o meno del modulo stesso. Pertanto, commettere un errore di battitura o sbagliare la firma del metodo può portare a comportamenti (mancanti) inaspettati.

Fortunatamente, esiste un controllo a tempo di compilazione facile e senza sovraccarico che potete aggiungere al vostro codice per assicurarvi di aver aggiunto i metodi corretti. Queste sono chiamate protezioni dell'interfaccia:

```go
var _ InterfaceName = (*YourType)(nil)
```

Sostituite `InterfaceName` con l'interfaccia che intendete soddisfare e `YourType` con il nome del tipo del vostro modulo.

Ad esempio, un gestore HTTP come il server di file statici potrebbe soddisfare più interfacce:

```go
// Protezioni dell'interfaccia
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Ciò impedisce al programma di compilare se `*FileServer` non soddisfa tali interfacce.

Senza le protezioni dell'interfaccia, possono insinuarsi bug confusi. Ad esempio, se il vostro modulo deve predisporsi prima di essere utilizzato ma il vostro metodo `Provision()` contiene un errore (es. nome errato o firma sbagliata), la predisposizione non avverrà mai, lasciandovi perplessi. Le protezioni dell'interfaccia sono semplicissime e possono prevenirlo. Solitamente si inseriscono in fondo al file.


## Moduli Host

Un modulo diventa un modulo host quando carica i propri moduli guest. Questo è utile se una parte della funzionalità del modulo può essere implementata in modi diversi.

Un modulo host è quasi sempre una struct. Normalmente, il supporto per un modulo guest richiede due campi nella struct: uno per contenere il JSON grezzo e un altro per contenere il suo valore decodificato:

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

Il primo campo (`GadgetRaw` in questo esempio) è dove si trova la forma JSON grezza e non predisposta del modulo guest.

Il secondo campo (`Gadget`) è dove verrà infine memorizzato il valore finale e predisposto. Poiché il secondo campo non è rivolto all'utente, lo escludiamo dal JSON con un tag struct (potreste anche non esportarlo se non è necessario per altri pacchetti, e allora non serve alcun tag struct).

### Tag struct di Caddy

Il tag struct `caddy` sul campo del modulo grezzo aiuta Caddy a conoscere il namespace e il nome (che compongono l'ID completo) del modulo da caricare. Viene utilizzato anche per generare la documentazione.

Il tag struct ha un formato molto semplice: `key1=val1 key2=val2 ...`

Per i campi modulo, il tag struct apparirà così:

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

La parte `namespace=` è obbligatoria. Definisce il namespace in cui cercare il modulo.

La parte `inline_key=` viene usata solo se il nome del modulo si trova *inline* (all'interno) del modulo stesso; ciò implica che il valore è un oggetto in cui una delle chiavi è la *chiave inline* e il suo valore è il nome del modulo. Se omesso, il tipo del campo deve essere una [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) o `[]caddy.ModuleMap`, dove la chiave della mappa è il nome del modulo.


### Caricamento dei moduli guest

Per caricare un modulo guest, chiamate [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) durante la fase di predisposizione:

```go
// Provision configura g e carica il suo gadget.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	if g.GadgetRaw != nil {
		val, err := ctx.LoadModule(g, "GadgetRaw")
		if err != nil {
			return fmt.Errorf("loading gadget module: %v", err)
		}
		g.Gadget = val.(Gadgeter)
	}
	return nil
}
```

Notate che la chiamata `LoadModule()` prende un puntatore alla struct e il nome del campo come stringa. Strano, vero? Perché non passare direttamente il campo della struct? È perché esistono diversi modi per caricare i moduli a seconda della disposizione della configurazione. Questa firma del metodo permette a Caddy di usare la reflection per capire il modo migliore per caricare il modulo e, cosa più importante, leggere i suoi tag struct.

Se un modulo guest deve essere impostato esplicitamente dall'utente, dovreste restituire un errore se il campo Raw è nil o vuoto prima di tentare di caricarlo.

Notate come il modulo caricato venga sottoposto a type-assertion: `g.Gadget = val.(Gadgeter)` &mdash; questo perché il `val` restituito è di tipo `interface{}`, che non è molto utile. Tuttavia, ci aspettiamo che tutti i moduli nel namespace dichiarato (`foo.gizmo.gadgets` dal tag struct nel nostro esempio) implementino l'interfaccia `Gadgeter`, quindi questa asserzione di tipo è sicura, e a quel punto possiamo usarlo!

Se il vostro modulo host definisce un nuovo namespace, assicuratevi di documentare sia quel namespace che i suoi tipi Go per gli sviluppatori, [come abbiamo fatto qui](/docs/extending-caddy/namespaces).

## Documentazione del modulo

Registrate il modulo per far apparire un nuovo modulo Caddy nella documentazione dei moduli ed essere disponibile su http://caddyserver.com/download. La registrazione è disponibile su http://caddyserver.com/account. Create un nuovo account se non ne avete già uno e cliccate su "Register package".

## Esempio completo

Supponiamo di voler scrivere un modulo handler HTTP. Sarà un middleware fittizio a scopo dimostrativo che stampa l'indirizzo IP del visitatore su uno stream ad ogni richiesta HTTP.

Vogliamo anche che sia configurabile tramite il Caddyfile, perché la maggior parte delle persone preferisce usare il Caddyfile in situazioni non automatizzate. Facciamo questo registrando una direttiva handler del Caddyfile, che è un tipo di direttiva che può aggiungere un gestore alla rotta HTTP. Implementiamo anche l'interfaccia `caddyfile.Unmarshaler`. Aggiungendo queste poche righe di codice, questo modulo può essere configurato con il Caddyfile! Ad esempio: `visitor_ip stdout`.

Ecco il codice per un tale modulo, con commenti esplicativi:

```go
package visitorip

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/caddyserver/caddy/v2"
	"github.com/caddyserver/caddy/v2/caddyconfig/caddyfile"
	"github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile"
	"github.com/caddyserver/caddy/v2/modules/caddyhttp"
)

func init() {
	caddy.RegisterModule(Middleware{})
	httpcaddyfile.RegisterHandlerDirective("visitor_ip", parseCaddyfile)
}

// Middleware implementa un handler HTTP che scrive l'indirizzo IP
// del visitatore su un file o stream.
type Middleware struct {
	// Il file o lo stream su cui scrivere. Può essere "stdout"
	// o "stderr".
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule restituisce le informazioni sul modulo Caddy.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision implementa caddy.Provisioner.
func (m *Middleware) Provision(ctx caddy.Context) error {
	switch m.Output {
	case "stdout":
		m.w = os.Stdout
	case "stderr":
		m.w = os.Stderr
	default:
		return fmt.Errorf("an output stream is required")
	}
	return nil
}

// Validate implementa caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP implementa caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile implementa caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consuma il nome della direttiva

	// richiede un argomento
	if !d.NextArg() {
		return d.ArgErr()
	}

	// memorizza l'argomento
	m.Output = d.Val()
	return nil
}

// parseCaddyfile deserializza i token da h in un nuovo Middleware.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Protezioni dell'interfaccia
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
