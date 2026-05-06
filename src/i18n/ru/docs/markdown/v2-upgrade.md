---
title: Переход на Caddy 2
---

Руководство по обновлению
=============

Caddy 2 — полностью новая code base, написанная с нуля, чтобы улучшить Caddy 1. Caddy 2 не backwards-compatible с Caddy 1. Но не переживайте: для большинства базовых setups отличий немного. Это guide поможет перейти как можно проще.

Здесь не рассматриваются новые features -- кстати, они действительно классные, их стоит [изучить](/docs/getting-started) -- цель только в том, чтобы быстро запустить вас на Caddy 2.

- [Главное](#high-order-bits)
- [Шаги](#steps)
- [HTTPS и ports](#https-and-ports)
- [Command line](#command-line)
- [Caddyfile](#caddyfile)
	- [Основные изменения](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [Service files](#service-files)
- [Plugins](#plugins)
- [Получение помощи](#getting-help)



<a id="high-order-bits"></a>
## Главное

- "Caddy 2" по-прежнему называется просто `caddy`. Мы можем использовать "Caddy 2", чтобы уточнить version и сделать transition менее confusing.
- Большинству users нужно просто заменить binary `caddy` и обновленную config `Caddyfile` (после тестирования).
- Возможно, лучше переходить на Caddy 2 без assumptions, перенесенных из Caddy 1.
- Возможно, вашу niche v1 configuration нельзя идеально повторить в v2. Обычно для этого есть веская причина.
- Command line больше не используется для server configuration.
- Environment variables больше не нужны для configuration.
- Основной способ передать Caddy 2 configuration — через его [API](/docs/api), но также можно использовать [command `caddy`](/docs/command-line).
- Нужно знать, что native configuration language Caddy 2 — [JSON](/docs/json/), а Caddyfile — лишь еще один [config adapter](/docs/config-adapters), который converts в JSON за вас. Extremely custom/advanced use cases могут требовать JSON, потому что не вся возможная configuration выражается через Caddyfile.
- Caddyfile в основном похож, но стал гораздо мощнее; directives изменились.



<a id="steps"></a>
## Шаги

1. Познакомьтесь с Caddy 2, пройдя tutorial [Getting Started](/docs/getting-started).
2. Выполните шаг 1, если еще не сделали. Серьезно -- мы не можем переоценить, насколько важно хотя бы знать, как пользоваться Caddy 2. (И это веселее!)
3. Используйте guide ниже, чтобы перенести command(s) `caddy`.
4. Используйте guide ниже, чтобы перенести Caddyfile.
5. Протестируйте новую config локально или в staging.
6. Тестируйте, тестируйте и еще раз тестируйте
7. Deploy и получайте удовольствие!



<a id="https-and-ports"></a>
## HTTPS и ports

Default port Caddy больше не `:2015`. Default port Caddy 2 — `:443` или, если hostname/IP неизвестен, port `:80`. Ports всегда можно customize в config.

Default protocol Caddy 2 — [*всегда* HTTPS, если hostname или IP известен](/docs/automatic-https#overview). Это отличается от Caddy 1, где только public-looking domains использовали HTTPS по умолчанию. Теперь *каждый* site использует HTTPS (если вы не отключили его, явно указав port `:80` или `http://`).

IP addresses и localhost domains получат certificates от [locally-trusted, embedded CA](/docs/automatic-https#local-https). Все остальные domains будут использовать ZeroSSL или Let's Encrypt. (Все это configurable.)

Storage structure certificates и ACME resources изменилась. Caddy 2, вероятно, получит новые certificates для ваших sites; но если у вас много certificates, их можно migrate вручную, если он не сделает этого сам. Подробности см. issues [#2955](https://github.com/caddyserver/caddy/issues/2955) и [#3124](https://github.com/caddyserver/caddy/issues/3124).



<a id="command-line"></a>
## Command line

Команда `caddy` теперь `caddy run`.

Все command line flags отличаются. Удалите их; вся server config теперь находится внутри actual config document (обычно Caddyfile или JSON). Вероятно, замену большинству command line flags из v1 вы найдете в [JSON structure](/docs/json/) или [Caddyfile global options](/docs/caddyfile/options).

Команда вроде `caddy -conf ../Caddyfile` станет `caddy run --config ../Caddyfile`.

Как и раньше, если Caddyfile находится в текущей folder, Caddy найдет и использует его автоматически; в этом случае flag `--config` не нужен.

Signals в основном те же, кроме USR1 и USR2, которые больше не поддерживаются. Вместо них используйте command [`caddy reload`](/docs/command-line#caddy-reload) или [API](/docs/api), чтобы загрузить новую configuration.

Запуск `caddy` без config раньше запускал простой file server. Эквивалент в Caddy 2 — [`caddy file-server`](/docs/command-line#caddy-file-server).

Environment variables больше не релевантны, кроме `HOME` (и опционально любых `XDG_*` variables, которые вы задаете). `CADDYPATH` [заменен OS conventions](/docs/conventions#file-locations).



## Caddyfile

[v2 Caddyfile](/docs/caddyfile/concepts) очень похож на то, с чем вы уже знакомы. Главное, что нужно сделать, — изменить directives.

⚠️ **Обязательно прочитайте новые directives!** Особенно если config advanced: есть много нюансов. Эти советы помогут быстро перейти, но прочитайте полную документацию каждой directive, чтобы понимать implications upgrade. И, конечно, тщательно тестируйте configs перед production.


<a id="primary-changes"></a>
### Основные изменения

- Если вы обслуживаете static files, нужно добавить [директиву `file_server`](/docs/caddyfile/directives/file_server), потому что Caddy 2 не предполагает этого по умолчанию. Caddy 2 также не sniff MIME по умолчанию по security reasons; если Content-Type отсутствует, может потребоваться задать header самостоятельно через directive [header](/docs/caddyfile/directives/header).

- В v1 вы могли filter (или "match") directives только по request path. В v2 [request matching](/docs/caddyfile/matchers) гораздо мощнее. Любые v2 directives, которые добавляют middleware в HTTP handler chain или каким-либо образом изменяют HTTP request/response, используют эту новую matching functionality. [Подробнее о v2 request matchers.](/docs/caddyfile/matchers) Их нужно понимать, чтобы разобраться в v2 Caddyfile.

- Хотя многие [placeholders](/docs/conventions#placeholders) те же, многие изменились, и появилось [много новых](/docs/modules/http#docs), включая [shorthands for Caddyfile](/docs/caddyfile/concepts#placeholders).

- Logs Caddy 2 все structured, и default format — JSON. Все log levels могут идти в один log для processing (но при необходимости это можно customize).

- Там, где в Caddy 1 requests matched по path prefix, path matching в Caddy 2 теперь exact by default. Если нужно match prefix вроде `/foo/`, в Caddy 2 нужен `/foo/*`.

Ниже перечислены некоторые самые распространенные v1 directives и описано, как convert их для v2 Caddyfile.

⚠️ **Если v1 directive отсутствует на этой странице, это не значит, что v2 не может это сделать!** Некоторые v1 directives не нужны, плохо translate или реализованы другими способами в v2. Для advanced customization может потребоваться перейти на JSON. Изучите [нашу документацию](/docs/caddyfile), чтобы найти нужное!


### basicauth

HTTP Basic Authentication по-прежнему настраивается directive [`basic_auth`](/docs/caddyfile/directives/basic_auth). Однако Caddy 2 configuration не принимает plaintext passwords. Их нужно hash; с этим поможет [`caddy hash-password`](/docs/command-line#caddy-hash-password).

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


### browse

File browsing теперь включается через directive [`file_server`](/docs/caddyfile/directives/file_server).

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


### errors

Custom error pages можно реализовать через [`handle_errors`](/docs/caddyfile/directives/handle_errors).


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

### ext

Implied file extensions можно сделать через [`try_files`](/docs/caddyfile/directives/try_files).

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


### fastcgi

Если вы обслуживаете PHP, v2 equivalent — [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

Обратите внимание, что directive `fastcgi` из v1 многое делала под капотом, включая trying files on disk, rewriting requests и даже redirecting. Directive v2 `php_fastcgi` тоже делает это за вас, но docs дают ее [expanded form](/docs/caddyfile/directives/php_fastcgi#expanded-form), которую можно modify, если требования отличаются.

В v2 не нужен preset `php`, потому что directive `php_fastcgi` предполагает PHP по умолчанию. Строка вроде `php_fastcgi 127.0.0.1:9000 php` заставит reverse proxy думать, что есть второй backend с именем `php`, что приведет к connection errors.

Subdirectives в v2 другие -- для PHP они вам, вероятно, не понадобятся.


### gzip

Единая directive [`encode`](/docs/caddyfile/directives/encode) теперь используется для всех response encodings, включая multiple compression formats.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

Интересный факт: Caddy 2 также поддерживает `zstd` (но browsers пока нет).


### header

[В основном без изменений](/docs/caddyfile/directives/header), но теперь гораздо мощнее, потому что в v2 может делать substring replacements.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


### log

Включает access logging; directive [`log`](/docs/caddyfile/directives/log) все еще можно использовать в v2, но все logs structured и по умолчанию encoded как JSON.

Рекомендуемый способ включить access logging:

```caddy-d
log
```

что emits structured logs в stderr. (Также можно emit в file или network socket; см. docs directive [`log`](/docs/caddyfile/directives/log).)

По умолчанию logs будут в [structured](/docs/logging) JSON format. Если по legacy reasons нужны logs в Common Log Format (CLF), можно использовать plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder).


### proxy

V2 equivalent — [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

Заметные изменения subdirectives: `header_upstream` и `header_downstream` стали `header_up` и `header_down` соответственно; subdirectives, связанные с load balancing, имеют prefix `lb_`.

Еще одно важное отличие: v2 proxy по умолчанию передает все incoming headers thru (включая header `Host`) и устанавливает header `X-Forwarded-For`. Иными словами, режим "transparent" из v1 в основном является default в v2 (но если нужны другие headers вроде X-Real-IP, их нужно задавать самостоятельно). Header `Host` по-прежнему можно override/customize через subdirective `header_up`.

Websocket proxying в v2 "просто работает"; не нужно "enable" websockets, как в v1.

Subdirective `without` удалена, потому что [rewrite hacks](#rewrite) больше не нужны в v2 благодаря improved matcher support.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


### redir

[Без изменений](/docs/caddyfile/directives/redir), кроме нескольких деталей об optional status code argument. Большинству configs ничего менять не нужно.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


### rewrite

Semantics request rewriting ("internal redirecting") немного изменилась. Если вы использовали так называемый "rewrite hack" в v1 как способ match requests по чему-то кроме простого path prefix, в v2 это совершенно не нужно.

[Новая directive `rewrite`](/docs/caddyfile/directives/rewrite) очень проста, но мощна, поскольку большая часть ее complexity в v2 handled by [matchers](/docs/caddyfile/matchers):

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Обратите внимание, что мы просто используем обычные [matcher tokens](/docs/caddyfile/matchers) Caddy 2; это больше не special case для этой directive.

Начните с удаления всех rewrite hacks; превратите их в [named matchers](/docs/caddyfile/concepts#named-matchers). Оцените каждый v1 `rewrite`, чтобы понять, нужен ли он в v2. Подсказка: v1 Caddyfile, который использует `rewrite` для добавления path prefix, а затем `proxy` с `without`, чтобы удалить тот же prefix, — это rewrite hack, и его можно eliminate.

Новые directives [`route`](/docs/caddyfile/directives/route) и [`handle`](/docs/caddyfile/directives/handle) могут быть полезны для большего контроля над advanced routing logic.


### root

[Без изменений](/docs/caddyfile/directives/root).

Не забудьте добавить [директиву `file_server`](/docs/caddyfile/directives/file_server), если обслуживаете static files, потому что Caddy 2 не предполагает этого по умолчанию, тогда как в v1 это всегда было enabled.


### status

V2 equivalent — [`respond`](/docs/caddyfile/directives/respond), которая также может write response body.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


### templates

Overall syntax directive [`templates`](/docs/caddyfile/directives/templates) не изменился, но actual template actions/functions другие и значительно улучшены. Например, templates способны include files, render markdown, делать internal sub-requests, parse front matter и многое другое!

[См. docs](/docs/modules/http.handlers.templates) для подробностей о новых functions.

- **v1:** `templates`
- **v2:** `templates`


### tls

Основы directive [`tls`](/docs/caddyfile/directives/tls) не изменились, например указание собственного cert и key:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

Но [auto-HTTPS logic](/docs/automatic-https) Caddy *изменилась*, так что учитывайте это!

Cipher suite names также изменились.

Распространенная configuration в Caddy 2 — использовать `tls internal`, чтобы он обслуживал locally-trusted certificate для dev hostname, который не является `localhost` или IP address.

Большинству sites эта directive вообще не нужна.


<a id="service-files"></a>
## Service files

Мы рекомендуем использовать [один из наших official systemd service files](/docs/running#linux-service) для Caddy deployments.

Если нужен custom service file, основывайте его на нашем. Они тщательно tuned именно так по веским причинам! При необходимости обязательно customize свой.


## Plugins

Plugins, написанные для v1, не совместимы с v2 автоматически. Многие v1 plugins в v2 вообще не нужны. С другой стороны, v2 гораздо проще и гибче расширять, чем v1!

Если хотите написать plugin для Caddy 2, [узнайте, как написать Caddy module](/docs/extending-caddy).


<a id="building-caddy-2-with-plugins"></a>
### Building Caddy 2 with plugins

Caddy 2 можно скачать с plugins на [interactive download page](/download). Также можно [собрать Caddy самостоятельно](/docs/build) с помощью `xcaddy` и выбрать, какие plugins включить. `xcaddy` automates instructions в файле Caddy [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go).


<a id="getting-help"></a>
## Получение помощи

Если не получается заставить Caddy работать, сначала посмотрите документацию на нашем сайте. Потратьте время на эксперименты и понимание происходящего - v2 во многом сильно отличается от v1 (но при этом очень знаком)!

Если все еще нужна помощь, станьте частью [нашего community](https://caddy.community)! Возможно, помогая другим, вы лучше всего поможете и себе.
