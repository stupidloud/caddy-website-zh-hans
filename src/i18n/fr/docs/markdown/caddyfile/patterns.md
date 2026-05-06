---
title: Modèles courants de Caddyfile
---

# Modèles courants de Caddyfile

Cette page présente quelques configurations Caddyfile complètes et minimales pour des cas d'utilisation courants. Elles peuvent servir de points de départ utiles pour vos propres documents Caddyfile.

Il ne s'agit pas de solutions prêtes à l'emploi (drop-in) ; vous devrez personnaliser votre nom de domaine, vos ports/sockets, vos chemins de répertoires, etc. Elles sont destinées à illustrer certains des modèles de configuration les plus fréquents.

- [Serveur de fichiers statiques](#static-file-server)
- [Proxy inverse](#reverse-proxy)
- [PHP](#php)
- [Rediriger le sous-domaine `www.`](#redirect-www-subdomain)
- [Slashes de fin (Trailing slashes)](#trailing-slashes)
- [Certificats wildcard](#wildcard-certificates)
- [Applications monopage (SPAs)](#single-page-apps-spas)
- [Caddy proxifiant vers un autre Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## Serveur de fichiers statiques

```caddy
example.com {
	root /var/www
	file_server
}
```

Comme d'habitude, la première ligne est l'adresse du site. La [directive `root`](/docs/caddyfile/directives/root) spécifie le chemin vers la racine du site (le `*` signifie qu'il correspond à toutes les requêtes, afin de lever l'ambiguïté avec un [sélecteur de chemin](/docs/caddyfile/matchers#path-matchers)) — modifiez le chemin vers votre site s'il ne s'agit pas du répertoire de travail actuel. Enfin, nous activons le [serveur de fichiers statiques](/docs/caddyfile/directives/file_server).



<a id="reverse-proxy"></a>
## Proxy inverse

Proxifier toutes les requêtes :

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Proxifier uniquement les requêtes dont le chemin commence par `/api/` et servir des fichiers statiques pour tout le reste :

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Ceci utilise un [sélecteur de requête](/docs/caddyfile/matchers#syntax) pour ne faire correspondre que les requêtes commençant par `/api/` et les proxifier vers le backend. Toutes les autres requêtes seront servies depuis la racine ([`root`](/docs/caddyfile/directives/root)) du site avec le [serveur de fichiers statiques](/docs/caddyfile/directives/file_server). Cela repose également sur le fait que `reverse_proxy` est placé plus haut dans l'[ordre des directives](/docs/caddyfile/directives#directive-order) que `file_server`.

Retrouvez de nombreux autres [exemples de `reverse_proxy` ici](/docs/caddyfile/directives/reverse_proxy#examples).



<a id="php"></a>
## PHP

### PHP-FPM

Avec un service PHP FastCGI en cours d'exécution, une configuration comme celle-ci fonctionne pour la plupart des applications PHP modernes :

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

Adaptez la racine du site en conséquence ; cet exemple suppose que le répertoire web (webroot) de votre application PHP se trouve dans un dossier `public` — les requêtes pour des fichiers existant sur le disque seront servies par [`file_server`](/docs/caddyfile/directives/file_server), et tout le reste sera routé vers `index.php` pour être traité par l'application PHP.

Vous pouvez parfois utiliser un socket unix pour vous connecter à PHP-FPM :

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

La [directive `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) est en réalité un raccourci pour [plusieurs morceaux de configuration](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

Alternativement, vous pouvez utiliser [FrankenPHP](https://frankenphp.dev/), qui est une distribution de Caddy appelant PHP directement via CGO (liaisons Go vers C). Cela peut être jusqu'à 4 fois plus rapide qu'avec PHP-FPM, et encore mieux si vous pouvez utiliser le mode worker.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-www-subdomain"></a>
## Rediriger le sous-domaine `www.`

Pour **ajouter** le sous-domaine `www.` avec une redirection HTTP :

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Pour le **supprimer** :

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Pour le supprimer pour **plusieurs domaines** à la fois ; ceci utilise les espaces réservés `{labels.*}` qui sont les segments du nom d'hôte, indexés par `0` depuis la droite (ex: `0`=`com`, `1`=`example-one`, `2`=`www`) :

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## Slashes de fin (Trailing slashes)

Vous n'aurez généralement pas besoin de configurer cela vous-même ; la [directive `file_server`](/docs/caddyfile/directives/file_server) ajoutera ou supprimera automatiquement les slashes de fin des requêtes par le biais de redirections HTTP, selon que la ressource demandée est respectivement un répertoire ou un fichier.

Cependant, si vous en avez besoin, vous pouvez toujours imposer les slashes de fin avec votre config. Il y a deux façons de le faire : en interne ou en externe.

### Application interne

Ceci utilise la directive [`rewrite`](/docs/caddyfile/directives/rewrite). Caddy réécrira l'URI de manière interne pour ajouter ou supprimer le slash de fin :

```caddy
example.com {
	rewrite /ajouter     /ajouter/
	rewrite /supprimer/ /supprimer
}
```

En utilisant une réécriture, les requêtes avec et sans slash de fin seront identiques pour le reste de la chaîne.


### Application externe

Ceci utilise la directive [`redir`](/docs/caddyfile/directives/redir). Caddy demandera au navigateur de changer l'URI pour ajouter ou supprimer le slash de fin :

```caddy
example.com {
	redir /ajouter     /ajouter/
	redir /supprimer/ /supprimer
}
```

En utilisant une redirection, le client devra réémettre la requête, imposant une URI unique acceptable pour une ressource.



<a id="wildcard-certificates"></a>
## Certificats wildcard

Pour la plupart des émetteurs incluant Let's Encrypt, vous devez activer le [défi DNS ACME](/docs/automatic-https#dns-challenge) pour que Caddy automatise les certificats wildcard.

Avec le défi DNS activé, depuis Caddy 2.10, Caddy privilégiera un certificat wildcard applicable déjà configuré ou géré avant de gérer un certificat séparé pour un sous-domaine.



Si vous avez besoin de servir plusieurs sous-domaines avec le même certificat wildcard, la meilleure façon de les gérer est avec un Caddyfile comme celui-ci, en utilisant la [directive `handle`](/docs/caddyfile/directives/handle) et les [sélecteurs `host`](/docs/caddyfile/matchers#host) :

```caddy
*.example.com {
	tls {
		dns <nom_fournisseur> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo !"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar !"
	}

	# Repli pour les domaines non gérés autrement
	handle {
		abort
	}
}
```

Vous devez activer le [défi DNS ACME](/docs/automatic-https#dns-challenge) pour que Caddy gère automatiquement les certificats wildcard.



<a id="single-page-apps-spas"></a>
## Applications monopage (SPAs)

Lorsqu'une page web effectue son propre routage, les serveurs peuvent recevoir beaucoup de requêtes pour des pages qui n'existent pas côté serveur, mais qui sont affichables côté client tant que le fichier index unique est servi à la place. Les applications web conçues ainsi sont appelées SPAs, ou applications monopage.

L'idée principale est de demander au serveur de "tester les fichiers" pour voir si le fichier demandé existe côté serveur, et sinon, de se replier sur un fichier index où le client effectue le routage (généralement avec du JavaScript côté client).

Une config SPA typique ressemble généralement à ceci :

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

Si votre SPA est couplée à une API ou à d'autres points d'accès réservés au serveur, vous voudrez utiliser des blocs `handle` pour les traiter exclusivement :

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

Si votre `index.html` contient des références à vos ressources JS/CSS avec des noms de fichiers hachés, vous pourriez envisager d'ajouter un en-tête `Cache-Control` pour demander aux clients de *ne pas* le mettre en cache (afin que si les ressources changent, les navigateurs récupèrent les nouvelles). Comme la réécriture `try_files` est utilisée pour servir votre `index.html` depuis n'importe quel chemin ne correspondant pas à un autre fichier sur le disque, vous pouvez envelopper le `try_files` avec un `route` afin que le gestionnaire `header` s'exécute *après* la réécriture (il s'exécuterait normalement avant en raison de l'[ordre des directives](/docs/caddyfile/directives#directive-order)) :

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Caddy proxifiant vers un autre Caddy

Si vous avez une instance Caddy accessible publiquement (appelons-la "front"), et une autre instance Caddy dans votre réseau privé (appelons-la "back") servant votre application réelle, vous pouvez utiliser la [directive `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) pour transmettre les requêtes.

Instance front :

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Instance back :

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Cet exemple sert deux domaines différents, les proxifiant tous deux vers la même instance Caddy "back", sur le port `80`. Votre instance back sert les deux domaines de manières différentes, elle est donc configurée avec deux blocs de site séparés.

- Sur le back, [`http://`](/docs/caddyfile/concepts#addresses) est utilisé pour accepter le HTTP sur le port `80`. L'instance front termine le TLS, et le trafic entre front et back se fait sur un réseau privé, il n'est donc pas nécessaire de le ré-chiffrer.

- Vous pouvez utiliser un port différent comme `8080` sur l'instance back si nécessaire ; ajoutez simplement `:8080` à chaque adresse de site sur la config du back, OU réglez l'[option globale `http_port`](/docs/caddyfile/options#http_port) sur `8080`.

- Sur le back, l'[option globale `trusted_proxies`](/docs/caddyfile/options#trusted-proxies) est utilisée pour dire à Caddy de faire confiance à l'instance front comme proxy. Cela garantit que l'IP réelle du client est préservée.

- Pour aller plus loin, vous pourriez avoir plus d'une instance back entre lesquelles vous effectuez un [équilibrage de charge](/docs/caddyfile/directives/reverse_proxy#load-balancing). Vous pourriez mettre en place du mTLS (mutual TLS) en utilisant le [`acme_server`](/docs/caddyfile/directives/acme_server) sur l'instance front de sorte qu'il agisse comme la CA pour l'instance back (utile si le trafic entre front et back traverse des réseaux non fiables).
