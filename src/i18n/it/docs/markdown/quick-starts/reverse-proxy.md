---
title: Avvio rapido al reverse proxy
---

# Avvio rapido al reverse proxy

Questa guida vi mostrerà come rendere operativo velocemente un reverse proxy pronto per la produzione, con o senza HTTPS.

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- `caddy` nel vostro PATH
- Un processo backend in esecuzione verso cui effettuare il proxy

---

Questo tutorial assume che abbiate un servizio HTTP backend in esecuzione su `127.0.0.1:9000`. Questi comandi sono per Linux, ma gli stessi principi si applicano ad altri sistemi operativi.

Potete rendere operativo un semplice reverse proxy senza un file di configurazione, oppure potete usare un file di configurazione per maggiore flessibilità e controllo.


## Riga di comando

Per avviare un proxy HTTP in chiaro dalla porta 2080 alla porta 9000 sulla vostra macchina:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Quindi provatelo:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Il [comando `reverse-proxy`](/docs/command-line#reverse-proxy) è inteso per reverse proxy facili e veloci. (Potete usarlo in produzione se i vostri requisiti sono semplici.)

## Caddyfile

Nella directory di lavoro corrente, create un file chiamato `Caddyfile` con questo contenuto:

```caddy
:2080

reverse_proxy :9000
```

Quel file di configurazione è approssimativamente equivalente al comando `caddy reverse-proxy` descritto sopra.

Quindi, dalla stessa directory, eseguite:

<pre><code class="cmd bash">caddy run</code></pre>

Quindi provate il vostro proxy:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Se modificate il Caddyfile, assicuratevi di [ricaricare](/docs/command-line#caddy-reload) Caddy.

Questo era un esempio semplice. Potete fare molto di più con la [direttiva `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

## HTTPS dal client al proxy

Caddy servirà il vostro proxy tramite [HTTPS automaticamente e per impostazione predefinita](/docs/automatic-https) se conosce l'hostname (nome di dominio). Il comando `caddy reverse-proxy` userà `localhost` come predefinito se omettete il flag `--from`, oppure potete sostituire la prima riga del vostro Caddyfile con il nome di dominio del proxy.

- Se usate `localhost` o qualsiasi dominio che termina in `.localhost`, Caddy userà un certificato auto-firmato a rinnovo automatico. La prima volta che lo farete, potrebbe essere necessario inserire una password mentre Caddy tenta di installare il certificato root della sua CA nell'archivio di fiducia.
- Se usate qualsiasi altro nome di dominio, Caddy tenterà di ottenere un certificato pubblicamente affidabile; assicuratevi che i vostri record DNS puntino alla vostra macchina e che le porte 80 e 443 siano aperte al pubblico e dirette verso Caddy.

Se non specificate una porta, Caddy userà la 443 per l'HTTPS. In tal caso avrete bisogno anche dei permessi per associarvi alle porte basse. Alcuni modi per farlo su Linux:

- Eseguire come root (es. `sudo -E`).
- Oppure eseguire `sudo setcap cap_net_bind_service=+ep $(which caddy)` per dare a Caddy questa specifica capacità.

Ecco il comando `caddy reverse-proxy` più semplice che vi offre l'HTTPS:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Quindi provatelo:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Potete personalizzare l'hostname usando il flag `--from`:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

Se non avete il permesso di associarvi a porte basse, potete effettuare il proxy da una porta superiore:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Se state usando un Caddyfile, cambiate semplicemente la prima riga con il vostro nome di dominio, ad esempio:

```caddy
example.com

reverse_proxy :9000
```

## HTTPS dal proxy al backend

Caddy può anche effettuare il proxy utilizzando l'HTTPS tra se stesso e il backend se quest'ultimo supporta il TLS. Usate semplicemente `https://` nell'indirizzo del vostro backend:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Questo richiede che il certificato del backend sia considerato affidabile dal sistema su cui Caddy è in esecuzione. (Caddy non si fida dei certificati auto-firmati a meno che non sia esplicitamente configurato per farlo.)

Naturalmente, potete usare l'HTTPS su entrambi i lati:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

Questo serve l'HTTPS dal client al proxy, e dal proxy al backend.

Se l'hostname verso cui state effettuando il proxy è diverso da quello da cui state effettuando il proxy, dovrete usare il flag `--change-host-header`:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

Per impostazione predefinita, Caddy passa tutti gli header HTTP inalterati, incluso `Host`, e Caddy deriva il ServerName TLS dall'header Host. Il flag `--change-host-header` reimposta l'header Host su quello del backend in modo che l'handshake TLS possa essere completato con successo. Nell'esempio sopra, verrebbe cambiato da `example.com` a `localhost:9000` (e `localhost` verrebbe usato nell'handshake TLS).
