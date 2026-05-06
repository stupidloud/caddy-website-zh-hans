---
title: "Scrivere adattatori di configurazione"
---

# Scrivere adattatori di configurazione

Per varie ragioni, potreste voler configurare Caddy usando un formato che non sia il [JSON](/docs/json/). Caddy ha un supporto di prima classe per questo tramite gli [adattatori di configurazione](/docs/config-adapters).

Se non ne esiste già uno per il linguaggio/sintassi/formato che preferite, potete scriverne uno!

## Template

Ecco un template da cui potete iniziare:

```go
package myadapter

import (
	"fmt"

	"github.com/caddyserver/caddy/v2/caddyconfig"
)

func init() {
	caddyconfig.RegisterAdapter("nome_adattatore", MyAdapter{})
}

// MyAdapter adatta ____ al JSON di Caddy.
type MyAdapter struct{
}

// Adapt adatta il corpo al JSON di Caddy.
func (a MyAdapter) Adapt(body []byte, options map[string]interface{}) ([]byte, []caddyconfig.Warning, error) {
	// TODO: analizzare il corpo e convertirlo in JSON
	return nil, nil, fmt.Errorf("non implementato")
}
```

- Consultate il godoc per [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- Consultate il godoc per l'interfaccia [`Adapter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

Il JSON restituito **non** dovrebbe essere indentato; dovrebbe sempre essere compatto. Il chiamante potrà sempre abbellirlo se lo desidera.

Si noti che, sebbene gli adattatori di configurazione siano dei *plugin* di Caddy, essi non sono *moduli* di Caddy perché non si integrano in una parte della configurazione (ma appariranno in `list-modules` per comodità). Pertanto, non hanno i metodi `Provision()` o `Validate()` né seguono il resto del ciclo di vita dei moduli. Devono solo implementare l'interfaccia `Adapter` ed essere registrati come adattatori.

Quando popolate campi della configurazione che sono di tipo `json.RawMessage` (ovvero campi modulo), usate le funzioni `JSON()` e `JSONModuleObject()`:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) serve per serializzare (marshal) i valori dei moduli senza il nome del modulo incorporato. (Spesso usato per i campi ModuleMap dove il nome del modulo è la chiave della mappa.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) serve per serializzare i valori dei moduli con il nome del modulo aggiunto all'oggetto. (Usato praticamente ovunque altro.)


## Tipi di Server Caddyfile

È inoltre possibile implementare un formato Caddyfile personalizzato. L'adattatore Caddyfile è un'unica implementazione di adattatore e il suo "tipo di server" predefinito è HTTP, ma supporta "tipi di server" alternativi alla registrazione. Ad esempio, l'HTTP Caddyfile viene registrato in questo modo:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Dovreste implementare l'[interfaccia `caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) e registrare il vostro adattatore di conseguenza.
