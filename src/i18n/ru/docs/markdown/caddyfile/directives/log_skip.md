---
title: log_skip (директива Caddyfile)
---

# log_skip

Пропускает access logging для совпавших requests.

Ее следует использовать вместе с [директивой `log`](log), чтобы пропускать logging requests, которые не важны для ваших задач.

До v2.8.0 эта директива называлась `skip_log`, но была переименована для согласованности с другими директивами.


<a id="syntax"></a>
## Синтаксис

```caddy-d
log_skip [<matcher>]
```


<a id="examples"></a>
## Примеры

Пропустить access logging для статических файлов, хранящихся в subpath:

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


Пропустить access logging для requests, совпадающих с pattern; в этом случае — для файлов с определенными расширениями:

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


Matcher не нужен, если он уже находится внутри route, который сам находится внутри matcher. Например, с handle для file server определенного subpath:

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
