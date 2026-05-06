---
title: php_fastcgi (директива Caddyfile)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Опинионированная директива, которая проксирует requests к PHP FastCGI server, например php-fpm.

- [Синтаксис](#syntax)
- [Развернутая форма](#expanded-form)
  - [Пояснение](#explanation)
- [Примеры](#examples)

[`reverse_proxy`](reverse_proxy) в Caddy способен обслуживать любое FastCGI application, но эта директива специально адаптирована для PHP apps. Это удобное сокращение, заменяющее [более длинную конфигурацию](#expanded-form).

Она ожидает, что любой `index.php` в site root работает как router. Если это нежелательно, либо перенастройте [поддирективу `try_files`](#try_files), чтобы изменить default rewrite behaviour, либо возьмите [развернутую форму](#expanded-form) за основу и настройте ее под свои требования.

Помимо перечисленных ниже поддиректив, эта директива также поддерживает все поддирективы [`reverse_proxy`](reverse_proxy#syntax). Например, можно включить load balancing и health checks.

**Большинство современных PHP apps нормально работают без дополнительных поддиректив или customization.** Поддирективы обычно используются только в отдельных edge cases или с legacy PHP apps.

<a id="syntax"></a>
## Синтаксис

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** — [addresses](/docs/conventions#network-addresses) FastCGI servers. Обычно это TCP socket или unix socket file.

- **root** <span id="root"/> задает root folder сайта. Рекомендуется всегда использовать [директиву `root`](root) вместе с `php_fastcgi`, но переопределение может быть полезно, когда ваш PHP-FPM upstream использует другой root, чем Caddy (см. [пример](#docker)). По умолчанию используется значение [директивы `root`](root), если она применена, иначе текущий рабочий каталог Caddy.

- **split** <span id="split"/> задает substrings для разделения URI на две части. Первый совпавший substring будет использован, чтобы отделить "path info" от path. Первая часть получает suffix с совпавшим substring и считается фактическим resource (CGI script) name. Вторая часть будет установлена в PATH_INFO для использования CGI script. По умолчанию: `.php`

- **index** <span id="index"/> задает filename, который нужно считать directory index file. Это влияет на file matcher в [развернутой форме](#expanded-form). По умолчанию: `index.php`. Можно установить в `off`, чтобы отключить rewrite fallback к `index.php`, когда matching file не найден.

- **try_files** <span id="try_files"/> задает override для default try-files rewrite. Подробности см. в [директиве `try_files`](try_files). По умолчанию: `{path} {path}/index.php index.php`.

- **env** <span id="env"/> устанавливает дополнительную environment variable в заданное значение. Можно указать несколько раз для нескольких environment variables. По умолчанию все релевантные FastCGI environment variables уже установлены (включая HTTP headers), но можно добавлять или переопределять variables по необходимости. 

- **resolve_root_symlink** <span id="resolve_root_symlink"/> когда directory [`root`](#root) является symbolic link (symlink), включает разрешение к фактическому значению. Иногда это используется как deployment strategy: symlink просто переключается на новую версию в другом directory. По умолчанию отключено, чтобы избежать повторных system calls.

- **capture_stderr** <span id="capture_stderr"/> включает захват и logging любых сообщений, отправленных upstream fastcgi server в `stderr`. По умолчанию logging выполняется на уровне `WARN`. Если response имеет status `4xx` или `5xx`, вместо этого используется уровень `ERROR`. По умолчанию `stderr` игнорируется.

- **dial_timeout** <span id="dial_timeout"/> — [duration value](/docs/conventions#durations), задающее время ожидания при подключении к upstream socket. По умолчанию: `3s`.

- **read_timeout** <span id="read_timeout"/> — [duration value](/docs/conventions#durations), задающее время ожидания при чтении из FastCGI upstream. По умолчанию: без timeout.

- **write_timeout** <span id="write_timeout"/> — [duration value](/docs/conventions#durations), задающее время ожидания при отправке в FastCGI upstream. По умолчанию: без timeout.


Поскольку эта директива является опинионированной оберткой над reverse proxy, можно использовать любые поддирективы [`reverse_proxy`](reverse_proxy#syntax), чтобы настроить ее.


<a id="expanded-form"></a>
## Развернутая форма

Директива `php_fastcgi` (без поддиректив) эквивалентна следующей конфигурации. Большинство современных PHP apps хорошо работают с этим preset. Если ваше app не работает так, можно заимствовать эту конфигурацию и настроить ее как нужно вместо использования сокращения `php_fastcgi`.

```caddy-d
route {
	# Добавить trailing slash для directory requests
	# Это redirection автоматически отключается, если "{http.request.uri.path}/index.php"
	# отсутствует в списке try_files
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Если запрошенный файл не существует, пробуем index files и предполагаем, что index.php всегда существует
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# Проксировать PHP files к FastCGI responder
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
### Пояснение

- Первый section занимается canonicalizing request path. Цель — гарантировать, что requests, нацеленные на directory на диске, действительно имеют trailing slash `/` в request path, так что для requests к этому directory валиден только один URL.

  Эта canonicalization происходит только если поддиректива `try_files` содержит `{path}/index.php` (по умолчанию).

  Это выполняется через request matcher, который совпадает только с requests, которые *не* заканчиваются slash и отображаются на directory на диске, содержащий файл `index.php`; при совпадении выполняется HTTP 308 redirect с добавленным trailing slash. Например, request с path `/foo` будет redirected на `/foo/` (с добавлением `/`, чтобы canonicalize path к directory), если `/foo/index.php` существует на диске.

- Следующий section выполняет path rewrites на основе того, существует ли matching file на диске. Также побочный эффект — запоминание части path после `.php` (если request path содержал `.php`). Это важно, чтобы Caddy корректно установил FastCGI environment variables.

  - Сначала проверяется, является ли `{path}` существующим на диске файлом. Если да, rewrite выполняется на этот path. Это фактически short-circuit остальное и гарантирует, что requests к files, которые *существуют* на диске, не будут иначе переписаны (см. следующие шаги). Например, если на диске есть файл `/js/app.js`, request к этому path останется без изменений.

  - Затем проверяется, является ли `{path}/index.php` существующим на диске файлом. Если да, rewrite выполняется на этот path. Для requests к directory вроде `/foo/` будет проверен `/foo//index.php` (нормализуется в `/foo/index.php`) и request будет переписан на этот path, если он существует. Такое поведение иногда полезно, если вы запускаете другое PHP app в subdirectory вашего webroot.

  - Наконец, rewrite всегда выполняется на `index.php` (для современных PHP apps он почти всегда существует). Это позволяет PHP app обрабатывать любые requests к paths, которые *не* соответствуют files на диске, используя script `index.php` как entrypoint.

- И наконец, последний section фактически проксирует request к вашему PHP FastCGI (или PHP-FPM) service, чтобы выполнить PHP code. Request matcher совпадает только с requests, которые заканчиваются на `.php`, поэтому любой file, который *не* является PHP script и *существует* на диске, *не* будет обработан этой директивой и пройдет дальше.

Директивы `php_fastcgi` обычно недостаточно самой по себе. Почти всегда ее следует использовать вместе с [директивой `root`](root), чтобы задать расположение ваших files на диске (для современных PHP apps это может быть `/var/www/html/public`, где directory `public` содержит `index.php`), и с [директивой `file_server`](file_server), чтобы отдавать static files (JS, CSS, images и т. д.), которые иначе не обрабатываются этой директивой и проходят дальше.



<a id="examples"></a>
## Примеры

Проксировать все PHP requests к FastCGI responder, слушающему `127.0.0.1:9000`:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

То же самое, но только для requests под `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

При использовании PHP-FPM, слушающего через unix socket:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[Директива `root`](root) почти всегда используется, чтобы указать directory с PHP scripts, а [директива `file_server`](file_server) — чтобы отдавать static files:

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> При обслуживании нескольких PHP apps через Caddy webroot для каждого app должен быть разным, чтобы Caddy мог отдельно читать и отдавать static files, а также обнаруживать существование PHP files.

Если вы используете Docker, часто ваши PHP-FPM containers имеют files, mounted в один и тот же root. В таком случае решение — mount files в Caddy container в разные directories, затем использовать [поддирективу `root`](#root), чтобы задать root для каждого container:

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Для PHP site, который не использует `index.php` как entrypoint, можно fallback к выдаче ошибки `404`. Ошибку можно поймать и обработать [директивой `handle_errors`](handle_errors):

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
