---
title: Il Caddyfile
---

# Il Caddyfile

Il **Caddyfile** è un formato di configurazione di Caddy comodo e pensato per gli esseri umani. È il modo preferito dalla maggior parte degli utenti per utilizzare Caddy perché è facile da scrivere, semplice da capire ed espressivo quanto basta per la maggior parte dei casi d'uso.

Si presenta così:

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(Questo è un Caddyfile reale, pronto per la produzione, che serve WordPress con HTTPS completamente gestito.)

L'idea di base è che si digita prima l'indirizzo del sito, poi le caratteristiche o le funzionalità di cui il sito ha bisogno. [Visualizza altri pattern comuni.](/docs/caddyfile/patterns)

## Menu

- #### [Guida rapida](/docs/quick-starts/caddyfile)
  Un buon punto di partenza per familiarizzare con il Caddyfile.
- #### [Tutorial completo sul Caddyfile](/docs/caddyfile-tutorial)
  Imparate a fare diverse operazioni comuni con il Caddyfile.
- #### [Concetti del Caddyfile](/docs/caddyfile/concepts)
  Lettura obbligatoria! Struttura, indirizzi dei siti, matcher, placeholder e altro ancora.
- #### [Direttive](/docs/caddyfile/directives)
  Parole chiave all'inizio delle righe che abilitano le funzionalità per i vostri siti.
- #### [Matcher di richiesta](/docs/caddyfile/matchers)
  Filtrate le richieste utilizzando i matcher con le vostre direttive.
- #### [Opzioni globali](/docs/caddyfile/options)
  Impostazioni che si applicano all'intero server piuttosto che ai singoli siti.
- #### [Pattern comuni](/docs/caddyfile/patterns)
  Modi semplici per fare operazioni comuni.
<!-- - #### [Specifica del Caddyfile](/docs/caddyfile/spec) TODO: Finish this -->


## Nota

Il Caddyfile è solo un [adattatore di configurazione](/docs/config-adapters) per Caddy. Di solito è preferito quando si creano manualmente le configurazioni, ma non è così espressivo, flessibile o programmabile come la [struttura JSON nativa](/docs/json/) di Caddy. Se state automatizzando le vostre configurazioni/distribuzioni di Caddy, potreste voler usare JSON con l'[API di Caddy](/docs/api). (In realtà potete usare il Caddyfile anche con l'API, ma con alcune limitazioni.)
