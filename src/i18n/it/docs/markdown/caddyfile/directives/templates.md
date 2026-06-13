---
title: templates (direttiva del Caddyfile)
---

# templates

Esegue il corpo della risposta come un documento [template](/docs/modules/http.handlers.templates). I template forniscono primitive funzionali per la creazione di semplici pagine dinamiche. Le funzionalità includono sub-richieste HTTP, inclusioni di file HTML, rendering di Markdown, analisi di JSON, strutture dati di base, casualità, tempo e altro ancora.

<aside class="tip">

I template possono essere eseguiti sul corpo della risposta proveniente da *qualsiasi* origine, che si tratti di un file statico su disco o di un servizio web dietro proxy. Sarebbe saggio abilitare la valutazione dei template solo per contenuti di cui ti fidi, che controlli e/o che sanifichi! Una configurazione errata può causare violazioni della sicurezza. Ad esempio, se un'app dietro proxy consente agli utenti di scrivere/pubblicare contenuti, e tali contenuti includono testo che assomiglia ad azioni dei template, ciò consentirebbe a utenti arbitrari di valutare i template e potenzialmente di accedere all'ambiente, ai file locali e alla rete. Non abilitare i template su contenuti generati dagli utenti (senza sanificarli).

</aside>


## Sintassi

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** sono i tipi MIME su cui interverrà il middleware dei template; qualsiasi risposta che non abbia un `Content-Type` idoneo non verrà valutata come template.

  Predefinito: `text/html text/plain`.

- **between** sono i delimitatori di apertura e chiusura per le azioni del template. Potete cambiarli se interferiscono con il resto del vostro documento.

  Predefinito: `{{printf "{{ }}"}}`.

- **root** è la radice del sito, quando si usano funzioni che accedono al file system.

  Il valore predefinito è la radice del sito impostata dalla [direttiva `root`](root), o la directory di lavoro corrente se non impostata.

- **extensions** permette di registrare funzioni template personalizzate fornite da moduli nel namespace `http.handlers.templates.functions.*`.

  Ogni sottodirettiva all'interno del blocco corrisponde a un nome di modulo. Questi moduli possono aggiungere funzioni personalizzate alla mappa delle funzioni del template, tipicamente usate per implementare componenti riutilizzabili. Questa funzionalità è principalmente intesa per i plugin.

La documentazione per le funzioni template integrate può essere trovata nel [modulo templates](/docs/modules/http.handlers.templates#docs).



## Esempi

Per un esempio completo di un sito che usa i template per servire il markdown, date un'occhiata al codice sorgente di [questo stesso sito web](https://github.com/caddyserver/website)! Nello specifico, guardate il [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) e [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html).

Abilita i template per un sito statico:

```caddy
example.com {
	root * /srv
	templates
	file_server
}
```

Per servire una semplice risposta statica usando un template, assicuratevi di impostare `Content-Type`:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `L'anno corrente è: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Uso di un'estensione del template (plugin):

```caddy
example.com {
	root * /srv
	templates {
		extensions {
			# Richiede il plugin caddy-hitcounter:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
