---
title: "Config Adapters schreiben"
---

<a id="writing-config-adapters"></a>
# Config Adapters schreiben

Aus verschiedenen Gründen möchtest du Caddy vielleicht mit einem Format konfigurieren, das nicht [JSON](/docs/json/) ist. Caddy unterstützt das erstklassig über [config adapters](/docs/config-adapters).

Wenn es für die Sprache, Syntax oder das Format, das du bevorzugst, noch keinen Adapter gibt, kannst du selbst einen schreiben.

<a id="template"></a>
## Vorlage

Hier ist eine Vorlage, mit der du beginnen kannst:

```go
package myadapter

import (
	"fmt"

	"github.com/caddyserver/caddy/v2/caddyconfig"
)

func init() {
	caddyconfig.RegisterAdapter("adapter_name", MyAdapter{})
}

// MyAdapter adapts ____ to Caddy JSON.
type MyAdapter struct{
}

// Adapt adapts the body to Caddy JSON.
func (a MyAdapter) Adapt(body []byte, options map[string]interface{}) ([]byte, []caddyconfig.Warning, error) {
	// TODO: body parsen und nach JSON konvertieren
	return nil, nil, fmt.Errorf("not implemented")
}
```

- Siehe godoc für [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- Siehe godoc für das Interface ['Adapter'](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

Das zurückgegebene JSON sollte **nicht** eingerückt sein; es sollte immer kompakt sein. Der Aufrufer kann es jederzeit schön formatieren, wenn er möchte.

Beachte: config adapters sind zwar Caddy-*plugins*, aber keine Caddy-*modules*, weil sie nicht in einen Teil der Konfiguration integriert werden (sie erscheinen der Bequemlichkeit halber aber in `list-modules`). Deshalb haben sie keine Methoden `Provision()` oder `Validate()` und folgen auch nicht dem restlichen module lifecycle. Sie müssen nur das Interface `Adapter` implementieren und als Adapter registriert werden.

Wenn du Felder der Konfiguration befüllst, die den Typ `json.RawMessage` haben (also module fields), verwende die Funktionen `JSON()` und `JSONModuleObject()`:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) ist zum Marshaling von module values ohne eingebetteten module name gedacht. (Wird oft für `ModuleMap`-Felder verwendet, bei denen der module name der map key ist.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) ist zum Marshaling von module values gedacht, bei dem der module name dem Objekt hinzugefügt wird. (Wird praktisch überall sonst verwendet.)


<a id="caddyfile-server-types"></a>
## Caddyfile Server Types

Es ist auch möglich, ein eigenes Caddyfile-Format zu implementieren. Der Caddyfile adapter ist eine einzelne Adapter-Implementierung, und sein Standard-"server type" ist HTTP; er unterstützt bei der Registrierung aber alternative "server types". Das HTTP Caddyfile wird zum Beispiel so registriert:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Du würdest das Interface [`caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) implementieren und deinen eigenen Adapter entsprechend registrieren.
