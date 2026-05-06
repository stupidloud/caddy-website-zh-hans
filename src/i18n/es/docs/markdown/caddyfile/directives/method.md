---
title: method (directiva de Caddyfile)
---

# method

Cambia el método HTTP en la solicitud.


## Sintaxis

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** es el método HTTP al que cambiar la solicitud.


## Ejemplos

Cambiar el método para todas las solicitudes bajo `/api` a `POST`:

```caddy-d
method /api* POST
```
