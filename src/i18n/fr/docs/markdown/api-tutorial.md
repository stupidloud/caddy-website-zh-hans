---
title: "Tutoriel API"
---

# Tutoriel API

Ce tutoriel vous montrera comment utiliser l'[API d'administration](/docs/api) de Caddy, qui permet d'automatiser sa configuration de manière programmable.

**Objectifs :**
- 🔲 Lancer le démon (daemon)
- 🔲 Donner une configuration à Caddy
- 🔲 Tester la configuration
- 🔲 Remplacer la configuration active
- 🔲 Parcourir la configuration
- 🔲 Utiliser les balises `@id`

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- Expérience de base avec le JSON
- `caddy` et `curl` présents dans votre PATH

---

Pour démarrer le démon Caddy, utilisez la sous-commande `run` :

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Lancer le démon</aside>

Cela bloque le terminal indéfiniment, mais que se passe-t-il ? Pour l'instant... rien. Par défaut, la configuration de Caddy est vide. Nous pouvons le vérifier en utilisant l'[API d'administration](/docs/api) dans un autre terminal :

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Nous pouvons rendre Caddy utile en lui donnant une configuration. Une manière de procéder consiste à faire une requête POST sur le point d'accès [/load](/docs/api#post-load). Comme pour toute requête HTTP, il existe de nombreuses façons de le faire, mais dans ce tutoriel, nous utiliserons `curl`.

## Votre première configuration

Pour préparer notre requête, nous devons créer une configuration. La configuration de Caddy est simplement un [document JSON](/docs/json/) (ou [tout ce qui se convertit en JSON](/docs/config-adapters)).

<aside class="tip">
	L'utilisation de fichiers de configuration n'est pas obligatoire. L'API de configuration peut toujours être utilisée sans fichiers, ce qui est pratique pour l'automatisation. Ce tutoriel utilise un fichier car il est plus commode pour l'édition manuelle.
</aside>

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

Ensuite, envoyez-le :

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Assurez-vous de ne pas oublier le @ devant le nom de votre fichier ; cela indique à curl que vous envoyez un fichier.
</aside>

<aside class="complete">Donner une configuration à Caddy</aside>

Nous pouvons vérifier que Caddy a appliqué notre nouvelle configuration avec une autre requête GET :

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Testez que cela fonctionne en vous rendant sur [localhost:2015](http://localhost:2015) dans votre navigateur ou utilisez `curl` :

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">Tester la configuration</aside>

Si vous voyez _Hello, world!_, alors félicitations — ça fonctionne ! Il est toujours bon de s'assurer que votre configuration fonctionne comme prévu, surtout avant de la déployer en production.

Changeons notre message de bienvenue de "Hello world!" en quelque chose d'un peu plus motivant : "Je peux faire des choses difficiles." Faites ce changement dans votre fichier de configuration, de sorte que l'objet handler ressemble maintenant à ceci :

```json
{
	"handler": "static_response",
	"body": "Je peux faire des choses difficiles."
}
```

Enregistrez le fichier, puis mettez à jour la configuration active de Caddy en exécutant à nouveau la même requête POST :

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Remplacer la configuration active</aside>

Pour faire bonne mesure, vérifiez que la configuration a été mise à jour :

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Testez en rafraîchissant la page dans votre navigateur (ou en exécutant à nouveau `curl`), et vous verrez un message inspirant !


## Parcours de la configuration

Au lieu d'envoyer l'intégralité du fichier de configuration pour un petit changement, utilisons une fonctionnalité puissante de l'API de Caddy pour effectuer la modification sans jamais toucher à notre fichier.

<aside class="tip">
	Faire de petits changements sur des serveurs de production en remplaçant toute la configuration comme nous l'avons fait plus haut peut être dangereux ; c'est comme avoir un accès root sur un système de fichiers. L'API de Caddy vous permet de limiter la portée de vos modifications pour garantir que d'autres parties de votre configuration ne soient pas modifiées accidentellement.
</aside>

En utilisant le chemin de l'URI de la requête, nous pouvons naviguer dans la structure de la configuration et mettre à jour uniquement la chaîne du message (veillez à faire défiler vers la droite si le texte est coupé) :

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Travaillez plus intelligemment, pas plus dur."'
</code></pre>


<aside class="tip">

Chaque fois que vous modifiez la configuration via l'API, Caddy conserve une copie de la nouvelle configuration pour que vous puissiez la [**reprendre (--resume)** plus tard](/docs/command-line#caddy-run) !

</aside>


Vous pouvez vérifier que cela a fonctionné avec une requête GET similaire, par exemple :

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Vous devriez voir :

```json
[{"handle":[{"body":"Travaillez plus intelligemment, pas plus dur.","handler":"static_response"}]}]
```


<aside class="tip">

Vous pouvez utiliser la [commande `jq` <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) pour embellir la sortie JSON : **`curl ... | jq`**

</aside>


<aside class="complete">Parcourir la configuration</aside>

**Note importante :** Cela devrait être évident, mais une fois que vous utilisez l'API pour effectuer un changement qui n'est pas dans votre fichier de configuration d'origine, celui-ci devient obsolète. Il existe plusieurs façons de gérer cela :

- Utilisez le drapeau `--resume` de la commande [caddy run](/docs/command-line#caddy-run) pour utiliser la dernière configuration active.
- Ne mélangez pas l'utilisation de fichiers de configuration avec des modifications via l'API ; gardez une seule source de vérité.
- [Exportez la nouvelle configuration de Caddy](/docs/api#get-configpath) avec une requête GET ultérieure (moins recommandé que les deux premières options).



## Utilisation de `@id` en JSON

Le parcours de configuration est certainement utile, mais les chemins sont un peu longs, ne trouvez-vous pas ?

Nous pouvons donner à notre objet handler une [balise `@id`](/docs/api#using-id-in-json) pour le rendre plus facile d'accès :

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Cela ajoute une propriété à notre objet handler : `"@id": "msg"`, il ressemble donc maintenant à ceci :

```json
{
	"@id": "msg",
	"body": "Travaillez plus intelligemment, pas plus dur.",
	"handler": "static_response"
}
```


<aside class="tip">

Les balises **@id** peuvent être placées dans n'importe quel objet et peuvent avoir n'importe quelle valeur primitive (généralement une chaîne de caractères). [En savoir plus](/docs/api#using-id-in-json)

</aside>


Nous pouvons alors y accéder directement :

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

Et maintenant nous pouvons changer le message avec un chemin plus court :

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Certains raccourcis sont bons."'
</code></pre>

Et vérifiez à nouveau :

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">Utiliser les balises <code>@id</code></aside>
