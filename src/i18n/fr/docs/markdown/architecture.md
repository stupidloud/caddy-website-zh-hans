---
title: Architecture
---

Architecture
============

Caddy est un binaire statique unique et autonome, sans aucune dépendance externe, car il est écrit en Go. Ces valeurs constituent des éléments importants de la vision du projet, car elles simplifient le déploiement et réduisent les dépannages fastidieux en environnement de production.

S'il n'y a pas de liaison dynamique, comment peut-il être étendu ? Caddy dispose d'une architecture de plugins novatrice qui étend ses capacités bien au-delà de n'importe quel autre serveur web, même ceux ayant des dépendances externes (liées dynamiquement).

Notre philosophie de "moins de pièces mobiles" se traduit finalement par des sites plus fiables, plus faciles à gérer et moins coûteux — particulièrement à grande échelle. Ce document semi-technique décrit comment nous atteignons cet objectif grâce à l'ingénierie logicielle.


## Vue d'ensemble

Caddy se compose d'une commande, d'une bibliothèque centrale (core) et de modules.

La **commande** fournit l'[interface en ligne de commande](/docs/command-line) que vous connaissez probablement. C'est ainsi que vous lancez le processus depuis votre système d'exploitation. La quantité de code et de logique ici est assez minimale, contenant uniquement ce qui est nécessaire pour initialiser le "core" de la manière souhaitée par l'utilisateur. Nous évitons intentionnellement d'utiliser des drapeaux (flags) et des variables d'environnement pour la configuration, sauf en ce qui concerne l'initialisation de la configuration.


<aside class="tip">

Les modules peuvent ajouter des sous-commandes à l'interface en ligne de commande ! C'est par exemple de là que provient la commande [`caddy file-server`](/docs/command-line#caddy-file-server). Ces commandes ajoutées peuvent avoir tous les drapeaux ou utiliser toutes les variables d'environnement qu'elles souhaitent, même si les commandes de base de Caddy en minimisent l'usage.

</aside>


La **[bibliothèque centrale](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**, ou "core" de Caddy, gère principalement la configuration. Elle peut lancer ([`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run)) une nouvelle configuration ou arrêter ([`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop)) une configuration en cours. Elle fournit également divers utilitaires, types et valeurs à l'usage des modules.

Les **modules** s'occupent de tout le reste. De nombreux modules sont intégrés à Caddy : ce sont les _modules standard_. Ils sont jugés comme étant les plus utiles pour la majorité des utilisateurs.


<aside class="tip">

Parfois, les termes *module*, *plugin* et *extension* sont utilisés de manière interchangeable, et c'est généralement correct. Techniquement, tous les modules sont des plugins, mais tous les plugins ne sont pas des modules. Les modules sont spécifiquement un type de plugin qui étend la [structure de configuration](/docs/json/) de Caddy.

</aside>




## Le Core de Caddy

À la base, Caddy se contente de charger une configuration initiale ou, s'il n'y en a pas, d'ouvrir un socket pour accepter une nouvelle configuration ultérieurement.

Une [configuration Caddy](/docs/json/) est un document JSON, avec certains champs à son niveau supérieur :

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

Le "core" de Caddy sait nativement comment travailler avec certains de ces champs : 

- [`admin`](/docs/json/admin/) pour pouvoir mettre en place l'[API d'administration](/docs/api) et gérer le processus
- [`logging`](/docs/json/logging/) pour pouvoir [émettre des journaux](/docs/logging)

Mais les autres champs de premier niveau (comme [`apps`](/docs/json/apps/)) sont opaques pour le core de Caddy. En fait, tout ce que Caddy sait faire avec les octets de `apps` est de les désérialiser dans un type d'interface sur lequel il peut appeler deux méthodes :

1. `Start()`
2. `Stop()`

... et c'est tout. Il appelle `Start()` sur chaque application lorsqu'une configuration est chargée, et `Stop()` sur chaque application lorsqu'une configuration est déchargée.

Lorsqu'un module d'application est démarré, il initie le cycle de vie des modules de cette application.


<aside class="tip">

Si vous êtes un programmeur qui construit des modules Caddy, vous pouvez trouver des informations analogues dans notre guide [Étendre Caddy](/docs/extending-caddy), mais avec une approche plus orientée vers le code.

</aside>


## Cycle de vie d'un module

Il existe deux types de modules : les _modules hôtes_ (host modules) et les _modules invités_ (guest modules).

Les **modules hôtes** (ou modules "parents") sont ceux qui chargent d'autres modules.

Les **modules invités** (ou modules "enfants") sont ceux qui sont chargés. Tous les modules sont des modules invités — même les modules d'application.

Les modules sont chargés, provisionnés et validés, utilisés, puis nettoyés, selon cette séquence :

1. Chargé
2. Provisionné et validé
3. Utilisé
4. Nettoyé

Caddy lance le cycle de vie des modules lors du chargement d'une configuration, d'abord en initialisant tous les modules d'application configurés. À partir de là, le processus se répète en cascade à mesure que chaque module d'application prend le relais pour le reste.

### Phase de chargement (Load)

Charger un module consiste à désérialiser ses octets JSON en une valeur typée en mémoire. C'est... essentiellement tout. Il s'agit simplement de décoder du JSON en une valeur.

### Phase de provisionnement (Provision)

C'est dans cette phase que se déroule la majeure partie du travail d'installation. Tous les modules ont l'opportunité de se provisionner après avoir été chargés.

Comme toutes les propriétés provenant de l'encodage JSON auront déjà été décodées, seule la configuration supplémentaire doit avoir lieu ici. La tâche la plus courante lors du provisionnement est la configuration des modules invités. En d'autres termes, le provisionnement d'un module hôte entraîne également le provisionnement de ses modules invités, et ainsi de suite.

Vous pouvez vous en faire une idée en [parcourant la structure JSON de Caddy dans notre documentation](/docs/json/). Partout où vous voyez `{•••}`, c'est là que des modules invités peuvent être utilisés ; et en cliquant sur l'un d'eux, vous pouvez continuer l'exploration jusqu'à ce qu'il n'y ait plus de modules invités.

D'autres tâches de provisionnement courantes consistent à configurer des valeurs internes qui seront utilisées pendant la durée de vie du module, ou à normaliser les entrées. Par exemple, le module [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) utilise la phase de provisionnement pour extraire les valeurs CIDR des entrées textuelles qu'il a reçues du JSON. De cette façon, il n'a pas à le faire lors de chaque requête HTTP, ce qui est plus efficace.

La validation peut également avoir lieu lors de la phase de provisionnement. Si la configuration résultante d'un module est invalide, une erreur peut être retournée ici, ce qui interrompt tout le processus de chargement de la configuration.

### Phase d'utilisation (Use)

Une fois qu'un module invité est provisionné et validé, il peut être utilisé par son module hôte. Ce que cela signifie exactement dépend de chaque module hôte.

Chaque module possède un identifiant (ID), composé d'un espace de noms (namespace) et d'un nom dans cet espace de noms. Par exemple, [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) est un gestionnaire HTTP car il se trouve dans l'espace de noms `http.handlers` et son nom est `reverse_proxy`. Tous les modules de l'espace de noms `http.handlers` satisfont à la même interface, connue du module hôte. Ainsi, l'application `http` sait comment charger et utiliser ces types de modules.

### Phase de nettoyage (Cleanup)

Lorsqu'il est temps d'arrêter une configuration, tous les modules sont déchargés. Si un module a alloué des ressources qui doivent être libérées, il a l'opportunité de le faire lors de la phase de nettoyage.


## Branchement (Plugging in)

Un module — ou n'importe quel plugin Caddy — est "branché" à Caddy en ajoutant un `import` pour le paquet du module. En important le paquet, [le module s'enregistre](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) auprès du core de Caddy. Ainsi, au démarrage du processus Caddy, celui-ci connaît chaque module par son nom. Il peut même faire l'association entre les valeurs du module et les noms, et vice-versa.


<aside class="tip">

Des plugins peuvent être ajoutés sans modifier du tout le code source de Caddy. Il y a des instructions [dans le readme](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins) pour ce faire !

</aside>


## Gestion de la configuration

Changer la configuration active d'un serveur en cours d'exécution (souvent appelé "rechargement" ou reload) peut être délicat avec les niveaux élevés de concurrence et les milliers de paramètres requis par les serveurs. Caddy résout ce problème élégamment grâce à une conception qui présente de nombreux avantages :

- Aucune interruption des services en cours
- Des changements de configuration granulaires sont possibles
- Un seul verrou requis (en arrière-plan)
- Tous les rechargements sont atomiques, cohérents, isolés et durable ("ACID")
- État global minimal

Vous pouvez [regarder une vidéo sur la conception de Caddy 2 ici](https://www.youtube.com/watch?v=EhJO8giOqQs) (en anglais).

Un rechargement de config fonctionne en provisionnant les nouveaux modules, et si tous réussissent, les anciens sont nettoyés. Pendant une courte période, deux configurations sont opérationnelles simultanément.

Chaque configuration est associée à un [contexte](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) qui détient tout l'état du module, de sorte que la majeure partie de l'état ne s'échappe jamais de la portée d'une configuration. C'est une excellente nouvelle pour la justesse, la performance et la simplicité !

Cependant, un état véritablement global est parfois nécessaire. Par exemple, le proxy inverse peut suivre la santé de ses serveurs d'amont ; comme il n'existe qu'un seul exemplaire de chaque serveur d'amont globalement, il serait dommage qu'il les oublie à chaque changement mineur de configuration. Heureusement, Caddy [fournit des installations](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool) similaires au ramasse-miettes d'un langage de programmation pour maintenir l'état global propre.

Une approche évidente pour les mises à jour de config en ligne consiste à synchroniser l'accès à chaque paramètre de config, même dans les chemins critiques. C'est incroyablement mauvais en termes de performance et de complexité — particulièrement à grande échelle — c'est pourquoi Caddy n'utilise pas cette approche.

Au lieu de cela, les configurations sont traitées comme des unités immuables et atomiques : soit tout est remplacé, soit rien n'est changé. Les [points d'accès de l'API d'administration](/docs/api) — qui permettent des changements granulaires en naviguant dans la structure — ne modifient qu'une représentation en mémoire de la configuration, à partir de laquelle un tout nouveau document de configuration est généré et chargé. Cette approche présente des avantages considérables en termes de simplicité, de performance et de cohérence. Puisqu'il n'y a qu'un seul verrou, il est facile pour Caddy de traiter des rechargements rapides.
