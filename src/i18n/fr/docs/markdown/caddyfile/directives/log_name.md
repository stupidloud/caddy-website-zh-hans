---
title: log_name (directive Caddyfile)
---

# log_name

Surcharge le nom du logger à utiliser pour une requête lors de l'écriture des journaux d'accès avec la [directive `log`](log).

Cette directive est utile lorsque vous souhaitez journaliser des requêtes dans des fichiers différents selon une condition, comme le chemin ou la méthode de la requête.

Plus d'un nom de logger peut être spécifié, de sorte que le journal de la requête soit envoyé à plusieurs loggers correspondants.

Ceci est souvent associé à l'option [`no_hostname`](log#no_hostname) de la directive `log`, qui empêche le logger d'être associé à l'un des noms d'hôte du bloc de site, afin que seules les requêtes définissant `log_name` envoient des journaux à ce logger.


## Syntaxe

```caddy-d
log_name [<matcher>] <noms...>
```


## Exemples

Vous pourriez vouloir journaliser les requêtes dans des fichiers différents, par exemple journaliser les vérifications de santé (health checks) dans un fichier séparé des journaux d'accès principaux.

L'utilisation de `no_hostname` dans un bloc `log` empêche le logger d'être associé à l'un des noms d'hôte du bloc de site (ici `localhost`), afin que seules les requêtes ayant `log_name` réglé sur le nom de ce logger reçoivent les journaux.

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Sain"
	}

	handle {
		respond "Bonjour le monde"
	}
}
```
