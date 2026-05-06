---
title: request_header (direttiva del Caddyfile)
---

# request_header

Manipola i campi dell'header HTTP sulla richiesta. Può impostare, aggiungere ed eliminare i valori dell'header, o eseguire sostituzioni utilizzando espressioni regolari.

Se intendete manipolare gli header per il proxying, usate invece la [sottodirettiva `header_up`](/docs/caddyfile/directives/reverse_proxy#header_up) di `reverse_proxy`, poiché tali manipolazioni sono consapevoli del proxy.

Per manipolare gli header delle risposte HTTP, potete usare la direttiva [`header`](header).


## Sintassi

```caddy-d
request_header [<matcher>] [[+|-]<campo> [<valore>|<ricerca>] [<sostituzione>]]
```

- **&lt;campo&gt;** è il nome del campo dell'header.

  Senza prefisso, il campo viene impostato (sovrascritto).

  Prefisso con `+` per aggiungere il campo invece di sovrascriverlo se esiste già; i campi dell'header possono apparire più di una volta in una richiesta.

  Prefisso con `-` per eliminare il campo. Il campo può usare le wildcard `*` all'inizio o alla fine per eliminare tutti i campi corrispondenti.

- **&lt;valore&gt;** è il valore del campo dell'header, se si aggiunge o si imposta un campo.

- **&lt;ricerca&gt;** è la sottostringa o l'espressione regolare da cercare.

- **&lt;sostituzione&gt;** è il valore di sostituzione; obbligatorio se si esegue una ricerca e sostituzione.


## Esempi

Rimuove l'header Referer dalla richiesta:

```caddy-d
request_header -Referer
```

Elimina tutti gli header che contengono un underscore dalla richiesta:

```caddy-d
request_header -*_*
```
