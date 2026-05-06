---
title: handle (directive Caddyfile)
---

# handle

Évalue un groupe de directives de manière mutuellement exclusive par rapport aux autres blocs `handle` au même niveau d'imbrication.

En d'autres termes, lorsque plusieurs directives `handle` apparaissent à la suite, seul le premier bloc `handle` *correspondant* sera évalué. Un bloc handle sans sélecteur agit comme une route de *repli* (fallback).

Les directives `handle` sont triées selon l'[algorithme de tri des directives](/docs/caddyfile/directives#sorting-algorithm) en fonction de leurs sélecteurs. La directive [`handle_path`](handle_path) est un cas particulier qui se trie avec la même priorité qu'un `handle` possédant un sélecteur de chemin.

Les blocs handle peuvent être imbriqués si nécessaire. Seules les directives de gestionnaire HTTP peuvent être utilisées à l'intérieur des blocs handle.

## Syntaxe

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** est une liste de directives de gestionnaire HTTP ou de blocs de directives, une par ligne, tout comme elles seraient utilisées en dehors d'un bloc handle.



## Directives similaires

Il existe d'autres directives pouvant envelopper des directives de gestionnaire HTTP, mais chacune a son utilité selon le comportement que vous souhaitez exprimer :

- [`handle_path`](handle_path) fait la même chose que `handle`, mais il supprime un préfixe de la requête avant d'exécuter ses gestionnaires.

- [`handle_errors`](handle_errors) est comme `handle`, mais il n'est invoqué que lorsque Caddy rencontre une erreur pendant le traitement de la requête.

- [`route`](route) enveloppe d'autres directives comme le fait `handle`, mais avec deux distinctions :
  1. les blocs route ne sont pas mutuellement exclusifs entre eux,
  2. les directives à l'intérieur d'une route ne sont pas [réordonnées](/docs/caddyfile/directives#directive-order), vous offrant plus de contrôle si nécessaire.



## Exemples

Gérer les requêtes dans `/foo/` avec le serveur de fichiers statiques, et les autres requêtes avec le proxy inverse :

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

Vous pouvez mélanger `handle` et [`handle_path`](handle_path) dans le même site, et ils seront toujours mutuellement exclusifs entre eux :

```caddy
example.com {
	handle_path /foo/* {
		# Le préfixe "/foo" est supprimé du chemin
	}

	handle /bar/* {
		# Le chemin conserve "/bar"
	}
}
```

Vous pouvez imbriquer des blocs `handle` pour créer une logique de routage plus complexe :

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Ce bloc ne correspond qu'aux chemins sous /foo/bar
		}

		handle {
			# Ce bloc correspond à tout le reste sous /foo/
		}
	}

	handle {
		# Ce bloc correspond à tout le reste (agit comme repli)
	}
}
```
