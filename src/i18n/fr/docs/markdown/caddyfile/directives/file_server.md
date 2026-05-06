---
title: file_server (directive Caddyfile)
---

<script>
ready(function() {
	// Fix inline browse arg
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# file_server

Un serveur de fichiers statiques qui supporte les systèmes de fichiers réels et virtuels. Il forme les chemins de fichiers en ajoutant le chemin de l'URI de la requête au [chemin racine du site](root).

Par défaut, il impose des URIs canoniques ; ce qui signifie que des redirections HTTP seront émises pour les requêtes vers des répertoires qui ne se terminent pas par un slash (pour l'ajouter), ou les requêtes vers des fichiers qui ont un slash final (pour le supprimer). Cependant, les redirections ne sont pas émises si une réécriture interne modifie le dernier élément du chemin (le nom du fichier).

Le plus souvent, la directive `file_server` est associée à la directive [`root`](root) pour définir la racine des fichiers pour l'ensemble du site. Cette directive possède également une sous-directive `root` (voir ci-dessous) pour définir la racine uniquement pour ce gestionnaire (non recommandé). Notez qu'une racine de site ne garantit pas un cloisonnement (sandbox) : le serveur de fichiers empêche la traversée de répertoires à partir des composants du chemin, mais les liens symboliques à l'intérieur de la racine peuvent toujours permettre des accès en dehors de celle-ci.

Lorsque des erreurs surviennent (ex: fichier non trouvé `404`, permission refusée `403`), les routes d'erreur seront invoquées. Utilisez la directive [`handle_errors`](handle_errors) pour définir des routes d'erreur et afficher des pages d'erreur personnalisées.

Lors de l'utilisation de `browse`, la sortie par défaut est produite par le modèle (template) HTML. Les clients peuvent demander le listage du répertoire soit en JSON, soit en texte brut, en utilisant respectivement les en-têtes `Accept: application/json` ou `Accept: text/plain`. La sortie JSON peut être utile pour les scripts, et la sortie texte brut peut être utile pour un usage humain dans un terminal.


## Syntaxe

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <chemin>
	hide          <fichiers...>
	index         <noms_fichiers...>
	browse        [<fichier_modele>] {
		reveal_symlinks
		sort <champ_tri> [<direction>]
		file_limit <nombre>
	}
	precompressed [<formats...>]
	status        <statut>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> spécifie un système de fichiers alternatif (peut-être virtuel) à utiliser. Tout module Caddy dans l'espace de noms `caddy.fs` peut être utilisé ici. Tout chemin racine/préfixe s'appliquera toujours aux modules de système de fichiers alternatifs. Par défaut, le disque local est utilisé.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 introduit le [drapeau `--embed`](https://github.com/caddyserver/xcaddy#custom-builds) pour intégrer une arborescence de fichiers dans le build Caddy personnalisé, et enregistre un module `fs` nommé `embedded` qui permet à votre site statique d'être distribué sous forme d'exécutable Caddy.

- **root** <span id="root"/> définit le chemin vers la racine du site. C'est similaire à la directive [`root`](root) sauf qu'elle s'applique uniquement à cette instance de serveur de fichiers et surcharge toute autre racine de site ayant pu être définie. Par défaut : `{http.vars.root}` ou le répertoire de travail actuel. Note : Cette sous-directive ne change la racine que pour ce gestionnaire. Pour que d'autres directives (comme [`try_files`](try_files) ou [`templates`](templates)) connaissent la même racine de site, utilisez la directive [`root`](root) à la place.

- **hide** <span id="hide"/> est une liste de fichiers ou de dossiers à cacher ; s'ils sont demandés, le serveur de fichiers prétendra qu'ils n'existent pas. Accepte les espaces réservés et les motifs globaux. Notez qu'il s'agit de chemins de *système de fichiers*, PAS de chemins de requête. En d'autres termes, les chemins relatifs utilisent le répertoire de travail actuel comme base, PAS la racine du site ; et tous les chemins sont transformés en leur forme absolue avant comparaison (si possible). Spécifier un nom de fichier ou un motif sans séparateur de chemin cachera tous les fichiers ayant un nom correspondant quel que soit leur emplacement ; sinon, une correspondance par préfixe de chemin sera tentée, puis une correspondance glob. Puisqu'il s'agit d'une config Caddyfile, le ou les fichiers de configuration actifs seront ajoutés par défaut. Les comparaisons de masquage sont sensibles à la casse ; sur les systèmes de fichiers insensibles à la casse, un chemin de requête avec une casse différente peut toujours se résoudre vers le même chemin sur le disque, `hide` ne doit donc pas être traité comme une barrière de sécurité pour les chemins sensibles.

- **index** <span id="index"/> est une liste de noms de fichiers à rechercher comme fichiers index. Par défaut : `index.html index.txt`

- **browse** <span id="browse"/> active le listage des fichiers pour les requêtes vers des répertoires qui n'ont pas de fichier index.

  - **<fichier_modele>** <span id="template_file"/> est un fichier de modèle personnalisé optionnel à utiliser pour les listages de répertoires. Par défaut, utilise le modèle qui peut être extrait avec la commande `caddy file-server export-template`, qui affichera le modèle par défaut sur stdout. Le modèle intégré peut également être trouvé [ici dans le code source ![lien externe](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html). Les modèles browse peuvent également utiliser les actions du [module standard templates](/docs/modules/http.handlers.templates#docs).

  - **reveal_symlinks** <span id="reveal_symlinks"/> active l'affichage de la cible des liens symboliques dans les listages de répertoires. Par défaut, les cibles des liens symboliques sont cachées, et seul le fichier de lien lui-même est affiché.

  - **sort** <span id="sort"/> change le tri par défaut pour les listages de répertoires. Le premier paramètre est le champ/colonne par lequel trier : `name`, `namedirfirst`, `size`, ou `time`. Le second argument est une direction optionnelle : `asc` ou `desc`. Par exemple, `sort name desc` triera par nom dans l'ordre décroissant.

  - **file_limit** <span id="file_limit"/> définit un nombre maximum de fichiers à afficher dans les listages de répertoires. Par défaut : `10000`. Si le nombre de fichiers dépasse cette limite, seuls les N premiers fichiers seront affichés, où N est la limite spécifiée.

- **precompressed** <span id="precompressed"/> est la liste des formats d'encodage pour rechercher des fichiers sidecar précompressés. Les arguments sont une liste ordonnée de formats d'encodage pour rechercher des [fichiers sidecar](https://fr.wikipedia.org/wiki/Fichier_sidecar) précompressés. Les formats supportés sont `gzip` (`.gz`), `zstd` (`.zst`) et `br` (`.br`). Si les formats sont omis, ils valent par défaut `br zstd gzip` (dans cet ordre).

  Toutes les recherches de fichiers chercheront d'abord l'existence du fichier non compressé. Une fois trouvé, Caddy cherchera des fichiers sidecar avec l'extension de fichier de chaque format activé. Si un fichier sidecar précompressé est trouvé, Caddy répondra avec le fichier précompressé, avec l'en-tête de réponse `Content-Encoding` réglé de manière appropriée. Sinon, Caddy répondra avec le fichier non compressé comme d'habitude. Si la [directive `encode`](encode) est activée, elle pourra compresser la réponse à la volée si elle n'est pas déjà précompressée.

- **status** <span id="status"/> est une surcharge de code d'état optionnelle à utiliser lors de l'écriture de la réponse. Particulièrement utile lors de la réponse à une requête avec une [page d'erreur personnalisée](handle_errors). Peut être un code d'état à 3 chiffres, par exemple : `404`. Les espaces réservés sont supportés. Par défaut, le code d'état écrit sera typiquement `200`, ou `206` pour un contenu partiel.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> désactive le comportement par défaut de redirection (pour ajouter un slash final si le chemin de la requête est un répertoire, ou supprimer le slash final si le chemin de la requête est un fichier). Notez que par défaut, la canonisation ne se produira pas si le dernier élément du chemin de la requête (le nom du fichier) a subi une réécriture interne, afin d'éviter d'écraser une réécriture explicite par un comportement implicite.

- **pass_thru** <span id="pass_thru"/> active le mode "pass-thru", qui continue vers le prochain gestionnaire HTTP de la route si le fichier demandé n'est pas trouvé, au lieu de déclencher une erreur `404` (invoquant les routes [`handle_errors`](handle_errors)). Pratiquement, ceci n'est utile qu'à l'intérieur d'un bloc [`route`](route) avec d'autres directives de gestionnaire suivant `file_server`, car cette directive est effectivement [ordonnée en dernier](/docs/caddyfile/directives#directive-order).


## Exemples

Un serveur de fichiers statiques depuis le répertoire actuel :

```caddy-d
file_server
```

Avec les listages de fichiers activés :

```caddy-d
file_server browse
```

Servir uniquement les fichiers statiques à l'intérieur du dossier `/static` :

```caddy-d
file_server /static/*
```

La directive `file_server` est généralement associée à la directive [`root`](root) pour définir le chemin racine à partir duquel servir les fichiers :

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Si vous faites tourner Caddy en tant que service systemd, la lecture de fichiers depuis `/home` ne fonctionnera pas, car l'utilisateur `caddy` n'a pas la permission "exécution" sur le répertoire `/home` (nécessaire pour la traversée). Il est recommandé de placer vos fichiers dans `/srv` ou `/var/www/html` à la place.

</aside>


Cacher tous les dossiers `.git` et leur contenu :

```caddy-d
file_server {
	hide .git
}
```

Si supporté par le client (en-tête `Accept-Encoding`), vérifie l'existence de fichiers précompressés à côté du fichier demandé. Ainsi, si `/chemin/vers/fichier` est demandé, il vérifie `/chemin/vers/fichier.br`, `/chemin/vers/fichier.zst` et `/chemin/vers/fichier.gz` dans cet ordre et sert le premier fichier disponible avec le `Content-Encoding` correspondant :

```caddy-d
file_server {
	precompressed
}
```
