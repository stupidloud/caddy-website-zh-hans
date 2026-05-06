---
title: php_fastcgi (directive Caddyfile)
---

<script>
ready(function() {
	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Une directive pré-configurée qui proxifie les requêtes vers un serveur PHP FastCGI tel que php-fpm.

- [Syntaxe](#syntax)
- [Forme étendue](#expanded-form)
  - [Explication](#explanation)
- [Exemples](#examples)

Le [`reverse_proxy`](reverse_proxy) de Caddy est capable de servir n'importe quelle application FastCGI, mais cette directive est conçue spécifiquement pour les applications PHP. Cette directive est un raccourci pratique, remplaçant une [configuration plus longue](#expanded-form).

Elle suppose que tout fichier `index.php` à la racine du site agit comme un routeur. Si ce n'est pas souhaitable, reconfigurez soit la [sous-directive `try_files`](#try_files) pour modifier le comportement de réécriture par défaut, soit prenez la [forme étendue](#expanded-form) comme base et personnalisez-la selon vos besoins.

En plus des sous-directives listées ci-dessous, cette directive supporte également toutes les sous-directives de [`reverse_proxy`](reverse_proxy#syntax). Par exemple, vous pouvez activer l'équilibrage de charge et les vérifications de santé.

**La plupart des applications PHP modernes fonctionnent parfaitement sans sous-directives supplémentaires ni personnalisation.** Les sous-directives ne sont généralement utilisées que dans certains cas particuliers ou avec des applications PHP héritées (legacy).


<a id="syntax"></a>
## Syntaxe

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <chemin>
	split <sous-chaînes...>
	index <nom_fichier>|off
	try_files <fichiers...>
	env [<cle> <valeur>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <durée>
	read_timeout  <durée>
	write_timeout <durée>

	<toutes les autres sous-directives de reverse_proxy...>
}
```

- **<php-fpm_gateways...>** sont les [adresses](/docs/conventions#network-addresses) des serveurs FastCGI. Typiquement, soit un socket TCP, soit un fichier de socket unix.

- **root** <span id="root"/> définit le dossier racine du site. Il est recommandé de toujours utiliser la [directive `root`](root) conjointement avec `php_fastcgi`, mais surcharger ceci peut être utile lorsque votre amont PHP-FPM utilise une racine différente de celle de Caddy (voir [un exemple](#docker)). Par défaut, utilise la valeur de la [directive `root`](root) si elle est présente, sinon le répertoire de travail actuel de Caddy.

- **split** <span id="split"/> définit les sous-chaînes pour découper l'URI en deux parties. La première sous-chaîne correspondante sera utilisée pour séparer les "infos de chemin" (path info) du chemin. La première partie est suffixée avec la sous-chaîne correspondante et sera considérée comme le nom de la ressource réelle (script CGI). La seconde partie sera définie dans `PATH_INFO` pour que le script CGI puisse l'utiliser. Par défaut : `.php`.

- **index** <span id="index"/> spécifie le nom du fichier à traiter comme fichier d'index du répertoire. Cela affecte le sélecteur de fichier dans la [forme étendue](#expanded-form). Par défaut : `index.php`. Peut être réglé sur `off` pour désactiver le repli de réécriture vers `index.php` lorsqu'un fichier correspondant n'est pas trouvé.

- **try_files** <span id="try_files"/> spécifie une surcharge pour la réécriture par défaut. Voir la [directive `try_files`](try_files) pour les détails. Par défaut : `{path} {path}/index.php index.php`.

- **env** <span id="env"/> définit une variable d'environnement supplémentaire à la valeur donnée. Peut être spécifiée plusieurs fois pour plusieurs variables d'environnement. Par défaut, toutes les variables d'environnement FastCGI pertinentes sont déjà définies (incluant les en-têtes HTTP) mais vous pouvez en ajouter ou les surcharger selon vos besoins. 

- **resolve_root_symlink** <span id="resolve_root_symlink"/> lorsque le répertoire [`root`](#root) est un lien symbolique (symlink), ceci permet de le résoudre vers sa valeur réelle. C'est parfois utilisé comme stratégie de déploiement, en changeant simplement le lien symbolique pour pointer vers la nouvelle version dans un autre répertoire. Désactivé par défaut pour éviter les appels système répétés.

- **capture_stderr** <span id="capture_stderr"/> active la capture et la journalisation de tout message envoyé par le serveur fastcgi amont sur `stderr`. La journalisation se fait au niveau `WARN` par défaut. Si la réponse a un statut `4xx` ou `5xx`, le niveau `ERROR` sera utilisé à la place. Par défaut, `stderr` est ignoré.

- **dial_timeout** <span id="dial_timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit le temps d'attente lors de la connexion au socket amont. Par défaut : `3s`.

- **read_timeout** <span id="read_timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit le temps d'attente lors de la lecture depuis l'amont FastCGI. Par défaut : pas de délai d'expiration.

- **write_timeout** <span id="write_timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit le temps d'attente lors de l'envoi vers l'amont FastCGI. Par défaut : pas de délai d'expiration.


Puisque cette directive est une enveloppe pré-configurée autour d'un reverse proxy, vous pouvez utiliser n'importe quelle sous-directive de [`reverse_proxy`](reverse_proxy#syntax) pour la personnaliser.


<a id="expanded-form"></a>
## Forme étendue

La directive `php_fastcgi` (sans sous-directives) est identique à la configuration suivante. La plupart des applications PHP modernes fonctionnent bien avec ce préréglage. Si la vôtre ne le fait pas, n'hésitez pas à vous inspirer de ceci et à le personnaliser selon vos besoins au lieu d'utiliser le raccourci `php_fastcgi`.

```caddy-d
route {
	# Ajouter le slash final pour les requêtes de répertoires
	# Cette redirection est automatiquement désactivée si "{http.request.uri.path}/index.php"
	# n'apparaît pas dans la liste try_files
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Si le fichier demandé n'existe pas, essayer les fichiers d'index et supposer quindex.php existe toujours
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# Proxifier les fichiers PHP vers le répondeur FastCGI
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```


<a id="explanation"></a>
### Explication

- La première section s'occupe de la canonisation du chemin de la requête. L'objectif est de s'assurer que les requêtes ciblant un répertoire sur le disque ont bien le slash final `/` ajouté au chemin de la requête, afin qu'une seule URL soit valide pour les requêtes vers ce répertoire.

  Cette canonisation n'a lieu que si la sous-directive `try_files` contient `{path}/index.php` (le défaut).

  Ceci est effectué en utilisant un sélecteur de requête qui ne correspond qu'aux requêtes ne se terminant *pas* par un slash, et qui pointent vers un répertoire sur le disque contenant un fichier `index.php` ; s'il y a correspondance, une redirection HTTP 308 est effectuée avec le slash final ajouté. Ainsi par exemple, une requête avec le chemin `/foo` serait redirigée vers `/foo/` (en ajoutant un `/`, pour canoniser le chemin vers le répertoire), si `/foo/index.php` existe sur le disque.

- La section suivante s'occupe d'effectuer des réécritures de chemin selon qu'un fichier correspondant existe sur le disque. Cela a également pour effet secondaire de mémoriser la partie du chemin après `.php` (si le chemin de la requête contenait `.php`). C'est important pour que Caddy puisse définir correctement les variables d'environnement FastCGI.

  - D'abord, il vérifie si `{path}` est un fichier existant sur le disque. Si oui, il réécrit vers ce chemin. Cela court-circuite le reste, et garantit que les requêtes vers des fichiers qui *existent* sur le disque ne soient pas réécrites autrement (voir étapes suivantes). Ainsi si par exemple vous avez un fichier `/js/app.js` sur le disque, alors la requête vers ce chemin restera inchangée.

  - Ensuite, il vérifie si `{path}/index.php` est un fichier existant sur le disque. Si oui, il réécrit vers ce chemin. Pour les requêtes vers un répertoire comme `/foo/`, il cherchera alors `/foo//index.php` (qui est normalisé en `/foo/index.php`), et réécrira la requête vers ce chemin s'il existe. Ce comportement est parfois utile si vous faites tourner une autre application PHP dans un sous-répertoire de votre racine web.

  - Enfin, il réécrira toujours vers `index.php` (il existe presque toujours pour les applications PHP modernes). Cela permet à votre application PHP de gérer toute requête pour des chemins ne pointant pas vers des fichiers sur le disque, en utilisant le script `index.php` comme point d'entrée.

- Et enfin, la dernière section est ce qui proxifie réellement la requête vers votre service PHP FastCGI (ou PHP-FPM) pour exécuter votre code PHP. Le sélecteur de requête ne correspondra qu'aux requêtes se terminant par `.php`, ainsi tout fichier qui n'est *pas* un script PHP et qui *existe* sur le disque ne sera *pas* traité par cette directive, et continuera dans la chaîne.

La directive `php_fastcgi` n'est généralement pas suffisante seule. Elle devrait presque toujours être associée à la [directive `root`](root) pour définir l'emplacement de vos fichiers sur le disque (pour les applications PHP modernes, cela peut être `/var/www/html/public`, où le répertoire `public` est celui contenant votre `index.php`), et à la [directive `file_server`](file_server) pour servir vos fichiers statiques (vos JS, CSS, images, etc.) qui ne sont pas gérés par cette directive et qui ont continué dans la chaîne.



<a id="examples"></a>
## Exemples

Proxifier toutes les requêtes PHP vers un répondeur FastCGI écoutant sur `127.0.0.1:9000` :

```caddy-d
php_fastcgi 127.0.0.1:9000
```

Identique, mais uniquement pour les requêtes sous `/blog/` :

```caddy-d
php_fastcgi /blog/* localhost:9000
```

Lors de l'utilisation de PHP-FPM écoutant via un socket unix :

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

La [directive `root`](root) est presque toujours utilisée pour spécifier le répertoire contenant les scripts PHP, et la [directive `file_server`](file_server) pour servir les fichiers statiques :

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Lors du service de plusieurs applications PHP avec Caddy, la racine web de chaque application doit être différente afin que Caddy puisse lire et servir vos fichiers statiques séparément et détecter si les fichiers PHP existent.

Si vous utilisez Docker, vos conteneurs PHP-FPM auront souvent les fichiers montés à la même racine. Dans ce cas, la solution est de monter les fichiers dans votre conteneur Caddy dans des répertoires différents, puis d'utiliser la [sous-directive `root`](#root) pour définir la racine de chaque conteneur :

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Pour un site PHP qui n'utilise pas `index.php` comme point d'entrée, vous pouvez vous replier sur l'émission d'une erreur `404` à la place. L'erreur peut être capturée et gérée avec la [directive `handle_errors`](handle_errors) :

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
