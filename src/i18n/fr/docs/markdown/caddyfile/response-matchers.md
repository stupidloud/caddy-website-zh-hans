---
title: Sélecteurs de réponse (Caddyfile)
---

<script>
ready(function() {
	// Sélecteurs de réponse
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# Sélecteurs de réponse (Response Matchers)

Les **sélecteurs de réponse** peuvent être utilisés pour filtrer (ou classifier) les réponses selon des critères spécifiques.

Ils apparaissent typiquement uniquement comme configuration à l'intérieur de certaines autres directives, afin de prendre des décisions sur la réponse au moment où elle est écrite vers le client.

- [Syntaxe](#syntax)
- [Sélecteurs](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## Syntaxe

Si une directive accepte des sélecteurs de réponse, l'usage est représenté par `[<response_matcher>]` ou `[<inline_response_matcher>]` dans la documentation de syntaxe.

- Le jeton **<response_matcher>** peut être le nom d'un sélecteur de réponse nommé précédemment déclaré. Par exemple : `@nom`.
- Le jeton **<inline_response_matcher>** peut correspondre aux critères de réponse eux-mêmes, sans nécessiter de déclaration préalable. Par exemple : `status 200`.

### Nommé

```caddy-d
@nom {
	status <code...>
	header <champ> [<valeur>]
}
```
Si un seul aspect de la réponse est pertinent pour la directive, vous pouvez mettre le nom et le critère sur la même ligne :

```caddy-d
@nom status <code...>
```

### En ligne (Inline)

```caddy-d
... {
	status <code...>
	header <champ> [<valeur>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <champ> [<valeur>]
```

<a id="matchers"></a>
## Sélecteurs

<a id="status"></a>
### status

```caddy-d
status <code...>
```

Par code d'état HTTP.

- **&lt;code...&gt;** est une liste de codes d'état HTTP. Les cas particuliers sont des chaînes comme `2xx` et `3xx`, qui correspondent respectivement à tous les codes d'état dans les plages `200`-`299` et `300`-`399`.

#### Exemple :

```caddy-d
@succes status 2xx
```



<a id="header"></a>
### header

```caddy-d
header <champ> [<valeur>]
```

Par champs d'en-tête de réponse.

- `<champ>` est le nom du champ d'en-tête HTTP à vérifier.
	- S'il est préfixé par `!`, le champ ne doit pas exister pour correspondre (omettre l'argument valeur).
- `<valeur>` est la valeur que le champ doit avoir pour correspondre.
	- S'il est préfixé par `*`, il effectue une correspondance rapide par suffixe (apparaît à la fin).
	- S'il est suffixé par `*`, il effectue une correspondance rapide par préfixe (apparaît au début).
	- S'il est entouré de `*`, il effectue une correspondance rapide par sous-chaîne (apparaît n'importe où).
	- Sinon, c'est une correspondance exacte rapide.

Différents champs d'en-tête au sein d'un même ensemble sont liés par un ET. Les valeurs multiples par champ sont liées par un OU.

Notez que les champs d'en-tête peuvent être répétés et avoir des valeurs différentes. Les applications backend DOIVENT considérer que les valeurs de champs d'en-tête sont des tableaux, pas des valeurs singulières, et Caddy n'interprète pas le sens de telles ambiguïtés.

#### Exemple :

Sélectionner les réponses dont l'en-tête `Foo` contient la valeur `bar` :

```caddy-d
@upgrade header Foo *bar*
```

Sélectionner les réponses dont l'en-tête `Foo` possède la valeur `bar` OU `baz` :

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Sélectionner les réponses qui ne possèdent pas du tout le champ d'en-tête `Foo` :

```caddy-d
@pas_foo header !Foo
```
