---
title: root (директива Caddyfile)
---

# root

Задает root path сайта, используемый различными matchers и directives, которые обращаются к файловой системе. Если не задан, site root по умолчанию — текущий рабочий каталог.

Конкретно эта директива устанавливает placeholder `{http.vars.root}`. Она взаимно исключает другие директивы `root` в том же блоке, поэтому безопасно определять несколько roots с пересекающимися matchers: они не будут каскадно перезаписывать друг друга.

Эта директива не включает отдачу статических файлов автоматически, поэтому часто используется вместе с [директивой `file_server`](file_server) или [директивой `php_fastcgi`](php_fastcgi).


<a id="syntax"></a>
## Синтаксис

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** — путь, используемый как site root.

До v2.8.0 аргумент `<path>` мог быть ошибочно принят parser за [matcher token](/docs/caddyfile/matchers#syntax), если начинался с `/`, поэтому было необходимо указывать wildcard matcher token (`*`).


<a id="examples"></a>
## Примеры

Установить site root в `/home/bob/public_html` (предполагается, что Caddy запущен от пользователя `bob`):

<aside class="tip">

Если вы запускаете Caddy как systemd service, чтение файлов из `/home` не будет работать, потому что пользователь `caddy` не имеет "executable" permission на каталог `/home` (необходимо для traversal). Рекомендуется вместо этого размещать файлы в `/srv` или `/var/www/html`.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Обратите внимание, что до v2.8.0 здесь требовался [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers), потому что первый аргумент был неоднозначен с [path matcher](/docs/caddyfile/matchers#path-matchers), т. е. `root * /srv`, но теперь это можно упростить до `root /srv`.

</aside>


Установить site root в `public_html` (относительно текущего рабочего каталога) для всех requests:

```caddy-d
root public_html
```

Изменить site root только для requests в `/foo/*`:

```caddy-d
root /foo/* /home/user/public_html/foo
```

Директива `root` обычно используется вместе с [`file_server`](file_server) для отдачи статических файлов и/или с [`php_fastcgi`](php_fastcgi) для обслуживания PHP site:

```caddy
example.com {
	root /srv
	file_server
}
```
