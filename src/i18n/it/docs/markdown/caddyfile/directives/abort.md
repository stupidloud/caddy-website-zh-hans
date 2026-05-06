---
title: abort (direttiva del Caddyfile)
---

# abort

Interrompe la richiesta HTTP immediatamente.

Questa direttiva chiude la connessione con il client senza inviare alcuna risposta, nemmeno un codice di stato. È utile per prevenire abusi o per determinati scenari di sicurezza.

## Sintassi

```caddy-d
abort [<matcher>]
```

## Esempi

Interrompe le richieste provenienti da determinati IP:

```caddy
example.com {
	@cattivi remote_ip 1.2.3.4
	abort @cattivi
}
```
