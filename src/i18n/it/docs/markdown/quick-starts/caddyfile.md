---
title: Avvio rapido al Caddyfile
---

# Avvio rapido al Caddyfile

Create un nuovo file di testo chiamato `Caddyfile` (senza estensione).

La prima cosa da scrivere in un Caddyfile è l'indirizzo del vostro sito:

```caddy
localhost
```

<aside class="tip">
	Se le porte HTTP e HTTPS (rispettivamente 80 e 443) sono porte privilegiate sul vostro sistema operativo, dovrete eseguire Caddy con privilegi elevati o utilizzare porte superiori. Per ottenere il permesso, eseguitelo come root con `sudo -E` o usate `sudo setcap cap_net_bind_service=+ep $(which caddy)`. In alternativa, per usare porte superiori, cambiate semplicemente l'indirizzo in qualcosa come `localhost:2080` e cambiate la porta HTTP utilizzando l'opzione [`http_port`](/docs/caddyfile/options) del Caddyfile.
</aside>

Quindi premete invio e scrivete ciò che volete che faccia, in modo che appaia così:

```caddy
localhost

respond "Ciao, mondo!"
```

Salvate il file ed eseguite Caddy dalla stessa cartella che contiene il vostro Caddyfile:

<pre><code class="cmd bash">caddy start</code></pre>

Probabilmente vi verrà chiesta la password, perché Caddy serve tutti i siti &mdash; anche quelli locali &mdash; tramite HTTPS per impostazione predefinita. (La richiesta della password dovrebbe avvenire solo la prima volta!)

<aside class="tip">
	Per l'HTTPS locale, Caddy genera automaticamente per voi i certificati e le chiavi private univoche. Il certificato root viene aggiunto all'archivio di fiducia del vostro sistema, ed è per questo che la richiesta della password è necessaria. Ciò vi consente di sviluppare localmente tramite HTTPS senza errori di certificato.
</aside>

(Se ricevete errori di permesso, potreste dover eseguire con privilegi elevati o scegliere una porta superiore alla 1023.)

Aprite il vostro browser su [localhost](http://localhost) o usate `curl`:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Ciao, mondo!</code></pre>

Potete definire più siti in un Caddyfile racchiudendoli tra parentesi graffe `{ }`. Cambiate il vostro Caddyfile in questo modo:

```caddy
localhost {
	respond "Ciao, mondo!"
}

localhost:2016 {
	respond "Arrivederci, mondo!"
}
```

Potete fornire a Caddy la configurazione aggiornata in due modi: tramite l'API direttamente:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

oppure con il comando reload, che effettua la stessa richiesta API per voi:

<pre><code class="cmd bash">caddy reload</code></pre>

Provate il vostro nuovo endpoint "arrivederci" [nel vostro browser](https://localhost:2016) o con `curl` per assicurarvi che funzioni:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Arrivederci, mondo!</code></pre>

Quando avrete finito con Caddy, assicuratevi di fermarlo:

<pre><code class="cmd bash">caddy stop</code></pre>

## Letture consigliate

- [Concetti del Caddyfile](/docs/caddyfile/concepts)
- [Direttive](/docs/caddyfile/directives)
- [Pattern comuni](/docs/caddyfile/patterns)
