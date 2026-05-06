---
title: method (diretiva do Caddyfile)
---

# method

Altera o método HTTP da requisição.


## Sintaxe

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** é o método HTTP para o qual a requisição será alterada.


## Exemplos

Altere o método de todas as requisições sob `/api` para `POST`:

```caddy-d
method /api* POST
```
