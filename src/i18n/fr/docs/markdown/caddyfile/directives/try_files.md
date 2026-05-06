---
title: try_files (directive Caddyfile)
---

# try_files

Réécrit le chemin de l'URI de la requête vers le premier des fichiers listés qui existe dans la racine du site. Si aucun fichier ne correspond, aucune réécriture n'est effectuée.


## Syntaxe

```caddy-d
try_files <fichiers...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<fichiers...>** est la liste des fichiers à tester. Le chemin de l'URI sera réécrit vers le premier qui existe.

  Pour faire correspondre des répertoires, ajoutez un slash final `/` au chemin. Tous les chemins de fichiers sont relatifs à la [racine (root)](root) du site, et les [motifs glob](https://pkg.go.dev/path/filepath#Match) seront développés.

  Chaque argument peut également contenir une chaîne de requête, auquel cas la chaîne de requête sera également modifiée si elle correspond à ce fichier particulier.

  Si la politique `try_policy` est `first_exist` (par défaut), alors le dernier élément de la liste peut être un nombre préfixé par `=` (ex: `=404`), ce qui, en dernier recours, émettra une erreur avec ce code ; l'erreur peut être capturée et gérée avec [`handle_errors`](handle_errors).

- **policy** est la politique pour choisir le fichier parmi la liste de fichiers. 

  Par défaut : `first_exist`



## Forme étendue

La directive `try_files` est essentiellement un raccourci pour :

```caddy-d
@try_files file <fichiers...>
rewrite @try_files {file_match.relative}
```

Notez que cette directive n'accepte pas de jeton de sélecteur. Si vous avez besoin d'une logique de sélection plus complexe, utilisez alors la forme étendue ci-dessus comme base.

Consultez le [sélecteur `file`](/docs/caddyfile/matchers#file) pour plus de détails.



## Exemples

Si la requête ne correspond à aucun fichier statique, réécrire vers votre point d'entrée index/routeur PHP :

```caddy-d
try_files {path} /index.php
```

Idem, mais en ajoutant le chemin original à la chaîne de requête (requis par certaines applications PHP héritées) :

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

Idem, mais en faisant également correspondre les répertoires :

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Tenter de réécrire vers un fichier ou un répertoire s'il existe, sinon émettre une erreur 404 (pouvant être capturée et gérée avec [`handle_errors`](handle_errors)) :

```caddy-d
try_files {path} {path}/ =404
```

Choisir la version la plus récemment déployée d'un fichier statique (ex: servir `index.be331df.html` lorsque `index.html` est demandé) :

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
