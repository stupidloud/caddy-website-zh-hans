---
title: root (Caddyfile directive)
---

# root

Setzt den Root-Pfad der Site, der von verschiedenen Matchern und Direktiven verwendet wird, die auf das Dateisystem zugreifen. Wenn er nicht gesetzt ist, ist das Standard-Site-Root das aktuelle Arbeitsverzeichnis.

Konkret setzt diese Direktive den Platzhalter `{http.vars.root}`. Sie ist gegenseitig exklusiv zu anderen `root`-Direktiven im selben Block. Dadurch ist es sicher, mehrere Roots mit sich überschneidenden Matchern zu definieren: Sie werden nicht kaskadieren und einander überschreiben.

Diese Direktive aktiviert nicht automatisch das Ausliefern statischer Dateien. Daher wird sie häufig zusammen mit der [`file_server`-Direktive](file_server) oder der [`php_fastcgi`-Direktive](php_fastcgi) verwendet.


<a id="syntax"></a>
## Syntax

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** ist der Pfad, der als Site-Root verwendet wird.

Vor v2.8.0 konnte das Argument `<path>` vom Parser mit einem [Matcher-Token](/docs/caddyfile/matchers#syntax) verwechselt werden, wenn es mit `/` begann. Deshalb musste ein Wildcard-Matcher-Token (`*`) angegeben werden.


<a id="examples"></a>
## Beispiele

Das Site-Root auf `/home/bob/public_html` setzen (setzt voraus, dass Caddy als Benutzer `bob` läuft):

<aside class="tip">

Wenn Sie Caddy als systemd-Service ausführen, funktioniert das Lesen von Dateien aus `/home` nicht, weil der Benutzer `caddy` keine "execute"-Berechtigung für das Verzeichnis `/home` hat (erforderlich zum Durchlaufen). Es wird empfohlen, Ihre Dateien stattdessen in `/srv` oder `/var/www/html` abzulegen.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Beachten Sie, dass vor v2.8.0 hier ein [Wildcard Matcher](/docs/caddyfile/matchers#wildcard-matchers) erforderlich war, weil das erste Argument mit einem [Path Matcher](/docs/caddyfile/matchers#path-matchers) mehrdeutig ist, also `root * /srv`. Heute kann dies zu `root /srv` vereinfacht werden.

</aside>


Das Site-Root für alle Anfragen auf `public_html` setzen (relativ zum aktuellen Arbeitsverzeichnis):

```caddy-d
root public_html
```

Das Site-Root nur für Anfragen in `/foo/*` ändern:

```caddy-d
root /foo/* /home/user/public_html/foo
```

Die `root`-Direktive wird häufig mit [`file_server`](file_server) kombiniert, um statische Dateien auszuliefern, und/oder mit [`php_fastcgi`](php_fastcgi), um eine PHP-Site auszuliefern:

```caddy
example.com {
	root /srv
	file_server
}
```
