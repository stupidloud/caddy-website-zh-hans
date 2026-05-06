---
title: Fonctionnement des journaux (Logging)
---

Fonctionnement des journaux (Logging)
=====================================

Caddy dispose d'installations de journalisation puissantes et flexibles, mais elles peuvent différer de ce dont vous avez l'habitude, surtout si vous venez d'hébergements mutualisés archaïques ou d'autres serveurs web hérités.


## Vue d'ensemble

Il existe deux aspects principaux dans la journalisation : l'émission et la consommation.

L'**émission** signifie la production de messages. Elle se compose de trois étapes :

1. Collecte des informations pertinentes (contexte)
2. Construction d'une représentation utile (encodage)
3. Envoi de cette représentation vers une sortie (écriture)

Cette fonctionnalité est intégrée au cœur de Caddy, permettant à n'importe quelle partie du code source de Caddy ou des modules (plugins) d'émettre des journaux.

La **consommation** est la réception et le traitement des messages. Pour être utiles, les journaux émis doivent être consommés. Des journaux simplement écrits mais jamais lus n'apportent aucune valeur. Consommer des journaux peut être aussi simple qu'un administrateur lisant la sortie console, ou aussi avancé que l'utilisation d'un outil d'agrégation de journaux ou d'un service cloud pour filtrer, compter et indexer les messages.

### Le rôle de Caddy

*Caddy est un émetteur de journaux*. Il ne consomme pas les journaux, à l'exception du traitement minimal requis pour encoder et écrire les journaux. C'est important car cela simplifie le cœur de Caddy, réduit les bugs et les cas particuliers, tout en allégeant la charge de maintenance. En fin de compte, le traitement des journaux sort du cadre du core de Caddy.

Cependant, il est toujours possible de créer un module d'application Caddy qui consomme les journaux (à notre connaissance, il n'en existe pas encore).


## Journaux structurés

Comme la plupart des applications modernes, les journaux de Caddy sont *structurés*. Cela signifie que les informations contenues dans un message ne sont pas simplement une chaîne de caractères ou une tranche d'octets opaque. Au lieu de cela, les données restent fortement typées et sont indexées par des *noms de champs* individuels jusqu'au moment d'encoder le message et de l'écrire.

Comparez les journaux non structurés traditionnels — comme l'archaïque Common Log Format (CLF) — couramment utilisés avec les serveurs HTTP classiques :

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Ce format "a une structure" mais n'est pas "structuré" : il ne peut être utilisé que pour journaliser des requêtes HTTP. Il n'y a pas de moyen (efficace) de l'encoder différemment, car c'est une chaîne d'octets opaque. Il manque également beaucoup d'informations. Il n'inclut même pas l'en-tête Host de la requête ! Ce format de journal n'est utile que lors de l'hébergement d'un seul site, et pour obtenir les informations les plus basiques sur les requêtes.

<aside class="tip">
	L'absence d'informations sur l'hôte dans le CLF est la raison pour laquelle ces journaux doivent généralement être écrits dans des fichiers séparés lors de l'hébergement de plusieurs sites : il n'y a pas d'autre moyen de connaître l'en-tête Host de la requête !
</aside>

Comparez maintenant un message de journal structuré équivalent provenant de Caddy, encodé en JSON et formaté joliment pour l'affichage :

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Vous pouvez voir à quel point le journal structuré est beaucoup plus utile et contient bien plus d'informations. L'abondance d'informations dans ce message n'est pas seulement utile, elle n'entraîne quasiment aucun surcoût de performance : les journaux de Caddy sont sans allocation (zero-allocation). Les journaux structurés n'ont aucune restriction sur les types de données ou le contexte : ils peuvent être utilisés dans n'importe quel chemin de code et inclure tout type d'information.

Parce que les journaux sont structurés et fortement typés, ils peuvent être encodés dans n'importe quel format. Donc, si vous ne voulez pas travailler avec du JSON, les journaux peuvent être encodés dans n'importe quelle autre représentation. Caddy en supporte d'autres via les [modules d'encodage de journaux](/docs/json/logging/logs/encoder/), et d'autres encore peuvent être ajoutés.

**Plus important encore** dans la distinction entre journaux structurés et formats hérités, un journal structuré [peut être transformé en l'ancien Common Log Format <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) au prix d'une pénalité de performance, mais pas l'inverse. Passer du CLF aux formats structurés est complexe (ou du moins inefficace), et impossible compte tenu du manque d'informations.

En essence, une journalisation efficace et structurée promeut généralement ces philosophies :

- Trop de journaux valent mieux que pas assez
- Filtrer vaut mieux que jeter
- Différer l'encodage pour une plus grande flexibilité et interopérabilité
 

## Émission

Dans le code, une émission de journal ressemble à ceci :

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Il s'agit d'une véritable ligne de code provenant du proxy inverse de Caddy. C'est cette ligne qui vous permet d'inspecter les requêtes vers les serveurs d'amont configurés lorsque vous avez activé la journalisation debug. C'est une donnée inestimable lors d'un dépannage !
</aside>

On voit que cet appel de fonction contient le niveau de journalisation, un message et plusieurs champs de données. Tout ceci est fortement typé, et Caddy utilise une bibliothèque de journalisation sans allocation, de sorte que les émissions de journaux sont rapides et efficaces avec presque aucun surcoût.

La variable `logger` est un `zap.Logger` auquel peut être associé n'importe quelle quantité de contexte, incluant à la fois un nom et des champs de données. Cela permet aux loggers d'"hériter" très proprement des contextes parents, autorisant un traçage et des métriques avancés.

À partir de là, le message est envoyé à travers un pipeline de traitement hautement efficace où il est encodé et écrit.


## Pipeline de journalisation

Comme vu précédemment, les messages sont émis par des **loggers**. Les messages sont ensuite envoyés à des **logs** pour traitement.

Caddy vous permet de [configurer plusieurs "logs"](/docs/json/logging/logs/) capables de traiter les messages. Un "log" se compose d'un encodeur (encoder), d'un écrivain (writer), d'un niveau minimal, d'un ratio d'échantillonnage (sampling) et d'une liste de loggers à inclure ou exclure. Dans Caddy, il y a toujours un log par défaut nommé `default`. Vous pouvez le personnaliser en spécifiant un log indexé par `"default"` dans [cet objet](/docs/json/logging/logs/) de la configuration.

<aside class="tip">

Ce serait le bon moment pour [explorer la documentation de la journalisation de Caddy](/docs/json/logging/) afin de vous familiariser avec la structure et les paramètres dont nous parlons.

</aside>


- **Encodeur (Encoder) :** Le format du journal. Transforme la représentation des données en mémoire en une tranche d'octets. Les encodeurs ont accès à tous les champs d'un message.
- **Écrivain (Writer) :** La sortie du journal. Peut être n'importe quel module d'écriture de journal, comme vers un fichier ou un socket réseau. Il écrit simplement des octets.
- **Niveau (Level) :** Les journaux ont différents niveaux, de DEBUG à FATAL. Les messages inférieurs au niveau spécifié seront ignorés par le log.
- **Échantillonnage (Sampling) :** Les chemins extrêmement sollicités peuvent émettre plus de journaux qu'il n'est possible d'en traiter efficacement ; l'activation de l'échantillonnage est un moyen de réduire la charge tout en conservant un échantillon représentatif de messages.
- **Inclure/Exclure :** Chaque message est émis par un logger, qui possède un nom (généralement dérivé de l'ID du module). Les logs peuvent inclure ou exclure les messages de certains loggers.

Lorsqu'un message de journal est émis depuis Caddy :

- Le nom du logger d'origine est vérifié par rapport à la liste d'inclusion/exclusion de chaque log ; s'il est inclus (ou non exclu), il est admis dans ce log.
- Si l'échantillonnage est activé, un calcul rapide détermine s'il faut conserver le message.
- Le message est encodé à l'aide de l'encodeur configuré pour le log.
- Les octets encodés sont ensuite écrits vers l'écrivain configuré pour le log.

Par défaut, tous les messages vont vers tous les logs configurés. Cela respecte les valeurs de la journalisation structurée décrites ci-dessus. Vous pouvez limiter quels messages vont vers quels logs en définissant leurs listes d'inclusion/exclusion, mais c'est principalement pour filtrer les messages de différents modules ; ce n'est pas destiné à être utilisé comme un service d'agrégation de journaux. Pour maintenir l'efficacité du pipeline de journalisation de Caddy, le traitement avancé des messages de journaux est différé à la phase de consommation.

## Consommation

Une fois les messages envoyés vers une sortie, un consommateur va les lire, les analyser et les traiter en conséquence.

Il s'agit d'un domaine de problème très différent de l'émission de journaux, et le cœur de Caddy ne gère pas la consommation (bien qu'un module d'application Caddy puisse tout à fait le faire). Il existe de nombreux outils utilisables pour traiter des flux de messages JSON (ou d'autres formats) et pour visualiser, filtrer, indexer et interroger les journaux. Vous pourriez même écrire ou implémenter le vôtre.

Par exemple, si vous utilisez un logiciel hérité qui nécessite un CLF séparé en différents fichiers basés sur un champ particulier (ex: le nom d'hôte), vous pourriez utiliser ou écrire un outil simple qui lit le JSON, appelle `sprintf()` pour créer une chaîne CLF, puis l'écrit dans un fichier basé sur la valeur du champ `request.host`.

Les installations de journalisation de Caddy peuvent également être utilisées pour implémenter des métriques et du traçage : les métriques comptent essentiellement les messages ayant certaines caractéristiques, et le traçage lie plusieurs messages entre eux sur la base de points communs.

Les possibilités de ce que vous pouvez faire en consommant les journaux de Caddy sont infinies !
