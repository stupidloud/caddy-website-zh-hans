---
title: Démarrage rapide du Caddyfile
---

# Démarrage rapide du Caddyfile

Créez un nouveau fichier texte nommé `Caddyfile` (sans extension).

La première chose à saisir dans un Caddyfile est l'adresse de votre site :

```caddy
localhost
```

<aside class="tip">

Si les ports HTTP et HTTPS (80 et 443 respectivement) sont des ports privilégiés sur votre système d'exploitation, vous devrez soit lancer Caddy avec des privilèges élevés, soit utiliser des ports plus élevés. Pour obtenir les permissions, lancez Caddy en tant que root avec `sudo -E` ou utilisez `sudo setcap cap_net_bind_service=+ep $(which caddy)`. Alternativement, pour utiliser des ports plus élevés, changez simplement l'adresse en quelque chose comme `localhost:2080` et modifiez le port HTTP à l'aide de l'option Caddyfile [`http_port`](/docs/caddyfile/options).

</aside>

Ensuite, appuyez sur Entrée et saisissez ce que vous voulez que le serveur fasse, pour obtenir ceci :

```caddy
localhost

respond "Hello, world!"
```

Enregistrez le fichier et lancez Caddy depuis le dossier qui contient votre Caddyfile :

<pre><code class="cmd bash">caddy start</code></pre>

Votre mot de passe vous sera probablement demandé, car Caddy sert tous les sites — même locaux — via HTTPS par défaut. (La demande de mot de passe ne devrait se produire que la première fois !)

<aside class="tip">

Pour le HTTPS local, Caddy génère automatiquement des certificats et des clés privées uniques pour vous. Le certificat racine est ajouté au magasin de confiance de votre système, c'est pourquoi la saisie du mot de passe est nécessaire. Cela vous permet de développer localement en HTTPS sans erreurs de certificat.

</aside>

(Si vous obtenez des erreurs de permissions, vous devrez peut-être lancer Caddy avec des privilèges élevés ou choisir un port supérieur à 1023.)

Ouvrez [localhost](http://localhost) dans votre navigateur ou utilisez `curl` :

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

Vous pouvez définir plusieurs sites dans un Caddyfile en les enveloppant dans des accolades `{ }`. Modifiez votre Caddyfile ainsi :

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

Vous pouvez donner à Caddy la configuration mise à jour de deux manières, soit via l'API directement :

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

soit avec la commande reload, qui effectue la même requête API pour vous :

<pre><code class="cmd bash">caddy reload</code></pre>

Testez votre nouveau point d'accès "goodbye" [dans votre navigateur](https://localhost:2016) ou avec `curl` pour vérifier qu'il fonctionne :

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Quand vous avez fini avec Caddy, n'oubliez pas de l'arrêter :

<pre><code class="cmd bash">caddy stop</code></pre>

## Lectures complémentaires

- [Concepts du Caddyfile](/docs/caddyfile/concepts)
- [Directives](/docs/caddyfile/directives)
- [Modèles courants](/docs/caddyfile/patterns)
