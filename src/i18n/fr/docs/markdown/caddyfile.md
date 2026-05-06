---
title: Le Caddyfile
---

# Le Caddyfile

Le **Caddyfile** est un format de configuration de Caddy pratique et conçu pour les humains. C'est la méthode préférée de la plupart des utilisateurs car il est facile à écrire, facile à comprendre et suffisamment expressif pour la majorité des cas d'utilisation.

Il ressemble à ceci :

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(Il s'agit d'un véritable Caddyfile prêt pour la production qui sert un site WordPress avec HTTPS entièrement géré.)

L'idée de base est de saisir d'abord l'adresse de votre site, puis les fonctionnalités ou fonctions dont votre site a besoin. [Voir d'autres modèles courants.](/docs/caddyfile/patterns)

## Menu

- #### [Guide de démarrage rapide](/docs/quick-starts/caddyfile)
  Un bon point de départ pour se familiariser avec le Caddyfile.
- #### [Tutoriel complet du Caddyfile](/docs/caddyfile-tutorial)
  Apprenez à réaliser diverses tâches courantes avec le Caddyfile.
- #### [Concepts du Caddyfile](/docs/caddyfile/concepts)
  Lecture indispensable ! Structure, adresses de sites, sélecteurs, espaces réservés (placeholders), etc.
- #### [Directives](/docs/caddyfile/directives)
  Mots-clés en début de ligne qui activent des fonctionnalités pour vos sites.
- #### [Sélecteurs de requête (Matchers)](/docs/caddyfile/matchers)
  Filtrez les requêtes en utilisant des sélecteurs avec vos directives.
- #### [Options globales](/docs/caddyfile/options)
  Paramètres s'appliquant à l'ensemble du serveur plutôt qu'à des sites individuels.
- #### [Modèles courants](/docs/caddyfile/patterns)
  Des manières simples de réaliser des tâches courantes.
<!-- - #### [Spécification du Caddyfile](/docs/caddyfile/spec) TODO: Terminer ceci -->


## Note

Le Caddyfile n'est qu'un [adaptateur de configuration](/docs/config-adapters) pour Caddy. Il est généralement préféré lors de la création manuelle de configurations, mais il n'est pas aussi expressif, flexible ou programmable que la [structure JSON native](/docs/json/) de Caddy. Si vous automatisez vos configurations ou déploiements Caddy, vous pourriez souhaiter utiliser le JSON avec l'[API de Caddy](/docs/api). (Vous pouvez en réalité utiliser le Caddyfile avec l'API également, mais de manière plus limitée.)
