---
title: log_skip (Caddyfile directive)
---

# log_skip

Überspringt Access Logging für gematchte Requests.

Dies sollte zusammen mit der Direktive [`log`](log) verwendet werden, um das Logging von Requests zu überspringen, die für Ihre Zwecke nicht relevant sind.

Vor v2.8.0 hieß diese Direktive `skip_log`, wurde aber zur Konsistenz mit anderen Direktiven umbenannt.


<a id="syntax"></a>
## Syntax

```caddy-d
log_skip [<matcher>]
```


<a id="examples"></a>
## Beispiele

Access Logging für statische Dateien überspringen, die in einem Unterpfad gespeichert sind:

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


Access Logging für Requests überspringen, die auf ein Muster passen; in diesem Fall für Dateien mit bestimmten Erweiterungen:

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


Der Matcher ist nicht nötig, wenn er innerhalb einer Route gefunden wird, die bereits in einem Matcher liegt. Zum Beispiel mit einem Handle für einen Dateiserver für einen bestimmten Unterpfad:

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
