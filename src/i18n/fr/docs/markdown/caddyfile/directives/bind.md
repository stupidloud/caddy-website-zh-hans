---
title: bind (directive Caddyfile)
---

# bind

Surcharge l'interface sur laquelle le socket du serveur doit se lier.

Normalement, l'écouteur se lie à l'interface vide (wildcard). Cependant, vous pouvez forcer l'écouteur à se lier à un autre nom d'hôte ou IP à la place. Cette directive n'accepte qu'un hôte, pas de port. Le port est déterminé par l' [adresse du site](/docs/caddyfile/concepts#addresses) (valeur par défaut : `443`).

Notez que lier des sites de manière incohérente peut entraîner des conséquences imprévues. Par exemple, si deux sites sur le même port pointent vers `127.0.0.1` et qu'un seul de ces sites est configuré avec `bind 127.0.0.1`, alors un seul site sera accessible car l'autre se liera au port sans hôte spécifique ; l'OS choisira le socket correspondant le plus précis. (Les hôtes virtuels ne sont pas partagés entre différents écouteurs.)

`bind` accepte les [adresses réseau](/docs/conventions#network-addresses), mais ne peut pas inclure de port.


## Syntaxe

```caddy-d
bind <hôtes...>
```

- **&lt;hôtes...&gt;** est la liste des interfaces d'hôte sur lesquelles l'écouteur doit se lier. 


## Exemples

Pour rendre un socket accessible uniquement sur la machine actuelle, liez-le à l'interface de boucle locale (localhost) :

```caddy
example.com {
	bind 127.0.0.1
}
```

Pour inclure l'IPv6 :

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

Pour se lier à `10.0.0.1:8080` :

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

Pour se lier à un socket de domaine Unix sur `/run/caddy` :

```caddy
example.com {
	bind unix//run/caddy
}
```

Pour changer les permissions de fichier afin qu'il soit accessible en écriture par tous les utilisateurs (la [valeur par défaut](/docs/conventions#network-addresses) est `0200`, soit accessible en écriture uniquement par le propriétaire) :

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

Pour lier un domaine à deux interfaces différentes, avec des réponses différentes :

```caddy
example.com {
	bind 10.0.0.1
	respond "Un"
}

example.com {
	bind 10.0.0.2
	respond "Deux"
}
```
