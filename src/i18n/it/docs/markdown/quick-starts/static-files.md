---
title: Avvio rapido ai file statici
---

# Avvio rapido ai file statici

Questa guida vi mostrerà come rendere operativo velocemente un server di file statici pronto per la produzione.

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- `caddy` nel vostro PATH
- Una cartella contenente il vostro sito web

---

Esistono due modi semplici per rendere operativo rapidamente un server di file.

## Riga di comando

Nel vostro terminale, spostatevi nella directory radice del vostro sito ed eseguite:

<pre><code class="cmd bash">caddy file-server</code></pre>

Se ricevete un errore di permessi, probabilmente significa che il vostro sistema operativo non vi permette di associarvi a porte basse &mdash; usate quindi una porta alta al suo posto:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Quindi aprite [localhost](http://localhost) (o [localhost:2015](http://localhost:2015)) nel vostro browser per vedere il vostro sito!

Se non avete un file index ma volete visualizzare un elenco dei file, usate l'opzione `--browse`:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

Potete usare un'altra cartella come radice del sito:

<pre><code class="cmd bash">caddy file-server --root ~/miosito</code></pre>



## Caddyfile

Nella radice del vostro sito, create un file chiamato `Caddyfile` con questo contenuto:

```caddy
localhost

file_server
```

Se non avete il permesso di associarvi a porte basse, sostituite `localhost` con `localhost:2015` (o un'altra porta alta).

Quindi, dalla stessa directory, eseguite:

<pre><code class="cmd bash">caddy run</code></pre>

Potete quindi caricare [localhost](https://localhost) (o qualunque sia l'indirizzo nella vostra configurazione) per vedere il vostro sito!

La [direttiva `file_server`](/docs/caddyfile/directives/file_server) ha molte altre opzioni per personalizzare il vostro sito. Assicuratevi di [ricaricare](/docs/command-line#caddy-reload) Caddy (o fermarlo e avviarlo di nuovo) quando modificate il Caddyfile!

Se non avete un file index ma volete visualizzare un elenco dei file, usate l'argomento `browse`:

```caddy
localhost

file_server browse
```

Potete anche usare un'altra cartella come radice del sito:

```caddy
localhost

root * /var/www/miosito
file_server
```
