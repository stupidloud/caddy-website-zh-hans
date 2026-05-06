---
title: Démarrage rapide du HTTPS
---

# Démarrage rapide du HTTPS

Ce guide vous montrera comment mettre en place un [HTTPS entièrement géré](/docs/automatic-https) en un rien de temps.

<aside class="tip">
	Caddy utilise le HTTPS par défaut pour tous les sites, tant qu'un nom d'hôte est fourni dans la configuration. Ce tutoriel suppose que vous voulez mettre en ligne un site avec un certificat publiquement approuvé (donc pas "localhost"), nous utiliserons donc un nom de domaine public et des ports externes.
</aside>

**Prérequis :**
- Compétences de base en terminal / ligne de commande
- Compréhension de base du DNS
- Un nom de domaine public enregistré
- Accès externe aux ports 80 et 443
- `caddy` et `curl` présents dans votre PATH

---

Dans ce tutoriel, remplacez `exemple.com` par votre véritable nom de domaine.

Configurez les enregistrements A/AAAA de votre domaine pour qu'ils pointent vers votre serveur. Vous pouvez le faire en vous connectant à l'interface de votre fournisseur DNS.

Avant de continuer, vérifiez que les enregistrements sont corrects avec une requête faisant autorité. Remplacez `exemple.com` par votre nom de domaine (et si vous utilisez l'IPv6, remplacez `type=A` par `type=AAAA`) :

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=exemple.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

Assurez-vous également que votre serveur est accessible de l'extérieur sur les ports 80 et 443 depuis une interface publique.

<aside class="tip">
	Si vous êtes sur un réseau domestique ou restreint, vous devrez peut-être rediriger les ports ou ajuster les paramètres de votre pare-feu.
</aside>

Tout ce qu'il reste à faire est de lancer Caddy avec votre nom de domaine dans la configuration. Il existe plusieurs façons d'y parvenir.

## Caddyfile

C'est la manière la plus courante d'obtenir du HTTPS.

Créez un fichier nommé `Caddyfile` (sans extension) dont la première ligne est votre nom de domaine, par exemple :

```caddy
exemple.com

respond "Hello, privacy!"
```

Puis, depuis le même répertoire, lancez :

<pre><code class="cmd bash">caddy run</code></pre>

Vous verrez Caddy provisionner un certificat TLS et servir votre site en HTTPS. Cela a été possible car l'adresse de votre site dans le Caddyfile contenait un nom de domaine.


## La commande `file-server`

Si vous avez seulement besoin de servir des fichiers statiques en HTTPS, lancez cette commande (en remplaçant le nom de domaine) :

<pre><code class="cmd bash">caddy file-server --domain exemple.com</code></pre>

Vous verrez Caddy provisionner un certificat TLS et servir votre site en HTTPS.


## La commande `reverse-proxy`

Si vous avez seulement besoin d'un proxy inverse simple en HTTPS (comme terminaison TLS), lancez cette commande (en remplaçant le nom de domaine et l'adresse réelle de votre backend) :

<pre><code class="cmd bash">caddy reverse-proxy --from exemple.com --to localhost:9000</code></pre>

Vous verrez Caddy provisionner un certificat TLS et servir votre site en HTTPS.


## Configuration JSON

En règle générale, tout [sélecteur d'hôte (host matcher)](/docs/json/apps/http/servers/routes/match/host/) déclenchera le HTTPS automatique.

Ainsi, une configuration JSON telle que la suivante activera le [HTTPS automatique](/docs/automatic-https) prêt pour la production :

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["exemple.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
