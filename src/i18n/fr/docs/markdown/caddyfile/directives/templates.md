---
title: templates (directive Caddyfile)
---

# templates

Exécute le corps de la réponse en tant que document [modèle (template)](/docs/modules/http.handlers.templates). Les modèles fournissent des primitives fonctionnelles pour créer des pages dynamiques simples. Les fonctionnalités incluent des sous-requêtes HTTP, des inclusions de fichiers HTML, le rendu de Markdown, l'analyse de JSON, des structures de données de base, de l'aléatoire, la gestion du temps, et bien plus encore.


## Syntaxe

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <delim_ouvrant> <delim_fermant>
	root    <chemin>
	extensions {
		<nom> {
			...
		}
	}
}
```

- **mime** sont les types MIME sur lesquels le middleware templates agira ; toute réponse n'ayant pas un `Content-Type` éligible ne sera pas évaluée en tant que modèle.

  Par défaut : `text/html text/plain`.

- **between** sont les délimiteurs d'ouverture et de fermeture pour les actions des modèles. Vous pouvez les modifier s'ils interfèrent avec le reste de votre document.

  Par défaut : `{{printf "{{ }}"}}`.

- **root** est la racine du site, lors de l'utilisation de fonctions qui accèdent au système de fichiers.

  Par défaut, utilise la racine du site définie par la [directive `root`](root), ou le répertoire de travail actuel si elle n'est pas définie.

- **extensions** vous permet d'enregistrer des fonctions de modèle personnalisées fournies par des modules dans l'espace de noms `http.handlers.templates.functions.*`.

  Chaque sous-directive à l'intérieur du bloc correspond à un nom de module. Ces modules peuvent ajouter des fonctions personnalisées à la map des fonctions de modèles, typiquement utilisées pour implémenter des composants réutilisables. Cette fonctionnalité est principalement destinée aux plugins.

La documentation des fonctions de modèles intégrées peut être consultée dans le [module templates](/docs/modules/http.handlers.templates#docs).



## Exemples

Pour un exemple complet de site utilisant les modèles pour servir du markdown, jetez un œil au code source de [ce site même](https://github.com/caddyserver/website) ! Plus précisément, regardez le [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) et [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html).

Activer les modèles pour un site statique :

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

Pour servir une réponse statique simple utilisant un modèle, assurez-vous de définir le `Content-Type` :

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `L'année actuelle est : {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Utilisation d'une extension de modèle (plugin) :

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# Nécessite le plugin caddy-hitcounter :
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
