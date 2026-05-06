---
title: rewrite (direttiva del Caddyfile)
---

# rewrite

Riscrive l'URI della richiesta internamente.

Una riscrittura cambia parte o tutto l'URI della richiesta. Si noti che l'URI non include lo schema o l'autorità (host e porta), e i client tipicamente non inviano frammenti. Pertanto, questa direttiva viene utilizzata principalmente per la manipolazione del **percorso** (path) e della stringa di **query**.

La direttiva `rewrite` implica l'intento di accettare la richiesta, ma con delle modifiche.

È mutualmente esclusiva rispetto ad altre direttive `rewrite` nello stesso blocco, quindi è sicuro definire riscritture che altrimenti ricadrebbero l'una nell'altra, poiché verrà eseguita solo la prima riscrittura corrispondente.

Un [matcher di richiesta](/docs/caddyfile/matchers) che corrisponde a una richiesta prima del `rewrite` potrebbe non corrispondere alla stessa richiesta dopo il `rewrite`. Se volete che il vostro `rewrite` condivida una rotta con altri handler, usate le direttive [`route`](route) o [`handle`](handle).


## Sintassi

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** è l'URI verso cui riscrivere la richiesta. Verranno modificate solo le componenti dell'URI (percorso o stringa di query) specificate nella riscrittura. Il percorso dell'URI è qualsiasi sottostringa che preceda `?`. Se `?` viene omesso, l'intero token è considerato il percorso.

Prima della v2.8.0, l'argomento `<to>` poteva essere confuso dal parser per un [token matcher](/docs/caddyfile/matchers#sintassi) se iniziava con `/`, quindi era necessario specificare un token matcher wildcard (`*`).


## Direttive simili

Esistono altre direttive che eseguono riscritture, ma implicano un intento diverso o eseguono la riscrittura senza una sostituzione completa dell'URI:

- [`uri`](uri) manipola un URI (rimozione del prefisso, del suffisso o sostituzione di sottostringhe).

- [`try_files`](try_files) riscrive la richiesta in base all'esistenza dei file.



## Esempi

Riscrive tutte le richieste verso `index.html`, lasciando invariata l'eventuale stringa di query:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Si noti che prima della v2.8.0, era necessario un [matcher wildcard](/docs/caddyfile/matchers#wildcard-matchers) qui perché il primo argomento è ambiguo rispetto a un [matcher di percorso](/docs/caddyfile/matchers#path-matchers), ovvero `rewrite * /foo`, ma ora può essere semplificato in `rewrite /foo`.

</aside>

Antepone `/api` a tutte le richieste, preservando il resto dell'URI, per poi effettuare il reverse proxy verso un'app:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Sostituisce la stringa di query sulle richieste API con `a=b`, lasciando invariato il percorso:

```caddy
example.com {
	rewrite ?a=b
}
```

Solo per le richieste verso `/api/`, preserva la stringa di query esistente e aggiunge una coppia chiave-valore:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Cambia sia il percorso che la stringa di query, preservando la stringa di query originale e aggiungendo il percorso originale come parametro `p`:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
