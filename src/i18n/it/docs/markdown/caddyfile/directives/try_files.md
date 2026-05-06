---
title: try_files (direttiva del Caddyfile)
---

# try_files

Riscrive il percorso dell'URI della richiesta al primo dei file elencati che esiste nella radice del sito. Se nessun file corrisponde, non viene eseguita alcuna riscrittura.


## Sintassi

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **&lt;files...&gt;** è l'elenco dei file da provare. Il percorso dell'URI verrà riscritto al primo che esiste.

  Per far corrispondere le directory, aggiungete una barra in avanti `/` finale al percorso. Tutti i percorsi dei file sono relativi alla [root](root) del sito, e i [pattern glob](https://pkg.go.dev/path/filepath#Match) verranno espansi.

  Ogni argomento può anche contenere una stringa di query, nel qual caso anche la stringa di query verrà modificata se corrisponde a quel particolare file.

  Se la `try_policy` è `first_exist` (quella predefinita), allora l'ultimo elemento dell'elenco può essere un numero preceduto da `=` (es. `=404`), che come fallback genererà un errore con quel codice; l'errore può essere intercettato e gestito con [`handle_errors`](handle_errors).

- **policy** è la policy per la scelta del file tra l'elenco dei file. 

  Predefinito: `first_exist`



## Forma estesa

La direttiva `try_files` è fondamentalmente una scorciatoia per:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

Si noti che questa direttiva non accetta un token matcher. Se avete bisogno di una logica di matching più complessa, usate la forma estesa sopra indicata come base.

Consultate il [matcher `file`](/docs/caddyfile/matchers#file) per ulteriori dettagli.



## Esempi

Se la richiesta non corrisponde ad alcun file statico, riscrive verso il vostro punto di ingresso index/router PHP:

```caddy-d
try_files {path} /index.php
```

Lo stesso, ma aggiungendo il percorso originale alla stringa di query (richiesto da alcune app PHP legacy):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

Lo stesso, ma fa corrispondere anche le directory:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Tenta la riscrittura verso un file o una directory se esiste, altrimenti genera un errore 404 (che può essere intercettato e gestito con [`handle_errors`](handle_errors)):

```caddy-d
try_files {path} {path}/ =404
```

Sceglie la versione distribuita più recentemente di un file statico (es. serve `index.be331df.html` quando viene richiesto `index.html`):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
