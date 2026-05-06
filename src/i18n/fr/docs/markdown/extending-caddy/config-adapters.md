---
title: "Écrire des adaptateurs de configuration"
---

# Écrire des adaptateurs de configuration

Pour diverses raisons, vous pouvez souhaiter configurer Caddy en utilisant un format qui n'est pas le [JSON](/docs/json/). Caddy prend cela en charge de manière native grâce aux [adaptateurs de configuration (config adapters)](/docs/config-adapters).

S'il n'en existe pas déjà un pour le langage/la syntaxe/le format que vous préférez, vous pouvez en écrire un !

## Modèle (Template)

Voici un modèle avec lequel vous pouvez commencer :

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

- Voir la godoc pour [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- Voir la godoc pour l'interface ['Adapter'](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

Le JSON retourné ne doit **pas** être indenté ; il doit toujours être compact. L'appelant peut toujours l'embellir s'il le souhaite.

Notez que bien que les adaptateurs de configuration soient des _plugins_ Caddy, ce ne sont pas des _modules_ Caddy car ils ne s'intègrent pas dans une partie de la configuration (mais ils apparaîtront dans `list-modules` par commodité). Ainsi, ils n'ont pas de méthodes `Provision()` ou `Validate()` et ne suivent pas le reste du cycle de vie des modules. Ils doivent seulement implémenter l'interface `Adapter` et être enregistrés en tant qu'adaptateurs.

Lors du remplissage des champs de la configuration qui sont des types `json.RawMessage` (c'est-à-dire des champs de module), utilisez les fonctions `JSON()` et `JSONModuleObject()` :

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) sert à sérialiser (marshaling) les valeurs de module sans intégrer le nom du module. (Souvent utilisé pour les champs ModuleMap où le nom du module est la clé de la map.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) sert à sérialiser les valeurs de module avec le nom du module ajouté à l'objet. (Utilisé à peu près partout ailleurs.)


## Types de serveur Caddyfile

Il est également possible d'implémenter un format Caddyfile personnalisé. L'adaptateur Caddyfile est une implémentation unique d'adaptateur et son "type de serveur" par défaut est HTTP, mais il supporte d'autres "types de serveur" lors de l'enregistrement. Par exemple, le Caddyfile HTTP est enregistré comme ceci :

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Vous implémenteriez l'[interface `caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) et enregistreriez votre propre adaptateur en conséquence.
