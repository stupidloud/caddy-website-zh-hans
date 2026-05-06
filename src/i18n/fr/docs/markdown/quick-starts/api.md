---
title: Démarrage rapide de l'API
---

# Démarrage rapide de l'API

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- `caddy` et `curl` présents dans votre PATH

---

Commencez par lancer Caddy :

<pre><code class="cmd bash">caddy start</code></pre>

Caddy tourne actuellement à vide (avec une configuration vierge). Donnez-lui une configuration simple avec `curl` :

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
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
EOF</code></pre>

Saisir un corps de requête POST avec [Heredoc](https://fr.wikipedia.org/wiki/Document_en_ligne) peut être fastidieux. Si vous préférez utiliser des fichiers, enregistrez le JSON dans un fichier nommé `caddy.json` puis utilisez cette commande à la place :

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Maintenant, chargez [localhost:2015](http://localhost:2015) dans votre navigateur ou utilisez `curl` :

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Nous pouvons également définir plusieurs sites sur différentes interfaces avec ce JSON :

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Mettez à jour votre fichier JSON puis effectuez à nouveau la requête API.

Testez votre nouveau point d'accès "goodbye" [dans votre navigateur](http://localhost:2016) ou avec `curl` pour vérifier qu'il fonctionne :

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Quand vous avez fini avec Caddy, n'oubliez pas de l'arrêter :

<pre><code class="cmd bash">caddy stop</code></pre>

Il y a bien plus à faire avec l'API, notamment l'exportation de configuration et les modifications granulaires (plutôt que de tout mettre à jour). Consultez le [tutoriel API complet](/docs/api-tutorial) pour apprendre comment !

## Lectures complémentaires

- [Tutoriel API complet](/docs/api-tutorial)
- [Documentation de l'API](/docs/api)
