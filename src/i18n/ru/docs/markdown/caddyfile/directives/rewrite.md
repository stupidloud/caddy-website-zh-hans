---
title: rewrite (директива Caddyfile)
---

# rewrite

Внутренне переписывает request URI.

Rewrite изменяет часть или весь request URI. Обратите внимание, что URI не включает scheme или authority (host и port), а clients обычно не отправляют fragments. Поэтому эта директива в основном используется для изменения **path** и **query** string.

Директива `rewrite` подразумевает намерение принять запрос, но с изменениями.

Она взаимно исключает другие директивы `rewrite` в том же блоке, поэтому безопасно определять rewrites, которые иначе каскадно переходили бы друг в друга: будет выполнен только первый совпавший rewrite.

[Request matcher](/docs/caddyfile/matchers), который совпадает с запросом до `rewrite`, может не совпадать с тем же запросом после `rewrite`. Если нужно, чтобы `rewrite` разделял route с другими handlers, используйте директивы [`route`](route) или [`handle`](handle).


<a id="syntax"></a>
## Синтаксис

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** — URI, на который нужно переписать запрос. Обрабатываются только те компоненты URI (path или query string), которые указаны в rewrite. URI path — это любая подстрока перед `?`. Если `?` опущен, весь token считается path.

До v2.8.0 аргумент `<to>` мог быть ошибочно принят parser за [matcher token](/docs/caddyfile/matchers#syntax), если начинался с `/`, поэтому было необходимо указывать wildcard matcher token (`*`).


<a id="similar-directives"></a>
## Похожие директивы

Есть и другие директивы, которые выполняют rewrites, но подразумевают другое намерение или выполняют rewrite без полной замены URI:

- [`uri`](uri) изменяет URI (strip prefix, suffix или substring replacement).

- [`try_files`](try_files) переписывает запрос на основе существования файлов.



<a id="examples"></a>
## Примеры

Переписать все requests на `index.html`, оставив query string без изменений:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Обратите внимание, что до v2.8.0 здесь требовался [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers), потому что первый аргумент был неоднозначен с [path matcher](/docs/caddyfile/matchers#path-matchers), т. е. `rewrite * /foo`, но теперь это можно упростить до `rewrite /foo`.

</aside>

Добавить prefix `/api` ко всем requests, сохранив остальную часть URI, затем reverse proxy к app:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Заменить query string в API requests на `a=b`, оставив path без изменений:

```caddy
example.com {
	rewrite ?a=b
}
```

Только для requests к `/api/` сохранить существующий query string и добавить key-value pair:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Изменить и path, и query string, сохранив исходный query string и добавив исходный path как параметр `p`:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
