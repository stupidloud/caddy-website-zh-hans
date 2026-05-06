---
title: reverse_proxy (directive Caddyfile)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Sélecteur de réponse">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@nom')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Sélecteur de réponse">@nom</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Sélecteur de réponse">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Sélecteur de réponse">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

Proxifie les requêtes vers un ou plusieurs backends avec des options configurables pour le transport, l'équilibrage de charge, les vérifications de santé, la manipulation de requêtes et la mise en tampon (buffering).

- [Syntaxe](#syntax)
- [Amonts (Upstreams)](#upstreams)
  - [Adresses d'amont](#upstream-addresses)
  - [Amonts dynamiques](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Équilibrage de charge](#load-balancing)
  - [Vérifications de santé actives](#active-health-checks)
  - [Vérifications de santé passives](#passive-health-checks)
  - [Événements](#events)
- [Streaming](#streaming)
- [En-têtes](#headers)
- [Réécritures](#rewrites)
- [Transports](#transports)
  - [Le transport `http`](#the-http-transport)
  - [Le transport `fastcgi`](#the-fastcgi-transport)
- [Interception des réponses](#intercepting-responses)
- [Exemples](#examples)


<a id="syntax"></a>
## Syntaxe

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# load balancing
	lb_policy       <nom> [<options...>]
	lb_retries      <essais>
	lb_try_duration <durée>
	lb_try_interval <intervalle>
	lb_retry_match  <request-matcher>

	# vérification de santé active
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <intervalle>
	health_passes       <nombre>
	health_fails	    <nombre>
	health_timeout      <durée>
	health_method       <méthode>
	health_status       <statut>
	health_request_body <corps>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<champ> [<valeurs...>]
	}

	# vérification de santé passive
	fail_duration     <durée>
	max_fails         <nombre>
	unhealthy_status  <statut>
	unhealthy_latency <durée>
	unhealthy_request_count <nombre>

	# streaming
	flush_interval     <durée>
	request_buffers    <taille>
	response_buffers   <taille>
	stream_timeout     <durée>
	stream_close_delay <durée>

	# manipulation requête/en-tête
	trusted_proxies [private_ranges] <plages...>
	header_up   [+|-]<champ> [<valeur|regexp> [<remplacement>]]
	header_down [+|-]<champ> [<valeur|regexp> [<remplacement>]]
	method <méthode>
	rewrite <vers>

	# aller-retour
	transport <nom> {
		...
	}

	# optionnellement intercepter les réponses de l'amont
	@nom {
		status <code...>
		header <champ> [<valeur>]
	}
	replace_status [<matcher>] <code_statut>
	handle_response [<matcher>] {
		<directives...>

		# directives spéciales disponibles uniquement dans handle_response
		copy_response [<matcher>] [<statut>] {
			status <statut>
		}
		copy_response_headers [<matcher>] {
			include <champs...>
			exclude <champs...>
		}
	}
}
```


<a id="upstreams"></a>
## Amonts (Upstreams)

- **&lt;upstreams...&gt;** est une liste d'amonts (backends) vers lesquels proxifier.
- **to** <span id="to"/> est une manière alternative de spécifier la liste des amonts, un (ou plus) par ligne.
- **dynamic** <span id="dynamic"/> configure un module d' _amonts dynamiques_. Cela permet d'obtenir la liste des amonts dynamiquement pour chaque requête. Voir les [amonts dynamiques](#dynamic-upstreams) ci-dessous pour une description des modules standard d'amonts dynamiques. Les amonts dynamiques sont récupérés à chaque itération de la boucle du proxy (donc potentiellement plusieurs fois par requête si les nouveaux essais d'équilibrage de charge sont activés) et seront préférés aux amonts statiques. Si une erreur survient, le proxy se repliera sur l'utilisation des éventuels amonts configurés statiquement.


<a id="upstream-addresses"></a>
### Adresses d'amont

Les adresses d'amont statiques peuvent prendre la forme d'une URL contenant uniquement le schéma et l'hôte/port, ou une [adresse réseau Caddy](/docs/conventions#network-addresses) conventionnelle. Exemples valides :

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

Par défaut, les connexions vers l'amont se font via le HTTP en texte clair. Lors de l'utilisation de la forme URL, un schéma peut être utilisé pour définir certains réglages par défaut du [`transport`](#transports) comme raccourci.
- L'utilisation de `https://` comme schéma utilisera le [transport `http`](#the-http-transport) avec le [`tls`](#tls) activé.

  De plus, vous pourriez avoir besoin de surcharger l'en-tête `Host` afin qu'il corresponde à la valeur du SNI TLS, laquelle est utilisée par les serveurs pour le routage et la sélection de certificat. Voir la section [HTTPS](#https) ci-dessous pour plus de détails.

- L'utilisation de `h2c://` comme schéma utilisera le [transport `http`](#the-http-transport) avec les [versions HTTP](#versions) réglées pour autoriser les connexions HTTP/2 en texte clair.

- L'utilisation de `http://` comme schéma est identique à l'omission du schéma, puisque le HTTP est déjà le défaut. Cette syntaxe est incluse par symétrie avec les autres raccourcis de schéma.

Les schémas ne peuvent pas être mélangés, car ils modifient la configuration commune du transport (un transport compatible TLS ne peut pas transporter à la fois du HTTPS et du HTTP en texte clair). Toute configuration explicite du transport ne sera pas écrasée, et l'omission des schémas ou l'utilisation d'autres ports ne fera pas supposer un transport particulier.

Lors de l'utilisation de l'IPv6 avec une zone (ex: adresses de lien local avec une interface réseau spécifique), un schéma **ne peut pas** être utilisé comme raccourci car le `%` provoquerait une erreur d'analyse d'URL ; configurez explicitement le transport à la place.

Lors de l'utilisation de la forme d'[adresse réseau](/docs/conventions#network-addresses), le type de réseau est spécifié comme préfixe à l'adresse de l'amont. Ceci ne peut pas être combiné avec un schéma d'URL. Cas particulier : `unix+h2c/` est supporté comme raccourci pour le réseau `unix/` plus les mêmes effets que le schéma `h2c://`. Les plages de ports sont supportées comme raccourci, lequel se développe en plusieurs amonts avec le même hôte.

Les adresses d'amont **ne peuvent pas** contenir de chemins ou de chaînes de requête, car cela impliquerait une réécriture simultanée de la requête pendant le proxying, comportement qui n'est ni défini ni supporté. Vous pouvez utiliser la directive [`rewrite`](/docs/caddyfile/directives/rewrite) si vous en avez besoin.

Si l'adresse n'est pas une URL (c'est-à-dire n'a pas de schéma), alors des [espaces réservés](/docs/caddyfile/concepts#placeholders) peuvent être utilisés, mais cela rend l'amont _dynamiquement statique_, ce qui signifie que potentiellement beaucoup de backends différents agissent comme un seul amont statique en termes de vérifications de santé et d'équilibrage de charge. Nous recommandons d'utiliser un module d' [amonts dynamiques](#dynamic-upstreams) à la place, si possible. Lors de l'utilisation d'espaces réservés, un port **doit** être inclus (soit par le remplacement de l'espace réservé, soit comme suffixe statique à l'adresse).


<a id="dynamic-upstreams"></a>
### Amonts dynamiques

Le proxy inverse de Caddy est livré en standard avec quelques modules d'amonts dynamiques. Notez que l'utilisation d'amonts dynamiques a des implications pour l'équilibrage de charge et les vérifications de santé, selon la configuration de la politique : les vérifications de santé actives ne s'exécutent pas pour les amonts dynamiques ; et l'équilibrage de charge ainsi que les vérifications de santé passives sont plus efficaces si la liste des amonts est relativement stable et cohérente (surtout avec le round-robin). Idéalement, les modules d'amonts dynamiques ne retournent que des backends sains et utilisables.


<a id="srv"></a>
#### SRV

Récupère les amonts depuis des enregistrements DNS SRV.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <nom>
		refresh   <intervalle>
		resolvers <ip...>
		dial_timeout        <durée>
		dial_fallback_delay <durée>
	}
```

- **&lt;full_name&gt;** est le nom de domaine complet de l'enregistrement à rechercher (ex: `_service._proto.nom`).
- **service** est la composante service du nom complet.
- **proto** est la composante protocole du nom complet. Soit `tcp` soit `udp`.
- **name** est la composante nom. Ou, si `service` et `proto` sont vides, le nom de domaine complet à interroger.
- **refresh** est la fréquence de rafraîchissement des résultats mis en cache. Par défaut : `1m`.
- **resolvers** est la liste des résolveurs DNS pour surcharger les résolveurs du système.
- **dial_timeout** est le délai d'expiration pour la requête.
- **dial_fallback_delay** est le temps d'attente avant de lancer une connexion RFC 6555 Fast Fallback. Par défaut : `300ms`.



<a id="aaaaa"></a>
#### A/AAAA

Récupère les amonts depuis des enregistrements DNS A/AAAA.

```caddy-d
	dynamic a [<nom> <port>] {
		name      <nom>
		port      <port>
		refresh   <intervalle>
		resolvers <ip...>
		dial_timeout        <durée>
		dial_fallback_delay <durée>
		versions ipv4|ipv6
	}
```

- **name** est le nom de domaine à interroger.
- **port** est le port à utiliser pour le backend.
- **refresh** est la fréquence de rafraîchissement des résultats mis en cache. Par défaut : `1m`.
- **resolvers** est la liste des résolveurs DNS pour surcharger les résolveurs du système.
- **dial_timeout** est le délai d'expiration pour la requête.
- **dial_fallback_delay** est le temps d'attente avant de lancer une connexion RFC 6555 Fast Fallback. Par défaut : `300ms`.
- **versions** est la liste des versions d'IP pour lesquelles résoudre. Par défaut : `ipv4 ipv6` ce qui correspond respectivement aux enregistrements A et AAAA.


<a id="multi"></a>
#### Multi

Ajoute les résultats de plusieurs modules d'amonts dynamiques. Utile si vous voulez des sources redondantes d'amonts, par exemple : un cluster primaire de SRV épaulé par un cluster secondaire de SRV.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** est le nom du module pour les amonts dynamiques, suivi de sa configuration. Plus d'un peut être spécifié.




<a id="load-balancing"></a>
## Équilibrage de charge

L'équilibrage de charge est typiquement utilisé pour répartir le trafic entre plusieurs amonts. En activant les nouveaux essais (retries), il peut également être utilisé avec un ou plusieurs amonts, pour retenir les requêtes jusqu'à ce qu'un amont sain puisse être sélectionné (ex: pour attendre et mitiger les erreurs lors du redémarrage ou du redéploiement d'un amont).

Ceci est activé par défaut, avec la politique `random`. Les nouveaux essais sont désactivés par défaut.

- **lb_policy** <span id="lb_policy"/> est le nom de la politique d'équilibrage de charge, ainsi que ses éventuelles options. Par défaut : `random`.

  Pour les politiques impliquant un hachage, l'algorithme [highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) est utilisé pour garantir qu'un client ou une requête avec la même clé de hachage soit associé au même amont, même si la liste des amonts change.

  Certaines politiques supportent un repli (fallback) en option, si indiqué, auquel cas elles acceptent un [bloc](/docs/caddyfile/concepts#blocks) avec `fallback <policy>` qui prend une autre politique d'équilibrage de charge. Pour ces politiques, le repli par défaut est `random`. Configurer un repli permet d'utiliser une politique secondaire si la primaire n'en sélectionne pas, autorisant des combinaisons puissantes. Les replis peuvent être imbriqués plusieurs fois si souhaité.
  
  Par exemple, `header` peut être utilisé en priorité pour permettre aux développeurs de choisir un amont spécifique, avec un repli sur `first` pour toutes les autres connexions afin d'implémenter un basculement (failover) primaire/secondaire.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` choisit un amont au hasard.

	- `random_choose <n>` sélectionne deux amonts ou plus au hasard, puis choisit celui ayant la charge la plus faible (`n` vaut généralement 2).

	- `first` choisit le premier amont disponible, selon l'ordre dans lequel ils sont définis dans la config, permettant un basculement primaire/secondaire ; n'oubliez pas d'activer les vérifications de santé avec ceci, sinon le basculement ne se produira pas.

	- `round_robin` itère chaque amont tour à tour.

	- `weighted_round_robin <poids...>` itère chaque amont tour à tour, en respectant les poids fournis. Le nombre d'arguments de poids doit correspondre au nombre d'amonts configurés. Les poids doivent être des entiers non négatifs. Par exemple avec deux amonts et les poids `5 1`, le premier amont serait sélectionné 5 fois de suite avant que le second ne soit sélectionné une fois, puis le cycle recommence. Si zéro est utilisé comme poids, cela désactivera la sélection de l'amont pour les nouvelles requêtes.

	- `least_conn` choisit l'amont avec le plus petit nombre de requêtes en cours ; si plusieurs hôtes ont le même nombre minimal de requêtes, alors l'un d'eux est choisi au hasard.

	- `ip_hash` associe l'IP distante (le pair immédiat) à un amont persistant (sticky).

	- `client_ip_hash` associe l'IP du client à un amont persistant ; ceci est idéalement couplé avec l' [option globale `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) qui active l'analyse de l'IP réelle du client, sinon il se comporte comme `ip_hash`.

	- `uri_hash` associe l'URI de la requête (chemin et requête) à un amont persistant.

	- `query [clé]` associe une requête à un amont persistant, en hachant la valeur du paramètre de requête ; si la clé spécifiée n'est pas présente, la politique de repli sera utilisée pour sélectionner un amont (`random` par défaut).

	- `header [champ]` associe un en-tête de requête à un amont persistant, en hachant la valeur de l'en-tête ; si le champ d'en-tête spécifié n'est pas présent, la politique de repli sera utilisée pour sélectionner un amont (`random` par défaut).

	- `cookie [<nom> [<secret>]]` lors de la première requête d'un client (quand il n'y a pas de cookie), la politique de repli sera utilisée pour sélectionner un amont (`random` par défaut), et un en-tête `Set-Cookie` est ajouté à la réponse (le nom par défaut du cookie est `lb` s'il n'est pas spécifié). La valeur du cookie est l'adresse de connexion de l'amont choisi, hachée avec HMAC-SHA256 (en utilisant `<secret>` comme secret partagé, chaîne vide si non spécifié).
	
	  Lors des requêtes ultérieures où le cookie est présent, la valeur du cookie sera associée au même amont s'il est disponible ; s'il n'est pas disponible ou non trouvé, un nouvel amont est sélectionné avec la politique de repli, et le cookie est ajouté à la réponse.

	  Si vous souhaitez utiliser un amont particulier à des fins de débogage, vous pouvez hacher l'adresse de l'amont avec le secret, et définir le cookie dans votre client HTTP (navigateur ou autre). Par exemple, avec PHP, vous pourriez lancer ce qui suit pour calculer la valeur du cookie, où `10.1.0.10:8080` est l'adresse de l'un de vos amonts, et `secret` est votre secret configuré :
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  Vous pouvez définir le cookie dans votre navigateur via la console Javascript, par exemple pour définir le cookie nommé `lb` :
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> est le nombre de fois qu'il faut réessayer de sélectionner des backends disponibles pour chaque requête si le prochain hôte disponible est hors service. Par défaut, les nouveaux essais sont désactivés (zéro).

  Si [`lb_try_duration`](#lb_try_duration) est également configuré, alors les nouveaux essais peuvent s'arrêter prématurément si la durée est atteinte. En d'autres termes, la durée d'essai prime sur le nombre d'essais.

- **lb_try_duration** <span id="lb_try_duration"/> est une [valeur de durée](/docs/conventions#durations) qui définit combien de temps il faut essayer de sélectionner des backends disponibles pour chaque requête si le prochain hôte disponible est hors service. Par défaut, les nouveaux essais sont désactivés (durée nulle).

  Les clients attendront jusqu'à cette durée pendant que l'équilibreur de charge tente de trouver un hôte amont disponible. Un point de départ raisonnable pourrait être `5s` puisque le délai d'expiration de connexion par défaut du transport HTTP est de `3s`, cela devrait donc permettre au moins un nouvel essai si le premier amont sélectionné ne peut être joint ; mais n'hésitez pas à expérimenter pour trouver le bon équilibre pour votre cas d'utilisation.

- **lb_try_interval** <span id="lb_try_interval"/> est une [valeur de durée](/docs/conventions#durations) qui définit le temps d'attente entre la sélection de chaque hôte dans le pool. Par défaut : `250ms`. Pertinent uniquement lorsqu'une requête vers un hôte amont échoue. Sachez que régler ceci sur `0` avec une `lb_try_duration` non nulle peut faire s'emballer le CPU si tous les backends sont hors service et que la latence est très faible.

- **lb_retry_match** <span id="lb_retry_match"/> restreint pour quelles requêtes les nouveaux essais sont autorisés. Une requête doit correspondre à cette condition pour être réessayée si la connexion à l'amont a réussi mais que l'aller-retour suivant a échoué. Si la connexion à l'amont a échoué, un nouvel essai est toujours autorisé. Par défaut, seules les requêtes `GET` sont réessayées.

  La syntaxe pour cette option est la même que pour les [sélecteurs de requête nommés](/docs/caddyfile/matchers#named-matchers), mais sans le `@nom`. Si vous avez besoin d'un seul sélecteur, vous pouvez le configurer sur la même ligne. Pour plusieurs sélecteurs, un bloc est nécessaire.



<a id="active-health-checks"></a>
### Vérifications de santé actives

Les vérifications de santé actives effectuent des vérifications en arrière-plan sur un minuteur. Pour activer ceci, `health_uri` ou `health_port` sont requis.

- **health_uri** <span id="health_uri"/> est le chemin d'URI (et la requête optionnelle) pour les vérifications de santé actives.

- **health_upstream** <span id="health_upstream"/> est l'ip:port à utiliser pour les vérifications de santé actives, s'il est différent de l'amont. Ceci doit être utilisé conjointement avec `health_header` et `{http.reverse_proxy.active.target_upstream}`.

- **health_port** <span id="health_port"/> est le port à utiliser pour les vérifications de santé actives, s'il est différent du port de l'amont. Ignoré si `health_upstream` est utilisé.

- **health_interval** <span id="health_interval"/> est une [valeur de durée](/docs/conventions#durations) qui définit la fréquence à laquelle effectuer les vérifications de santé actives. Par défaut : `30s`.

- **health_passes** <span id="health_passes"/> est le nombre de vérifications de santé réussies consécutives requises avant de marquer le backend comme sain à nouveau. Par défaut : `1`.

- **health_fails** <span id="health_fails"/> est le nombre de vérifications de santé échouées consécutives requises avant de marquer le backend comme malsain. Par défaut : `1`.

- **health_timeout** <span id="health_timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit combien de temps il faut attendre une réponse avant de marquer le backend comme hors service. Par défaut : `5s`.

- **health_method** <span id="health_method"/> est la méthode HTTP à utiliser pour la vérification de santé active. Par défaut : `GET`.

- **health_status** <span id="health_status"/> est le code d'état HTTP attendu d'un backend sain. Peut être un code d'état à 3 chiffres, ou une classe de code d'état se terminant par `xx`. Par exemple : `200` (le défaut), ou `2xx`.

- **health_request_body** <span id="health_request_body"/> est une chaîne de caractères représentant le corps de requête à envoyer avec la vérification de santé active.

- **health_body** <span id="health_body"/> est une sous-chaîne ou une expression régulière à faire correspondre sur le corps de réponse d'une vérification de santé active. Si le backend ne retourne pas un corps correspondant, il sera marqué comme hors service.

- **health_follow_redirects** fera en sorte que la vérification de santé suive les redirections fournies par l'amont. Par défaut, une réponse de redirection ferait compter la vérification de santé comme un échec.

- **health_headers** <span id="health_headers"/> permet de spécifier les en-têtes à définir sur les requêtes de vérification de santé actives. C'est utile si vous devez changer l'en-tête `Host`, ou si vous devez fournir une authentification à votre backend dans le cadre de vos vérifications de santé.



<a id="passive-health-checks"></a>
### Vérifications de santé passives

Les vérifications de santé passives se produisent en ligne avec les requêtes proxifiées réelles. Pour activer ceci, `fail_duration` est requis.

- **fail_duration** <span id="fail_duration"/>  is a [duration string](/docs/conventions#durations) that sets how long to remember a failed request. A duration > `0` enables passive health checking; the default is `0` (disabled). A reasonable starting point might be `30s` to balance error rates with responsiveness when bringing an unhealthy upstream back online; but feel free to experiment to find the right balance for your use case.

- **max_fails** <span id="max_fails"/> is the maximum number of failed requests within `fail_duration` that are needed to consider a backend to be down; must be >= `1`; default is `1`.

- **unhealthy_status** <span id="unhealthy_status"/> counts a request as failed if the response comes back with one of these status codes. Can be a 3-digit status code or a status class ending in `xx`, for example: `404` or `5xx`.

- **unhealthy_latency** <span id="unhealthy_latency"/> is a [duration string](/docs/conventions#durations) that counts a request as failed if it takes this long to get a response.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> is the number of simultaneous requests to a backend allowed before marking it as down. In other words, if a particular backend is currently already processing this many requests, then it's considered "overloaded" and other backends will be preferred instead.

  Ceci devrait être un nombre raisonnablement élevé ; configurer ceci signifie que le proxy aura une limite de `unhealthy_request_count × nombre_amonts` requêtes simultanées au total, et toute requête après ce point résultera en une erreur faute d'amonts disponibles.


<a id="events"></a>
## Événements

Lorsqu'un amont bascule d'un état sain vers malsain ou vice-versa, [un événement](/docs/caddyfile/options#event-options) est émis. Ces événements peuvent être utilisés pour déclencher d'autres actions, comme envoyer une notification ou journaliser un message. Les événements sont les suivants :

- `healthy` est émis lorsqu'un amont est marqué comme sain alors qu'il était précédemment malsain.
- `unhealthy` est émis lorsqu'un amont est marqué comme malsain alors qu'il était précédemment sain.

Dans les deux cas, le `host` est inclus comme métadonnée dans l'événement pour identifier l'amont qui a changé d'état. Il peut être utilisé comme un espace réservé avec `{event.data.host}` avec le gestionnaire d'événement `exec`, par exemple.



<a id="streaming"></a>
## Streaming

Par défaut, le proxy met partiellement en tampon la réponse pour l'efficacité réseau.

Le proxy supporte également les connexions WebSocket, effectuant la requête de mise à niveau HTTP puis faisant basculer la connexion vers un tunnel bidirectionnel.

<aside class="tip">

Par défaut, les connexions WebSocket sont fermées de force (avec un message de contrôle Close envoyé à la fois au client et à l'amont) lorsque la config est rechargée. Chaque requête détient une référence à la config, donc fermer les anciennes connexions est nécessaire pour garder l'utilisation de la mémoire sous contrôle. Ce comportement de fermeture peut être personnalisé avec les options [`stream_timeout`](#stream_timeout) et [`stream_close_delay`](#stream_close_delay).

</aside>

- **flush_interval** <span id="flush_interval"/> est une [valeur de durée](/docs/conventions#durations) qui ajuste la fréquence à laquelle Caddy doit vider le tampon de réponse vers le client. Par défaut, aucun vidage périodique n'est effectué. Une valeur négative (typiquement -1) suggère un "mode basse latence" qui désactive complètement la mise en tampon de la réponse et vide immédiatement après chaque écriture vers le client, et n'annule pas la requête vers le backend même si le client se déconnecte prématurément. Cette option est ignorée et les réponses sont vidées immédiatement vers le client si l'un des critères suivants s'applique depuis la réponse :
	- `Content-Type: text/event-stream`
	- `Content-Length` est inconnu
	- HTTP/2 des deux côtés du proxy, `Content-Length` est inconnu, et `Accept-Encoding` est soit non défini, soit vaut "identity".

- **request_buffers** <span id="request_buffers"/> fera en sorte que le proxy lise jusqu'à `<taille>` octets du corps de la requête dans un tampon avant de l'envoyer vers l'amont. C'est très inefficace et ne devrait être fait que si l'amont exige de lire les corps de requêtes sans délai (ce qui est un point que l'application amont devrait corriger). Accepte tous les formats de taille supportés par [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **response_buffers** <span id="response_buffers"/> fera en sorte que le proxy lise jusqu'à `<taille>` octets du corps de la réponse pour les mettre dans un tampon avant d'être retournés au client. Cela devrait être évité autant que possible pour des raisons de performance, mais peut être utile si le backend a des contraintes de mémoire plus serrées. Accepte tous les formats de taille supportés par [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **stream_timeout** <span id="stream_timeout"/> est une [valeur de durée](/docs/conventions#durations) après laquelle les requêtes de streaming comme les WebSockets seront fermées de force à la fin du délai. Cela annule essentiellement les connexions si elles restent ouvertes trop longtemps. Un point de départ raisonnable pourrait être `24h` pour éliminer les connexions datant de plus d'un jour. Par défaut : pas de délai d'expiration.

- **stream_close_delay** <span id="stream_close_delay"/> est une [valeur de durée](/docs/conventions#durations) qui retarde la fermeture forcée des requêtes de streaming comme les WebSockets lorsque la config est déchargée ; au lieu de cela, le flux restera ouvert jusqu'à la fin du délai. En d'autres termes, activer ceci empêche les flux de se fermer immédiatement lors d'un rechargement de config de Caddy. Activer ceci peut être une bonne idée pour éviter une vague massive de reconnexions de clients dont les connexions auraient été fermées par la fermeture de la config précédente. Un point de départ raisonnable pourrait être quelque chose comme `5m` pour permettre aux utilisateurs de quitter naturellement la page 5 minutes après un rechargement de config. Par défaut : pas de délai.


<a id="headers"></a>
## En-têtes

Le proxy peut **manipuler les en-têtes** entre lui-même et le backend :

- **header_up** <span id="header_up"/> définit, ajoute (avec le préfixe `+`), supprime (avec le préfixe `-`), ou effectue un remplacement (en utilisant deux arguments, un motif de recherche et un remplacement) dans un en-tête de requête partant vers le backend amont.

- **header_down** <span id="header_down"/> définit, ajoute (avec le préfixe `+`), supprime (avec le préfixe `-`), ou effectue un remplacement (en utilisant deux arguments, un motif de recherche et un remplacement) dans un en-tête de réponse venant de l'amont vers le client aval.

Par exemple, pour définir un en-tête de requête, en écrasant toute valeur existante :

```caddy-d
header_up Quelque-En-tete "la valeur"
```

Pour ajouter un en-tête de réponse ; notez qu'il peut y avoir plusieurs valeurs pour un champ d'en-tête :

```caddy-d
header_down +Quelque-En-tete "première valeur"
header_down +Quelque-En-tete "seconde valeur"
```

Pour supprimer un en-tête de requête, l'empêchant d'atteindre le backend :

```caddy-d
header_up -Quelque-En-tete
```

Pour supprimer tous les en-têtes de requête correspondants, en utilisant une correspondance par suffixe :

```caddy-d
header_up -Quelque-*
```

Pour supprimer *tous* les en-têtes de requête, afin de pouvoir ajouter individuellement ceux que vous voulez (non recommandé) :

```caddy-d
header_up -*
```

Pour effectuer un remplacement par expression régulière sur un en-tête de requête :

```caddy-d
header_up Quelque-En-tete "^prefixe-([A-Za-z0-9]*)$" "remplace-$1-suffixe"
```

Le langage d'expression régulière utilisé est RE2, inclus dans Go. Voir la [référence de syntaxe RE2](https://github.com/google/re2/wiki/Syntax) et l' [aperçu de la syntaxe regexp de Go](https://pkg.go.dev/regexp/syntax). La chaîne de remplacement est [développée](https://pkg.go.dev/regexp#Regexp.Expand), permettant l'utilisation des valeurs capturées, par exemple `$1` étant le premier groupe de capture.


### Par défaut

Par défaut, Caddy transmet les en-têtes entrants — y compris `Host` — au backend sans modifications, avec trois exceptions :

- Il définit ou augmente le champ d'en-tête [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Il définit le champ d'en-tête [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Il définit le champ d'en-tête [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"/> Pour ces en-têtes `X-Forwarded-*`, par défaut, le proxy ignorera leurs valeurs provenant des requêtes entrantes, afin de prévenir l'usurpation (spoofing).

Si Caddy n'est pas le premier serveur auquel vos clients se connectent (par exemple lorsqu'un CDN est devant Caddy), vous pouvez configurer `trusted_proxies` avec une liste de plages d'IP (CIDR) desquelles les requêtes entrantes sont de confiance pour avoir envoyé de bonnes valeurs pour ces en-têtes.

Il est fortement recommandé de configurer cela via l' [option globale `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) plutôt que dans le proxy, afin que cela s'applique à tous les gestionnaires de proxy de votre serveur, et cela présente l'avantage d'activer l'analyse de l'IP du client.

<aside class="tip">

Si vous utilisez Cloudflare devant Caddy, sachez que vous pourriez être vulnérable à l'usurpation de l'en-tête `X-Forwarded-For`. Nos amis chez [Authelia](https://www.authelia.com) ont documenté une [solution de contournement](https://www.authelia.com/integration/proxies/forwarded-headers/) pour configurer Cloudflare afin qu'il ignore les valeurs entrantes pour cet en-tête.

</aside>

De plus, lors de l'utilisation du [transport `http`](#the-http-transport), l'en-tête `Accept-Encoding: gzip` sera défini s'il est manquant dans la requête du client. Cela permet à l'amont de servir du contenu compressé s'il le peut. Ce comportement peut être désactivé avec [`compression off`](#compression) sur le transport.


### HTTPS

Puisque (la plupart) des en-têtes conservent leur valeur originale lors du proxying, il est souvent nécessaire de surcharger l'en-tête `Host` avec l'adresse de l'amont configuré lors du proxying vers le HTTPS, de sorte que l'en-tête `Host` corresponde à la valeur du ServerName TLS :

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Depuis Caddy v2.11.0, ceci est fait automatiquement, il n'est donc plus nécessaire de surcharger explicitement l'en-tête `Host` lors du proxying vers le HTTPS. Si vous souhaitez désactiver ce comportement, vous pouvez définir l'en-tête `Host` à sa valeur originale (mais cela a rarement du sens de le faire) :

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

L'en-tête `X-Forwarded-Host` est toujours transmis [par défaut](#defaults), l'amont peut donc toujours l'utiliser s'il a besoin de connaître la valeur originale de l'en-tête `Host`.

Il en va de même lors de la terminaison du TLS dans Caddy et du proxying via HTTP, que ce soit vers un port ou un socket unix. En effet, Caddy lui-même doit recevoir le bon Host lorsqu'il est la cible de `reverse_proxy`. Dans le cas du socket unix, `upstream_hostport` sera le chemin du socket, et le Host doit être défini explicitement.


<a id="rewrites"></a>
## Réécritures

Par défaut, Caddy effectue la requête amont avec la même méthode HTTP et la même URI que la requête entrante, sauf si une réécriture a été effectuée dans la chaîne de middlewares avant d'atteindre `reverse_proxy`.

Avant de la proxifier, la requête est clonée ; cela garantit que toute modification effectuée sur la requête pendant le gestionnaire ne fuite pas vers d'autres gestionnaires. C'est utile dans les situations où le traitement doit continuer après le proxy.

En plus des [manipulations d'en-têtes](#headers), la méthode et l'URI de la requête peuvent être modifiées avant d'être envoyées vers l'amont :

- **method** <span id="method"/> modifie la méthode HTTP de la requête clonée. Si la méthode est modifiée en `GET` ou `HEAD`, alors le corps de la requête entrante ne sera *pas* envoyé vers l'amont par ce gestionnaire. C'est utile si vous souhaitez permettre à un autre gestionnaire de consommer le corps de la requête.
- **rewrite** <span id="rewrite"/> modifie l'URI (chemin et requête) de la requête clonée. C'est similaire à la [directive `rewrite`](/docs/caddyfile/directives/rewrite), sauf qu'elle ne persiste pas la réécriture au-delà de la portée de ce gestionnaire.

Ces réécritures sont souvent utiles pour un modèle comme les "requêtes de pré-vérification", où une requête est envoyée à un autre serveur pour aider à décider comment continuer le traitement de la requête actuelle.

Par exemple, la requête pourrait être envoyée à une passerelle d'authentification pour décider si la requête provient d'un utilisateur authentifié (ex: la requête possède un cookie de session) et doit continuer, ou si elle doit plutôt être redirigée vers une page de connexion. Pour ce modèle, Caddy fournit une directive raccourcie [`forward_auth`](/docs/caddyfile/directives/forward_auth) pour éviter la majeure partie du code de configuration répétitif.



<a id="transports"></a>
## Transports

Le **transport** de proxy de Caddy est branchable (pluggable) :

- **transport** <span id="transport"/> définit comment communiquer avec le backend. Par défaut : `http`.


<a id="the-http-transport"></a>
### Le transport `http`

```caddy-d
transport http {
	read_buffer             <taille>
	write_buffer            <taille>
	max_response_header     <taille>
	proxy_protocol          v1|v2
	dial_timeout            <durée>
	dial_fallback_delay     <durée>
	response_header_timeout <durée>
	expect_continue_timeout <durée>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <fichier_cert> <fichier_clé>
	tls_insecure_skip_verify
	tls_curves <courbes...>
	tls_timeout <durée>
	tls_trust_pool <module>
	tls_server_name <nom_serveur>
	tls_renegotiation <niveau>
	tls_except_ports <ports...>
	keepalive [off|<durée>]
	keepalive_interval <intervalle>
	keepalive_idle_conns <nombre_max>
	keepalive_idle_conns_per_host <nombre>
	versions <versions...>
	compression off
	max_conns_per_host <nombre>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> est la taille du tampon de lecture en octets. Accepte tous les formats supportés par [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Par défaut : `4KiB`.

- **write_buffer** <span id="write_buffer"/> est la taille du tampon d'écriture en octets. Accepte tous les formats supportés par [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Par défaut : `4KiB`.

- **max_response_header** <span id="max_response_header"/> est le nombre maximum d'octets à lire depuis les en-têtes de réponse. Accepte tous les formats supportés par [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Par défaut : `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> active le [protocole PROXY](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (popularisé par HAProxy) sur la connexion vers l'amont, en ajoutant les données de l'IP réelle du client. Ceci est idéalement couplé avec l' [option globale `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) si Caddy est derrière un autre proxy. Les versions `v1` et `v2` sont supportées. Ceci ne devrait être utilisé que si vous savez que le serveur amont est capable d'analyser le protocole PROXY. Par défaut, ceci est désactivé.

- **dial_timeout** <span id="dial_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente lors de la connexion au socket de l'amont. Par défaut : `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> est la [durée](/docs/conventions#durations) maximale d'attente avant de lancer une connexion RFC 6555 Fast Fallback. Une valeur négative désactive cela. Par défaut : `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente pour lire les en-têtes de réponse depuis l'amont. Par défaut : pas de délai d'expiration.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente pour les premiers en-têtes de réponse de l'amont après avoir écrit complètement les en-têtes de requête si la requête possède l'en-tête `Expect: 100-continue`. Par défaut : pas de délai d'expiration.

- **read_timeout** <span id="read_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente pour la prochaine lecture depuis le backend. Par défaut : pas de délai d'expiration.

- **write_timeout** <span id="write_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente pour les prochaines écritures vers le backend. Par défaut : pas de délai d'expiration.

- **resolvers** <span id="resolvers"/> est une liste de résolveurs DNS pour surcharger les résolveurs du système.

- **tls** <span id="tls"/> utilise le HTTPS avec le backend. Ceci sera activé automatiquement si vous spécifiez des backends utilisant le schéma `https://`, ou si l'une des options `tls_*` ci-dessous est configurée.

- **tls_client_auth** <span id="tls_client_auth"/> active l'authentification client TLS de deux manières : (1) en spécifiant un nom de domaine pour lequel Caddy doit obtenir un certificat et le maintenir renouvelé, ou (2) en spécifiant un fichier de certificat et un fichier de clé à présenter pour l'authentification client TLS auprès du backend.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> désactive la vérification de l'échange TLS, rendant la connexion non sécurisée et vulnérable aux attaques de l'homme du milieu. _Ne pas utiliser en production._

- **tls_curves** <span id="tls_curves"/> est une liste de courbes elliptiques à supporter pour la connexion amont. Les défauts de Caddy sont modernes et sûrs, vous ne devriez donc avoir besoin de configurer cela que si vous avez des exigences spécifiques.

- **tls_timeout** <span id="tls_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente pour que l'échange TLS se termine. Par défaut : pas de délai d'expiration.

- **tls_trust_pool** <span id="tls_trust_pool"/> configure la source des autorités de certification de confiance de manière similaire à la [sous-directive `trust_pool`](/docs/caddyfile/directives/tls#trust_pool) décrite dans la documentation de la directive `tls`. La liste des sources de pools de confiance disponibles dans une installation standard de Caddy est disponible [ici](/docs/caddyfile/directives/tls#trust-pool-providers).

- **tls_server_name** <span id="tls_server_name"/> définit le nom du serveur utilisé lors de la vérification du certificat reçu lors de l'échange TLS. Par défaut, il utilisera la partie hôte de l'adresse de l'amont.

  Vous n'avez besoin de surcharger ceci que si votre adresse d'amont ne correspond pas au certificat que l'amont est susceptible d'utiliser. Par exemple si l'adresse de l'amont est une adresse IP, alors vous auriez besoin de configurer ceci avec le nom d'hôte servi par le serveur amont.

  Un espace réservé de requête peut être utilisé, auquel cas un clone de la config du transport HTTP sera utilisé sur chaque requête, ce qui peut entraîner une pénalité de performance.

- **tls_renegotiation** <span id="tls_renegotiation"/> définit le niveau de renégociation TLS. La renégociation TLS est l'acte d'effectuer des échanges ultérieurs après le premier. Le niveau peut être l'un des suivants :
  - `never` (le défaut) désactive la renégociation.
  - `once` permet à un serveur distant de demander la renégociation une fois par connexion.
  - `freely` permet à un serveur distant de demander la renégociation de manière répétée.

- **tls_except_ports** <span id="tls_except_ports"/> lorsque le TLS est activé, si la cible amont utilise l'un des ports donnés, le TLS sera désactivé pour ces connexions. Ceci peut être utile lors de la configuration d'amonts dynamiques, où certains amonts attendent du HTTP et d'autres des requêtes HTTPS.

- **keepalive** <span id="keepalive"/> est soit `off` soit une [valeur de durée](/docs/conventions#durations) qui spécifie combien de temps garder les connexions ouvertes (timeout). Par défaut : `2m`.

  ⚠️ Les requêtes vers des amonts HTTP/1.1 peuvent échouer à cause d'erreurs "connection reset by peer" si la durée du keepalive dépasse le délai de keepalive du serveur amont. Les requêtes idempotentes seront réessayées par le transport HTTP de Go, mais Caddy répondra avec un code d'état 502 dans les autres cas.

- **keepalive_interval** <span id="keepalive_interval"/> est la [durée](/docs/conventions#durations) entre les sondes de vivacité (liveness probes). Par défaut : `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> définit le nombre maximum de connexions à garder vivantes. Par défaut : pas de limite.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> si non nul, contrôle le nombre maximum de connexions inactives (keep-alive) à garder par hôte. Par défaut : `32`.

- **versions** <span id="versions"/> permet de personnaliser quelles versions de HTTP supporter.
  
  Les options valides sont : `1.1`, `2`, `h2c`, `3`. 

  Par défaut : `1.1 2`, ou si le [schéma de l'amont](#upstream-addresses) est `h2c://`, alors le défaut est `h2c 2`.

  `h2c` active les connexions HTTP/2 en texte clair vers l'amont. C'est une fonctionnalité non standard qui n'utilise pas le transport HTTP par défaut de Go, elle est donc exclusive des autres fonctionnalités.

  `3` active les connexions HTTP/3 vers l'amont. ⚠️ C'est une fonctionnalité expérimentale et sujette à modification.

- **compression** <span id="compression"/> peut être utilisé pour désactiver la compression vers le backend en le réglant sur `off`.

- **max_conns_per_host** <span id="max_conns_per_host"/> limite optionnellement le nombre total de connexions par hôte, incluant les connexions en phase de connexion, actives, et inactives. Par défaut : pas de limite.

- **network_proxy** <span id="network_proxy"/> spécifie le nom d'un module de proxy réseau à utiliser pour les requêtes vers le serveur amont. S'il n'est pas explicitement configuré, Caddy respecte le proxy configuré via les variables d'environnement selon la [stdlib Go](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), c'est-à-dire `HTTP_PROXY`, `HTTPS_PROXY`, et `NO_PROXY`. Lorsqu'une valeur est fournie pour ce paramètre, les requêtes passeront par le proxy inverse dans l'ordre suivant : Client (utilisateurs) → `reverse_proxy` → `network_proxy` → amont. Les modules intégrés sont :
	- `none`, qui sert à ignorer les réglages d'environnement de `HTTP_PROXY`, `HTTPS_PROXY`, et `NO_PROXY`.
	- `url <url>`, qui sert à spécifier une URL unique outrepassant la configuration d'environnement.


<a id="the-fastcgi-transport"></a>
### Le transport `fastcgi`

```caddy-d
transport fastcgi {
	root  <chemin>
	split <sur>
	env   <cle> <valeur>
	resolve_root_symlink
	dial_timeout  <durée>
	read_timeout  <durée>
	write_timeout <durée>
	capture_stderr
}
```

- **root** <span id="root"/> est la racine du site. Par défaut : `{http.vars.root}` ou le répertoire de travail actuel.

- **split** <span id="split"/> est l'endroit où découper le chemin pour obtenir le `PATH_INFO` à la fin de l'URI.

- **env** <span id="env"/> définit une variable d'environnement supplémentaire à la valeur donnée. Peut être spécifiée plus d'une fois pour plusieurs variables d'environnement.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> active la résolution du répertoire `root` vers sa valeur réelle en évaluant un lien symbolique, s'il en existe un.

- **dial_timeout** <span id="dial_timeout"/> est le temps d'attente lors de la connexion au socket de l'amont. Accepte les [valeurs de durée](/docs/conventions#durations). Par défaut : `3s`.

- **read_timeout** <span id="read_timeout"/> est le temps d'attente lors de la lecture depuis le serveur FastCGI. Accepte les [valeurs de durée](/docs/conventions#durations). Par défaut : pas de délai d'expiration.

- **write_timeout** <span id="write_timeout"/> est le temps d'attente lors de l'envoi vers le serveur FastCGI. Accepte les [valeurs de durée](/docs/conventions#durations). Par défaut : pas de délai d'expiration.

- **capture_stderr** <span id="capture_stderr"/> active la capture et la journalisation de tout message envoyé par le serveur fastcgi amont sur `stderr`. La journalisation se fait au niveau `WARN` par défaut. Si la réponse a un statut `4xx` ou `5xx`, alors le niveau `ERROR` sera utilisé à la place. Par défaut, `stderr` est ignoré.

<aside class="tip">

Si vous essayez de servir une application PHP moderne, vous cherchez peut-être la [directive `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi), qui est un raccourci pour un proxy utilisant la directive `fastcgi`, avec les réécritures nécessaires pour utiliser `index.php` comme point d'entrée de routage.

</aside>


<a id="intercepting-responses"></a>
## Interception des réponses

Le proxy inverse peut être configuré pour intercepter les réponses du backend. Pour faciliter cela, des [sélecteurs de réponse](/docs/caddyfile/response-matchers) peuvent être définis (syntaxe similaire aux sélecteurs de requête) et la première route `handle_response` correspondante sera invoquée.

Lorsqu'un gestionnaire de réponse est invoqué, la réponse du backend n'est pas écrite vers le client, et la route `handle_response` configurée sera exécutée à la place ; il appartient à cette route d'écrire une réponse. Si la route n'écrit *pas* de réponse, alors le traitement de la requête continuera avec les gestionnaires qui sont [ordonnés après](/docs/caddyfile/directives#directive-order) ce `reverse_proxy`.

- **@nom** est le nom d'un [sélecteur de réponse](/docs/caddyfile/response-matchers). Tant que chaque sélecteur de réponse possède un nom unique, plusieurs sélecteurs peuvent être définis. Une réponse peut être sélectionnée sur son code d'état et la présence ou la valeur d'un en-tête de réponse.

- **replace_status** <span id="replace_status"/> change simplement le code d'état de la réponse lorsqu'elle correspond au sélecteur donné.

- **handle_response** <span id="handle_response"/> définit la route à exécuter lorsqu'elle correspond au sélecteur donné (ou, si un sélecteur est omis, toutes les réponses). Le premier bloc correspondant sera appliqué. À l'intérieur d'un bloc `handle_response`, toutes les autres [directives](/docs/caddyfile/directives) peuvent être utilisées.

De plus, à l'intérieur de `handle_response`, deux directives de gestionnaire spéciales peuvent être utilisées :

- **copy_response** <span id="copy_response"/> copie le corps de la réponse reçu du backend en retour vers le client. Permet optionnellement de changer le code d'état de la réponse ce faisant. Cette directive est [ordonnée avant `respond`](/docs/caddyfile/directives#directive-order).

- **copy_response_headers** <span id="copy_response_headers"/> copie les en-têtes de réponse du backend vers le client, incluant optionnellement _OU_ excluant une liste de champs d'en-tête (on ne peut pas spécifier à la fois `include` et `exclude`). Cette directive est [ordonnée après `header`](/docs/caddyfile/directives#directive-order).

Trois espaces réservés seront rendus disponibles au sein des routes `handle_response` :

- `{rp.status_code}` Le code d'état de la réponse du backend.

- `{rp.status_text}` Le texte de statut de la réponse du backend.

- `{rp.header.*}` Les en-têtes de la réponse du backend.

Alors que le gestionnaire de réponse du proxy inverse peut copier la nouvelle réponse reçue du proxy vers le client, il ne peut pas transmettre cette nouvelle réponse à un proxy inverse ultérieur. Chaque utilisation de `reverse_proxy` reçoit le corps de la requête originale (ou tel que modifié par un module différent).



<a id="examples"></a>
## Exemples

Proxifier toutes les requêtes vers un backend local :

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


[Équilibrer la charge](#load-balancing) de toutes les requêtes [entre 3 backends](#upstreams) :

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


Idem, mais uniquement pour les requêtes sous `/api`, et persistant en utilisant la [politique `cookie`](#lb_policy) :

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


Utiliser les [vérifications de santé actives](#active-health-checks) pour déterminer quels backends sont sains, et activer les [nouveaux essais](#lb_try_duration) sur les connexions échouées, en retenant la requête jusqu'à ce qu'un backend sain soit trouvé :

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Configurer quelques [options de transport](#transports) :

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Proxifier vers un [amont HTTPS](#https) (depuis la v2.11.0, Caddy définit automatiquement l'en-tête `Host` pour correspondre à l'hôte de l'amont, il n'est donc plus nécessaire de le faire manuellement) :

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Proxifier vers un amont HTTPS, mais [⚠️ désactiver la vérification TLS](#tls_insecure_skip_verify). Ce n'est PAS RECOMMANDÉ, car cela désactive tous les contrôles de sécurité qu'offre le HTTPS ; proxifier via HTTP dans des réseaux privés est préférable si possible, car cela évite le faux sentiment de sécurité :

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


À la place, vous pouvez établir la confiance avec l'amont en [faisant explicitement confiance au certificat de l'amont](#tls_trust_pool), et (optionnellement) en réglant le TLS-SNI pour correspondre au nom d'hôte dans le certificat de l'amont :

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /chemin/vers/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



[Supprimer un préfixe de chemin](handle_path) avant le proxying ; mais soyez attentif au [problème des sous-dossiers <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575) :

```caddy
example.com {
	handle_path /prefixe/* {
		reverse_proxy localhost:9000
	}
}
```


Remplacer un préfixe de chemin avant le proxying, en utilisant une [réécriture `rewrite`](/docs/caddyfile/directives/rewrite) :

```caddy
example.com {
	handle_path /ancien-prefixe/* {
		rewrite /nouveau-prefixe{path}
		reverse_proxy localhost:9000
	}
}
```


Support de `X-Accel-Redirect`, c'est-à-dire servir des fichiers statiques comme demandé, en [interceptant la réponse](#intercepting-responses) :

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /chemin/vers/fichiers/prives
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Page d'erreur personnalisée pour les erreurs venant de l'amont, en [interceptant les réponses d'erreur](#intercepting-responses) par code d'état :

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /chemin/vers/pages/erreur
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Obtenir des backends [dynamiquement](#dynamic-upstreams) à partir de requêtes DNS d'[enregistrements `A`/`AAAA`](#aaaaa) :

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Obtenir des backends [dynamiquement](#dynamic-upstreams) à partir de requêtes DNS d'[enregistrements `SRV`](#srv) :

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


L'utilisation des [vérifications de santé actives](#active-health-checks) et de `health_upstream` peut être utile lors de la création d'un service intermédiaire pour effectuer une vérification de santé plus approfondie. `{http.reverse_proxy.active.target_upstream}` peut alors être utilisé comme en-tête pour fournir l'amont original au service de vérification de santé.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
