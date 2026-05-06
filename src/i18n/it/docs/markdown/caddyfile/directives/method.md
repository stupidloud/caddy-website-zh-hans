---
title: method (direttiva del Caddyfile)
---

# method

Cambia internamente il metodo HTTP della richiesta.

Questa direttiva è utile quando è necessario che gli handler successivi nella catena (es. un reverse proxy) vedano un metodo HTTP diverso da quello originale inviato dal client.

## Sintassi

```caddy-d
method [<matcher>] &lt;verbo&gt;
```

- **&lt;verbo&gt;** è il nuovo metodo HTTP da usare (es. `GET`, `POST`).

## Esempi

Cambia tutte le richieste in `GET` per un determinato percorso:

```caddy
example.com {
	method /sola-lettura/* GET
	reverse_proxy localhost:9000
}
```
