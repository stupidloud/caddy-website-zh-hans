---
title: forward_auth (directive Caddyfile)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.innerText.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Fix uri subdirective, gets parsed as matcher arg because of "uri" directive
	$$_('.k').forEach(item => {
		if (item.innerText.includes('uri') && item.nextElementSibling && item.nextElementSibling.classList.contains('nd')) {
			const next = item.nextElementSibling;
			next.classList.remove('nd');
			next.classList.add('s');
			next.textContent = next.textContent;
		}
	});
});
</script>

# forward_auth

Une directive pré-configurée qui proxifie un clone de la requête vers une passerelle d'authentification, laquelle peut décider si le traitement doit continuer, ou s'il doit être envoyé vers une page de connexion.

- [Syntaxe](#syntax)
- [Forme étendue](#expanded-form)
- [Exemples](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Le [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) de Caddy est capable d'effectuer des "requêtes de pré-vérification" vers un service externe, mais cette directive est conçue spécifiquement pour le cas d'utilisation de l'authentification. Cette directive n'est en réalité qu'un moyen pratique d'utiliser une configuration plus longue et plus courante (ci-dessous).

Cette directive effectue une requête `GET` vers l'amont configuré avec l' `uri` réécrite :
- Si l'amont répond avec un code d'état `2xx`, alors l'accès est accordé et les champs d'en-tête de `copy_headers` sont copiés vers la requête originale, et le traitement continue.
- Sinon, si l'amont répond avec n'importe quel autre code d'état, alors la réponse de l'amont est copiée en retour vers le client. Cette réponse devrait typiquement impliquer une redirection vers la page de connexion de la passerelle d'authentification.

Si ce comportement n'est pas exactement ce que vous souhaitez, vous pouvez prendre la [forme étendue](#expanded-form) ci-dessous comme base et la personnaliser selon vos besoins.

Toutes les sous-directives de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) sont supportées, et transmises au gestionnaire `reverse_proxy` sous-jacent.


<a id="syntax"></a>
## Syntaxe

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <vers>
	copy_headers <champs...> {
		<champs...>
	}
}
```

- **&lt;upstreams...&gt;** est une liste de serveurs d'amont (backends) vers lesquels envoyer les requêtes d'authentification.

- **uri** est l'URI (chemin et requête) à définir sur la requête envoyée vers l'amont. Ce sera généralement le point d'accès de vérification de la passerelle d'authentification.

- **copy_headers** est une liste de champs d'en-tête HTTP à copier depuis la réponse vers la requête originale, lorsque la requête possède un code d'état de succès.

  Le champ peut être renommé en utilisant `>` suivi du nouveau nom, par exemple `Ancien>Nouveau`.

  Un bloc peut être utilisé pour lister tous les champs, un par ligne, si vous préférez pour la lisibilité.

Puisque cette directive est une enveloppe pré-configurée autour d'un reverse proxy, vous pouvez utiliser n'importe quelle sous-directive de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) pour la personnaliser.


<a id="expanded-form"></a>
## Forme étendue

La directive `forward_auth` est identique à la configuration suivante. Les passerelles d'authentification comme [Authelia](https://www.authelia.com/) fonctionnent bien avec ce préréglage. Si la vôtre ne le fait pas, n'hésitez pas à vous inspirer de ceci et à le personnaliser selon vos besoins au lieu d'utiliser le raccourci `forward_auth`.

```caddy-d
reverse_proxy <upstreams...> {
	# Toujours GET, afin que le corps de la
	# requête entrante ne soit pas consommé
	method GET

	# Changer l'URI vers le point d'accès de
	# vérification de la passerelle d'auth
	rewrite <to>

	# Transmettre la méthode et l'URI originales,
	# puisqu'elles sont réécrites ci-dessus ; ceci
	# s'ajoute aux autres en-têtes X-Forwarded-*
	# déjà définis par reverse_proxy
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# Sur une réponse de succès, copier les en-têtes de réponse
	@good status 2xx
	handle_response @good {
		# par exemple, pour chaque champ copy_headers...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## Exemples


<a id="authelia"></a>
### Authelia

Délégation de l'authentification à [Authelia](https://www.authelia.com/), avant de servir votre application via un proxy inverse :

```caddy
# Servir la passerelle d'authentification elle-même
auth.example.com {
	reverse_proxy authelia:9091
}

# Servir votre application
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

Pour plus d'informations, consultez la [documentation d'Authelia](https://www.authelia.com/integration/proxies/caddy/) pour l'intégration avec Caddy.


<a id="tailscale"></a>
### Tailscale

Délégation de l'authentification à [Tailscale](https://tailscale.com/) (actuellement nommé [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/), mais cela fonctionne toujours avec Caddy), et utilisation de la syntaxe alternative pour `copy_headers` afin de *renommer* les en-têtes copiés (notez le `>` dans chaque en-tête) :

```caddy-d
forward_auth unix//run/tailscale.nginx-auth.sock {
	uri /auth
	header_up Remote-Addr {remote_host}
	header_up Remote-Port {remote_port}
	header_up Original-URI {uri}
	copy_headers {
		Tailscale-User>X-Webauth-User
		Tailscale-Name>X-Webauth-Name
		Tailscale-Login>X-Webauth-Login
		Tailscale-Tailnet>X-Webauth-Tailnet
		Tailscale-Profile-Picture>X-Webauth-Profile-Picture
	}
}
```
