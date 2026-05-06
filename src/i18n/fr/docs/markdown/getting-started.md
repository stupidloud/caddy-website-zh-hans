---
title: "Premiers pas"
---

<a id="getting-started"></a>
# Premiers pas

Bienvenue sur Caddy ! Ce tutoriel explore les bases de l'utilisation de Caddy et vous aidera à vous familiariser avec l'outil à un haut niveau.

**Objectifs :**
- 🔲 Lancer le démon (daemon)
- 🔲 Essayer l'API
- 🔲 Donner une configuration à Caddy
- 🔲 Tester la configuration
- 🔲 Créer un Caddyfile
- 🔲 Utiliser l'adaptateur de configuration
- 🔲 Démarrer avec une configuration initiale
- 🔲 Comparer le JSON et le Caddyfile
- 🔲 Comparer l'API et les fichiers de configuration
- 🔲 Exécuter en arrière-plan
- 🔲 Rechargement de configuration sans interruption

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- Compétences de base en édition de texte
- `caddy` et `curl` présents dans votre PATH

---

**Si vous avez [installé Caddy](/docs/install) via un gestionnaire de paquets, Caddy est peut-être déjà en cours d'exécution en tant que service. Si c'est le cas, veuillez arrêter le service avant de suivre ce tutoriel.**

Commençons par le lancer :

<pre><code class="cmd bash">caddy</code></pre>

Oups ; sans sous-commande, la commande `caddy` affiche seulement l'aide. Vous pouvez l'utiliser dès que vous oubliez quoi faire.

Pour démarrer Caddy en tant que démon, utilisez la sous-commande `run` :

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Lancer le démon</aside>

Cela bloque le terminal indéfiniment, mais que se passe-t-il ? Pour l'instant... rien. Par défaut, la configuration de Caddy est vide. Nous pouvons le vérifier en utilisant l'[API d'administration](/docs/api) dans un autre terminal :

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

Ce n'est **pas** votre site web : le point d'accès (endpoint) d'administration sur localhost:2019 est utilisé pour contrôler Caddy et est restreint à l'hôte local par défaut.

</aside>


<aside class="complete">Essayer l'API</aside>

Nous pouvons rendre Caddy utile en lui donnant une configuration. Il y a plusieurs manières de procéder, mais nous allons commencer par faire une requête POST sur le point d'accès [/load](/docs/api#post-load) avec `curl` dans la section suivante.



<a id="your-first-config"></a>
## Votre première configuration

Pour préparer notre requête, nous devons créer une configuration. Dans son essence, la configuration de Caddy est simplement un [document JSON](/docs/json/).

Enregistrez ceci dans un fichier JSON (par exemple `caddy.json`) :

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

<aside class="tip">

L'utilisation de fichiers de configuration n'est pas obligatoire, mais nous en utilisons un pour ce tutoriel. L'[API d'administration](/docs/api) de Caddy est conçue pour être utilisée par d'autres programmes ou scripts.

</aside>


Ensuite, envoyez-le :

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Donner une configuration à Caddy</aside>

Nous pouvons vérifier que Caddy a appliqué notre nouvelle configuration avec une autre requête GET :

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Testez que cela fonctionne en vous rendant sur [localhost:2015](http://localhost:2015) dans votre navigateur ou utilisez `curl` :

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Si vous voyez _Hello, world!_, alors félicitations — ça fonctionne ! Il est toujours bon de s'assurer que votre configuration fonctionne comme prévu, surtout avant de la déployer en production.

<aside class="complete">Tester la configuration</aside>


<a id="your-first-caddyfile"></a>
## Votre premier Caddyfile

C'était *un peu laborieux* juste pour un "Hello World".

Une autre manière de configurer Caddy est d'utiliser le [**Caddyfile**](/docs/caddyfile). La même configuration que celle écrite en JSON plus haut peut s'exprimer simplement ainsi :

```caddy
:2015

respond "Hello, world!"
```


Enregistrez cela dans un fichier nommé `Caddyfile` (sans extension) dans le répertoire courant.

<aside class="complete">Créer un Caddyfile</aside>

Arrêtez Caddy s'il est déjà lancé (<kbd>Ctrl</kbd>+<kbd>C</kbd>), puis exécutez :

<pre><code class="cmd bash">caddy adapt</code></pre>

Ou si vous avez enregistré le Caddyfile ailleurs ou sous un autre nom :

<pre><code class="cmd bash">caddy adapt --config /chemin/vers/Caddyfile</code></pre>

Vous verrez une sortie JSON ! Que s'est-il passé ?

Nous venons d'utiliser un [_adaptateur de configuration_](/docs/config-adapters) pour convertir notre Caddyfile vers la structure JSON native de Caddy.

<aside class="complete">Utiliser l'adaptateur de configuration</aside>

Bien que nous pourrions prendre cette sortie et faire une autre requête API, nous pouvons sauter toutes ces étapes car la commande `caddy` peut le faire pour nous. S'il existe un fichier nommé Caddyfile dans le répertoire courant et qu'aucune autre configuration n'est spécifiée, Caddy chargera le Caddyfile, l'adaptera pour nous et le lancera immédiatement.

Maintenant qu'il y a un Caddyfile dans le dossier courant, exécutons à nouveau `caddy run` :

<pre><code class="cmd bash">caddy run</code></pre>

Ou si votre Caddyfile est ailleurs :

<pre><code class="cmd bash">caddy run --config /chemin/vers/Caddyfile</code></pre>

(S'il porte un autre nom qui ne commence pas par "Caddyfile", vous devrez spécifier `--adapter caddyfile`.)

Vous pouvez maintenant essayer de charger votre site à nouveau et vous verrez qu'il fonctionne !

<aside class="complete">Démarrer avec une configuration initiale</aside>

Comme vous pouvez le voir, il existe plusieurs façons de démarrer Caddy avec une configuration initiale :

- Un fichier nommé Caddyfile dans le répertoire courant
- Le drapeau `--config` (optionnellement avec le drapeau `--adapter`)
- Le drapeau `--resume` (si une configuration a été chargée précédemment)


<a id="json-vs-caddyfile"></a>
## JSON vs Caddyfile

Vous savez maintenant que le Caddyfile est simplement converti en JSON pour vous.

Le Caddyfile semble plus facile que le JSON, mais devriez-vous toujours l'utiliser ? Chaque approche a ses avantages et ses inconvénients. La réponse dépend de vos besoins et de votre cas d'utilisation.

JSON | Caddyfile
-----|----------
Facile à générer | Facile à rédiger à la main
Facilement programmable | Difficile à automatiser
Extrêmement expressif | Modérément expressif
Toute la gamme des fonctionnalités Caddy | La plupart des fonctionnalités Caddy
Permet de parcourir la configuration | Impossible de naviguer dans le Caddyfile
Modifications partielles de config | Uniquement des changements complets
Peut être exporté | Ne peut pas être exporté
Compatible avec tous les endpoints API | Compatible avec certains endpoints API
Documentation générée automatiquement | Documentation rédigée à la main
Omniprésent | Niche
Plus efficace | Plus coûteux en calcul
Un peu ennuyeux | Plutôt amusant
**En savoir plus : [Structure JSON](/docs/json/)** | **En savoir plus : [Docs Caddyfile](/docs/caddyfile)**

Vous devrez décider ce qui convient le mieux à votre situation.

Il est important de noter que le JSON et le Caddyfile (ainsi que [tout autre adaptateur de configuration supporté](/docs/config-adapters)) peuvent être utilisés avec l'[API de Caddy](/docs/api). Cependant, vous bénéficiez de toute la gamme des fonctionnalités de Caddy et de l'API si vous utilisez JSON. Si vous utilisez un adaptateur de configuration, la seule façon de charger ou de modifier la configuration via l'API est le [point d'accès /load](/docs/api#post-load).

<aside class="complete">Comparer le JSON et le Caddyfile</aside>


<a id="api-vs-config-files"></a>
## API vs Fichiers de configuration

<aside class="tip">

Sous le capot, même les fichiers de configuration passent par les points d'accès de l'API de Caddy ; la commande `caddy` ne fait qu'envelopper ces appels API pour vous.

</aside>


Vous devrez également décider si votre flux de travail est basé sur l'API ou sur la ligne de commande (CLI). (Vous *pouvez* utiliser à la fois l'API et les fichiers de configuration sur le même serveur, mais nous ne le recommandons pas : il est préférable d'avoir une seule source de vérité.)

API | Fichiers de configuration
----|-------------
Changements de config via requêtes HTTP | Changements de config via commandes shell
Facile à mettre à l'échelle | Difficile à mettre à l'échelle
Difficile à gérer à la main | Facile à gérer à la main
Vraiment amusant | Également amusant
**En savoir plus : [Tutoriel API](/docs/api-tutorial)** | **En savoir plus : [Tutoriel Caddyfile](/docs/caddyfile-tutorial)**

<aside class="tip">
	Gérer manuellement la configuration d'un serveur via l'API est tout à fait faisable avec les bons outils, par exemple : n'importe quel client REST.
</aside>

Le choix entre l'API ou le fichier de configuration est indépendant de l'utilisation des adaptateurs de configuration : vous pouvez utiliser JSON tout en le stockant dans un fichier et utiliser l'interface en ligne de commande ; inversement, vous pouvez aussi utiliser le Caddyfile avec l'API.

Mais la plupart des gens utiliseront les combinaisons JSON+API ou Caddyfile+CLI.

Comme vous pouvez le voir, Caddy est adapté à une grande variété de cas d'utilisation et de déploiements !

<aside class="complete">Comparer l'API et les fichiers de configuration</aside>



<a id="start-stop-run"></a>
## Démarrer, arrêter, exécuter

Puisque Caddy est un serveur, il fonctionne indéfiniment. Cela signifie que votre terminal ne sera pas libéré après avoir exécuté `caddy run` tant que le processus n'est pas terminé (généralement avec <kbd>Ctrl</kbd>+<kbd>C</kbd>).

Bien que `caddy run` soit le plus courant et généralement recommandé (surtout lors de la création d'un service système !), vous pouvez alternativement utiliser `caddy start` pour démarrer Caddy et le laisser s'exécuter en arrière-plan :

<pre><code class="cmd bash">caddy start</code></pre>

Cela vous permettra d'utiliser à nouveau votre terminal, ce qui est pratique dans certains environnements interactifs sans écran (headless).

Vous devrez alors arrêter le processus vous-même, car <kbd>Ctrl</kbd>+<kbd>C</kbd> ne l'arrêtera pas pour vous :

<pre><code class="cmd bash">caddy stop</code></pre>

Ou utilisez [le point d'accès /stop](/docs/api#post-stop) de l'API.

<aside class="complete">Exécuter en arrière-plan</aside>


<a id="reloading-config"></a>
## Rechargement de la configuration

Votre serveur peut effectuer des rechargements/changements de configuration sans interruption de service.

Tous les [points d'accès de l'API](/docs/api) qui chargent ou modifient la configuration sont gracieux et sans temps d'arrêt.

Cependant, lors de l'utilisation de la ligne de commande, il peut être tentant d'utiliser <kbd>Ctrl</kbd>+<kbd>C</kbd> pour arrêter votre serveur, puis de le redémarrer pour prendre en compte la nouvelle configuration. Ne faites pas cela : arrêter et redémarrer le serveur est indépendant des changements de configuration et entraînera une interruption de service.

<aside class="tip">
	Arrêter votre serveur provoquera une interruption de service.
</aside>

Utilisez plutôt la commande [`caddy reload`](/docs/command-line#caddy-reload) pour un changement de configuration gracieux :

<pre><code class="cmd bash">caddy reload</code></pre>

En réalité, cela utilise simplement l'API sous le capot. Cela chargera et, si nécessaire, adaptera votre fichier de configuration en JSON, puis remplacera gracieusement la configuration active sans interruption.

S'il y a des erreurs lors du chargement de la nouvelle configuration, Caddy revient à la dernière configuration fonctionnelle.

<aside class="tip">
	Techniquement, la nouvelle configuration est démarrée avant que l'ancienne ne soit arrêtée, donc pendant un court instant, les deux configurations fonctionnent en même temps ! Si la nouvelle échoue, elle s'arrête avec une erreur, tandis que l'ancienne n'est tout simplement pas arrêtée.
</aside>

<aside class="complete">Rechargement de configuration sans interruption</aside>
