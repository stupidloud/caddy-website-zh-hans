---
title: "Caddyfile-Unterstützung"
---

<a id="caddyfile-support"></a>
# Caddyfile-Unterstützung

Caddy modules werden aufgrund ihres namespace automatisch zur [nativen JSON-Konfiguration](/docs/json/) hinzugefügt, sobald sie [registriert](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) sind. Dadurch sind sie sowohl nutzbar als auch dokumentiert. Caddyfile-Unterstützung ist deshalb rein optional, wird aber oft von Benutzern gewünscht, die das Caddyfile bevorzugen.

<a id="unmarshaler"></a>
## Unmarshaler

Um Caddyfile-Unterstützung für dein module hinzuzufügen, implementiere einfach das Interface [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Welche Caddyfile-Syntax dein module hat, bestimmst du darüber, wie du die tokens parst.

Die Aufgabe eines unmarshaler ist lediglich, den Typ deines modules einzurichten, z. B. indem er dessen Felder mit dem übergebenen [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) befüllt. Ein module-Typ namens `Gizmo` könnte zum Beispiel diese Methode haben:

```go
// UnmarshalCaddyfile implements caddyfile.Unmarshaler. Syntax:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // Direktivenname verbrauchen

	if !d.Args(&g.Name) {
		// nicht genug Argumente
		return d.ArgErr()
	}
	if d.NextArg() {
		// optionales Argument
		g.Option = d.Val()
	}
	if d.NextArg() {
		// zu viele Argumente
		return d.ArgErr()
	}

	return nil
}
```

Es ist eine gute Idee, die Syntax im godoc-Kommentar der Methode zu dokumentieren. Weitere Informationen zum Parsen des Caddyfile findest du in der [godoc zum Package `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc).

Das token mit dem Direktivenname kann mit einem einfachen Aufruf von `d.Next()` verbraucht bzw. übersprungen werden.

Achte darauf, mit `d.NextArg()` oder `d.RemainingArgs()` auf fehlende und/oder überschüssige Argumente zu prüfen. Verwende `d.ArgErr()` für eine einfache Meldung im "ungültiger Fall"-Stil, oder `d.Errf("some message")`, um eine hilfreiche Fehlermeldung mit Erklärung des Problems zu formulieren, idealerweise mit einem Lösungsvorschlag.

Du solltest außerdem einen [interface guard](/docs/extending-caddy#interface-guards) hinzufügen, um sicherzustellen, dass das Interface korrekt erfüllt wird:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### Blöcke

Wenn du mehr Konfiguration akzeptieren möchtest, als auf eine einzelne Zeile passt, kannst du einen Block mit subdirectives erlauben. Das geht mit `d.NextBlock()` und einer Iteration, bis du wieder auf der ursprünglichen Verschachtelungsebene bist:

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

Solange jede Schleifeniteration das gesamte Segment (Zeile oder Block) verbraucht, ist das eine elegante Art, Blöcke zu behandeln.

<a id="http-directives"></a>
## HTTP-Direktiven

Das HTTP Caddyfile ist Caddys Standard-Syntax für Caddyfile adapter (oder "server type"). Es ist erweiterbar, das heißt, du kannst eigene "top-level" directives für dein module [registrieren](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective):

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Wenn deine directive nur einen einzelnen HTTP handler zurückgibt (wie es häufig der Fall ist), ist [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) für dich möglicherweise einfacher:

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

Die Grundidee ist, dass [die Parsing-Funktion](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc), die du mit deiner directive verknüpfst, einen oder mehrere Werte vom Typ [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue) zurückgibt. (Oder, wenn du `RegisterHandlerDirective` verwendest, gibt sie direkt den befüllten Wert `caddyhttp.MiddlewareHandler` zurück.) Jeder config value ist einer ["class"](#classes) zugeordnet, die dem HTTP Caddyfile adapter hilft zu erkennen, in welchen Teilen der finalen JSON-Konfiguration er verwendet werden kann. Alle config values werden in einen Pool gelegt, aus dem der Adapter beim Erstellen der finalen JSON-Konfiguration zieht.

Dieses Design erlaubt deiner directive, beliebige config values für beliebige erkannte classes zurückzugeben. Damit kann sie alle Teile der Konfiguration beeinflussen, für die der HTTP Caddyfile adapter eine bestimmte class vorgesehen hat.

Wenn du die Methode `UnmarshalCaddyfile()` bereits implementiert hast, kann deine parse function so einfach sein:

```go
// parseCaddyfileHandler unmarshals tokens from h into a new middleware handler value.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Weitere Informationen zur Verwendung des Typs `httpcaddyfile.Helper` findest du in der [godoc des Packages `httpcaddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc).

<a id="handler-order"></a>
### Handler-Reihenfolge

Alle directives, die HTTP middleware/handler-Werte zurückgeben, müssen in der richtigen Reihenfolge ausgewertet werden. Ein handler, der zum Beispiel das root-Verzeichnis der Site setzt, muss vor einem handler kommen, der auf das root-Verzeichnis zugreift, damit dieser den Verzeichnispfad kennt.

Das HTTP Caddyfile [hat eine fest codierte Reihenfolge für die Standard-Direktiven](/docs/caddyfile/directives#directive-order). Dadurch müssen Benutzer die Implementierungsdetails der häufigsten Funktionen ihres Webservers nicht kennen, und korrekte Konfigurationen lassen sich leichter schreiben. Eine einzelne, fest codierte Liste verhindert außerdem Nichtdeterminismus angesichts der erweiterbaren Natur des Caddyfile.

**Wenn du eine neue handler directive registrierst, muss sie zu dieser Liste hinzugefügt werden, bevor sie verwendet werden kann (außerhalb eines `route`-Blocks).** Das geschieht mit einer von drei Methoden:

- (Empfohlen) Der plugin author kann nach dem Registrieren der directive in `init()` [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) aufrufen, um die directive relativ zu einer anderen [standard directive](/docs/caddyfile/directives#directive-order) in die Reihenfolge einzufügen. Dann können Benutzer die directive direkt in ihren Sites verwenden, ohne zusätzliche Einrichtung. Um deine directive `gizmo` beispielsweise nach dem handler `header` auswerten zu lassen:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Benutzer können die [globale Option `order`](/docs/caddyfile/options) hinzufügen, um die Standardreihenfolge für ihr Caddyfile zu ändern. Beispiel: `order gizmo before respond` fügt eine neue directive `gizmo` ein, die vor dem handler `respond` ausgewertet wird. Danach kann die directive normal verwendet werden.

- Benutzer können die directive in einen [`route`-Block](/docs/caddyfile/directives/route) setzen. Da directives in einem route-Block nicht neu sortiert werden, müssen die dort verwendeten directives nicht in der Liste auftauchen.

Wenn du eine der beiden letzten Optionen wählst, dokumentiere für deine Benutzer bitte eine Empfehlung, an welcher Stelle der Liste deine directive richtig einsortiert werden sollte, damit sie sie korrekt verwenden können.

<a id="classes"></a>
### Classes

Diese Tabelle beschreibt jede class mit exportierten Typen, die vom HTTP Caddyfile adapter erkannt wird:

Class name | Erwarteter Typ | Beschreibung
---------- | ------------- | -----------
bind | `[]string` | Bind-Adressen für Server-listener
route | `caddyhttp.Route` | HTTP handler route
error_route | `*caddyhttp.Subroute` | HTTP error handling route
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS connection policy
tls.cert_issuer | `certmagic.Issuer` | TLS certificate issuer
tls.cert_loader | `caddytls.CertificateLoader` | TLS certificate loader

<a id="server-types"></a>
## Server Types

Strukturell ist das Caddyfile ein einfaches Format. Deshalb kann es unterschiedliche Arten von Caddyfile-Formaten geben (manchmal "server types" genannt), passend zu unterschiedlichen Anforderungen.

Das Standardformat ist das HTTP Caddyfile, mit dem du wahrscheinlich vertraut bist. Dieses Format konfiguriert hauptsächlich die [`http` app](/docs/modules/http), streut aber möglicherweise auch Konfiguration in andere Teile der Caddy-Konfigurationsstruktur ein (z. B. in die `tls` app, um Zertifikate zu laden und zu automatisieren).

Um andere apps als HTTP zu konfigurieren, kannst du einen eigenen config adapter implementieren, der [deinen eigenen server type](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter) verwendet. Der Caddyfile adapter parst die Eingabe tatsächlich für dich und gibt dir die Liste der server blocks und options; anschließend ist es Aufgabe deines Adapters, diese Struktur zu interpretieren und daraus eine JSON-Konfiguration zu machen.
