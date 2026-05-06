---
title: acme_server (directive Caddyfile)
---

# acme_server

Un gestionnaire de serveur utilisant le protocole [ACME](https://tools.ietf.org/html/rfc8555) intégré. Cela permet à une instance Caddy de délivrer des certificats pour n'importe quel autre logiciel compatible ACME (y compris d'autres instances Caddy).

Lorsqu'il est activé, les requêtes correspondant au chemin `/acme/*` seront traitées par le serveur ACME.


## Configuration client

En utilisant les paramètres par défaut du serveur ACME, les clients ACME doivent simplement être configurés pour utiliser `https://localhost/acme/local/directory` comme point d'accès ACME. (`local` est l'ID de l'autorité de certification par défaut de Caddy.)


## Syntaxe

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <durée>
	resolvers  <solveurs...>
	challenges <défis...>
	allow_wildcard_names
	allow {
		domains <domaines...>
		ip_ranges <adresses...>
	}
	deny {
		domains <domaines...>
		ip_ranges <adresses...>
	}
}
```

- **ca** spécifie l'identifiant (ID) de l'autorité de certification avec laquelle signer les certificats. Par défaut, il s'agit de `local`, qui est l'autorité de certification par défaut de Caddy, destinée aux certificats auto-signés utilisés localement, ce qui est courant dans les environnements de développement. Pour une utilisation plus large, il est recommandé de spécifier une autorité de certification différente pour éviter toute confusion. Si l'autorité de certification avec l'ID donné n'existe pas déjà, elle sera créée. Consultez les [options globales de l'application PKI](/docs/caddyfile/options#pki-options) pour configurer d'autres autorités de certification.

- **lifetime** (Par défaut : `12h`) est une [durée](/docs/conventions#durations) qui spécifie la période de validité des certificats délivrés. Cette valeur doit être inférieure à la durée de vie du [certificat intermédiaire](/docs/caddyfile/options#intermediate-lifetime) utilisé pour la signature. Il n'est pas recommandé de changer cela sauf si c'est absolument nécessaire.

- **resolvers** sont les adresses des résolveurs DNS à utiliser lors de la recherche des enregistrements TXT pour résoudre les défis DNS ACME. Accepte les [adresses réseau](/docs/conventions#network-addresses) utilisant par défaut l'UDP et le port 53, sauf indication contraire. Si l'hôte est une adresse IP, elle sera contactée directement pour résoudre le serveur amont. Si l'hôte n'est pas une adresse IP, les adresses sont résolues en utilisant la [convention de résolution de noms](https://golang.org/pkg/net/#hdr-Name_Resolution) de la bibliothèque standard Go. Si plusieurs résolveurs sont spécifiés, l'un d'eux est choisi au hasard.

- **challenges** définit les types de défis activés. S'il n'est pas défini ou si la directive est utilisée sans valeurs, tous les types de défis sont activés. Les valeurs acceptées sont : http-01, tls-alpn-01, dns-01.

- **allow_wildcard_names** active la délivrance de certificats avec des SAN (Subject Alternative Name) génériques (wildcard).

- **allow**, **deny** configurent la politique opérationnelle de l' `acme_server`. L'évaluation de la politique suit les critères décrits par Step-CA [ici](https://smallstep.com/docs/step-ca/policies/#policy-evaluation).

	- **domains** définit les noms de domaine des sujets à autoriser ou à refuser selon les critères d'évaluation de la politique.

	- **ip_ranges** définit les plages d'adresses IP des sujets à autoriser ou à refuser selon les critères d'évaluation de la politique.

## Exemples

Pour servir un serveur ACME avec l'ID `home` sur le domaine `acme.exemple.com`, avec l'autorité de certification personnalisée via l' [option globale `pki`](/docs/caddyfile/options#pki-options), et délivrant son propre certificat en utilisant l'émetteur `internal` :

```caddy
{
	pki {
		ca home {
			name "Ma CA domestique"
		}
	}
}

acme.exemple.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

Si vous avez un autre serveur Caddy, il peut utiliser le serveur ACME ci-dessus pour délivrer ses propres certificats :

```caddy
{
	acme_ca https://acme.exemple.com/acme/home/directory
	acme_ca_root /chemin/vers/home_ca_root.crt
}

exemple.com {
	respond "Bonjour le monde !"
}
```
