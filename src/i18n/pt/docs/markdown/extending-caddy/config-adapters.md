---
title: "Escrevendo adaptadores de configuração"
---

<a id="writing-config-adapters"></a>
# Escrevendo adaptadores de configuração

Por vários motivos, talvez você queira configurar o Caddy usando um formato que não seja [JSON](/docs/json/). O Caddy oferece suporte de primeira classe a isso por meio de [adaptadores de configuração](/docs/config-adapters).

Se ainda não existir um adaptador para a linguagem/sintaxe/formato que você prefere, você pode escrever um.

<a id="template"></a>
## Template

Aqui está um template do qual você pode partir:

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
	// TODO: parse body and convert it to JSON
	return nil, nil, fmt.Errorf("not implemented")
}
```

- Veja o godoc de [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- Veja o godoc da interface [`Adapter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

O JSON retornado **não** deve ser indentado; ele deve ser sempre compacto. Quem chama pode formatá-lo depois, se quiser.

Observe que, embora adaptadores de configuração sejam _plugins_ do Caddy, eles não são _módulos_ do Caddy porque não se integram a uma parte da configuração (mas aparecem em `list-modules` por conveniência). Portanto, eles não têm métodos `Provision()` ou `Validate()` nem seguem o restante do ciclo de vida de módulos. Eles só precisam implementar a interface `Adapter` e ser registrados como adaptadores.

Ao preencher campos da configuração que são do tipo `json.RawMessage` (isto é, campos de módulo), use as funções `JSON()` e `JSONModuleObject()`:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) serve para serializar valores de módulo sem o nome do módulo embutido. (Frequentemente usado para campos ModuleMap, em que o nome do módulo é a chave do mapa.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) serve para serializar valores de módulo com o nome do módulo adicionado ao objeto. (Usado praticamente em todos os outros lugares.)


<a id="caddyfile-server-types"></a>
## Tipos de servidor do Caddyfile

Também é possível implementar um formato Caddyfile personalizado. O adaptador Caddyfile é uma única implementação de adaptador e seu "tipo de servidor" padrão é HTTP, mas ele suporta "tipos de servidor" alternativos no registro. Por exemplo, o Caddyfile HTTP é registrado assim:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Você implementaria a [interface `caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) e registraria seu próprio adaptador de acordo.
