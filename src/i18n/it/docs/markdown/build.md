---
title: "Compilazione dai sorgenti"
---

# Compilazione dai sorgenti

Esistono diverse opzioni per compilare Caddy, se avete bisogno di una build personalizzata (ad esempio con dei plugin):
- [Git](#git): Compilazione dal repository Git
- [`xcaddy`](#xcaddy): Compilazione utilizzando `xcaddy`
- [Docker](#docker): Creazione di un'immagine Docker personalizzata

Requisiti:

- [Go](https://golang.org/doc/install) 1.20 o successivo

La sezione [File di supporto del pacchetto](#file-di-supporto-del-pacchetto-per-build-personalizzate-per-debianubunturaspbian) contiene istruzioni per gli utenti che hanno installato Caddy utilizzando il comando APT su sistemi derivati da Debian, ma che necessitano dell'eseguibile personalizzato per le loro operazioni.



## Git

Requisiti:

- Go installato (vedi sopra)

Clonate il repository:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Se non avete git, potete scaricare il codice sorgente come archivio di file [da GitHub](https://github.com/caddyserver/caddy). Ogni [release](https://github.com/caddyserver/caddy/releases) dispone anche di snapshot dei sorgenti.

Compilazione:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

A causa di [un bug in Go](https://github.com/golang/go/issues/29228), questi passaggi di base non incorporano le informazioni sulla versione. Se desiderate la versione (`caddy version`), dovete compilare Caddy come dipendenza anziché come modulo principale. Le istruzioni per farlo si trovano nel file [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) di Caddy. In alternativa, potete usare [`xcaddy`](#xcaddy) che automatizza questo processo.

</aside>

I programmi in Go sono facili da compilare per altre piattaforme. È sufficiente impostare le variabili d'ambiente `GOOS`, `GOARCH` e/o `GOARM` se diverse. ([Consultate la documentazione di Go per i dettagli.](https://golang.org/doc/install/source#environment))

Ad esempio, per compilare Caddy per Windows quando non siete su Windows:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

O allo stesso modo per Linux ARMv6 quando non siete su Linux o su ARMv6:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## xcaddy

Il [comando `xcaddy`](https://github.com/caddyserver/xcaddy) è il modo più semplice per compilare Caddy con le informazioni sulla versione e/o con i plugin.

Requisiti:

- Go installato (vedi sopra)
- Assicuratevi che [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) sia nel vostro `PATH`

**Non** è necessario scaricare il codice sorgente di Caddy (verrà fatto automaticamente).

Quindi, compilare Caddy (con le informazioni sulla versione) è semplice come:

<pre><code class="cmd bash">xcaddy build</code></pre>

Per compilare con i plugin, usate `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Come potete vedere, è possibile personalizzare le versioni dei plugin con la sintassi `@`. Le versioni possono essere un nome di tag, uno SHA di commit o un branch.

La compilazione cross-platform con `xcaddy` funziona allo stesso modo del comando `go`. Ad esempio, per la compilazione incrociata per macOS:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## Docker

Potete usare l'immagine `:builder` come scorciatoia per compilare un nuovo binario di Caddy con moduli personalizzati:

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Assicuratevi di sostituire `<version>` con l'ultima versione di Caddy per iniziare.

Notate la seconda istruzione `FROM`: produce un'immagine molto più piccola sovrapponendo semplicemente il binario appena compilato all'immagine standard di `caddy`.

Il builder usa `xcaddy` per compilare Caddy con i moduli forniti, in modo simile al processo [descritto sopra](#xcaddy). Le opzioni `--mount=type=cache,target=/go/pkg/mod` e `--mount=type=cache,target=/root/.cache/go-build` vengono utilizzate per memorizzare nella cache le dipendenze dei moduli Go e gli artefatti della compilazione, rispettivamente, velocizzando le build successive. Il flag è una [funzionalità di Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), non di `xcaddy`.

Per usare Docker Compose, consultate il nostro file [`compose.yml`](/docs/running#docker-compose) raccomandato e le istruzioni d'uso.



## File di supporto del pacchetto per build personalizzate per Debian/Ubuntu/Raspbian

Questa procedura mira a semplificare l'esecuzione di binari `caddy` personalizzati mantenendo i file di supporto del pacchetto `caddy`.

Questa procedura consente agli utenti di sfruttare la configurazione predefinita, i file del servizio systemd e il completamento automatico bash del pacchetto ufficiale.

Requisiti:
- Installate il pacchetto `caddy` seguendo [queste istruzioni](/docs/install#debian-ubuntu-raspbian)
- Compilate il vostro binario `caddy` personalizzato (vedi sezioni precedenti), oppure [scaricate](/download) una build personalizzata
- Il vostro binario `caddy` personalizzato deve trovarsi nella directory corrente

Procedura:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

Spiegazione:

- `dpkg-divert` sposterà il binario `/usr/bin/caddy` in `/usr/bin/caddy.default` e imposterà una deviazione nel caso in cui un pacchetto voglia installare un file in questa posizione.

- `update-alternatives` creerà un collegamento simbolico dal binario caddy desiderato a `/usr/bin/caddy`.

- `systemctl restart caddy` spegnerà la versione predefinita del server Caddy e avvierà quella personalizzata.

Potete passare dal binario `caddy` personalizzato a quello predefinito eseguendo il comando seguente e seguendo le informazioni a schermo. Quindi, riavviate il servizio Caddy.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Per aggiornare Caddy da questo momento in poi, potete eseguire [`caddy upgrade`](/docs/command-line#caddy-upgrade). Questo comando tenta di [scaricare](/download) una build con gli stessi plugin della build attuale, con l'ultima versione di Caddy, e sostituisce quindi il binario corrente con quello nuovo.
