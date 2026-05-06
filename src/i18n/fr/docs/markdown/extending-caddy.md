---
title: "Étendre Caddy"
---

# Étendre Caddy

Caddy est facile à étendre grâce à son architecture modulaire. La plupart des extensions Caddy (ou plugins) sont appelées _modules_ si elles étendent ou s'insèrent dans la structure de configuration de Caddy. Pour être précis, les modules Caddy sont distincts des [modules Go](https://github.com/golang/go/wiki/Modules) (mais ce sont aussi des modules Go).

**Prérequis :**
- Compréhension de base de [l'architecture de Caddy](/docs/architecture)
- Maîtrise du langage Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Démarrage rapide

Un module Caddy est n'importe quel type nommé qui s'enregistre en tant que module Caddy lors de l'importation de son paquet. Crucialement, un module implémente toujours l'interface [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), qui fournit son nom et une fonction constructeur.

Dans un nouveau module Go, collez le modèle suivant dans un fichier Go et personnalisez le nom de votre paquet, le nom de votre type et l'ID de votre module Caddy :

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo est un exemple ; mettez votre propre type ici.
type Gizmo struct {
}

// CaddyModule retourne les informations du module Caddy.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

Ensuite, lancez cette commande depuis le répertoire de votre projet, et vous devriez voir votre module dans la liste :

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

La [commande `xcaddy`](https://github.com/caddyserver/xcaddy) est un élément essentiel du flux de travail de tout développeur de modules. Elle compile Caddy avec votre plugin, puis l'exécute avec les arguments fournis. Elle supprime le binaire temporaire à chaque fois (similaire à `go run`).

</aside>


Félicitations, votre module s'enregistre auprès de Caddy et peut être utilisé dans le [document de configuration de Caddy](/docs/json/) partout où des modules du même espace de noms sont utilisés.

Sous le capot, `xcaddy` crée simplement un nouveau module Go qui requiert à la fois Caddy et votre plugin (avec un `replace` approprié pour utiliser votre version de développement locale), puis ajoute un import pour s'assurer qu'il est compilé :

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Bases des modules

Les modules Caddy :

1. Implémentent l'interface `caddy.Module` pour fournir un ID et un constructeur.
2. Ont un nom unique dans l'espace de noms approprié.
3. Satisfont généralement une ou plusieurs interfaces significatives pour le module hôte de cet espace de noms.

Les **modules hôtes** (ou _modules parents_) sont des modules qui chargent/initialisent d'autres modules. Ils définissent généralement des espaces de noms pour les modules invités.

Les **modules invités** (ou _modules enfants_) sont des modules qui sont chargés ou initialisés. Tous les modules sont des modules invités.


<a id="module-ids"></a>
## IDs de module

Chaque module Caddy possède un identifiant unique (ID), composé d'un espace de noms et d'un nom :

- Un ID complet ressemble à `foo.bar.nom_du_module`.
- L'espace de noms serait `foo.bar`.
- Le nom serait `nom_du_module`, qui doit être unique dans son espace de noms.

Les IDs de module doivent utiliser la convention `snake_case`.

<a id="namespaces"></a>
### Espaces de noms (Namespaces)

Les espaces de noms sont comme des classes ; un espace de noms définit une fonctionnalité commune à tous les modules qu'il contient. Par exemple, nous pouvons nous attendre à ce que tous les modules de l'espace de noms `http.handlers` soient des gestionnaires HTTP. Il s'ensuit qu'un module hôte peut effectuer une assertion de type sur les modules invités de cet espace de noms, passant de types `interface{}` à un type plus spécifique et utile comme `caddyhttp.MiddlewareHandler`.

Un module invité doit être correctement placé dans un espace de noms pour être reconnu par un module hôte, car les modules hôtes demanderont à Caddy des modules au sein d'un certain espace de noms pour fournir la fonctionnalité souhaitée. Par exemple, si vous écriviez un module de gestionnaire HTTP appelé `gizmo`, le nom de votre module serait `http.handlers.gizmo`, car l'application `http` recherchera des gestionnaires dans l'espace de noms `http.handlers`.

En d'autres termes, on s'attend à ce que les modules Caddy implémentent [certaines interfaces](/docs/extending-caddy/namespaces) en fonction de leur espace de noms. Avec cette convention, les développeurs de modules peuvent dire des choses intuitives comme : "Tous les modules de l'espace de noms `http.handlers` sont des gestionnaires HTTP". Techniquement, cela signifie généralement : "Tous les modules de l'espace de noms `http.handlers` implémentent l'interface `caddyhttp.MiddlewareHandler`". Puisque ce jeu de méthodes est connu, le type plus spécifique peut être affirmé et utilisé.

**[Voir le tableau associant tous les espaces de noms standard de Caddy à leurs types Go.](/docs/extending-caddy/namespaces)**

Les espaces de noms `caddy` et `admin` sont réservés et ne peuvent pas être des noms d'applications.

Pour écrire des modules qui s'insèrent dans des modules hôtes tiers, consultez la documentation de ces modules pour connaître leurs espaces de noms.

<a id="names"></a>
### Noms

Le nom au sein d'un espace de noms est significatif et très visible pour les utilisateurs, mais il n'est pas particulièrement important tant qu'il est unique, concis et cohérent avec ce qu'il fait.


<a id="app-modules"></a>
## Modules d'application (App)

Les applications sont des modules avec un espace de noms vide, et qui deviennent par convention leur propre espace de noms de haut niveau. Les modules d'application implémentent l'interface [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Ces modules apparaissent dans la propriété [`"apps"`](/docs/json/#apps) au sommet de la configuration de Caddy :

```json
{
	"apps": {}
}
```

Des exemples d'[applications](/docs/json/apps/) sont `http` et `tls`. Les leurs correspondent à l'espace de noms vide.

Les modules invités écrits pour ces applications doivent être dans un espace de noms dérivé du nom de l'application. Par exemple, les gestionnaires HTTP utilisent l'espace de noms `http.handlers` et les chargeurs de certificats TLS utilisent l'espace de noms `tls.certificates`.

<a id="module-implementation"></a>
## Implémentation d'un module

Un module peut être virtuellement n'importe quel type, mais les structures (structs) sont les plus courantes car elles peuvent contenir la configuration de l'utilisateur.


<a id="configuration"></a>
### Configuration

La plupart des modules nécessitent une configuration. Caddy s'en occupe automatiquement, tant que votre type est compatible avec le JSON. Ainsi, si un module est un type struct, il aura besoin de tags de struct sur ses champs, qui doivent utiliser le `snake_case` selon la convention Caddy :

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

L'utilisation de l'option `omitempty` dans le tag de struct omettra le champ de la sortie JSON s'il possède la valeur par défaut (zéro) de son type. C'est utile pour garder la configuration JSON propre et concise lorsqu'elle est sérialisée (ex: lors de l'adaptation d'un Caddyfile en JSON).

Lorsqu'un module est initialisé, sa configuration est déjà renseignée. Il est également possible d'effectuer des étapes supplémentaires de [provisionnement](#provisioning) et de [validation](#validating) après l'initialisation d'un module.


<a id="module-lifecycle"></a>
### Cycle de vie du module

La vie d'un module commence lorsqu'il est chargé par un module hôte. Voici ce qui se passe :

1. [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) est appelé pour obtenir une instance de la valeur du module.
2. La configuration du module est désérialisée (unmarshaled) dans cette instance.
3. Si le module est un [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner), la méthode `Provision()` est appelée.
4. Si le module est un [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator), la méthode `Validate()` est appelée.
5. À ce stade, le module hôte reçoit le module invité chargé sous forme de valeur `interface{}`, le module hôte effectuera donc généralement une assertion de type pour transformer le module invité en un type plus utile. Consultez la documentation du module hôte pour savoir ce qui est requis d'un module invité dans son espace de noms, par exemple quelles méthodes doivent être implémentées.
6. Lorsqu'un module n'est plus nécessaire, et s'il s'agit d'un [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper), la méthode `Cleanup()` est appelée.

Notez que plusieurs instances chargées de votre module peuvent se chevaucher à un moment donné ! Lors des changements de configuration, les nouveaux modules sont démarrés avant que les anciens ne soient arrêtés. Veillez à utiliser l'état global avec précaution. Utilisez le type [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) pour aider à gérer l'état global entre les chargements de modules. Si votre module écoute sur un socket, utilisez `caddy.Listen*()` pour obtenir un socket supportant l'usage simultané.

<a id="provisioning"></a>
### Provisionnement (Provisioning)

La configuration d'un module sera automatiquement désérialisée dans sa valeur (lors du chargement de la configuration JSON). Cela signifie, par exemple, que les champs de la structure seront remplis pour vous.

Cependant, si votre module nécessite des étapes de configuration supplémentaires, vous pouvez implémenter l'interface (optionnelle) [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) :

```go
// Provision configure le module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO : configurer le module
	return nil
}
```

C'est ici que vous devez définir les valeurs par défaut pour les champs qui n'ont pas été fournis par l'utilisateur (champs qui n'ont pas leur valeur par défaut). Si un champ est obligatoire, vous pouvez retourner une erreur s'il n'est pas renseigné. Pour les champs numériques où la valeur zéro a une signification (ex: une durée de timeout), vous pourriez vouloir supporter `-1` pour signifier "désactivé" plutôt que `0`, afin de pouvoir définir une valeur par défaut si l'utilisateur ne l'a pas configuré.

C'est également généralement ici que les modules hôtes chargeront leurs modules invités/enfants.

Un module peut accéder à d'autres applications en appelant `ctx.App()`, mais les modules ne doivent pas avoir de dépendances circulaires. En d'autres termes, un module chargé par l'application `http` ne peut pas dépendre de l'application `tls` si un module chargé par l'application `tls` dépend de l'application `http`. (Très similaire aux règles interdisant les cycles d'importation en Go.)

De plus, vous devriez éviter d'effectuer des opérations coûteuses dans `Provision`, car le provisionnement est effectué même si une configuration est seulement en cours de validation. En phase de provisionnement, ne vous attendez pas à ce que le module soit réellement utilisé.

<a id="logs"></a>
#### Journaux (Logs)

Consultez [comment fonctionne la journalisation](/docs/logging) dans Caddy. Si votre module a besoin de journalisation, n'utilisez pas `log.Print*()` de la bibliothèque standard Go. En d'autres termes, **n'utilisez pas le logger global de Go**. Caddy utilise une journalisation structurée, haute performance et hautement flexible avec [zap](https://github.com/uber-go/zap).

Pour émettre des journaux, récupérez un logger dans la méthode Provision de votre module :

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger est un *zap.Logger
}
```

Ensuite, vous pouvez émettre des journaux structurés et nivelés en utilisant `g.logger`. Consultez la [godoc de zap](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger) pour plus de détails.


<a id="validating"></a>
### Validation

Les modules qui souhaitent valider leur configuration peuvent le faire en satisfaisant l'interface (optionnelle) [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) :

```go
// Validate valide que le module a une configuration utilisable.
func (g Gizmo) Validate() error {
	// TODO : valider la configuration du module
	return nil
}
```

`Validate` doit être une fonction en lecture seule. Elle est exécutée après la méthode `Provision()`.


<a id="interface-guards"></a>
### Gardes d'interface (Interface guards)

Le comportement des modules Caddy est implicite car les interfaces Go sont satisfaites implicitement. Ajouter simplement les bonnes méthodes au type de votre module suffit à garantir (ou non) la correction de votre module. Ainsi, faire une faute de frappe ou se tromper dans la signature d'une méthode peut conduire à un comportement inattendu (ou une absence de comportement).

Heureusement, il existe une vérification facile, sans surcoût et à la compilation que vous pouvez ajouter à votre code pour vous assurer que vous avez ajouté les bonnes méthodes. On les appelle des gardes d'interface :

```go
var _ NomInterface = (*VotreType)(nil)
```

Remplacez `NomInterface` par l'interface que vous avez l'intention de satisfaire, et `VotreType` par le nom du type de votre module.

Par exemple, un gestionnaire HTTP tel que le serveur de fichiers statiques pourrait satisfaire plusieurs interfaces :

```go
// Gardes d'interface
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Cela empêche le programme de compiler si `*FileServer` ne satisfait pas ces interfaces.

Sans gardes d'interface, des bugs déroutants peuvent s'immiscer. Par exemple, si votre module doit se provisionner avant d'être utilisé mais que votre méthode `Provision()` contient une erreur (ex: faute de frappe ou mauvaise signature), le provisionnement n'aura jamais lieu, ce qui peut vous laisser perplexe. Les gardes d'interface sont très simples et peuvent éviter cela. Ils se placent généralement en bas du fichier.


<a id="host-modules"></a>
## Modules hôtes

Un module devient un module hôte lorsqu'il charge ses propres modules invités. C'est utile si une partie de la fonctionnalité du module peut être implémentée de différentes manières.

Un module hôte est presque toujours une structure (struct). Normalement, le support d'un module invité nécessite deux champs de structure : l'un pour contenir son JSON brut, et l'autre pour contenir sa valeur décodée :

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

Le premier champ (`GadgetRaw` dans cet exemple) est l'endroit où se trouve la forme JSON brute, non provisionnée, du module invité.

Le second champ (`Gadget`) est l'endroit où la valeur finale, provisionnée, sera finalement stockée. Puisque le second champ n'est pas destiné à l'utilisateur, nous l'excluons du JSON avec un tag de structure. (Vous pourriez également ne pas l'exporter s'il n'est pas nécessaire à d'autres paquets, et alors aucun tag de structure n'est nécessaire.)

<a id="caddy-struct-tags"></a>
### Tags de structure Caddy

Le tag de structure `caddy` sur le champ du module brut aide Caddy à connaître l'espace de noms et le nom (composant l'ID complet) du module à charger. Il est également utilisé pour générer la documentation.

Le tag de structure a un format très simple : `key1=val1 key2=val2 ...`

Pour les champs de module, le tag de structure ressemblera à :

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

La partie `namespace=` est obligatoire. Elle définit l'espace de noms dans lequel chercher le module.

La partie `inline_key=` n'est utilisée que si le nom du module se trouve _en ligne_ (inline) avec le module lui-même ; cela implique que la valeur est un objet dont l'une des clés est la _clé en ligne_, et sa valeur est le nom du module. Si elle est omise, le type du champ doit être un [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) ou `[]caddy.ModuleMap`, où la clé de la map est le nom du module.


<a id="loading-guest-modules"></a>
### Chargement de modules invités

Pour charger un module invité, appelez [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) pendant la phase de provisionnement :

```go
// Provision configure g et charge son gadget.
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

Notez que l'appel à `LoadModule()` prend un pointeur vers la structure et le nom du champ sous forme de chaîne de caractères. Étrange, n'est-ce pas ? Pourquoi ne pas simplement passer le champ de la structure directement ? C'est parce qu'il existe plusieurs façons de charger des modules en fonction de la disposition de la configuration. Cette signature de méthode permet à Caddy d'utiliser la réflexion pour déterminer la meilleure façon de charger le module et, surtout, de lire ses tags de structure.

Si un module invité doit explicitement être défini par l'utilisateur, vous devriez retourner une erreur si le champ Raw est nul ou vide avant d'essayer de le charger.

Remarquez comment le module chargé subit une assertion de type : `g.Gadget = val.(Gadgeter)` — c'est parce que le `val` retourné est de type `interface{}`, ce qui n'est pas très utile. Cependant, nous nous attendons à ce que tous les modules de l'espace de noms déclaré (`foo.gizmo.gadgets` du tag de structure dans notre exemple) implémentent l'interface `Gadgeter`, donc cette assertion de type est sûre, et nous pouvons ensuite l'utiliser !

Si votre module hôte définit un nouvel espace de noms, assurez-vous de documenter à la fois cet espace de noms et son ou ses types Go pour les développeurs [comme nous l'avons fait ici](/docs/extending-caddy/namespaces).

<a id="module-documentation"></a>
## Documentation des modules

Enregistrez le module pour qu'un nouveau module Caddy apparaisse dans la documentation des modules et soit disponible sur http://caddyserver.com/download. L'enregistrement est disponible sur http://caddyserver.com/account. Créez un nouveau compte si vous n'en avez pas déjà un et cliquez sur "Register package".

<a id="complete-example"></a>
## Exemple complet

Supposons que nous voulions écrire un module de gestionnaire HTTP. Ce sera un middleware factice à des fins de démonstration qui affiche l'adresse IP du visiteur dans un flux à chaque requête HTTP.

Nous voulons également qu'il soit configurable via le Caddyfile, car la plupart des gens préfèrent utiliser le Caddyfile dans des situations non automatisées. Nous faisons cela en enregistrant une directive de gestionnaire Caddyfile, qui est un type de directive capable d'ajouter un gestionnaire à la route HTTP. Nous implémentons également l'interface `caddyfile.Unmarshaler`. En ajoutant ces quelques lignes de code, ce module peut être configuré avec le Caddyfile ! Par exemple : `visitor_ip stdout`.

Voici le code pour un tel module, avec des commentaires explicatifs :

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

// Middleware implémente un gestionnaire HTTP qui écrit
// l'adresse IP du visiteur dans un fichier ou un flux.
type Middleware struct {
	// Le fichier ou le flux dans lequel écrire. Peut être "stdout"
	// ou "stderr".
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule retourne les informations du module Caddy.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision implémente caddy.Provisioner.
func (m *Middleware) Provision(ctx caddy.Context) error {
	switch m.Output {
	case "stdout":
		m.w = os.Stdout
	case "stderr":
		m.w = os.Stderr
	default:
		return fmt.Errorf("un flux de sortie est requis")
	}
	return nil
}

// Validate implémente caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("aucun écrivain (writer)")
	}
	return nil
}

// ServeHTTP implémente caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile implémente caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consommer le nom de la directive

	// requiert un argument
	if !d.NextArg() {
		return d.ArgErr()
	}

	// stocker l'argument
	m.Output = d.Val()
	return nil
}

// parseCaddyfile désérialise les jetons de h dans un nouveau Middleware.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Gardes d'interface
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
