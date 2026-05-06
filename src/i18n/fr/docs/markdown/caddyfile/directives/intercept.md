---
title: intercept (directive Caddyfile)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Sélecteur de réponse">${text}</a>`;
		}
	});

	// Response matchers
	const nameMatchers = Array.from($$_('pre.chroma .nd')).filter(item => item.innerText.includes('@nom'));
	if (nameMatchers.length > 0) {
		const first = nameMatchers[0];
		const span = document.createElement('span');
		span.className = 'nd';
		first.parentNode.insertBefore(span, first);
		span.appendChild(first);
		span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;">@nom</a>';
	}
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText === 'status') {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;">status</a>';
		}
	});
	
	const headerElements = $$_('pre.chroma .k');
	for (let item of headerElements) {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;">header</a>';
			break;
		}
	}

	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# intercept

Une abstraction généralisée de la fonctionnalité d' [interception de réponse](reverse_proxy#intercepting-responses) de la directive [`reverse_proxy`](reverse_proxy). Elle peut être utilisée avec n'importe quel gestionnaire produisant des réponses, y compris ceux issus de plugins comme `php_server` de [FrankenPHP](https://frankenphp.dev/).

Cette directive vous permet de [faire correspondre des réponses](/docs/caddyfile/response-matchers), et la première route `handle_response` ou `replace_status` correspondante sera invoquée. Lors de l'invocation, le corps de la réponse originale est retenu, offrant à cette route l'opportunité d'écrire un corps de réponse différent, avec un nouveau code d'état ou n'importe quelle manipulation d'en-tête de réponse nécessaire. Si la route n'écrit *pas* de nouveau corps de réponse, alors le corps de la réponse originale est écrit à la place.


## Syntaxe

```caddy-d
intercept [<matcher>] {
	@nom {
		status <code...>
		header <champ> [<valeur>]
	}

	replace_status [<response_matcher>] <code>

	handle_response [<response_matcher>] {
		<directives...>
	}
}
```

- **@nom** est un bloc de [sélecteur de réponse](/docs/caddyfile/response-matchers) nommé. Tant que chaque sélecteur de réponse possède un nom unique, plusieurs sélecteurs peuvent être définis. Une réponse peut être sélectionnée sur son code d'état et la présence ou la valeur d'un en-tête de réponse.

- **replace_status** <span id="replace_status"/> change simplement le code d'état de la réponse lorsqu'elle correspond au sélecteur donné.

- **handle_response** <span id="handle_response"/> définit la route à exécuter lorsque la réponse originale correspond au sélecteur de réponse donné. Si le sélecteur est omis, toutes les réponses sont interceptées. Lorsque plusieurs blocs `handle_response` sont définis, le premier bloc correspondant sera appliqué. À l'intérieur du bloc, toutes les autres [directives](/docs/caddyfile/directives) peuvent être utilisées.

Au sein des routes `handle_response`, les espaces réservés suivants sont disponibles pour extraire des informations de la réponse originale :

- `{resp.status_code}` Le code d'état de la réponse originale.

- `{resp.header.*}` Les en-têtes de la réponse originale.


## Exemples

Lors de l'utilisation de `php_server` de [FrankenPHP](https://frankenphp.dev/), vous pouvez utiliser `intercept` pour implémenter le support de `X-Accel-Redirect`, en servant des fichiers statiques comme demandé par l'application PHP :

```caddy
localhost {
	root /srv

	intercept {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /chemin/vers/fichiers/prives
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}

	php_server
}
```
