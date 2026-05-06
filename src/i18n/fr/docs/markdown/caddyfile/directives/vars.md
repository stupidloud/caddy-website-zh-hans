---
title: vars (directive Caddyfile)
---

# vars

Définit une ou plusieurs variables à une valeur particulière, pour être utilisée ultérieurement dans la chaîne de traitement de la requête.

La manière principale d'accéder aux variables est avec les espaces réservés (placeholders), qui ont la forme `{vars.nom_variable}`, ou avec les sélecteurs de requête [`vars`](/docs/caddyfile/matchers#vars) et [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

Vous pouvez utiliser des variables avec la directive [`templates`](templates) en utilisant la fonction `placeholder`, par exemple : `{{ "{{placeholder \"http.vars.nom_variable\"}}" }}`

En tant que cas particulier, il est possible de surcharger la variable nommée `http.auth.user.id`, laquelle est stockée dans le replacer, afin de mettre à jour le champ `user_id` dans les [journaux d'accès (access logs)](log).


## Syntaxe

```caddy-d
vars [<matcher>] [<nom> <valeur>] {
    <nom> <valeur>
    ...
}
```

- **&lt;nom&gt;** est le nom de la variable à définir.

- **&lt;valeur&gt;** est la valeur de la variable.

  La valeur sera convertie en type si possible ; `true` et `false` seront convertis en types booléens, et les valeurs numériques seront converties en entier ou flottant en conséquence. Pour éviter cette conversion et les garder en tant que chaînes de caractères, vous pouvez les entourer de [guillemets](/docs/caddyfile/concepts#tokens-and-quotes).

## Exemples

Définir une variable unique, la valeur étant conditionnelle selon le chemin de la requête, puis répondre avec la valeur :

```caddy
example.com {
	vars /foo* estFoo "ouaip"
	vars estFoo "non"

	respond {vars.estFoo}
}
```

Définir plusieurs variables, chacune convertie vers le type scalaire approprié :

```caddy-d
vars {
	# booléen
	abc true

	# entier
	def 1

	# flottant
	ghi 2.3

	# chaîne
	jkl "exemple"
}
```
