---
title: "API"
---

# API

Caddy se configure via un point d'accès (endpoint) d'administration accessible via HTTP à l'aide d'une API [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer). Vous pouvez [configurer ce point d'accès](/docs/json/admin/) dans votre configuration Caddy.

<a id="default-address"></a>
**Adresse par défaut : `localhost:2019`**

L'adresse par défaut peut être modifiée en définissant la variable d'environnement `CADDY_ADMIN`. Certaines méthodes d'installation peuvent la définir différemment. L'adresse spécifiée dans la configuration Caddy a toujours la priorité sur la valeur par défaut.

<aside class="tip">
	Si vous exécutez du code non fiable sur votre serveur (aïe 😬), assurez-vous de protéger votre point d'accès d'administration en isolant les processus, en corrigeant les programmes vulnérables et en configurant le point d'accès pour qu'il se lie à un socket Unix avec des permissions restreintes à la place.
</aside>

La configuration la plus récente sera sauvegardée sur le disque après toute modification (sauf si [désactivé](/docs/json/admin/config/)). Vous pouvez reprendre la dernière configuration fonctionnelle après un redémarrage avec [`caddy run --resume`](/docs/command-line#caddy-run), ce qui garantit la durabilité de la configuration en cas de coupure de courant ou d'événement similaire.

Pour commencer avec l'API, essayez notre [tutoriel API](/docs/api-tutorial) ou, si vous n'avez qu'une minute, notre [guide de démarrage rapide de l'API](/docs/quick-starts/api).

---

- **[POST /load](#post-load)**
  Définit ou remplace la configuration active

- **[POST /stop](#post-stop)**
  Arrête la configuration active et quitte le processus

- **[GET /config/[path]](#get-configpath)**
  Exporte la configuration au chemin nommé

- **[POST /config/[path]](#post-configpath)**
  Définit ou remplace un objet ; ajoute à un tableau
  
- **[PUT /config/[path]](#put-configpath)**
  Crée un nouvel objet ; insère dans un tableau

- **[PATCH /config/[path]](#patch-configpath)**
  Remplace un objet ou un élément de tableau existant

- **[DELETE /config/[path]](#delete-configpath)**
  Supprime la valeur au chemin nommé

- **[Utilisation de `@id` en JSON](#using-id-in-json)**
  Navigue facilement dans la structure de la configuration

- **[Modifications de config concurrentes](#concurrent-config-changes)**
  Évite les collisions lors de modifications non synchronisées de la config

- **[POST /adapt](#post-adapt)**
  Adapte une configuration en JSON sans l'exécuter

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Retourne des informations sur une autorité de certification (CA) d'une [application PKI](/docs/json/apps/pki/) particulière

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Retourne la chaîne de certificats d'une CA d'une [application PKI](/docs/json/apps/pki/) particulière

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Retourne l'état actuel des serveurs d'amont (upstreams) configurés pour le proxy


<a id="post-load"></a>
## POST /load

Définit la configuration de Caddy, en écrasant toute configuration précédente. L'appel bloque jusqu'à ce que le rechargement soit terminé ou échoue. Les changements de configuration sont légers, efficaces et ne provoquent aucune interruption de service. Si la nouvelle configuration échoue pour une raison quelconque, l'ancienne configuration est remise en place sans interruption.

Ce point d'accès prend en charge différents formats de configuration grâce aux adaptateurs de configuration. L'en-tête `Content-Type` de la requête indique le format utilisé dans le corps de la requête. Habituellement, il s'agit de `application/json` qui représente le format natif de Caddy. Pour un autre format, spécifiez le `Content-Type` approprié afin que la valeur après le slash `/` soit le nom de l'adaptateur à utiliser. Par exemple, pour soumettre un Caddyfile, utilisez `text/caddyfile` ; pour du JSON 5, utilisez `application/json5` ; etc.

Si la nouvelle configuration est identique à l'actuelle, aucun rechargement n'aura lieu. Pour forcer un rechargement, définissez `Cache-Control: must-revalidate` dans les en-têtes de la requête.

### Exemples

Définir une nouvelle configuration active :

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Note : le drapeau `-d` de curl supprime les sauts de ligne. Si votre format de configuration y est sensible (comme le Caddyfile), utilisez `--data-binary` à la place :

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="post-stop"></a>
## POST /stop

Arrête proprement le serveur et quitte le processus. Pour arrêter uniquement la configuration en cours sans quitter le processus, utilisez [DELETE /config/](#delete-configpath).

### Exemple

Arrêter le processus :

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


<a id="get-configpath"></a>
## GET /config/[path]

Exporte la configuration actuelle de Caddy au chemin nommé. Retourne un corps JSON.

### Exemples

Exporter toute la configuration et l'afficher joliment :

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

Exporter seulement les adresses d'écoute (listeners) :

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



<a id="post-configpath"></a>
## POST /config/[path]

Modifie la configuration de Caddy au chemin nommé avec le corps JSON de la requête. Si la valeur de destination est un tableau, POST ajoute à la fin ; s'il s'agit d'un objet, il le crée ou le remplace.

Cas particulier : plusieurs éléments peuvent être ajoutés à un tableau si :

1. le chemin se termine par `/...`
2. l'élément du chemin avant `/...` désigne un tableau
3. la charge utile (payload) est un tableau

Dans ce cas, les éléments du tableau de la charge utile seront développés et chacun sera ajouté au tableau de destination. En termes Go, cela aurait le même effet que :

```go
baseSlice = append(baseSlice, newElems...)
```

### Exemples

Ajouter une adresse d'écoute :

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Ajouter plusieurs adresses d'écoute :

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

<a id="put-configpath"></a>
## PUT /config/[path]

Modifie la configuration de Caddy au chemin nommé avec le corps JSON de la requête. Si la valeur de destination est une position (index) dans un tableau, PUT insère l'élément ; s'il s'agit d'un objet, il crée strictement une nouvelle valeur.

### Exemple

Ajouter une adresse d'écoute en première position :

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


<a id="patch-configpath"></a>
## PATCH /config/[path]

Modifie la configuration de Caddy au chemin nommé avec le corps JSON de la requête. PATCH remplace strictement une valeur ou un élément de tableau existant.

### Exemple

Remplacer les adresses d'écoute :

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



<a id="delete-configpath"></a>
## DELETE /config/[path]

Supprime la configuration de Caddy au chemin nommé. DELETE supprime la valeur cible.

### Exemples

Pour décharger toute la configuration actuelle tout en laissant le processus s'exécuter :

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Pour arrêter seulement l'un de vos serveurs HTTP :

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## Utilisation de `@id` en JSON

Vous pouvez intégrer des identifiants (IDs) dans votre document JSON pour faciliter l'accès direct à ces parties du JSON.

Ajoutez simplement un champ nommé `"@id"` à un objet et donnez-lui un nom unique. Par exemple, si vous avez un gestionnaire de proxy inverse auquel vous voulez accéder fréquemment :

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Pour l'utiliser, faites simplement une requête au point d'accès API `/id/` de la même manière que vous le feriez pour le point d'accès `/config/` correspondant, mais sans tout le chemin. L'identifiant vous amène directement dans cette portée de la configuration.

Par exemple, pour accéder aux serveurs d'amont (upstreams) du proxy inverse sans identifiant, le chemin ressemblerait à ceci :

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

mais avec un identifiant, le chemin devient

```
/id/my_proxy/upstreams
```

ce qui est beaucoup plus facile à mémoriser et à écrire à la hand.

<a id="concurrent-config-changes"></a>
## Modifications de config concurrentes

<aside class="tip">

Cette section concerne tous les points d'accès `/config/`. Elle est expérimentale et sujette à modification.

</aside>


L'API de configuration de Caddy offre des [garanties ACID <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) pour les requêtes individuelles, mais les modifications impliquant plus d'une seule requête sont sujettes à des collisions ou des pertes de données si elles ne sont pas correctement synchronisées.

Par exemple, deux clients peuvent effectuer un `GET /config/foo` en même temps, faire une modification dans cette portée (chemin de config), puis appeler `POST|PUT|PATCH|DELETE /config/foo/...` en même temps pour appliquer leurs changements, entraînant une collision : soit l'un écrasera l'autre, soit le second pourrait laisser la config dans un état imprévu car il a été appliqué à une version différente de la config que celle sur laquelle il a été préparé. C'est parce que les modifications ne sont pas conscientes les unes des autres.

L'API de Caddy ne prend pas en charge les transactions s'étendant sur plusieurs requêtes, et le protocole HTTP est sans état. Cependant, vous pouvez utiliser les en-têtes `Etag` et `If-Match` pour détecter et prévenir les collisions pour toute modification, comme une sorte de contrôle de concurrence optimiste. C'est utile s'il y a la moindre chance que vous utilisiez les points d'accès `/config/...` de Caddy de manière concurrente sans synchronisation. Toutes les réponses aux requêtes `GET /config/...` possèdent un en-tête HTTP appelé `Etag` qui contient le chemin et un hachage du contenu dans cette portée (ex: `Etag: "/config/apps/http/servers 65760b8e"`). Définissez simplement l'en-tête `If-Match` sur une requête de modification avec la valeur de l'en-tête Etag provenant d'une requête `GET` précédente.

L'algorithme de base est le suivant :

1. Effectuer une requête `GET` sur n'importe quelle portée `S` de la configuration. Conserver l'en-tête `Etag` de la réponse.
2. Effectuer la modification souhaitée sur la configuration retournée.
3. Effectuer une requête `POST|PUT|PATCH|DELETE` dans la portée `S`, en définissant l'en-tête de requête `If-Match` avec la valeur de l'en-tête `Etag` stockée.
4. Si la réponse est HTTP 412 (Precondition Failed), recommencez depuis l'étape 1, ou abandonnez après trop de tentatives.

Cet algorithme permet de gérer en toute sécurité plusieurs modifications chevauchantes sur la configuration de Caddy sans synchronisation explicite. Il est conçu pour que des modifications simultanées sur différentes parties de la configuration ne nécessitent pas de nouvel essai : seules les modifications qui chevauchent la même portée de la configuration peuvent éventuellement causer une collision et donc nécessiter un nouvel essai.


<a id="post-adapt"></a>
## POST /adapt

Adapte une configuration en JSON Caddy sans la charger ni l'exécuter. En cas de succès, le document JSON résultant est retourné dans le corps de la réponse.

L'en-tête `Content-Type` est utilisé pour spécifier le format de la configuration de la même manière que pour [/load](#post-load). Par exemple, pour adapter un Caddyfile, définissez `Content-Type: text/caddyfile`.

Ce point d'accès adaptera n'importe quel format de configuration tant que l'[adaptateur de configuration](/docs/config-adapters) associé est intégré à votre build de Caddy.

### Exemples

Adapter un Caddyfile en JSON :

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="get-pkicaltidgt"></a>
## GET /pki/ca/&lt;id&gt;

Retourne des informations sur une autorité de certification (CA) d'une [application PKI](/docs/json/apps/pki/) particulière via son identifiant. Si l'identifiant de CA demandé est celui par défaut (`local`), alors la CA sera provisionnée si elle ne l'a pas déjà été. Les autres identifiants de CA retourneront une erreur s'ils n'ont pas été provisionnés auparavant.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


<a id="get-pkicaltidgtcertificates"></a>
## GET /pki/ca/&lt;id&gt;/certificates

Retourne la chaîne de certificats d'une CA d'une [application PKI](/docs/json/apps/pki/) particulière via son identifiant. Si l'identifiant de CA demandé est celui par défaut (`local`), alors la CA sera provisionnée si elle ne l'a pas déjà été. Les autres identifiants de CA retourneront une erreur s'ils n'ont pas été provisionnés auparavant.

Ce point d'accès est utilisé en interne par la commande [`caddy trust`](/docs/command-line#caddy-trust) pour permettre l'installation du certificat racine de la CA dans le magasin de confiance de votre système.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

Retourne l'état actuel des serveurs d'amont (upstreams/backends) configurés pour le proxy inverse sous forme de document JSON.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Chaque entrée du tableau JSON est un [serveur d'amont (upstream)](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/) configuré stocké dans le pool d'amont global.

- **address** est l'adresse de connexion du serveur d'amont.
- **num_requests** est le nombre de requêtes actives actuellement traitées par le serveur d'amont.
- **fails** est le nombre actuel de requêtes échouées mémorisées, tel que configuré par les vérifications de santé (health checks) passives.

Si votre objectif est de déterminer la disponibilité d'un backend, vous devrez croiser les propriétés pertinentes du serveur d'amont avec la configuration du gestionnaire que vous utilisez. Par exemple, si vous avez activé les [vérifications de santé passives](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) pour vos proxys, vous devez également prendre en compte les valeurs `fails` et `num_requests` pour déterminer si un serveur d'amont est considéré comme disponible : vérifiez que le montant de `fails` est inférieur à votre montant maximum d'échecs configuré pour votre proxy (c'est-à-dire [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)), et que `num_requests` est inférieur ou égal à votre montant maximum de requêtes par serveur d'amont configuré (c'est-à-dire [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) pour tout le proxy, ou [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) pour les serveurs d'amont individuels).
