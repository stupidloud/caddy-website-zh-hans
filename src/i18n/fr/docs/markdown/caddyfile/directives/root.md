---
title: root (directive Caddyfile)
---

# root

Définit le chemin racine du site, utilisé par divers sélecteurs et directives qui accèdent au système de fichiers. Si non défini, la racine par défaut du site est le répertoire de travail actuel.

Plus précisément, cette directive définit l'espace réservé `{http.vars.root}`. Elle est mutuellement exclusive avec les autres directives `root` du même bloc, il est donc sûr de définir plusieurs racines avec des sélecteurs qui s'intersectent : elles ne cascadent pas et ne s'écrasent pas entre elles.

Cette directive n'active pas automatiquement le service de fichiers statiques, elle est donc souvent utilisée conjointement avec la [directive `file_server`](file_server) ou la [directive `php_fastcgi`](php_fastcgi).


## Syntaxe

```caddy-d
root [<matcher>] <chemin>
```

- **&lt;chemin&gt;** est le chemin à utiliser comme racine du site.

Avant la v2.8.0, l'argument `<chemin>` pouvait être confondu par l'analyseur avec un [jeton de sélecteur](/docs/caddyfile/matchers#syntax) s'il commençait par `/`, il était donc nécessaire de spécifier un jeton de sélecteur générique (`*`).


## Exemples

Définir la racine du site à `/home/bob/public_html` (suppose que Caddy s'exécute avec l'utilisateur `bob`) :

<aside class="tip">

Si vous faites tourner Caddy en tant que service systemd, la lecture de fichiers depuis `/home` ne fonctionnera pas, car l'utilisateur `caddy` n'a pas la permission "exécution" sur le répertoire `/home` (nécessaire pour la traversée). Il est recommandé de placer vos fichiers dans `/srv` ou `/var/www/html` à la place.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Notez qu'avant la v2.8.0, un [sélecteur générique](/docs/caddyfile/matchers#wildcard-matchers) était requis ici car le premier argument est ambigu avec un [sélecteur de chemin](/docs/caddyfile/matchers#path-matchers), ex: `root * /srv`, mais cela peut désormais être simplifié en `root /srv`.

</aside>


Définir la racine du site à `public_html` (relatif au répertoire de travail actuel) pour toutes les requêtes :

```caddy-d
root public_html
```

Changer la racine du site uniquement pour les requêtes dans `/foo/*` :

```caddy-d
root /foo/* /home/user/public_html/foo
```

La directive `root` est couramment associée à [`file_server`](file_server) pour servir des fichiers statiques et/ou avec [`php_fastcgi`](php_fastcgi) pour servir un site PHP :

```caddy
example.com {
	root /srv
	file_server
}
```
