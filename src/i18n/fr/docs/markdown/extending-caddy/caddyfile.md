---
title: "Support du Caddyfile"
---

# Support du Caddyfile

Les modules Caddy sont automatiquement ajoutés à la [configuration JSON native](/docs/json/) en raison de leur espace de noms lorsqu'ils sont [enregistrés](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule), ce qui les rend à la fois utilisables et documentés. Le support du Caddyfile est donc purement optionnel, mais il est souvent demandé par les utilisateurs qui préfèrent ce format.

<a id="unmarshaler"></a>
## Unmarshaler

Pour ajouter le support du Caddyfile à votre module, il suffit d'implémenter l'interface [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Vous choisissez la syntaxe Caddyfile de votre module par la manière dont vous analysez les jetons (tokens).

Le rôle d'un unmarshaler est simplement de configurer le type de votre module, par exemple en remplissant ses champs, à l'aide du [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) qui lui est transmis. Par exemple, un type de module nommé `Gizmo` pourrait avoir cette méthode :

```go
// UnmarshalCaddyfile implémente caddyfile.Unmarshaler. Syntaxe :
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consommer le nom de la directive

	if !d.Args(&g.Name) {
		// pas assez d'arguments
		return d.ArgErr()
	}
	if d.NextArg() {
		// argument optionnel
		g.Option = d.Val()
	}
	if d.NextArg() {
		// trop d'arguments
		return d.ArgErr()
	}

	return nil
}
```

Il est recommandé de documenter la syntaxe dans le commentaire godoc de la méthode. Consultez la [godoc du paquet `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc) pour plus d'informations sur l'analyse du Caddyfile.

Le jeton du nom de la directive peut être consommé/ignoré avec un simple appel à `d.Next()`.

Assurez-vous de vérifier les arguments manquants et/ou excédentaires avec `d.NextArg()` ou `d.RemainingArgs()`. Utilisez `d.ArgErr()` pour un message simple de "cas invalide", ou utilisez `d.Errf("un message")` pour créer un message d'erreur utile avec une explication du problème (et idéalement, une suggestion de solution).

Vous devriez également ajouter un [garde d'interface](/docs/extending-caddy#interface-guards) pour vous assurer que l'interface est correctement satisfaite :

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### Blocs

Pour accepter plus de configuration qu'une seule ligne ne le permet, vous pouvez souhaiter autoriser un bloc avec des sous-directives. Cela peut être fait en utilisant `d.NextBlock()` et en itérant jusqu'à ce que vous reveniez au niveau de nesting initial :

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

Tant que chaque itération de la boucle consomme l'intégralité du segment (ligne ou bloc), c'est une manière élégante de gérer les blocs.

<a id="http-directives"></a>
## Directives HTTP

Le Caddyfile HTTP est la syntaxe d'adaptation par défaut de Caddy (ou "type de serveur"). Il est extensible, ce qui signifie que vous pouvez [enregistrer](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective) vos propres directives de "haut niveau" pour votre module :

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Si votre directive ne retourne qu'un seul gestionnaire HTTP (ce qui est courant), vous trouverez peut-être [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) plus simple :

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

L'idée de base est que [la fonction d'analyse](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) que vous associez à votre directive retourne une ou plusieurs valeurs [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue). (Ou, si vous utilisez `RegisterHandlerDirective`, elle retourne simplement directement la valeur `caddyhttp.MiddlewareHandler` remplie.) Chaque valeur de configuration est associée à une ["classe"](#classes) qui aide l'adaptateur Caddyfile HTTP à savoir dans quelle(s) partie(s) de la configuration JSON finale elle peut être utilisée. Toutes les valeurs de configuration sont rassemblées pour que l'adaptateur puisse y puiser lors de la construction de la configuration JSON finale.

Cette conception permet à votre directive de retourner n'importe quelle valeur de configuration pour n'importe quelle classe reconnue, ce qui signifie qu'elle peut influencer n'importe quelle partie de la configuration pour laquelle l'adaptateur Caddyfile HTTP a une classe désignée.

Si vous avez déjà implémenté la méthode `UnmarshalCaddyfile()`, votre fonction d'analyse pourrait être aussi simple que :

```go
// parseCaddyfileHandler désérialise les jetons de h dans une nouvelle valeur de gestionnaire middleware.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Consultez la [godoc du paquet `httpcaddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc) pour plus d'informations sur l'utilisation du type `httpcaddyfile.Helper`.

<a id="handler-order"></a>
### Ordre des gestionnaires

Toutes les directives qui retournent des valeurs de middleware/gestionnaire HTTP doivent être évaluées dans le bon ordre. Par exemple, un gestionnaire qui définit le répertoire racine du site doit venir avant un gestionnaire qui accède à ce répertoire racine, afin qu'il connaisse le chemin du répertoire.

Le Caddyfile HTTP [possède un ordre codé en dur pour les directives standard](/docs/caddyfile/directives#directive-order). Cela garantit que les utilisateurs n'ont pas besoin de connaître les détails d'implémentation des fonctions les plus courantes de leur serveur web, et facilite la rédaction de configurations correctes. Une liste unique et codée en dur évite également le non-déterminisme étant donné la nature extensible du Caddyfile.

**Lorsque vous enregistrez une nouvelle directive de gestionnaire, elle doit être ajoutée à cette liste avant de pouvoir être utilisée (en dehors d'un bloc `route`).** Cela se fait par l'une des trois méthodes suivantes :

- (Recommandé) L'auteur du plugin peut appeler [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) dans `init()` après avoir enregistré la directive, pour l'insérer dans l'ordre par rapport à une autre [directive standard](/docs/caddyfile/directives#directive-order). Ce faisant, les utilisateurs peuvent utiliser la directive directement dans leurs sites sans configuration supplémentaire. Par exemple, pour insérer votre directive `gizmo` afin qu'elle soit évaluée après le gestionnaire `header` :

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Les utilisateurs peuvent ajouter l'[option globale `order`](/docs/caddyfile/options) pour modifier l'ordre standard dans leur Caddyfile. Par exemple : `order gizmo before respond` insérera une nouvelle directive `gizmo` pour être évaluée avant le gestionnaire `respond`. La directive peut alors être utilisée normalement.

- Les utilisateurs peuvent placer la directive dans un [bloc `route`](/docs/caddyfile/directives/route). Comme les directives dans un bloc route ne sont pas réordonnées, les directives utilisées dans ce bloc n'ont pas besoin d'apparaître dans la liste.

Si vous choisissez l'une des deux dernières options, veuillez documenter une recommandation pour vos utilisateurs sur l'endroit approprié de la liste pour ordonner votre directive, afin qu'ils puissent l'utiliser correctement.

<a id="classes"></a>
### Classes

Ce tableau décrit chaque classe avec des types exportés reconnus par l'adaptateur Caddyfile HTTP :

Nom de classe | Type attendu | Description
---------- | ------------- | -----------
bind | `[]string` | Adresses de liaison (bind) de l'écouteur du serveur
route | `caddyhttp.Route` | Route du gestionnaire HTTP
error_route | `*caddyhttp.Subroute` | Route de gestion des erreurs HTTP
tls.connection_policy | `*caddytls.ConnectionPolicy` | Politique de connexion TLS
tls.cert_issuer | `certmagic.Issuer` | Émetteur de certificat TLS
tls.cert_loader | `caddytls.CertificateLoader` | Chargeur de certificat TLS

<a id="server-types"></a>
## Types de serveur

Structurellement, le Caddyfile est un format simple, il peut donc y avoir différents types de formats de Caddyfile (parfois appelés "types de serveur") pour répondre à différents besoins.

Le format de Caddyfile par défaut est le Caddyfile HTTP, avec lequel vous êtes probablement familier. Ce format configure principalement l'[application `http`](/docs/modules/http) tout en pouvant potentiellement parsemer de la configuration dans d'autres parties de la structure Caddy (ex : l'application `tls` pour charger et automatiser les certificats).

Pour configurer des applications autres que HTTP, vous pouvez souhaiter implémenter votre propre adaptateur de configuration qui utilise [votre propre type de serveur](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter). L'adaptateur Caddyfile analysera alors l'entrée pour vous et vous donnera la liste des blocs de serveur et des options, et c'est à votre adaptateur de donner un sens à cette structure et de la transformer en une configuration JSON.
