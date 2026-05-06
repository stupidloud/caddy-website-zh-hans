---
title: Руководство по Caddyfile
---

<a id="caddyfile-tutorial"></a>
# Руководство по Caddyfile

Это руководство научит вас основам [HTTP Caddyfile](/docs/caddyfile), чтобы вы могли быстро и легко создавать понятные и рабочие конфигурации сайтов.

**Цели:**
- 🔲 Первый сайт
- 🔲 Сервер статических файлов
- 🔲 Templates
- 🔲 Сжатие
- 🔲 Несколько сайтов
- 🔲 Matchers
- 🔲 Переменные окружения
- 🔲 Комментарии

**Предварительные требования:**
- Базовые навыки работы с терминалом / командной строкой
- Базовые навыки работы с текстовым редактором
- `caddy` в вашем PATH

---

Создайте новый текстовый файл с именем `Caddyfile` (без расширения).

Первое, что нужно ввести, — [адрес](/docs/caddyfile/concepts#addresses) вашего сайта:

```caddy
localhost
```

<aside class="tip">

Если порты HTTP и HTTPS (80 и 443 соответственно) являются привилегированными портами в вашей ОС, вам нужно либо запускать с повышенными правами, либо использовать более высокий порт. Чтобы использовать более высокий порт, просто измените адрес на что-то вроде `localhost:2015` и измените HTTP-порт с помощью параметра Caddyfile [http_port](/docs/caddyfile/options).

</aside>


Затем нажмите Enter и укажите, что он должен делать. Для этого руководства сделайте ваш Caddyfile таким:

```caddy
localhost

respond "Hello, world!"
```

Сохраните его и запустите Caddy (поскольку это учебное руководство, мы используем флаг `--watch`, чтобы изменения в Caddyfile применялись автоматически):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Если вы получаете ошибки прав доступа, попробуйте использовать более высокий порт в адресе (например, `localhost:2015`) и [изменить HTTP-порт](/docs/caddyfile/options), либо запустите с повышенными правами.

</aside>


В первый раз у вас попросят пароль. Это нужно, чтобы Caddy мог обслуживать ваш сайт по HTTPS.

<aside class="tip">

Caddy по умолчанию обслуживает все сайты по HTTPS, если host или IP является частью адреса сайта. [Автоматический HTTPS](/docs/automatic-https) можно отключить, явно добавив к адресу префикс `http://`.

</aside>


<aside class="complete">Первый сайт</aside>

Откройте [localhost](https://localhost) в браузере и посмотрите, как работает ваш веб-сервер, уже с HTTPS!

<aside class="tip">
	Если в первый раз появится ошибка сертификата, возможно, потребуется перезапустить браузер.
</aside>

Это не особенно интересно, поэтому изменим статический ответ на [file server](/docs/caddyfile/directives/file_server) с включенным выводом списка каталогов:

```caddy
localhost

file_server browse
```

Сохраните Caddyfile, затем обновите вкладку браузера. Вы должны увидеть либо список файлов, либо HTML-страницу, если в текущем каталоге есть index-файл.

<aside class="complete">Сервер статических файлов</aside>

<a id="adding-functionality"></a>
## Добавление функциональности

Сделаем с нашим файловым сервером что-нибудь интересное: будем обслуживать templated page. Создайте новый файл и вставьте в него это:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Сохраните это как `caddy.html` в текущем каталоге и загрузите в браузере: [https://localhost/caddy.html](https://localhost/caddy.html)

Вывод будет таким:

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Подождите. Мы должны были увидеть сегодняшнюю дату. Почему это не сработало? Потому что сервер еще не настроен на обработку templates! Исправить легко: просто добавьте строку в Caddyfile, чтобы он выглядел так:

```caddy
localhost

templates
file_server browse
```

Сохраните это, затем обновите вкладку браузера. Вы должны увидеть:

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

С [модулем templates](/docs/modules/http.handlers.templates) Caddy можно делать много полезного со статическими файлами: подключать другие HTML-файлы, выполнять sub-requests, задавать response headers, работать со структурами данных и многое другое!

<aside class="complete">Templates</aside>

Хорошая практика — сжимать ответы быстрым и современным алгоритмом сжатия. Включим поддержку Gzip и Zstandard с помощью директивы [`encode`](/docs/caddyfile/directives/encode):

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Сжатие</aside>

Это базовый процесс запуска semi-advanced, production-ready сайта!

Когда вы будете готовы включить [автоматический HTTPS](/docs/automatic-https), просто замените адрес сайта (`localhost` в нашем руководстве) на ваше доменное имя. Подробнее смотрите в нашем [кратком руководстве по HTTPS](/docs/quick-starts/https).

<a id="multiple-sites"></a>
## Несколько сайтов

С текущим Caddyfile у нас может быть только одно определение сайта! Только первая строка может быть адресом или адресами сайта, а вся остальная часть файла должна быть директивами для этого сайта.

Но легко сделать так, чтобы можно было добавить больше сайтов!

Наш Caddyfile на текущий момент:

```caddy
localhost

encode
templates
file_server browse
```

эквивалентен этому:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

за исключением того, что второй вариант позволяет добавлять больше сайтов.

Обернув блок сайта в фигурные скобки `{ }`, мы можем определить несколько разных сайтов в одном Caddyfile.

Например:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

Когда блоки сайтов обернуты в фигурные скобки, только [адреса](/docs/caddyfile/concepts#addresses) находятся вне фигурных скобок, а только [директивы](/docs/caddyfile/directives) находятся внутри них.

Для нескольких сайтов, которые используют одну и ту же конфигурацию, можно добавить больше адресов, например:

```caddy
:8080, :8081 {
	...
}
```

Затем можно определить столько разных сайтов, сколько нужно, если каждый адрес уникален.

<aside class="complete">Несколько сайтов</aside>


<a id="matchers"></a>
## Matchers

Иногда нужно применять некоторые директивы только к определенным запросам. Например, предположим, что нам нужны и файловый сервер, и reverse proxy, но очевидно, что нельзя делать оба действия для каждого запроса! Либо файловый сервер запишет ответ со статическим файлом, либо reverse proxy передаст запрос backend и вернет его ответ.

Эта конфигурация не будет работать так, как нам нужно (`reverse_proxy` получит приоритет из-за [порядка директив](/docs/caddyfile/directives#directive-order)):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

На практике reverse proxy может понадобиться только для API-запросов, то есть запросов с базовым путем `/api/`. Это легко сделать, добавив [matcher token](/docs/caddyfile/matchers#syntax):

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

Готово; теперь reverse proxy будет приоритетным для всех запросов, начинающихся с `/api/`.

Часть `/api/*`, которую мы только что добавили, называется **matcher token**. Это matcher token, потому что он начинается с прямой косой черты `/` и стоит сразу после директивы (но для уверенности всегда можно посмотреть [документацию директивы](/docs/caddyfile/directives)).

Matchers действительно мощные. Можно объявлять именованные matchers и использовать их как `@name`, чтобы сопоставлять не только путь запроса! Перед продолжением уделите минуту тому, чтобы [узнать больше о matchers](/docs/caddyfile/matchers)!

<aside class="complete">Matchers</aside>

<a id="environment-variables"></a>
## Переменные окружения

Адаптер Caddyfile позволяет подставлять [переменные окружения](/docs/caddyfile/concepts#environment-variables) до разбора Caddyfile.

Сначала задайте переменную окружения (в той же shell, где запускается Caddy):

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Затем ее можно использовать в Caddyfile так:

```caddy
{$SITE_ADDRESS}

file_server
```

Перед разбором Caddyfile она будет развернута в:

```caddy
localhost:9055

file_server
```

Переменные окружения можно использовать в любом месте Caddyfile, для любого количества tokens.

<aside class="complete">Переменные окружения</aside>


<a id="comments"></a>
## Комментарии

И последнее, что будет очень полезно: если вы хотите оставить замечание или заметку в Caddyfile, можно использовать комментарии, начинающиеся с `#`:

```caddy
# this starts a comment
```

<aside class="complete">Комментарии</aside>

<a id="further-reading"></a>
## Дополнительное чтение

- [Основные понятия Caddyfile](/docs/caddyfile/concepts)
- [Директивы](/docs/caddyfile/directives)
- [Распространенные шаблоны](/docs/caddyfile/patterns)
