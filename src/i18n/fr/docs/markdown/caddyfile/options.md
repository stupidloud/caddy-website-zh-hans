---
title: Options globales (Caddyfile)
---

<script>
ready(function() {
	// Nous ajouterons des liens sur les options dans le bloc de code en haut
	// vers leurs ancres associées.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Ajouter des liens sur les commentaires vers leurs sections respectives
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // l'espace blanc de début
			text = text.slice(text.indexOf('#')); // seulement la partie commentaire
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Correction chirurgicale d'un lien en double ; 'name' apparaît deux fois comme lien
	// pour deux sections différentes, nous changeons donc la seconde en #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Correction chirurgicale de `renewal_window_ratio` qui apparaît deux fois
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


# Options globales

Le Caddyfile permet de spécifier des options s'appliquant globalement. Certaines options agissent comme des valeurs par défaut ; d'autres personnalisent les serveurs HTTP et ne s'appliquent pas à un seul site particulier ; tandis que d'autres encore personnalisent le comportement de l'[adaptateur](/docs/config-adapters) Caddyfile.

Le tout début de votre Caddyfile peut être un **bloc d'options globales**. C'est un bloc qui n'a pas de clés :

```caddy
{
	...
}
```

Il ne peut y en avoir qu'un seul au maximum, et il doit être le premier bloc du Caddyfile.

Les options possibles sont (cliquez sur chaque option pour accéder à sa documentation) :

```caddy
{
	# Options générales
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hôtes...>
	order <dir1> first|last|[before|after <dir2>]
	storage <nom_module> {
		<options...>
	}
	storage_clean_interval <durée>
	admin   off|<adresse> {
		origins <origines...>
		enforce_origin
	}
	persist_config off
	log [nom] {
		output  <module_writer> ...
		format  <module_encoder> ...
		level   <niveau>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <durée>
	shutdown_delay <durée>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# Options TLS
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <votre_email>
	default_sni <nom>
	fallback_sni <nom>
	local_certs
	skip_install_trust
	acme_ca <url_repertoire>
	acme_ca_root <fichier_pem>
	acme_eab {
		key_id <id_clé>
		mac_key <clé_mac>
	}
	acme_dns <fournisseur> ...
	dns <fournisseur> ...
	ech <noms_publics...> {
		dns <fournisseur> ...
	}
	on_demand_tls {
		ask        <point_acces>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <nom> ...
	renew_interval <durée>
	cert_lifetime  <durée>
	ocsp_interval  <durée>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Options du serveur
	servers [<adresse_ecoute>] {
		name <nom>
		listener_wrappers {
			<enveloppes_ecouteur...>
		}
		timeouts {
			read_body   <durée>
			read_header <durée>
			write       <durée>
			idle        <durée>
		}
		keepalive_interval <durée>
		keepalive_idle     <durée>
		keepalive_count    <nombre>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <en_têtes...>

		trace
		max_header_size <taille>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# Systèmes de fichiers
	filesystem <nom> <module> {
		<options...>
	}

	# Options PKI
	pki {
		ca [<id>] {
			name                  <nom>
			root_cn               <nom>
			intermediate_cn       <nom>
			intermediate_lifetime <durée>
			maintenance_interval  <durée>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <chemin>
				key    <chemin>
			}
			intermediate {
				format <format>
				cert   <chemin>
				key    <chemin>
			}
		}
	}

	# Options d'événements
	events {
		on <événement> <gestionnaire...>
	}
}
```


## Options générales

<a id="debug"></a>
##### `debug`
Active le mode debug, ce qui définit le niveau de journalisation à `DEBUG` pour le [logger par défaut](#log). Cela révèle plus de détails qui peuvent être utiles lors du dépannage (et est très verbeux en production). Nous vous demandons d'activer ceci avant de demander de l'aide sur les [forums de la communauté](https://caddy.community). Par exemple, en haut de votre Caddyfile, si vous n'avez pas d'autres options globales :

```caddy
{
	debug
}
```


<a id="http-port"></a>
##### `http_port`
Le port à utiliser par le serveur pour le HTTP.

**Pour usage interne uniquement** ; ne change pas le port HTTP pour les clients. Ceci est typiquement utilisé si, au sein de votre réseau interne, vous avez besoin de rediriger le port `80` vers un port différent (ex: `8080`) avant qu'il n'atteigne Caddy, pour des raisons de routage.

Par défaut : `80`


<a id="https-port"></a>
##### `https_port`
Le port à utiliser par le serveur pour le HTTPS.

**Pour usage interne uniquement** ; ne change pas le port HTTPS pour les clients. Ceci est typiquement utilisé si, au sein de votre réseau interne, vous avez besoin de rediriger le port `443` vers un port différent (ex: `8443`) avant qu'il n'atteigne Caddy, pour des raisons de routage.

Par défaut : `443`


<a id="default-bind"></a>
##### `default_bind`
La ou les adresses de liaison (bind) par défaut à utiliser pour tous les sites, si la [directive `bind`](/docs/caddyfile/directives/bind) n'est pas utilisée dans le site. Par défaut : vide, ce qui lie à toutes les interfaces.

<aside class="tip">

Gardez à l'esprit que cela ne s'appliquera qu'aux serveurs générés par le Caddyfile ; cela signifie que le serveur HTTP créé par le [HTTPS automatique](/docs/automatic-https) pour les redirections HTTP-vers-HTTPS n'héritera pas de ces adresses de liaison. Pour contourner cela, assurez-vous de déclarer un site `http://` (il peut être vide, sans directives) afin qu'il existe lors de l'adaptation du Caddyfile, pour recevoir les adresses de liaison.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



<a id="order"></a>
##### `order`
Assigne un ordre à la ou aux directives de gestionnaire HTTP. Comme les gestionnaires HTTP s'exécutent dans une chaîne séquentielle, il est nécessaire que les gestionnaires soient exécutés dans le bon ordre. Les directives standard ont un [ordre prédéfini](/docs/caddyfile/directives#directive-order), mais si vous utilisez des modules de gestionnaire HTTP tiers, vous devrez définir l'ordre explicitement soit en utilisant cette option, soit en plaçant la directive dans un [bloc `route`](/docs/caddyfile/directives/route). L'ordre peut être décrit de manière absolue (`first` ou `last`), ou relative (`before` ou `after`) à une autre directive.

Par exemple, pour utiliser le [plugin `replace-response`](https://github.com/caddyserver/replace-response), vous voudriez vous assurer que sa directive est ordonnée après `encode` afin qu'elle puisse effectuer des remplacements avant que la réponse ne soit encodée (car les réponses remontent la chaîne des gestionnaires, elles ne la descendent pas) :

```caddy
{
	order replace after encode
}
```


<a id="storage"></a>
##### `storage`
Configure le mécanisme de stockage de Caddy. Par défaut, il s'agit de [`file_system`](/docs/json/storage/file_system/). Il existe de nombreux autres [modules de stockage](/docs/json/storage/) disponibles en tant que plugins.

Par exemple, pour changer l'emplacement de stockage du système de fichiers :

```caddy
{
	storage file_system /chemin/vers/emplacement/perso
}
```

La personnalisation du module de stockage est typiquement nécessaire lors de la synchronisation du stockage de Caddy entre plusieurs instances de Caddy pour s'assurer qu'elles utilisent toutes les mêmes certificats et clés. Consultez la [section HTTPS automatique sur le stockage](/docs/automatic-https#storage) pour plus de détails.


<a id="storage-clean-interval"></a>
##### `storage_clean_interval`
Fréquence à laquelle les unités de stockage sont scannées pour supprimer les ressources anciennes ou expirées. Ces scans exercent beaucoup de lectures (et d'opérations de listage) sur le module de stockage, choisissez donc un intervalle plus long pour les déploiements importants. Accepte les [valeurs de durée](/docs/conventions#durations).

Le stockage sera toujours nettoyé lors du premier démarrage du processus. Ensuite, un nouveau nettoyage sera lancé après cette durée suivant le début du nettoyage précédent si celui-ci s'est terminé en moins de la moitié de cet intervalle (sinon le prochain démarrage sera sauté).

Par défaut : `24h`

```caddy
{
	storage_clean_interval 7d
}
```




<a id="admin"></a>
##### `admin`
Personnalise le [point d'accès de l'API d'administration](/docs/api). Accepte les espaces réservés. Prend des [adresses réseau](/docs/conventions#network-addresses).

Par défaut : `localhost:2019`, sauf si la variable d'environnement `CADDY_ADMIN` est définie.

S'il est défini sur `off`, alors le point d'accès d'administration sera désactivé. Lorsqu'il est désactivé, **les modifications de configuration seront impossibles** sans arrêter et redémarrer le serveur, car la [commande `caddy reload`](/docs/command-line#caddy-reload) utilise l'API d'administration pour pousser la nouvelle config vers le serveur en cours d'exécution.

N'oubliez pas d'utiliser le drapeau CLI `--address` avec les [commandes](/docs/command-line) compatibles pour spécifier le point d'accès d'administration actuel, si l'adresse du serveur en cours d'exécution a été modifiée par rapport à la valeur par défaut.

Prend également en charge ces sous-options :

- **origins** configure la liste des [origines](https://developer.mozilla.org/en-US/docs/Glossary/Origin) autorisées à se connecter au point d'accès.

  Une valeur par défaut est choisie intelligemment :
  - si l'adresse d'écoute est le loopback (ex: `localhost` ou une IP loopback, ou un socket unix), alors les origines autorisées sont `localhost`, `::1` et `127.0.0.1`, jointes au port de l'adresse d'écoute (donc `localhost:2019` est une origine valide).
  - si l'adresse d'écoute n'est pas le loopback, alors l'origine autorisée est la même que l'adresse d'écoute.

  Si l'hôte de l'adresse d'écoute n'est pas une interface wildcard (les wildcards incluent : chaîne vide, ou `0.0.0.0`, ou `[::]`), alors l'application de l'en-tête `Host` est effectuée. Concrètement, cela signifie que par défaut, l'en-tête `Host` est validé pour être dans `origins`, puisque l'interface est `localhost`. Mais pour une adresse comme `:2020` qui possède une interface wildcard, la validation de l'en-tête `Host` n'est pas effectuée.

- **enforce_origin** force l'application de l'en-tête de requête `Origin`. Cela se fait implicitement chaque fois que des en-têtes CORS sont envoyés par le client ou si le client désactive explicitement le CORS avec `Sec-Fetch-Mode: no-cors`. Sinon, cette option est surtout utile lorsque l'adresse d'écoute est une interface wildcard (puisque `Host` n'est pas validé), et que l'API d'administration est exposée à l'internet public. Elle active les vérifications pré-vol (preflight) CORS et garantit que l'en-tête `Origin` est validé par rapport à la liste `origins`. N'utilisez ceci que si vous faites tourner Caddy sur votre machine de développement et avez besoin d'accéder à l'API d'administration depuis un navigateur web.

Par exemple, pour exposer l'API d'administration sur un port différent, sur toutes les interfaces — ⚠️ ce port **ne devrait pas être exposé publiquement**, sinon n'importe qui peut contrôler votre serveur ; envisagez d'activer l'application de l'origine si vous avez besoin qu'il soit public :

```caddy
{
	admin :2020
}
```

Pour désactiver l'API d'administration — ⚠️ cela rend les **rechargements de config impossibles** sans arrêter et redémarrer le serveur :

```caddy
{
	admin off
}
```

Pour utiliser un [socket unix](/docs/conventions#network-addresses) pour l'API d'administration, permettant un contrôle d'accès via les permissions de fichiers :

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Pour n'autoriser que les requêtes ayant un en-tête `Origin` correspondant :

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



<a id="persist-config"></a>
##### `persist_config`

Contrôle si la configuration JSON actuelle doit être persistée dans le [répertoire de configuration](/docs/conventions#configuration-directory), afin d'éviter de perdre les modifications de config effectuées via l'API d'administration. Actuellement, seule l'option `off` est supportée. Par défaut, la configuration est persistée.

```caddy
{
	persist_config off
}
```



<a id="log"></a>
##### `log`
Configure les loggers nommés.

Le nom peut être passé pour indiquer un logger spécifique dont on veut personnaliser le comportement. Si aucun nom n'est spécifié, le comportement du logger `default` est modifié. Vous pouvez en savoir plus sur le logger `default` et une explication sur le [fonctionnement de la journalisation dans Caddy](/docs/logging).

Plusieurs loggers avec des noms différents peuvent être configurés en utilisant `log` plusieurs fois.

Ceci diffère de la [directive `log`](/docs/caddyfile/directives/log), qui configure uniquement la journalisation des requêtes HTTP (également appelée journaux d'accès). L'option globale `log` partage sa structure de configuration avec la directive (sauf pour `include` et `exclude`), et la documentation complète peut être consultée sur la page de la directive.

- **output** configure l'endroit où écrire les journaux.

  Consultez la [directive `log`](/docs/caddyfile/directives/log#output-modules) pour la documentation complète.

- **format** décrit comment encoder, ou formater, les journaux.

  Consultez la [directive `log`](/docs/caddyfile/directives/log#format-modules) pour la documentation complète.

- **level** est le niveau d'entrée minimal à journaliser.

  Par défaut : `INFO`.

  Valeurs possibles : `DEBUG`, `INFO`, `WARN`, `ERROR`, et très rarement, `PANIC`, `FATAL`.

- **include** spécifie les noms de journaux à inclure dans ce logger.

  Par défaut, cette liste est vide (c'est-à-dire que tous les journaux sont inclus).

  Par exemple, pour n'inclure que les journaux émis par l'API d'administration, vous incluriez `admin.api`.

- **exclude** spécifie les noms de journaux à exclure de ce logger.

  Par défaut, cette liste est vide (c'est-à-dire qu'aucun journal n'est exclu).

  Par exemple, pour exclure uniquement les journaux d'accès HTTP, vous excluriez `http.log.access`.

Les noms de loggers que `include` et `exclude` acceptent dépendent des modules utilisés, et le moyen le plus simple de les découvrir est à partir des journaux précédents.

Voici un exemple journalisant en JSON tous les journaux d'accès HTTP et les journaux d'administration vers stdout :

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

<a id="grace-period"></a>
##### `grace_period`
Définit le délai de grâce pour l'arrêt des serveurs HTTP (c'est-à-dire lors des changements de config ou lorsque Caddy s'arrête).

Pendant le délai de grâce, aucune nouvelle connexion n'est acceptée, les connexions inactives sont fermées, et les connexions actives sont attendues impatiemment pour terminer leurs requêtes. Si les clients ne terminent pas leurs requêtes dans le délai de grâce, le serveur sera terminé de force pour permettre au rechargement de se terminer et libérer des ressources. Accepte les [valeurs de durée](/docs/conventions#durations).

Par défaut, le délai de grâce est éternel, ce qui signifie que les connexions ne sont jamais fermées de force.

```caddy
{
	grace_period 10s
}
```


<a id="shutdown-delay"></a>
##### `shutdown_delay`
Définit une [durée](/docs/conventions#durations)
_avant_ le [délai de grâce](#grace_period) pendant laquelle un serveur qui va être arrêté continue de fonctionner normalement, sauf que l'espace réservé `{http.shutting_down}` vaut `true` et `{http.time_until_shutdown}` donne le temps restant avant le début du délai de grâce.

Cela provoque un délai si un serveur est arrêté dans le cadre d'un changement de config, et planifie effectivement le changement pour plus tard. C'est utile pour annoncer aux vérificateurs de santé de ce serveur son arrêt imminent et laisser le temps à un répartiteur de charge de le retirer de la rotation ; par exemple :

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye dans {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Bonjour le monde !"
	}
}
```


## Options TLS

<a id="auto-https"></a>
##### `auto_https`
Configure le [HTTPS automatique](/docs/automatic-https), qui est la fonctionnalité permettant à Caddy d'automatiser la gestion des certificats et les redirections HTTP-vers-HTTPS pour vos sites.

Plusieurs modes sont disponibles :

- `off` : Désactive à la fois l'automatisation des certificats et les redirections HTTP-vers-HTTPS.

- `disable_redirects` : Désactive uniquement les redirections HTTP-vers-HTTPS.

- `disable_certs` : Désactive uniquement l'automatisation des certificats.

- `ignore_loaded_certs` : Automatise les certificats même pour les noms qui apparaissent sur des certificats chargés manuellement. Utile si vous avez spécifié un certificat via la [directive `tls`](/docs/caddyfile/directives/tls) qui contient des noms (ou des caractères génériques) que vous souhaitez plutôt voir gérés automatiquement.

<aside class="tip">

Cette option n'affecte pas le protocole par défaut de Caddy, qui est toujours le HTTPS lorsqu'une adresse de site possède un nom de domaine valide. Cela signifie que `auto_https off` ne fera pas en sorte que votre site soit servi via HTTP, cela désactivera seulement la gestion automatique des certificats et les redirections.

Cela signifie que si vous souhaitez servir votre site via HTTP, vous devez modifier votre [adresse de site](/docs/caddyfile/concepts#addresses) pour qu'elle soit préfixée par `http://` ou suffixée par `:80` (ou l' [option `http_port`](#http_port)).

</aside>

```caddy
{
	auto_https disable_redirects
}
```


<a id="email"></a>
##### `email`
Votre adresse e-mail. Principalement utilisée lors de la création d'un compte ACME auprès de votre autorité de certification, et est fortement recommandée en cas de problèmes avec vos certificats.

<aside class="tip">

Gardez à l'esprit que Let's Encrypt peut vous envoyer des e-mails concernant l'expiration prochaine de votre certificat, mais cela peut être trompeur car Caddy a pu choisir d'utiliser un émetteur différent (ex: ZeroSSL) lors du renouvellement. Vérifiez vos journaux et/ou le certificat lui-même (dans votre navigateur par exemple) pour voir quel émetteur a été utilisé, et que son expiration est toujours valide ; si c'est le cas, vous pouvez ignorer l'e-mail de Let's Encrypt en toute sécurité.

</aside>

```caddy
{
	email admin@example.com
}
```


<a id="default-sni"></a>
##### `default_sni`
Définit un nom de serveur TLS (ServerName) par défaut pour le cas où les clients n'utilisent pas le SNI dans leur ClientHello.

```caddy
{
	default_sni example.com
}
```


<a id="fallback-sni"></a>
##### `fallback_sni`
⚠️ <i>Expérimental</i>

Si configuré, le repli (fallback) devient le nom de serveur TLS dans le ClientHello si le ServerName d'origine ne correspond à aucun certificat dans le cache.

Les utilisations pour cela sont très spécifiques ; typiquement si un client est un CDN et transmet le ServerName de l'échange aval mais peut accepter un certificat avec le nom d'hôte de l'origine à la place, alors vous définiriez ceci comme le nom d'hôte de votre origine. Notez que Caddy doit gérer un certificat pour ce nom.

```caddy
{
	fallback_sni example.com
}
```


<a id="local-certs"></a>
##### `local_certs`
Provoque l'émission en interne par défaut de **tous** les certificats, plutôt que par une autorité de certification ACME (publique) telle que Let's Encrypt. C'est utile comme interrupteur rapide dans les environnements de développement.

```caddy
{
	local_certs
}
```


<a id="skip-install-trust"></a>
##### `skip_install_trust`
Passe les tentatives d'installation de la racine de l'autorité de certification locale dans le magasin de confiance du système, ainsi que dans les magasins de confiance Java et Mozilla Firefox.

```caddy
{
	skip_install_trust
}
```


<a id="acme-ca"></a>
##### `acme_ca`
Spécifie l'URL du répertoire de l'autorité de certification ACME. Il est fortement recommandé de définir ceci sur le [point d'accès staging <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) de Let's Encrypt pour les tests ou le développement. Par défaut : les points d'accès de production de ZeroSSL et Let's Encrypt.

Notez qu'une autorité de certification ACME configurée globalement peut ne pas s'appliquer à tous les sites ; consultez les [prérequis du nom d'hôte](/docs/automatic-https#hostname-requirements) pour l'utilisation de l'émetteur (ou des émetteurs) ACME par défaut.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

<a id="acme-ca-root"></a>
##### `acme_ca_root`
Spécifie un fichier PEM contenant un certificat racine de confiance pour les points d'accès de l'autorité de certification ACME, s'il n'est pas dans le magasin de confiance du système.

```caddy
{
	acme_ca_root /chemin/vers/ca/root.pem
}
```


<a id="acme-eab"></a>
##### `acme_eab`
Spécifie une liaison de compte externe (External Account Binding) à utiliser pour toutes les transactions ACME.

Par exemple, avec des identifiants fictifs de ZeroSSL :

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


<a id="acme-dns"></a>
##### `acme_dns`
Configure le fournisseur du [défi DNS ACME](/docs/automatic-https#dns-challenge) à utiliser pour toutes les transactions ACME.

Nécessite un build personnalisé de Caddy avec un plugin pour votre fournisseur DNS.

Les jetons suivant le nom du fournisseur configurent celui-ci de la même manière que s'il était spécifié dans l' [émetteur `acme` de la directive `tls`](/docs/caddyfile/directives/tls#acme).

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


<a id="dns"></a>
##### `dns`
Configure un fournisseur DNS par défaut à utiliser lorsqu'aucun autre n'est spécifié localement dans un contexte pertinent. Par exemple, si le défi DNS ACME est activé mais ne possède pas de fournisseur DNS configuré, ce défaut global sera utilisé. Il est également appliqué pour la publication des configurations Encrypted ClientHello (ECH).

Votre binaire Caddy doit être compilé avec le module du fournisseur DNS spécifié pour que cela fonctionne.

Exemple, en utilisant des identifiants provenant d'une variable d'environnement :

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Nécessite Caddy 2.10 beta 1 ou plus récent.)


<a id="ech"></a>
##### `ech`
Active le Encrypted ClientHello (ECH) en utilisant le ou les noms de domaine publics spécifiés comme nom de serveur en texte clair (SNI) lors des échanges TLS. Dans les bonnes conditions, l'ECH peut aider à protéger les noms de domaine de vos sites sur le réseau lors des connexions. Caddy générera et publiera une configuration ECH pour chaque nom public spécifié. La publication est la manière dont les clients compatibles (tels que les navigateurs modernes correctement configurés) savent qu'ils doivent utiliser l'ECH pour accéder à vos sites.

Afin de fonctionner correctement, la ou les configurations ECH doivent être publiées d'une manière attendue par les clients. La plupart des navigateurs (avec le DNS-over-HTTPS ou le DNS-over-TLS activé) s'attendent à ce que les configurations ECH soient publiées dans des enregistrements DNS de type HTTPS. Caddy effectue ce type de publication automatiquement, mais vous devez spécifier un fournisseur DNS soit avec la sous-option `dns`, soit globalement avec l' [option globale `dns`](#dns), et votre binaire Caddy doit être construit avec le module du fournisseur DNS spécifié. (Des builds personnalisés sont disponibles sur notre [page de téléchargement](/download).)

**Notes sur la confidentialité :**

- Il est généralement conseillé de **maximiser la taille de votre [_ensemble d'anonymat_](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction)**. À ce titre, nous recommandons typiquement à la plupart des utilisateurs de ne configurer *qu'un seul* nom de domaine public pour protéger tous vos sites.
- **Votre serveur doit faire autorité pour le ou les noms de domaine publics que vous spécifiez** (c'est-à-dire qu'ils doivent pointer vers votre serveur) car Caddy obtiendra un certificat pour eux. Ces certificats sont vitaux pour aider les clients conformes aux spécifications à se connecter de manière fiable et sûre avec l'ECH dans certains cas. Ils sont uniquement utilisés pour faciliter un échange ECH correct, et ne sont pas utilisés pour les données d'application (vos sites — sauf si vous définissez un site qui est le même que votre nom de domaine public).
- Chaque circonstance peut être différente. Nous recommandons de consulter des experts pour **revoir votre modèle de menace** si les enjeux sont élevés, car l'ECH n'est pas une solution universelle.

Exemple utilisant des identifiants provenant d'une variable d'environnement pour la publication vers des serveurs de noms parqués chez Cloudflare :

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Cela devrait faire en sorte que les clients compatibles chargent tous vos sites avec `ech.example.net`, plutôt que les noms de sites individuels exposés en texte clair.

Une publication réussie nécessite que les domaines de votre site soient parqués chez le fournisseur DNS configuré et que les enregistrements puissent être modifiés avec les identifiants / la configuration du fournisseur fournis.

(Nécessite Caddy 2.10 beta 1 ou plus récent.)


<a id="on-demand-tls"></a>
##### `on_demand_tls`
Configure le [TLS à la demande (On-Demand TLS)](/docs/automatic-https#on-demand-tls) là où il est activé, mais ne l'active pas (pour l'activer, utilisez la [sous-directive `on_demand` de la directive `tls`](/docs/caddyfile/directives/tls#syntax)). Requis pour une utilisation en environnements de production, afin de prévenir les abus.

- **ask** fera en sorte que Caddy effectue une requête HTTP vers l'URL indiquée, demandant si un domaine est autorisé à se voir délivrer un certificat.

  La requête possède une chaîne de requête `?domain=` contenant la valeur du nom de domaine.

  Si le point d'accès retourne un code d'état `2xx`, Caddy sera autorisé à obtenir un certificat pour ce nom. Tout autre code d'état entraînera l'annulation de l'émission du certificat et une erreur lors de l'échange TLS.

<aside class="tip">

Le point d'accès ask doit répondre *aussi vite que possible*, en quelques millisecondes idéalement. Typiquement, votre point d'accès devrait effectuer une recherche en temps constant dans une base de données avec un index par nom de domaine ; évitez les boucles. Évitez d'effectuer des requêtes DNS ou d'autres requêtes réseau.

</aside>

- **permission** permet d'utiliser des modules personnalisés pour déterminer si un certificat doit être délivré pour un nom particulier. Le module doit implémenter l' [interface `caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission). Un module de permission `http` est inclus, c'est ce que l'option `ask` utilise, et il reste en tant que raccourci pour la compatibilité descendante.

- ⚠️ Les options de limitation de débit **interval** et **burst** étaient disponibles, mais elles ne sont PAS recommandées. Supprimez-les de votre config si vous les avez encore.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


<a id="key-type"></a>
##### `key_type`
Spécifie le type de clé à générer pour les certificats TLS ; ne changez ceci que si vous avez un besoin spécifique de le personnaliser.

Les valeurs possibles sont : `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


<a id="cert-issuer"></a>
##### `cert_issuer`
Définit l'émetteur (ou la source) des certificats TLS.

Cela permet de configurer les émetteurs globalement, au lieu de le faire par site comme vous le feriez avec la [sous-directive `issuer` de la directive `tls`](/docs/caddyfile/directives/tls#issuer).

Peut être répété si vous souhaitez configurer plus d'un émetteur à essayer. Ils seront essayés dans l'ordre où ils sont définis.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


<a id="renew-interval"></a>
##### `renew_interval`
Fréquence à laquelle tous les certificats chargés et gérés sont scannés pour vérifier leur expiration, et déclencher le renouvellement s'ils sont expirés.

Par défaut : `10m`

```caddy
{
	renew_interval 30m
}
```


<a id="cert-lifetime"></a>
##### `cert_lifetime`
La période de validité à demander à l'autorité de certification pour la délivrance d'un certificat.

Cette valeur est utilisée pour calculer le champ `notAfter` de la commande ACME ; par conséquent, le système doit avoir une horloge raisonnablement synchronisée. NOTE : Toutes les autorités de certification ne supportent pas cela. Vérifiez la documentation ACME de votre autorité de certification pour voir si cela est autorisé et quelles valeurs peuvent être utilisées.

Par défaut : `0` (l'autorité de certification choisit la durée de vie, généralement 90 jours)

⚠️ Ceci est une fonctionnalité expérimentale. Sujette à modification ou suppression.

```caddy
{
	cert_lifetime 30d
}
```


<a id="ocsp-interval"></a>
##### `ocsp_interval`
Fréquence à laquelle vérifier si les [agrafes OCSP <img src="/old/resources/images/external-link.svg" class="external-link">](https://fr.wikipedia.org/wiki/Agrafage_OCSP) ont besoin d'être mises à jour.

Par défaut : `1h`

```caddy
{
	ocsp_interval 2h
}
```


<a id="ocsp-stapling"></a>
##### `ocsp_stapling`
Peut être réglé sur `off` pour désactiver l'agrafage OCSP. Utile dans les environnements où les répondeurs ne sont pas joignables à cause de pare-feux.

```caddy
{
	ocsp_stapling off
}
```

<a id="renewal-window-ratio"></a>
##### `renewal_window_ratio`
Le ratio (entre 0 et 1) de la durée de vie du certificat qui doit rester avant que Caddy ne tente de renouveler le certificat. Par exemple, si un certificat a une durée de vie de 90 jours, et que ce ratio est de `0.3333` (la valeur par défaut), alors Caddy tentera continuellement de renouveler le certificat lorsqu'il lui reste 30 jours ou moins avant son expiration. Peut également être défini par site avec la [sous-directive `renewal_window_ratio` de la directive `tls`](/docs/caddyfile/directives/tls#renewal_window_ratio).

Vous devriez rarement avoir besoin de changer cela, mais cela peut être utile pour renouveler plus tard dans la vie du certificat si votre autorité de certification a un temps de délivrance très long.

Gardez à l'esprit qu'il s'agit d'une suggestion, puisque les émetteurs ACME peuvent implémenter l' [extension ARI](https://datatracker.ietf.org/doc/rfc9773/) qui permet à l'émetteur de dicter une fenêtre dans laquelle le client ACME (Caddy dans ce cas) devrait tenter le renouvellement, et cette fenêtre peut ne pas s'aligner sur ce ratio.

```caddy
{
	renewal_window_ratio 0.1
}
```


<a id="preferred-chains"></a>
##### `preferred_chains`
Si votre autorité de certification fournit plusieurs chaînes de certificats, vous pouvez utiliser cette option pour spécifier quelle chaîne Caddy doit préférer. Définissez l'une des options suivantes :

- **smallest** dira à Caddy de préférer les chaînes ayant le plus petit nombre d'octets.

- **root_common_name** est une liste d'un ou plusieurs noms communs ; Caddy choisira la première chaîne ayant une racine qui correspond à au moins l'un des noms communs spécifiés.

- **any_common_name** est une liste d'un ou plusieurs noms communs ; Caddy choisira la première chaîne ayant un émetteur qui correspond à au moins l'un des noms communs spécifiés.

Notez que spécifier `preferred_chains` comme option globale affectera tous les émetteurs s'il n'y a pas de [config au niveau de l'émetteur qui la surcharge](/docs/caddyfile/directives/tls#acme).

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


## Options du serveur

Personnalise les [serveurs HTTP](/docs/json/apps/http/servers/) avec des paramètres qui s'étendent potentiellement sur plusieurs sites, et ne peuvent donc pas être correctement configurés dans les blocs de site. Ces options affectent l'écouteur/le socket ou d'autres installations sous la couche HTTP.

Peut être spécifiée plus d'une fois avec des valeurs d' `adresse_ecoute` différentes pour configurer différentes options par serveur. Par exemple, `servers :443` s'appliquera uniquement au serveur lié à l'adresse d'écoute `:443`. Omettre l'adresse d'écoute appliquera les options à tout serveur restant.

<aside class="tip">

Utilisez la commande [`caddy adapt`](/docs/command-line#caddy-adapt) pour trouver l'adresse d'écoute des serveurs dans votre Caddyfile.

</aside>


Par exemple, pour configurer différentes options pour les serveurs sur les ports `:80` et `:443`, vous spécifieriez deux blocs `servers` :

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

Lorsque vous utilisez `servers`, cela s'appliquera **uniquement** aux serveurs qui **apparaissent réellement** dans votre Caddyfile (c'est-à-dire qui sont produits par un bloc de site). Rappelez-vous, le [HTTPS automatique](/docs/automatic-https) créera un serveur écoutant sur le port `80` (ou l' [option `http_port`](#http_port)), pour servir les redirections HTTP->HTTPS et pour résoudre le défi HTTP ACME ; cela se produit à l'exécution, c'est-à-dire _après_ que l'adaptateur Caddyfile a appliqué `servers`. En d'autres termes, cela signifie que `servers` **ne s'appliquera pas** à `:80` à moins que vous ne déclariez explicitement un bloc de site tel que `http://` ou `:80`.


<aside class="tip">

Si vous utilisez la [directive `bind`](/docs/caddyfile/directives/bind) ou l' [option globale `default_bind`](/docs/caddyfile/options#default-bind), l' `adresse_ecoute` *DOIT* correspondre à l'adresse de liaison combinée au port du bloc de site, sinon les paramètres ne seront pas appliqués. Par exemple :

```caddy
{
	# Ceci ne correspondra PAS au serveur, l'adresse de liaison est manquante
	servers :8080 {
		name private
	}

	# Ceci fonctionnera car c'est une correspondance exacte
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



<a id="name"></a>
##### `name`

Un nom personnalisé à assigner à ce serveur. Généralement utile pour identifier un serveur par son nom dans les journaux et les métriques. S'il n'est pas défini, Caddy le définira dynamiquement en utilisant un motif `srvX`, où `X` commence à `0` et s'incrémente selon le nombre de serveurs dans la config.

Gardez à l'esprit que seuls les serveurs produits par les blocs de site de votre config verront leurs paramètres appliqués. Le [HTTPS automatique](/docs/automatic-https) crée un serveur `:80` (ou [`http_port`](#http_port)) à l'exécution, donc si vous voulez le renommer, vous aurez besoin d'au moins un bloc de site `http://` vide.

Par exemple :

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```



<a id="listener-wrappers"></a>
##### `listener_wrappers`

Permet de configurer les [enveloppes d'écouteur (listener wrappers)](/docs/json/apps/http/servers/listener_wrappers/), qui peuvent modifier le comportement de l'écouteur de socket. Elles sont appliquées dans l'ordre indiqué.

###### `tls`

L'enveloppe d'écouteur `tls` est une enveloppe d'écouteur factice (no-op) qui marque l'endroit où l'écouteur TLS doit se trouver dans une chaîne d'enveloppes d'écouteur. Elle ne doit être utilisée que si une autre enveloppe d'écouteur doit être placée devant l'échange TLS.

###### `http_redirect`

L'enveloppe [`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) fournit des redirections HTTP->HTTPS pour les connexions qui arrivent sur le port TLS en tant que requête HTTP, en détectant via les premiers octets qu'il ne s'agit pas d'un échange TLS, mais d'une requête HTTP. C'est extrêmement utile lors du service de HTTPS sur un port non standard (autre que `443`), puisque les navigateurs tenteront le HTTP sauf si le schéma est spécifié. Elle doit être placée _avant_ l'enveloppe d'écouteur `tls`. Voici un exemple :

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

L'enveloppe d'écouteur [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) (avant la v2.7.0, elle n'était disponible que via un plugin) active l'analyse du [protocole PROXY](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (popularisé par HAProxy). Elle doit être utilisée _avant_ l'enveloppe d'écouteur `tls` puisqu'elle analyse les données en texte clair au début de la connexion :

Sachez que les métadonnées du protocole PROXY peuvent être appliquées à la connexion avant l'évaluation des sélecteurs ou des [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies). L'adresse IP du pair immédiat sera perdue pour toute évaluation ultérieure.

```caddy-d
proxy_protocol {
	timeout <durée>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <politique>
}
```

- **timeout** spécifie la durée maximale d'attente pour l'en-tête PROXY. Par défaut : `5s`.

- **allow** est une liste de plages CIDR de sources de confiance pour recevoir des en-têtes PROXY. Les sockets Unix sont de confiance par défaut et ne font pas partie de cette option.

- **deny** est une liste de plages CIDR de sources de confiance desquelles rejeter les en-têtes PROXY.

- **fallback_policy** est l'action à entreprendre si l'en-tête PROXY provient d'une adresse qui n'est dans aucune des deux listes allow/deny. La politique de repli par défaut est `ignore`. Les valeurs acceptées pour `fallback_policy` sont :
	- `ignore` : adresse provenant de l'en-tête PROXY, mais accepte la connexion
	- `use` : adresse provenant de l'en-tête PROXY
	- `reject` : rejette la connexion lorsqu'un en-tête PROXY est envoyé
	- `require` : exige que la connexion envoie un en-tête PROXY, rejette s'il est absent
	- `skip` : accepte une connexion sans exiger l'en-tête PROXY.


Par exemple, pour un serveur HTTPS (nécessitant l'enveloppe d'écouteur `tls`) qui accepte les en-têtes PROXY provenant d'une plage d'adresses IP spécifique, et rejette les en-têtes PROXY provenant d'une autre plage, avec un délai d'expiration de 2 secondes :

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


<a id="timeouts"></a>
##### `timeouts`

- **read_body** est une [valeur de durée](/docs/conventions#durations) qui définit le temps autorisé pour une lecture depuis le téléversement d'un client. Régler ceci sur une valeur courte et non nulle peut atténuer les attaques slowloris, mais peut aussi affecter les clients légitimement lents. Par défaut, pas de délai d'expiration.

- **read_header** est une [valeur de durée](/docs/conventions#durations) qui définit le temps autorisé pour une lecture depuis les en-têtes de requête d'un client. Par défaut, pas de délai d'expiration.

- **write** est une [valeur de durée](/docs/conventions#durations) qui définit le temps autorisé pour une écriture vers un client. Notez que régler ceci sur une petite valeur lors du service de fichiers volumineux peut affecter négativement les clients légitimement lents. Par défaut, pas de délai d'expiration.

- **idle** est une [valeur de durée](/docs/conventions#durations) qui définit le temps maximum d'attente pour la prochaine requête lorsque les keep-alives sont activés. Par défaut : 5 minutes pour aider à éviter l'épuisement des ressources.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


<a id="keepalive-interval"></a>
##### `keepalive_interval`

L'intervalle auquel les paquets de maintien de connexion (keepalive) TCP sont envoyés pour garder la connexion vivante à la couche TCP quand aucune autre donnée n'est transmise. Par défaut : `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


<a id="keepalive-idle"></a>
##### `keepalive_idle`

La durée pendant laquelle une connexion doit être inactive avant que des paquets de maintien de connexion TCP ne soient envoyés quand aucune autre donnée n'est transmise. Par défaut : `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


<a id="keepalive-count"></a>
##### `keepalive_count`

Le nombre maximum de paquets de maintien de connexion TCP à envoyer avant de considérer la connexion comme morte. Par défaut : `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


<a id="0rtt"></a>
##### `0rtt`

Par défaut, le 0-RTT (early data) est activé pour les écouteurs QUIC (c'est-à-dire HTTP/3) afin de permettre aux clients d'envoyer des données lors du premier aller-retour de l'échange TLS, ce qui peut améliorer les performances pour les connexions répétées.

Vous pouvez régler ceci sur `off` pour désactiver le 0-RTT pour les écouteurs QUIC. Une raison de désactiver le 0-RTT est si un [sélecteur `remote_ip`](/docs/caddyfile/matchers#remote-ip) est utilisé, ce qui introduit une dépendance sur la vérification de l'adresse distante si le routage se produit avant que l'échange TLS ne soit terminé. Une réponse HTTP 425 est écrite dans ce cas, mais certains clients (navigateurs) peuvent mal se comporter et ne pas effectuer de nouvel essai, désactiver le 0-RTT peut donc garantir que les réponses 425 ne sont pas vues par les utilisateurs, au prix de la perte des bénéfices de performance du 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


<a id="trusted-proxies"></a>
##### `trusted_proxies`

Permet de configurer les plages d'adresses IP (CIDR) des serveurs proxys desquels les requêtes doivent être de confiance. Par défaut, aucun proxy n'est de confiance.

L'activation de cette option fait que les requêtes de confiance voient l'IP _réelle_ du client analysée depuis les en-têtes HTTP (par défaut, `X-Forwarded-For` ; voir [`client_ip_headers`](#client-ip-headers) pour configurer d'autres en-têtes). Si elle est de confiance, l'IP client est ajoutée aux [journaux d'accès](/docs/caddyfile/directives/log), est disponible via l'espace réservé `{client_ip}`, et permet l'utilisation du [sélecteur `client_ip`](/docs/caddyfile/matchers#client-ip). Si la requête ne provient pas d'un proxy de confiance, alors l'IP client est réglée sur l'adresse IP distante de la connexion entrante directe ou sur l'adresse définie par le [protocole PROXY](/docs/caddyfile/options#proxy-protocol) s'il est utilisé. Par défaut, les IPs dans les en-têtes sont analysées de gauche à droite. Voir [`trusted_proxies_strict`](#trusted-proxies-strict) pour modifier ce comportement.

Certains sélecteurs ou gestionnaires peuvent utiliser le statut de confiance de la requête pour prendre des décisions. Par exemple, s'il est de confiance, le gestionnaire [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) proxifiera et augmentera les en-têtes de requête sensibles `X-Forwarded-*`.

Actuellement, seul le module de source d'IP `static` est inclus dans la distribution standard de Caddy, mais cela peut être [étendu](/docs/extending-caddy) avec des plugins pour maintenir une liste dynamique de plages d'IP.


###### `static`

Prend une liste statique (fixe) de plages d'IP (CIDR) à considérer de confiance.

En tant que raccourci, `private_ranges` peut être utilisé pour correspondre à toutes les plages privées IPv4 et IPv6. Cela équivaut à spécifier toutes ces plages : `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

La syntaxe est la suivante :

```caddy-d
trusted_proxies static [private_ranges] <plages...>
```

Voici un exemple complet, faisant confiance à une plage IPv4 d'exemple et une plage IPv6 :

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

<a id="trusted-proxies-strict"></a>
##### `trusted_proxies_strict`

Lorsque [`trusted_proxies`](#trusted-proxies) est activé, les IPs dans les en-têtes (configurés par [`client_ip_headers`](#client-ip-headers)) sont analysées de gauche à droite par défaut. La première adresse IP non fiable trouvée devient l'adresse réelle du client. Depuis la v2.8, vous pouvez opter pour une analyse de droite à gauche de ces en-têtes avec `trusted_proxies_strict`. Par défaut, cette option est désactivée pour des raisons de compatibilité descendante.

Les proxys amont tels que HAProxy, CloudFlare, AWS ALB, CloudFront, etc. ajouteront chaque nouvelle adresse distante de connexion à la droite de `X-Forwarded-For`. Il est recommandé d'activer `trusted_proxies_strict` lorsque vous travaillez avec ceux-ci, car l'adresse IP la plus à gauche peut être usurpée par le client.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

Spécifiquement dans le cas d'AWS ALB, vous voudrez certainement activer cette option. [D'après leur documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15), vous ne pouvez identifier l'IP réelle du client qu'en réglant le mode XFF sur `append`. Cette IP sera ajoutée à la droite de `X-Forwarded-For` et ne peut être extraite en toute sécurité que via `trusted_proxies_strict`.

</aside>

<a id="trusted-proxies-unix"></a>
##### `trusted_proxies_unix`

L'option `trusted_proxies_unix` permet de faire confiance à toutes les connexions provenant de sockets Unix, ce qui est utile quand Caddy se trouve derrière un proxy inverse (éventuellement une autre instance de Caddy) qui se connecte à lui via un socket Unix (c'est-à-dire que la [directive `bind`](/docs/caddyfile/directives/bind) est réglée sur un socket unix). C'est désactivé par défaut.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

<a id="client-ip-headers"></a>
##### `client_ip_headers`

En association avec [`trusted_proxies`](#trusted-proxies), permet de configurer quels en-têtes utiliser pour déterminer l'adresse IP du client. Par défaut, seul `X-Forwarded-For` est pris en compte. Plusieurs champs d'en-tête peuvent être spécifiés, auquel cas la première valeur d'en-tête non vide est utilisée.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


<a id="metrics"></a>
##### `metrics`

Active la collecte de métriques ; nécessaire avant de pouvoir interroger les métriques ou les pousser avec l'OTLP. Notez que les métriques réduisent les performances sur les serveurs très sollicités. (Notre communauté travaille à améliorer cela. N'hésitez pas à vous impliquer !)

```caddy
{
	metrics
}
```

Vous pouvez ajouter l'option `per_host` pour étiqueter les métriques avec le nom d'hôte de la métrique.

```caddy
{
	metrics {
		per_host
	}
}
```

En raison du risque de cardinalité infinie lié à l'observation de tous les hôtes possibles pouvant être envoyés par les clients, Caddy n'enregistrera les métriques que pour les hôtes configurés, tandis que tous les autres hôtes (ex: attacker.com) sont agrégés sous l'étiquette "_other". Pour forcer l'observation de tous les hôtes, et là où le risque de cardinalité infinie est acceptable, vous pouvez ajouter `observe_catchall_hosts`. Notez que l'ajout de `observe_catchall_hosts` n'activera pas `per_host`. Cependant, ceci est automatiquement activé pour les serveurs HTTPS (puisque les certificats offrent une certaine protection contre la cardinalité non bornée), mais désactivé par défaut pour les serveurs HTTP afin de prévenir les attaques de cardinalité provenant d'en-têtes Host arbitraires.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Vous pouvez ajouter l'option `otlp` pour pousser les mêmes métriques vers un point d'accès au protocole OpenTelemetry (OTLP). L'exportateur est configuré par les variables d'environnement standard OpenTelemetry `OTEL_*`, telles que `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` et `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Par exemple :

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Consultez [Surveiller Caddy avec des métriques](/docs/metrics) pour plus de détails.

<a id="trace"></a>
##### `trace`

Journalise chaque gestionnaire individuel qui est invoqué. Nécessite que le journal soit émis au niveau `DEBUG` (vous pouvez le faire avec l' [option globale `debug`](#debug)).

NOTE : Cela peut journaliser la configuration de vos modules de gestionnaire HTTP ; n'activez pas ceci dans des contextes non sécurisés lorsqu'il y a des données sensibles dans la configuration.

⚠️ Ceci est une fonctionnalité expérimentale. Sujette à modification ou suppression.

```caddy
{
	servers {
		trace
	}
}
```


<a id="max-header-size"></a>
##### `max_header_size`

La taille maximale à analyser depuis les en-têtes de requête HTTP d'un client. Si la limite est dépassée, le serveur répondra avec le statut HTTP `431 Request Header Fields Too Large`. Accepte tous les formats supportés par [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Par défaut, la limite est de `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


<a id="enable-full-duplex"></a>
##### `enable_full_duplex`

Active la communication en duplex intégral (full-duplex) pour les requêtes HTTP/1.

Pour les requêtes HTTP/1, le serveur HTTP de Go consomme par défaut toute partie non lue du corps de la requête avant de commencer à écrire la réponse, empêchant les gestionnaires de lire la requête et d'écrire la réponse de manière concurrente. L'activation de cette option désactive ce comportement et permet aux gestionnaires de continuer à lire la requête tout en écrivant la réponse.

Pour les requêtes HTTP/2+, le serveur HTTP de Go autorise toujours les lectures et réponses concurrentes, cette option n'a donc aucun effet.

Testez minutieusement avec vos clients HTTP, car certains clients plus anciens peuvent ne pas supporter le HTTP/1 en duplex intégral, ce qui peut provoquer un blocage (deadlock). Consultez [golang/go#57786](https://github.com/golang/go/issues/57786) pour plus d'infos.

⚠️ Ceci est une fonctionnalité expérimentale. Sujette à modification ou suppression.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


<a id="log-credentials"></a>
##### `log_credentials`

Par défaut, les journaux d'accès (activés avec la [directive `log`](/docs/caddyfile/directives/log)) possédant des en-têtes contenant des informations potentiellement sensibles (`Cookie`, `Set-Cookie`, `Authorization` et `Proxy-Authorization`) seront journalisés en tant que `REDACTED`.

Si vous souhaitez que ces en-têtes ne soient *pas* masqués, vous pouvez activer l'option `log_credentials`.

```caddy
{
	servers {
		log_credentials
	}
}
```



<a id="protocols"></a>
##### `protocols`

La liste séparée par des espaces des protocoles HTTP à supporter.

Par défaut : `h1 h2 h3`

Les valeurs acceptées sont :
- `h1` pour HTTP/1.1
- `h2` pour HTTP/2
- `h2c` pour HTTP/2 en texte clair
- `h3` pour HTTP/3

Actuellement, l'activation du HTTP/2 (incluant le H2C) implique nécessairement l'activation du HTTP/1.1 car la bibliothèque standard Go ne nous permet pas de désactiver le HTTP/1.1 lors de l'utilisation de son serveur HTTP. Cependant, soit le HTTP/1.1, soit le HTTP/3 peuvent être activés indépendamment.

Notez que le H2C ("HTTP/2 en texte clair" ou "H2 sur TCP") et le HTTP/3 ne sont pas implémentés par la bibliothèque standard Go, certaines fonctionnalités peuvent donc être limitées. Nous recommandons de ne pas activer le H2C à moins que ce ne soit absolument nécessaire pour votre application.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



<a id="strict-sni-host"></a>
##### `strict_sni_host`

L'activation de cette option exige que l'en-tête `Host` d'une requête corresponde à la valeur du `ServerName` envoyé par le ClientHello TLS du client, une sauvegarde nécessaire lors de l'utilisation de l'authentification client TLS. En cas de non-correspondance, une réponse avec le statut HTTP `421 Misdirected Request` est renvoyée au client.

Cette option sera automatiquement activée si l' [authentification client](/docs/caddyfile/directives/tls#client_auth) est configurée. Cela interdit le contournement de l'authentification client TLS (domain fronting) qui pourrait autrement être exploité en envoyant une valeur SNI non protégée lors d'un échange TLS, puis en mettant un domaine protégé dans l'en-tête Host après avoir établi la connexion. Ce comportement est un défaut sûr, mais vous pouvez l'éteindre explicitement avec `insecure_off` ; par exemple dans le cas d'un proxy où le domain fronting est souhaité et que l'accès n'est pas restreint selon le nom d'hôte.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



## Systèmes de fichiers

<a id="filesystem"></a>
L'option globale `filesystem` permet de déclarer un ou plusieurs systèmes de fichiers pouvant être utilisés pour les E/S fichiers.

Cela pourrait vous permettre de vous connecter à un système de fichiers distant tournant dans le cloud, ou à une base de données avec une interface de type fichier, ou même de lire des fichiers intégrés dans le binaire Caddy.

Les systèmes de fichiers sont déclarés avec un nom pour les identifier. Cela signifie que vous pouvez vous connecter à plus d'un système de fichiers du même type, si nécessaire.

Par défaut, Caddy ne possède aucun module de système de fichiers, vous devrez donc construire Caddy avec un plugin pour le système de fichiers que vous souhaitez utiliser.

#### Exemple

En utilisant un module imaginaire de système de fichiers `perso`, vous pourriez déclarer deux systèmes de fichiers :

```caddy
{
	filesystem foo perso {
		...
	}

	filesystem bar perso {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



## Options PKI

L'application PKI (Public Key Infrastructure) est la fondation des fonctionnalités de [HTTPS local](/docs/automatic-https#local-https) et de [serveur ACME](/docs/caddyfile/directives/acme_server) de Caddy. L'application définit des autorités de certification (CAs) capables de signer des certificats.

L'ID de l'autorité de certification par défaut est `local`. Si l'ID est omis lors de la configuration de la `ca`, alors `local` est supposé par défaut.

<a id="name-1"></a>
##### `name`
Le nom de l'autorité de certification tel qu'affiché à l'utilisateur.

Par défaut : `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "Ma CA locale"
		}
	}
}
```

<a id="root-cn"></a>
##### `root_cn`
Le nom à mettre dans le champ CommonName du certificat racine.

Par défaut : `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "Ma CA locale - 2024 ECC Root"
		}
	}
}
```

<a id="intermediate-cn"></a>
##### `intermediate_cn`
Le nom à mettre dans le champ CommonName des certificats intermédiaires.

Par défaut : `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "Ma CA locale - ECC Intermediate"
		}
	}
}
```

<a id="intermediate-lifetime"></a>
##### `intermediate_lifetime`
La [durée](/docs/conventions#durations) de validité des certificats intermédiaires. Cette valeur **doit** être inférieure à la durée de vie du certificat racine (`3600d` ou 10 ans).

Par défaut : `7d`. Il n'est *pas recommandé* de changer ceci, sauf si c'est absolument nécessaire.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

<a id="maintenance-interval"></a>
##### `maintenance_interval`
La [durée](/docs/conventions#durations) de la fréquence de vérification du besoin de renouvellement des certificats intermédiaires (et racine, le cas échéant).

Par défaut : `10m`. Il n'est *pas recommandé* de changer ceci, sauf si c'est absolument nécessaire.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

<a id="renewal-window-ratio-1"></a>
##### `renewal_window_ratio`
Le ratio (entre 0 et 1) de la durée de vie du certificat qui doit rester avant que Caddy ne tente de renouveler les certificats. Par exemple, si un certificat a une durée de vie de 1 an, et que ce ratio est de `0.2` (la valeur par défaut), alors Caddy tentera continuellement de renouveler le certificat lorsqu'il lui reste 73 jours ou moins avant l'expiration.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


<a id="root"></a>
##### `root`
Une paire de clés (certificat et clé privée) à utiliser comme racine pour l'autorité de certification. Si non spécifiée, une sera générée et gérée automatiquement.

- **format** est le format dans lequel le certificat et la clé privée sont fournis. Actuellement, seul `pem_file` est supporté, ce qui est le défaut, ce champ est donc optionnel.
- **cert** est le certificat. Il doit s'agir du chemin vers un fichier PEM, lors de l'utilisation du format `pem_file`.
- **key** est la clé privée. Il doit s'agir du chemin vers un fichier PEM, lors de l'utilisation du format `pem_file`.

<a id="intermediate"></a>
##### `intermediate`
Une paire de clés (certificat et clé privée) à utiliser comme intermédiaire pour l'autorité de certification. Si non spécifiée, une sera générée et gérée automatiquement.

- **format** est le format dans lequel le certificat et la clé privée sont fournis. Actuellement, seul `pem_file` est supporté, ce qui est le défaut, ce champ est donc optionnel.
- **cert** est le certificat. Il doit s'agir du chemin vers un fichier PEM, lors de l'utilisation du format `pem_file`.
- **key** est la clé privée. Il doit s'agir du chemin vers un fichier PEM, lors de l'utilisation du format `pem_file`.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /chemin/vers/root.pem
				key /chemin/vers/root.key
			}
			intermediate {
				format pem_file
				cert /chemin/vers/intermediate.pem
				key /chemin/vers/intermediate.key
			}
		}
	}
}
```


## Options d'événements

<a id="events"></a>
Les modules Caddy émettent des événements lorsque des choses intéressantes se produisent (ou sont sur le point de se produire).

Les événements incluent typiquement une charge utile de métadonnées. La meilleure façon de découvrir les événements et leurs charges utiles est de consulter la documentation de chaque module, mais vous pouvez également voir les événements et leurs charges utiles de données en activant l' [option globale `debug`](#debug) et en lisant les journaux.

<a id="on"></a>
##### `on`

Lie un gestionnaire d'événement à l'événement nommé. Spécifiez le nom du module de gestionnaire d'événement, suivi de sa configuration.

Par exemple, pour lancer une commande après l'obtention d'un certificat (nécessite un [plugin tiers <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec)), avec une partie de la charge utile de l'événement passée au script en utilisant un espace réservé :

```caddy
{
	events {
		on cert_obtained exec ./mon-script.sh {event.data.certificate_path}
	}
}
```

### Événements

Ces événements standard sont émis par Caddy :

- [événements `tls` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [événements `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#events)

Des plugins peuvent également émettre des événements, vérifiez donc leur documentation pour les détails.
