---
title: Распространенные шаблоны Caddyfile
---

<a id="common-caddyfile-patterns"></a>
# Распространенные шаблоны Caddyfile

На этой странице показаны несколько полных и минимальных конфигураций Caddyfile для распространенных сценариев. Они могут быть полезной отправной точкой для ваших собственных файлов Caddyfile.

Это не готовые решения, которые можно вставить без изменений; вам потребуется настроить доменное имя, порты или сокеты, пути к каталогам и т. д. Их цель — показать самые распространенные шаблоны конфигурации.

- [Статический файловый сервер](#static-file-server)
- [Обратный прокси](#reverse-proxy)
- [PHP](#php)
- [Перенаправление поддомена `www.`](#redirect-www-subdomain)
- [Завершающие косые черты](#trailing-slashes)
- [Wildcard-сертификаты](#wildcard-certificates)
- [Одностраничные приложения (SPA)](#single-page-apps-spas)
- [Проксирование из Caddy в другой Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## Статический файловый сервер

```caddy
example.com {
	root /var/www
	file_server
}
```

Как обычно, первая строка — это адрес сайта. [Директива `root`](/docs/caddyfile/directives/root) задает путь к корню сайта (`*` означает совпадение со всеми запросами, чтобы устранить неоднозначность с [matcher пути](/docs/caddyfile/matchers#path-matchers))&mdash;измените путь на каталог вашего сайта, если это не текущий рабочий каталог. Наконец, мы включаем [статический файловый сервер](/docs/caddyfile/directives/file_server).



<a id="reverse-proxy"></a>
## Обратный прокси

Проксировать все запросы:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Проксировать только запросы, путь которых начинается с `/api/`, а для всего остального отдавать статические файлы:

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Здесь используется [matcher запроса](/docs/caddyfile/matchers#syntax), чтобы сопоставить только запросы, начинающиеся с `/api/`, и проксировать их на backend. Все остальные запросы будут обслуживаться из [`root`](/docs/caddyfile/directives/root) сайта через [статический файловый сервер](/docs/caddyfile/directives/file_server). Это также опирается на то, что `reverse_proxy` находится выше `file_server` в [порядке директив](/docs/caddyfile/directives#directive-order).

Больше [примеров `reverse_proxy` приведено здесь](/docs/caddyfile/directives/reverse_proxy#examples).



## PHP

### PHP-FPM

Если запущен сервис PHP FastCGI, примерно такая конфигурация подходит для большинства современных PHP-приложений:

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

Настройте корень сайта соответственно; этот пример предполагает, что webroot вашего PHP-приложения находится в каталоге `public`&mdash;запросы к файлам, существующим на диске, будут обслуживаться через [`file_server`](/docs/caddyfile/directives/file_server), а все остальное будет направлено в `index.php` для обработки PHP-приложением.

Иногда для подключения к PHP-FPM можно использовать unix-сокет:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[Директива `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) на самом деле является сокращением для [нескольких частей конфигурации](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

В качестве альтернативы можно использовать [FrankenPHP](https://frankenphp.dev/) — дистрибутив Caddy, который вызывает PHP напрямую через CGO (привязки Go к C). Это может быть до 4 раз быстрее, чем PHP-FPM, и еще лучше, если можно использовать worker mode.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-www-subdomain"></a>
## Перенаправление поддомена `www.`

Чтобы **добавить** поддомен `www.` через HTTP-перенаправление:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Чтобы **удалить** его:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Чтобы удалить его сразу для **нескольких доменов**; здесь используются placeholders `{labels.*}`, которые представляют части имени хоста, индексируемые с `0` справа налево (например, `0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## Завершающие косые черты

Обычно это не нужно настраивать самостоятельно; [директива `file_server`](/docs/caddyfile/directives/file_server) автоматически добавляет или удаляет завершающие косые черты из запросов с помощью HTTP-перенаправлений, в зависимости от того, является запрошенный ресурс каталогом или файлом соответственно.

Тем не менее, при необходимости вы все равно можете принудительно применять завершающие косые черты в конфигурации. Есть два способа: внутренний и внешний.

<a id="internal-enforcement"></a>
### Внутреннее принудительное применение

Здесь используется директива [`rewrite`](/docs/caddyfile/directives/rewrite). Caddy внутренне перепишет URI, чтобы добавить или удалить завершающую косую черту:

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

При использовании rewrite запросы с завершающей косой чертой и без нее будут эквивалентны.


<a id="external-enforcement"></a>
### Внешнее принудительное применение

Здесь используется директива [`redir`](/docs/caddyfile/directives/redir). Caddy попросит браузер изменить URI, чтобы добавить или удалить завершающую косую черту:

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

При использовании redirect клиенту придется повторно отправить запрос, что закрепляет один допустимый URI для ресурса.



<a id="wildcard-certificates"></a>
## Wildcard-сертификаты

Для большинства issuers, включая Let's Encrypt, необходимо включить [ACME DNS challenge](/docs/automatic-https#dns-challenge), чтобы Caddy мог автоматизировать wildcard-сертификаты.

Если DNS challenge включен, начиная с Caddy 2.10 Caddy предпочтет применимый wildcard-сертификат, который уже настроен или управляется, прежде чем управлять отдельным сертификатом для поддомена.



Если нужно обслуживать несколько поддоменов с одним wildcard-сертификатом, лучший способ — использовать такой Caddyfile с применением [директивы `handle`](/docs/caddyfile/directives/handle) и [`host` matchers](/docs/caddyfile/matchers#host):

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# Fallback for otherwise unhandled domains
	handle {
		abort
	}
}
```

Необходимо включить [ACME DNS challenge](/docs/automatic-https#dns-challenge), чтобы Caddy автоматически управлял wildcard-сертификатами.



<a id="single-page-apps-spas"></a>
## Одностраничные приложения (SPA)

Когда web-страница выполняет собственную маршрутизацию, серверы могут получать много запросов к страницам, которых нет на стороне сервера, но которые можно отрисовать на стороне клиента, если вместо них отдать единый индексный файл. Web-приложения с такой архитектурой известны как SPA, или одностраничные приложения.

Основная идея в том, чтобы сервер "проверял файлы" и определял, существует ли запрошенный файл на стороне сервера; если нет, он откатывается к индексному файлу, где маршрутизацию выполняет клиент (обычно с помощью клиентского JavaScript).

Типичная конфигурация SPA обычно выглядит примерно так:

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

Если SPA совмещено с API или другими endpoint'ами, существующими только на стороне сервера, для них стоит использовать блоки `handle`, чтобы обрабатывать их отдельно:

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

Если ваш `index.html` содержит ссылки на JS/CSS-ресурсы с хешированными именами файлов, стоит рассмотреть добавление заголовка `Cache-Control`, который укажет клиентам *не* кешировать его (чтобы при изменении ресурсов браузеры загружали новые версии). Поскольку rewrite `try_files` используется для отдачи `index.html` с любого пути, который не соответствует другому файлу на диске, можно обернуть `try_files` в `route`, чтобы handler `header` выполнялся *после* rewrite (обычно он выполнялся бы раньше из-за [порядка директив](/docs/caddyfile/directives#directive-order)):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Проксирование из Caddy в другой Caddy

Если один экземпляр Caddy доступен публично (назовем его "front"), а другой экземпляр Caddy находится в вашей частной сети (назовем его "back") и обслуживает фактическое приложение, можно использовать [директиву `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy), чтобы передавать запросы дальше.

Экземпляр front:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Экземпляр back:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Этот пример обслуживает два разных домена, проксируя оба на один и тот же экземпляр Caddy back на порту `80`. Экземпляр back обслуживает два домена по-разному, поэтому он настроен двумя отдельными блоками сайтов.

- На back используется [`http://`](/docs/caddyfile/concepts#addresses), чтобы принимать HTTP на порту `80`. Экземпляр front завершает TLS, а трафик между front и back идет по частной сети, поэтому повторно шифровать его не нужно.

- При необходимости на экземпляре back можно использовать другой порт, например `8080`; просто добавьте `:8080` к каждому адресу сайта в конфигурации back ИЛИ задайте [глобальную опцию `http_port`](/docs/caddyfile/options#http_port) равной `8080`.

- На back [глобальная опция `trusted_proxies`](/docs/caddyfile/options#trusted_proxies) используется, чтобы указать Caddy доверять экземпляру front как прокси. Это гарантирует сохранение реального IP-адреса клиента.

- Если идти дальше, можно иметь больше одного экземпляра back и выполнять между ними [load balancing](/docs/caddyfile/directives/reverse_proxy#load-balancing). Можно настроить mTLS (mutual TLS) с помощью [`acme_server`](/docs/caddyfile/directives/acme_server) на экземпляре front так, чтобы он выступал как CA для экземпляра back (это полезно, если трафик между front и back проходит через недоверенные сети).
