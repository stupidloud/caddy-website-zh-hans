---
title: try_files (директива Caddyfile)
---

# try_files

Переписывает request URI path на первый из перечисленных файлов, который существует в site root. Если ни один файл не совпал, rewrite не выполняется.


<a id="syntax"></a>
## Синтаксис

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** — список файлов для проверки. URI path будет переписан на первый существующий файл.

  Чтобы сопоставлять directories, добавьте завершающий forward slash `/` к path. Все file paths относительны к site [root](root), а [glob patterns](https://pkg.go.dev/path/filepath#Match) будут развернуты.

  Каждый аргумент также может содержать query string; в этом случае query string также будет изменен, если совпадет именно этот файл.

  Если `try_policy` равен `first_exist` (по умолчанию), последний элемент списка может быть числом с prefix `=` (например, `=404`), которое как fallback выдаст ошибку с этим code; ошибку можно поймать и обработать через [`handle_errors`](handle_errors).

- **policy** — policy выбора файла из списка файлов. 

  По умолчанию: `first_exist`



<a id="expanded-form"></a>
## Развернутая форма

Директива `try_files` фактически является сокращением для:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

Обратите внимание, что эта директива не принимает matcher token. Если нужна более сложная matching logic, используйте развернутую форму выше как основу.

Подробнее см. matcher [`file`](/docs/caddyfile/matchers#file).



<a id="examples"></a>
## Примеры

Если запрос не совпадает ни с одним статическим файлом, переписать его на PHP index/router entrypoint:

```caddy-d
try_files {path} /index.php
```

То же самое, но с добавлением исходного path в query string (требуется некоторым legacy PHP apps):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

То же самое, но также сопоставлять directories:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Попытаться переписать на файл или directory, если он существует, иначе выдать ошибку 404 (которую можно поймать и обработать через [`handle_errors`](handle_errors)):

```caddy-d
try_files {path} {path}/ =404
```

Выбрать самую недавно развернутую версию статического файла (например, отдавать `index.be331df.html`, когда запрошен `index.html`):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
