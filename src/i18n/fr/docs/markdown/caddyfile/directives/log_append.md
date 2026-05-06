---
title: log_append (directive Caddyfile)
---

# log_append

Ajoute un champ au journal d'accès pour la requête actuelle.

Ceci doit être utilisé aux côtés de la [directive `log`](log) qui est requise pour activer la journalisation des accès en premier lieu.

La valeur peut être une chaîne statique, ou un [espace réservé (placeholder)](/docs/caddyfile/concepts#placeholders) qui sera remplacé par sa valeur au moment de la requête.


## Syntaxe

```caddy-d
log_append [<matcher>] [<]<cle> <valeur>
```

Par défaut, le champ de journal est ajouté lors de la remontée de la chaîne de middlewares (c'est-à-dire "tardivement"), après que tous les gestionnaires suivants ont terminé (ex: après des gestionnaires comme [`reverse_proxy`](reverse_proxy), [`respond`](respond), ou [`file_server`](file_server), qui écrivent une réponse), afin de capturer l'état final de la requête et de la réponse.

Si `<` est utilisé comme préfixe à la clé, il est marqué comme "précoce" (early), ce qui signifie que le champ de journal sera ajouté aux journaux *avant* d'appeler le prochain gestionnaire de la chaîne, afin que la requête puisse être lue avant d'être modifiée par les gestionnaires suivants.

À des fins de débogage uniquement (pas pour une utilisation en production), le gestionnaire possède un traitement spécial lorsque la valeur est l'un de ces espaces réservés : `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}`, ou `{http.response.body_base64}`. Si un espace réservé de corps de requête est utilisé, alors le mode "précoce" est implicitement activé, et le corps de la requête sera mis en tampon (buffered). Si un espace réservé de corps de réponse est utilisé, la mise en tampon de la réponse est activée pour capturer le corps de la réponse et le champ est ajouté au journal "tardivement", au moment où la réponse est écrite.


## Exemples

Afficher dans les journaux la zone du site depuis laquelle la requête est servie, soit `static` soit `dynamic` :

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

Afficher dans les journaux quel serveur amont du proxy inverse a été effectivement utilisé (soit `node1`, `node2` ou `node3`) ainsi que le temps passé à proxifier vers l'amont en millisecondes et le temps qu'il a fallu à l'amont pour écrire l'en-tête de réponse :

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Un champ peut être ajouté aux journaux de manière "précoce" en préfixant la clé par `<`. Cela vous permet de capturer l'état de la requête avant qu'elle ne soit modifiée par les gestionnaires suivants. Par exemple, pour journaliser le chemin original de la requête avant qu'il ne soit réécrit (bien qu'il s'agisse d'un exemple artificiel, puisque le chemin original est déjà journalisé de toute façon, mais cela aide à illustrer le point) :

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

À des fins de débogage, ajouter les corps de requête et de réponse aux journaux (pas pour la production, car cela nuit aux performances et rend les journaux très bruyants). Si vous vous attendez à ce que les corps soient des données binaires avec des caractères non imprimables, vous pouvez utiliser les variantes base64 des espaces réservés à la place (ex: `{http.request.body_base64}` et `{http.response.body_base64}`), qui seront plus faciles à copier et inspecter :

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
