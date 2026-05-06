---
title: abort (directive Caddyfile)
---

# abort

Empêche toute réponse au client en interrompant immédiatement la chaîne de gestionnaires HTTP et en fermant la connexion. Tout flux HTTP actif et concurrent sur la même connexion est interrompu.


## Syntaxe

```caddy-d
abort [<matcher>]
```

## Exemples

Fermer de force une connexion reçue pour des domaines inconnus lors de l'utilisation d'un certificat wildcard :

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "C'est foo !" 200
    }

    handle {
		# Les domaines non gérés arrivent ici,
		# mais nous ne voulons pas accepter leurs requêtes
        abort
    }
}
```
