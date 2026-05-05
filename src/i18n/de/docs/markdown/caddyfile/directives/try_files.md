---
title: try_files (Caddyfile directive)
---

# try_files

Schreibt den URI-Pfad der Anfrage auf die erste der aufgelisteten Dateien um, die im Site-Root existiert. Wenn keine Datei passt, wird kein Rewrite durchgeführt.


<a id="syntax"></a>
## Syntax

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** ist die Liste der zu probierenden Dateien. Der URI-Pfad wird auf die erste existierende Datei umgeschrieben.

  Um Verzeichnisse abzugleichen, hängen Sie einen abschließenden Slash `/` an den Pfad an. Alle Dateipfade sind relativ zum Site-[Root](root), und [Glob-Muster](https://pkg.go.dev/path/filepath#Match) werden expandiert.

  Jedes Argument kann auch einen Query String enthalten; in diesem Fall wird auch der Query String geändert, wenn diese bestimmte Datei passt.

  Wenn `try_policy` `first_exist` ist (der Standard), darf das letzte Element in der Liste eine mit `=` präfixierte Zahl sein (z. B. `=404`). Als Fallback wird dann ein Fehler mit diesem Code ausgegeben; der Fehler kann mit [`handle_errors`](handle_errors) abgefangen und behandelt werden.

- **policy** ist die Richtlinie zur Auswahl einer Datei aus der Liste.

  Standard: `first_exist`



<a id="expanded-form"></a>
## Erweiterte Form

Die Direktive `try_files` ist im Grunde eine Abkürzung für:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

Beachten Sie, dass diese Direktive kein Matcher-Token akzeptiert. Wenn Sie komplexere Matching-Logik benötigen, verwenden Sie die oben gezeigte erweiterte Form als Grundlage.

Weitere Details finden Sie beim [`file`-Matcher](/docs/caddyfile/matchers#file).



<a id="examples"></a>
## Beispiele

Wenn die Anfrage auf keine statische Datei passt, nach Ihrem PHP-Index-/Router-Entrypoint umschreiben:

```caddy-d
try_files {path} /index.php
```

Dasselbe, aber mit Hinzufügen des ursprünglichen Pfads zum Query String (von manchen alten PHP-Apps benötigt):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

Dasselbe, aber zusätzlich Verzeichnisse abgleichen:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Versuchen, auf eine Datei oder ein Verzeichnis umzuschreiben, wenn es existiert, andernfalls einen 404-Fehler ausgeben (der mit [`handle_errors`](handle_errors) abgefangen und behandelt werden kann):

```caddy-d
try_files {path} {path}/ =404
```

Die zuletzt bereitgestellte Version einer statischen Datei auswählen (z. B. `index.be331df.html` ausliefern, wenn `index.html` angefordert wird):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
