---
title: handle_path (directive Caddyfile)
---

<script>
ready(function() {
	// Add a link to [<path_matcher>] as a special case for this directive.
	// The matcher text includes <> characters which are parsed as HTML,
	// so we must use text() to change the link text.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Matcher token">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

Fonctionne de la même manière que la [directive `handle`](handle), mais utilise implicitement [`uri strip_prefix`](uri) pour supprimer le préfixe du chemin correspondant.

Traiter une requête correspondant à un certain chemin (tout en supprimant ce chemin de l'URI de la requête) est un cas d'utilisation suffisamment courant pour avoir sa propre directive par commodité.


## Syntaxe

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** est une liste de directives de gestionnaire HTTP ou de blocs de directives, une par ligne, tout comme elles seraient utilisées en dehors d'un bloc `handle_path`.

Seul un unique [sélecteur de chemin](/docs/caddyfile/matchers#path-matchers) est accepté, et il est requis ; vous ne pouvez pas utiliser de sélecteurs nommés avec `handle_path`.

## Exemples

Cette configuration :

```caddy-d
handle_path /prefixe/* {
	...
}
```

👆 est effectivement identique à celle-ci 👇, mais la forme `handle_path` 👆 est légèrement plus succincte :

```caddy-d
handle /prefixe/* {
	uri strip_prefix /prefixe
	...
}
```

Un exemple complet de Caddyfile, où `handle_path` et `handle` sont mutuellement exclusifs ; mais, soyez attentif au [problème des sous-dossiers <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575) :

```caddy
example.com {
	# Servir votre API, en supprimant le préfixe /api
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Servir votre site statique
	handle {
		root /srv
		file_server
	}
}
```
