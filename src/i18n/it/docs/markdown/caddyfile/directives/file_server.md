---
title: file_server (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Corregge l'argomento inline 'browse'
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// Aggiungeremo link a tutte le sottodirettive se un tag anchor corrispondente viene trovato nella pagina.
	addLinksToSubdirectives();
});
</script>

# file_server

Un server di file statici che supporta file system reali e virtuali. Forma i percorsi dei file aggiungendo il percorso URI della richiesta al [percorso radice del sito](root).

Per impostazione predefinita, impone gli URI canonici; il che significa che verranno emessi reindirizzamenti HTTP per le richieste verso directory che non terminano con uno slash finale (per aggiungerlo), o richieste verso file che hanno uno slash finale (per rimuoverlo). Tuttavia, i reindirizzamenti non vengono emessi se una riscrittura interna modifica l'ultimo elemento del percorso (il nome del file).

Molto spesso, la direttiva `file_server` è accoppiata alla direttiva [`root`](root) per impostare la radice dei file per l'intero sito. Questa direttiva ha anche una sottodirettiva `root` (vedi sotto) per impostare la radice solo per questo handler (non raccomandato). Si noti che la radice di un sito non garantisce il sandboxing: il server di file previene l'attraversamento delle directory (directory traversal) dai componenti del percorso, ma i collegamenti simbolici all'interno della radice possono comunque consentire accessi all'esterno della stessa.

Quando si verificano errori (es. file non trovato `404`, permesso negato `403`), verranno invocate le rotte di errore. Usate la direttiva [`handle_errors`](handle_errors) per definire le rotte di errore e visualizzare pagine di errore personalizzate.

Quando si usa `browse`, l'output predefinito è prodotto dal template HTML. I client possono richiedere l'elenco delle directory sia come JSON che come testo semplice, usando rispettivamente gli header `Accept: application/json` o `Accept: text/plain`. L'output JSON può essere utile per lo scripting, mentre l'output in testo semplice può essere utile per l'uso da terminale umano.


## Sintassi

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> specifica un file system alternativo (forse virtuale) da usare. Qui può essere usato qualsiasi modulo Caddy nel namespace `caddy.fs`. Qualsiasi percorso radice/prefisso si applicherà comunque ai moduli file system alternativi. Per impostazione predefinita, viene usato il disco locale.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 introduce il [flag `--embed`](https://github.com/caddyserver/xcaddy#custom-builds) per incorporare un albero del file system nella build personalizzata di Caddy, e registra un modulo `fs` chiamato `embedded` che permette al vostro sito statico di essere distribuito come un eseguibile Caddy.

- **root** <span id="root"/> imposta il percorso verso la radice del sito. È simile alla direttiva [`root`](root) eccetto che si applica solo a questa istanza di file server e sovrascrive qualsiasi altra radice del sito che potrebbe essere stata definita. Predefinito: `{http.vars.root}` o la directory di lavoro corrente. Nota: Questa sottodirettiva cambia la radice solo per questo handler. Affinché altre direttive (come [`try_files`](try_files) o [`templates`](templates)) conoscano la stessa radice del sito, usate invece la direttiva [`root`](root).

- **hide** <span id="hide"/> è un elenco di file o cartelle da nascondere; se richiesti, il server di file fingerà che non esistano. Accetta placeholder e pattern glob. Si noti che questi sono percorsi del *file system*, NON percorsi di richiesta. In altri termini, i percorsi relativi usano la directory di lavoro corrente come base, NON la radice del sito; inoltre tutti i percorsi vengono trasformati nella loro forma assoluta prima dei confronti (se possibile). Specificare un nome file o un pattern senza un separatore di percorso nasconderà tutti i file con un nome corrispondente indipendentemente dalla loro posizione; altrimenti, verrà tentata una corrispondenza del prefisso del percorso, e poi una corrispondenza glob. Trattandosi di una configurazione del Caddyfile, i file di configurazione attivi verranno aggiunti per impostazione predefinita. I confronti di hide fanno distinzione tra maiuscole e minuscole; sui filesystem che non ne fanno distinzione, un percorso di richiesta con un uso diverso delle maiuscole potrebbe comunque risolversi nello stesso percorso su disco, quindi `hide` non dovrebbe essere trattato come un confine di sicurezza per percorsi sensibili.

- **index** <span id="index"/> è un elenco di nomi di file da cercare come file index. Predefinito: `index.html index.txt`

- **browse** <span id="browse"/> abilita gli elenchi dei file per le richieste verso directory che non hanno un file index.

  - **&lt;template_file&gt;** <span id="template_file"/> è un file template personalizzato opzionale da usare per gli elenchi delle directory. Il valore predefinito è il template che può essere estratto usando il comando `caddy file-server export-template`, che stamperà il template predefinito su stdout. Il template integrato può essere trovato anche [qui nel codice sorgente ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html). I template di browse possono usare anche le azioni dal [modulo standard dei template](/docs/modules/http.handlers.templates#docs).

  - **reveal_symlinks** <span id="reveal_symlinks"/> abilita la rivelazione dei target dei collegamenti simbolici negli elenchi delle directory. Per impostazione predefinita, i target dei collegamenti simbolici sono nascosti e viene mostrato solo il file del collegamento stesso.

  - **sort** <span id="sort"/> cambia l'ordinamento predefinito per gli elenchi delle directory. Il primo parametro è il campo/colonna per cui ordinare: `name`, `namedirfirst`, `size`, o `time`. Il secondo argomento è una direzione opzionale: `asc` o `desc`. Ad esempio, `sort name desc` ordinerà per nome in ordine decrescente.

  - **file_limit** <span id="file_limit"/> imposta un numero massimo di file da mostrare negli elenchi delle directory. Predefinito: `10000`. Se il numero di file supera questo limite, verranno mostrati solo i primi N file, dove N è il limite specificato.

- **precompressed** <span id="precompressed"/> è l'elenco dei formati di codifica per cui cercare file "sidecar" precompressi. Gli argomenti sono un elenco ordinato di formati di codifica per cui cercare [file sidecar](https://en.wikipedia.org/wiki/Sidecar_file) precompressi. I formati supportati sono `gzip` (`.gz`), `zstd` (`.zst`) e `br` (`.br`). Se i formati vengono omessi, il valore predefinito è `br zstd gzip` (in quest'ordine).

  Tutte le ricerche di file verificheranno prima l'esistenza del file non compresso. Una volta trovato, Caddy cercherà i file sidecar con l'estensione del file di ogni formato abilitato. Se viene trovato un file sidecar precompresso, Caddy risponderà con il file precompresso, con l'header di risposta `Content-Encoding` impostato appropriatamente. In caso contrario, Caddy risponderà con il file non compresso come di consueto. Se la [direttiva `encode`](encode) è abilitata, allora potrebbe comprimere la risposta al volo se non precompressa.

- **status** <span id="status"/> è un sovrascrittura opzionale del codice di stato da usare quando si scrive la risposta. Particolarmente utile quando si risponde a una richiesta con una [pagina di errore personalizzata](handle_errors). Può essere un codice di stato a 3 cifre, ad esempio: `404`. I placeholder sono supportati. Per impostazione predefinita, il codice di stato scritto sarà tipicamente `200`, o `206` per contenuti parziali.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> disabilita il comportamento predefinito di reindirizzamento (per aggiungere uno slash finale se il percorso della richiesta è una directory, o rimuovere lo slash finale se il percorso della richiesta è un file). Si noti che, per impostazione predefinita, la canonizzazione non avverrà se l'ultimo elemento del percorso della richiesta (il nome del file) ha subito una riscrittura interna, per evitare di sovrascrivere una riscrittura esplicita con un comportamento implicito.

- **pass_thru** <span id="pass_thru"/> abilita la modalità pass-thru, che continua verso il successivo handler HTTP nella rotta se il file richiesto non viene trovato, anziché innescare un errore `404` (invocando le rotte [`handle_errors`](handle_errors)). In pratica, questo è utile solo all'interno di un blocco [`route`](route) con altre direttive handler che seguono `file_server`, perché questa direttiva è effettivamente [ordinata per ultima](/docs/caddyfile/directives#ordine-delle-direttive).


## Esempi

Un server di file statici dalla directory corrente:

```caddy-d
file_server
```

Con elenchi dei file abilitati:

```caddy-d
file_server browse
```

Serve solo file statici all'interno della cartella `/static`:

```caddy-d
file_server /static/*
```

La direttiva `file_server` è solitamente accoppiata alla [direttiva `root`](root) per impostare il percorso radice da cui servire i file:

```caddy
example.com {
	root * /srv
	file_server
}
```

<aside class="tip">

Se state eseguendo Caddy come servizio systemd, la lettura dei file da `/home` non funzionerà, perché l'utente `caddy` non ha il permesso di "esecuzione" sulla directory `/home` (necessario per l'attraversamento). Si raccomanda di posizionare i vostri file in `/srv` o `/var/www/html`.

</aside>


Nasconde tutte le cartelle `.git` e il loro contenuto:

```caddy-d
file_server {
	hide .git
}
```

Se supportato dal client (header `Accept-Encoding`) controlla l'esistenza di file precompressi accanto al file richiesto. Quindi se viene richiesto `/percorso/del/file`, controlla `/percorso/del/file.br`, `/percorso/del/file.zst` e `/percorso/del/file.gz` in quest'ordine e serve il primo file disponibile con il corrispondente `Content-Encoding`:

```caddy-d
file_server {
	precompressed
}
```
