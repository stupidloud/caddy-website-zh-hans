---
title: request_header (директива Caddyfile)
---

# request_header

Управляет HTTP header fields в запросе. Может устанавливать, добавлять и удалять значения header, а также выполнять замены с помощью regular expressions.

Если вы собираетесь изменять headers для проксирования, используйте вместо этого [поддирективу `header_up`](/docs/caddyfile/directives/reverse_proxy#header_up) директивы `reverse_proxy`, поскольку эти изменения учитывают proxy context.

Для управления HTTP response headers можно использовать директиву [`header`](header).


<a id="syntax"></a>
## Синтаксис

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** — имя поля header.

  Без prefix поле устанавливается (перезаписывается).

  Prefix `+` добавляет поле вместо перезаписи (установки), если поле уже существует; header fields могут появляться в запросе более одного раза.

  Prefix `-` удаляет поле. Поле может использовать wildcards `*` в prefix или suffix, чтобы удалить все совпадающие поля.

- **&lt;value&gt;** — значение поля header, если поле добавляется или устанавливается.

- **&lt;find&gt;** — substring или regular expression для поиска.

- **&lt;replace&gt;** — replacement value; обязателен при выполнении search-and-replace.


<a id="examples"></a>
## Примеры

Удалить header Referer из запроса:

```caddy-d
request_header -Referer
```

Удалить из запроса все headers, содержащие underscore:

```caddy-d
request_header -*_*
```
