---
title: Sélecteurs de requête (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

# Sélecteurs de requête (Matchers)

Les **sélecteurs de requête** peuvent être utilisés pour filtrer (ou classifier) les requêtes selon divers critères.

- [Syntaxe](#syntax)
	- [Exemples](#examples)
	- [Sélecteurs génériques (Wildcards)](#wildcard-matchers)
	- [Sélecteurs de chemin](#path-matchers)
	- [Sélecteurs nommés](#named-matchers)
- [Sélecteurs standard](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


<a id="syntax"></a>
## Syntaxe

Dans le Caddyfile, un **jeton de sélecteur** suivant immédiatement la directive peut limiter la portée de cette directive. Le jeton de sélecteur peut prendre l'une de ces formes :

1. [**`*`**](#wildcard-matchers) pour correspondre à toutes les requêtes (wildcard ; par défaut).
2. [**`/chemin`**](#path-matchers) commençant par un slash pour correspondre au chemin d'une requête.
3. [**`@nom`**](#named-matchers) pour spécifier un *sélecteur nommé*.

Si une directive supporte les sélecteurs, elle apparaîtra sous la forme `[<matcher>]` dans sa documentation de syntaxe. Les jetons de sélecteur sont [généralement optionnels](/docs/caddyfile/directives#syntax), indiqués par `[ ]`. Si le jeton de sélecteur est omis, il équivaut à un sélecteur générique (`*`).


<a id="examples"></a>
#### Exemples

Cette directive s'applique à [toutes](#wildcard-matchers) les requêtes HTTP :

```caddy-d
reverse_proxy localhost:9000
```

Et ceci est identique (`*` est inutile ici) :

```caddy-d
reverse_proxy * localhost:9000
```

Mais cette directive ne s'applique qu'aux requêtes possédant un [chemin](#path-matchers) commençant par `/api/` :

```caddy-d
reverse_proxy /api/* localhost:9000
```

Pour effectuer une correspondance sur autre chose qu'un chemin, définissez un [sélecteur nommé](#named-matchers) et référencez-le en utilisant `@nom` :

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### Sélecteurs génériques (Wildcard matchers)

Le sélecteur générique (ou "catch-all") `*` correspond à toutes les requêtes, et n'est nécessaire que si un jeton de sélecteur est requis par la syntaxe. Par exemple, si le premier argument que vous voulez donner à une directive se trouve être également un chemin, il ressemblerait exactement à un sélecteur de chemin ! Vous pouvez donc utiliser un sélecteur générique pour lever l'ambiguïté, par exemple :

```caddy-d
root * /home/www/mysite
```

Sinon, ce sélecteur n'est pas souvent utilisé. Nous recommandons généralement de l'omettre si la syntaxe ne l'exige pas.


<a id="path-matchers"></a>
### Sélecteurs de chemin (Path matchers)

Le filtrage par chemin d'URI est la manière la plus courante de sélectionner des requêtes, le sélecteur peut donc être écrit en ligne, comme ceci :

```caddy-d
redir /ancien.html /nouveau.html
```

Les jetons de sélecteur de chemin doivent commencer par un slash `/`.

**[Le filtrage de chemin](#path) est une correspondance exacte par défaut, pas par préfixe.** Vous devez ajouter un `*` pour une correspondance rapide par préfixe. Notez que `/foo*` correspondra à `/foo` et `/foo/` ainsi qu'à `/foobar` ; vous pourriez en réalité préférer `/foo/*` à la place.


<a id="named-matchers"></a>
### Sélecteurs nommés (Named matchers)

Tous les sélecteurs qui ne sont pas des sélecteurs de chemin ou génériques doivent être des sélecteurs nommés. Il s'agit d'un sélecteur défini en dehors de toute directive particulière, et qui peut être réutilisé.

Définir un sélecteur avec un nom unique vous donne plus de flexibilité, vous permettant de combiner [n'importe quel sélecteur disponible](#standard-matchers) dans un ensemble :

```caddy-d
@nom {
	...
}
```

ou, s'il n'y a qu'un seul sélecteur dans l'ensemble, vous pouvez le mettre sur la même ligne :

```caddy-d
@nom ...
```

Vous pouvez ensuite utiliser le sélecteur ainsi, en le spécifiant comme premier argument d'une directive :

```caddy-d
directive @nom
```

Par exemple, ceci proxifie les requêtes WebSocket HTTP/1.1 vers `localhost:6001`, et les autres requêtes vers `localhost:8080`. Il sélectionne les requêtes possédant un en-tête nommé `Connection` _contenant_ `Upgrade`, **et** un autre champ nommé `Upgrade` valant exactement `websocket` :

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Si l'ensemble de sélecteurs ne contient qu'un seul sélecteur, une syntaxe sur une seule ligne fonctionne également :

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

En tant que cas particulier, le [sélecteur `expression`](#expression) peut être utilisé sans spécifier son nom tant qu'un argument [entre guillemets](/docs/caddyfile/concepts#tokens-and-quotes) (l'expression CEL elle-même) suit le nom du sélecteur :

```caddy-d
@not-found `{err.status_code} == 404`
```

Comme les directives, les définitions de sélecteurs nommés doivent se trouver à l'intérieur des [blocs de site](/docs/caddyfile/concepts#structure) qui les utilisent.

Une définition de sélecteur nommé constitue un _ensemble de sélecteurs_. Les sélecteurs au sein d'un ensemble sont liés par un ET logique ; c'est-à-dire que tous doivent correspondre. Par exemple, si vous avez à la fois un sélecteur [`header`](#header) et [`path`](#path) dans l'ensemble, les deux doivent correspondre.

Plusieurs sélecteurs du même type peuvent être fusionnés (ex: plusieurs sélecteurs [`path`](#path) dans le même ensemble) en utilisant l'algèbre de Boole (ET/OU), comme décrit dans leurs sections respectives ci-dessous.

Pour une logique de sélection booléenne plus complexe, il est recommandé d'utiliser le [sélecteur `expression`](#expression) pour écrire une expression CEL, qui supporte le **et** `&&`, le **ou** `||`, et les **parenthèses** `( )`.



<a id="standard-matchers"></a>
## Sélecteurs standard

La documentation complète des sélecteurs peut être consultée [dans la documentation de chaque module de sélecteur respectif](/docs/json/apps/http/servers/routes/match/).

Les requêtes peuvent être sélectionnées des manières suivantes :


<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <plages...>

expression client_ip('<plages...>')
```

Par l'adresse IP du client. Accepte des IPs exactes ou des plages CIDR. Les zones IPv6 sont supportées.

Ce sélecteur est optimal lorsque l'option globale [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) est configurée, sinon il agit de manière identique au sélecteur [`remote_ip`](#remote-ip). Seules les requêtes provenant de proxys de confiance verront leur IP client analysée au début de la requête ; les requêtes non fiables utiliseront l'adresse IP distante du pair immédiat ou l'adresse définie via le [protocole PROXY](/docs/caddyfile/options#proxy-protocol).

En tant que raccourci, `private_ranges` peut être utilisé pour correspondre à toutes les plages privées IPv4 et IPv6. Cela équivaut à spécifier toutes ces plages : `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Il peut y avoir plusieurs sélecteurs `client_ip` par sélecteur nommé, et leurs plages seront fusionnées et liées par un OU logique.

#### Exemple :

Sélectionner les requêtes provenant d'adresses IPv4 privées :

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Ce sélecteur est couramment associé au sélecteur [`not`](#not) pour inverser la sélection. Par exemple, pour interrompre toutes les connexions provenant d'adresses IPv4 et IPv6 _publiques_ (qui est l'inverse de toutes les plages privées) :

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Bonjour, vous devez provenir d'un réseau privé !"
}
```

Dans une [expression CEL](#expression), cela ressemblerait à ceci :

```caddy-d
@mes-amis `client_ip('12.23.34.45', '23.34.45.56')`
```


<a id="expression"></a>
### expression

```caddy-d
expression <cel...>
```

Par n'importe quelle expression [CEL (Common Expression Language)](https://github.com/google/cel-spec) qui retourne `true` ou `false`.

La plupart des autres sélecteurs de requête peuvent également être utilisés dans les expressions en tant que fonctions, ce qui permet plus de flexibilité pour la logique booléenne que les expressions extérieures. Consultez la documentation de chaque sélecteur pour connaître la syntaxe supportée au sein des expressions CEL.

Les [espaces réservés (placeholders)](/docs/conventions#placeholders) Caddy (ou les [raccourcis Caddyfile](/docs/caddyfile/concepts#placeholders)) peuvent être utilisés dans ces expressions CEL, car ils sont prétraités et convertis en appels de fonction CEL classiques avant d'être interprétés par l'environnement CEL. Si un espace réservé doit être passé en tant qu'argument de chaîne à une fonction de sélecteur, alors le `{` initial doit être échappé avec un antislash `\` afin qu'il ne soit pas prétraité, par exemple `file('\{path}.md')`.

Par commodité, le nom du sélecteur peut être omis lors de la définition d'un sélecteur nommé constitué uniquement d'une expression CEL. L'expression CEL doit être [entre guillemets](/docs/caddyfile/concepts#tokens-and-quotes) (accents graves ou heredocs recommandés). Cela se lit assez bien :

```caddy-d
@mutable `{method}.startsWith("P")`
```

Dans ce cas, le sélecteur CEL est supposé par défaut.

#### Exemples :

Sélectionner les requêtes dont la méthode commence par `P`, ex: `PUT` ou `POST` :

```caddy-d
@methods expression {method}.startsWith("P")
```

Sélectionner les requêtes où le gestionnaire a retourné le code d'état d'erreur `404`, s'utiliserait conjointement avec la [directive `handle_errors`](/docs/caddyfile/directives/handle_errors) :

```caddy-d
@404 expression {err.status_code} == 404
```

Sélectionner les requêtes où le chemin correspond à l'une de deux expressions régulières différentes ; ceci n'est possible à écrire qu'en utilisant une expression, car le sélecteur [`path_regexp`](#path-regexp) ne peut normalement exister qu'une seule fois par sélecteur nommé :

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

Ou la même chose, en omettant le nom du sélecteur, et en entourant d' [accents graves](/docs/caddyfile/concepts#tokens-and-quotes) pour qu'il soit analysé comme un seul jeton :

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

Vous pouvez utiliser la [syntaxe heredoc](/docs/caddyfile/concepts#heredocs) pour écrire des expressions CEL multi-lignes :

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Bonjour l'API !"
```


---
<a id="file"></a>
### file

```caddy-d
file {
	root       <chemin>
	try_files  <fichiers...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <fichiers...>

expression `file({
	'root': '<chemin>',
	'try_files': ['<fichiers...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<fichiers...>')
```

Par fichiers.

- `root` définit le répertoire dans lequel chercher les fichiers. Par défaut, il s'agit du répertoire de travail actuel, ou de la [variable](/docs/modules/http.handlers.vars) `root` (`{http.vars.root}`) si elle est définie (peut être définie via la [directive `root`](/docs/caddyfile/directives/root)).

- `try_files` vérifie les fichiers dans sa liste qui correspondent à la politique `try_policy`.

  Pour faire correspondre des répertoires, ajoutez un slash de fin `/` au chemin. Tous les chemins de fichiers sont relatifs à la racine ([root](/docs/caddyfile/directives/root)) du site, et les [motifs glob](https://pkg.go.dev/path/filepath#Match) seront développés.

  Si la politique `try_policy` est `first_exist` (par défaut), alors le dernier élément de la liste peut être un nombre préfixé par `=` (ex: `=404`), ce qui, en dernier recours, émettra une erreur avec ce code ; l'erreur peut être capturée et gérée avec [`handle_errors`](/docs/caddyfile/directives/handle_errors).



- `try_policy` spécifie comment choisir un fichier. Par défaut : `first_exist`.

	- `first_exist` vérifie l'existence du fichier. Le premier fichier qui existe est sélectionné.

	- `first_exist_fallback` est similaire à `first_exist`, mais suppose que le dernier élément de la liste existe toujours pour éviter un accès disque.

	- `smallest_size` choisit le fichier ayant la plus petite taille.

	- `largest_size` choisit le fichier ayant la plus grande taille.

	- `most_recently_modified` choisit le fichier ayant été modifié le plus récemment.

- `split_path` provoquera le découpage du chemin au premier délimiteur de la liste trouvé dans chaque chemin de fichier à tester. Pour chaque valeur découpée, la partie gauche du découpage incluant le délimiteur lui-même sera le chemin de fichier testé. Par exemple, `/remote.php/dav/` en utilisant un délimiteur de `.php` testerait le fichier `/remote.php`. Chaque délimiteur doit apparaître à la fin d'un composant de chemin d'URI afin d'être utilisé comme délimiteur de découpage. C'est un paramètre de niche principalement utilisé lors du service de sites PHP.

Parce que `try_files` avec une politique de `first_exist` est très courant, il existe un raccourci sur une seule ligne pour cela :

```caddy-d
file <fichiers...>
```

Un sélecteur `file` vide (sans fichiers listés après lui) vérifiera si le fichier demandé — tel quel depuis l'URI, relatif à la [racine du site](/docs/caddyfile/directives/root) — existe. C'est effectivement la même chose que `file {path}`.


<aside class="tip">

Étant donné que la réécriture basée sur l'existence d'un fichier sur le disque est très courante, il existe également une [directive `try_files`](/docs/caddyfile/directives/try_files) qui est un raccourci du sélecteur `file` et d'un [gestionnaire `rewrite`](/docs/caddyfile/directives/rewrite).

</aside>


Lors d'une correspondance, quatre nouveaux espaces réservés seront rendus disponibles :

- `{file_match.relative}` Le chemin du fichier relatif à la racine. C'est souvent utile lors de la réécriture de requêtes.
- `{file_match.absolute}` Le chemin absolu du fichier correspondant, incluant la racine.
- `{file_match.type}` Le type de fichier, `file` ou `directory`.
- `{file_match.remainder}` La portion restante après le découpage du chemin du fichier (si `split_path` est configuré).


#### Exemples :

Sélectionner les requêtes où le chemin est un fichier qui existe :

```caddy-d
@file file
```

Sélectionner les requêtes où le chemin suivi de `.html` est un fichier qui existe, ou sinon, où le chemin est un fichier qui existe :

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

Même chose que ci-dessus, sauf en utilisant le raccourci sur une ligne, et en se repliant sur l'émission d'une erreur 404 si aucun fichier n'est trouvé :

```caddy-d
@html-ou-erreur file {path}.html {path} =404
```

Quelques exemples supplémentaires utilisant des [expressions CEL](#expression). Gardez à l'esprit que les espaces réservés sont prétraités et convertis en appels de fonction CEL classiques avant d'être interprétés par l'environnement CEL, la concaténation est donc utilisée ici. De plus, la forme longue doit être utilisée en cas de concaténation avec des espaces réservés en raison de limitations d'analyse actuelles :

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
<a id="header"></a>
### header

```caddy-d
header <champ> [<valeur> ...]

expression header({'<champ>': '<valeur>'})
```

Par champs d'en-tête de requête.

- `<champ>` est le nom du champ d'en-tête HTTP à vérifier.
	- S'il est préfixé par `!`, le champ ne doit pas exister pour correspondre (omettre l'argument valeur).
- `<valeur>` est la valeur que le champ doit avoir pour correspondre. Une ou plusieurs peuvent être spécifiées.
	- S'il est préfixé par `*`, il effectue une correspondance rapide par suffixe (apparaît à la fin).
	- S'il est suffixé par `*`, il effectue une correspondance rapide par préfixe (apparaît au début).
	- S'il est entouré de `*`, il effectue une correspondance rapide par sous-chaîne (apparaît n'importe où).
	- Sinon, c'est une correspondance exacte rapide.

Différents champs d'en-tête au sein d'un même ensemble sont liés par un ET. Les valeurs multiples par champ sont liées par un OU.

Notez que les champs d'en-tête peuvent être répétés et avoir des valeurs différentes. Les applications backend DOIVENT considérer que les valeurs de champs d'en-tête sont des tableaux, pas des valeurs singulières, et Caddy n'interprète pas le sens de telles ambiguïtés.

#### Exemple :

Sélectionner les requêtes avec l'en-tête `Connection` contenant `Upgrade` :

```caddy-d
@upgrade header Connection *Upgrade*
```

Sélectionner les requêtes avec l'en-tête `Foo` contenant `bar` OU `baz` :

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Sélectionner les requêtes qui ne possèdent pas du tout le champ d'en-tête `Foo` :

```caddy-d
@pas_foo header !Foo
```

En utilisant une [expression CEL](#expression), sélectionner les requêtes WebSocket en vérifiant si l'en-tête `Connection` contient `Upgrade` et si l'en-tête `Upgrade` vaut `websocket` (HTTP/2 possède l'en-tête `:protocol` pour cela) :

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<nom>] <champ> <regexp>

expression header_regexp('<nom>', '<champ>', '<regexp>')
expression header_regexp('<champ>', '<regexp>')
```

Comme [`header`](#header), mais supporte les expressions régulières.

Le langage d'expression régulière utilisé est RE2, inclus dans Go. Voir la [référence de syntaxe RE2](https://github.com/google/re2/wiki/Syntax) et l' [aperçu de la syntaxe regexp de Go](https://pkg.go.dev/regexp/syntax).

Depuis la v2.8.0, si le `nom` n'est *pas* fourni, le nom sera tiré du nom du sélecteur nommé. Par exemple, un sélecteur nommé `@foo` entraînera le nommage de ce sélecteur en `foo`. Le principal avantage de spécifier un nom est si plus d'un sélecteur regexp (ex: `header_regexp` et [`path_regexp`](#path-regexp), ou plusieurs champs d'en-tête différents) est utilisé dans le même sélecteur nommé.

Les groupes de capture peuvent être accédés via [espace réservé (placeholder)](/docs/caddyfile/concepts#placeholders) dans les directives après la sélection :
- `{re.<nom>.<groupe_capture>}` où :
  - `<nom>` est le nom de l'expression régulière,
  - `<groupe_capture>` est soit le nom soit le numéro du groupe de capture dans l'expression.

- `{re.<groupe_capture>}` sans nom, est également rempli par commodité. La mise en garde est que si plusieurs sélecteurs regexp sont utilisés à la suite, alors les valeurs des espaces réservés seront écrasées par le sélecteur suivant.

Le groupe de capture `0` est la correspondance regexp complète, `1` est le premier groupe de capture, `2` est le second, et ainsi de suite. Ainsi, `{re.foo.1}` ou `{re.1}` contiendront tous deux la valeur du premier groupe de capture.

Une seule expression régulière est supportée par champ d'en-tête, car les motifs regexp ne peuvent pas être fusionnés ; si vous en avez besoin de plus, envisagez d'utiliser un [sélecteur `expression`](#expression). Les correspondances contre plusieurs champs d'en-tête différents seront liées par un ET.

#### Exemple :

Sélectionner les requêtes où l'en-tête Cookie contient `login_` suivi d'une chaîne hexadécimale, avec un groupe de capture accessible via `{re.login.1}` ou `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Ceci peut être simplifié en omettant le nom, qui sera déduit du sélecteur nommé :

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

Ou la même chose, en utilisant une [expression CEL](#expression) :

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
<a id="host"></a>
### host

```caddy-d
host <hôtes...>

expression host('<hôtes...>')
```

Sélectionne la requête par le champ d'en-tête `Host` de la requête.

Comme la plupart des blocs de site indiquent déjà les hôtes dans l'adresse du site, ce sélecteur est plus couramment utilisé dans les blocs de site qui utilisent un nom d'hôte wildcard (voir le [modèle des certificats wildcard](/docs/caddyfile/patterns#wildcard-certificates)), mais où une logique spécifique au nom d'hôte est requise.

Plusieurs sélecteurs `host` seront liés par un OU.

#### Exemple :

Sélectionner un sous-domaine :

```caddy-d
@sub host sous.exemple.com
```

Sélectionner le domaine apex et un sous-domaine :

```caddy-d
@site host exemple.com www.exemple.com
```

Plusieurs sous-domaines en utilisant une [expression CEL](#expression) :

```caddy-d
@app `host('app1.exemple.com', 'app2.exemple.com')`
```



---
<a id="method"></a>
### method

```caddy-d
method <verbes...>

expression method('<verbes...>')
```

Par la méthode (verbe) de la requête HTTP. Les verbes doivent être en majuscules, comme `POST`. Peut correspondre à une ou plusieurs méthodes.

Plusieurs sélecteurs `method` seront liés par un OU.

#### Exemples :

Sélectionner les requêtes avec la méthode `GET` :

```caddy-d
@get method GET
```

Sélectionner les requêtes avec les méthodes `PUT` ou `DELETE` :

```caddy-d
@put-delete method PUT DELETE
```

Sélectionner les méthodes en lecture seule à l'aide d'une [expression CEL](#expression) :

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
<a id="not"></a>
### not

```caddy-d
not <sélecteur>
```

ou, pour nier plusieurs sélecteurs qui seront liés par un ET, ouvrez un bloc :

```caddy-d
not {
	<sélecteurs...>
}
```

Les résultats des sélecteurs inclus seront niés.

#### Exemples :

Sélectionner les requêtes dont les chemins ne commencent PAS par `/css/` OU `/js/`.

```caddy-d
@pas-assets {
	not path /css/* /js/*
}
```

Sélectionner les requêtes n'ayant NI :
- un préfixe de chemin `/api/`, NI
- la méthode de requête `POST`

c'est-à-dire qu'elles ne doivent avoir aucun de ceux-là pour correspondre :

```caddy-d
@avec-aucun {
	not path /api/*
	not method POST
}
```

Sélectionner les requêtes n'ayant PAS LES DEUX :
- un préfixe de chemin `/api/`, ET
- la méthode de requête `POST`

c'est-à-dire qu'elles ne doivent avoir ni l'un ni l'autre ou seulement l'un des deux pour correspondre :

```caddy-d
@sans-les-deux {
	not {
		path /api/*
		method POST
	}
}
```

Il n'y a pas d' [expression CEL](#expression) pour ce sélecteur, car vous pouvez utiliser l'opérateur `!` pour la négation à la place. Par exemple :

```caddy-d
@sans-les-deux `!path('/api*') && !method('POST')`
```

Ce qui est la même chose que ceci, en utilisant des parenthèses :

```caddy-d
@sans-les-deux `!(path('/api*') || method('POST'))`
```




---
<a id="path"></a>
### path

```caddy-d
path <chemins...>

expression path('<chemins...>')
```

Par chemin de requête (le composant chemin de l'URI de la requête). Les correspondances de chemin sont exactes mais insensibles à la casse. Des caractères génériques `*` peuvent être utilisés :

- À la fin uniquement, pour une correspondance par préfixe (`/prefixe/*`)
- Au début uniquement, pour une correspondance par suffixe (`*.suffixe`)
- Des deux côtés uniquement, pour une correspondance par sous-chaîne (`*/contient/*`)
- Au milieu uniquement, pour une correspondance globale (glob) (`/comptes/*/infos`)

Les slashes sont significatifs. Par exemple, `/foo*` correspondra à `/foo`, `/foobar`, `/foo/`, et `/foo/bar`, mais `/foo/*` ne correspondra *pas* à `/foo` ni à `/foobar`.

Les chemins de requête sont nettoyés pour résoudre les points de traversée de répertoire avant la sélection. De plus, les slashes multiples sont fusionnés sauf si le motif de correspondance possède des slashes multiples. En d'autres termes, `/foo` correspondra à `/foo` et `//foo`, mais `//foo` ne correspondra qu'à `//foo`.

Comme il existe plusieurs formes échappées pour toute URI donnée, le chemin de la requête est normalisé (décodé par URL, déséchappé) sauf pour les séquences d'échappement aux positions où des séquences d'échappement sont également présentes dans le motif de correspondance. Par exemple, `/foo/bar` correspond à la fois à `/foo/bar` et à `/foo%2Fbar`, mais `/foo%2Fbar` ne correspondra qu'à `/foo%2Fbar`, car la séquence d'échappement est explicitement donnée dans la configuration.

L'échappement spécial de caractère générique `%*` peut également être utilisé à la place de `*` pour laisser sa plage de correspondance échappée. Par exemple, `/groupes/*/*` ne correspondra pas à `/groupes/AC%2FDC/T.N.T` car le chemin sera comparé dans un espace normalisé où il ressemble à `/groupes/AC/DC/T.N.T`, ce qui ne correspond pas au motif ; cependant, `/groupes/%*/*` correspondra à `/groupes/AC%2FDC/T.N.T` car la plage représentée par `%*` sera comparée sans décoder les séquences d'échappement.

Plusieurs chemins seront liés par un OU.

#### Exemples :

Sélectionner plusieurs répertoires et leur contenu :

```caddy-d
@assets path /js/* /css/* /images/*
```

Sélectionner un fichier spécifique :

```caddy-d
@favicon path /favicon.ico
```

Sélectionner par extensions de fichiers :

```caddy-d
@extensions path *.js *.css
```

Avec une [expression CEL](#expression) :

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<nom>] <regexp>

expression path_regexp('<nom>', '<regexp>')
expression path_regexp('<regexp>')
```

Comme [`path`](#path), mais supporte les expressions régulières. S'exécute contre le chemin décodé par URI/déséchappé.

Le langage d'expression régulière utilisé est RE2, inclus dans Go. Voir la [référence de syntaxe RE2](https://github.com/google/re2/wiki/Syntax) et l' [aperçu de la syntaxe regexp de Go](https://pkg.go.dev/regexp/syntax).

Depuis la v2.8.0, si le `nom` n'est *pas* fourni, le nom sera tiré du nom du sélecteur nommé. Par exemple, un sélecteur nommé `@foo` entraînera le nommage de ce sélecteur en `foo`. Le principal avantage de spécifier un nom est si plus d'un sélecteur regexp (ex: `path_regexp` et [`header_regexp`](#header-regexp)) est utilisé dans le même sélecteur nommé.

Les groupes de capture peuvent être accédés via [espace réservé (placeholder)](/docs/caddyfile/concepts#placeholders) dans les directives après la sélection :
- `{re.<nom>.<groupe_capture>}` où :
  - `<nom>` est le nom de l'expression régulière,
  - `<groupe_capture>` est soit le nom soit le numéro du groupe de capture dans l'expression.

- `{re.<groupe_capture>}` sans nom, est également rempli par commodité. La mise en garde est que si plusieurs sélecteurs regexp sont utilisés à la suite, alors les valeurs des espaces réservés seront écrasées par le sélecteur suivant.

Le groupe de capture `0` est la correspondance regexp complète, `1` est le premier groupe de capture, `2` est le second, et ainsi de suite. Ainsi, `{re.foo.1}` ou `{re.1}` contiendront tous deux la valeur du premier groupe de capture.

Il ne peut y avoir qu'un seul motif `path_regexp` par sélecteur nommé, car ce sélecteur ne peut pas être fusionné avec lui-même ; si vous en avez besoin de plus, envisagez d'utiliser un [sélecteur `expression`](#expression).

#### Exemple :

Sélectionner les requêtes où le chemin se termine par une chaîne hexadécimale de 6 caractères suivie de `.css` ou `.js` comme extension de fichier, avec des groupes de capture (parties entourées de `( )`), qui peuvent être accédés via `{re.static.1}` et `{re.static.2}` (ou `{re.1}` et `{re.2}`), respectivement :

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Ceci peut être simplifié en omettant le nom, qui sera déduit du sélecteur nommé :

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

Ou la même chose, en utilisant une [expression CEL](#expression), en validant également que le [`fichier`](#file) existe sur le disque :

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
<a id="protocol"></a>
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

Par protocole de requête. Un nom de protocole large tel que `http`, `https`, ou `grpc` peut être utilisé ; ou des versions HTTP spécifiques ou minimales telles que `http/1.1` ou `http/2+`.

Il ne peut y avoir qu'un seul sélecteur `protocol` par sélecteur nommé.

#### Exemple :

Sélectionner les requêtes utilisant HTTP/2 :

```caddy-d
@http2 protocol http/2+
```

Avec une [expression CEL](#expression) :

```caddy-d
@http2 `protocol('http/2+')`
```



---
<a id="query"></a>
### query

```caddy-d
query <cle>=<val>...
query ""

expression query({'<cle>': '<val>'})
expression query({'<cle>': ['<vals...>']})
```

Par paramètres de chaîne de requête (query string). Doit être une séquence de paires `clé=valeur`, ou une chaîne vide "". Les clés sont comparées exactement (sensibles à la casse) mais supportent également `*` pour correspondre à n'importe quelle valeur. Les valeurs peuvent utiliser des espaces réservés. Une chaîne vide correspond aux requêtes HTTP sans paramètres de requête.

Il peut y avoir plusieurs sélecteurs `query` par sélecteur nommé, et les paires ayant les mêmes clés seront liées par un OU. Les clés différentes seront liées par un ET. Ainsi, toutes les clés du sélecteur doivent avoir au moins une valeur correspondante.

Les chaînes de requête illégales (mauvaise syntaxe, points-virgules non échappés, etc.) échoueront à l'analyse et ne correspondront donc pas.

**NOTE :** Les paramètres de chaîne de requête sont des tableaux, pas des valeurs singulières. C'est parce que les clés répétées sont valides dans les chaînes de requête, et chacune peut avoir une valeur différente. Ce sélecteur correspondra pour une clé si l'une quelconque de ses valeurs configurées est assignée dans la chaîne de requête. Les applications backend utilisant des chaînes de requête DOIVENT prendre en considération que les valeurs de chaîne de requête sont des tableaux et peuvent avoir plusieurs valeurs.

#### Exemple :

Sélectionner un paramètre de requête `q` avec n'importe quelle valeur :

```caddy-d
@recherche query q=*
```

Sélectionner un paramètre de requête `sort` avec la valeur `asc` ou `desc` :

```caddy-d
@trie query sort=asc sort=desc
```

Sélectionner à la fois `q` et `sort`, avec une [expression CEL](#expression) :

```caddy-d
@recherche-trie `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <plages...>

expression remote_ip('<plages...>')
```

Par adresse IP distante (c'est-à-dire l'adresse IP du pair immédiat ou l'adresse définie via le [protocole PROXY](/docs/caddyfile/options#proxy-protocol)). Accepte des IPs exactes ou des plages CIDR. Les zones IPv6 sont supportées.

En tant que raccourci, `private_ranges` peut être utilisé pour correspondre à toutes les plages privées IPv4 et IPv6. Cela équivaut à spécifier toutes ces plages : `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Si vous souhaitez faire correspondre l'"IP réelle" du client, telle qu'analysée depuis les en-têtes HTTP, utilisez le sélecteur [`client_ip`](#client-ip) à la place.

Il peut y avoir plusieurs sélecteurs `remote_ip` par sélecteur nommé, et leurs plages seront fusionnées et liées par un OU.

#### Exemple :

Sélectionner les requêtes provenant d'adresses IPv4 privées :

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Ce sélecteur est couramment associé au sélecteur [`not`](#not) pour inverser la sélection. Par exemple, pour interrompre toutes les connexions provenant d'adresses IPv4 et IPv6 _publiques_ (qui est l'inverse de toutes les plages privées) :

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Bonjour, vous devez provenir d'un réseau privé !"
}
```

Dans une [expression CEL](#expression), cela ressemblerait à ceci :

```caddy-d
@mes-amis `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
<a id="vars"></a>
### vars

```caddy-d
vars <variable> <valeurs...>

expression vars({'<variable>': '<valeur>'})
expression vars({'<variable>': ['<valeurs...>']})
```

Par la valeur d'une variable dans le contexte de la requête, ou la valeur d'un espace réservé. Plusieurs valeurs peuvent être spécifiées pour correspondre à n'importe laquelle de ces valeurs possibles (OU logique).

L'argument **&lt;variable&gt;** peut être soit un nom de variable, soit un espace réservé entre accolades `{ }`. (Les espaces réservés ne sont pas développés dans le premier paramètre.)

Ce sélecteur est très utile lorsqu'il est associé à la [directive `map`](/docs/caddyfile/directives/map) qui définit des sorties, à la [directive `vars`](/docs/caddyfile/directives/vars) au sein de vos routes, ou avec des plugins qui définissent certaines informations dans le contexte de la requête.

#### Exemple :

Sélectionner une sortie de la [directive `map`](/docs/caddyfile/directives/map) nommée `magic_number` pour les valeurs `3` ou `5` :

```caddy-d
vars {magic_number} 3 5
```

Sélectionner la valeur d'un espace réservé arbitraire, ex : l'ID de l'utilisateur authentifié, soit `Bob` soit `Alice` :

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Un exemple complet utilisant la [directive `vars`](/docs/caddyfile/directives/vars) pour définir une variable, puis en effectuant une sélection sur celle-ci avec le [sélecteur `vars`](#vars). Ici, nous combinons deux en-têtes de requête en une seule variable, et effectuons une sélection sur cette variable :

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "Vous avez envoyé Foo=123 et Bar=456 !"
	}
	handle {
		respond "Foo et Bar n'étaient pas spéciaux."
	}
}
```

Dans une [expression CEL](#expression), cela ressemblerait à ceci :

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<nom>] <variable> <regexp>

expression vars_regexp('<nom>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

Comme [`vars`](#vars), mais supporte les expressions régulières.

Le langage d'expression régulière utilisé est RE2, inclus dans Go. Voir la [référence de syntaxe RE2](https://github.com/google/re2/wiki/Syntax) et l' [aperçu de la syntaxe regexp de Go](https://pkg.go.dev/regexp/syntax).

Depuis la v2.8.0, si le `nom` n'est *pas* fourni, le nom sera tiré du nom du sélecteur nommé. Par exemple, un sélecteur nommé `@foo` entraînera le nommage de ce sélecteur en `foo`. Le principal avantage de spécifier un nom est si plus d'un sélecteur regexp (ex: `vars_regexp` et [`header_regexp`](#header-regexp)) est utilisé dans le même sélecteur nommé.

Les groupes de capture peuvent être accédés via [espace réservé (placeholder)](/docs/caddyfile/concepts#placeholders) dans les directives après la sélection :
- `{re.<nom>.<groupe_capture>}` où :
  - `<nom>` est le nom de l'expression régulière,
  - `<groupe_capture>` est soit le nom soit le numéro du groupe de capture dans l'expression.

- `{re.<groupe_capture>}` sans nom, est également rempli par commodité. La mise en garde est que si plusieurs sélecteurs regexp sont utilisés à la suite, alors les valeurs des espaces réservés seront écrasées par le sélecteur suivant.

Le groupe de capture `0` est la correspondance regexp complète, `1` est le premier groupe de capture, `2` est le second, et ainsi de suite. Ainsi, `{re.foo.1}` ou `{re.1}` contiendront tous deux la valeur du premier groupe de capture.

Une seule expression régulière est supportée par nom de variable, car les motifs regexp ne peuvent pas être fusionnés ; si vous en avez besoin de plus, envisagez d'utiliser un [sélecteur `expression`](#expression). Les correspondances contre plusieurs variables différentes seront liées par un ET.

#### Exemple :

Sélectionner une sortie de la [directive `map`](/docs/caddyfile/directives/map) nommée `magic_number` pour une valeur commençant par `4`, en capturant la valeur dans un groupe de capture accessible via `{re.magic.1}` ou `{re.1}` :

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Ceci peut être simplifié en omettam le nom, qui sera déduit du sélecteur nommé :

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

Dans une [expression CEL](#expression), cela ressemblerait à ceci :

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
