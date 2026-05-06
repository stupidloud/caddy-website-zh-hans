---
title: "Командная строка"
---

<a id="command-line"></a>
# Командная строка

Caddy имеет стандартный unix-подобный интерфейс командной строки. Базовое использование:

```
caddy <command> [<args...>]
```

`<carets>` обозначают параметры, которые заменяются вашим вводом.

`[brackets]` обозначают необязательные параметры. `(brackets)` обозначают обязательные параметры.

Многоточие `...` обозначает продолжение, то есть один или несколько параметров.

`--flags` могут иметь однобуквенное сокращение, например `-f`.

**Быстрый старт: `caddy`, `caddy help` или `man caddy` (если установлен)**

---

- **[caddy adapt](#caddy-adapt)**
  Адаптирует конфигурационный документ в собственный JSON

- **[caddy build-info](#caddy-build-info)**
  Выводит информацию о сборке

- **[caddy completion](#caddy-completion)**
  Генерирует скрипт автодополнения shell

- **[caddy environ](#caddy-environ)**
  Выводит окружение

- **[caddy file-server](#caddy-file-server)**
  Простой, но production-ready файловый сервер

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Вспомогательная команда файлового сервера для экспорта шаблона файлового браузера по умолчанию

- **[caddy fmt](#caddy-fmt)**
  Форматирует Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Хеширует пароль и выводит base64

- **[caddy help](#caddy-help)**
  Показывает справку по командам caddy

- **[caddy list-modules](#caddy-list-modules)**
  Перечисляет установленные модули Caddy

- **[caddy manpage](#caddy-manpage)**
  Генерирует manpages

- **[caddy reload](#caddy-reload)**
  Изменяет конфигурацию запущенного процесса Caddy

- **[caddy respond](#caddy-respond)**
  Быстрый и аккуратный жестко заданный HTTP-сервер для разработки и тестирования

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Простой, но production-ready HTTP(S) reverse proxy

- **[caddy run](#caddy-run)**
  Запускает процесс Caddy на переднем плане

- **[caddy start](#caddy-start)**
  Запускает процесс Caddy в фоне

- **[caddy stop](#caddy-stop)**
  Останавливает запущенный процесс Caddy

- **[caddy storage export](#caddy-storage)**
  Экспортирует содержимое настроенного storage в tarball

- **[caddy storage import](#caddy-storage)**
  Импортирует ранее экспортированный tarball в настроенный storage

- **[caddy trust](#caddy-trust)**
  Устанавливает сертификат в локальные хранилища доверия

- **[caddy untrust](#caddy-untrust)**
  Удаляет доверие к сертификату из локальных хранилищ доверия

- **[caddy upgrade](#caddy-upgrade)**
  Обновляет Caddy до последнего релиза

- **[caddy add-package](#caddy-add-package)**
  Обновляет Caddy до последнего релиза с добавлением дополнительных plugins

- **[caddy remove-package](#caddy-remove-package)**
  Обновляет Caddy до последнего релиза с удалением некоторых plugins

- **[caddy validate](#caddy-validate)**
  Проверяет, является ли конфигурационный файл корректным

- **[caddy version](#caddy-version)**
  Выводит версию

- **[Signals](#signals)**
  Как Caddy обрабатывает signals

- **[Exit codes](#exit-codes)**
  Коды, выдаваемые при завершении процесса Caddy

<a id="subcommands"></a>
## Подкоманды


<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Адаптирует конфигурацию в собственную JSON-структуру Caddy, записывает результат в stdout, предупреждения в stderr, затем завершается.

`--config` — путь к конфигурационному файлу. Если он не указан, предполагается `Caddyfile` в текущем каталоге, если он существует; иначе этот флаг обязателен. Если вы хотите использовать stdin вместо обычного файла, используйте - как путь.

`--adapter` указывает используемый адаптер конфигурации; по умолчанию это `caddyfile`.

`--pretty` форматирует вывод с отступами для удобства чтения человеком.

`--validate` загрузит и provision адаптированную конфигурацию, чтобы проверить ее корректность (но фактически не запустит config).

Обратите внимание, что успешно адаптированная конфигурация все еще может не пройти валидацию. Например, используйте такой Caddyfile:

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

Попробуйте адаптировать его:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

Это завершается успешно без ошибки. Затем попробуйте:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

Хотя этот Caddyfile можно адаптировать в JSON без ошибок, фактические файлы сертификата и/или ключа не существуют, поэтому валидация завершается ошибкой, потому что ошибка возникает на этапе provisioning. Поэтому валидация является более строгой проверкой ошибок, чем адаптация.

<a id="example"></a>
#### Пример

Чтобы адаптировать Caddyfile в JSON, который легко читать и вручную изменять:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

Выводит информацию, предоставленную Go о сборке (путь основного модуля, версии пакетов, замены модулей).




<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Генерирует скрипты автодополнения shell. Это позволяет получить tab-complete или auto-complete (или похожее поведение, в зависимости от shell) при вводе команд `caddy`.

Чтобы получить инструкции по установке этого скрипта в ваш конкретный shell, выполните `caddy help completion` или `caddy completion -h`.



<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

Выводит окружение, как его видит caddy, затем завершается. Это может быть полезно при отладке init systems или process manager units вроде systemd.




<a id="caddy-file-server"></a>
### `caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Запускает простой, но production-ready сервер статических файлов.

`--root` указывает корневой путь файлов. По умолчанию используется текущий рабочий каталог.

`--listen` принимает адрес listener. По умолчанию это `:80`, если не используется `--domain`; тогда по умолчанию будет `:443`.

`--domain` будет обслуживать файлы только через этот hostname, и Caddy попытается обслуживать его по HTTPS, поэтому сначала убедитесь, что публичный DNS настроен правильно, если это публичное доменное имя. Порт по умолчанию будет изменен на 443.

`--browse` включает listing каталогов, если запрошен каталог без index-файла.

`--reveal-symlinks` показывает цель символических ссылок в listing каталогов, когда включен `--browse`.

`--templates` включает rendering templates.

`--access-log` включает журнал запросов/доступа.

`--debug` включает подробное логирование.

`--file-limit` задает максимальное количество файлов для показа в listing каталогов. По умолчанию: `10000`. Если число файлов превышает этот лимит, будут показаны только первые N файлов, где N — указанный лимит.

`--no-compress` отключает сжатие. По умолчанию включено сжатие Zstandard и Gzip.

`--precompressed` указывает форматы кодирования, по которым искать precompressed sidecar files. Можно повторять для нескольких форматов. Подробнее смотрите в [директиве file_server](/docs/caddyfile/directives/file_server#precompressed).

Эта команда отключает admin API, чтобы было проще запускать несколько экземпляров на локальной машине разработки.


<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Экспортирует шаблон файлового браузера по умолчанию в stdout

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Форматирует или prettify Caddyfile, затем завершается. Результат выводится в stdout, если не используется `--overwrite`; команда завершится с кодом `1`, если есть какие-либо отличия.

`<path>` указывает путь к Caddyfile. Если это `-`, ввод читается из stdin. Если путь не указан, вместо него предполагается файл с именем Caddyfile в текущем каталоге.

`--overwrite` записывает результат во входной файл вместо вывода в терминал. Если вход не является обычным файлом, этот флаг не имеет эффекта.

`--diff` сравнивает вывод с входом, и строки получают префиксы `-` и `+` там, где они отличаются. Обратите внимание, что неизмененные строки получают префикс из двух пробелов для выравнивания, и это не является допустимым форматом patch; это только визуальный инструмент.


<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

Удобный способ хешировать plaintext password. Полученный hash записывается в stdout в формате, который можно напрямую использовать в конфигурации Caddy.

`--plaintext`
    Пароль для хеширования. Если не указан, он будет прочитан из stdin.
    Если Caddy подключен к управляющему TTY, ввод не будет отображаться.

`--algorithm`
    Выбирает алгоритм хеширования. Допустимые варианты:
      * `argon2id` (рекомендуется для современной безопасности)
      * `bcrypt`  (legacy, медленнее, настраиваемая cost, default cost — `14`)

Параметры, специфичные для bcrypt:

`--bcrypt-cost`
    Задает сложность хеширования bcrypt. Более высокие значения повышают безопасность,
    делая вычисление hash медленнее и более CPU-intensive.
    Должно быть в допустимом диапазоне [bcrypt.MinCost, bcrypt.MaxCost].
    Если не указано или некорректно, используется default cost.

Параметры, специфичные для Argon2id:

`--argon2id-time`
    Количество выполняемых итераций. Увеличение этого значения делает
    хеширование медленнее и более устойчивым к brute-force attacks.

`--argon2id-memory`
    Объем памяти, используемый во время хеширования.
    Большие значения повышают устойчивость к GPU/ASIC attacks.

`--argon2id-threads`
    Количество используемых CPU threads. Увеличивайте для более быстрого хеширования
    на многоядерных системах.

`--argon2id-keylen`
    Длина итогового hash в байтах. Более длинные keys повышают
    безопасность, но немного увеличивают размер хранения.


<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

Выводит текст справки CLI, при необходимости для конкретной подкоманды, затем завершается.



<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

Выводит установленные модули Caddy, при необходимости с информацией о пакетах и/или версиях из связанных Go modules, затем завершается.

В некоторых scripted situations может быть избыточно выводить все стандартные модули, поэтому можно использовать `--skip-standard`, чтобы исключить их из вывода.

`--json` выводит информацию о модулях в формате JSON, что полезно для программной обработки.

NOTE: Из-за [ошибки в Go](https://github.com/golang/go/issues/29228) информация о версиях доступна только если Caddy собран как dependency, а не как основной module. Используйте [xcaddy](/docs/build#xcaddy), чтобы упростить это.



<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Генерирует страницы руководства/документации для команд Caddy и записывает их в каталог по указанному пути. Вывод этой команды можно читать командой `man`.

`--directory` (обязательный) — путь к каталогу, в который нужно записать man pages. Он будет создан, если не существует.

После генерации manual pages обычно нужно установить. Процедура зависит от платформы, но на типичных Linux-системах она выглядит примерно так:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Затем можно выполнить `man caddy` (или `man caddy-*` для подкоманд), чтобы читать документацию в терминале.

Manual pages — это отдельная документация, отличная от той, что размещена на нашем сайте. На сайте документация более полная и часто обновляется.




<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Передает запущенному экземпляру Caddy новую конфигурацию. Это имеет тот же эффект, что POST документа в [/load endpoint](/docs/api#post-load), но эта команда удобна для простых рабочих процессов вокруг конфигурационных файлов. По сравнению с командами `stop`, `start` и `run`, эта единственная команда является корректным, семантическим способом изменить/перезагрузить запущенную конфигурацию.

Поскольку эта команда использует API, admin endpoint не должен быть отключен.

`--config` — конфигурационный файл, который нужно применить. Если это `-`, config читается из stdin. Если не указан, команда попробует файл с именем `Caddyfile` в текущем рабочем каталоге и, если он существует, адаптирует его с помощью адаптера конфигурации `caddyfile`; иначе отсутствие конфигурационного файла для загрузки является ошибкой.

`--adapter` указывает используемый адаптер конфигурации, если он нужен. Этот флаг не нужен, если имя файла `--config` начинается с `Caddyfile` или заканчивается на `.caddyfile`, что предполагает адаптер `caddyfile`. Иначе этот флаг обязателен, если предоставленный конфигурационный файл не в собственном JSON-формате Caddy.

`--address` нужно использовать, если admin endpoint не слушает на адресе по умолчанию и если он отличается от адреса в предоставленном конфигурационном файле.

`--force` заставляет reload выполниться даже если указанная config такая же, как уже запущенная в Caddy. Это полезно, чтобы принудительно reprovision modules Caddy, что может иметь side-effects, например повторную загрузку вручную загруженных TLS certificates.




<a id="caddy-respond"></a>
### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


Запускает один или несколько простых, жестко заданных HTTP-серверов, полезных для разработки, staging и некоторых production-сценариев. Это может пригодиться для проверки или отладки HTTP clients, scripts или даже load balancers.

`--status` — возвращаемый HTTP status code.

`--header` добавляет HTTP header; ожидается формат `Field: value`. Этот флаг можно использовать несколько раз.

`--body` указывает response body. Альтернативно body можно передать pipe из stdin.

`--listen` — адрес listener, которым может быть любой [network address](/docs/conventions#network-addresses), распознаваемый Caddy; он также может включать диапазон портов для запуска нескольких servers.

`--debug` включает подробное debug logging.

`--access-log` включает access/request logging.

Если не указано никаких options, эта команда слушает случайный доступный порт и отвечает на HTTP-запросы пустым ответом 200. Адрес listen можно настроить флагом `--listen`, и он всегда будет выведен в stdout. Если адрес listen включает диапазон портов, будет запущено несколько servers.

Если задан финальный безымянный аргумент, он будет считаться status code (как флаг `--status`), если это трехзначное число. Иначе он используется как response body (как флаг `--body`). Флаги `--status` и `--body` всегда переопределяют этот аргумент.

Body можно задать тремя способами: флагом, финальным (и безымянным) аргументом команды или pipe в stdin (если флаг и аргумент не заданы). Для body поддерживается ограниченная [template evaluation](https://pkg.go.dev/text/template) со следующими переменными:

Variable | Description
---------|-------------
`.N`       | Номер сервера
`.Port`    | Порт listener
`.Address` | Адрес listener


<a id="examples"></a>
#### Примеры

Пустой ответ 200 на случайном порту:
<pre><code class="cmd bash">caddy respond</code></pre>

HTTP response с body:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Несколько servers и templates:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

Передача maintenance page через pipe:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




<a id="caddy-reverse-proxy"></a>
### `caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Простой, но production-ready reverse proxy. Полезен для быстрых развертываний, demos и разработки.

Просто передает HTTP(S) traffic с адреса `--from` на адрес `--to`. Можно указать несколько адресов `--to`, повторяя флаг. Требуется как минимум один адрес `--to`. Адрес `--to` может содержать диапазон портов как сокращение для развертывания в несколько upstreams.

Если в адресах не указано иное, адрес `--from` будет считаться HTTPS, если задан hostname, а адрес `--to` будет считаться HTTP.

Если адрес `--from` содержит host или IP, Caddy попытается обслуживать proxy по HTTPS с сертификатом (если это не переопределено схемой HTTP или портом).

Если обслуживается HTTPS: 
  - `--disable-redirects` можно использовать, чтобы не привязываться к HTTP-порту.

  - `--internal-certs` можно использовать, чтобы принудительно выдавать certificates с помощью внутреннего CA вместо попытки выдать публичный certificate.

Для proxying:
  - `--header-up` можно использовать, чтобы задать request header, отправляемый upstream.
  
  - `--header-down` можно использовать, чтобы задать response header, отправляемый обратно client.
  
  - `--change-host-header` задает header Host в request равным адресу upstream вместо значения по умолчанию из входящего Host header.

    Это сокращение для `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`
  
  - `--insecure` отключает TLS verification с upstream. WARNING: THIS DISABLES SECURITY BY NOT VERIFYING THE UPSTREAM'S CERTIFICATE.
  
  - `--debug` включает подробное logging.

Эта команда отключает admin API, чтобы было проще запускать несколько экземпляров на локальной машине разработки.



<a id="caddy-run"></a>
### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Запускает Caddy и блокируется на неопределенное время; то есть режим "daemon".

`--config` указывает начальный конфигурационный файл, который нужно сразу загрузить и использовать. Если это `-`, config читается из stdin. Если config не указан, Caddy запустится с пустой конфигурацией и настройками по умолчанию для [admin API endpoints](/docs/api), через которые можно передать ему новую конфигурацию. Особый случай: если в текущем рабочем каталоге есть файл с именем "Caddyfile" и подключен адаптер конфигурации `caddyfile` (по умолчанию), этот файл будет загружен и использован для настройки Caddy даже без каких-либо флагов командной строки.

`--adapter` — имя адаптера конфигурации, который нужно использовать при загрузке начальной config, если он нужен. Этот флаг не нужен, если имя файла `--config` начинается с `Caddyfile` или заканчивается на `.caddyfile`, что предполагает адаптер `caddyfile`. Иначе этот флаг обязателен, если предоставленный конфигурационный файл не в собственном JSON-формате Caddy. Все warnings будут выведены в log, но имейте в виду, что любая adaptation без errors сразу будет использована, даже если есть warnings. Если вы хотите сначала просмотреть результат adaptation, используйте подкоманду [`caddy adapt`](#caddy-adapt).

`--pidfile` записывает PID в указанный файл.

`--environ` выводит окружение перед запуском. Это то же самое, что команда `caddy environ`, но без завершения после вывода.

`--envfile` загружает переменные окружения из указанного файла в формате `KEY=VALUE`. Поддерживаются комментарии, начинающиеся с `#`; ключи могут иметь префикс `export`; значения могут быть заключены в двойные кавычки (двойные кавычки внутри можно экранировать); поддерживаются многострочные значения.

`--resume` использует последнюю загруженную конфигурацию, которая была autosaved, переопределяя флаг `--config` (если он есть). Использование этого флага гарантирует долговечность config при перезагрузках машины или перезапусках процесса. Он наиболее полезен в [API](/docs/api)-centric deployments.

`--watch` следит за конфигурационным файлом и автоматически перезагружает его после изменений. ⚠️ Эта функция предназначена только для локальных сред разработки!

<aside class="advice">

Не останавливайте сервер для изменения конфигурации в production! Это приведет к простою. (Это должно быть очевидно, но вы удивитесь, сколько жалоб мы получаем на это.) Вместо этого используйте команду [`caddy reload`](#caddy-reload) или отправьте процессу сигнал `SIGUSR1`, который имеет тот же эффект, что `caddy reload` с текущей загруженной config.

</aside>



<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></code></pre>

То же, что [`caddy run`](#caddy-run), но в фоне. Эта команда блокируется только до тех пор, пока фоновый процесс успешно не запустится (или не завершится ошибкой), затем возвращается.

Note: флаг `--config` *не* поддерживает `-` для чтения config из stdin.

Использовать эту команду с system services или в Windows не рекомендуется. В Windows дочерний процесс останется привязанным к терминалу, поэтому закрытие окна принудительно остановит Caddy, что неочевидно. Рассмотрите запуск Caddy [как service](/docs/running).

После запуска можно использовать [`caddy stop`](#caddy-stop) или API endpoint [`POST /stop`](/docs/api#post-stop), чтобы завершить фоновый процесс.



<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

Остановка (и перезапуск) сервера не связана с изменениями config. **Не используйте команду stop для изменения конфигурации в production, если не хотите downtime.** Вместо этого используйте команду [`caddy reload`](#caddy-reload).

</aside>


Плавно останавливает запущенный процесс Caddy (кроме процесса самой команды stop) и заставляет его завершиться. Для плавного shutdown она использует endpoint admin API [`POST /stop`](/docs/api#post-stop).

Адрес этого request можно настроить флагом `--address` или взять из указанного `--config`, если admin API запущенного экземпляра не использует listen address по умолчанию.

Если вы хотите остановить текущую конфигурацию, но не хотите завершать процесс, используйте [`caddy reload`](#caddy-reload) с пустой config или endpoint [`DELETE /config/`](/docs/api#delete-configpath).


<a id="caddy-storage"></a>
### `caddy storage`

<i>⚠️ Experimental</i>

Позволяет экспортировать и импортировать содержимое настроенного data storage Caddy.

Это полезно, когда нужно перейти с одного [storage module](/docs/json/storage/) на другой: экспортировать из старого, обновить config, затем импортировать в новый.

Следующую команду можно использовать, чтобы за один шаг скопировать storage между разными modules, используя старую и новую configs и передавая вывод команды export в команду import.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

Обратите внимание: при использовании [filesystem storage](/docs/conventions#data-directory) команду export нужно запускать от того же пользователя, от которого обычно работает Caddy, иначе может быть использовано неправильное расположение storage.

Например, при запуске Caddy как [systemd service](/docs/running#linux-service) он будет работать от пользователя `caddy`, поэтому команды export или import следует запускать от этого пользователя. Обычно это можно сделать с помощью `sudo -u caddy <command>`.

</aside>


#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` — config file load. Это обязательно, чтобы был подключен правильный storage module.

`--output` — имя файла, в который нужно записать tarball. Если это `-`, вывод записывается в stdout.



#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` — config file load. Это обязательно, чтобы был подключен правильный storage module.

`--input` — имя файла tarball, из которого нужно читать. Если это `-`, ввод читается из stdin.


<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Устанавливает root certificate для CA, управляемого [PKI app](/docs/json/apps/pki/) Caddy, в локальные trust stores. 

Caddy попытается автоматически установить свои root certificates в локальные trust stores при первой генерации, но это может не получиться, если у Caddy нет соответствующих прав на запись в trust store. Эта команда нужна, чтобы заранее установить certificates перед их использованием, если серверный процесс работает от непривилегированного пользователя (например, через systemd). На unix systems может понадобиться выполнить эту команду с `sudo`.

По умолчанию эта команда устанавливает root certificate для default CA Caddy (то есть "local"). Можно указать ID другой CA флагом `--ca`.

Эта команда попытается подключиться к [admin API](/docs/api) Caddy, чтобы получить root certificate через endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates). Можно явно указать `--address` или использовать флаг `--config`, чтобы загрузить admin address из config, если admin API запущенного экземпляра не использует listen address по умолчанию.

Также можно использовать binary `caddy` с этой командой для установки certificates на других машинах в вашей сети, если admin API сделан доступным для других машин; будьте осторожны и не открывайте admin API недоверенным clients.


<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Удаляет доверие к root certificate из локальных trust store(s).

Эта команда удаляет trust; она не обязательно полностью удаляет root certificate из trust stores. Поэтому повторное trust и untrust новых certificates может заполнять trust databases.

Эта команда не удаляет и не изменяет certificate files из настроенного storage Caddy.

Эту команду можно использовать одним из двух способов:
- Указать прямой путь к root certificate, доверие к которому нужно удалить, с помощью флага `--cert`.
- Получить root certificate из [admin API](/docs/api) через endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). Это поведение по умолчанию, если флаги не заданы.

Если используется admin API, CA ID по умолчанию — "local". Можно указать ID другой CA флагом `--ca`. Можно явно указать `--address` или использовать флаг `--config`, чтобы загрузить admin address из config, если admin API запущенного экземпляра не использует listen address по умолчанию.


<a id="caddy-upgrade"></a>
### `caddy upgrade`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Заменяет текущий binary Caddy последней версией с [нашей страницы загрузки](/download), с теми же установленными modules, включая все сторонние plugins, зарегистрированные на сайте Caddy.

Обновления не прерывают работающие servers; сейчас команда только заменяет binary на диске. Это может измениться в будущем, если мы найдем хороший способ сделать это.

Процесс upgrade отказоустойчив: текущий binary сначала сохраняется как backup (копируется рядом с текущим), и если что-то пойдет не так, автоматически восстанавливается. Если вы хотите сохранить backup после завершения upgrade process, используйте option `--keep-backup`.

Этой команде могут потребоваться повышенные права, если у вашего пользователя нет разрешения на запись в executable file.



<a id="caddy-add-package"></a>
### `caddy add-package`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Подобно `caddy upgrade`, заменяет текущий binary Caddy последней версией с теми же установленными modules, *плюс* packages, перечисленные как arguments и включенные в новый binary. Список packages, которые можно установить, смотрите на [нашей странице загрузки](/download). Каждый argument должен быть полным именем package.

Например:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



<a id="caddy-remove-package"></a>
### `caddy remove-package`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Подобно `caddy upgrade`, заменяет текущий binary Caddy последней версией с теми же установленными modules, но *без* packages, перечисленных как arguments, если они существовали в текущем binary. Выполните `caddy list-modules --packages`, чтобы увидеть список package names нестандартных modules, включенных в текущий binary.



<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

Проверяет конфигурационный файл, затем завершается. Эта команда десериализует config, затем загружает и provisions все его modules так, как если бы запускала config, но фактически config не запускается. Это выявляет errors в конфигурации, возникающие на этапах loading или provisioning, и является более строгой проверкой ошибок, чем простая serialization config как JSON.

`--config` — конфигурационный файл для проверки. Если это `-`, config читается из stdin. По умолчанию используется `Caddyfile` в текущем каталоге, если он есть.

`--adapter` — имя используемого адаптера конфигурации. Этот флаг не нужен, если имя файла `--config` начинается с `Caddyfile` или заканчивается на `.caddyfile`, что предполагает адаптер `caddyfile`. Иначе этот флаг обязателен, если предоставленный конфигурационный файл не в собственном JSON-формате Caddy.

`--envfile` загружает переменные окружения из указанного файла в формате `KEY=VALUE`. Поддерживаются комментарии, начинающиеся с `#`; ключи могут иметь префикс `export`; значения могут быть заключены в двойные кавычки (двойные кавычки внутри можно экранировать); поддерживаются многострочные значения.



<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

Выводит версию и завершается.



<a id="signals"></a>
## Signals

Caddy перехватывает некоторые signals и игнорирует другие. Signals могут запускать определенное поведение процесса.

Signal | Behavior
-------|----------
`SIGINT` | Graceful exit. Повторная отправка signal принудительно завершит процесс сразу.
`SIGQUIT` | Немедленно завершает Caddy, но все равно очищает locks в storage, потому что это важно.
`SIGTERM` | Graceful exit.
`SIGUSR1` | Перезагружает config file, но только если Caddy запущен через `caddy run` (без `--resume`) и в config не вносились изменения через [API](/docs/api) (включая [`caddy reload`]#caddy-reload)).
`SIGUSR2` | Игнорируется.
`SIGHUP` | Игнорируется.

Graceful exit означает, что новые подключения больше не принимаются, а существующие connections будут drained до закрытия socket. Может применяться grace period (и он настраивается). Когда grace period заканчивается, connections принудительно завершаются. Locks в storage и другие resources, которые отдельные modules должны освобождать, очищаются во время graceful shutdown.

Когда получен signal для перезагрузки config (`SIGUSR1`), он действует как принудительный config reload (то есть reload выполняется даже если текст config не изменился), что может заново загрузить dependent files вроде TLS certificates с диска. 

Signal-based config reloads включены только если Caddy запущен через `caddy run` с конфигурационным файлом. Они отключаются (signals игнорируются, в log появляется warning), если Caddy запущен с `--resume` (так как это подразумевает API workflow), или если любое изменение config получено через admin API, или если `caddy reload` запущен с *другим* filename или config adapter, чем при исходном запуске. Это нужно, чтобы избежать конфликтов между методами перезагрузки.



<a id="exit-codes"></a>
## Exit codes

Caddy возвращает code при завершении процесса:

Code | Meaning
-----|---------
`0` | Нормальное завершение.
`1` | Неудачный запуск. **Не перезапускайте процесс автоматически; вероятно, ошибка повторится, если не внести изменения.**
`2` | Принудительное завершение. Caddy был принудительно завершен без очистки resources.
`3` | Неудачное завершение. Caddy завершился с некоторыми errors во время cleanup.

В bash получить exit code последней команды можно через `echo $?`.
