---
title: Tutoriel Caddyfile
---

# Tutoriel Caddyfile

Ce tutoriel vous enseignera les bases du [Caddyfile HTTP](/docs/caddyfile) afin que vous puissiez produire rapidement et facilement des configurations de sites fonctionnelles et élégantes.

**Objectifs :**
- 🔲 Premier site
- 🔲 Serveur de fichiers statiques
- 🔲 Modèles (Templates)
- 🔲 Compression
- 🔲 Sites multiples
- 🔲 Sélecteurs (Matchers)
- 🔲 Variables d'environnement
- 🔲 Commentaires

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- Compétences de base en édition de texte
- `caddy` présent dans votre PATH

---

Créez un nouveau fichier texte nommé `Caddyfile` (sans extension).

La première chose à saisir est l'[adresse](/docs/caddyfile/concepts#addresses) de votre site :

```caddy
localhost
```

<aside class="tip">

Si les ports HTTP et HTTPS (80 et 443 respectivement) sont des ports privilégiés sur votre système d'exploitation, vous devrez soit lancer Caddy avec des privilèges élevés, soit utiliser un port plus élevé. Pour utiliser un port plus élevé, changez simplement l'adresse en quelque chose comme `localhost:2015` et modifiez le port HTTP à l'aide de l'option Caddyfile [http_port](/docs/caddyfile/options).

</aside>


Ensuite, appuyez sur Entrée et saisissez ce que vous voulez que le serveur fasse. Pour ce tutoriel, faites en sorte que votre Caddyfile ressemble à ceci :

```caddy
localhost

respond "Hello, world!"
```

Enregistrez le fichier et lancez Caddy (comme il s'agit d'un tutoriel, nous utiliserons le drapeau `--watch` pour que les modifications de notre Caddyfile soient appliquées automatiquement) :

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Si vous rencontrez des erreurs de permissions, essayez d'utiliser un port plus élevé dans votre adresse (comme `localhost:2015`) et [changez le port HTTP](/docs/caddyfile/options), ou lancez Caddy avec des privilèges élevés.

</aside>


La première fois, votre mot de passe vous sera demandé. C'est pour que Caddy puisse servir votre site via HTTPS.

<aside class="tip">

Caddy sert tous les sites via HTTPS par défaut tant qu'un hôte ou une IP fait partie de l'adresse du site. Le [HTTPS automatique](/docs/automatic-https) peut être désactivé en préfixant explicitement l'adresse par `http://`.

</aside>


<aside class="complete">Premier site</aside>

Ouvrez [localhost](https://localhost) dans votre navigateur et admirez votre serveur web en action, avec HTTPS inclus !

<aside class="tip">
	Il se peut que vous deviez redémarrer votre navigateur si vous obtenez une erreur de certificat la première fois.
</aside>

Ce n'est pas particulièrement passionnant, alors transformons notre réponse statique en un [serveur de fichiers](/docs/caddyfile/directives/file_server) avec l'exploration de répertoires activée :

```caddy
localhost

file_server browse
```

Enregistrez votre Caddyfile, puis rafraîchissez l'onglet de votre navigateur. Vous devriez voir soit une liste de fichiers, soit une page HTML s'il y a un fichier index dans le répertoire courant.

<aside class="complete">Serveur de fichiers statiques</aside>

## Ajout de fonctionnalités

Faisons quelque chose d'intéressant avec notre serveur de fichiers : servir une page utilisant des modèles. Créez un nouveau fichier et collez-y ceci :

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Tutoriel Caddy</title>
	</head>
	<body>
		Page chargée à : {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Enregistrez-le sous le nom `caddy.html` dans le répertoire courant et chargez-le dans votre navigateur : [https://localhost/caddy.html](https://localhost/caddy.html)

Le résultat est :

```
Page chargée à : {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Attendez une minute. Nous devrions voir la date du jour. Pourquoi cela n'a-t-il pas fonctionné ? C'est parce que le serveur n'a pas encore été configuré pour évaluer les modèles ! Facile à corriger, ajoutez simplement une ligne au Caddyfile pour qu'il ressemble à ceci :

```caddy
localhost

templates
file_server browse
```

Enregistrez, puis rechargez l'onglet du navigateur. Vous devriez voir :

```
Page chargée à : {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Avec le [module de modèles](/docs/modules/http.handlers.templates) de Caddy, vous pouvez faire beaucoup de choses utiles avec des fichiers statiques, comme inclure d'autres fichiers HTML, effectuer des sous-requêtes, définir des en-têtes de réponse, manipuler des structures de données, et bien plus encore !

<aside class="complete">Modèles</aside>

C'est une bonne pratique de compresser les réponses avec un algorithme de compression rapide et moderne. Activons le support de Gzip et Zstandard en utilisant la directive [`encode`](/docs/caddyfile/directives/encode) :

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Compression</aside>

C'est le processus de base pour mettre en place un site semi-avancé et prêt pour la production !

Lorsque vous êtes prêt à activer le [HTTPS automatique](/docs/automatic-https), remplacez simplement l'adresse de votre site (`localhost` dans notre tutoriel) par votre nom de domaine. Consultez notre [guide de démarrage rapide HTTPS](/docs/quick-starts/https) pour plus d'informations.

## Sites multiples

Avec notre Caddyfile actuel, nous ne pouvons définir qu'un seul site ! Seule la première ligne peut contenir la ou les adresses du site, et tout le reste du fichier doit être constitué de directives pour ce site.

Mais il est facile de faire en sorte que nous puissions ajouter d'autres sites !

Notre Caddyfile actuel :

```caddy
localhost

encode
templates
file_server browse
```

est équivalent à celui-ci :

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

sauf que le second nous permet d'ajouter d'autres sites.

En enveloppant notre bloc de site dans des accolades `{ }`, nous sommes capables de définir plusieurs sites différents dans le même Caddyfile.

Par exemple :

```caddy
:8080 {
	respond "Je suis le port 8080"
}

:8081 {
	respond "Je suis le port 8081"
}
```

Lorsque l'on enveloppe des blocs de site dans des accolades, seules les [adresses](/docs/caddyfile/concepts#addresses) apparaissent à l'extérieur des accolades et seules les [directives](/docs/caddyfile/directives) apparaissent à l'intérieur.

Pour plusieurs sites partageant la même configuration, vous pouvez ajouter d'autres adresses, par exemple :

```caddy
:8080, :8081 {
	...
}
```

Vous pouvez ensuite définir autant de sites différents que vous le souhaitez, tant que chaque adresse est unique.

<aside class="complete">Sites multiples</aside>


## Sélecteurs (Matchers)

Nous pouvons vouloir appliquer certaines directives uniquement à certaines requêtes. Par exemple, supposons que nous voulions avoir à la fois un serveur de fichiers et un proxy inverse, mais nous ne pouvons évidemment pas faire les deux sur chaque requête ! Soit le serveur de fichiers écrira une réponse avec un fichier statique, soit le proxy inverse transmettra la requête à un backend et renverra sa réponse.

Cette configuration ne fonctionnera pas comme nous le souhaitons (`reverse_proxy` aura la priorité en raison de l'[ordre des directives](/docs/caddyfile/directives#directive-order)) :

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

En pratique, nous pourrions vouloir utiliser le proxy inverse uniquement pour les requêtes API, c'est-à-dire les requêtes ayant un chemin de base `/api/`. C'est facile à faire en ajoutant un [jeton de sélecteur](/docs/caddyfile/matchers#syntax) :

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

Voilà ; maintenant le proxy inverse sera prioritaire pour toutes les requêtes commençant par `/api/`.

La partie `/api/*` que nous venons d'ajouter s'appelle un **jeton de sélecteur**. Vous pouvez savoir qu'il s'agit d'un jeton de sélecteur car il commence par un slash `/` et il apparaît juste après la directive (mais vous pouvez toujours vérifier dans la [documentation de la directive](/docs/caddyfile/directives) pour en être sûr).

Les sélecteurs sont vraiment puissants. Vous pouvez déclarer des sélecteurs nommés et les utiliser sous la forme `@nom` pour effectuer des correspondances sur bien plus que le simple chemin de la requête ! Prenez un moment pour [en savoir plus sur les sélecteurs](/docs/caddyfile/matchers) avant de continuer !

<aside class="complete">Sélecteurs</aside>

## Variables d'environnement

L'adaptateur Caddyfile permet de substituer des [variables d'environnement](/docs/caddyfile/concepts#environment-variables) avant que le Caddyfile ne soit analysé.

Tout d'abord, définissez une variable d'environnement (dans le même shell qui lance Caddy) :

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Ensuite, vous pouvez l'utiliser comme ceci dans le Caddyfile :

```caddy
{$SITE_ADDRESS}

file_server
```

Avant que le Caddyfile ne soit analysé, il sera étendu en :

```caddy
localhost:9055

file_server
```

Vous pouvez utiliser des variables d'environnement n'importe où dans le Caddyfile, pour n'importe quel nombre de jetons.

<aside class="complete">Variables d'environnement</aside>


## Commentaires

Une dernière chose qui vous sera très utile : si vous voulez faire une remarque ou noter quoi que ce soit dans votre Caddyfile, vous pouvez utiliser des commentaires, commençant par `#` :

```caddy
# ceci commence un commentaire
```

<aside class="complete">Commentaires</aside>

## Lectures complémentaires

- [Concepts du Caddyfile](/docs/caddyfile/concepts)
- [Directives](/docs/caddyfile/directives)
- [Modèles courants](/docs/caddyfile/patterns)
