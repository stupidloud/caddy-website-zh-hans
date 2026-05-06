---
title: Démarrage rapide Railway
---

# Démarrage rapide Railway

Déployer Caddy sur Railway est un moyen simple et sans tracas de déployer un build Caddy personnalisé avec des plugins.

**Prérequis :**
- Un compte [Railway](https://railway.com) gratuit

## Déployer Caddy sur Railway

Rendez-vous sur notre [page de téléchargement](/download) et sélectionnez les plugins dont vous avez besoin, puis cliquez sur le bouton violet "Deploy on Railway" en haut de la page.

<details>
	<summary>Ou, configurez le modèle manuellement</summary>

Alternativement, si vous préférez configurer le modèle Railway vous-même, voici comment faire.

Allez sur le modèle sur Railway :

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

et ajoutez les plugins nécessaires en cliquant sur "Configure" :

![Écran de déploiement](/resources/images/railway/deploy-screen.png)

Puis collez les plugins dans la variable `CADDY_PLUGINS`, séparés par des espaces :

![Ajouter des plugins](/resources/images/railway/deploy-config.png)

</details>

Cliquez sur Deploy. Une fois le déploiement terminé, vous pouvez le tester en cliquant sur le lien ici :

![Visiter votre déploiement](/resources/images/railway/prod-link.png)

Vous devriez voir une page de bienvenue indiquant que votre nouveau serveur fonctionne !

Ensuite, vous pouvez personnaliser votre déploiement pour servir votre propre site ou faire office de proxy vers un autre service Railway.

## Personnaliser le déploiement

Pour servir votre propre site web, ou pour changer la configuration, il suffit d'"éjecter" [notre modèle](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) vers votre propre dépôt :

![Éjecter le modèle](/resources/images/railway/eject.png)

Depuis votre propre dépôt, vous pouvez :

- Placer votre propre site dans le dossier `www`.
- Modifier la configuration de Caddy, qui se trouve dans le [Caddyfile](/docs/caddyfile).

Commitez simplement vos changements et pushez-les, puis vous pourrez redéployer sur Railway.

Si vous voulez changer les plugins de votre build Caddy, il vous suffit de modifier la variable `CADDY_PLUGINS` et de redéployer :

![Changer les plugins](/resources/images/railway/plugins-variable.png)

## Conseils

Railway gère la terminaison TLS pour vous, vous devez donc écrire votre configuration Caddy comme si elle recevait du trafic proxifié (car c'est le cas). Par conséquent, si vous utilisez des hôtes dans les adresses de site de votre Caddyfile, vous devriez utiliser `auto_https off` dans vos options globales. Avec notre modèle, Caddy n'est pas exposé directement à l'extérieur.


## Variables

Variables d'environnement que vous pouvez définir dans votre projet Railway et que ce modèle peut utiliser :

Nom | Description | Valeur par défaut | Exemple(s)
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | Liste de plugins Caddy séparés par des espaces | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
