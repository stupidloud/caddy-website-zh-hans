---
title: Profilage de Caddy
---

Profilage de Caddy
==================

Un **profil de programme** est un instantané de l'utilisation des ressources par un programme au moment de son exécution. Les profils peuvent être extrêmement utiles pour identifier des zones problématiques, dépanner des bugs et des plantages, et optimiser le code.

Caddy utilise les outils de Go pour capturer des profils, appelés [pprof](https://github.com/google/pprof), qui sont intégrés à la commande `go`.

Les profils rendent compte des consommateurs de CPU et de mémoire, affichent les traces de pile (stack traces) des goroutines, et aident à traquer les blocages (deadlocks) ou les primitives de synchronisation à forte contention.

Lors du signalement de certains bugs dans Caddy, nous pouvons vous demander un profil. Cet article est là pour vous aider. Il décrit comment obtenir des profils avec Caddy et comment les utiliser et les interpréter en général.


Deux choses à savoir avant de commencer :

1. **Les profils Caddy ne sont PAS sensibles en termes de sécurité.** Ils contiennent des relevés techniques inoffensifs, pas le contenu de la mémoire. Ils ne donnent pas accès aux systèmes. Ils peuvent être partagés en toute sécurité.
2. **Les profils sont légers et peuvent être collectés en production.** C'est d'ailleurs une pratique recommandée pour de nombreux utilisateurs (voir plus loin dans cet article).

## Obtenir des profils

Les profils sont disponibles via l'[interface d'administration](/docs/api) à l'adresse `/debug/pprof/`. Sur une machine faisant tourner Caddy, ouvrez cette adresse dans votre navigateur :

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	Par défaut, l'API d'administration n'est accessible que localement. Si vous l'exécutez à distance, dans des VM ou des conteneurs, consultez la section suivante pour savoir comment accéder à ce point d'accès.
</aside>

Vous remarquerez un tableau simple de compteurs et de liens, tels que :

Compteur | Profil
---------|--------------------
79       | allocs
0        | block
0        | cmdline
22       | goroutine
79       | heap
0        | mutex
0        | profile
29       | threadcreate
0        | trace
         | dump complet de la pile des goroutines

Les compteurs sont un moyen pratique d'identifier rapidement des fuites. Si vous suspectez une fuite, rafraîchissez la page à plusieurs reprises et vous verrez un ou plusieurs de ces compteurs augmenter constamment. Si le compteur "heap" augmente, il s'agit d'une possible fuite de mémoire ; si c'est "goroutine", il s'agit d'une possible fuite de goroutine.

Cliquez sur les profils pour voir à quoi ils ressemblent. Certains peuvent être vides et c'est normal la plupart du temps. Les plus couramment utilisés sont **goroutine** (piles de fonctions), **heap** (mémoire) et **profile** (CPU). D'autres profils sont utiles pour dépanner la contention de mutex ou les deadlocks.

En bas de la page, se trouve une description simple de chaque profil :

- **allocs :** Un échantillonnage de toutes les allocations mémoire passées.
- **block :** Traces de pile ayant conduit à un blocage sur des primitives de synchronisation.
- **cmdline :** L'invocation en ligne de commande du programme actuel.
- **goroutine :** Traces de pile de toutes les goroutines actuelles. Utilisez `debug=2` comme paramètre de requête pour exporter dans le même format qu'un panic non récupéré.
- **heap :** Un échantillonnage des allocations mémoire des objets vivants. Vous pouvez spécifier le paramètre GET `gc` pour lancer le ramasse-miettes (GC) avant de prendre l'échantillon.
- **mutex :** Traces de pile des détenteurs de mutex faisant l'objet d'une contention.
- **profile :** Profil CPU. Vous pouvez spécifier la durée en secondes via le paramètre GET `seconds`. Une fois le fichier de profil obtenu, utilisez la commande `go tool pprof` pour l'analyser.
- **threadcreate :** Traces de pile ayant conduit à la création de nouveaux threads du système d'exploitation.
- **trace :** Une trace d'exécution du programme actuel. Vous pouvez spécifier la durée en secondes via le paramètre GET `seconds`. Une fois le fichier obtenu, utilisez la commande `go tool trace` pour l'analyser.

<aside class="tip">

La différence entre "goroutine" et "dump complet de la pile des goroutines" réside dans le paramètre `?debug=2` : le dump complet ressemble à ce que vous verriez après un panic ; il est plus verbeux et, surtout, ne regroupe pas les goroutines identiques.

</aside>


### Télécharger des profils

Cliquer sur les liens de la page d'index pprof ci-dessus vous donnera les profils au format texte. C'est utile pour le débogage, et c'est ce que l'équipe Caddy préfère car nous pouvons les parcourir à la recherche d'indices évidents sans avoir besoin d'outils supplémentaires.

Cependant, le format par défaut est en réalité binaire. Les liens HTML ajoutent le paramètre `?debug=` pour les formater en texte, sauf pour le lien "profile" (CPU), qui n'a pas de représentation textuelle.

Voici les paramètres de requête que vous pouvez définir (d'après [la documentation de Go](https://pkg.go.dev/net/http/pprof#hdr-Parameters)) :

- **`debug=N` (tous profils sauf cpu) :** format de réponse : N = 0 : binaire (défaut), N > 0 : texte brut.
- **`gc=N` (profil heap) :** N > 0 : lance un cycle de ramasse-miettes avant le profilage.
- **`seconds=N` (profils allocs, block, goroutine, heap, mutex, threadcreate) :** retourne un profil différentiel (delta).
- **`seconds=N` (profils cpu, trace) :** profilage pour la durée indiquée.

Comme il s'agit de points d'accès HTTP, vous pouvez aussi utiliser n'importe quel client HTTP comme curl ou wget pour télécharger les profils.

Une fois vos profils téléchargés, vous pouvez les téléverser dans un commentaire de ticket GitHub ou utiliser un site comme [pprof.me](https://pprof.me/). Pour les profils CPU spécifiquement, [flamegraph.com](https://flamegraph.com/) est une autre option.


## Accès à distance

*Si vous pouvez déjà accéder à l'API d'administration localement, ignorez cette section.*

Par défaut, l'API d'administration de Caddy n'est accessible que via l'interface de boucle locale (loopback). Cependant, il existe au moins 3 façons d'accéder à distance au point d'accès `/debug/pprof` de Caddy :

### Proxy inverse via votre site

Une option simple consiste à créer un proxy inverse vers ce point d'accès depuis votre site :

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Cela rendra bien sûr les profils accessibles à toute personne pouvant se connecter à votre site. Si ce n'est pas souhaité, vous pouvez ajouter une authentification en utilisant un module d'authentification HTTP de votre choix.

(N'oubliez pas le sélecteur `/debug/pprof/*`, sinon vous ferez un proxy de l'intégralité de l'API d'administration !)


### Tunnel SSH

Une autre méthode consiste à utiliser un tunnel SSH. Il s'agit d'une connexion chiffrée utilisant le protocole SSH entre votre ordinateur et votre serveur. Lancez une commande comme celle-ci sur votre ordinateur :

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Cela redirige `localhost:8123` (sur votre machine locale) vers `localhost:2019` sur `example.com`. Veillez à remplacer `username`, `example.com` et les ports si nécessaire.

<aside class="tip">

Cette commande s'exécutera au premier plan. Gardez à l'esprit que si vous essayez de passer le processus en arrière-plan avec <kbd>Ctrl</kbd>+<kbd>Z</kbd>, cela mettra le tunnel en pause et les connexions échoueront.

</aside>

Ensuite, dans un autre terminal, vous pouvez lancer `curl` ainsi :

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Vous pouvez éviter d'avoir à utiliser `-H "Host: ..."` en utilisant le port `2019` des deux côtés du tunnel (mais cela nécessite que le port `2019` ne soit pas déjà utilisé sur votre propre ordinateur, par exemple si Caddy n'y tourne pas localement).

Tant que le tunnel est actif, vous pouvez accéder à n'importe quelle partie de l'API d'administration. Tapez <kbd>Ctrl</kbd>+<kbd>C</kbd> sur la commande `ssh` pour fermer le tunnel.

#### Tunnel permanent

Lancer un tunnel avec la commande ci-dessus nécessite de garder le terminal ouvert. Si vous voulez lancer le tunnel en arrière-plan, vous pouvez faire ainsi :

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Cela démarrera en arrière-plan et créera un socket de contrôle sur `/tmp/caddy-tunnel.sock`. Vous pourrez alors utiliser ce socket pour fermer le tunnel quand vous aurez fini :

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


### API d'administration distante

Vous pouvez également configurer l'API d'administration pour qu'elle accepte les connexions distantes de clients autorisés.

(TODO: Écrire un article à ce sujet.)



## Profils de goroutines

Le dump de goroutines est utile pour savoir quelles goroutines existent et quelles sont leurs piles d'appels. En d'autres termes, il nous donne une idée du code qui est soit en cours d'exécution, soit en train de bloquer/attendre.

Si vous cliquez sur "goroutines" ou allez sur `/debug/pprof/goroutine?debug=1`, vous verrez une liste de goroutines et leurs piles d'appels. Par exemple :

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
...
```

La première ligne, `goroutine profile: total 88`, indique ce que nous regardons et combien il y a de goroutines.

La liste des goroutines suit. Elles sont regroupées par piles d'appels, par ordre décroissant de fréquence.

Une ligne de goroutine a cette syntaxe : `<compteur> @ <adresses...>`

La ligne commence par le nombre de goroutines ayant cette pile d'appels. Le symbole `@` indique le début des adresses d'instructions d'appel (les pointeurs de fonction) d'où provient la goroutine. Chaque pointeur est un appel de fonction.

Vous remarquerez peut-être que beaucoup de vos goroutines partagent la même première adresse d'appel. Il s'agit du `main`, ou point d'entrée de votre programme. Certaines goroutines n'en proviendront pas car les programmes ont diverses fonctions `init()` et le runtime Go peut également lancer des goroutines.

Les lignes qui suivent commencent par `#` et sont en fait des commentaires destinés au lecteur. Elles contiennent la trace de pile actuelle de la goroutine. Le haut représente le haut de la pile, c'est-à-dire la ligne de code en cours d'exécution. Le bas représente le bas de la pile, ou le code que la goroutine a initialement commencé à exécuter.

La trace de pile a ce format :

```
<adresse> <paquet/fonction>+<offset> <nom_fichier>:<ligne>
```

L'adresse est le pointeur de fonction, puis vous verrez le paquet Go et le nom de la fonction (avec le nom du type associé s'il s'agit d'une méthode), et l'offset de l'instruction dans la fonction. Enfin, l'information sans doute la plus utile, le nom du fichier et le numéro de ligne, se trouvent à la fin.

### Dump complet de la pile des goroutines

Si nous changeons le paramètre de requête en `?debug=2`, nous obtenons un dump complet. Cela inclut une trace de pile verbeuse pour chaque goroutine, et les goroutines identiques ne sont pas regroupées. Cette sortie peut être très volumineuse sur des serveurs chargés, mais ce sont des informations passionnantes !

Regardons-en une correspondant à la première pile d'appels ci-dessus (tronquée) :

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

Malgré sa verbosité, les informations les plus utiles fournies de manière unique par ce dump sont les première et dernière lignes de chaque goroutine.

La première ligne contient le numéro de la goroutine (61961905), son état ("IO wait") et sa durée ("1 minutes") :

- **Numéro de goroutine :** Oui, les goroutines ont des numéros ! Mais ils ne sont pas exposés à notre code. Ces numéros sont cependant très utiles dans une trace de pile car nous pouvons voir quelle goroutine a lancé celle-ci (voir à la fin : "created by ... in goroutine 61961902"). Les outils présentés ci-dessous nous aident à dessiner des graphiques visuels de cela.

- **État :** Cela nous indique ce que la goroutine fait actuellement. Voici quelques états possibles :
	- `running` : En train d'exécuter du code — génial !
	- `IO wait` : En attente du réseau. Ne consomme pas de thread système car elle est parquée sur un gestionnaire réseau non-bloquant (network poller).
	- `sleep` : Nous en avons tous besoin.
	- `select` : Bloquée sur un select ; attend qu'un cas devienne disponible.
	- `select (no cases):` Bloquée spécifiquement sur un select vide `select {}`. Caddy en utilise un dans son main pour continuer à tourner car les arrêts sont initiés depuis d'autres goroutines.
	- `chan receive` : Bloquée sur une réception de canal (`<-ch`).
	- `semacquire` : Attend d'acquérir un sémaphore (primitive de synchronisation de bas niveau).
	- `syscall` : Exécute un appel système. Consomme un thread système.

- **Durée :** Depuis combien de temps la goroutine existe. Utile pour trouver des bugs comme les fuites de goroutines. Par exemple, si nous attendons à ce que toutes les connexions réseau soient fermées après quelques minutes, que signifie le fait de trouver de nombreuses goroutines de connexion actives depuis des heures ?

### Interpréter les dumps de goroutines

Sans regarder le code, que pouvons-nous apprendre sur la goroutine ci-dessus ?

Elle a été créée il y a environ une minute, attend des données sur un socket réseau, et son numéro de goroutine est assez élevé (61961905).

D'après le premier dump (debug=1), nous savons que sa pile d'appels est exécutée relativement fréquemment, et le numéro élevé de goroutine combiné à la courte durée suggère qu'il y a eu des dizaines de millions de ces goroutines à vie relativement courte. Elle se trouve dans une fonction nommée `pollWait` et son historique d'appels inclut la lecture de trames HTTP/2 à partir d'une connexion réseau chiffrée utilisant TLS.

On peut donc en déduire que cette goroutine traite une requête HTTP/2 ! Elle attend des données du client. De plus, nous savons que la goroutine qui l'a créée n'est pas l'une des premières du processus car elle a aussi un numéro élevé ; trouver cette goroutine dans le dump révèle qu'elle a été créée pour gérer un nouveau flux HTTP/2 au cours d'une requête existante. Par contraste, d'autres goroutines avec des numéros élevés pourraient être créées par une goroutine à bas numéro (comme 32), indiquant une toute nouvelle connexion provenant d'un appel `Accept()` sur le socket.

Chaque programme est différent, mais lors du débogage de Caddy, ces schémas ont tendance à se vérifier.

## Profils mémoire

Les profils mémoire (ou heap) suivent les allocations sur le tas, qui sont les principaux consommateurs de mémoire sur un système. Les allocations sont aussi un suspect habituel pour les problèmes de performance car allouer de la mémoire nécessite des appels système, qui peuvent être lents.

Les profils heap ressemblent aux profils de goroutines sous presque tous les aspects, sauf le début de la première ligne. Voici un exemple :

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
...
```

Le format de la première ligne est le suivant :

```
<objets vivants> <mémoire vive> [<allocations>: <mémoire allouée>] @ <adresses...>
```

Dans l'exemple ci-dessus, nous avons une seule allocation effectuée par `bufio.NewWriterSize()` mais actuellement aucun objet vivant provenant de cette pile d'appels.

Il est intéressant de noter que nous pouvons déduire de cette pile d'appels que le paquet http2 a utilisé un pool de 4 Ko pour écrire une ou des trames HTTP/2 vers le client. Vous verrez souvent des objets poolés dans les profils mémoire Go si les chemins critiques ont été optimisés pour réutiliser les allocations. Cela réduit les nouvelles allocations, et le profil heap peut vous aider à savoir si le pool est utilisé correctement !

## Profils CPU

Les profils CPU vous aident à comprendre où le programme Go passe la majeure partie de son temps planifié sur le processeur.

Cependant, il n'existe pas de forme textuelle pour ceux-ci. Dans la section suivante, nous utiliserons les commandes `go tool pprof` pour nous aider à les lire.

Pour télécharger un profil CPU, effectuez une requête vers `/debug/pprof/profile?seconds=N`, où N est le nombre de secondes pendant lesquelles vous souhaitez collecter le profil. Pendant la collecte du profil CPU, les performances du programme peuvent être légèrement impactées. (Les autres profils n'ont pratiquement aucun impact sur les performances.)

Une fois terminé, un fichier binaire devrait être téléchargé, judicieusement nommé `profile`. Nous devons ensuite l'examiner.

## `go tool pprof`

Nous allons utiliser l'analyseur de profil intégré de Go pour lire le profil CPU à titre d'exemple, mais vous pouvez l'utiliser avec n'importe quel type de profil.

Lancez cette commande (en remplaçant "profile" par le chemin réel du fichier s'il est différent), ce qui ouvre une invite interactive :

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

Vous pouvez utiliser cette commande pour examiner n'importe quel type de profil, pas seulement les profils CPU. Les principes sont les mêmes pour les autres profils et les concepts se transposent.

</aside>

C'est un outil que vous pouvez explorer. Saisir `help` vous donne une liste de commandes et `o` affichera les options actuelles. En tapant `help <commande>`, vous obtiendrez des informations sur une commande spécifique.

Il y a beaucoup de commandes, mais en voici quelques-unes courantes :

- `top` : Affiche ce qui a utilisé le plus de CPU. Vous pouvez ajouter un nombre comme `top 20` pour en voir plus, ou une expression régulière pour se "focaliser" sur certains éléments ou en ignorer.
- `web` : Ouvre le graphe d'appels dans votre navigateur web. C'est un excellent moyen de visualiser l'utilisation du CPU.
- `svg` : Génère une image SVG du graphe d'appels. C'est identique à `web` sauf qu'il n'ouvre pas votre navigateur et que le SVG est sauvegardé localement.
- `tree` : Une vue tabulaire de la pile d'appels.

Commençons par `top`. On voit une sortie comme :

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
...
```

Les 10 plus gros consommateurs de CPU étaient tous dans le runtime Go — en particulier, beaucoup de ramasse-miettes (n'oubliez pas que les appels système sont utilisés pour libérer et allouer de la mémoire). C'est un indice que nous pourrions réduire les allocations pour améliorer les performances, et qu'un profil heap vaudrait la peine.

D'accord, mais si nous voulons voir l'utilisation du CPU par notre propre code ? Nous pouvons ignorer les motifs contenant "runtime" ainsi :

```
(pprof) top -runtime
```

Eh bien, il est clair que les métriques Prometheus sont un autre gros consommateur, mais vous remarquerez que de manière cumulative, elles représentent des ordres de grandeur de moins que le GC ci-dessus. Cette différence marquée suggère que nous devrions nous concentrer sur la réduction du GC.

<aside class="tip">

Il est important de noter que les profils CPU obtiennent leurs mesures par un échantillonnage intermittent, et les échantillons ne seront jamais capturés plus fréquemment que le taux d'échantillonnage, qui est de 10 ms par défaut. C'est pourquoi vous ne verrez aucune durée cumulative inférieure à 10 ms (elles sont probablement moindres, mais arrondies au niveau supérieur). Pour des mesures plus précises, vous pouvez effectuer une trace d'exécution, qui n'utilise pas l'échantillonnage. (TODO: Ajouter une section sur le traçage.)

</aside>

Utilisons `q` pour quitter ce profil et utilisons la même commande sur le profil heap :

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
...
```

Bingo. Près de la moitié de la mémoire est allouée strictement pour les tampons de lecture et d'écriture via notre utilisation du paquet `bufio`. On peut donc en déduire qu'optimiser notre code pour réduire la mise en tampon serait très bénéfique. (Le [correctif associé dans Caddy](https://github.com/caddyserver/caddy/pull/4978) fait précisément cela).

### Visualisations

Si nous lançons plutôt les commandes `svg` ou `web`, nous obtiendrons une visualisation du profil :

![CPU profile visualization](/old/resources/images/profile.png)

Ceci est un profil CPU, mais des graphiques similaires sont disponibles pour d'autres types de profils.

Pour apprendre à lire ces graphiques, consultez [la documentation de pprof](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).


### Différenciation de profils (Diff)

Après avoir modifié le code, vous pouvez comparer l'avant et l'après à l'aide d'une analyse différentielle ("diff"). Voici un diff du heap :

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
...
</code></pre>

Comme on peut le voir, nous avons réduit les allocations mémoire d'environ la moitié !

Les diffs peuvent aussi être visualisés. Cela permet de voir très clairement comment les changements ont affecté les performances de certaines parties du programme.

## Lectures complémentaires

Il y a énormément de choses à maîtriser en matière de profilage de programme, et nous n'avons fait qu'effleurer la surface.

Pour vraiment devenir un pro du profilage, penchez-vous sur ces ressources :

- [Documentation pprof](https://github.com/google/pprof/blob/main/doc/README.md)
- [Un cas concret d'utilisation de profils avec Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Performance sur le wiki Go](https://github.com/golang/go/wiki/Performance)
- [Le paquet `net/http/pprof`](https://pkg.go.dev/net/http/pprof)
