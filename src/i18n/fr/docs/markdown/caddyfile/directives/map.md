---
title: map (directive Caddyfile)
---

# map

Définit les valeurs d'espaces réservés personnalisés en fonction d'une valeur d'entrée.

Elle compare la valeur source avec le côté entrée de l'association (map), et pour celle qui correspond, elle applique la ou les valeurs de sortie à chaque destination. Les destinations deviennent des noms d'espaces réservés. Des valeurs de sortie par défaut peuvent également être spécifiées pour chaque destination.

Les espaces réservés associés ne sont évalués que lorsqu'ils sont utilisés, ainsi même pour de très grandes associations, cette directive est tout à fait efficace.

## Syntaxe

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<entree> <sorties...>
	default    <defauts...>
}
```

- **&lt;source&gt;** est la valeur d'entrée sur laquelle basculer. Généralement un espace réservé.

- **&lt;destinations...&gt;** sont les espaces réservés à créer qui contiendront les valeurs de sortie.

- **&lt;entree&gt;** est la valeur d'entrée à faire correspondre. Si préfixée par `~`, elle est traitée comme une expression régulière.

- **&lt;sorties...&gt;** est une ou plusieurs valeurs de sortie à stocker dans l'espace réservé associé. La première sortie est écrite dans la première destination, la seconde sortie dans la seconde destination, etc.
  
  Cas particulier : l'analyseur Caddyfile traite les sorties étant un tiret littéral (`-`) comme des valeurs nulles/nil. C'est utile si vous souhaitez vous replier sur une valeur par défaut pour cette sortie particulière dans le cas d'une entrée donnée, tout en utilisant des valeurs non par défaut pour d'autres sorties.

  Les sorties seront converties en type si possible ; `true` et `false` seront convertis en types booléens, et les valeurs numériques seront converties en entier ou flottant en conséquence. Pour éviter cette conversion, vous pouvez entourer la sortie de [guillemets](/docs/caddyfile/concepts#tokens-and-quotes) et elles resteront des chaînes de caractères.

  Le nombre de sorties pour chaque association ne doit pas dépasser le nombre de destinations ; cependant, par commodité, il peut y avoir moins de sorties que de destinations, et toutes les sorties manquantes seront remplies implicitement.
  
  Si une expression régulière a été utilisée en entrée, alors les groupes de capture peuvent être référencés avec `${group}` où `group` est soit le nom, soit le numéro du groupe de capture dans l'expression. Le groupe de capture `0` est la correspondance regexp complète, `1` est le premier groupe de capture, `2` est le second, et ainsi de suite.

- **&lt;default&gt;** spécifie les valeurs de sortie à stocker si aucune entrée ne correspond.


## Exemples

L'exemple suivant démontre la plupart des aspects de cette directive :

```caddy-d
map {host}                {mon_espace_reserve}  {magic_number} {
	example.com           "quelque valeur"      3
	foo.example.com       "autre valeur"
	~(.*)\.example\.com$  "sous-domaine ${1}"  5

	~.*\.net$             -                     7
	~.*\.xyz$             -                     15

	default               "domaine inconnu"     42
}
```

Cette directive bascule sur la valeur de `{host}`, c'est-à-dire le nom de domaine de la requête.

- Si la requête concerne `example.com`, définit `{mon_espace_reserve}` à `quelque valeur`, et `{magic_number}` à `3`.
- Sinon, si la requête concerne `foo.example.com`, définit `{mon_espace_reserve}` à `autre valeur`, et laisse `{magic_number}` par défaut à `42`.
- Sinon, si la requête concerne n'importe quel sous-domaine de `example.com`, définit `{mon_espace_reserve}` à une chaîne contenant la valeur du premier groupe de capture regexp, c'est-à-dire l'intégralité du sous-domaine, et définit `{magic_number}` à 5.
- Sinon, si la requête concerne n'importe quel hôte se terminant par `.net` ou `.xyz`, définit uniquement `{magic_number}` à `7` ou `15`, respectivement. Laisse `{mon_espace_reserve}` non défini.
- Sinon (pour tous les autres hôtes), les valeurs par défaut s'appliqueront : `{mon_espace_reserve}` sera défini à `domaine inconnu` et `{magic_number}` sera défini à `42`.
