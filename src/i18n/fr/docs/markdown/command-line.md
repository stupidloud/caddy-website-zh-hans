---
title: "Ligne de commande"
---

# Ligne de commande

Caddy possède une interface en ligne de commande standard de type Unix. L'utilisation de base est la suivante :

```
caddy <commande> [<args...>]
```

Les `<chevrons>` indiquent des paramètres à remplacer par votre saisie.

Les `[crochets]` indiquent des paramètres optionnels. Les `(parenthèses)` indiquent des paramètres requis.

Les points de suspension `...` indiquent une continuation, c'est-à-dire un ou plusieurs paramètres.

Les `--drapeaux` peuvent avoir un raccourci d'une seule lettre comme `-f`.

**Démarrage rapide : `caddy`, `caddy help`, ou `man caddy` (si installé)**

---

- **[caddy adapt](#caddy-adapt)**
  Adapte un document de configuration au format JSON natif

- **[caddy build-info](#caddy-build-info)**
  Affiche les informations de compilation

- **[caddy completion](#caddy-completion)**
  Génère un script de complétion pour le shell

- **[caddy environ](#caddy-environ)**
  Affiche les variables d'environnement

- **[caddy file-server](#caddy-file-server)**
  Un serveur de fichiers simple mais prêt pour la production

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Commande auxiliaire pour exporter le modèle par défaut du navigateur de fichiers

- **[caddy fmt](#caddy-fmt)**
  Formate un Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Hache un mot de passe et l'affiche en base64

- **[caddy help](#caddy-help)**
  Affiche l'aide pour les commandes Caddy

- **[caddy list-modules](#caddy-list-modules)**
  Liste les modules Caddy installés

- **[caddy manpage](#caddy-manpage)**
  Génère des pages de manuel (manpages)

- **[caddy reload](#caddy-reload)**
  Modifie la configuration du processus Caddy en cours d'exécution

- **[caddy respond](#caddy-respond)**
  Un serveur HTTP rapide pour le développement et les tests

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Un proxy inverse HTTP(S) simple mais prêt pour la production

- **[caddy run](#caddy-run)**
  Lance le processus Caddy au premier plan

- **[caddy start](#caddy-start)**
  Lance le processus Caddy en arrière-plan

- **[caddy stop](#caddy-stop)**
  Arrête le processus Caddy en cours d'exécution

- **[caddy storage export](#caddy-storage-export)**
  Exporte le contenu du stockage configuré vers une archive tar

- **[caddy storage import](#caddy-storage-import)**
  Importe une archive tar précédemment exportée vers le stockage configuré

- **[caddy trust](#caddy-trust)**
  Installe un certificat dans le(s) magasin(s) de confiance local(aux)

- **[caddy untrust](#caddy-untrust)**
  Retire la confiance d'un certificat dans le(s) magasin(s) de confiance local(aux)

- **[caddy upgrade](#caddy-upgrade)**
  Met à jour Caddy vers la dernière version

- **[caddy add-package](#caddy-add-package)**
  Met à jour Caddy vers la dernière version, en ajoutant des plugins supplémentaires

- **[caddy remove-package](#caddy-remove-package)**
  Met à jour Caddy vers la dernière version, en retirant certains plugins

- **[caddy validate](#caddy-validate)**
  Vérifie si un fichier de configuration est valide

- **[caddy version](#caddy-version)**
  Affiche la version

- **[Signaux](#signals)**
  Comment Caddy gère les signaux système

- **[Codes de sortie](#exit-codes)**
  Codes émis lorsque le processus Caddy s'arrête

## Sous-commandes


<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;chemin&gt;]
	[-a, --adapter &lt;nom&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Adapte une configuration vers la structure JSON native de Caddy et écrit le résultat sur stdout, ainsi que les éventuels avertissements sur stderr, puis quitte.

`--config` est le chemin vers le fichier de configuration. Si omis, Caddy cherche un `Caddyfile` dans le répertoire courant s'il existe ; sinon, ce drapeau est requis. Si vous souhaitez utiliser stdin plutôt qu'un fichier, utilisez `-` comme chemin.

`--adapter` spécifie l'adaptateur de configuration à utiliser ; par défaut, il s'agit de `caddyfile`.

`--pretty` formatera la sortie avec une indentation pour une meilleure lisibilité humaine.

`--validate` chargera et initialisera la configuration adaptée pour vérifier sa validité (mais ne lancera pas son exécution).

Notez qu'une configuration adaptée avec succès peut tout de même échouer à la validation. Par exemple, avec ce Caddyfile :

```caddy
localhost

tls cert_pasexistant.pem key_pasexistant.pem
```

Si vous l'adaptez :

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

L'opération réussit sans erreur. Essayez ensuite :

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_pasexistant.pem: no such file or directory
</code></pre>

Bien que ce Caddyfile puisse être converti en JSON sans erreur, les fichiers de certificat ou de clé n'existent pas réellement. La validation échoue donc car cette erreur survient lors de la phase d'initialisation (provisioning). Ainsi, la validation est un contrôle d'erreur plus robuste que l'adaptation.

#### Exemple

Pour adapter un Caddyfile en un JSON facile à lire et à ajuster manuellement :

<pre><code class="cmd bash">caddy adapt --config /chemin/vers/Caddyfile --pretty</code></pre>



<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

Affiche les informations fournies par Go concernant la compilation (chemin du module principal, versions des paquets, remplacements de modules).




<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Génère des scripts de complétion pour le shell. Cela permet d'obtenir l'auto-complétion lors de la saisie des commandes `caddy`.

Pour obtenir les instructions d'installation pour votre shell spécifique, lancez `caddy help completion` ou `caddy completion -h`.



<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

Affiche l'environnement tel que vu par Caddy, puis quitte. Utile pour déboguer les systèmes d'initialisation ou les unités de gestionnaire de processus comme systemd.




<a id="caddy-file-server"></a>
### `caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;chemin&gt;]
	[--listen &lt;adresse&gt;]
	[-d, --domain &lt;exemple.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;nombre&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Lance un serveur de fichiers statiques simple mais prêt pour la production.

`--root` spécifie le chemin du répertoire racine. Par défaut, il s'agit du répertoire de travail actuel.

`--listen` accepte une adresse d'écoute. Par défaut : `:80`, sauf si `--domain` est utilisé, auquel cas `:443` sera utilisé.

`--domain` ne servira les fichiers que via ce nom d'hôte, et Caddy tentera de le servir via HTTPS. Assurez-vous que le DNS public est correctement configuré. Le port par défaut passera à 443.

`--browse` active l'affichage du contenu des répertoires si un répertoire sans fichier index est demandé.

`--reveal-symlinks` affiche la cible des liens symboliques dans l'explorateur de fichiers (quand `--browse` est activé).

`--templates` active le rendu des modèles (templates).

`--access-log` active les journaux d'accès.

`--debug` active la journalisation détaillée.

`--file-limit` définit un nombre maximum de fichiers à afficher dans l'explorateur. Par défaut : `10000`. Si le nombre de fichiers dépasse cette limite, seuls les N premiers fichiers seront affichés.

`--no-compress` désactive la compression. Par défaut, Zstandard et Gzip sont activés.

`--precompressed` spécifie les formats d'encodage pour rechercher des fichiers précompressés. Peut être répété pour plusieurs formats. Voir la [directive file_server](/docs/caddyfile/directives/file_server#precompressed).

Cette commande désactive l'API d'administration, ce qui facilite l'exécution de plusieurs instances sur une machine de développement locale.


<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Exporte le modèle par défaut de l'explorateur de fichiers vers stdout.

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;chemin&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Formate ou embellit un Caddyfile, puis quitte. Le résultat est affiché sur stdout sauf si `--overwrite` est utilisé, et quittera avec le code `1` s'il y a des différences.

`<chemin>` spécifie le chemin vers le Caddyfile. Si `-`, l'entrée est lue depuis stdin. Par défaut, Caddy cherche un fichier nommé `Caddyfile` dans le répertoire courant.

`--overwrite` écrit le résultat directement dans le fichier d'entrée au lieu de l'afficher sur le terminal. Si l'entrée n'est pas un fichier régulier, ce drapeau n'a aucun effet.

`--diff` compare la sortie avec l'entrée, et les lignes seront préfixées par `-` et `+` là où elles diffèrent. Notez que les lignes inchangées sont préfixées par deux espaces pour l'alignement, et que ceci n'est pas un format de patch valide ; c'est uniquement un outil visuel.


<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;mot_de_passe&gt;]
	[-a, --algorithm &lt;nom&gt;]
	[--bcrypt-cost &lt;coût&gt;]</code></pre>

Moyen pratique de hacher un mot de passe en texte clair. Le hachage résultant est écrit sur stdout dans un format directement utilisable dans votre configuration Caddy.

`--plaintext`
    Le mot de passe à hacher. Si omis, il sera lu depuis stdin. Si Caddy est attaché à un terminal de contrôle, la saisie ne sera pas affichée.

`--algorithm`
    Sélectionne l'algorithme de hachage. Les options valides sont :
      * `argon2id` (recommandé pour une sécurité moderne)
      * `bcrypt` (hérité, plus lent, coût configurable, coût par défaut `14`)

Paramètres spécifiques à bcrypt :

`--bcrypt-cost`
    Définit la difficulté du hachage bcrypt. Des valeurs plus élevées augmentent la sécurité en rendant le calcul du hachage plus lent et plus intensif pour le CPU. Doit être dans la plage valide [bcrypt.MinCost, bcrypt.MaxCost]. Si omis ou invalide, le coût par défaut est utilisé.

Paramètres spécifiques à Argon2id :

`--argon2id-time`
    Nombre d'itérations à effectuer. Augmenter ceci rend le hachage plus lent et plus résistant aux attaques par force brute.

`--argon2id-memory`
    Quantité de mémoire à utiliser pendant le hachage. Des valeurs plus grandes augmentent la résistance aux attaques par GPU/ASIC.

`--argon2id-threads`
    Nombre de threads CPU à utiliser. Augmenter pour un hachage plus rapide sur les systèmes multi-cœurs.

`--argon2id-keylen`
    Longueur du hachage résultant en octets. Des clés plus longues augmentent la sécurité mais augmentent légèrement la taille de stockage.


<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;commande&gt;]</code></pre>

Affiche l'aide de la CLI, éventuellement pour une sous-commande spécifique, puis quitte.



<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

Affiche les modules Caddy installés, éventuellement avec les informations de paquet et/ou de version de leurs modules Go associés, puis quitte.

Dans certaines situations de script, il peut être redondant d'afficher également tous les modules standard, vous pouvez donc utiliser `--skip-standard` pour les omettre de la sortie.

`--json` affiche les informations au format JSON, ce qui peut être utile pour un traitement programmable.

NOTE : En raison d'un [bug dans Go](https://github.com/golang/go/issues/29228), les informations de version ne sont disponibles que si Caddy est compilé en tant que dépendance et non en tant que module principal. Utilisez [xcaddy](/docs/build#xcaddy) pour faciliter cela.



<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;chemin&gt;)</code></pre>

Génère des pages de manuel/documentation pour les commandes Caddy et les écrit dans le répertoire au chemin spécifié. La sortie de cette commande peut être lue par la commande `man`.

`--directory` (requis) est le chemin du répertoire dans lequel écrire les man pages. Il sera créé s'il n'existe pas.

Une fois générées, les pages de manuel doivent généralement être installées. Cette procédure varie selon la plateforme, mais sur les systèmes Linux typiques, cela ressemble à ceci :

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Vous pouvez ensuite lancer `man caddy` (ou `man caddy-*` pour les sous-commandes) pour lire la documentation dans votre terminal.

Les pages de manuel sont des documentations distinctes de ce qui se trouve sur notre site web. Notre site web possède une documentation plus complète qui est mise à jour souvent.




<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;chemin&gt;]
	[-a, --adapter &lt;nom&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Donne une nouvelle configuration à l'instance Caddy en cours d'exécution. Cela a le même effet que d'envoyer un document POST au [point d'accès /load](/docs/api#post-load), mais cette commande est pratique pour les flux de travail simples basés sur des fichiers de configuration. Comparée aux commandes `stop`, `start` et `run`, cette commande unique est le moyen correct et sémantique de changer/recharger la configuration active.

Parce que cette commande utilise l'API, le point d'accès d'administration ne doit pas être désactivé.

`--config` est le fichier de configuration à appliquer. Si `-`, la configuration est lue depuis stdin. Si non spécifié, elle essaiera un fichier nommé `Caddyfile` dans le répertoire courant et, s'il existe, l'adaptera en utilisant l'adaptateur de configuration `caddyfile` ; sinon, une erreur survient s'il n'y a pas de fichier de configuration à charger.

`--adapter` spécifie un adaptateur de configuration à utiliser, le cas échéant. Ce drapeau n'est pas nécessaire si le nom de fichier `--config` commence par `Caddyfile` ou se termine par `.caddyfile`, ce qui suppose l'adaptateur `caddyfile`. Sinon, ce drapeau est requis si le fichier de configuration fourni n'est pas au format JSON natif de Caddy.

`--address` doit être utilisé si le point d'accès d'administration n'écoute pas sur l'adresse par défaut et s'il est différent de l'adresse dans le fichier de configuration fourni.

`--force` provoquera un rechargement même si la configuration spécifiée est identique à celle déjà active. Peut être utile pour forcer Caddy à ré-initialiser (reprovision) ses modules, ce qui peut avoir des effets secondaires, par exemple : recharger des certificats TLS chargés manuellement.




<a id="caddy-respond"></a>
### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Champ&gt;: &lt;valeur&gt;"]
	[-b, --body &lt;contenu&gt;]
	[-l, --listen &lt;adresse&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


Lance un ou plusieurs serveurs HTTP simples avec une réponse fixe, utiles pour le développement, la pré-production et certains cas d'utilisation de production. Cela peut être utile pour vérifier ou déboguer des clients HTTP, des scripts ou même des répartiteurs de charge (load balancers).

`--status` est le code d'état HTTP à retourner.

`--header` ajoute un en-tête HTTP ; le format `Champ: valeur` est attendu. Ce drapeau peut être utilisé plusieurs fois.

`--body` spécifie le corps de la réponse. Alternativement, le corps peut être passé via un tube (pipe) depuis stdin.

`--listen` est l'adresse d'écoute, qui peut être n'importe quelle [adresse réseau](/docs/conventions#network-addresses) reconnue par Caddy, et peut inclure une plage de ports pour démarrer plusieurs serveurs.

`--debug` active la journalisation de débogage verbeuse.

`--access-log` active la journalisation des accès/requêtes.

Sans option spécifiée, cette commande écoute sur un port aléatoire disponible et répond aux requêtes HTTP par une réponse 200 vide. L'adresse d'écoute peut être personnalisée avec le drapeau `--listen` et sera toujours affichée sur stdout. Si l'adresse d'écoute inclut une plage de ports, plusieurs serveurs seront démarrés.

Si un argument final non nommé est fourni, il sera traité comme un code d'état (identique au drapeau `--status`) s'il s'agit d'un nombre à 3 chiffres. Sinon, il est utilisé comme corps de réponse (identique au drapeau `--body`). Les drapeaux `--status` et `--body` auront toujours la priorité sur cet argument.

Un corps peut être fourni de 3 manières : un drapeau, un argument final (et non nommé) à la commande, ou via un tube depuis stdin (si le drapeau et l'argument ne sont pas définis). Une [évaluation de modèle (template)](https://pkg.go.dev/text/template) limitée est supportée sur le corps, avec les variables suivantes :

Variable | Description
---------|-------------
`.N`       | Numéro du serveur
`.Port`    | Port d'écoute
`.Address` | Adresse d'écoute


#### Exemples

Réponse 200 vide sur un port aléatoire :
<pre><code class="cmd bash">caddy respond</code></pre>

Réponse HTTP avec un corps :
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Serveurs multiples et modèles :
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "Je suis le serveur {{.N}} sur le port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
Je suis le serveur 2 sur le port 2002</code></pre>

Passer une page de maintenance via un tube :
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




<a id="caddy-reverse-proxy"></a>
### `caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;adresse&gt;]
	(-t, --to &lt;adresse&gt;)
	[-H, --header-up "&lt;Champ&gt;: &lt;valeur&gt;"]
	[-d, --header-down "&lt;Champ&gt;: &lt;valeur&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Un proxy inverse simple mais prêt pour la production. Utile pour des déploiements rapides, des démos et du développement.

Transfère simplement le trafic HTTP(S) de l'adresse `--from` vers l'adresse `--to`. Plusieurs adresses `--to` peuvent être spécifiées en répétant le drapeau. Au moins une adresse `--to` est requise. L'adresse `--to` peut avoir une plage de ports comme raccourci pour s'étendre à plusieurs serveurs d'amont (upstreams).

Sauf indication contraire dans les adresses, l'adresse `--from` sera supposée être en HTTPS si un nom d'hôte est fourni, et l'adresse `--to` sera supposée être en HTTP.

Si l'adresse `--from` possède un hôte ou une IP, Caddy tentera de servir le proxy via HTTPS avec un certificat (sauf surcharge par le schéma HTTP ou le port).

Si vous servez du HTTPS : 
  - `--disable-redirects` peut être utilisé pour éviter de se lier au port HTTP.
  - `--internal-certs` peut être utilisé pour forcer l'émission de certificats via la CA interne au lieu de tenter d'émettre un certificat public.

Pour le proxying :
  - `--header-up` peut être utilisé pour définir un en-tête de requête à envoyer vers l'amont.
  - `--header-down` peut être utilisé pour définir un en-tête de réponse à renvoyer au client.
  - `--change-host-header` définit l'en-tête Host de la requête à l'adresse de l'amont, au lieu de conserver par défaut l'en-tête Host entrant. C'est un raccourci pour `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`
  - `--insecure` désactive la vérification TLS avec l'amont. AVERTISSEMENT : CELA DÉSACTIVE LA SÉCURITÉ EN NE VÉRIFIANT PAS LE CERTIFICAT DE L'AMONT.
  - `--debug` active la journalisation verbeuse.

Cette commande désactive l'API d'administration pour faciliter l'exécution de plusieurs instances sur une machine de développement locale.



<a id="caddy-run"></a>
### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;chemin&gt;]
	[-a, --adapter &lt;nom&gt;]
	[--pidfile &lt;fichier&gt;]
	[-e, --environ]
	[--envfile &lt;fichier&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Lance Caddy et bloque indéfiniment ; c'est-à-dire le mode "démon".

`--config` spécifie un fichier de configuration initial à charger et utiliser immédiatement. Si `-`, la configuration est lue depuis stdin. Si aucune configuration n'est spécifiée, Caddy se lancera avec une configuration vide et utilisera les paramètres par défaut pour les [points d'accès de l'API d'administration](/docs/api), qui pourront être utilisés pour lui fournir une nouvelle configuration. Cas particulier : si le répertoire de travail actuel contient un fichier nommé "Caddyfile" et que l'adaptateur de configuration `caddyfile` est présent (par défaut), alors ce fichier sera chargé et utilisé pour configurer Caddy, même sans aucun drapeau de ligne de commande.

`--adapter` est le nom de l'adaptateur de configuration à utiliser lors du chargement de la configuration initiale, le cas échéant. Ce drapeau n'est pas nécessaire si le nom de fichier `--config` commence par `Caddyfile` ou se termine par `.caddyfile`, ce qui suppose l'adaptateur `caddyfile`. Sinon, ce drapeau est requis si le fichier de configuration fourni n'est pas au format JSON natif de Caddy. Tout avertissement sera affiché dans le journal, mais sachez que toute adaptation sans erreur sera immédiatement utilisée, même s'il y a des avertissements. Si vous souhaitez examiner les résultats de l'adaptation au préalable, utilisez la sous-commande [`caddy adapt`](#caddy-adapt).

`--pidfile` écrit le PID dans le fichier spécifié.

`--environ` affiche l'environnement avant de démarrer. C'est la même chose que la commande `caddy environ`, mais ne s'arrête pas après l'affichage.

`--envfile` charge les variables d'environnement depuis le fichier spécifié, au format `CLÉ=VALEUR`. Les commentaires commençant par `#` sont supportés ; les clés peuvent être préfixées par `export` ; les valeurs peuvent être entre guillemets doubles (les guillemets doubles à l'intérieur peuvent être échappés) ; les valeurs multi-lignes sont supportées.

`--resume` utilise la dernière configuration chargée qui a été sauvegardée automatiquement, outrepassant le drapeau `--config` (si présent). L'utilisation de ce drapeau garantit la durabilité de la configuration à travers les redémarrages de la machine ou du processus. Il est particulièrement utile dans les déploiements centrés sur l'[API](/docs/api).

`--watch` surveillera le fichier de configuration et le rechargera automatiquement après chaque modification. ⚠️ Cette fonctionnalité est destinée à être utilisée uniquement dans des environnements de développement local !

<aside class="advice">

N'arrêtez pas le serveur pour changer de configuration lors d'une exécution en production ! Cela entraînera une interruption de service. (Cela devrait être évident mais vous seriez surpris du nombre de plaintes que nous recevons à ce sujet.) Utilisez plutôt la commande [`caddy reload`](#caddy-reload), ou envoyez un signal `SIGUSR1` au processus, ce qui a le même effet que `caddy reload` avec la configuration actuellement chargée.

</aside>



<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;chemin&gt;]
	[-a, --adapter &lt;nom&gt;]
	[--envfile &lt;fichier&gt;]
	[--pidfile &lt;fichier&gt;]
	[-w, --watch]</code></pre>

Identique à [`caddy run`](#caddy-run), mais en arrière-plan. Cette commande ne bloque que jusqu'à ce que le processus en arrière-plan soit lancé avec succès (ou échoue à se lancer), puis elle rend la main.

Note : le drapeau `--config` ne supporte *pas* `-` pour lire la configuration depuis stdin.

L'utilisation de cette commande est déconseillée avec les services système ou sous Windows. Sous Windows, le processus fils restera attaché au terminal, donc fermer la fenêtre arrêtera brutalement Caddy, ce qui n'est pas évident. Envisagez plutôt de faire tourner Caddy [en tant que service](/docs/running).

Une fois démarré, vous pouvez utiliser [`caddy stop`](#caddy-stop) ou le point d'accès API [`POST /stop`](/docs/api#post-stop) pour quitter le processus en arrière-plan.



<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;chemin&gt; [-a, --adapter &lt;nom&gt;]]</code></pre>

<aside class="tip">

L'arrêt (et le redémarrage) du serveur est orthogonal aux changements de configuration. **N'utilisez pas la commande stop pour changer de configuration en production, sauf si vous voulez une interruption de service.** Utilisez plutôt la commande [`caddy reload`](#caddy-reload).

</aside>


Arrête proprement le processus Caddy en cours d'exécution (autre que le processus de la commande stop elle-même) et provoque sa sortie. Elle utilise le point d'accès [`POST /stop`](/docs/api#post-stop) de l'API d'administration pour effectuer un arrêt propre.

L'adresse de cette requête peut être personnalisée en utilisant le drapeau `--address`, ou à partir du `--config` fourni, si le point d'accès d'administration de l'instance en cours n'utilise pas l'adresse d'écoute par défaut.

Si vous voulez arrêter la configuration actuelle mais ne voulez pas quitter le processus, utilisez [`caddy reload`](#caddy-reload) avec une configuration vide, ou le point d'accès [`DELETE /config/`](/docs/api#delete-configpath).


<a id="caddy-storage-export"></a>
<a id="caddy-storage-import"></a>
<a id="caddy-storage"></a>
### `caddy storage`

<i>⚠️ Expérimental</i>

Permet l'exportation et l'importation du contenu du stockage de données configuré de Caddy.

Ceci est utile lors de la transition d'un [module de stockage](/docs/json/storage/) à un autre, en exportant depuis votre ancien module, en mettant à jour votre configuration, puis en important dans le nouveau.

La commande suivante peut être utilisée pour copier le stockage entre différents modules en une seule fois, en utilisant les anciennes et nouvelles configurations, en redirigeant la sortie de la commande d'exportation vers la commande d'importation.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

Veuillez noter que lors de l'utilisation du [stockage sur système de fichiers](/docs/conventions#data-directory), vous devez lancer la commande d'exportation avec le même utilisateur que celui avec lequel Caddy tourne normalement, sinon le mauvais emplacement de stockage pourrait être utilisé.

Par exemple, lorsque Caddy tourne comme un [service systemd](/docs/running#linux-service), il s'exécute en tant qu'utilisateur `caddy`, vous devriez donc lancer les commandes d'exportation ou d'importation avec cet utilisateur. Cela peut généralement être fait avec `sudo -u caddy <commande>`.

</aside>


#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;chemin&gt;
	[-o, --output &lt;chemin&gt;]</code></pre>

`--config` est le fichier de configuration à charger. C'est requis pour que le bon module de stockage soit connecté.

`--output` est le nom du fichier dans lequel écrire l'archive tar. Si `-`, la sortie est écrite sur stdout.



#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;chemin&gt;
	-i, --input &lt;chemin&gt;</code></pre>

`--config` est le fichier de configuration à charger. C'est requis pour que le bon module de stockage soit connecté.

`--input` est le nom du fichier de l'archive tar à lire. Si `-`, l'entrée est lue depuis stdin.


<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;chemin&gt; [-a, --adapter &lt;nom&gt;]]</code></pre>

Installe un certificat racine pour une CA gérée par l'[application PKI](/docs/json/apps/pki/) de Caddy dans les magasins de confiance locaux. 

Caddy tentera d'installer ses certificats racines dans les magasins de confiance locaux automatiquement lorsqu'ils sont générés pour la première fois, mais cela peut échouer si Caddy n'a pas les permissions appropriées pour écrire dans le magasin de confiance. Cette commande est nécessaire pour pré-installer les certificats avant de les utiliser, si le processus serveur s'exécute avec un utilisateur non privilégié (comme via systemd). Vous pourriez avoir besoin de lancer cette commande avec `sudo` sur les systèmes Unix.

Par défaut, cette commande installe le certificat racine pour la CA par défaut de Caddy (c'est-à-dire "local"). Vous pouvez spécifier l'ID d'une autre CA avec le drapeau `--ca`.

Cette commande tentera de se connecter à l'[API d'administration](/docs/api) de Caddy pour récupérer le certificat racine, en utilisant le point d'accès [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates). Vous pouvez explicitement spécifier l'adresse avec `--address`, ou utiliser le drapeau `--config` pour charger l'adresse d'administration depuis votre configuration, si le point d'accès d'administration de l'instance en cours n'utilise pas l'adresse d'écoute par défaut.

Vous pouvez également utiliser le binaire `caddy` avec cette commande pour installer des certificats sur d'autres machines de votre réseau, si l'API d'administration est rendue accessible à d'autres machines — faites attention en faisant cela à ne pas exposer l'API d'administration à des clients non fiables.


<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;chemin&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;chemin&gt; [-a, --adapter &lt;nom&gt;]]</code></pre>

Retire la confiance d'un certificat racine des magasin(s) de confiance local(aux).

Cette commande désinstalle la confiance ; elle ne supprime pas nécessairement le certificat racine entièrement des magasins de confiance. Ainsi, faire confiance et retirer la confiance de nouveaux certificats de manière répétée peut remplir les bases de données de confiance.

Cette commande ne supprime ni ne modifie les fichiers de certificats du stockage configuré de Caddy.

Cette commande peut être utilisée de deux manières :
- En spécifiant un chemin direct vers le certificat racine dont on veut retirer la confiance avec le drapeau `--cert`.
- En récupérant le certificat racine depuis l'[API d'administration](/docs/api) en utilisant le point d'accès [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). C'est le comportement par défaut si aucun drapeau n'est fourni.

Si l'API d'administration est utilisée, alors l'ID de la CA est par défaut "local". Vous pouvez spécifier l'ID d'une autre CA avec le drapeau `--ca`. Vous pouvez explicitement spécifier l'adresse avec `--address`, ou utiliser le drapeau `--config` pour charger l'adresse d'administration depuis votre configuration, si le point d'accès d'administration de l'instance en cours n'utilise pas l'adresse d'écoute par défaut.


<a id="caddy-upgrade"></a>
### `caddy upgrade`

<i>⚠️ Expérimental</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Remplace le binaire Caddy actuel par la dernière version provenant de [notre page de téléchargement](/download) avec les mêmes modules installés, incluant tous les plugins tiers enregistrés sur le site web de Caddy.

Les mises à jour n'interrompent pas les serveurs en cours d'exécution ; actuellement, la commande ne fait que remplacer le binaire sur le disque. Cela pourrait changer à l'avenir si nous trouvons un bon moyen de le faire.

Le processus de mise à jour est tolérant aux pannes ; le binaire actuel est d'abord sauvegardé (copié à côté de l'actuel) et automatiquement restauré si quelque chose se passe mal. Si vous souhaitez conserver la sauvegarde une fois le processus de mise à jour terminé, vous pouvez utiliser l'option `--keep-backup`.

Cette commande peut nécessiter des privilèges élevés si votre utilisateur n'a pas la permission d'écrire sur le fichier exécutable.



<a id="caddy-add-package"></a>
### `caddy add-package`

<i>⚠️ Expérimental</i>

<pre><code class="cmd bash">caddy add-package &lt;paquets...&gt;
	[-k, --keep-backup]</code></pre>

De manière similaire à `caddy upgrade`, remplace le binaire Caddy actuel par la dernière version avec les mêmes modules installés, *plus* les paquets listés en arguments inclus dans le nouveau binaire. Retrouvez la liste des paquets que vous pouvez installer sur [notre page de téléchargement](/download). Chaque argument doit être le nom complet du paquet.

Par exemple :

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



<a id="caddy-remove-package"></a>
### `caddy remove-package`

<i>⚠️ Expérimental</i>

<pre><code class="cmd bash">caddy remove-package &lt;paquets...&gt;
	[-k, --keep-backup]</code></pre>

De manière similaire à `caddy upgrade`, remplace le binaire Caddy actuel par la dernière version avec les mêmes modules installés, mais *sans* les paquets listés en arguments, s'ils existaient dans le binaire actuel. Lancez `caddy list-modules --packages` pour voir la liste des noms de paquets des modules non-standard inclus dans le binaire actuel.



<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;chemin&gt;]
	[-a, --adapter &lt;nom&gt;]
	[--envfile &lt;fichier&gt;]</code></pre>

Valide un fichier de configuration puis quitte. Cette commande désérialise la configuration, puis charge et initialise (provision) tous ses modules comme pour lancer la configuration, mais celle-ci n'est pas réellement lancée. Cela expose les erreurs dans une configuration qui surviennent pendant les phases de chargement ou d'initialisation et constitue un contrôle d'erreur plus fort qu'une simple sérialisation d'une configuration en JSON.

`--config` est le fichier de configuration à valider. Si `-`, la configuration est lue depuis stdin. Par défaut, il s'agit du `Caddyfile` dans le répertoire courant, le cas échéant.

`--adapter` est le nom de l'adaptateur de configuration à utiliser. Ce drapeau n'est pas nécessaire si le nom de fichier `--config` commence par `Caddyfile` ou se termine par `.caddyfile`, ce qui suppose l'adaptateur `caddyfile`. Sinon, ce drapeau est requis si le fichier de configuration fourni n'est pas au format JSON natif de Caddy.

`--envfile` charge les variables d'environnement depuis le fichier spécifié, au format `CLÉ=VALEUR`. Les commentaires commençant par `#` sont supportés ; les clés peuvent être préfixées par `export` ; les valeurs peuvent être entre guillemets doubles (les guillemets doubles à l'intérieur peuvent être échappés) ; les valeurs multi-lignes sont supportées.



<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

Affiche la version et quitte.



<a id="signals"></a>
## Signaux

Caddy intercepte certains signaux et en ignore d'autres. Les signaux peuvent initier des comportements spécifiques du processus.

Signal | Comportement
-------|----------
`SIGINT` | Sortie propre (graceful). Renvoyez le signal pour forcer la sortie immédiatement.
`SIGQUIT` | Quitte Caddy immédiatement, mais nettoie tout de même les verrous en stockage car c'est important.
`SIGTERM` | Sortie propre (graceful).
`SIGUSR1` | Recharge le fichier de configuration, mais uniquement s'il a été lancé avec `caddy run` (sans `--resume`) et qu'aucune modification de la configuration n'a été effectuée via [l'API](/docs/api) (incluant [`caddy reload`](#caddy-reload)).
`SIGUSR2` | Ignoré.
`SIGHUP` | Ignoré.

Une sortie propre signifie que les nouvelles connexions ne sont plus acceptées, et les connexions existantes seront drainées avant que le socket ne soit fermé. Un délai de grâce peut s'appliquer (et est configurable). Une fois le délai de grâce écoulé, les connexions seront interrompues brutalement. Les verrous en stockage et les autres ressources que les modules individuels doivent libérer sont nettoyés lors d'un arrêt propre.

Lorsqu'un signal de rechargement de configuration (`SIGUSR1`) est reçu, il agit comme un rechargement forcé de la configuration (c'est-à-dire un rechargement même si le texte de la configuration est inchangé) qui peut recharger les fichiers dépendants comme les certificats TLS depuis le disque. 

Les rechargements de configuration basés sur les signaux ne sont activés que si Caddy est lancé avec `caddy run` avec un fichier de configuration. Ils deviennent désactivés (signaux ignorés, avec un avertissement dans le journal) si Caddy est lancé avec `--resume` (puisqu'il implique un flux de travail via l'API), ou si un changement de configuration est reçu via l'API d'administration, ou si `caddy reload` est lancé avec un nom de fichier ou un adaptateur de configuration *différent* de celui de départ. Ceci est fait pour éviter les conflits entre les méthodes de rechargement.



<a id="exit-codes"></a>
## Codes de sortie

Caddy retourne un code lorsque le processus se termine :

Code | Signification
-----|---------
`0` | Sortie normale.
`1` | Échec au démarrage. **Ne redémarrez pas automatiquement le processus ; il y aura probablement une nouvelle erreur à moins que des modifications ne soient apportées.**
`2` | Sortie forcée. Caddy a été forcé de quitter sans nettoyage des ressources.
`3` | Sortie en échec. Caddy a quitté avec des erreurs pendant le nettoyage.

En bash, vous pouvez obtenir le code de sortie de la dernière commande avec `echo $?`.
