---
title: "Caddy erweitern"
---

<a id="extending-caddy"></a>
# Caddy erweitern

Caddy lässt sich dank seiner modularen Architektur leicht erweitern. Die meisten Arten von Caddy-Erweiterungen (oder plugins) werden als *modules* bezeichnet, wenn sie Caddys Konfigurationsstruktur erweitern oder sich in sie einklinken. Zur Klarstellung: Caddy modules sind etwas anderes als [Go modules](https://github.com/golang/go/wiki/Modules) (auch wenn sie ebenfalls Go modules sind).

**Voraussetzungen:**
- Grundverständnis von [Caddys Architektur](/docs/architecture)
- Sicherer Umgang mit der Sprache Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Schnellstart

Ein Caddy module ist jeder benannte Typ, der sich selbst als Caddy module registriert, wenn sein Package importiert wird. Entscheidend ist: Ein module implementiert immer das Interface [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), das seinen Namen und eine Konstruktorfunktion bereitstellt.

Füge in einem neuen Go module die folgende Vorlage in eine Go-Datei ein und passe Package-Name, Typname und Caddy module ID an:

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo is an example; put your own type here.
type Gizmo struct {
}

// CaddyModule returns the Caddy module information.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

Führe danach diesen Befehl im Verzeichnis deines Projekts aus. Dein module sollte in der Liste erscheinen:

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

Der Befehl [`xcaddy`](https://github.com/caddyserver/xcaddy) ist ein wichtiger Teil des Workflows jedes module developer. Er kompiliert Caddy mit deinem plugin und führt Caddy anschließend mit den angegebenen Argumenten aus. Die temporäre Binary wird jedes Mal verworfen (ähnlich wie bei `go run`).

</aside>


Glückwunsch, dein module registriert sich bei Caddy und kann in [Caddys config document](/docs/json/) überall dort verwendet werden, wo modules im selben namespace genutzt werden.

Unter der Haube erstellt `xcaddy` einfach ein neues Go module, das sowohl Caddy als auch dein plugin benötigt (mit einem passenden `replace`, um deine lokale Entwicklungsversion zu verwenden), und fügt dann einen Import hinzu, damit es einkompiliert wird:

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Grundlagen zu modules

Caddy modules:

1. Implementieren das Interface `caddy.Module`, um eine ID und einen Konstruktor bereitzustellen
2. Haben einen eindeutigen Namen im passenden namespace
3. Erfüllen normalerweise ein oder mehrere Interfaces, die für das host module dieses namespace relevant sind

**Host modules** (oder *parent modules*) sind modules, die andere modules laden oder initialisieren. Sie definieren typischerweise namespaces für guest modules.

**Guest modules** (oder *child modules*) sind modules, die geladen oder initialisiert werden. Alle modules sind guest modules.


<a id="module-ids"></a>
## Module IDs

Jedes Caddy module hat eine eindeutige ID, die aus namespace und name besteht:

- Eine vollständige ID sieht so aus: `foo.bar.module_name`
- Der namespace wäre `foo.bar`
- Der name wäre `module_name`; er muss innerhalb seines namespace eindeutig sein

Module IDs müssen die Konvention `snake_case` verwenden.

<a id="namespaces"></a>
### Namespaces

Namespaces sind wie Klassen: Ein namespace definiert eine Funktionalität, die allen modules darin gemeinsam ist. Zum Beispiel können wir erwarten, dass alle modules im namespace `http.handlers` HTTP handlers sind. Daraus folgt, dass ein host module guest modules in diesem namespace aus Typen `interface{}` per type assertion in einen spezifischeren, nützlicheren Typ wie `caddyhttp.MiddlewareHandler` umwandeln kann.

Ein guest module muss korrekt namespaced sein, damit es von einem host module erkannt wird. Host modules fragen Caddy nämlich nach modules innerhalb eines bestimmten namespace, um die vom host module gewünschte Funktionalität bereitzustellen. Wenn du zum Beispiel ein HTTP handler module namens `gizmo` schreibst, wäre der Name deines modules `http.handlers.gizmo`, weil die `http` app im namespace `http.handlers` nach handlers sucht.

Anders gesagt: Von Caddy modules wird erwartet, dass sie abhängig von ihrem module namespace [bestimmte Interfaces](/docs/extending-caddy/namespaces) implementieren. Mit dieser Konvention können module developers intuitive Aussagen treffen wie: "Alle modules im namespace `http.handlers` sind HTTP handlers." Technischer heißt das normalerweise: "Alle modules im namespace `http.handlers` implementieren das Interface `caddyhttp.MiddlewareHandler`." Weil dieses method set bekannt ist, kann auf den spezifischeren Typ geprüft und er verwendet werden.

**[Tabelle ansehen, die alle Standard-Caddy-namespaces ihren Go-Typen zuordnet.](/docs/extending-caddy/namespaces)**

Die namespaces `caddy` und `admin` sind reserviert und können keine app names sein.

Wenn du modules schreibst, die sich in host modules von Drittanbietern einklinken, lies die namespace-Dokumentation dieser modules.

<a id="names"></a>
### Namen

Der name innerhalb eines namespace ist wichtig und für Benutzer sehr sichtbar, aber technisch nicht besonders bedeutend, solange er eindeutig und knapp ist und sinnvoll beschreibt, was das module tut.


<a id="app-modules"></a>
## App modules

Apps sind modules mit leerem namespace, die konventionell zu ihrem eigenen top-level namespace werden. App modules implementieren das Interface [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Diese modules erscheinen in der Eigenschaft [`"apps"`](/docs/json/#apps) auf der obersten Ebene von Caddys Konfiguration:

```json
{
	"apps": {}
}
```

Beispiel-[apps](/docs/json/apps/) sind `http` und `tls`. Ihr namespace ist leer.

Guest modules, die für diese apps geschrieben werden, sollten in einem vom app name abgeleiteten namespace liegen. HTTP handlers verwenden zum Beispiel den namespace `http.handlers`, und TLS certificate loaders verwenden den namespace `tls.certificates`.

<a id="module-implementation"></a>
## Module-Implementierung

Ein module kann praktisch jeder Typ sein, aber structs sind am häufigsten, weil sie Benutzerkonfiguration speichern können.


<a id="configuration"></a>
### Konfiguration

Die meisten modules benötigen Konfiguration. Caddy erledigt das automatisch, solange dein Typ mit JSON kompatibel ist. Wenn ein module also ein struct-Typ ist, benötigt es struct tags an seinen Feldern; diese sollten nach Caddy-Konvention `snake_casing` verwenden:

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

Die Option `omitempty` im struct tag lässt das Feld in der JSON-Ausgabe weg, wenn es den zero value seines Typs hat. Das ist nützlich, um die JSON-Konfiguration beim Marshaling sauber und knapp zu halten (z. B. beim Anpassen von Caddyfile nach JSON).

Wenn ein module initialisiert wird, ist seine Konfiguration bereits ausgefüllt. Es ist außerdem möglich, nach der Initialisierung zusätzliche Schritte für [provisioning](#provisioning) und [validation](#validating) auszuführen.


<a id="module-lifecycle"></a>
### Module lifecycle

Das Leben eines modules beginnt, wenn es von einem host module geladen wird. Folgendes passiert:

1. [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) wird aufgerufen, um eine Instanz des module-Werts zu erhalten.
2. Die Konfiguration des modules wird in diese Instanz unmarshaled.
3. Wenn das module ein [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) ist, wird die Methode `Provision()` aufgerufen.
4. Wenn das module ein [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) ist, wird die Methode `Validate()` aufgerufen.
5. An diesem Punkt erhält das host module das geladene guest module als Wert `interface{}`. Das host module wird das guest module daher normalerweise per type assertion in einen nützlicheren Typ umwandeln. Prüfe die Dokumentation des host module, um zu wissen, was von einem guest module in dessen namespace verlangt wird, z. B. welche Methoden implementiert sein müssen.
6. Wenn ein module nicht mehr benötigt wird und ein [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper) ist, wird die Methode `Cleanup()` aufgerufen.

Beachte, dass mehrere geladene Instanzen deines modules zu einem bestimmten Zeitpunkt überlappen können. Bei Konfigurationsänderungen werden neue modules gestartet, bevor die alten gestoppt werden. Verwende globalen Zustand daher vorsichtig. Nutze den Typ [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool), um globalen Zustand über module loads hinweg zu verwalten. Wenn dein module auf einem Socket lauscht, verwende `caddy.Listen*()`, um einen Socket zu erhalten, der überlappende Nutzung unterstützt.

<a id="provisioning"></a>
### Provisioning

Die Konfiguration eines modules wird automatisch in seinen Wert unmarshaled (beim Laden der JSON-Konfiguration). Das bedeutet zum Beispiel, dass struct fields für dich ausgefüllt werden.

Wenn dein module jedoch zusätzliche provisioning-Schritte benötigt, kannst du das (optionale) Interface [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) implementieren:

```go
// Provision sets up the module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: module einrichten
	return nil
}
```

Hier solltest du Standardwerte für Felder setzen, die nicht vom Benutzer angegeben wurden (Felder, die nicht ihren zero value haben). Wenn ein Feld erforderlich ist, kannst du einen Fehler zurückgeben, wenn es nicht gesetzt ist. Bei numerischen Feldern, deren zero value eine Bedeutung hat (z. B. eine timeout duration), möchtest du vielleicht `-1` als "aus" unterstützen statt `0`; dann kannst du einen Standardwert setzen, wenn der Benutzer das Feld nicht konfiguriert hat.

Das ist typischerweise auch die Stelle, an der host modules ihre guest/child modules laden.

Ein module kann mit `ctx.App()` auf andere apps zugreifen, modules dürfen aber keine zirkulären Abhängigkeiten haben. Anders gesagt: Ein von der `http` app geladenes module kann nicht von der `tls` app abhängen, wenn ein von der `tls` app geladenes module von der `http` app abhängt. (Sehr ähnlich zu den Regeln, die Importzyklen in Go verbieten.)

Außerdem solltest du teure Operationen in `Provision` vermeiden, weil provisioning auch dann ausgeführt wird, wenn eine Konfiguration nur validiert wird. In der provisioning-Phase solltest du nicht erwarten, dass das module tatsächlich verwendet wird.

<a id="logs"></a>
#### Logs

Siehe [wie Logging in Caddy funktioniert](/docs/logging). Wenn dein module Logging benötigt, verwende nicht `log.Print*()` aus der Go-Standardbibliothek. Anders gesagt: **Verwende nicht Gos globalen Logger**. Caddy nutzt hochperformantes, sehr flexibles, strukturiertes Logging mit [zap](https://github.com/uber-go/zap).

Um Logs auszugeben, hole dir in der Provision-Methode deines modules einen Logger:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger is a *zap.Logger
}
```

Danach kannst du mit `g.logger` strukturierte Logs mit Levels ausgeben. Details findest du in [zaps godoc](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger).


<a id="validating"></a>
### Validating

Modules, die ihre Konfiguration validieren möchten, können das tun, indem sie das (optionale) Interface [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) erfüllen:

```go
// Validate validates that the module has a usable config.
func (g Gizmo) Validate() error {
	// TODO: setup des modules validieren
	return nil
}
```

`Validate` sollte eine read-only-Funktion sein. Sie wird nach der Methode `Provision()` ausgeführt.


<a id="interface-guards"></a>
### Interface guards

Das Verhalten von Caddy modules ist implizit, weil Go interfaces implizit erfüllt werden. Es reicht, deinem module-Typ die richtigen Methoden hinzuzufügen, um die Korrektheit deines modules herzustellen oder zu brechen. Ein Tippfehler oder eine falsche Methodensignatur kann deshalb zu unerwartetem (fehlendem) Verhalten führen.

Zum Glück gibt es eine einfache compile-time-Prüfung ohne Laufzeitkosten, die du deinem Code hinzufügen kannst, um sicherzustellen, dass du die richtigen Methoden hinzugefügt hast. Diese Prüfungen heißen interface guards:

```go
var _ InterfaceName = (*YourType)(nil)
```

Ersetze `InterfaceName` durch das Interface, das du erfüllen willst, und `YourType` durch den Namen des Typs deines modules.

Ein HTTP handler wie der static file server könnte zum Beispiel mehrere Interfaces erfüllen:

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Das verhindert, dass das Programm kompiliert, wenn `*FileServer` diese Interfaces nicht erfüllt.

Ohne interface guards können verwirrende Bugs entstehen. Wenn dein module sich zum Beispiel vor der Nutzung provisionen muss, deine Methode `Provision()` aber einen Fehler hat (z. B. falsch geschrieben oder falsche Signatur), findet provisioning nie statt. Interface guards sind sehr einfach und können das verhindern. Sie stehen normalerweise am Ende der Datei.


<a id="host-modules"></a>
## Host modules

Ein module wird zu einem host module, wenn es eigene guest modules lädt. Das ist nützlich, wenn ein Teil der Funktionalität des modules auf unterschiedliche Weise implementiert werden kann.

Ein host module ist fast immer ein struct. Normalerweise benötigt die Unterstützung eines guest module zwei struct fields: eines für das rohe JSON und eines für den decodierten Wert:

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

Das erste Feld (`GadgetRaw` in diesem Beispiel) enthält die rohe, noch nicht provisioned JSON-Form des guest module.

Das zweite Feld (`Gadget`) ist der Ort, an dem der finale, provisioned Wert später gespeichert wird. Da das zweite Feld nicht für Benutzer gedacht ist, schließen wir es mit einem struct tag aus JSON aus. (Du könntest es auch unexported machen, wenn es von anderen Packages nicht benötigt wird; dann ist kein struct tag nötig.)

<a id="caddy-struct-tags"></a>
### Caddy struct tags

Der struct tag `caddy` am raw module field hilft Caddy, namespace und name (zusammen die vollständige ID) des zu ladenden modules zu kennen. Er wird außerdem zum Generieren von Dokumentation verwendet.

Der struct tag hat ein sehr einfaches Format: `key1=val1 key2=val2 ...`

Für module fields sieht der struct tag so aus:

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

Der Teil `namespace=` ist erforderlich. Er definiert den namespace, in dem nach dem module gesucht werden soll.

Der Teil `inline_key=` wird nur verwendet, wenn der Name des modules *inline* beim module selbst gefunden wird. Das bedeutet, dass der Wert ein Objekt ist, bei dem einer der Schlüssel der *inline key* ist und dessen Wert der Name des modules ist. Wird er weggelassen, muss der Feldtyp eine [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) oder `[]caddy.ModuleMap` sein, wobei der map key der module name ist.


<a id="loading-guest-modules"></a>
### Guest modules laden

Um ein guest module zu laden, rufe während der provision phase [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) auf:

```go
// Provision sets up g and loads its gadget.
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

Beachte, dass der Aufruf `LoadModule()` einen Pointer auf das struct und den Feldnamen als string erhält. Seltsam, oder? Warum nicht einfach das struct field direkt übergeben? Der Grund ist, dass es je nach Layout der Konfiguration mehrere Arten gibt, modules zu laden. Diese Methodensignatur erlaubt Caddy, per Reflection herauszufinden, wie das module am besten geladen wird, und vor allem seine struct tags zu lesen.

Wenn ein guest module ausdrücklich vom Benutzer gesetzt werden muss, solltest du einen Fehler zurückgeben, wenn das Raw-Feld nil oder leer ist, bevor du versuchst, es zu laden.

Achte darauf, wie das geladene module per type assertion umgewandelt wird: `g.Gadget = val.(Gadgeter)` - denn das zurückgegebene `val` hat den Typ `interface{}`, der nicht besonders nützlich ist. Wir erwarten aber, dass alle modules im deklarierten namespace (`foo.gizmo.gadgets` aus dem struct tag in unserem Beispiel) das Interface `Gadgeter` implementieren. Deshalb ist diese type assertion sicher, und dann können wir das module verwenden.

Wenn dein host module einen neuen namespace definiert, dokumentiere unbedingt sowohl diesen namespace als auch seine Go-Typen für Entwickler, [wie wir es hier getan haben](/docs/extending-caddy/namespaces).

<a id="module-documentation"></a>
## Module-Dokumentation

Registriere das module, damit ein neues Caddy module in der module documentation erscheint und unter http://caddyserver.com/download verfügbar ist. Die Registrierung ist unter http://caddyserver.com/account verfügbar. Erstelle ein neues Konto, falls du noch keines hast, und klicke auf "Register package".

<a id="complete-example"></a>
## Vollständiges Beispiel

Angenommen, wir möchten ein HTTP handler module schreiben. Das wird eine absichtlich einfache middleware zu Demonstrationszwecken, die bei jedem HTTP request die IP-Adresse des Besuchers in einen Stream schreibt.

Außerdem soll sie über das Caddyfile konfigurierbar sein, weil die meisten Menschen in nicht automatisierten Situationen lieber das Caddyfile verwenden. Dazu registrieren wir eine Caddyfile handler directive, also eine Art directive, die der HTTP route einen handler hinzufügen kann. Außerdem implementieren wir das Interface `caddyfile.Unmarshaler`. Mit diesen wenigen Codezeilen kann dieses module über das Caddyfile konfiguriert werden. Beispiel: `visitor_ip stdout`.

Hier ist der Code für ein solches module, mit erläuternden Kommentaren:

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

// Middleware implements an HTTP handler that writes the
// visitor's IP address to a file or stream.
type Middleware struct {
	// The file or stream to write to. Can be "stdout"
	// or "stderr".
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule returns the Caddy module information.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision implements caddy.Provisioner.
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

// Validate implements caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP implements caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile implements caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consume directive name

	// require an argument
	if !d.NextArg() {
		return d.ArgErr()
	}

	// store the argument
	m.Output = d.Val()
	return nil
}

// parseCaddyfile unmarshals tokens from h into a new Middleware.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Interface guards
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
