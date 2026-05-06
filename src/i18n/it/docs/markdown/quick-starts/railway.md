---
title: Avvio rapido a Railway
---

# Avvio rapido a Railway

Distribuire Caddy su Railway è un modo semplice e senza intoppi per distribuire una build di Caddy personalizzata con dei plugin.

**Prerequisiti:**
- Un account [Railway](https://railway.com) gratuito

## Distribuire Caddy su Railway

Andate alla nostra [pagina di download](/download) e selezionate i plugin necessari, quindi cliccate sul pulsante viola "Deploy on Railway" in alto.

<details>
	<summary>Oppure, configura il template manualmente</summary>

In alternativa, se desiderate configurare il template Railway da soli, ecco come fare.

Andate al template su Railway:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

e aggiungete i plugin necessari cliccando su "Configure":

![Schermata di distribuzione](/resources/images/railway/deploy-screen.png)

Quindi incollate i plugin nella variabile `CADDY_PLUGINS`, separati da spazi:

![Aggiunta plugin](/resources/images/railway/deploy-config.png)

</details>

Cliccate su Deploy, poi al termine della distribuzione potrete provarlo cliccando sul link qui:

![Visita la tua distribuzione](/resources/images/railway/prod-link.png)

Dovreste vedere una pagina di benvenuto che mostra che il vostro nuovo server è in funzione!

Successivamente, potrete personalizzare la vostra distribuzione per servire il vostro sito o effettuare il proxy verso un altro servizio Railway.

## Personalizzare la distribuzione

Per servire il vostro sito web o per cambiare la configurazione, è sufficiente effettuare l'"eject" del [nostro template](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) nel vostro repository:

![Eject template](/resources/images/railway/eject.png)

Dal vostro repository potrete:

- Inserire il vostro sito nella cartella `www`.
- Modificare la configurazione di Caddy, ovvero il [Caddyfile](/docs/caddyfile).

È sufficiente effettuare il commit delle modifiche e il push, quindi potrete ridistribuire su Railway.

Se desiderate cambiare i plugin nella vostra build di Caddy, tutto ciò che dovete fare è modificare la variabile `CADDY_PLUGINS` e ridistribuire:

![Cambia plugin](/resources/images/railway/plugins-variable.png)

## Suggerimenti

Railway termina il TLS per voi, quindi dovreste scrivere la configurazione di Caddy come se fosse dietro un proxy (perché lo è). Pertanto, se usate gli host negli indirizzi del sito del vostro Caddyfile, dovreste usare `auto_https off` nelle vostre opzioni globali. Con il nostro template, Caddy non è rivolto direttamente alla rete esterna (edge-facing).


## Variabili

Variabili d'ambiente che potete impostare nel vostro progetto Railway e che questo template potrebbe utilizzare:

Nome | Descrizione | Predefinito | Esempio/i
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | Elenco di plugin Caddy separati da spazi | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
