---
title: handle_path (Caddyfile directive)
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

Funktioniert genauso wie die Direktive [`handle`](handle), verwendet aber implizit [`uri strip_prefix`](uri), um das gematchte Pfadpräfix zu entfernen.

Einen Request zu behandeln, der auf einen bestimmten Pfad passt (während dieser Pfad aus der Request-URI entfernt wird), ist ein so häufiger Anwendungsfall, dass es dafür eine eigene Direktive zur Bequemlichkeit gibt.


<a id="syntax"></a>
## Syntax

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** ist eine Liste von HTTP-Handler-Direktiven oder Direktivenblöcken, eine pro Zeile, genauso wie sie außerhalb eines `handle_path`-Blocks verwendet würden.

Es wird nur ein einzelner [Path-Matcher](/docs/caddyfile/matchers#path-matchers) akzeptiert, und er ist erforderlich; Sie können keine benannten Matcher mit `handle_path` verwenden.

<a id="examples"></a>
## Beispiele

Diese Konfiguration:

```caddy-d
handle_path /prefix/* {
	...
}
```

ist effektiv dasselbe wie diese, aber die `handle_path`-Form ist etwas knapper:

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

Ein vollständiges Caddyfile-Beispiel, in dem `handle_path` und `handle` gegenseitig exklusiv sind; beachten Sie aber das [Subfolder-Problem <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# Ihre API ausliefern und dabei das Präfix /api entfernen
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Ihre statische Site ausliefern
	handle {
		root /srv
		file_server
	}
}
```
