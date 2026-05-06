---
title: "Supporto al Caddyfile"
---

# Supporto al Caddyfile

I moduli di Caddy vengono aggiunti automaticamente alla [configurazione JSON nativa](/docs/json/) in virtù del loro namespace quando vengono [registrati](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule), rendendoli sia utilizzabili che documentati. Questo rende il supporto al Caddyfile puramente opzionale, ma è spesso richiesto dagli utenti che preferiscono il Caddyfile.

## Unmarshaler

Per aggiungere il supporto al Caddyfile per il vostro modulo, implementate semplicemente l'interfaccia [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Siete voi a scegliere la sintassi del Caddyfile che il vostro modulo avrà, in base a come analizzate i token.

Il compito di un unmarshaler è semplicemente quello di impostare il tipo del vostro modulo, ad esempio popolando i suoi campi, utilizzando il [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) che gli viene passato. Ad esempio, un tipo di modulo chiamato `Gizmo` potrebbe avere questo metodo:

```go
// UnmarshalCaddyfile implementa caddyfile.Unmarshaler. Sintassi:
//
// gizmo <nome> [<opzione>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consuma il nome della direttiva

	if !d.Args(&g.Name) {
		// non abbastanza argomenti
		return d.ArgErr()
	}
	if d.NextArg() {
		// argomento opzionale
		g.Option = d.Val()
	}
	if d.NextArg() {
		// troppi argomenti
		return d.ArgErr()
	}

	return nil
}
```

È una buona idea documentare la sintassi nel commento godoc del metodo. Consultate il [godoc per il pacchetto `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc) per ulteriori informazioni sull'analisi del Caddyfile.

Il token del nome della direttiva può essere consumato/saltato con una semplice chiamata `d.Next()`.

Assicuratevi di controllare gli argomenti mancanti e/o in eccesso con `d.NextArg()` o `d.RemainingArgs()`. Usate `d.ArgErr()` per un semplice messaggio di "caso non valido", oppure usate `d.Errf("qualche messaggio")` per creare un messaggio di errore utile con una spiegazione del problema (e idealmente una soluzione suggerita).

Dovreste anche aggiungere una [protezione dell'interfaccia](/docs/extending-caddy#protezioni-dellinterfaccia-interface-guards) per assicurarvi che l'interfaccia sia soddisfatta correttamente:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

### Blocchi

Per accettare una configurazione più ampia di quella che può stare su una singola riga, potreste voler consentire un blocco con sottodirettive. Ciò può essere fatto usando `d.NextBlock()` e iterando fino a tornare al livello di nidificazione originale:

```go
for nesting := d.Nesting(); d.NextBlock(nesting); {
	switch d.Val() {
		case "sub_directive_1":
		// ...
		case "sub_directive_2":
		// ...
	}
}
```

Finché ogni iterazione del ciclo consuma l'intero segmento (riga o blocco), questo è un modo elegante per gestire i blocchi.

## Direttive HTTP

L'HTTP Caddyfile è la sintassi dell'adattatore Caddyfile predefinita di Caddy (o "tipo di server"). È estensibile, il che significa che potete [registrare](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterDirective) le vostre direttive di "primo livello" per il vostro modulo:

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Se la vostra direttiva restituisce solo un singolo gestore HTTP (come accade comunemente), potreste trovare più facile [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective):

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

L'idea di base è che [la funzione di analisi](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) che associate alla vostra direttiva restituisce uno o più valori [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue). (Oppure, se usate `RegisterHandlerDirective`, restituisce semplicemente il valore `caddyhttp.MiddlewareHandler` popolato direttamente.) Ogni valore di configurazione è associato a una ["classe"](#classi) che aiuta l'adattatore HTTP Caddyfile a sapere in quale parte (o parti) della configurazione JSON finale può essere utilizzato. Tutti i valori di configurazione vengono scaricati in un mucchio da cui l'adattatore attinge durante la costruzione della configurazione JSON finale.

Questo design consente alla vostra direttiva di restituire qualsiasi valore di configurazione per qualsiasi classe riconosciuta, il che significa che può influenzare qualsiasi parte della configurazione per la quale l'adattatore HTTP Caddyfile ha una classe designata.

Se avete già implementato il metodo `UnmarshalCaddyfile()`, allora la vostra funzione di analisi potrebbe essere semplice come:

```go
// parseCaddyfileHandler deserializza i token da h in un nuovo valore middleware handler.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Consultate il [godoc del pacchetto `httpcaddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc) per ulteriori informazioni su come usare il tipo `httpcaddyfile.Helper`.

### Ordine dei gestori

Tutte le direttive che restituiscono valori middleware/handler HTTP devono essere valutate nell'ordine corretto. Ad esempio, un gestore che imposta la directory radice del sito deve venire prima di un gestore che accede alla directory radice, in modo che quest'ultimo sappia qual è il percorso della directory.

L'HTTP Caddyfile [ha un ordinamento predefinito per le direttive standard](/docs/caddyfile/directives#ordine-delle-direttive). Ciò garantisce che gli utenti non debbano conoscere i dettagli implementativi delle funzioni più comuni del loro server web e rende più facile per loro scrivere configurazioni corrette. Un unico elenco predefinito previene anche l'indeterminismo data la natura estensibile del Caddyfile.

**Quando registrate una nuova direttiva gestore, questa deve essere aggiunta a quell'elenco prima di poter essere utilizzata (al di fuori di un blocco `route`).** Ciò avviene utilizzando uno di tre metodi:

- (Raccomandato) L'autore del plugin può chiamare [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) in `init()` dopo aver registrato la direttiva, per inserirla nell'ordine rispetto a un'altra [direttiva standard](/docs/caddyfile/directives#ordine-delle-direttive). In questo modo, gli utenti possono usare la direttiva direttamente nei loro siti senza configurazioni extra. Ad esempio, per inserire la vostra direttiva `gizmo` affinché venga valutata dopo il gestore `header`:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Gli utenti possono aggiungere l'[opzione globale `order`](/docs/caddyfile/options) per modificare l'ordine standard per il loro Caddyfile. Ad esempio: `order gizmo before respond` inserirà una nuova direttiva `gizmo` da valutare prima del gestore `respond`. Quindi la direttiva potrà essere usata normalmente.

- Gli utenti possono inserire la direttiva in un [blocco `route`](/docs/caddyfile/directives/route). Poiché le direttive in un blocco route non vengono riordinate, le direttive usate in un blocco route non devono apparire nell'elenco.

Se scegliete una delle ultime due opzioni, documentate una raccomandazione per i vostri utenti su quale sia il posto giusto nell'elenco per ordinare la vostra direttiva, in modo che possano usarla correttamente.

### Classi

Questa tabella descrive ogni classe con tipi esportati che è riconosciuta dall'adattatore HTTP Caddyfile:

Nome classe | Tipo atteso | Descrizione
---------- | ------------- | -----------
bind | `[]string` | Indirizzi di associazione dei listener del server
route | `caddyhttp.Route` | Rotta dell'handler HTTP
error_route | `*caddyhttp.Subroute` | Rotta per la gestione degli errori HTTP
tls.connection_policy | `*caddytls.ConnectionPolicy` | Policy di connessione TLS
tls.cert_issuer | `certmagic.Issuer` | Emittente del certificato TLS
tls.cert_loader | `caddytls.CertificateLoader` | Caricatore del certificato TLS

## Tipi di Server

Strutturalmente, il Caddyfile è un formato semplice, quindi possono esistere diversi tipi di formati Caddyfile (a volte chiamati "tipi di server") per soddisfare diverse esigenze.

Il formato Caddyfile predefinito è l'HTTP Caddyfile, con cui probabilmente avete familiarità. Questo formato configura principalmente l'[app `http`](/docs/modules/http) pur potendo potenzialmente spargere alcune configurazioni in altre parti della struttura di configurazione di Caddy (es. l'app `tls` per caricare e automatizzare i certificati).

Per configurare app diverse dall'HTTP, potreste voler implementare il vostro adattatore di configurazione che utilizzi il [vostro tipo di server](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter). L'adattatore Caddyfile analizzerà effettivamente l'input per voi e vi darà l'elenco dei blocchi server e delle opzioni, e spetterà al vostro adattatore dare un senso a quella struttura e trasformarla in una configurazione JSON.
