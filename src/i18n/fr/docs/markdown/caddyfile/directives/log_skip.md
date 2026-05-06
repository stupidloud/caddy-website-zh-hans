---
title: log_skip (directive Caddyfile)
---

# log_skip

Ignore la journalisation des accès pour les requêtes correspondantes.

Ceci doit être utilisé aux côtés de la [directive `log`](log) pour ignorer la journalisation des requêtes qui ne sont pas pertinentes pour vos besoins.

Avant la v2.8.0, cette directive s'appelait `skip_log`, mais a été renommée pour plus de cohérence avec les autres directives.


## Syntaxe

```caddy-d
log_skip [<matcher>]
```


## Exemples

Ignorer la journalisation des accès pour les fichiers statiques stockés dans un sous-chemin :

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


Ignorer la journalisation des accès pour les requêtes correspondant à un motif ; dans ce cas, pour les fichiers avec des extensions particulières :

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


Le sélecteur n'est pas nécessaire s'il se trouve dans une route possédant déjà un sélecteur. Par exemple avec un bloc handle pour un serveur de fichiers pour un sous-chemin particulier :

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
