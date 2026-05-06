---
title: Matcher di risposta (Caddyfile)
---

<script>
ready(function() {
	// Matcher di risposta
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

	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# Matcher di risposta

I **matcher di risposta** possono essere usati per filtrare (o classificare) le risposte in base a criteri specifici.

Questi appaiono tipicamente solo come configurazione all'interno di alcune altre direttive, per prendere decisioni sulla risposta mentre viene scritta verso il client.

- [Sintassi](#sintassi)
- [Matcher](#matcher)
	- [status](#status)
	- [header](#header)

## Sintassi

Se una direttiva accetta matcher di risposta, l'uso è rappresentato come `[<response_matcher>]` o `[<inline_response_matcher>]` nella documentazione della sintassi.

- Il token **<response_matcher>** può essere il nome di un matcher di risposta con nome precedentemente dichiarato. Ad esempio: `@nome`.
- Il token **<inline_response_matcher>** può essere il criterio di risposta stesso, senza richiedere una dichiarazione preventiva. Ad esempio: `status 200`.

### Con nome

```caddy-d
@nome {
	status <codice...>
	header <campo> [<valore>]
}
```
Se solo un aspetto della risposta è rilevante per la direttiva, potete mettere il nome e i criteri sulla stessa riga:

```caddy-d
@nome status <codice...>
```

### Inline

```caddy-d
... {
	status <codice...>
	header <campo> [<valore>]
}
```
```caddy-d
... status <codice...>
```
```caddy-d
... header <campo> [<valore>]
```

## Matcher

### status

```caddy-d
status <codice...>
```

In base al codice di stato HTTP.

- **&lt;codice...&gt;** è un elenco di codici di stato HTTP. Casi speciali sono stringhe come `2xx` e `3xx`, che corrispondono a tutti i codici di stato rispettivamente nell'intervallo `200`-`299` e `300`-`399`.

#### Esempio:

```caddy-d
@success status 2xx
```



### header

```caddy-d
header <campo> [<valore>]
```

In base ai campi dell'header della risposta.

- `<campo>` è il nome del campo header HTTP da controllare.
	- Se preceduto da `!`, il campo non deve esistere per corrispondere (omettere l'argomento valore).
- `<valore>` è il valore che il campo deve avere per corrispondere.
	- Se preceduto da `*`, esegue una corrispondenza rapida del suffisso (appare alla fine).
	- Se terminante con `*`, esegue una corrispondenza rapida del prefisso (appare all'inizio).
	- Se racchiuso tra `*`, esegue una corrispondenza rapida della sottostringa (appare ovunque).
	- Altrimenti, è una corrispondenza esatta rapida.

Diversi campi header all'interno dello stesso set sono uniti in AND. Più valori per lo stesso campo sono uniti in OR.

Si noti che i campi header possono essere ripetuti e avere valori diversi. Le applicazioni backend DEVONO tenere in considerazione che i valori dei campi header sono array, non valori singoli, e Caddy non interpreta il significato in tali casi.

#### Esempio:

Far corrispondere le risposte con l'header `Foo` contenente il valore `bar`:

```caddy-d
@upgrade header Foo *bar*
```

Far corrispondere le risposte con l'header `Foo` che ha valore `bar` OPPURE `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Far corrispondere le risposte che non hanno affatto il campo header `Foo`:

```caddy-d
@not_foo header !Foo
```
