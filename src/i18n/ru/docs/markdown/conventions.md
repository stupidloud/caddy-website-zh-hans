---
title: Соглашения
---

<a id="conventions"></a>
# Соглашения

Экосистема Caddy придерживается нескольких соглашений, чтобы поведение платформы было согласованным и интуитивным.


- [Сетевые адреса](#network-addresses)
- [Placeholders](#placeholders)
- [Расположения файлов](#file-locations)
  - [Data directory](#data-directory)
  - [Configuration directory](#configuration-directory)
- [Durations](#durations)



<a id="network-addresses"></a>
## Сетевые адреса

При указании network address для dial или bind Caddy принимает string в таком формате:

```
network/address
```

Часть network необязательна (по умолчанию `tcp`) и может быть любой, которую распознает [функция Go `net.Dial`](https://pkg.go.dev/net#Dial). Если network указана, один forward slash `/` должен разделять части network и address.

Network может быть любой из следующих; варианты с suffix `4` или `6` означают только IPv4 или IPv6 соответственно:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

Часть address может быть в одной из этих форм:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

Host может быть любым hostname, resolvable domain name или IP address.

В случае IPv6 addresses адрес должен быть заключен в square brackets `[]`. Zone identifier (начинающийся с `%`) необязателен (часто используется для link-local addresses).

Port может быть одиночным значением (`:8080`) или inclusive range (`:8080-8085`). Port range будет развернут в отдельные addresses. Не все config fields принимают port ranges. Специальный port `:0` означает любой доступный port.

Unix socket path допустим только при использовании network type `unix*`. Forward slash, разделяющий network и address, не считается частью path.

Когда unix socket используется как bind address, можно опционально указать file permission mode после path, отделив его pipe `|`. По умолчанию `0200` (octal), т. е. `u=w,g=,o=` (symbolic). Ведущий `0` необязателен.

Допустимые примеры:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Сетевые адреса Caddy — не URLs. URLs связывают нижние и верхние уровни [модели OSI <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture), но Caddy часто использует network addresses независимо от конкретного application, поэтому их объединение было бы проблемным. В Caddy network addresses точно указывают resources, к которым можно dial или bind на L3-L5, а URLs объединяют L3-L7, что слишком много. Network address требует, чтобы host+port и path были взаимоисключающими, а URLs — нет. Network addresses иногда поддерживают port ranges, а URLs — нет.

</aside>




<a id="placeholders"></a>
## Placeholders

Конфигурация Caddy поддерживает использование *placeholders*. Placeholders — простой способ вставлять dynamic values в static configuration.

<aside class="tip">

Placeholders похожи на variables в другом ПО. Например, [у nginx есть variables <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) вроде `$uri` и `$document_root`, а эквиваленты Caddy — [`{http.request.uri}`](/docs/json/apps/http/#docs) и [`{http.vars.root}`](/docs/caddyfile/directives/root).

</aside>


Placeholders ограничены curly braces `{ }` с обеих сторон и содержат identifier внутри, например: `{foo.bar}`. Открывающую brace placeholder можно экранировать `\{like.this}`, чтобы предотвратить replacement. Placeholder identifiers обычно namespaced с dots, чтобы избежать collisions между modules.

Доступность placeholders зависит от context. Не все placeholders доступны во всех частях config. Например, [HTTP app устанавливает placeholders](/docs/json/apps/http/#docs), доступные только в областях config, связанных с обработкой HTTP requests. Когда request проходит через [`reverse_proxy` handler](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs), handler устанавливает несколько proxy-specific placeholders. На эти placeholders можно ссылаться во время proxying, а также после него (в `handle_response`), например при установке response headers или обогащении access logs.

Следующие placeholders доступны всегда (global):

Placeholder | Описание
------------|-------------
`{env.*}` | Environment variable; пример: `{env.HOME}`
`{file.*}` | Содержимое из файла; пример: `{file./path/to/secret.txt}`
`{system.hostname}` | Локальный hostname системы
`{system.slash}` | Filepath separator системы
`{system.os}` | OS системы
`{system.arch}` | Architecture системы
`{system.wd}` | Текущий рабочий каталог
`{time.now}` | Текущее время как Go Time struct
`{time.now.http}` | Текущее время в формате, используемом в [HTTP headers <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)
`{time.now.unix}` | Текущее время как unix timestamp в секундах
`{time.now.unix_ms}` | Текущее время как unix timestamp в миллисекундах
`{time.now.common_log}` | Текущее время в Common Log Format
`{time.now.year}` | Текущий год в формате YYYY

Не все config fields поддерживают placeholders, но большинство ожидаемых мест поддерживает. Поддержка placeholders должна быть явно добавлена в эти fields. Authors plugins могут [прочитать эту статью](/docs/extending-caddy/placeholders), чтобы узнать, как добавить поддержку placeholders в свои modules.




<a id="file-locations"></a>
## Расположения файлов

Этот раздел содержит информацию о том, где искать разные files. Описанные здесь file и directory paths в лучшем случае являются defaults; некоторые можно переопределить.

<a id="your-config-files"></a>
### Ваши config files

Нет единого общепринятого места, куда нужно помещать config files. Размещайте их там, где это имеет наибольший смысл для вас.

<aside class="tip">

Единственным исключением может быть файл с именем `Caddyfile` в текущем рабочем каталоге: команда caddy для удобства пытается использовать его, если другой config file не указан.

</aside>


Distributions, которые поставляются с config file по умолчанию, должны документировать, где находится этот config file, даже если это может быть очевидно для package/distro maintainers. Для большинства Linux installations Caddyfile будет находиться в `/etc/caddy/Caddyfile`.


<a id="data-directory"></a>
### Data directory

Caddy хранит TLS certificates и другие важные assets в data directory, которая поддерживается [настроенным storage module](/docs/json/storage/) (по умолчанию: local file system).

Если environment variable `XDG_DATA_HOME` установлена, это `$XDG_DATA_HOME/caddy`.

Иначе path зависит от platform и следует OS conventions:

OS | Data directory path
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (или `/sdcard/caddy`)

Все остальные OSes используют directory path Linux/BSD.

**Data directory нельзя считать cache.** Ее содержимое **не** ephemeral и не существует только ради performance. Caddy хранит TLS certificates, private keys, OCSP staples и другую необходимую информацию в data directory. Ее не следует очищать без понимания последствий.

Критически важно, чтобы этот directory был persistent и writeable для Caddy.


<a id="configuration-directory"></a>
### Configuration directory

Здесь Caddy может сохранять некоторую configuration на disk. В частности, он сохраняет последнюю active configuration (по умолчанию) в эту папку, чтобы позже легко возобновить работу с помощью [`caddy run --resume`](/docs/command-line#caddy-run).

<aside class="tip">

Configuration directory — это *не* место, где нужно хранить [ваши config files](#your-config-files). (Хотя это разрешено.)

</aside>


Если environment variable `XDG_CONFIG_HOME` установлена, это `$XDG_CONFIG_HOME/caddy`.

Иначе path зависит от platform и следует OS conventions:


OS | Config directory path
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Все остальные OSes используют directory path Linux/BSD.

Критически важно, чтобы этот directory был persistent и writeable для Caddy.


<a id="durations"></a>
## Durations

Duration strings часто используются во всей конфигурации Caddy. Они имеют тот же format, что и [синтаксис Go `time.ParseDuration`](https://golang.org/pkg/time/#ParseDuration), но также можно использовать `d` для day (для простоты считаем 1 day = 24 hours). Допустимые units:

- `ns` (nanosecond)
- `us`/`µs` (microsecond)
- `ms` (millisecond)
- `s` (second)
- `m` (minute)
- `h` (hour)
- `d` (day)

Примеры:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

В [JSON config](/docs/json/) duration values также могут быть integers, представляющими nanoseconds.
