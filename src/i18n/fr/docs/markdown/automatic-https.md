---
title: "HTTPS Automatique"
---

# HTTPS Automatique

**Caddy a été le premier serveur web à utiliser le HTTPS automatiquement _et par défaut_.**

Le HTTPS automatique provisionne des certificats TLS pour tous vos sites et s'occupe de leur renouvellement. Il redirige également le trafic HTTP vers HTTPS pour vous ! Caddy utilise des paramètres par défaut sûrs et modernes — aucune interruption de service, configuration supplémentaire ou outil tiers n'est requis.

<aside class="tip">
	Caddy a innové dans la technologie du HTTPS automatique ; nous le faisons depuis le premier jour où cela a été possible en 2015. La logique d'automatisation HTTPS de Caddy est la plus mature et la plus robuste au monde.
</aside>

Voici une vidéo de 28 secondes montrant comment cela fonctionne :

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Menu :**

- [Vue d'ensemble](#overview)
- [Activation](#activation)
- [Effets](#effects)
- [Prérequis du nom d'hôte](#hostname-requirements)
- [HTTPS local](#local-https)
- [Tests](#testing)
- [Défis ACME](#acme-challenges)
- [TLS à la demande (On-Demand)](#on-demand-tls)
- [Erreurs](#errors)
- [Stockage](#storage)
- [Certificats Wildcard](#wildcard-certificates)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## Vue d'ensemble

**Par défaut, Caddy sert tous les sites via HTTPS.**

- Caddy sert les adresses IP et les noms d'hôtes locaux/internes via HTTPS en utilisant des certificats auto-signés qui sont automatiquement approuvés localement (si autorisé).
	- Exemples : `localhost`, `127.0.0.1`
- Caddy sert les noms DNS publics via HTTPS en utilisant des certificats provenant d'une autorité de certification (CA) ACME publique telle que [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) ou [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com).
	- Exemples : `example.com`, `sub.example.com`, `*.example.com`

Caddy maintient le renouvellement de tous les certificats gérés et redirige automatiquement le HTTP (port par défaut `80`) vers le HTTPS (port par défaut `443`).

**Pour le HTTPS local :**

- Caddy peut demander un mot de passe pour installer son certificat racine unique dans votre magasin de confiance. Cela n'arrive qu'une fois par racine ; et vous pouvez le supprimer à tout moment.
- Tout client accédant au site sans faire confiance au certificat racine de Caddy verra des erreurs de sécurité.

**Pour les noms de domaine publics :**

<aside class="tip">

Ce sont des prérequis communs pour tout site de production basique, pas seulement pour Caddy. La différence principale est de configurer vos enregistrements DNS correctement **avant** de lancer Caddy afin qu'il puisse provisionner les certificats.

</aside>


- Si les enregistrements A/AAAA de votre domaine pointent vers votre serveur,
- si les ports `80` et `443` sont ouverts de l'extérieur,
- si Caddy peut se lier à ces ports (_ou_ si ces ports sont redirigés vers Caddy),
- si votre [répertoire de données](/docs/conventions#data-directory) est accessible en écriture et persistant,
- et si votre nom de domaine apparaît quelque part dans la configuration,

alors les sites seront servis via HTTPS automatiquement. Vous n'aurez rien d'autre à faire. Ça fonctionne tout simplement !

Parce que le HTTPS utilise une infrastructure publique partagée, en tant qu'administrateur de serveur, vous devez comprendre le reste des informations de cette page pour éviter les problèmes inutiles, les dépanner lorsqu'ils surviennent et configurer correctement les déploiements avancés.



<a id="activation"></a>
## Activation

Caddy active implicitement le HTTPS automatique lorsqu'il connaît un nom de domaine (c'est-à-dire un nom d'hôte) ou une adresse IP qu'il sert. Il existe plusieurs façons de renseigner votre domaine/IP à Caddy, selon la manière dont vous le lancez ou le configurez :

- Une [adresse de site](/docs/caddyfile/concepts#addresses) dans le [Caddyfile](/docs/caddyfile)
- Un [sélecteur d'hôte (host matcher)](/docs/json/apps/http/servers/routes/match/host/) au niveau supérieur dans les [routes JSON](/docs/modules/http#servers/routes)
- Des drapeaux de ligne de commande comme [`--domain`](/docs/command-line#caddy-file-server) ou [`--from`](/docs/command-line#caddy-reverse-proxy)
- Le chargeur de certificat [automate](/docs/json/apps/tls/certificates/automate/)

L'un des éléments suivants empêchera l'activation du HTTPS automatique, en tout ou en partie :

- Le désactiver explicitement [via JSON](/docs/json/apps/http/servers/automatic_https/) ou [via Caddyfile](/docs/caddyfile/options#auto-https)
- Ne fournir aucun nom d'hôte ou adresse IP dans la configuration
- Écouter exclusivement sur le port HTTP
- Préfixer l'[adresse du site](/docs/caddyfile/concepts#addresses) avec `http://` dans le Caddyfile
- Charger manuellement des certificats (à moins que [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/) ne soit défini)

**Cas particuliers :**

- Les domaines se terminant par `.ts.net` ne seront pas gérés par Caddy. Au lieu de cela, Caddy tentera automatiquement d'obtenir ces certificats au moment de l'établissement de la connexion (handshake) auprès de l'instance [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) locale. Cela nécessite que le [HTTPS soit activé dans votre compte Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) et que le processus Caddy soit lancé en tant que root, ou que vous configuriez `tailscaled` pour donner à l'utilisateur de Caddy la [permission de récupérer des certificats](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).


<a id="effects"></a>
## Effets

Lorsque le HTTPS automatique est activé, les événements suivants se produisent :

- Des certificats sont obtenus et renouvelés pour [tous les noms de domaine éligibles](#hostname-requirements)
- Le trafic HTTP est redirigé vers HTTPS (cela utilise le [port HTTP](/docs/modules/http#http_port) `80`)

Le HTTPS automatique n'écrase jamais une configuration explicite, il ne fait que la compléter.

Si vous avez déjà un [serveur](/docs/json/apps/http/servers/) écoutant sur le port HTTP, les routes de redirection HTTP->HTTPS seront insérées après vos routes possédant un sélecteur d'hôte, mais avant une route générique (catch-all) définie par l'utilisateur.

Vous pouvez [personnaliser ou désactiver le HTTPS automatique](/docs/json/apps/http/servers/automatic_https/) si nécessaire ; par exemple, vous pouvez ignorer certains noms de domaine ou désactiver les redirections (pour le Caddyfile, faites-le avec les [options globales](/docs/caddyfile/options)).


<a id="hostname-requirements"></a>
## Prérequis du nom d'hôte

Tous les noms d'hôtes (noms de domaine) sont éligibles à des certificats entièrement gérés s'ils :

- ne sont pas vides
- consistent uniquement en caractères alphanumériques, tirets, points et le caractère générique (`*`)
- ne commencent pas ou ne se terminent pas par un point ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

De plus, les noms d'hôtes sont éligibles à des certificats de confiance publique s'ils :

- ne sont pas localhost (incluant les extensions `.localhost`, `.local`, `.internal` et `.home.arpa`)
- ne sont pas une adresse IP
- n'ont qu'un seul caractère générique `*` comme étiquette la plus à gauche


<a id="local-https"></a>
## HTTPS local

Caddy utilise automatiquement le HTTPS pour tous les sites ayant un hôte (domaine, IP ou nom d'hôte) spécifié, y compris les hôtes internes et locaux. Certains hôtes ne sont pas publics (ex: `127.0.0.1`, `localhost`) ou ne sont généralement pas éligibles à des certificats de confiance publique (ex: les adresses IP — vous pouvez obtenir des certificats pour celles-ci, mais seulement auprès de certaines autorités de certification). Ceux-ci sont tout de même servis via HTTPS, sauf si désactivé.

Pour servir des sites non publics via HTTPS, Caddy génère sa propre autorité de certification (CA) et l'utilise pour signer les certificats. La chaîne de confiance se compose d'un certificat racine et d'un certificat intermédiaire. Les certificats finaux (leaf) sont signés par l'intermédiaire. Ils sont stockés dans le [répertoire de données de Caddy](/docs/conventions#data-directory) sous `pki/authorities/local`.

L'autorité de certification locale de Caddy est propulsée par les [bibliothèques Smallstep <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/).

Le HTTPS local n'utilise pas ACME et n'effectue aucune validation DNS. Il ne fonctionne que sur la machine locale et n'est approuvé que là où le certificat racine de l'autorité de certification est installé.

<a id="ca-root"></a>
### Racine de l'autorité de certification (CA Root)

La clé privée racine est générée de manière unique à l'aide d'une source pseudo-aléatoire cryptographiquement sécurisée et persistée dans le stockage avec des permissions limitées. Elle n'est chargée en mémoire que pour effectuer des tâches de signature, après quoi elle quitte le champ d'application pour être collectée par le ramasse-miettes (garbage collector).

Bien que Caddy puisse être configuré pour signer directement avec la racine (pour supporter des clients non conformes), cela est désactivé par défaut, et la clé racine n'est utilisée que pour signer les intermédiaires.

La première fois qu'une clé racine est utilisée, Caddy tentera de l'installer dans le ou les magasins de confiance locaux du système. S'il n'en a pas la permission, il demandera un mot de passe. Ce comportement peut être désactivé avec [`skip_install_trust` dans un Caddyfile](/docs/caddyfile/options#skip-install-trust) ou [`"install_trust": false` dans une configuration JSON](/docs/json/apps/pki/certificate_authorities/install_trust/). Si cela échoue parce qu'il est exécuté par un utilisateur non privilégié, vous pouvez lancer [`caddy trust`](/docs/command-line#caddy-trust) pour réessayer l'installation en tant qu'utilisateur privilégié.

<aside class="tip">
	Il est sûr de faire confiance au certificat racine de Caddy sur votre propre machine tant que votre ordinateur n'est pas compromis et que votre clé racine unique n'est pas divulguée.
</aside>

Une fois l'autorité de certification racine de Caddy installée, vous la verrez dans votre magasin de confiance local sous le nom "Caddy Local Authority" (à moins que vous n'ayez configuré un nom différent). Vous pouvez la désinstaller à tout moment si vous le souhaitez (la commande [`caddy untrust`](/docs/command-line#caddy-untrust) rend cela facile).

Notez que l'installation automatique du certificat dans les magasins de confiance locaux n'est faite que par commodité et n'est pas garantie de fonctionner, en particulier si des conteneurs sont utilisés ou si Caddy est lancé comme un service système non privilégié. En fin de compte, si vous vous appuyez sur une PKI interne, il incombe à l'administrateur système de s'assurer que l'autorité de certification racine de Caddy est correctement ajoutée aux magasins de confiance nécessaires (cela sort du cadre du serveur web).


<a id="ca-intermediates"></a>
### Intermédiaires de l'autorité de certification (CA Intermediates)

Un certificat et une clé intermédiaires seront également générés et utilisés pour signer les certificats finaux (sites individuels).

Contrairement au certificat racine, les certificats intermédiaires ont une durée de vie beaucoup plus courte et seront automatiquement renouvelés selon les besoins.


<a id="testing"></a>
## Tests

Pour tester ou expérimenter votre configuration Caddy, assurez-vous de [changer le point d'accès ACME](/docs/modules/tls.issuance.acme#ca) pour une URL de test ou de développement, sinon vous risquez d'atteindre des limites de débit qui peuvent bloquer votre accès au HTTPS pendant une semaine, selon la limite atteinte.

L'une des autorités de certification par défaut de Caddy est [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), qui dispose d'un [point d'accès de test <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) qui n'est pas soumis aux mêmes [limites de débit <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/) :

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## Défis ACME

L'obtention d'un certificat TLS de confiance publique nécessite une validation par une autorité tierce de confiance publique. Aujourd'hui, ce processus de validation est automatisé avec le [protocole ACME <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555), et peut être effectué de trois manières ("types de défis"), décrites ci-dessous.

Les deux premiers types de défis sont activés par défaut. Si plusieurs défis sont activés, Caddy en choisit un au hasard pour éviter une dépendance accidentelle à un défi particulier. Au fil du temps, il apprend quel type de défi réussit le mieux et commencera à le privilégier, mais se rabattra sur d'autres types de défis disponibles si nécessaire.


<a id="http-challenge"></a>
### Défi HTTP

Le défi HTTP effectue une recherche DNS faisant autorité pour l'enregistrement A/AAAA du nom d'hôte candidat, puis demande une ressource cryptographique temporaire via le port `80` en utilisant HTTP. Si l'autorité de certification voit la ressource attendue, un certificat est émis.

Ce défi nécessite que le port `80` soit accessible de l'extérieur. Si Caddy ne peut pas écouter sur le port 80, les paquets provenant du port `80` doivent être redirigés vers le [port HTTP](/docs/json/apps/http/http_port/) de Caddy.

Ce défi est activé par défaut et ne nécessite aucune configuration explicite.


<a id="tls-alpn-challenge"></a>
### Défi TLS-ALPN

Le défi TLS-ALPN effectue une recherche DNS faisant autorité pour l'enregistrement A/AAAA du nom d'hôte candidat, puis demande une ressource cryptographique temporaire via le port `443` en utilisant un échange TLS (handshake) contenant des valeurs ServerName et ALPN spécifiques. Si l'autorité de certification voit la ressource attendue, un certificat est émis.

Ce défi nécessite que le port `443` soit accessible de l'extérieur. Si Caddy ne peut pas écouter sur le port 443, les paquets provenant du port `443` doivent être redirigés vers le [port HTTPS](/docs/json/apps/http/https_port/) de Caddy.

Ce défi est activé par défaut et ne nécessite aucune configuration explicite.


<a id="dns-challenge"></a>
### Défi DNS

Le défi DNS effectue une recherche DNS faisant autorité pour les enregistrements `TXT` du nom d'hôte candidat, et recherche un enregistrement `TXT` spécial avec une certaine valeur. Si l'autorité de certification voit la valeur attendue, un certificat est émis.

Ce défi ne nécessite aucun port ouvert, et le serveur demandant un certificat n'a pas besoin d'être accessible de l'extérieur. Cependant, le défi DNS nécessite une configuration. Caddy doit connaître les identifiants pour accéder au fournisseur DNS de votre domaine afin de pouvoir définir (et effacer) les enregistrements `TXT` spéciaux. Si le défi DNS est activé, les autres défis sont désactivés par défaut.

Étant donné que les autorités de certification ACME suivent les standards DNS lors de la recherche des enregistrements `TXT` pour la vérification du défi, vous pouvez utiliser des enregistrements CNAME pour déléguer la réponse au défi à d'autres zones DNS. Cela peut être utilisé pour déléguer le sous-domaine `_acme-challenge` à [une autre zone](/docs/caddyfile/directives/tls#dns_challenge_override_domain). Ceci est particulièrement utile si votre fournisseur DNS ne propose pas d'API, ou n'est pas supporté par l'un des plugins DNS de Caddy.

Le support des fournisseurs DNS est un effort communautaire. [Apprenez comment activer le défi DNS pour votre fournisseur sur notre wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## TLS à la demande (On-Demand)

Caddy a été le pionnier d'une nouvelle technologie que nous appelons le **TLS à la demande**, qui obtient dynamiquement un nouveau certificat lors du premier échange TLS qui le requiert, plutôt qu'au chargement de la configuration. Crucialement, cela ne nécessite **pas** de coder en dur les noms de domaine dans votre configuration à l'avance.

De nombreuses entreprises s'appuient sur cette fonctionnalité unique pour mettre à l'échelle leurs déploiements TLS à moindre coût et sans maux de tête opérationnels lorsqu'elles servent des dizaines de milliers de sites.

Le TLS à la demande est utile si :

- vous ne connaissez pas tous les noms de domaine lorsque vous lancez ou rechargez votre serveur,
- les noms de domaine ne sont peut-être pas correctement configurés tout de suite (enregistrements DNS non encore définis),
- vous n'avez pas le contrôle des noms de domaine (ex: ce sont des domaines de clients).

Lorsque le TLS à la demande est activé, vous n'avez pas besoin de spécifier les noms de domaine dans votre configuration pour obtenir des certificats pour eux. Au lieu de cela, lorsqu'un échange TLS est reçu pour un nom de serveur (SNI) pour lequel Caddy n'a pas encore de certificat, l'échange est mis en attente pendant que Caddy obtient un certificat pour terminer l'échange. Le délai n'est généralement que de quelques secondes, et seul cet échange initial est lent. Tous les échanges futurs sont rapides car les certificats sont mis en cache et réutilisés, et les renouvellements se produisent en arrière-plan. Les échanges futurs peuvent déclencher une maintenance pour le certificat afin de le maintenir renouvelé, mais cette maintenance se produit en arrière-plan si le certificat n'a pas encore expiré.

<a id="using-on-demand-tls"></a>
### Utiliser le TLS à la demande

**Le TLS à la demande doit être à la fois activé et restreint pour éviter les abus.**

L'activation du TLS à la demande se fait dans les [politiques d'automatisation TLS](/docs/json/apps/tls/automation/policies/) si vous utilisez la configuration JSON, ou [dans les blocs de site avec la directive `tls`](/docs/caddyfile/directives/tls) si vous utilisez le Caddyfile.

Pour éviter les abus de cette fonctionnalité, vous devez configurer des restrictions. Cela se fait dans l'[objet `automation` de la configuration JSON](/docs/json/apps/tls/automation/on_demand/), ou via l'[option globale `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) du Caddyfile. Les restrictions sont "globales" et ne sont pas configurables par site ou par domaine. La restriction principale est un point d'accès "ask" (interroger) auquel Caddy enverra une requête HTTP pour demander s'il a la permission d'obtenir et de gérer un certificat pour le domaine de l'échange TLS. Cela signifie que vous aurez besoin d'un backend interne capable, par exemple, d'interroger la table des comptes de votre base de données pour voir si un client s'est inscrit avec ce nom de domaine.

Gardez à l'esprit la rapidité avec laquelle votre autorité de certification est capable de délivrer des certificats. Si cela prend plus de quelques secondes, cela aura un impact négatif sur l'expérience utilisateur (uniquement pour le premier client).

En raison de sa nature différée et de la configuration supplémentaire requere pour éviter les abus, nous recommandons d'activer le TLS à la demande uniquement lorsque votre cas d'utilisation correspond à ce qui est décrit ci-dessus.

[Consultez notre article wiki pour plus d'informations sur l'utilisation efficace du TLS à la demande.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)


<a id="errors"></a>
## Erreurs

Caddy fait de son mieux pour continuer si des erreurs surviennent lors de la gestion des certificats.

Par défaut, la gestion des certificats est effectuée en arrière-plan. Cela signifie qu'elle ne bloquera pas le démarrage et ne ralentira pas vos sites. Cependant, cela signifie également que le serveur fonctionnera avant même que tous les certificats ne soient disponibles. L'exécution en arrière-plan permet à Caddy de réessayer avec un repli exponentiel (exponential backoff) sur une longue période.

Voici ce qui se passe s'il y a une erreur lors de l'obtention ou du renouvellement d'un certificat :

1. Caddy réessaye une fois après une courte pause au cas où ce serait un coup de chance
2. Caddy fait une courte pause, puis passe au type de défi activé suivant
3. Une fois que tous les types de défis activés ont été essayés, [il essaye l'émetteur configuré suivant](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. Une fois que tous les émetteurs ont été essayés, il recule de manière exponentielle
	- Maximum de 1 jour entre les tentatives
	- Jusqu'à 30 jours

Lors des tentatives avec Let's Encrypt, Caddy bascule sur leur [environnement de test <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) pour éviter les problèmes de limites de débit. Ce n'est pas une stratégie parfaite, mais en général c'est utile.

Les défis ACME prennent au moins quelques secondes, et la limitation interne du débit aide à atténuer les abus accidentels. Caddy utilise une limitation interne en plus de ce que vous ou l'autorité de certification configurez, de sorte que vous pouvez donner à Caddy un plateau avec un million de noms de domaine et il obtiendra progressivement — mais aussi vite qu'il le peut — des certificats pour tous. La limite de débit interne de Caddy est actuellement de 10 tentatives par compte ACME toutes les 10 secondes.

Pour éviter les fuites de ressources, Caddy annule les tâches en cours (y compris les transactions ACME) lorsque la configuration est modifiée. Bien que Caddy soit capable de gérer des rechargements de configuration fréquents, gardez à l'esprit ces considérations opérationnelles et envisagez de regrouper les changements de configuration pour réduire les rechargements et donner à Caddy une chance de terminer réellement l'obtention des certificats en arrière-plan.

<a id="issuer-fallback"></a>
### Repli d'émetteur (Issuer fallback)

Caddy est le premier (et jusqu'à présent le seul) serveur à supporter un basculement (failover) automatique et totalement redondant vers d'autres autorités de certification s'il ne parvient pas à obtenir un certificat.

Par défaut, Caddy active deux autorités de certification compatibles ACME : [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) et [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Si Caddy ne peut pas obtenir de certificat auprès de Let's Encrypt, il essayera avec ZeroSSL ; si les deux échouent, il reculera et réessaiera plus tard. Dans votre configuration, vous pouvez personnaliser les émetteurs que Caddy utilise pour obtenir des certificats, que ce soit de manière universelle ou pour des noms spécifiques.


<a id="storage"></a>
## Stockage

Caddy stockera les certificats publics, les clés privées et d'autres ressources dans son [installation de stockage configurée](/docs/json/storage/) (ou celle par défaut, si non configurée — voir le lien pour les détails).

**La chose principale que vous devez savoir en utilisant la configuration par défaut est que le dossier `$HOME` doit être accessible en écriture et persistant.** Pour vous aider à dépanner, Caddy affiche ses variables d'environnement au démarrage si le drapeau `--environ` est spécifié.

Toutes les instances de Caddy configurées pour utiliser le même stockage partageront automatiquement ces ressources et coordonneront la gestion des certificats en tant que cluster.

Avant de tenter toute transaction ACME, Caddy testera le stockage configuré pour s'assurer qu'il est accessible en écriture et qu'il a une capacité suffisante. Cela aide à réduire les conflits de verrouillage inutiles.


<a id="wildcard-certificates"></a>
## Certificats Wildcard

Caddy peut obtenir et gérer des certificats wildcard lorsqu'il est configuré pour servir un site avec un nom wildcard éligible. Un nom de site est éligible au wildcard si seule son étiquette de domaine la plus à gauche est un wildcard. Par exemple, `*.example.com` est éligible, mais ceux-là ne le sont pas : `sub.*.example.com`, `foo*.example.com`, `*bar.example.com` et `*.*.example.com`. (C'est une restriction de la WebPKI.)

Si vous utilisez le Caddyfile, Caddy prend les noms de site littéralement en ce qui concerne les noms de sujet de certificat. En d'autres termes, un site défini comme `sub.example.com` amènera Caddy à gérer un certificat pour `sub.example.com`, et un site défini comme `*.example.com` amènera Caddy à gérer un certificat wildcard pour `*.example.com`. Vous pouvez voir cela démontré sur notre page [Modèles courants de Caddyfile](/docs/caddyfile/patterns#wildcard-certificates). Si vous avez besoin d'un comportement différent, la [configuration JSON](/docs/json/) vous donne un contrôle plus précis sur les sujets de certificat et les noms de site ("host matchers").

Depuis Caddy 2.10, lors de l'automatisation d'un certificat wildcard, Caddy utilisera le certificat wildcard pour les sous-domaines individuels de la configuration. Il n'obtiendra pas de certificats pour les sous-domaines individuels sauf s'il est explicitement configuré pour le faire (ex: avec `force_automate`).

Les certificats wildcard représentent un large degré d'autorité et ne doivent être utilisés que lorsque vous avez tellement de sous-domaines que la gestion de certificats individuels saturerait la PKI ou vous ferait atteindre les limites de débit imposées par l'autorité de certification, ou si le compromis sur la confidentialité justifie le risque d'exposer autant de zones DNS en cas de compromission de clé. Notez que les certificats wildcard ne permettent pas à eux seuls de dissimuler des sous-domaines spécifiques : ils sont toujours exposés dans les paquets TLS ClientHello à moins que l'Encrypted ClientHello (ECH) ne soit activé. (Voir ci-dessous.)

**Note :** [Let's Encrypt nécessite <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) le [défi DNS](#dns-challenge) pour obtenir des certificats wildcard.


<a id="encrypted-clienthello-ech"></a>
## Encrypted ClientHello (ECH)

Normalement, les échanges TLS impliquent l'envoi du ClientHello, incluant le Server Name Indicator (SNI ; le domaine auquel on se connecte), en texte clair. C'est parce qu'il contient les paramètres nécessaires au chiffrement de la connexion qui suit l'échange. Cela expose bien sûr le nom de domaine, qui est la partie la plus sensible du ClientHello, à quiconque peut écouter les connexions, même s'ils ne sont pas à proximité physique immédiate. Cela révèle à quel service vous vous connectez alors que l'IP de destination peut servir de nombreux sites différents, et c'est ainsi que certains gouvernements censurent l'Internet.

Avec l'Encrypted ClientHello, le client peut protéger le nom de domaine en enveloppant le vrai ClientHello dans un ClientHello "externe" qui établit les paramètres de déchiffrement du ClientHello "interne". Cependant, de nombreuses pièces mobiles doivent s'assembler parfaitement pour que cela fonctionne et apporte de réels avantages en matière de confidentialité.

Tout d'abord, le client doit savoir quels paramètres, ou configuration, utiliser pour chiffrer le ClientHello. Ces informations incluent une clé publique et un domaine "externe" (le "nom public"), entre autres choses. Cette configuration doit être publiée ou distribuée d'une manière ou d'une autre de façon fiable.

Vous pourriez théoriquement l'écrire sur un morceau de papier et le distribuer à tout le monde, mais la plupart des navigateurs majeurs supportent la recherche d'enregistrements DNS de type HTTPS contenant les paramètres ECH lors de la connexion à un site. Par conséquent, vous devrez : (1) générer une configuration ECH (paire de clés publique/privée, entre autres paramètres), puis (2) créer un enregistrement DNS de type HTTPS contenant la configuration ECH encodée en base64.

Ou... vous pourriez laisser Caddy faire tout cela pour vous. Caddy est le premier et le seul serveur web capable de générer, publier et servir automatiquement des configurations ECH.

Une fois l'enregistrement HTTPS publié, les clients devront effectuer une recherche DNS pour l'enregistrement HTTPS lors de la connexion à votre site. Normalement, les recherches DNS sont en texte clair, ce qui compromet la sécurité des échanges ECH résultants, donc les navigateurs devront utiliser un protocole DNS sécurisé comme le DNS-over-HTTPS (DoH) ou le DNS-over-TLS (DoT). Selon le navigateur, cela peut nécessiter une activation manuelle.

Une fois que le client a téléchargé en toute sécurité la configuration ECH, il utilise la clé publique intégrée pour chiffrer le ClientHello et procède à la connexion à votre site. Caddy déchiffre alors le ClientHello interne et procède au service de votre site, sans que le nom de domaine n'apparaisse jamais en texte clair sur le réseau.

<a id="deployment-considerations"></a>
### Considérations de déploiement

L'ECH est une technologie nuancée. Même si Caddy automatise complètement l'ECH, de nombreux points doivent être pris en compte pour maximiser les avantages en matière de confidentialité. Vous devez également être conscient de divers compromis.

<a id="publication"></a>
#### Publication

Caddy ne créera un enregistrement HTTPS pour un domaine que s'il existe déjà un enregistrement pour ce domaine. Cela évite de casser les recherches DNS pour un sous-domaine qui pourrait être couvert par un wildcard. Assurez-vous que vos sites ont au moins un enregistrement A/AAAA pointant vers votre serveur. Si vous n'utilisez qu'un wildcard pour les enregistrements DNS, alors le domaine wildcard devra également apparaître dans votre configuration Caddy.

Caddy ne publiera pas d'enregistrement HTTPS pour un domaine qui possède un enregistrement CNAME.

<a id="ech-grease"></a>
#### ECH GREASE

Si vous ouvrez Wireshark puis vous connectez à n'importe quel site (même un qui ne supporte pas l'ECH) dans une version moderne d'un navigateur majeur comme Firefox ou Chrome (même avec l'ECH désactivé), vous remarquerez peut-être que son échange inclut l'extension `encrypted_client_hello` :

![ECH GREASE](/resources/images/ech-grease.png)

Le but est de rendre les véritables échanges ECH indiscernables des échanges en texte clair. Si les échanges ECH semblaient différents des normaux, les censeurs pourraient simplement bloquer les échanges ECH avec un minimum de dommages collatéraux. Mais s'ils bloquaient tout échange avec une extension ECH plausible, ils éteindraient pratiquement la majeure partie de l'Internet. (L'objectif est d'augmenter le coût de la censure généralisée.)

C'est principalement important à savoir lors du dépannage des connexions.

<a id="key-rotation"></a>
#### Rotation des clés

Comme pour les clés de certificat, il n'est pas de bonne pratique (et cela peut être carrément risqué) d'utiliser la même clé pendant longtemps. À ce titre, les clés ECH doivent être rotatées régulièrement. Contrairement aux certificats, les configurations ECH n'expirent pas strictement. Mais les serveurs devraient tout de même les rotater.

La rotation des clés est cependant délicate, car les clients doivent connaître les clés mises à jour. Si le serveur remplaçait simplement les anciennes clés par de nouvelles, tous les échanges ECH échoueraient à moins que les clients ne soient immédiatement informés des nouvelles clés. Mais la simple publication des clés mises à jour ne suffit pas. La réalité est que les enregistrements DNS ont des TTL, les résolveurs cachent les réponses, etc. Cela peut prendre des minutes, des heures, voire des jours pour que les clients interrogent les enregistrements HTTPS mis à jour et commencent à utiliser la nouvelle config ECH.

Pour cette raison, les serveurs devraient continuer à supporter les anciennes configs ECH pendant une certaine période. Ne pas le faire risque d'exposer les noms de serveurs en texte clair _à grande échelle_. Caddy rotate les clés de temps en temps, et supporte les clés rotatées pendant un certain temps, jusqu'à ce qu'elles soient finalement abandonnées.

Cependant, cela peut ne pas suffire. Certains clients ne recevront toujours pas les clés mises à jour pour diverses raisons, et chaque fois que cela arrive, il y a un risque d'exposer le nom du serveur. Il doit donc y avoir un autre moyen de donner aux clients la config mise à jour _en bande_ (in-band) avec la connexion. C'est à cela que sert le _nom externe_ (ou _nom public_).

<a id="public-name"></a>
#### Nom public

Le ClientHello "externe" est un ClientHello normal avec deux subtiles différences qui ne sont connues que du serveur d'origine :

1. L'extension SNI est fausse
2. L'extension ECH est vraie

Cette extension SNI "externe" contient le nom public qui protège vos vrais domaines. Ce nom peut être n'importe quoi, mais **votre serveur doit faire autorité pour le nom public** car Caddy obtiendra un certificat pour lui.

Si un client tente d'établir une connexion ECH mais que le serveur ne peut pas déchiffrer le ClientHello interne, il peut en fait terminer l'échange en utilisant le ClientHello _externe_ avec un certificat pour le nom externe. Cette connexion sécurisée est strictement utilisée _uniquement_ pour envoyer au client la config ECH actuelle ; c'est-à-dire que c'est une connexion TLS temporaire dans le seul but de terminer la connexion TLS initiale. Aucune donnée applicative n'est transmise : juste la clé ECH. Une fois que le client a la clé mise à jour, il peut établir la connexion TLS comme prévu.

De cette manière, le vrai nom du serveur reste protégé et les clients désynchronisés restent capables de se connecter, ce qui sont deux éléments vitaux de la sécurité.

Le nom public peut être l'un des domaines de votre site, un sous-domaine, ou n'importe quel autre nom de domaine qui pointe vers votre serveur. Nous recommandons de choisir exactement un nom générique. Par exemple, Cloudflare sert des millions de sites derrière `cloudflare-ech.com`. C'est important pour augmenter la taille de votre ensemble d'anonymat (anonymity set).

Les noms publics ne devraient pas être vides ; c'est-à-dire qu'un nom public doit être configuré pour que les choses fonctionnent. Caddy ne l'impose pas actuellement (et pourrait le faire plus tard), mais la spécification ECH exige que le nom public fasse au moins 1 octet de long. Certains logiciels accepteront des noms vides, d'autres non. Cela peut mener à des comportements confus comme des navigateurs utilisant l'ECH mais des serveurs le rejetant comme invalide ; ou des navigateurs n'utilisant pas l'ECH (parce qu'il est invalide) même si la config est correctement dans l'enregistrement DNS. Il incombe au propriétaire du site d'assurer une configuration et une publication ECH correctes pour garantir la confidentialité.


<a id="anonymity-set"></a>
#### Ensemble d'anonymat (Anonymity set)

Pour maximiser les bénéfices de l'ECH en matière de confidentialité, efforcez-vous de maximiser la taille de votre _ensemble d'anonymat_. En essence, cet ensemble est composé de serveurs orientés client qui ont un comportement identique pour les observateurs. L'idée est qu'un observateur ne peut pas facilement réduire/déduire les sites ou services possibles auxquels les clients se connectent.

En pratique, nous recommandons de n'avoir qu'un seul nom public pour tous vos sites. (Il n'y a qu'un seul nom public par config ECH, cela implique donc de n'avoir qu'une seule config ECH active à tout moment.) Si vous utilisez Caddy en cluster, Caddy partage et coordonne automatiquement les configs ECH avec les autres instances, ce qui s'occupe de cela pour vous.

Poussé à l'extrême, cela implique que chaque site sur Internet pourrait ou devrait être derrière une seule adresse IP et un seul nom public...


<a id="centralization"></a>
#### Centralisation

... ce qui nous amène à notre sujet suivant : la centralisation. L'une des critiques de l'ECH est qu'il tend à motiver la centralisation. Il le fait d'au moins deux manières : (1) par des clients favorisant le DoH/DoT pour les recherches DNS, ce qui envoie toutes les recherches DNS à travers une petite poignée de fournisseurs, et (2) en maximisant la taille de l'ensemble d'anonymat à grande échelle.

Lorsque le DoH ou le DoT est utilisé, les recherches DNS passent toutes par le fournisseur DoH/DoT. Entre le client et le fournisseur, les données DNS sont chiffrées, mais entre le fournisseur et le serveur DNS, elles ne le sont pas. Le DoH/DoT global canalise efficacement tout le juteux trafic DNS en texte clair dans quelques gros tuyaux mûrs pour l'observation... ou la panne.

De même, si nous maximisons vraiment l'ensemble d'anonymat à grande échelle, tous les sites seraient protégés derrière un seul nom public, comme `cloudflare-ech.com`. C'est bon pour la confidentialité, mais alors tout l'Internet est à la merci de Cloudflare et de ce seul nom de domaine. Maximiser à ce point n'est pas nécessaire ni pratique, mais les implications théoriques restent valables.

Nous recommandons à chaque organisation ou individu de choisir un seul nom pour tous ses sites et de l'utiliser, ce qui devrait offrir dans la plupart des cas une confidentialité suffisante. Cependant, veuillez consulter des experts avec vos modèles de menaces individuels pour votre cas spécifique.


<a id="subdomain-privacy"></a>
#### Confidentialité des sous-domaines

Avec l'ECH, il est désormais théoriquement possible de garder les sous-domaines secrets/privés vis-à-vis des canaux latéraux s'ils sont déployés correctement.

La plupart des sites n'en ont pas besoin car, d'une manière générale, les sous-domaines sont des informations publiques. Nous déconseillons de mettre des informations sensibles dans les noms de domaine. Cela dit...

Pour éviter de divulguer des sous-domaines sensibles dans les journaux de Transparence des Certificats (CT), utilisez plutôt un certificat wildcard. En d'autres termes, au lieu de mettre `sub.example.com` dans votre config, mettez `*.example.com`. (Voir [Certificats Wildcard](#wildcard-certificates) pour des informations importantes.)

Une autre source de fuites est le DNSSEC, que la plupart des serveurs DNS faisant autorité utilisent par défaut. Via une pratique nommée "zone walking", l'énumération des sous-domaines est possible en regardant les enregistrements NSEC, qui sont utilisés pour fournir un déni d'existence authentifié. Pour cela, ils pointent vers le sous-domaine disponible suivant par ordre alphabétique, formant une liste chaînée de tous les enregistrements. Assurez-vous que votre domaine utilise au moins NSEC3 ou idéalement un enregistrement CNAME wildcard pour atténuer ce risque.

Ensuite, activez l'ECH dans Caddy. Un certificat wildcard combiné à l'ECH et un enregistrement CNAME wildcard devrait correctement cacher les sous-domaines, tant que chaque client qui tente de s'y connecter utilise l'ECH et dispose d'une implémentation robuste. (Vous êtes toujours à la merci des clients pour préserver la confidentialité.)


<a id="enabling-ech"></a>
### Activer l'ECH

Puisque le fonctionnement de l'ECH nécessite de publier des configs dans les enregistrements DNS, vous aurez besoin d'un build de Caddy avec un [module caddy-dns](https://github.com/caddy-dns) intégré pour votre fournisseur DNS.

Ensuite, avec un Caddyfile, spécifiez la config de votre fournisseur DNS dans les options globales, ainsi que le nom public ECH que vous souhaitez utiliser :

```caddy
{
	dns <config fournisseur...>
	ech example.com
}
```

Rappelez-vous :

- Le module du fournisseur DNS doit être intégré et vous devez avoir la bonne configuration pour votre fournisseur/compte.
- Le nom public ECH doit pointer vers votre serveur. Caddy obtiendra un certificat pour lui. Il n'a pas besoin d'être l'un des domaines de votre site.

Si vous utilisez JSON, ajoutez ces propriétés à l'application `tls` :

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<nom fournisseur>",
	// configuration fournisseur
}
```

Ces configurations activeront l'ECH et publieront les configs ECH pour tous vos sites. La config JSON offre plus de flexibilité si vous avez besoin de personnaliser le comportement ou si vous avez une installation avancée.

### Vérifier l'ECH

Il n'y a pas encore beaucoup d'outillage autour de l'ECH, donc au moment de rédiger ces lignes, la meilleure et la plus universelle des manières de vérifier qu'il fonctionne est d'utiliser Wireshark et de chercher votre nom public dans le champ ServerName.

Tout d'abord, lancez votre serveur et voyez si les journaux mentionnent quelque chose comme "published ECH configuration list" pour vos domaines. (Si vous avez des erreurs de publication, assurez-vous que votre module de fournisseur DNS supporte [libdns 1.0](https://github.com/libdns/libdns) et ouvrez un ticket sur le dépôt de votre fournisseur si vous rencontrez des problèmes.) Caddy devrait également obtenir un certificat pour le nom public.

Ensuite, assurez-vous que votre navigateur a l'ECH activé ; cela peut nécessiter l'activation du DoH/DoT. C'est aussi une bonne idée de vider le cache DNS de votre navigateur (ou du système), pour s'assurer qu'il récupérera les enregistrements HTTPS nouvellement publiés. Nous recommandons également de fermer le navigateur ou au moins d'ouvrir un nouvel onglet privé pour s'assurer qu'il ne réutilise pas de connexions existantes.

Ensuite, ouvrez Wireshark et commencez à écouter sur l'interface réseau appropriée. Pendant que Wireshark collecte les paquets, chargez votre site dans votre navigateur. Vous pouvez ensuite mettre Wireshark en pause. Trouvez votre ClientHello TLS, et vous devriez voir le _nom public_ dans le champ ServerName, plutôt que le nom de domaine réel auquel vous vous êtes connecté.

Rappelez-vous : vous pouvez toujours voir une extension `encrypted_client_hello` même si l'ECH n'est pas utilisé. L'indicateur clé est la valeur SNI. Vous ne devriez jamais voir le vrai nom du site en texte clair avec Wireshark si l'ECH fonctionne correctement.

Si vous rencontrez des problèmes de déploiement avec l'ECH, demandez d'abord sur notre [forum](https://caddy.community). S'il s'agit d'un bug, vous pouvez [ouvrir un ticket](https://github.com/caddyserver/caddy/issues) sur GitHub.


### ECH dans le stockage

Les configurations ECH sont stockées dans le [répertoire de données](/docs/conventions#data-directory) dans le module de stockage configuré (celui par défaut étant le système de fichiers) sous le dossier `ech/configs`.

Le dossier suivant est un ID de config ECH, qui sont générés aléatoirement et relativement peu importants. Le caractère aléatoire est recommandé par la spécification pour aider à atténuer le fingerprinting/pistage.

Un fichier de métadonnées sidecar aide Caddy à garder une trace du moment où les publications ont eu lieu pour la dernière fois. Cela évite de pilonner votre fournisseur DNS à chaque rechargement de config. Si vous devez réinitialiser cet état, vous pouvez supprimer en toute sécurité le fichier de métadonnées. Cependant, cela peut également réinitialiser le moment où la clé sera rotatée. Vous pouvez également aller dans le fichier et effacer seulement les informations sur la publication.
