---
title: log_append (direttiva del Caddyfile)
---

# log_append

Aggiunge un campo al log degli accessi per la richiesta corrente.

Questa direttiva deve essere utilizzata insieme alla [direttiva `log`](log), che è necessaria per abilitare il logging degli accessi.

Il valore può essere una stringa statica, o un [placeholder](/docs/caddyfile/concepts#placeholder) che verrà sostituito con il valore del placeholder al momento della richiesta.


## Sintassi

```caddy-d
log_append [<matcher>] [<]&lt;chiave&gt; &lt;valore&gt;
```

Per impostazione predefinita, il campo del log viene aggiunto durante la risalita della catena dei middleware (ovvero "tardi"), dopo che tutti gli handler successivi sono stati completati (es. dopo handler come [`reverse_proxy`](reverse_proxy), [`respond`](respond), o [`file_server`](file_server), che scrivono una risposta), catturando così lo stato finale della richiesta e della risposta.

Se viene usato `<` come prefisso alla chiave, il campo viene contrassegnato come "anticipato" (early), il che significa che il campo del log verrà aggiunto ai log *prima* di chiamare l'handler successivo nella catena, consentendo di leggere la richiesta prima che venga modificata dagli handler successivi.

Solo a scopo di debugging (non per l'uso in produzione), l'handler dispone di una gestione specializzata quando il valore è uno di questi placeholder: `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}`, o `{http.response.body_base64}`. Se viene usato un placeholder del corpo della richiesta, allora la modalità "anticipata" viene abilitata implicitamente e il corpo della richiesta verrà bufferizzato. Se viene usato un placeholder del corpo della risposta, viene abilitato il buffering della risposta per catturare il corpo della risposta e il campo viene aggiunto al log "tardi", mentre la risposta viene scritta.


## Esempi

Visualizza nei log l'area del sito da cui la richiesta viene servita, o `static` o `dynamic`:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Risposta statica!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

Visualizza nei log quale upstream del reverse proxy è stato effettivamente utilizzato (uno tra `node1`, `node2` o `node3`), il tempo impiegato per il proxying verso l'upstream in millisecondi e quanto tempo ha impiegato l'upstream proxy per scrivere l'header della risposta:

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Un campo può essere aggiunto ai log in modo "anticipato" anteponendo `<` alla chiave. Questo permette di catturare lo stato della richiesta prima che venga modificata dagli handler successivi. Ad esempio, per loggare il percorso originale della richiesta prima che subisca una riscrittura (sebbene questo sia un esempio forzato, poiché il percorso originale della richiesta viene comunque loggato, ma aiuta a illustrare il concetto):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /nuova-base{uri}
	reverse_proxy localhost:9000
}
```

A scopo di debugging, aggiunge i corpi della richiesta e della risposta ai log (non per l'uso in produzione, poiché danneggia le prestazioni e rende i log molto rumorosi). Se ci si aspetta che i corpi siano dati binari con caratteri non stampabili, è possibile usare le varianti base64 dei placeholder (es. `{http.request.body_base64}` e `{http.response.body_base64}`), che saranno più facili da copiare e ispezionare:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
