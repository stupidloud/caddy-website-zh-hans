---
title: Démarrage rapide des fichiers statiques
---

# Démarrage rapide des fichiers statiques

Ce guide vous montrera comment mettre en place rapidement un serveur de fichiers statiques prêt pour la production.

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- `caddy` présent dans votre PATH
- Un dossier contenant votre site web

---

Il existe deux manières simples de lancer rapidement un serveur de fichiers.

## Ligne de commande

Dans votre terminal, rendez-vous dans le répertoire racine de votre site et lancez :

<pre><code class="cmd bash">caddy file-server</code></pre>

Si vous obtenez une erreur de permissions, cela signifie probablement que votre système d'exploitation ne vous autorise pas à vous lier à des ports bas — utilisez alors un port élevé :

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Ouvrez ensuite [localhost](http://localhost) (ou [localhost:2015](http://localhost:2015)) dans votre navigateur pour voir votre site !

Si vous n'avez pas de fichier index mais que vous voulez afficher une liste des fichiers, utilisez l'option `--browse` :

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

Vous pouvez utiliser un autre dossier comme racine du site :

<pre><code class="cmd bash">caddy file-server --root ~/monsite</code></pre>



## Caddyfile

À la racine de votre site, créez un fichier nommé `Caddyfile` avec ce contenu :

```caddy
localhost

file_server
```

Si vous n'avez pas la permission de vous lier à des ports bas, remplacez `localhost` par `localhost:2015` (ou un autre port élevé).

Ensuite, depuis le même répertoire, lancez :

<pre><code class="cmd bash">caddy run</code></pre>

Vous pouvez alors charger [localhost](https://localhost) (ou l'adresse définie dans votre configuration) pour voir votre site !

La [directive `file_server`](/docs/caddyfile/directives/file_server) possède davantage d'options pour personnaliser votre site. N'oubliez pas de [recharger](/docs/command-line#caddy-reload) Caddy (ou de l'arrêter et le relancer) lorsque vous modifiez le Caddyfile !

Si vous n'avez pas de fichier index mais que vous voulez afficher une liste des fichiers, utilisez l'argument `browse` :

```caddy
localhost

file_server browse
```

Vous pouvez également utiliser un autre dossier comme racine du site :

```caddy
localhost

root /var/www/monsite
file_server
```
