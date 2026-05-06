---
title: root (direttiva del Caddyfile)
---

# root

Imposta il percorso radice del sito, utilizzato da vari matcher e direttive che accedono al file system. Se non impostato, la radice predefinita del sito è la directory di lavoro corrente.

Nello specifico, questa direttiva imposta il placeholder `{http.vars.root}`. È mutualmente esclusiva rispetto ad altre direttive `root` nello stesso blocco, quindi è sicuro definire radici multiple con matcher che si intersecano: non ricadranno l'una nell'altra sovrascrivendosi.

Questa direttiva non abilita automaticamente il servizio di file statici, quindi viene spesso utilizzata insieme alla [direttiva `file_server`](file_server) o alla [direttiva `php_fastcgi`](php_fastcgi).


## Sintassi

```caddy-d
root [<matcher>] <percorso>
```

- **&lt;percorso&gt;** è il percorso da usare come radice del sito.

Prima della v2.8.0, l'argomento `<percorso>` poteva essere confuso dal parser per un [token matcher](/docs/caddyfile/matchers#sintassi) se iniziava con `/`, quindi era necessario specificare un token matcher wildcard (`*`).


## Esempi

Imposta la radice del sito su `/home/bob/public_html` (assume che Caddy venga eseguito come utente `bob`):

<aside class="tip">

Se state eseguendo Caddy come servizio systemd, la lettura dei file da `/home` non funzionerà, perché l'utente `caddy` non ha il permesso di "esecuzione" sulla directory `/home` (necessario per l'attraversamento). Si raccomanda di posizionare i vostri file in `/srv` o `/var/www/html`.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Si noti che prima della v2.8.0, era necessario un [matcher wildcard](/docs/caddyfile/matchers#wildcard-matchers) qui perché il primo argomento è ambiguo rispetto a un [matcher di percorso](/docs/caddyfile/matchers#path-matchers), ovvero `root * /srv`, ma ora può essere semplificato in `root /srv`.

</aside>


Imposta la radice del sito su `public_html` (relativa alla directory di lavoro corrente) per tutte le richieste:

```caddy-d
root public_html
```

Cambia la radice del sito solo per le richieste in `/foo/*`:

```caddy-d
root /foo/* /home/utente/public_html/foo
```

La direttiva `root` è comunemente abbinata a [`file_server`](file_server) per servire file statici e/o a [`php_fastcgi`](php_fastcgi) per servire un sito PHP:

```caddy
example.com {
	root * /srv
	file_server
}
```
