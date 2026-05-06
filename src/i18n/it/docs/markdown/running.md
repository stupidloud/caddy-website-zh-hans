---
title: Mantenere Caddy in esecuzione
---

# Mantenere Caddy in esecuzione

Sebbene Caddy possa essere eseguito direttamente tramite la sua [interfaccia a riga di comando](/docs/command-line), l'uso di un gestore di servizi per mantenerlo in esecuzione offre numerosi vantaggi, come garantire l'avvio automatico al riavvio del sistema e catturare i log di stdout/stderr.


- [Servizio Linux](#servizio-linux)
  - [File di unità](#file-di-unita)
  - [Installazione manuale](#installazione-manuale)
  - [Uso del servizio](#uso-del-servizio)
  - [HTTPS locale](#https-locale-con-systemd)
  - [Override](#override)
	- [Variabili d'ambiente](#variabili-dambiente)
	- [Override di `run` e `reload`](#override-di-run-e-reload)
	- [Riavvio in caso di crash](#riavvio-in-caso-di-crash)
  - [Considerazioni su SELinux](#considerazioni-su-selinux)
- [Servizio Windows](#servizio-windows)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Configurazione](#configurazione)
  - [Utilizzo](#utilizzo)
  - [HTTPS locale](#https-locale-con-docker)


## Servizio Linux

<a id="servizio-linux"></a>
Il modo raccomandato per eseguire Caddy su distribuzioni Linux dotate di systemd è utilizzare i nostri file di unità systemd ufficiali.


### File di unità

<a id="file-di-unita"></a>
Forniamo due diversi file di unità systemd tra cui scegliere, a seconda del vostro caso d'uso:

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service) se configurate Caddy con un [Caddyfile](/docs/caddyfile). Se preferite utilizzare un adattatore di configurazione diverso o un file di configurazione JSON, potete effettuare l'[override](#override) dei comandi `ExecStart` e `ExecReload`.

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service) se configurate Caddy esclusivamente tramite la sua [API](/docs/api). Questo servizio utilizza l'opzione [`--resume`](/docs/command-line#caddy-run) che avvierà Caddy utilizzando il file `autosave.json`, il quale viene [mantenuto](/docs/json/admin/config/) per impostazione predefinita.

Sono molto simili, ma differiscono nei comandi `ExecStart` e `ExecReload` per adattarsi ai diversi flussi di lavoro.

Se dovete passare da un servizio all'altro, dovreste disabilitare e fermare quello precedente prima di abilitare e avviare l'altro. Ad esempio, per passare dal servizio `caddy` al servizio `caddy-api`:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


### Installazione manuale

<a id="installazione-manuale"></a>
Alcuni [metodi di installazione](/docs/install) configurano automaticamente Caddy per l'esecuzione come servizio. Se avete scelto un metodo che non lo prevede, potete seguire queste istruzioni per farlo:

**Requisiti:**

- Il binario `caddy` che avete [scaricato](/download) o [compilato dai sorgenti](/docs/build)
- `systemctl --version` 232 o successiva
- Privilegi di `sudo`

Spostate il binario di caddy nel vostro `$PATH`, ad esempio:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Verificate che funzioni:
<pre><code class="cmd bash">caddy version</code></pre>

Create un gruppo chiamato `caddy`:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Create un utente chiamato `caddy` con una home directory scrivibile:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Se utilizzate un file di configurazione, assicuratevi che sia leggibile dall'utente `caddy` appena creato.

Successivamente, [scegliete un file di unità systemd](#file-di-unita) in base al vostro caso d'uso.

**Controllate attentamente le direttive `ExecStart` e `ExecReload`.** Assicuratevi che la posizione del binario e gli argomenti della riga di comando siano corretti per la vostra installazione! Ad esempio: se utilizzate un file di configurazione, modificate il percorso di `--config` se è diverso dai valori predefiniti.

Il percorso abituale dove salvare il file del servizio è: `/etc/systemd/system/caddy.service`

Dopo aver salvato il file del servizio, potete avviarlo per la prima volta con la solita procedura systemctl:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Verificate che sia in esecuzione:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Ora siete pronti per [usare il servizio](#uso-del-servizio)!



### Uso del servizio

<a id="uso-del-servizio"></a>
Se utilizzate un Caddyfile, potete modificare la vostra configurazione con `nano`, `vi` o il vostro editor preferito:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Potete posizionare i file del vostro sito statico in `/var/www/html` o in `/srv`. Assicuratevi che l'utente `caddy` abbia i permessi per leggere i file.

Per verificare che il servizio sia in esecuzione:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
Il comando di stato mostrerà anche la posizione del file di servizio attualmente in esecuzione.

Quando si utilizza il nostro file di servizio ufficiale, l'output di Caddy viene reindirizzato a `journalctl`. Per leggere i log completi ed evitare che le righe vengano troncate:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Se utilizzate un file di configurazione, potete ricaricare Caddy gradualmente dopo aver apportato modifiche:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Potete fermare il servizio con:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Non fermate il servizio per modificare la configurazione di Caddy. Fermare il server comporterà tempi di inattività. Usate invece il comando reload.

</aside>

Il processo Caddy verrà eseguito come utente `caddy`, che ha la sua `$HOME` impostata su `/var/lib/caddy`. Ciò significa che:
- La [posizione predefinita per la memorizzazione dei dati](/docs/conventions#data-directory) (per i certificati e altre informazioni di stato) sarà in `/var/lib/caddy/.local/share/caddy`.
- La [posizione predefinita per la memorizzazione della configurazione](/docs/conventions#configuration-directory) (per la configurazione JSON salvata automaticamente, utile principalmente per il servizio `caddy-api`) sarà in `/var/lib/caddy/.config/caddy`.


### HTTPS locale con systemd

<a id="https-locale-con-systemd"></a>
Quando utilizzate Caddy per lo sviluppo locale con HTTPS, potreste usare un [hostname](/docs/caddyfile/concepts#addresses) come `localhost` o `app.localhost`. Questo abilita l'[HTTPS locale](/docs/automatic-https#local-https) utilizzando la CA locale di Caddy per emettere certificati. 

Poiché Caddy viene eseguito come utente `caddy` quando agisce come servizio, non avrà i permessi per installare il suo certificato CA radice nell'archivio di fiducia del sistema. Per farlo, eseguite [`sudo caddy trust`](/docs/command-line#caddy-trust) per completare l'installazione.

Se volete che altri dispositivi si connettano al vostro server quando utilizzate l'[emittente `internal`](/docs/caddyfile/directives/tls#internal), dovrete installare il certificato CA radice anche su quei dispositivi. Potete trovare il certificato CA radice in `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. Molti browser web ora utilizzano il proprio archivio di fiducia (ignorando quello del sistema), quindi potrebbe essere necessario installare il certificato manualmente anche lì.


### Override

<a id="override"></a>
Il modo migliore per effettuare l'override di aspetti dei file di servizio è con questo comando:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Questo aprirà un file vuoto con il vostro editor di testo predefinito del terminale nel quale potrete sovrascrivere o aggiungere direttive alla definizione dell'unità. Questo è chiamato file "drop-in".

#### Variabili d'ambiente

<a id="variabili-dambiente"></a>
Se avete bisogno di definire variabili d'ambiente da usare nella vostra configurazione, potete farlo in questo modo:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

Allo stesso modo, se preferite mantenere un file separato per le variabili d'ambiente (envfile), potete utilizzare la direttiva [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) così:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Quindi il vostro file `/etc/caddy/.env` potrebbe apparire così (non usate le virgolette `"` attorno ai valori):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

#### Override di `run` e `reload`

<a id="override-di-run-e-reload"></a>
Se dovete cambiare il file di configurazione da quello predefinito (Caddyfile) per usarne uno JSON (notate che le direttive `Exec*` [devono essere resettate con stringhe vuote](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=) prima di impostare un nuovo valore):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

#### Riavvio in caso di crash

<a id="riavvio-in-caso-di-crash"></a>
Se volete che Caddy si riavvii da solo dopo 5 secondi in caso di crash imprevisto:
```systemd
[Service]
# Riavvia automaticamente caddy in caso di crash, a meno che il codice di uscita non sia 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Quindi, salvate il file, uscite dall'editor e riavviate il servizio per rendere effettive le modifiche:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



### Considerazioni su SELinux

<a id="considerazioni-su-selinux"></a>
Sui sistemi con SELinux abilitato avete due opzioni:
1. Installare Caddy utilizzando il [repository COPR](/docs/install#fedora-redhat-centos). Il file systemd e il binario caddy saranno già creati ed etichettati correttamente (quindi potete ignorare questa sezione). Se desiderate utilizzare una build personalizzata di Caddy, dovrete etichettare l'eseguibile come descritto di seguito.

2. [Scaricare Caddy da questo sito](/download) o compilarlo con [`xcaddy`](https://github.com/caddyserver/xcaddy). In entrambi i casi, dovrete etichettare i file voi stessi.

I file di unità systemd e i loro eseguibili non verranno eseguiti a meno che non siano etichettati rispettivamente con `systemd_unit_file_t` e `bin_t`.

L'etichetta `systemd_unit_file_t` viene applicata automaticamente ai file creati in `/etc/systemd/...`, quindi assicuratevi di creare lì il vostro file `caddy.service`, come da istruzioni per l'[installazione manuale](#manual-installation).

Per etichettare il binario `caddy`, potete usare il seguente comando:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

## Servizio Windows

<a id="servizio-windows"></a>
Ci sono due modi per eseguire Caddy come servizio su Windows: [sc.exe](#scexe) o [WinSW](#winsw).

### sc.exe

<a id="scexe"></a>
Per creare il servizio, eseguite:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "VOSTRO_PERCORSO\caddy.exe run"</code></pre>

(sostituite `VOSTRO_PERCORSO` con il percorso effettivo del vostro `caddy.exe`)

Per avviare:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Per fermare:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


### WinSW

<a id="winsw"></a>
Installate Caddy come servizio su Windows seguendo queste istruzioni.

**Requisiti:**

- Il binario `caddy.exe` che avete [scaricato](/download) o [compilato dai sorgenti](/docs/build)
- Qualsiasi `.exe` dall'ultima release del wrapper di servizio [WinSW](https://github.com/winsw/winsw/releases/latest) (la configurazione del servizio qui sotto è scritta per le versioni v2.x)

Mettete tutti i file in una directory del servizio. Negli esempi seguenti, utilizziamo `C:\caddy`.

Rinominate il file `WinSW-x64.exe` in `caddy-service.exe`.

Aggiungete un file `caddy-service.xml` nella stessa directory:

```xml
<service>
  <id>caddy</id>
  <!-- Nome visualizzato del servizio -->
  <name>Caddy Web Server (alimentato da WinSW)</name>
  <!-- Descrizione del servizio -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

Ora potete installare il servizio usando:
<pre><code class="cmd bash">caddy-service install</code></pre>

Potreste voler avviare la Console dei Servizi di Windows per vedere se il servizio è in esecuzione correttamente:
<pre><code class="cmd bash">services.msc</code></pre>

Tenete presente che i servizi Windows non possono essere ricaricati, quindi dovete dire direttamente a Caddy di ricaricare:
<pre><code class="cmd bash">caddy reload</code></pre>

Il riavvio è possibile tramite i normali comandi dei servizi Windows, ad esempio tramite la scheda "Servizi" di Gestione Attività.

Per personalizzare il wrapper del servizio, consultate la [documentazione di WinSW](https://github.com/winsw/winsw/tree/master#usage)


## Docker Compose

<a id="docker-compose"></a>
Il modo più semplice per iniziare con Docker è utilizzare Docker Compose. Consultate la documentazione su [Docker Hub](https://hub.docker.com/_/caddy) for ulteriori dettagli sull'immagine Docker ufficiale di Caddy.

<aside class="tip">

Questo presuppone che stiate usando [Docker Compose V2](https://docs.docker.com/compose/reference/), dove il comando è ora `docker compose` (con lo spazio) invece di `docker-compose` (con il trattino) della V1.

</aside>

### Configurazione

<a id="configurazione"></a>
Per prima cosa, create un file `compose.yml` (o aggiungete questo servizio al vostro file esistente):

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Assicuratevi di inserire la `<version>` dell'immagine con l'ultimo numero di versione, che potete trovare elencato su [Docker Hub](https://hub.docker.com/_/caddy) nella sezione "Tags".

Cosa fa questa configurazione:

- Utilizza la policy di riavvio `unless-stopped` per garantire che il container Caddy venga riavviato automaticamente al riavvio della macchina.
- Si collega alle porte `80` e `443` rispettivamente per HTTP e HTTPS, più `443/udp` per HTTP/3.
- Monta la directory `conf` che contiene la configurazione del vostro Caddyfile.
- Monta la directory `site` per servire i file statici del vostro sito da `/srv`.
- Volumi nominati per `/data` e `/config` per [mantenere informazioni importanti](/docs/conventions#file-locations).

Quindi, create un file chiamato `Caddyfile` come unico file nella directory `conf` e scrivete la vostra configurazione del [Caddyfile](/docs/caddyfile/concepts).

Se avete file statici da servire, potete posizionarli in una directory `site/` accanto alle configurazioni, quindi impostare la [`root`](/docs/caddyfile/directives/root) usando `root /srv`. In caso contrario, potete rimuovere il montaggio del volume `/srv`.

<aside class="tip">

Se state usando Caddy come [reverse proxy](/docs/caddyfile/directives/reverse_proxy) verso un altro container, ricordate che nel networking di Docker, `localhost` significa "questo container", non "questa macchina". Quindi, ad esempio, non usate `reverse_proxy localhost:8080`, ma usate `reverse_proxy altro-container:8080`.

</aside>

Se avete bisogno di una build personalizzata di Caddy con dei plugin, seguite le [istruzioni per la build Docker](/docs/build#docker) per creare un'immagine Docker personalizzata. Create il `Dockerfile` accanto al vostro `compose.yml`, quindi sostituite la riga `image:` nel vostro `compose.yml` con `build: .`.



### Utilizzo

<a id="utilizzo"></a>
Successivamente, potete avviare il container:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Per ricaricare Caddy dopo aver apportato modifiche al vostro Caddyfile:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Dalla v2.11.0, potete ricaricare usando `SIGUSR1`, a condizione che Caddy sia stato avviato con `caddy run` e un file di configurazione:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Per vedere i 1000 log più recenti di Caddy e seguirne i nuovi in tempo reale:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

### HTTPS locale con Docker

<a id="https-locale-con-docker"></a>
Quando utilizzate Docker per lo sviluppo locale con HTTPS, potreste usare un [hostname](/docs/caddyfile/concepts#addresses) come `localhost` or `app.localhost`. Questo abilita l'[HTTPS locale](/docs/automatic-https#local-https) utilizzando la CA locale di Caddy per emettere certificati. Ciò significa che i client HTTP al di fuori del container non si fideranno del certificato TLS servito da Caddy. Per risolvere il problema, potete installare il certificato CA radice di Caddy nell'archivio di fiducia del vostro computer host:

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

Molti browser web ora utilizzano il proprio archivio di fiducia (ignorando quello del sistema), quindi potrebbe essere necessario installare il certificato manualmente anche lì, utilizzando il file `root.crt` copiato dal container nel comando sopra.

- Per Firefox, andate in Preferenze > Privacy e sicurezza > Certificati > Mostra certificati > Autorità > Importa, e selezionate il file `root.crt`.

- For Chrome, andate in Impostazioni > Privacy e sicurezza > Sicurezza > Gestisci certificati > Autorità > Importa, e selezionate il file `root.crt`.
