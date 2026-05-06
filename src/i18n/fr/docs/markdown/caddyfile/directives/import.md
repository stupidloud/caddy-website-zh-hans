---
title: import (directive Caddyfile)
---

# import

Inclut un [extrait (snippet)](/docs/caddyfile/concepts#snippets) ou un fichier, en remplaçant cette directive par le contenu de l'extrait ou du fichier.

Cette directive est un cas particulier : elle est évaluée avant que la structure ne soit analysée, et elle peut apparaître n'importe où dans le Caddyfile.

## Syntaxe

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** est le nom de fichier, le motif glob, ou le nom de l'[extrait (snippet)](/docs/caddyfile/concepts#snippets) à inclure. Son contenu remplacera cette ligne comme si le contenu de ce fichier était apparu ici dès le départ.

  C'est une erreur si un fichier spécifique ne peut pas être trouvé, mais un motif glob vide n'est pas une erreur.

  Si vous importez un fichier spécifique, un avertissement sera émis si le fichier est vide.

  Si le motif est un nom de fichier ou un glob, il est toujours relatif au fichier dans lequel l' `import` apparaît.

  Si vous utilisez un motif glob `*` comme dernier segment de chemin, les fichiers cachés (c'est-à-dire les fichiers commençant par un `.`) sont ignorés. Pour importer les fichiers cachés, utilisez `.*` comme dernier segment.
- **&lt;args...&gt;** est une liste optionnelle d'arguments à passer aux jetons importés. Cet espace réservé est un cas particulier et est évalué au moment de l'analyse du Caddyfile, et non à l'exécution. Ils peuvent être utilisés sous diverses formes, de manière similaire à la [syntaxe des tranches (slices) de Go](https://gobyexample.com/slices) :
  - `{args[n]}` où `n` est l'index positionnel du paramètre commençant par 0
  - `{args[:]}` où tous les arguments sont insérés
  - `{args[:m]}` où les arguments avant `m` sont insérés
  - `{args[n:]}` où les arguments commençant à `n` sont insérés
  - `{args[n:m]}` où les arguments dans la plage entre `n` et `m` sont insérés

  Pour les formes qui insèrent plusieurs jetons, l'espace réservé **doit** être un [jeton](/docs/caddyfile/concepts#tokens-and-quotes) à lui seul, il ne peut pas faire partie d'un autre jeton. En d'autres termes, il doit avoir des espaces autour de lui, et ne peut pas être entre guillemets.

  Notez qu'avant la v2.7.0, la syntaxe était `{args.N}` mais cette forme a été dépréciée en faveur de la syntaxe plus flexible ci-dessus.

⚠️ <i>Expérimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** est un bloc optionnel à passer aux jetons importés. Cet espace réservé est un cas particulier, et est évalué récursivement au moment de l'analyse du Caddyfile, et non à l'exécution. Ils peuvent être utilisés sous deux formes :
  - `{block}` où le contenu de l'intégralité du bloc fourni sera substitué à l'espace réservé
  - `{blocks.key}` où `key` est le premier jeton d'un paramètre à l'intérieur du bloc fourni


## Exemples

Importer tous les fichiers dans un dossier adjacent `sites-enabled` (sauf les fichiers cachés) :

```caddy-d
import sites-enabled/*
```

Importer un extrait qui définit des en-têtes CORS en utilisant un argument d'importation :

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Importer un extrait qui prend une liste de serveurs d'amont (upstreams) de proxy comme arguments :

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Importer un extrait qui crée un proxy avec une règle de réécriture de préfixe comme premier argument :

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Expérimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Importer un extrait qui répond avec un message "hello world" et un type de contenu configurables :

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Importer un extrait qui fournit des options extensibles pour un proxy inverse :

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Importer un extrait qui sert n'importe quel ensemble de directives, mais avec un middleware pré-chargé :

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
