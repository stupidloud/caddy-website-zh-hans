---
title: uri (directive Caddyfile)
---

# uri

Manipule l'URI d'une requête. Elle peut supprimer un préfixe/suffixe de chemin ou remplacer des sous-chaînes sur l'intégralité de l'URI.

Cette directive est distincte de [`rewrite`](rewrite) dans le sens où `uri` modifie l'URI de manière *différentielle*, plutôt que de la réinitialiser vers quelque chose de complètement différent comme le fait `rewrite`. Alors que `rewrite` est traitée de manière spéciale comme une redirection interne, `uri` n'est qu'un middleware supplémentaire.


## Syntaxe

Plusieurs opérations différentes sont supportées :

```caddy-d
uri [<matcher>] strip_prefix <cible>
uri [<matcher>] strip_suffix <cible>
uri [<matcher>] replace      <cible> <remplacement> [<limite>]
uri [<matcher>] path_regexp  <cible> <remplacement>
uri [<matcher>] query        [-|+]<param> [<valeur>]
uri [<matcher>] query {
	<param> [<valeur>] [<remplacement>]
	...
}
```

Le premier argument (hors sélecteur) spécifie l'opération :

- **strip_prefix** supprime le préfixe du chemin.

- **strip_suffix** supprime le suffixe du chemin.

- **replace** effectue un remplacement de sous-chaîne sur l'intégralité de l'URI.

	- **&lt;cible&gt;** est le préfixe, le suffixe, ou la chaîne de recherche / expression régulière. S'il s'agit d'un préfixe, le slash initial peut être omis, car les chemins commencent toujours par un slash.

	- **&lt;remplacement&gt;** est la chaîne de remplacement. Supporte l'utilisation de groupes de capture avec la syntaxe `$nom` ou `${nom}`, ou avec un numéro pour l'index, tel que `$1`. Consultez la [documentation Go](https://golang.org/pkg/regexp/#Regexp.Expand) pour les détails. Si la valeur de remplacement est `""`, alors le texte correspondant est supprimé.

	- **&lt;limite&gt;** est une limite optionnelle du nombre maximum de remplacements.

- **path_regexp** effectue un remplacement par expression régulière sur la portion chemin de l'URI.

	- **&lt;cible&gt;** est le préfixe, le suffixe, ou la chaîne de recherche / expression régulière. S'il s'agit d'un préfixe, le slash initial peut être omis, car les chemins commencent toujours par un slash.

	- **&lt;remplacement&gt;** est la chaîne de remplacement. Supporte l'utilisation de groupes de capture avec la syntaxe `$nom` ou `${nom}`, ou avec un numéro pour l'index, tel que `$1`. Consultez la [documentation Go](https://golang.org/pkg/regexp/#Regexp.Expand) pour les détails. Si la valeur de remplacement est `""`, alors le texte correspondant est supprimé.

- **query** effectue des manipulations sur la requête d'URI (query), avec le mode dépendant du préfixe du nom du paramètre ou du nombre d'arguments. Un bloc peut être utilisé pour spécifier plusieurs opérations à la fois, groupées et effectuées dans cet ordre : renommer (rename) 🡒 définir (set) 🡒 ajouter (append) 🡒 remplacer (replace) 🡒 supprimer (delete).

	- Sans préfixe, le paramètre est défini avec la valeur donnée dans la requête.
	
	  Par exemple, `uri query foo bar` définira la valeur du paramètre `foo` à `bar`.

	- Préfixez par `-` pour supprimer le paramètre de la requête.
	
	  Par exemple, `uri query -foo` supprimera le paramètre `foo` de la requête.

	- Préfixez par `+` pour ajouter un paramètre à la requête, avec la valeur donnée. Cela n'écrasera *pas* un paramètre existant de même nom (omettez le `+` pour écraser).
	
	  Par exemple, `uri query +foo bar` ajoutera `foo=bar` à la requête.

	- Un paramètre avec `>` à l'intérieur renommera le paramètre vers la valeur après le `>`. 
	
	  Par exemple, `uri query foo>bar` renommera le paramètre `foo` en `bar`.

	- Avec trois arguments, un remplacement par expression régulière de la valeur de la requête est effectué, où le premier argument est le nom du paramètre de requête, le second est la valeur recherchée, et le troisième est le remplacement. Le premier argument (nom du paramètre) peut être `*` pour effectuer le remplacement sur tous les paramètres de requête.
	
	  Supporte l'utilisation de groupes de capture avec la syntaxe `$nom` ou `${nom}`, ou avec un numéro pour l'index, tel que `$1`. Consultez la [documentation Go](https://golang.org/pkg/regexp/#Regexp.Expand) pour les détails. Si la valeur de remplacement est `""`, alors le texte correspondant est supprimé.
	
	  Par exemple, `uri query foo ^(ba)r $1z` remplacerait la valeur du paramètre `foo`, si celle-ci commençait par `bar`, la valeur résultante devenant `baz`.

Les mutations d'URI se produisent sur la forme normalisée ou déséchappée de l'URI. Cependant, des séquences d'échappement peuvent être utilisées dans les motifs de préfixe ou de suffixe pour ne faire correspondre que ces échappements littéraux à ces positions dans le chemin de la requête. Par exemple, `uri strip_prefix /a/b` réécrira à la fois `/a/b/c` et `/a%2Fb/c` en `/c` ; et `uri strip_prefix /a%2Fb` réécrira `/a%2Fb/c` en `/c`, mais ne correspondra pas à `/a/b/c`.

Le chemin d'URI est nettoyé des points de traversée de répertoires avant les modifications. De plus, les slashes multiples (tels que `//`) sont fusionnés sauf si la `<cible>` contient également des slashes multiples.

## Directives similaires

D'autres directives peuvent également manipuler l'URI de la requête.

- [`rewrite`](rewrite) modifie l'intégralité du chemin et de la requête vers une nouvelle valeur au lieu de ne modifier que partiellement la valeur.

- [`handle_path`](handle_path) fait la même chose que [`handle`](handle), mais il supprime un préfixe de la requête avant de lancer ses gestionnaires. Peut être utilisé à la place de `uri strip_prefix` pour éliminer une ligne de configuration supplémentaire dans de nombreux cas.


## Exemples

Supprimer `/api` au début de tous les chemins de requête :

```caddy-d
uri strip_prefix /api
```

Supprimer `.php` à la fin de tous les chemins de requête :

```caddy-d
uri strip_suffix .php
```

Remplacer "/docs/" par "/v1/docs/" dans n'importe quelle URI de requête :

```caddy-d
uri replace /docs/ /v1/docs/
```

Réduire tous les slashes répétés dans le chemin de la requête (mais pas dans la requête d'URI) à un seul slash :

```caddy-d
uri path_regexp /{2,} /
```

Définir la valeur du paramètre de requête `foo` à `bar` :

```caddy-d
uri query foo bar
```

Supprimer le paramètre `foo` de la requête :

```caddy-d
uri query -foo
```

Renommer le paramètre de requête `foo` en `bar` :

```caddy-d
uri query foo>bar
```

Ajouter le paramètre `bar` à la requête :

```caddy-d
uri query +foo bar
```

Remplacer la valeur du paramètre de requête `foo` (si elle commence par `bar`) par `baz` :

```caddy-d
uri query foo ^(ba)r $1z
```

Effectuer plusieurs opérations de requête à la fois :

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
