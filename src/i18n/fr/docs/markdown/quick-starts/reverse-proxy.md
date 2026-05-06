---
title: Démarrage rapide du proxy inverse
---

# Démarrage rapide du proxy inverse

Ce guide vous montrera comment mettre en place rapidement un proxy inverse prêt pour la production, avec ou sans HTTPS.

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- `caddy` présent dans votre PATH
- Un processus backend en cours d'exécution vers lequel rediriger le trafic

---

Ce tutoriel suppose qu'un service HTTP backend tourne sur `127.0.0.1:9000`. Ces commandes sont pour Linux, mais les mêmes principes s'appliquent aux autres systèmes d'exploitation.

Vous pouvez lancer un proxy inverse simple sans fichier de configuration, ou utiliser un fichier pour plus de flexibilité et de contrôle.


## Ligne de commande

Pour lancer un proxy HTTP en texte clair du port 2080 vers le port 9000 de votre machine :

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Puis testez-le :

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

La [commande `reverse-proxy`](/docs/command-line#reverse-proxy) est destinée à mettre en place des proxys inverses rapidement et facilement. (Vous pouvez l'utiliser en production si vos besoins sont simples.)

## Caddyfile

Dans le répertoire de travail actuel, créez un fichier nommé `Caddyfile` avec ce contenu :

```caddy
:2080

reverse_proxy :9000
```

Ce fichier de configuration est approximativement l'équivalent de la commande `caddy reverse-proxy` ci-dessus.

Ensuite, depuis le même répertoire, lancez :

<pre><code class="cmd bash">caddy run</code></pre>

Puis testez votre proxy :

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Si vous modifiez le Caddyfile, n'oubliez pas de [recharger](/docs/command-line#caddy-reload) Caddy.

Ceci était un exemple simple. Vous pouvez faire bien plus avec la [directive `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

## HTTPS du client vers le proxy

Caddy servira votre proxy via [HTTPS automatiquement et par défaut](/docs/automatic-https) s'il connaît le nom d'hôte (nom de domaine). La commande `caddy reverse-proxy` utilisera `localhost` par défaut si vous omettez le drapeau `--from`, ou vous pouvez remplacer la première ligne de votre Caddyfile par le nom de domaine du proxy.

- Si vous utilisez `localhost` ou tout domaine se terminant par `.localhost`, Caddy utilisera un certificat auto-signé à renouvellement automatique. La première fois, votre mot de passe pourrait vous être demandé car Caddy tente d'installer le certificat racine de sa CA dans le magasin de confiance de votre système.
- Si vous utilisez n'importe quel autre nom de domaine, Caddy tentera d'obtenir un certificat publiquement approuvé ; assurez-vous que vos enregistrements DNS pointent vers votre machine et que les ports 80 et 443 sont ouverts au public et dirigés vers Caddy.

Si vous ne spécifiez pas de port, Caddy utilise le port 443 par défaut pour le HTTPS. Dans ce cas, vous aurez également besoin de la permission de vous lier à des ports bas. Quelques façons d'y parvenir sur Linux :

- Lancer en tant que root (ex: `sudo -E`).
- Ou lancer `sudo setcap cap_net_bind_service=+ep $(which caddy)` pour donner à Caddy cette capacité spécifique.

Voici la commande `caddy reverse-proxy` la plus basique pour obtenir du HTTPS :

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Puis testez-la :

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Vous pouvez personnaliser le nom d'hôte avec le drapeau `--from` :

<pre><code class="cmd bash">caddy reverse-proxy --from exemple.com --to :9000</code></pre>

Si vous n'avez pas la permission de vous lier aux ports bas, vous pouvez proxifier depuis un port plus élevé :

<pre><code class="cmd bash">caddy reverse-proxy --from exemple.com:8443 --to :9000</code></pre>

Si vous utilisez un Caddyfile, changez simplement la première ligne par votre nom de domaine, par exemple :

```caddy
exemple.com

reverse_proxy :9000
```

## HTTPS du proxy vers le backend

Caddy peut également proxifier en utilisant le HTTPS entre lui-même et le backend si celui-ci supporte le TLS. Utilisez simplement `https://` dans l'adresse de votre backend :

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Ceci nécessite que le certificat du backend soit approuvé par le système sur lequel Caddy tourne. (Caddy n'approuve pas les certificats auto-signés à moins d'être explicitement configuré pour le faire.)

Bien sûr, vous pouvez aussi faire du HTTPS des deux côtés :

<pre><code class="cmd bash">caddy reverse-proxy --from exemple.com --to https://exemple.com:9000</code></pre>

Ceci sert du HTTPS du client vers le proxy, et du proxy vers le backend.

Si le nom d'hôte vers lequel vous proxifiez est différent de celui depuis lequel vous proxifiez, vous devrez utiliser le drapeau `--change-host-header` :

<pre><code class="cmd bash">caddy reverse-proxy \
	--from exemple.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

Par défaut, Caddy transmet tous les en-têtes HTTP sans les modifier, incluant `Host`, et Caddy déduit le ServerName TLS de l'en-tête Host. Le drapeau `--change-host-header` réinitialise l'en-tête Host à celui du backend afin que l'échange TLS puisse se terminer avec succès. Dans l'exemple ci-dessus, il serait changé de `exemple.com` vers `localhost:9000` (et `localhost` serait utilisé lors de l'échange TLS).
