---
title: intercept (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Corregge i matcher di risposta per renderizzarli con il colore corretto,
	// e collega alla sezione dei matcher di risposta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Matcher di risposta">${text}</a>`;
		}
	});

	// Matcher di risposta
	const nameMatchers = Array.from($$_('pre.chroma .nd')).filter(item => item.innerText.includes('@name'));
	if (nameMatchers.length > 0) {
		const first = nameMatchers[0];
		const span = document.createElement('span');
		span.className = 'nd';
		first.parentNode.insertBefore(span, first);
		span.appendChild(first);
		span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;">@name</a>';
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

	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# intercept

Un'astrazione generalizzata della funzionalità di [intercettazione della risposta](reverse_proxy#intercepting-responses) della [direttiva `reverse_proxy`](reverse_proxy). Questa può essere utilizzata con qualsiasi handler che produce risposte, inclusi quelli provenienti da plugin come `php_server` di [FrankenPHP](https://frankenphp.dev/).

Questa direttiva permette di [filtrare le risposte](/docs/caddyfile/response-matchers), e verrà invocata la prima rotta `handle_response` o `replace_status` corrispondente. Quando invocata, il corpo della risposta originale viene trattenuto, offrendo l'opportunità a tale rotta di scrivere un corpo della risposta differente, con un nuovo codice di stato o con qualsiasi manipolazione necessaria degli header di risposta. Se la rotta *non* scrive un nuovo corpo della risposta, allora verrà scritto il corpo della risposta originale.


## Sintassi

```caddy-d
intercept [<matcher>] {
	@name {
		status <code...>
		header <field> [<value>]
	}

	replace_status [<response_matcher>] <code>

	handle_response [<response_matcher>] {
		<direttive...>
	}
}
```

- **@name** è un blocco di [matcher di risposta con nome](/docs/caddyfile/response-matchers). Finché ogni matcher di risposta ha un nome unico, ne possono essere definiti molteplici. Una risposta può essere filtrata in base al codice di stato e alla presenza o al valore di un header di risposta.

- **replace_status** <span id="replace_status"/> cambia semplicemente il codice di stato della risposta quando corrisponde al matcher fornito.

- **handle_response** <span id="handle_response"/> definisce la rotta da eseguire quando la risposta originale corrisponde al matcher di risposta fornito. Se un matcher viene omesso, tutte le risposte vengono intercettate. Quando vengono definiti più blocchi `handle_response`, verrà applicato il primo blocco corrispondente. All'interno del blocco, possono essere usate tutte le altre [direttive](/docs/caddyfile/directives).

All'interno delle rotte `handle_response`, sono disponibili i seguenti placeholder per estrarre informazioni dalla risposta originale:

- `{resp.status_code}` Il codice di stato della risposta originale.

- `{resp.header.*}` Gli header della risposta originale.


## Esempi

Quando si usa `php_server` di [FrankenPHP](https://frankenphp.dev/), potete usare `intercept` per implementare il supporto a `X-Accel-Redirect`, servendo file statici come richiesto dall'app PHP:

```caddy
localhost {
	root * /srv

	intercept {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root * /percorso/dei/file/privati
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}

	php_server
}
```
