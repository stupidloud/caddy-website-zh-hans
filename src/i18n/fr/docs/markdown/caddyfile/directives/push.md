---
title: push (directive Caddyfile)
---

# push

Configure le serveur pour envoyer préventivement des ressources au client en utilisant le HTTP/2 server push.

Les ressources peuvent être liées pour le server push en spécifiant le ou les en-têtes `Link` de la réponse. Cette directive poussera automatiquement les ressources décrites par les en-têtes `Link` amont dans ces formats :

- `<ressource>; as=script`
- `<ressource>; as=script,<ressource>; as=style`
- `<ressource>; nopush`
- `<ressource>;<ressource2>;...`

où `<ressource>` commence par un slash `/` (c'est-à-dire un chemin d'URI sur le même hôte). Seules les ressources sur le même hôte peuvent être poussées. Si une ressource liée est externe ou si elle possède l'attribut `nopush`, elle ne sera pas poussée.

Par défaut, les requêtes push incluront certains en-têtes jugés sûrs à copier depuis la requête originale :

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

car on suppose que beaucoup de requêtes échoueraient sans ces en-têtes ; ils n'ont pas besoin d'être configurés manuellement.

Les requêtes push sont virtualisées en interne, elles sont donc très légères.


## Syntaxe

```caddy-d
push [<matcher>] [<ressource>] {
	[GET|HEAD] <ressource>
	headers {
		[+]<champ> [<valeur|regexp> [<remplacement>]]
		-<champ>
	}
}
```

- **&lt;ressource&gt;** est le chemin d'URI cible à pousser. S'il est utilisé à l'intérieur du bloc, il peut être optionnellement précédé par la méthode (GET ou POST ; GET par défaut).
- **&lt;headers&gt;** manipule les en-têtes de la requête push en utilisant la même syntaxe que la [directive `header`](/docs/caddyfile/directives/header). Certains en-têtes sont reportés par défaut et n'ont pas besoin d'être configurés explicitement (voir ci-dessus).



## Exemples

Pousser toutes les ressources décrites par les en-têtes `Link` dans la réponse :

```caddy-d
push
```

Idem, mais pousse également `/resources/style.css` pour toutes les requêtes :

```caddy-d
push * /resources/style.css
```

Pousser `/foo.jpg` uniquement lorsque `/foo.html` est demandé par le client :

```caddy-d
push /foo.html /foo.jpg
```
