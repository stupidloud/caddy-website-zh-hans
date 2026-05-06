---
title: tls (directive Caddyfile)
---

<script>
ready(function() {
	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# tls

Configure le TLS pour le site.

**Les paramètres TLS par défaut de Caddy sont sûrs. Ne modifiez ces paramètres que si vous avez une bonne raison et comprenez les implications.** L'usage le plus courant de cette directive est de spécifier une adresse e-mail de compte ACME, de changer le point d'accès de l'autorité de certification ACME, ou de fournir vos propres certificats.

Note de compatibilité : En raison de sa nature sensible en tant que protocole de sécurité, des ajustements délibérés des défauts TLS peuvent être effectués dans de nouvelles versions mineures ou de correctifs. Les versions TLS, algorithmes de chiffrement (ciphers), fonctionnalités, etc. anciens ou cassés peuvent être supprimés à tout moment. Si votre déploiement est extrêmement sensible aux changements, vous devriez spécifier explicitement les valeurs qui doivent rester constantes, et être vigilant lors des mises à jour. Dans presque tous les cas, nous recommandons d'utiliser les paramètres par défaut.


## Syntaxe

```caddy-d
tls [internal|force_automate|<email>] | [<fichier_cert> <fichier_clé>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groupes...>
	alpn      <valeurs...>
	load      <chemins...>
	ca        <ca_dir_url>
	ca_root   <fichier_pem>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <nom_fournisseur> [<params...>]
	propagation_timeout <durée>
	propagation_delay   <durée>
	dns_ttl             <durée>
	dns_challenge_override_domain <domaine>
	resolvers <serveurs_dns...>
	eab       <id_clé> <clé_mac>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <nom_émetteur>  [<params...>]
	get_certificate <nom_gestionnaire> [<params...>]
	insecure_secrets_log <fichier_log>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** signifie utiliser l'autorité de certification (CA) interne de Caddy, de confiance locale, pour produire des certificats pour ce site. Pour configurer davantage l'émetteur [`internal`](#internal), utilisez la sous-directive [`issuer`](#issuer).

- **force_automate** force Caddy à automatiser les certificats pour le site, même si d'autres certificats gérés s'appliquent.

- **&lt;email&gt;** est l'adresse e-mail à utiliser pour le compte ACME gérant les certificats du site. Vous pourriez préférer utiliser l' [option globale `email`](/docs/caddyfile/options#email) à la place, pour configurer cela pour tous vos sites en une fois.

<aside class="tip">

Gardez à l'esprit que Let's Encrypt peut vous envoyer des e-mails concernant l'expiration prochaine de votre certificat, mais cela peut être trompeur car Caddy a pu choisir d'utiliser un émetteur différent (ex: ZeroSSL) lors du renouvellement. Vérifiez vos journaux et/ou le certificat lui-même (dans votre navigateur par exemple) pour voir quel émetteur a été utilisé, et que son expiration est toujours valide ; si c'est le cas, vous pouvez ignorer l'e-mail de Let's Encrypt en toute sécurité.

</aside>

- **&lt;fichier_cert&gt;** et **&lt;fichier_clé&gt;** sont les chemins vers les fichiers PEM du certificat et de la clé privée. En spécifier un seul est invalide.

- **protocols** <span id="protocols"/> spécifie les versions minimale et maximale du protocole. NE changez PAS ceci à moins de savoir ce que vous faites. Configurer ceci est rarement nécessaire, car Caddy utilisera toujours des défauts modernes.
  
  Min par défaut : `tls1.2`, Max par défaut : `tls1.3`

- **ciphers** <span id="ciphers"/> spécifie la liste des noms de suites de chiffrement par ordre de préférence décroissant. NE changez PAS ceci à moins de savoir ce que vous faites. Notez que les suites de chiffrement ne sont pas personnalisables pour TLS 1.3 ; et tous les algorithmes TLS 1.2 ne sont pas activés par défaut. Les noms supportés sont (par ordre de préférence de la bibliothèque standard Go) :
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> spécifie la liste des groupes EC (Elliptic Curve) à supporter. Il est recommandé de ne pas changer les défauts. Les valeurs supportées sont :
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> est la liste des valeurs à annoncer dans l' [extension ALPN <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) de l'échange TLS.

- **load** <span id="load"/> spécifie une liste de dossiers à partir desquels charger des fichiers PEM qui sont des lots certificat+clé.

- **ca** <span id="ca"/> modifie le point d'accès de l'autorité de certification ACME. Ceci est le plus souvent utilisé pour définir le [point d'accès staging de Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) lors de tests, ou un serveur ACME interne. (Pour changer cette valeur pour l'ensemble du Caddyfile, utilisez l' [option globale `acme_ca`](/docs/caddyfile/options) à la place.)

- **ca_root** <span id="ca_root"/> spécifie un fichier PEM contenant un certificat racine de confiance pour le point d'accès de l'autorité de certification ACME, s'il n'est pas dans le magasin de confiance du système.

- **key_type** <span id="key_type"/> est le type de clé à utiliser lors de la génération des CSR (Certificate Signing Request). Ne définissez ceci que si vous avez un besoin spécifique.

- **dns** <span id="dns"/> active le [défi DNS](/docs/automatic-https#dns-challenge) en utilisant le plugin de fournisseur spécifié, lequel doit être ajouté depuis l'un des dépôts [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Chaque plugin de fournisseur peut avoir sa propre syntaxe suivant son nom ; reportez-vous à leur documentation pour les détails. Le maintien du support pour chaque fournisseur DNS est un effort communautaire. [Apprenez comment activer le défi DNS pour votre fournisseur sur notre wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit le temps maximum d'attente pour que les enregistrements DNS TXT apparaissent lors de l'utilisation du défi DNS. Réglez sur `-1` pour désactiver les vérifications de propagation. Par défaut : 2 minutes.

- **propagation_delay** <span id="propagation_delay"/> est une [valeur de durée](/docs/conventions#durations) qui définit combien de temps attendre avant de commencer les vérifications de propagation des enregistrements DNS TXT lors de l'utilisation du défi DNS. Par défaut : `0` (pas d'attente).

- **dns_ttl** <span id="dns_ttl"/> est une [valeur de durée](/docs/conventions#durations) qui définit le TTL de l'enregistrement `TXT` utilisé pour le défi DNS. Rarement nécessaire.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> surcharge le domaine à utiliser pour le défi DNS. Ceci permet de déléguer le défi à un domaine différent.

  Vous pourriez vouloir utiliser ceci si le fournisseur DNS de votre domaine principal ne possède pas de [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) disponible. Vous pouvez à la place ajouter un enregistrement `CNAME` avec le sous-domaine `_acme-challenge` sur votre domaine principal, pointant vers un domaine secondaire pour lequel vous *possédez* un plugin. Cette option *ne nécessite pas* de support spécial de la part du plugin.
  
  Lorsque les émetteurs ACME tenteront de résoudre le défi DNS pour votre domaine principal, ils suivront alors le `CNAME` vers votre domaine secondaire pour trouver l'enregistrement `TXT`.

  **Note :** Utilisez le nom canonique complet de l'enregistrement CNAME comme valeur ici — le sous-domaine `_acme-challenge` ne sera pas préfixé automatiquement.

- **resolvers** <span id="resolvers"/> personnalise les résolveurs DNS utilisés lors de l'exécution du défi DNS ; ceux-ci ont la priorité sur les résolveurs du système ou n'importe quel résolveur par défaut. S'ils sont définis ici, les résolveurs seront propagés vers tous les émetteurs de certificats configurés.

  Il s'agit typiquement d'une liste d'adresses IP. Par exemple, pour utiliser [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) :

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> configure l'ACME external account binding (EAB) pour ce site, en utilisant l'ID de clé et la clé MAC fournis par votre autorité de certification.

- **on_demand** <span id="on_demand"/> active le [TLS à la demande (On-Demand TLS)](/docs/automatic-https#on-demand-tls) pour les noms d'hôte donnés dans la ou les adresses du bloc de site. **Avertissement de sécurité :** Faire cela en production est dangereux à moins que vous ne configuriez également l' [option globale `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) pour atténuer les abus.

- **reuse_private_keys** <span id="reuse_private_keys"/> active la réutilisation des clés privées lors du renouvellement des certificats. Par défaut, une nouvelle clé est créée pour chaque nouveau certificat afin de limiter le "pinning" et réduire la portée d'une compromission de clé. Le "key pinning" va à l'encontre des meilleures pratiques de l'industrie. Cette option n'est pas recommandée à moins que vous n'ayez une raison spécifique de l'utiliser ; elle pourrait être supprimée dans une version future.

- **client_auth** <span id="client_auth"/> active et configure l'authentification client TLS :
  - **mode** <span id="mode"/> est le mode d'authentification du client. Les valeurs autorisées sont :

    | Mode | Description |
    | --- | --- |
    | request | Demande un certificat aux clients, mais autorise même s'il n'y en a pas ; ne le vérifie pas |
    | require | Exige que les clients présentent un certificat, mais ne le vérifie pas |
    | verify_if_given | Demande un certificat aux clients ; autorise même s'il n'y en a pas, mais le vérifie s'il y en a un |
    | require_and_verify | Exige que les clients présentent un certificat valide qui est vérifié |

    Par défaut : `require_and_verify` si un module `trust_pool` est fourni ; sinon, `require`.
	
  - **trust_pool** <span id="trust_pool"/> configure la source des autorités de certification (CA) fournissant les certificats par rapport auxquels valider les certificats clients.
	
	L'autorité de certification utilisée fournissant le pool de certificats de confiance et la configuration au sein du segment dépendent du module de source de pool de confiance configuré. Les modules standard disponibles dans Caddy sont [listés ci-dessous](#trust-pool-providers). La liste complète des modules, y compris tiers, est listée dans la [documentation JSON `trust_pool`](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Plusieurs directives `trusted_*` peuvent être utilisées pour spécifier plusieurs certificats CA ou finaux (leaf). Les certificats clients qui ne sont pas listés comme l'un des certificats finaux ou signés par l'une des autorités spécifiées seront rejetés selon le **mode**.

  - **verifier** <span id="verifier"/> active l'utilisation d'un module de vérificateur de certificat client personnalisé. Ceux-ci peuvent effectuer des vérifications d'authentification client personnalisées, comme s'assurer que le certificat n'est pas révoqué.

- **issuer** <span id="issuer"/> configure un émetteur de certificat personnalisé, ou une source à partir de laquelle obtenir des certificats.

  L'émetteur utilisé et les options qui suivent dans ce segment dépendent des [modules d'émetteurs](#issuers) disponibles. Certaines des autres sous-directives telles que `ca` et `dns` sont en réalité des raccourcis pour configurer l'émetteur `acme` (et cette sous-directive a été ajoutée plus tard), ainsi spécifier cette directive avec certaines des autres est confus et donc interdit.
  
  Cette sous-directive peut être spécifiée plusieurs fois pour configureer plusieurs émetteurs redondants ; si l'un échoue à délivrer un certificat, le suivant sera essayé.

- **get_certificate** <span id="get_certificate"/> permet d'obtenir des certificats auprès d'un [module de gestionnaire](#certificate-managers) au moment de l'échange TLS.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> active la journalisation des secrets TLS vers un fichier. Ceci est également connu sous le nom de `SSLKEYLOGFILE`. Utilise le format de journal de clés NSS, lequel peut ensuite être analysé par Wireshark ou d'autres outils. ⚠️ **Avertissement de sécurité :** Ceci est dangereux car cela permet à d'autres programmes ou outils de déchiffrer vos connexions TLS, et compromet donc totalement la sécurité. Cependant, cette capacité peut être utile pour le débogage et le dépannage.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> est un ratio entre 0 et 1 qui détermine la durée de vie restante du certificat avant que Caddy ne tente de le renouveler. Par exemple, si un certificat a une durée de vie de 90 jours, et que ce ratio est de `0.3333` (la valeur par défaut), alors Caddy tentera continuellement de renouveler le certificat lorsqu'il lui reste 30 jours ou moins avant l'expiration. Peut également être défini globalement avec l' [option globale `renewal_window_ratio`](/docs/caddyfile/options#renewal-window-ratio).

  Vous devriez rarement avoir besoin de changer cela, mais cela peut être utile pour renouveler plus tard dans la vie du certificat si votre autorité de certification a un temps de délivrance très long.

  Gardez à l'esprit qu'il s'agit d'une suggestion puisque les émetteurs ACME peuvent implémenter l' [extension ARI](https://datatracker.ietf.org/doc/rfc9773/). L'ARI dicte une fenêtre dans laquelle le client ACME (Caddy dans ce cas) devrait tenter le renouvellement, et cette fenêtre peut ne pas s'aligner sur ce ratio.

- **force_automate** est identique à la spécification en ligne (voir ci-dessus).

### Fournisseurs de pool de confiance (Trust Pool Providers)

Voici les fournisseurs de pool de confiance standard pouvant être utilisés dans la sous-directive `trust_pool` :

#### inline

Le module `inline` analyse les certificats racines de confiance listés directement dans le Caddyfile au format DER encodé en base64. La directive `trust_der` peut être répétée plusieurs fois.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> est un certificat d'autorité de confiance encodé en base64 DER par rapport auquel valider les certificats clients.

#### file

Le module `file` lit les certificats racines de confiance à partir de fichiers PEM sur le disque. La directive `pem_file` peut accepter plusieurs chemins de fichiers sur la même ligne et peut être répétée plusieurs fois.

```caddy-d
... file [<fichier_pem>...] {
	pem_file <fichier_pem>...
}
```

- **pem_file** <span id="pem_file"/> est un chemin vers un fichier de certificat d'autorité PEM par rapport auquel valider les certificats clients.

#### pki_root

Le module `pki_root` obtient la _racine_ (root) et fait confiance aux certificats de l'autorité de certification définie dans l'[application PKI](/docs/caddyfile/options#pki-options). La directive `authority` peut accepter plusieurs autorités en même temps et peut être répétée plusieurs fois.

```caddy-d
... pki_root [<nom_ca>...] {
	authority <nom_ca>...
}
```

- **authority** <span id="authority"/> est le nom de l'autorité de certification configurée dans l'application PKI.

#### pki_intermediate

Le module `pki_intermediate` obtient l'_intermédiaire_ (intermediate) et fait confiance aux certificats de l'autorité de certification définie dans l'[application PKI](/docs/caddyfile/options#pki-options). La directive `authority` peut accepter plusieurs autorités en même temps et peut être répétée plusieurs fois.

```caddy-d
... pki_intermediate [<nom_ca>...] {
	authority <nom_ca>...
}
```

- **authority** <span id="authority"/> est le nom de l'autorité de certification configurée dans l'application PKI.

#### storage

Le module `storage` extrait les certificats racines de confiance du [stockage](/docs/caddyfile/options#storage) de Caddy. La directive `authority` peut accepter plusieurs autorités en même temps et peut être répétée plusieurs fois.

```caddy-d
... storage [<cles_stockage>...] {
	storage <module_stockage>
	keys    <cles_stockage>...
}
```

- **storage** <span id="storage"/> est un module de stockage optionnel à utiliser. Si non spécifié, le module de stockage par défaut sera utilisé. S'il est spécifié, il ne peut l'être qu'une seule fois.

- **keys** <span id="keys"/> est la liste des clés de stockage où sont stockés les fichiers PEM des certificats. La directive accepte plusieurs valeurs sur la même ligne et peut être spécifiée plusieurs fois.

#### http

Le module `http` obtient les certificats de confiance à partir de points d'accès HTTP. La directive `endpoints` peut accepter plusieurs points d'accès en même temps et peut être répétée plusieurs fois.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> est la liste des points d'accès HTTP à partir desquels obtenir les certificats. La directive accepte plusieurs valeurs sur la même ligne et peut être spécifiée plusieurs fois.

- **tls** <span id="tls"/> est une configuration TLS optionnelle à utiliser lors de la connexion au point d'accès HTTP. L'analyse du segment est définie dans la [section suivante](#tls-1).

##### TLS

```caddy-d
... {
	ca                    <module_ca>
	insecure_skip_verify
	handshake_timeout     <durée>
	server_name           <nom>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> est une directive optionnelle pour définir le fournisseur du pool de confiance. La configuration suit le même comportement que [`trust_pool`](#trust_pool). S'il est spécifié, il ne peut l'être qu'une seule fois.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> désactive la vérification de l'échange TLS, rendant la connexion non sécurisée et vulnérable aux attaques de l'homme du milieu. _Ne pas utiliser en production._ La vérification s'effectue par rapport aux autorités de certification de confiance du système ou telles que déterminées par la directive [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> est la [durée](/docs/conventions#durations) maximale d'attente pour que l'échange TLS se termine. Par défaut : pas de délai d'expiration.

- **server_name** <span id="server_name"/> définit le nom du serveur utilisé lors de la vérification du certificat reçu dans l'échange TLS. Par défaut, il utilisera la partie hôte de l'adresse de l'amont.

- **renegotiation** <span id="renegotiation"/> définit le niveau de renégociation TLS. La renégociation TLS est l'acte d'effectuer des échanges ultérieurs après le premier. Le niveau peut être l'un des suivants :
  - `never` (le défaut) désactive la renégociation.
  - `once` permet à un serveur distant de demander la renégociation une fois par connexion.
  - `freely` permet à un serveur distant de demander la renégociation de manière répétée.

### Vérificateurs (Verifiers)

Les modules de vérificateur de certificat client sont exécutés après avoir validé qu'ils ont été émis par une autorité de certification de confiance, si le `trust_pool` est configuré. Le seul vérificateur actuellement livré avec la distribution standard de Caddy est `leaf`.

#### Leaf

Le vérificateur `leaf` vérifie si le certificat client fait partie d'un ensemble défini de certificats autorisés. L'ensemble de certificats est chargé à l'aide de modules [chargeurs (loaders)](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders).

##### Chargeurs (Loaders)

La distribution standard de Caddy regroupe 4 chargeurs, dont 3 sont disponibles dans le Caddyfile.

###### File

Le chargeur `file` charge l'ensemble des certificats à partir de fichiers PEM spécifiés.

```caddy-d
... file <fichiers_pem...>
```

###### Folder

Le chargeur `folder` parcourt récursivement les répertoires nommés à la recherche de fichiers PEM à charger comme certificats clients acceptés.

```caddy-d
... folder <dossiers...>
```

###### PEM

Le chargeur `pem` accepte des certificats intégrés dans le Caddyfile au format PEM.

```caddy-d
... pem <chaines_pem...>
```

### Émetteurs (Issuers)

Ces émetteurs sont fournis en standard avec la directive `tls` :

#### acme

Obtient des certificats en utilisant le protocole ACME. Notez qu' `acme` est un émetteur par défaut (utilisant Let's Encrypt), le configurer explicitement est donc généralement inutile.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <durée>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <id_clé> <clé_mac>
	trusted_roots <fichiers_pem...>
	dns [<nom_fournisseur> [<options>]]
	propagation_timeout <durée>
	propagation_delay   <durée>
	dns_ttl             <durée>
	dns_challenge_override_domain <domaine>
	resolvers <serveurs_dns...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <nom>
}
```

- **dir** <span id="dir"/> est l'URL du répertoire de l'autorité de certification ACME.
  
  Par défaut : `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> est un répertoire de repli optionnel à utiliser lors du renouvellement des défis ; si tous les défis échouent, ce point d'accès sera utilisé pendant les nouveaux essais ; utile si une autorité de certification possède un point d'accès staging où vous souhaitez éviter les limitations de débit de leur point d'accès de production.

  Par défaut : `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> est l'adresse e-mail de contact du compte ACME.

- **timeout** <span id="timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit combien de temps attendre avant d'abandonner une opération ACME.

- **disable_http_challenge** <span id="disable_http_challenge"/> désactivera le défi HTTP.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> désactivera le défi TLS-ALPN.

- **alt_http_port** <span id="alt_http_port"/> est un port alternatif sur lequel servir le défi HTTP ; celui-ci doit se produire sur le port 80, vous devez donc rediriger les paquets vers ce port alternatif.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> est un port alternatif sur lequel servir le défi TLS-ALPN ; celui-ci doit se produire sur le port 443, vous devez donc rediriger les paquets vers ce port alternatif.

- **eab** <span id="eab"/> spécifie une liaison de compte externe (External Account Binding) qui peut être requise par certaines autorités de certification ACME.

- **trusted_roots** <span id="trusted_roots"/> est un ou plusieurs certificat(s) racine (en tant que noms de fichiers PEM) à croire lors de la connexion au serveur de l'autorité de certification ACME.

- **dns** <span id="dns"/> configure le défi DNS. Un fournisseur doit être configuré ici, sauf si l' [option globale `dns`](/docs/caddyfile/options#dns) spécifie un module de fournisseur DNS applicable globalement.

- **propagation_timeout** <span id="propagation_timeout"/> est une [valeur de durée](/docs/conventions#durations) qui définit le temps maximum d'attente pour que les enregistrements DNS TXT apparaissent lors de l'utilisation du défi DNS. Réglez sur `-1` pour désactiver les vérifications de propagation. Par défaut : 2 minutes.

- **propagation_delay** <span id="propagation_delay"/> est une [valeur de durée](/docs/conventions#durations) qui définit combien de temps attendre avant de commencer les vérifications de propagation des enregistrements DNS TXT lors de l'utilisation du défi DNS. Par défaut : 0 (pas d'attente).

- **dns_ttl** <span id="dns_ttl"/> est une [valeur de durée](/docs/conventions#durations) qui définit le TTL de l'enregistrement `TXT` utilisé pour le défi DNS. Rarement nécessaire.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> surcharge le domaine à utiliser pour le défi DNS. Ceci permet de déléguer le défi à un domaine différent.

  Vous pourriez vouloir utiliser ceci si le fournisseur DNS de votre domaine principal ne possède pas de [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) disponible. Vous pouvez à la place ajouter un enregistrement `CNAME` avec le sous-domaine `_acme-challenge` sur votre domaine principal, pointant vers un domaine secondaire pour lequel vous *possédez* un plugin. Cette option *ne nécessite pas* de support spécial de la part du plugin.
  
  Lorsque les émetteurs ACME tenteront de résoudre le défi DNS pour votre domaine principal, ils suivront alors le `CNAME` vers votre domaine secondaire pour trouver l'enregistrement `TXT`.

  **Note :** Utilisez le nom canonique complet de l'enregistrement CNAME comme valeur ici — le sous-domaine `_acme-challenge` ne sera pas préfixé automatiquement.

- **resolvers** <span id="resolvers"/> personnalise les résolveurs DNS utilisés lors de l'exécution du défi DNS ; ceux-ci ont la priorité sur les résolveurs du système ou n'importe quel résolveur par défaut. S'ils sont définis ici, les résolveurs seront propagés vers tous les émetteurs de certificats configurés.

  Il s'agit typiquement d'une liste d'adresses IP. Par exemple, pour utiliser [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) :

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> spécifie quelles chaînes de certificats Caddy devrait préférer ; utile si votre autorité de certification fournit plusieurs chaînes. Utilisez l'une des options suivantes :
	- **smallest** <span id="smallest"/> dira à Caddy de préférer les chaînes ayant le plus petit nombre d'octets.

	- **root_common_name** <span id="root_common_name"/> est une liste d'un ou plusieurs noms communs ; Caddy choisira la première chaîne ayant une racine qui correspond à au moins l'un des noms communs spécifiés.

	- **any_common_name** <span id="any_common_name"/> est une liste d'un ou plusieurs noms communs ; Caddy choisira la première chaîne ayant un émetteur qui correspond à au moins l'un des noms communs spécifiés.

- **profile** est le nom du [profil ACME](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) à appliquer lors de la commande de certificats. Si vous en spécifiez un, toutes les autorités de certification configurées (implicitement ou non) doivent supporter ce profil. Reportez-vous à la documentation de votre autorité de certification pour les profils disponibles ; certaines peuvent ne pas supporter les profils. EXPÉRIMENTAL : La spécification du profil ACME est encore à l'état de brouillon, cette fonctionnalité est donc sujette à modification ou suppression.


#### zerossl

Obtient des certificats en utilisant l'[API de délivrance de certificats propriétaire de ZeroSSL](https://zerossl.com/documentation/api/). Une clé d'API est requise et un paiement peut également l'être selon votre abonnement. Notez que cet émetteur est distinct du [point d'accès ACME de ZeroSSL](https://zerossl.com/documentation/acme/). Pour utiliser le point d'accès ACME de ZeroSSL, utilisez l'émetteur `acme` décrit ci-dessus configuré avec le point d'accès du répertoire ACME de ZeroSSL.

```caddy-d
... zerossl <cle_api> {
	validity_days <jours>
	alt_http_port <port>
	dns <nom_fournisseur> ...
	propagation_delay <durée>
	propagation_timeout <durée>
	resolvers <liste...>
	dns_ttl <durée>
}
```

- **validity_days** <span id="validity_days"/> définit la durée de vie du certificat. Seules certaines valeurs sont acceptées ; consultez la [documentation de ZeroSSL](https://zerossl.com/documentation/api/create-certificate/) pour les détails.
<!--   
  Par défaut : `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> est le port à utiliser pour terminer la validation HTTP de ZeroSSL, s'il ne s'agit pas du port 80.
- **dns** <span id="zerossl_dns"/> active la méthode de validation CNAME en utilisant le fournisseur DNS nommé avec la configuration donnée pour le provisionnement automatique d'enregistrements. Le plugin de fournisseur DNS doit être installé depuis l'un des dépôts [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Chaque plugin de fournisseur peut avoir sa propre syntaxe suivant son nom ; reportez-vous à leur documentation pour les détails. Le maintien du support pour chaque fournisseur DNS est un effort communautaire.
- **propagation_delay** <span id="propagation_delay"/> est le temps d'attente avant de vérifier la propagation de l'enregistrement CNAME.
- **propagation_timeout** <span id="propagation_timeout"/> est le temps d'attente pour la propagation de l'enregistrement CNAME avant d'abandonner.
- **resolvers** <span id="resolvers"/> définit des résolveurs DNS personnalisés à utiliser lors de la vérification de la propagation de l'enregistrement CNAME.
- **dns_ttl** <span id="dns_ttl"/> configure le TTL pour les enregistrements CNAME créés dans le cadre du processus de validation.



#### internal

Obtient des certificats auprès d'une autorité de certification interne.

```caddy-d
... internal {
	ca       <nom>
	lifetime <durée>
	sign_with_root
}
```

- **ca** <span id="ca"/> est le nom de l'autorité de certification interne à utiliser. Par défaut : `local`. Consultez les [options globales de l'application PKI](/docs/caddyfile/options#pki-options) pour configurer l'autorité de certification `local`, ou pour en créer d'autres.

  Par défaut, le certificat de l'autorité racine a une durée de vie de `3600d` (10 ans) et l'intermédiaire a une durée de vie de `7d` (7 jours).

  Caddy tentera d'installer le certificat de l'autorité racine dans le magasin de confiance du système, mais cela peut échouer lorsque Caddy s'exécute avec un utilisateur non privilégié, ou dans un conteneur Docker. Dans ce cas, le certificat de l'autorité racine devra être installé manuellement, soit en utilisant la commande [`caddy trust`](/docs/command-line#caddy-trust), soit en le [copiant hors du conteneur](/docs/running#usage).

- **lifetime** <span id="lifetime"/> est une [valeur de durée](/docs/conventions#durations) qui définit la période de validité pour les certificats finaux (leaf) émis en interne. Par défaut : `12h`. Il n'est PAS recommandé de changer ceci, sauf si c'est absolument nécessaire. Elle doit être plus courte que la durée de vie de l'intermédiaire.

- **sign_with_root** <span id="sign_with_root"/> force la racine à être l'émetteur au lieu de l'intermédiaire. Ce n'est PAS recommandé et ne devrait être utilisé que lorsque les appareils/clients ne valident pas correctement les chaînes de certificats (très rare).



### Gestionnaires de certificats (Certificate Managers)

Les modules gestionnaires de certificats sont distincts des modules émetteurs dans le sens où l'utilisation de modules gestionnaires implique qu'un outil ou service externe s'occupe du renouvellement du certificat, alors qu'un module émetteur implique que Caddy lui-même gère le certificat. (Les modules émetteurs prennent un CSR en entrée, mais les modules gestionnaires de certificats prennent un ClientHello TLS en entrée.)

Ces modules gestionnaires sont fournis en standard avec la directive `tls` :

#### tailscale

Obtient des certificats auprès d'une instance [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) tournant localement. Le [HTTPS doit être activé dans votre compte Tailscale](https://tailscale.com/kb/1153/enabling-https/) (ou votre serveur open source [Headscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)) ; et le processus Caddy doit soit s'exécuter en tant que root, soit vous devez configurer `tailscaled` pour donner à votre utilisateur Caddy la [permission de récupérer les certificats](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).

_**NOTE : Ceci est généralement inutile !** Caddy utilise automatiquement Tailscale pour tous les domaines `*.ts.net` sans aucune configuration supplémentaire._

```caddy-d
get_certificate tailscale  # souvent inutile !
```


#### http

Obtient des certificats en effectuant une requête HTTP(S). La réponse doit avoir un code d'état `200` et le corps doit contenir une chaîne PEM incluant le certificat complet (avec les intermédiaires) ainsi que la clé privée.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> est l'URL complète vers laquelle effectuer la requête. Il est fortement conseillé qu'il s'agisse d'un point d'accès local pour des raisons de performance. L'URL sera complétée par les paramètres de chaîne de requête suivants : 

  - `server_name` : valeur SNI
  - `signature_schemes` : liste séparée par des virgules des IDs hexadécimaux des algorithmes de signature
  - `cipher_suites` : liste séparée par des virgules des IDs hexadécimaux des suites de chiffrement
  - `local_ip` : adresse IP sur laquelle le client a effectué la requête



## Exemples

Utiliser un certificat et une clé personnalisés. Le certificat doit posséder des [SANs (Subject Alternative Names)](https://en.wikipedia.org/wiki/Subject_Alternative_Name) qui correspondent à l'adresse du site :

```caddy
example.com {
	tls cert.pem key.pem
}
```

Utiliser des certificats [de confiance locale](/docs/automatic-https#local-https) pour tous les hôtes du bloc de site actuel, plutôt que des certificats publics via ACME / Let's Encrypt (utile dans les environnements de dev) :

```caddy
example.com {
	tls internal
}
```

Utiliser des certificats de confiance locale, mais gérés [À la demande (On-Demand)](/docs/automatic-https#on-demand-tls) au lieu d'en arrière-plan. Cela vous permet de faire pointer n'importe quel domaine vers votre instance Caddy et de lui faire provisionner automatiquement un certificat pour vous. Ceci NE DEVRAIT PAS être utilisé si votre instance Caddy est accessible publiquement, car un attaquant pourrait l'utiliser pour épuiser les ressources de votre serveur :

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Utiliser des options personnalisées pour l'autorité de certification interne (impossible d'utiliser le raccourci `tls internal`) :

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Spécifier une adresse e-mail pour votre compte ACME (mais si une seule adresse est utilisée pour tous les sites, nous recommandons plutôt l' [option globale `email`](/docs/caddyfile/options)) :

```caddy
example.com {
	tls votre@email.com
}
```

Activer le défi DNS pour un domaine géré chez Cloudflare avec des identifiants de compte dans une variable d'environnement. Cela débloque le support des certificats wildcard, lequel nécessite une validation DNS :

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Obtenir la chaîne de certificats via HTTP, au lieu de laisser Caddy la gérer. Notez que [`get_certificate`](#certificate-managers) implique que [`on_demand`](#on_demand) est activé, récupérant les certificats via un module au lieu de déclencher une délivrance ACME :

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Activer l'authentification client TLS et exiger que les clients présentent un certificat valide qui est vérifié par rapport à toutes les autorités fournies via le fournisseur `file` de [`trust_pool`](#trust_pool) :

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
