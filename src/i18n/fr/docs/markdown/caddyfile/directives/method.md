---
title: method (directive Caddyfile)
---

# method

Modifie la méthode HTTP de la requête de manière interne.


## Syntaxe

```caddy-d
method [<matcher>] <methode>
```

- **&lt;methode&gt;** est la méthode HTTP vers laquelle modifier la requête.


## Exemples

Modifier la méthode en `POST` pour toutes les requêtes sous `/api` :

```caddy-d
method /api* POST
```
