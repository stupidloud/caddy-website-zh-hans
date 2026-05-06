---
title: handle_path (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Aggiunge un link a [<path_matcher>] come caso speciale per questa direttiva.
	// Il testo del matcher include i caratteri <> che vengono interpretati come HTML,
	// quindi dobbiamo usare innerHTML per cambiare il testo del link.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Token matcher">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

Funziona come la [direttiva `handle`](handle), ma usa implicitamente [`uri strip_prefix`](uri) per rimuovere il prefisso del percorso corrispondente.

Gestire una richiesta che corrisponde a un certo percorso (rimuovendo contemporaneamente tale percorso dall'URI della richiesta) è un caso d'uso sufficientemente comune da avere la propria direttiva per comodità.


## Sintassi

```caddy-d
handle_path <path_matcher> {
	<direttive...>
}
```

- **&lt;direttive...&gt;** è un elenco di direttive handler HTTP o blocchi direttiva, uno per riga, proprio come verrebbero usati all'esterno di un blocco `handle_path`.

Viene accettato solo un singolo [matcher di percorso](/docs/caddyfile/matchers#path-matchers), ed è obbligatorio; non è possibile usare matcher con nome con `handle_path`.

## Esempi

Questa configurazione:

```caddy-d
handle_path /prefisso/* {
	...
}
```

👆 è effettivamente identica a questa 👇, ma la forma `handle_path` 👆 è leggermente più concisa

```caddy-d
handle /prefisso/* {
	uri strip_prefix /prefisso
	...
}
```

Un esempio completo di Caddyfile, dove `handle_path` e `handle` sono mutualmente esclusivi; ma attenzione al [problema delle sottocartelle <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# Serve la vostra API, rimuovendo il prefisso /api
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Serve il vostro sito statico
	handle {
		root * /srv
		file_server
	}
}
```
