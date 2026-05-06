---
title: Directives du Caddyfile
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

# Directives du Caddyfile

Les directives sont des mots-clés fonctionnels qui apparaissent à l'intérieur des [blocs](/docs/caddyfile/concepts#blocks) de site. Parfois, elles peuvent ouvrir leurs propres blocs pouvant contenir des _sous-directives_, mais les directives **ne peuvent pas** être utilisées à l'intérieur d' autres directives, sauf indication contraire. Par exemple, vous ne pouvez pas utiliser `basic_auth` à l'intérieur d'un bloc `file_server`, car `file_server` ne sait pas comment gérer l'authentification. Cependant, vous *pouvez* utiliser certaines directives à l'intérieur de blocs de directives spéciaux comme `handle` et `route` car ils sont spécifiquement conçus pour regrouper les directives de gestionnaire HTTP.

- [Syntaxe](#syntax)
- [Ordre des directives](#directive-order)
- [Algorithme de tri](#sorting-algorithm)

Les directives suivantes sont fournies en standard avec Caddy, et peuvent être utilisées dans le Caddyfile HTTP :

<div id="directive-table">

Directive | Description
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Interrompt la requête HTTP
**[acme_server](/docs/caddyfile/directives/acme_server)** | Un serveur ACME intégré
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Impose l'authentification HTTP Basic
**[bind](/docs/caddyfile/directives/bind)** | Personnalise l'adresse de socket du serveur
**[encode](/docs/caddyfile/directives/encode)** | Encode (généralement compresse) les réponses
**[error](/docs/caddyfile/directives/error)** | Déclenche une erreur
**[file_server](/docs/caddyfile/directives/file_server)** | Sert des fichiers depuis le disque
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Délègue l'authentification à un service externe
**[fs](/docs/caddyfile/directives/fs)** | Définit le système de fichiers à utiliser pour les E/S fichiers
**[handle](/docs/caddyfile/directives/handle)** | Un groupe de directives mutuellement exclusives
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Définit des routes pour la gestion des erreurs
**[handle_path](/docs/caddyfile/directives/handle_path)** | Comme handle, mais supprime le préfixe du chemin
**[header](/docs/caddyfile/directives/header)** | Définit ou supprime des en-têtes de réponse
**[import](/docs/caddyfile/directives/import)** | Inclut des extraits (snippets) ou des fichiers
**[intercept](/docs/caddyfile/directives/intercept)** | Intercepte les réponses écrites par d'autres gestionnaires
**[invoke](/docs/caddyfile/directives/invoke)** | Invoque une route nommée
**[log](/docs/caddyfile/directives/log)** | Active la journalisation des accès/requêtes
**[log_append](/docs/caddyfile/directives/log_append)** | Ajoute un champ au journal d'accès
**[log_skip](/docs/caddyfile/directives/log_skip)** | Ignore la journalisation des accès pour les requêtes correspondantes
**[log_name](/docs/caddyfile/directives/log_name)** | Surcharge le ou les noms de logger pour l'écriture
**[map](/docs/caddyfile/directives/map)** | Associe une valeur d'entrée à une ou plusieurs sorties
**[method](/docs/caddyfile/directives/method)** | Modifie la méthode HTTP de manière interne
**[metrics](/docs/caddyfile/directives/metrics)** | Configure le point d'accès d'exposition des métriques Prometheus
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Sert des sites PHP via FastCGI
**[push](/docs/caddyfile/directives/push)** | Pousse du contenu vers le client via HTTP/2 server push
**[redir](/docs/caddyfile/directives/redir)** | Émet une redirection HTTP vers le client
**[request_body](/docs/caddyfile/directives/request_body)** | Manipule le corps de la requête
**[request_header](/docs/caddyfile/directives/request_header)** | Manipule les en-têtes de requête
**[respond](/docs/caddyfile/directives/respond)** | Écrit une réponse fixée (hard-coded) vers le client
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Un proxy inverse puissant et extensible
**[rewrite](/docs/caddyfile/directives/rewrite)** | Réécrit la requête de manière interne
**[root](/docs/caddyfile/directives/root)** | Définit le chemin vers la racine du site
**[route](/docs/caddyfile/directives/route)** | Un groupe de directives traitées littéralement comme une seule unité
**[templates](/docs/caddyfile/directives/templates)** | Exécute des modèles (templates) sur la réponse
**[tls](/docs/caddyfile/directives/tls)** | Personnalise les paramètres TLS
**[tracing](/docs/caddyfile/directives/tracing)** | Intégration avec le traçage OpenTelemetry
**[try_files](/docs/caddyfile/directives/try_files)** | Réécriture dépendant de l'existence d'un fichier
**[uri](/docs/caddyfile/directives/uri)** | Manipule l'URI
**[vars](/docs/caddyfile/directives/vars)** | Définit des variables arbitraires

</div>

<a id="syntax"></a>
## Syntaxe

La syntaxe de chaque directive ressemblera à ceci :

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

Les `<chevrons>` indiquent des jetons à remplacer par des valeurs réelles.

Les `[crochets]` indiquent des paramètres optionnels.

Les points de suspension `...` indiquent une continuation, c'est-à-dire un ou plusieurs paramètres ou lignes.

Les sous-directives sont généralement optionnelles, sauf indication contraire, même si elles n'apparaissent pas entre `[crochets]`.


### Sélecteurs (Matchers)

La plupart des directives — mais pas toutes — acceptent des [jetons de sélecteur](/docs/caddyfile/matchers#syntax), qui vous permettent de filtrer les requêtes. Les jetons de sélecteur sont généralement optionnels. Les directives supportent les sélecteurs si vous voyez ceci dans leur syntaxe :

```caddy-d
[<matcher>]
```

Parce que les jetons de sélecteur fonctionnent tous de la même manière, les diverses possibilités pour le jeton de sélecteur ne seront pas décrites sur chaque page afin d'éviter les répétitions. À la place, reportez-vous à la [documentation des sélecteurs](/docs/caddyfile/matchers) pour une explication détaillée de la syntaxe.


<a id="directive-order"></a>
## Ordre des directives

De nombreuses directives manipulent la chaîne de gestionnaires HTTP. L'ordre dans lequel ces directives sont évaluées importe, c'est pourquoi un ordre par défaut est codé en dur dans Caddy.

Vous pouvez surcharger/personnaliser cet ordre en utilisant l'[option globale `order`](/docs/caddyfile/options#order) ou la [directive `route`](/docs/caddyfile/directives/route).

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # uniquement dans le bloc handle_response de reverse_proxy
request_body

redir

# manipulation de la requête entrante
method
rewrite
uri
try_files

# gestionnaires middleware ; certains enveloppent les réponses
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# directives spéciales de routage et de répartition
invoke
handle
handle_path
route

# gestionnaires qui répondent typiquement aux requêtes
abort
error
copy_response # uniquement dans le bloc handle_response de reverse_proxy
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## Algorithme de tri

Pour faciliter l'utilisation, l'adaptateur Caddyfile trie les directives selon les règles suivantes :

- Les directives de noms différents sont triées selon leur position dans l'[ordre par défaut](#directive-order). L'ordre par défaut peut être surchargé avec l'[option globale `order`](/docs/caddyfile/options). Les directives issues de plugins n'ont *pas* d'ordre défini, l'option globale `order` ou la directive `route` doit donc être utilisée pour en définir un.

- Les directives de même nom sont triées selon leurs [sélecteurs](/docs/caddyfile/matchers#syntax).

  - La priorité la plus élevée est accordée à une directive possédant un unique [sélecteur de chemin](/docs/caddyfile/matchers#path-matchers).

    Les sélecteurs de chemin sont triés par spécificité, du plus précis au moins précis.
	
	En général, cela est effectué en triant par la longueur du sélecteur de chemin. Il existe une exception : si le chemin se termine par un `*` et que les chemins des deux sélecteurs sont par ailleurs identiques, le sélecteur sans `*` est considéré comme plus précis et trié plus haut.

    Par exemple :
    - `/foobar` est plus précis que `/foo`
    - `/foo` est plus précis que `/foo*`
    - `/foo/*` est plus précis que `/foo*`

  - Une directive possédant n'importe quel autre sélecteur est triée ensuite, dans l'ordre où elle apparaît dans le Caddyfile.

    Cela inclut les sélecteurs de chemin avec des valeurs multiples, et les [sélecteurs nommés](/docs/caddyfile/matchers#named-matchers).

  - Une directive sans sélecteur (c'est-à-dire correspondant à toutes les requêtes) est triée en dernier.

- La directive [`vars`](/docs/caddyfile/directives/vars) voit son tri par sélecteur inversé, car elle implique la définition de valeurs qui peuvent s'écraser les unes les autres, le sélecteur le plus précis doit donc être évalué en dernier.

- Le contenu de la directive [`route`](/docs/caddyfile/directives/route) ignore toutes les règles ci-dessus et conserve l'ordre dans lequel les directives y apparaissent.
