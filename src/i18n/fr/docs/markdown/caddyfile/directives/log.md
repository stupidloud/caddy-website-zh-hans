---
title: log (directive Caddyfile)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.textContent.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Nous ajouterons des liens vers toutes les sous-directives si une ancre correspondante est trouvée sur la page.
	addLinksToSubdirectives();
});
</script>

# log

Active et configure la journalisation des requêtes HTTP (également appelée journaux d'accès ou access logs).

<aside class="tip">

Pour configurer les journaux d'exécution de Caddy, consultez plutôt l' [option globale `log`](/docs/caddyfile/options#log).

</aside>


La directive `log` s'applique aux noms d'hôte du bloc de site dans lequel elle apparaît, sauf surcharge avec la sous-directive `hostnames`.

Lorsqu'elle est configurée, toutes les requêtes vers le site sont journalisées par défaut. Pour ignorer conditionnellement certaines requêtes, utilisez la [directive `log_skip`](log_skip).

Pour ajouter des champs personnalisés aux entrées de journal, utilisez la [directive `log_append`](log_append).


- [Syntaxe](#syntax)
- [Modules de sortie (Output)](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [Modules de format](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [Exemples](#examples)

Par défaut, les en-têtes contenant des informations potentiellement sensibles (`Cookie`, `Set-Cookie`, `Authorization` et `Proxy-Authorization`) seront journalisés en tant que `REDACTED` dans les journaux d'accès. Ce comportement peut être désactivé avec l'option globale de serveur [`log_credentials`](/docs/caddyfile/options#log-credentials).


<a id="syntax"></a>
## Syntaxe

```caddy-d
log [<logger_name>] {
	hostnames <noms_hôte...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <niveau>
	sampling {
		interval   <durée>
		first      <nombre>
		thereafter <nombre>
	}
}
```

- **logger_name** <span id="logger_name"/> est une surcharge optionnelle du nom du logger pour ce site.

  Par défaut, un nom de logger est généré automatiquement, ex: `log0`, `log1`, et ainsi de suite selon l'ordre des sites dans le Caddyfile. Ceci est utile uniquement si vous souhaitez vous référer de manière fiable à la sortie de ce logger depuis un autre logger défini dans les options globales. Voir [un exemple](#multiple-outputs) ci-dessous.

- **hostnames** <span id="hostnames"/> est une surcharge optionnelle des noms d'hôte auxquels ce logger s'applique.

  Par défaut, le logger s'applique aux noms d'hôte du bloc de site dans lequel il apparaît, c'est-à-dire les adresses du site. C'est utile si vous souhaitez définir des loggers différents par sous-domaine dans un [bloc de site wildcard](/docs/caddyfile/patterns#wildcard-certificates). Voir [un exemple](#wildcard-logs) ci-dessous.

- **no_hostname** <span id="no_hostname"/> empêche le logger d'être associé à l'un des noms d'hôte du bloc de site. Par défaut, le logger est associé à l' [adresse du site](/docs/caddyfile/concepts#addresses) dans laquelle la directive `log` apparaît.

  Ceci est utile lorsque vous souhaitez journaliser les requêtes dans des fichiers différents selon une condition, comme le chemin ou la méthode de la requête, en utilisant la [directive `log_name`](/docs/caddyfile/directives/log_name).

- **output** <span id="output"/> configure l'endroit où écrire les journaux. Voir les [modules `output`](#output-modules) ci-dessous.

  Par défaut : `stderr`.

- **format** <span id="format"/> décrit comment encoder, ou formater, les journaux. Voir les [modules `format`](#format-modules) ci-dessous.

  Par défaut : `console` si `stderr` est détecté comme étant un terminal, `json` sinon.

- **level** <span id="level"/> est le niveau d'entrée minimal à journaliser. Par défaut : `INFO`.

  Notez que les journaux d'accès n'émettent actuellement que des journaux de niveau `INFO` et `ERROR`.

- **sampling** <span id="sampling"/> configure l'échantillonnage des journaux pour réduire le volume. Si l'échantillonnage est spécifié, il est activé avec les valeurs par défaut ci-dessous. L'omettre désactive l'échantillonnage.

  - **interval** est la [fenêtre de durée](/docs/conventions#durations) sur laquelle effectuer l'échantillonnage. Par défaut : `1s` (désactivé).

  - **first** est le nombre de journaux à conserver au sein d'un niveau et d'un message donnés pour chaque intervalle. Par défaut : `100`.

  - **thereafter** est le nombre de journaux à ignorer dans chaque intervalle après les premiers journaux conservés. Par défaut : `100`.

  Par exemple, avec `interval 1s`, `first 5`, et `thereafter 10`, dans chaque intervalle de 10 secondes, les 5 premières entrées de journal seront conservées, puis une entrée de journal sur 10 avec le même niveau et le même message sera autorisée à passer pendant cette seconde.


<a id="output-modules"></a>
### Modules de sortie (Output)

La sous-directive **output** vous permet de personnaliser l'endroit où les journaux sont écrits.

#### stderr

Erreur standard (console, c'est le défaut).

```caddy-d
output stderr
```

#### stdout

Sortie standard (console).

```caddy-d
output stdout
```

#### discard

Pas de sortie.

```caddy-d
output discard
```

#### file

Un fichier. Par défaut, les fichiers de journal subissent une rotation (sont "roulés") en fonction de leur taille pour éviter l'épuisement de l'espace disque.

La rotation des journaux est fournie par [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack)

<aside class="tip">

**Note sur le rechargement des options de fichier de journal :** Un redémarrage du serveur est nécessaire pour appliquer les changements de configuration à un fichier de sortie donné.
Les changements ne seront pas appliqués lors d'un rechargement (reload) du serveur, sauf si vous ajoutez un nouveau nom de fichier de journal.

</aside>

```caddy-d
output file <nom_fichier> {
	mode          <mode>
	roll_disabled
	roll_size     <taille>
	roll_interval <durée>
	roll_minutes  <minutes...>
	roll_at	      <heures...>
	roll_uncompressed
	roll_local_time
	roll_keep     <nombre>
	roll_keep_for <jours>
	backup_time_format <format>
}
```

- **&lt;nom_fichier&gt;** est le chemin vers le fichier de journal.

  Lors de la rotation, les fichiers sont renommés en utilisant le modèle `<nom>-<timestamp>-<raison>.log`. Le timestamp est formaté selon l'option [`backup_time_format`](#backup_time_format). La raison est soit `size` (taille), soit `time` (temps), selon ce qui a déclenché la rotation. Si le fichier est compressé, `.gz` est ajouté au nom du fichier.

   Par exemple, si le nom de fichier est `access.log`, un fichier tourné pourrait être nommé `access-2026-01-30T22-15-42.123-size.log` s'il a été tourné à cause de sa taille, ou `access-2025-01-30T00-00-00.000-time.log` s'il l'a été à cause du temps écoulé.

- **mode** <span id="mode"/> est le mode/permissions de fichier Unix à utiliser pour le fichier de journal. Le mode se compose de 1 à 4 chiffres octaux (identique au format numérique accepté par la commande Unix [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://fr.wikipedia.org/wiki/Chmod), sauf qu'un mode tout à zéro est interprété comme le mode par défaut `600`).

  Par exemple : `0600` définirait le mode à `rw-,---,---` (accès en lecture/écriture au propriétaire du fichier, et aucun accès pour les autres) ; `0640` définirait le mode à `rw-,r--,---` (accès en lecture/écriture au propriétaire, lecture seule pour le groupe) ; `644` définit le mode à `rw-,r--,r--` offrant un accès en lecture/écriture au propriétaire, mais seulement un accès en lecture au groupe et aux autres utilisateurs.

- **roll_disabled** <span id="roll_disabled"/> désactive la rotation des journaux. Cela peut mener à une saturation du disque, n'utilisez donc ceci que si vos fichiers de journal sont gérés par un autre moyen.

- **roll_size** <span id="roll_size"/> est la taille à laquelle effectuer la rotation du fichier. L'implémentation actuelle supporte une résolution au mégaoctet ; les valeurs fractionnaires sont arrondies au mégaoctet entier supérieur. Par exemple, `1.1MiB` est arrondi à `2MiB`.

  Ceci est toujours activé. Si une écriture dans les journaux fait que le fichier dépasse la taille spécifiée, le journal subira immédiatement une rotation. Le nom du fichier de sauvegarde inclura `size` comme raison.

  Par défaut : `100MiB`.

- **roll_interval** <span id="roll_interval"/> est la durée maximale entre deux rotations de journaux. La valeur est une [chaîne de durée](/docs/conventions#durations) après laquelle effectuer la rotation.

  Lorsqu'elle est activée, le fichier subit une rotation lors de la prochaine écriture dans les journaux après que cette durée s'est écoulée depuis la dernière rotation. Le nom du fichier de sauvegarde inclura `time` comme raison.

  Notez que si réglé sur `24h`, il n'y a pas forcément de rotation à minuit, mais plutôt à la marque des 24 heures depuis la dernière rotation. Si une rotation se produit à cause de la taille, alors l'heure de la prochaine rotation sera décalée par rapport à la précédente. Vous pouvez utiliser les options `roll_at` ou `roll_minutes` pour effectuer des rotations à des heures spécifiques à la place.

  Par défaut : désactivé.

- **roll_minutes** <span id="roll_minutes"/> est une liste de valeurs de minutes (0-59) auxquelles effectuer la rotation du fichier. Par exemple, `10 40` ferait tourner le fichier toutes les 30 minutes à `xx:10` et `xx:40` de chaque heure. Les rotations sont alignées sur la minute de l'horloge (seconde 0).

  L'activation de ceci lance un minuteur goroutine qui déclenche une rotation aux minutes spécifiées (c'est-à-dire que cela introduit un peu de traitement en arrière-plan). Ceci s'ajoute à `roll_interval` et `roll_size`. Le nom du fichier de sauvegarde inclura `time` comme raison.

  Par défaut : désactivé.

- **roll_at** <span id="roll_at"/> est une liste de valeurs d'heures (au format 24 heures) auxquelles effectuer la rotation du fichier. Par exemple, `00:00 12:00` ferait tourner le fichier deux fois par jour, à minuit et à midi. Les rotations sont alignées sur la minute de l'horloge (seconde 0).

  L'activation de ceci lance un minuteur goroutine qui déclenche une rotation aux heures spécifiées (c'est-à-dire que cela introduit un peu de traitement en arrière-plan). Ceci s'ajoute à `roll_interval` et `roll_size`. Le nom du fichier de sauvegarde inclura `time` comme raison.

  Par défaut : désactivé.

- **roll_uncompressed** <span id="roll_uncompressed"/> désactive la compression gzip des journaux.

  Par défaut : la compression `gzip` est activée.

- **roll_local_time** <span id="roll_local_time"/> règle la rotation pour utiliser les timestamps locaux dans les noms de fichiers. 
  Par défaut : utilise l'heure UTC.

- **roll_keep** <span id="roll_keep"/> est le nombre de fichiers de journal à conserver avant de supprimer les plus anciens. Se déclenche lorsqu'un nouveau fichier de journal est créé.

  Par défaut : `10`.

- **roll_keep_for** <span id="roll_keep_for"/> est la durée de conservation des fichiers tournés sous forme de [chaîne de durée](/docs/conventions#durations). Se déclenche lorsqu'un nouveau fichier de journal est créé.
  L'implémentation actuelle supporte une résolution à la journée ; les valeurs fractionnaires sont arrondies au jour entier supérieur. Par exemple, `36h` (1,5 jour) est arrondi à `48h` (2 jours).
  
  Par défaut : `2160h` (90 jours).

- **backup_time_format** <span id="backup_time_format"/> est le format d'heure à utiliser dans les noms de fichiers de sauvegarde. Doit être une chaîne de mise en page (layout) d'heure valide ; consultez la [documentation Go](https://pkg.go.dev/time#pkg-constants) pour les détails complets.

  Par défaut : `2006-01-02T15-04-05`.


#### net

Un socket réseau. Si le socket tombe, il enverra les journaux vers stderr tout en tentant de se reconnecter.

```caddy-d
output net <adresse> {
	dial_timeout <durée>
	soft_start
}
```

- **&lt;adresse&gt;** est l'[adresse](/docs/conventions#network-addresses) vers laquelle écrire les journaux.

- **dial_timeout** <span id="dial_timeout"/> est la durée d'attente maximale pour une connexion réussie au socket du journal. Les émissions de journaux peuvent être bloquées pendant cette durée si le socket tombe.

- **soft_start** <span id="soft_start"/> ignorera les erreurs lors de la connexion au socket, vous permettant de charger votre configuration même si le service de journalisation distant est indisponible. Les journaux seront émis vers stderr à la place.


<a id="format-modules"></a>
### Modules de format

La sous-directive **format** vous permet de personnaliser la manière dont les journaux sont encodés (formatés). Elle apparaît à l'intérieur d'un bloc `log`.

<aside class="tip">

**Note sur le Common Log Format (CLF) :** Le CLF entre en conflit avec les journaux structurés modernes. Pour transformer vos journaux d'accès vers le format CLF (obsolète), veuillez utiliser le [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder).

</aside>


En plus de la syntaxe propre à chaque encodeur, ces propriétés communes peuvent être définies sur la plupart des encodeurs :

```caddy-d
format <encoder_module> {
	message_key     <cle>
	level_key       <cle>
	time_key        <cle>
	name_key        <cle>
	caller_key      <cle>
	stacktrace_key  <cle>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> La clé pour le champ de message de l'entrée de journal. Par défaut : `msg`.

- **level_key** <span id="level_key"/> La clé pour le champ de niveau de l'entrée de journal. Par défaut : `level`.

- **time_key** <span id="time_key"/> La clé pour le champ de temps de l'entrée de journal. Par défaut : `ts`.
- **name_key** <span id="name_key"/> La clé pour le champ de nom de l'entrée de journal. Par défaut : `name`.

- **caller_key** <span id="caller_key"/> La clé pour le champ d'appelant (caller) de l'entrée de journal.

- **stacktrace_key** <span id="stacktrace_key"/> La clé pour le champ de trace de pile (stacktrace) de l'entrée de journal.

- **line_ending** <span id="line_ending"/> La fin de ligne à utiliser.

- **time_format** <span id="time_format"/> Le format pour les timestamps.
  Par défaut : `wall_milli` si le format est par défaut `console`, `unix_seconds_float` sinon.
  
  Peut être l'un des suivants :
  - `unix_seconds_float` Nombre à virgule flottante de secondes depuis l'époque Unix.
  - `unix_milli_float` Nombre à virgule flottante de millisecondes depuis l'époque Unix.
  - `unix_nano` Nombre entier de nanosecondes depuis l'époque Unix.
  - `iso8601` Exemple : `2006-01-02T15:04:05.000Z0700`.
  - `rfc3339` Exemple : `2006-01-02T15:04:05Z07:00`.
  - `rfc3339_nano` Exemple : `2006-01-02T15:04:05.999999999Z07:00`.
  - `wall` Exemple : `2006/01/02 15:04:05`.
  - `wall_milli` Exemple : `2006/01/02 15:04:05.000`.
  - `wall_nano` Exemple : `2006/01/02 15:04:05.000000000`.
  - `common_log` Exemple : `02/Jan/2006:15:04:05 -0700`.
  - Ou n'importe quelle chaîne de mise en page d'heure compatible ; consultez la [documentation Go](https://pkg.go.dev/time#pkg-constants) pour les détails complets.
  
  Notez que les parties de la chaîne de format sont des constantes spéciales pour la mise en page ; ainsi `2006` est l'année, `01` est le mois, `Jan` est le mois sous forme de chaîne, `02` est le jour. N'utilisez pas les chiffres de la date actuelle réelle dans la chaîne de format.

- **time_local** <span id="time_local"/> Journalise avec l'heure locale du système plutôt que l'heure UTC par défaut.

- **duration_format** <span id="duration_format"/> Le format pour les durées.

  Par défaut : `seconds`.
  
  Peut être l'un des suivants :
  - `s`, `second` ou `seconds` Nombre à virgule flottante de secondes écoulées.
  - `ms`, `milli` ou `millis` Nombre à virgule flottante de millisecondes écoulées.
  - `ns`, `nano` ou `nanos` Nombre entier de nanosecondes écoulées.
  - `string` En utilisant le format de chaîne intégré de Go, par exemple `1m32.05s` ou `6.31ms`.

- **level_format** <span id="level_format"/> Le format pour les niveaux.

  Par défaut : `color` si le format est par défaut `console`, `lower` sinon.
  
  Peut être l'un des suivants :
  - `lower` Minuscule.
  - `upper` Majuscule.
  - `color` Majuscule, avec couleurs ANSI.
  

#### console

L'encodeur console formate l'entrée de journal pour la lisibilité humaine tout en préservant une certaine structure.

```caddy-d
format console
```

#### json

Formate chaque entrée de journal comme un objet JSON.

```caddy-d
format json
```


#### filter

Permet un filtrage par champ.

```caddy-d
format filter {
	fields {
		<champ> <filtre> ...
	}
	<champ> <filtre> ...
	wrap <module_encodage> ...
}
```

Les champs imbriqués peuvent être référencés en représentant une couche d'imbrication avec `>`. En d'autres termes, pour un objet comme `{"a":{"b":0}}`, le champ intérieur peut être référencé par `a>b`.

Les champs suivants sont fondamentaux pour le journal et ne peuvent pas être filtrés car ils sont ajoutés par la bibliothèque de journalisation sous-jacente comme des cas particuliers : `ts`, `level`, `logger`, et `msg`.

Spécifier `wrap` est optionnel ; si omis, un défaut est choisi selon que le module de sortie actuel est [`stderr`](#stderr) ou [`stdout`](#stdout), et est un terminal interactif, auquel cas [`console`](#console) est choisi, sinon [`json`](#json) est choisi.

Comme raccourci, le bloc `fields` peut être omis et les filtres peuvent être spécifiés directement à l'intérieur du bloc `filter`.


Voici les filtres disponibles :

##### delete

Marque un champ pour être ignoré lors de l'encodage.

```caddy-d
<champ> delete
```


##### rename

Renomme la clé d'un champ de journal.

```caddy-d
<champ> rename <cle>
```


##### replace

Marque un champ pour être remplacé par la chaîne fournie au moment de l'encodage.

```caddy-d
<champ> replace <remplacement>
```


<a id="ip-mask"></a>
##### ip_mask

Masque les adresses IP dans le champ en utilisant un masque CIDR, c'est-à-dire le nombre de bits de l'IP à conserver en partant de la gauche. Si le champ est un tableau de chaînes (ex: en-têtes HTTP), chaque valeur du tableau est masquée. La valeur peut être une chaîne d'adresses IP séparées par des virgules.

Il existe une configuration séparée pour les adresses IPv4 et IPv6, car elles possèdent un nombre total de bits différent.

Le plus souvent, les champs à filtrer sont :
- `request>remote_ip` pour le client se connectant directement
- `request>client_ip` pour le "client réel" analysé lorsque [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) est configuré
- `request>headers>X-Forwarded-For` si vous êtes derrière un proxy inverse

```caddy-d
<champ> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query

Marque un champ pour y effectuer une ou plusieurs actions afin de manipuler la partie requête (query) d'un champ URL. Le plus souvent, le champ à filtrer est `request>uri`.

```caddy-d
<champ> query {
	delete  <cle>
	replace <cle> <remplacement>
	hash    <cle>
}
```

Les actions disponibles sont :

- **delete** supprime la clé donnée de la requête.

- **replace** remplace la valeur de la clé de requête donnée par **remplacement**. Utile pour insérer un espace réservé de caviardage (redaction) ; vous verrez que la clé de requête était dans l'URL, mais la valeur est cachée.

- **hash** remplace la valeur de la clé de requête donnée par les 4 premiers octets du hachage SHA-256 de la valeur, en hexadécimal minuscule. Utile pour obscurcir la valeur si elle est sensible, tout en étant capable de remarquer si chaque requête avait une valeur différente.


##### cookie

Marque un champ pour y effectuer une ou plusieurs actions afin de manipuler la valeur d'un en-tête HTTP `Cookie`. Le plus souvent, le champ à filtrer est `request>headers>Cookie`.

```caddy-d
<champ> cookie {
	delete  <nom>
	replace <nom> <remplacement>
	hash    <nom>
}
```

Les actions disponibles sont :

- **delete** supprime le cookie donné par son nom de l'en-tête.

- **replace** remplace la valeur du cookie donné par **remplacement**. Utile pour insérer un espace réservé de caviardage ; vous verrez que le cookie était dans l'en-tête, mais la valeur est cachée.

- **hash** remplace la valeur du cookie donné par les 4 premiers octets du hachage SHA-256 de la valeur, en hexadécimal minuscule. Utile pour obscurcir la valeur si elle est sensible, tout en étant capable de remarquer si chaque requête avait une valeur différente.

Si plusieurs actions sont définies pour le même nom de cookie, seule la première action sera appliquée.


##### regexp

Applique un remplacement par expression régulière sur un champ au moment de l'encodage. Si le champ est un tableau de chaînes (ex: en-têtes HTTP), les remplacements sont appliqués à chaque valeur du tableau.

```caddy-d
<champ> regexp <motif> <remplacement>
```

Le langage d'expression régulière utilisé est RE2, inclus dans Go. Voir la [référence de syntaxe RE2](https://github.com/google/re2/wiki/Syntax) et l' [aperçu de la syntaxe regexp de Go](https://pkg.go.dev/regexp/syntax).

Dans la chaîne de remplacement, les groupes de capture peuvent être référencés par `${group}` où `group` est soit le nom, soit le numéro du groupe de capture dans l'expression. Le groupe de capture `0` est la correspondance regexp complète, `1` est le premier groupe de capture, `2` est le second, et ainsi de suite.


##### hash

Marque un champ pour être remplacé par les 4 premiers octets (8 caractères hexadécimaux) du hachage SHA-256 de la valeur au moment de l'encodage. Si le champ est un tableau de chaînes (ex: en-têtes HTTP), chaque valeur du tableau est hachée.

Utile pour obscurcir la valeur si elle est sensible, tout en étant capable de remarquer si chaque requête avait une valeur différente.

```caddy-d
<champ> hash
```

#### append

Ajoute un ou plusieurs champ(s) à toutes les entrées de journal.

```caddy-d
format append {
	fields {
		<champ> <valeur>
	}
	<champ> <valeur>
	wrap <module_encodage> ...
}
```

C'est particulièrement utile pour ajouter des informations sur l'instance Caddy produisant les entrées de journal, éventuellement via une variable d'environnement. Les valeurs de champs peuvent être des espaces réservés globaux (ex: `{env.*}`), mais *pas* des espaces réservés par requête car les journaux sont écrits en dehors du contexte de la requête HTTP.

Spécifier `wrap` est optionnel ; si omis, un défaut est choisi selon que le module de sortie actuel est [`stderr`](#stderr) ou [`stdout`](#stdout), et est un terminal interactif, auquel cas [`console`](#console) est choisi, sinon [`json`](#json) est choisi.

Le bloc `fields` peut être omis et les filtres peuvent être spécifiés directement à l'intérieur du bloc `append`.


<a id="examples"></a>
## Exemples

Activer la journalisation des accès vers le logger par défaut.

En d'autres termes, par défaut cela journalise vers `stderr`, mais ceci peut être modifié en reconfigurant le logger `default` avec l' [option globale `log`](/docs/caddyfile/options#log) :

```caddy
example.com {
	log
}
```


Écrire les journaux dans un fichier (avec rotation des journaux, activée par défaut) :

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


Personnaliser la rotation des journaux, avec une rotation quotidienne à minuit ou lorsque le fichier atteint 1 Go (selon ce qui arrive en premier), et conserver 5 fichiers tournés ou 30 jours de journaux :

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


Supprimer l'en-tête de requête `User-Agent` des journaux :

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


Caviarder plusieurs cookies sensibles. (Notez que certains en-têtes sensibles sont journalisés avec des valeurs vides par défaut ; voir l' [option globale `log_credentials`](/docs/caddyfile/options#log-credentials) pour activer la journalisation des valeurs de l'en-tête `Cookie`) :

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


Masquer l'adresse distante de la requête, en conservant les 16 premiers bits (ex: 255.255.0.0) pour les adresses IPv4, et les 32 premiers bits pour les adresses IPv6.

Notez que depuis Caddy v2.7, `remote_ip` et `client_ip` sont tous deux journalisés, où `client_ip` est l'"IP réelle" lorsque [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) est configuré :

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


Pour ajouter un ID de serveur provenant d'une variable d'environnement à toutes les entrées de journal, et le chaîner avec un `filter` pour supprimer un en-tête :

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> Pour écrire des fichiers de journal séparés pour chaque sous-domaine dans un [bloc de site wildcard](/docs/caddyfile/patterns#wildcard-certificates), en surchargeant `hostnames` pour chaque logger. Ceci utilise un [extrait (snippet)](/docs/caddyfile/concepts#snippets) pour éviter la répétition :

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> Pour écrire les journaux d'accès d'un sous-domaine particulier dans deux fichiers différents, avec des formats différents (l'un avec le [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) et l'autre avec [`json`](#json)). 

Ceci fonctionne en surchargeant le nom du logger par `foo` dans le bloc de site, puis en incluant les journaux d'accès produits par ce logger dans les deux loggers des options globales avec `include http.log.access.foo` :

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> Pour réduire le volume des journaux avec l'échantillonnage, par exemple pour conserver les 5 premières requêtes par seconde, puis 1 requête sur 10 par la suite :

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
