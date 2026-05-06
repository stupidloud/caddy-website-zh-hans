---
title: Tutorial sul Caddyfile
---

# Tutorial sul Caddyfile

Questo tutorial vi insegnerà le basi dell'[HTTP Caddyfile](/docs/caddyfile) in modo da poter creare rapidamente e facilmente configurazioni di siti funzionali e dall'aspetto gradevole.

**Obiettivi:**
- 🔲 Primo sito
- 🔲 Server di file statici
- 🔲 Template
- 🔲 Compressione
- 🔲 Siti multipli
- 🔲 Matcher
- 🔲 Variabili d'ambiente
- 🔲 Commenti

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- Competenze di base con editor di testo
- `caddy` nel vostro PATH

---

Create un nuovo file di testo chiamato `Caddyfile` (senza estensione).

La prima cosa da digitare è l'[indirizzo](/docs/caddyfile/concepts#addresses) del vostro sito:

```caddy
localhost
```

<aside class="tip">

Se le porte HTTP e HTTPS (rispettivamente 80 e 443) sono porte privilegiate sul vostro sistema operativo, dovrete eseguire Caddy con privilegi elevati o utilizzare una porta superiore. Per utilizzare una porta superiore, modificate semplicemente l'indirizzo in qualcosa come `localhost:2015` e cambiate la porta HTTP utilizzando l'opzione [http_port](/docs/caddyfile/options) del Caddyfile.

</aside>


Quindi premete invio e digitate ciò che volete che il sito faccia. Per questo tutorial, impostate il vostro Caddyfile così:

```caddy
localhost

respond "Hello, world!"
```

Salvate e avviate Caddy (trattandosi di un tutorial di formazione, useremo il flag `--watch` in modo che le modifiche al Caddyfile vengano applicate automaticamente):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Se ricevete errori di permessi, provate a usare una porta superiore nel vostro indirizzo (come `localhost:2015`) e [cambiate la porta HTTP](/docs/caddyfile/options), oppure eseguite con privilegi elevati.

</aside>


La prima volta vi verrà chiesta la password. Questo serve affinché Caddy possa servire il vostro sito tramite HTTPS.

<aside class="tip">

Caddy serve tutti i siti tramite HTTPS per impostazione predefinita, a condizione che un host o un IP faccia parte dell'indirizzo del sito. L'[HTTPS automatico](/docs/automatic-https) può essere disabilitato anteponendo esplicitamente `http://` all'indirizzo.

</aside>


<aside class="complete">Primo sito</aside>

Aprite [localhost](https://localhost) nel vostro browser e vedrete il vostro server web in funzione, completo di HTTPS!

<aside class="tip">
	Potrebbe essere necessario riavviare il browser se ricevete un errore di certificato la prima volta.
</aside>

Non è particolarmente entusiasmante, quindi cambiamo la nostra risposta statica in un [server di file](/docs/caddyfile/directives/file_server) con l'elenco delle directory abilitato:

```caddy
localhost

file_server browse
```

Salvate il vostro Caddyfile, quindi aggiornate la scheda del browser. Dovreste vedere un elenco di file o una pagina HTML se nella directory corrente è presente un file index.

<aside class="complete">Server di file statici</aside>

## Aggiungere funzionalità

Facciamo qualcosa di interessante con il nostro server di file: servire una pagina con template. Create un nuovo file e incollateci questo contenuto:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Pagina caricata il: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Salvatelo come `caddy.html` nella directory corrente e caricatelo nel browser: [https://localhost/caddy.html](https://localhost/caddy.html)

L'output è:

```
Pagina caricata il: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Aspettate un momento. Dovremmo vedere la data di oggi. Perché non ha funzionato? Perché il server non è ancora stato configurato per elaborare i template! È facile da risolvere: basta aggiungere una riga al Caddyfile in modo che appaia così:

```caddy
localhost

templates
file_server browse
```

Salvate e ricaricate la scheda del browser. Dovreste vedere:

```
Pagina caricata il: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Con il [modulo templates](/docs/modules/http.handlers.templates) di Caddy, potete fare molte cose utili con i file statici, come includere altri file HTML, effettuare sub-richieste, impostare gli header di risposta, lavorare con strutture dati e altro ancora!

<aside class="complete">Template</aside>

È buona norma comprimere le risposte con un algoritmo di compressione veloce e moderno. Abilitiamo il supporto a Gzip e Zstandard usando la direttiva [`encode`](/docs/caddyfile/directives/encode):

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Compressione</aside>

Questo è il processo di base per configurare un sito semi-avanzato e pronto per la produzione!

Quando sarete pronti ad attivare l'[HTTPS automatico](/docs/automatic-https), sostituite semplicemente l'indirizzo del vostro sito (`localhost` nel nostro tutorial) con il vostro nome di dominio. Consultate la nostra [guida rapida all'HTTPS](/docs/quick-starts/https) per ulteriori informazioni.

## Siti multipli

Con il nostro attuale Caddyfile, possiamo avere solo una definizione di sito! Solo la prima riga può contenere l'indirizzo (o gli indirizzi) del sito, e tutto il resto del file deve contenere le direttive per quel sito.

Ma è facile fare in modo di poter aggiungere più siti!

Il nostro Caddyfile finora:

```caddy
localhost

encode
templates
file_server browse
```

è equivalente a questo:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

con la differenza che il secondo ci permette di aggiungere più siti.

Racchiudendo il blocco del nostro sito tra parentesi graffe `{ }`, siamo in grado di definire più siti diversi nello stesso Caddyfile.

Per esempio:

```caddy
:8080 {
	respond "Sono la porta 8080"
}

:8081 {
	respond "Sono la porta 8081"
}
```

Quando si racchiudono i blocchi del sito tra parentesi graffe, solo gli [indirizzi](/docs/caddyfile/concepts#addresses) appaiono all'esterno delle graffe e solo le [direttive](/docs/caddyfile/directives) appaiono al loro interno.

Per più siti che condividono la stessa configurazione, potete aggiungere più indirizzi, per esempio:

```caddy
:8080, :8081 {
	...
}
```

Potete quindi definire tutti i siti diversi che volete, a patto che ogni indirizzo sia unico.

<aside class="complete">Siti multipli</aside>


## Matcher

Potremmo voler applicare alcune direttive solo a determinate richieste. Ad esempio, supponiamo di voler avere sia un server di file che un reverse proxy, ma ovviamente non possiamo fare entrambe le cose per ogni richiesta! O il server di file scriverà una risposta con un file statico, o il reverse proxy passerà la richiesta a un backend e riscriverà la sua risposta.

Questa configurazione non funzionerà come desiderato (`reverse_proxy` avrà la precedenza a causa dell'[ordine delle direttive](/docs/caddyfile/directives#directive-order)):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

In pratica, potremmo voler usare il reverse proxy solo per le richieste API, ovvero le richieste con un percorso di base `/api/`. È facile farlo aggiungendo un [token matcher](/docs/caddyfile/matchers#syntax):

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

Ecco fatto; ora il reverse proxy avrà la priorità per tutte le richieste che iniziano con `/api/`.

La parte `/api/*` che abbiamo appena aggiunto è chiamata **token matcher**. Potete riconoscerlo perché inizia con una barra in avanti `/` e appare subito dopo la direttiva (ma potete sempre verificarlo nella [documentazione della direttiva](/docs/caddyfile/directives) per esserne sicuri).

I matcher sono davvero potenti. Potete dichiarare dei matcher con nome e usarli come `@nome` per far corrispondere molto di più del semplice percorso della richiesta! Prendetevi un momento per [saperne di più sui matcher](/docs/caddyfile/matchers) prima di continuare!

<aside class="complete">Matcher</aside>

## Variabili d'ambiente

L'adattatore Caddyfile consente di sostituire le [variabili d'ambiente](/docs/caddyfile/concepts#environment-variables) prima che il Caddyfile venga analizzato.

Per prima cosa, impostate una variabile d'ambiente (nella stessa shell che esegue Caddy):

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Quindi potete usarla così nel Caddyfile:

```caddy
{$SITE_ADDRESS}

file_server
```

Prima che il Caddyfile venga analizzato, verrà espanso in:

```caddy
localhost:9055

file_server
```

Potete usare le variabili d'ambiente ovunque nel Caddyfile, per qualsiasi numero di token.

<aside class="complete">Variabili d'ambiente</aside>


## Commenti

Un'ultima cosa che troverete molto utile: se volete annotare o scrivere una nota nel vostro Caddyfile, potete usare i commenti, che iniziano con `#`:

```caddy
# questo inizia un commento
```

<aside class="complete">Commenti</aside>

## Letture consigliate

- [Concetti del Caddyfile](/docs/caddyfile/concepts)
- [Direttive](/docs/caddyfile/directives)
- [Pattern comuni](/docs/caddyfile/patterns)
