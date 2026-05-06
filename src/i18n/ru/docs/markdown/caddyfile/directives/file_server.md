---
title: file_server (директива Caddyfile)
---

<script>
ready(function() {
	// Fix inline browse arg
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# file_server

Статический файловый сервер, поддерживающий реальные и виртуальные файловые системы. Он формирует пути к файлам, добавляя URI path запроса к [корневому пути сайта](root).

По умолчанию он обеспечивает canonical URIs; это означает, что HTTP redirects будут выдаваться для запросов к каталогам без завершающей косой черты (чтобы добавить ее) или для запросов к файлам с завершающей косой чертой (чтобы удалить ее). Однако redirects не выдаются, если internal rewrite изменяет последний элемент пути (имя файла).

Чаще всего директива `file_server` используется вместе с директивой [`root`](root), чтобы задать file root для всего сайта. У этой директивы также есть поддиректива `root` (см. ниже), которая задает root только для этого handler'а (не рекомендуется). Обратите внимание, что site root не дает sandbox-гарантий: file server предотвращает directory traversal через компоненты пути, но symbolic links внутри root все еще могут разрешать доступ за пределы root.

Когда возникают ошибки (например, file not found `404`, permission denied `403`), будут вызваны error routes. Используйте директиву [`handle_errors`](handle_errors), чтобы определить error routes и показывать пользовательские страницы ошибок.

При использовании `browse` вывод по умолчанию создается HTML-шаблоном. Клиенты могут запросить listing каталога как JSON или plaintext, используя headers `Accept: application/json` или `Accept: text/plain` соответственно. JSON-вывод может быть полезен для scripting, а plaintext-вывод — для использования человеком в терминале.


<a id="syntax"></a>
## Синтаксис

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> задает альтернативную (возможно, виртуальную) файловую систему. Здесь можно использовать любой Caddy module в namespace `caddy.fs`. Любой root path/prefix все равно будет применяться к альтернативным file system modules. По умолчанию используется локальный диск.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 добавляет [флаг `--embed`](https://github.com/caddyserver/xcaddy#custom-builds), чтобы встроить дерево файловой системы в пользовательскую сборку Caddy, и регистрирует module `fs` с именем `embedded`, который позволяет распространять статический сайт как исполняемый файл Caddy.

- **root** <span id="root"/> задает путь к site root. Это похоже на директиву [`root`](root), но применяется только к этому экземпляру file server и переопределяет любой другой site root, который мог быть определен. По умолчанию: `{http.vars.root}` или текущий рабочий каталог. Примечание: эта поддиректива изменяет root только для этого handler'а. Чтобы другие директивы (например, [`try_files`](try_files) или [`templates`](templates)) знали тот же site root, используйте вместо этого директиву [`root`](root).

- **hide** <span id="hide"/> — список файлов или папок, которые нужно скрыть; при запросе file server будет делать вид, что они не существуют. Принимает placeholders и glob patterns. Обратите внимание, что это пути *file system*, А НЕ request paths. Иными словами, относительные пути используют текущий рабочий каталог как базу, А НЕ site root; а все пути перед сравнением преобразуются в абсолютную форму (если возможно). Указание имени файла или pattern без разделителя пути скрывает все файлы с совпадающим именем независимо от их расположения; иначе будет предпринята попытка совпадения по path prefix, а затем globular match. Поскольку это конфигурация Caddyfile, активные configuration file(s) по умолчанию будут добавлены. Сравнения hide чувствительны к регистру; на case-insensitive filesystems путь запроса с другим регистром все равно может разрешиться в тот же путь на диске, поэтому `hide` не следует считать границей безопасности для чувствительных путей.

- **index** <span id="index"/> — список имен файлов, которые нужно искать как index files. По умолчанию: `index.html index.txt`

- **browse** <span id="browse"/> включает listings файлов для запросов к каталогам, у которых нет index file.

  - **<template_file>** <span id="template_file"/> — необязательный пользовательский template file для listings каталогов. По умолчанию используется шаблон, который можно извлечь командой `caddy file-server export-template`; она выведет стандартный шаблон в stdout. Встроенный шаблон также можно найти [здесь в исходном коде ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html). Browse templates также могут использовать actions из [стандартного модуля templates](/docs/modules/http.handlers.templates#docs).

  - **reveal_symlinks** <span id="reveal_symlinks"/> включает показ целей symbolic links в listings каталогов. По умолчанию цели symlink скрыты, и показывается только сам файл-ссылка.

  - **sort** <span id="sort"/> изменяет сортировку по умолчанию для listings каталогов. Первый параметр — поле/столбец для сортировки: `name`, `namedirfirst`, `size` или `time`. Второй аргумент — необязательное направление: `asc` или `desc`. Например, `sort name desc` отсортирует по имени в порядке убывания.

  - **file_limit** <span id="file_limit"/> задает максимальное количество файлов для показа в listings каталогов. По умолчанию: `10000`. Если число файлов превышает этот предел, будут показаны только первые N файлов, где N — указанный предел.

- **precompressed** <span id="precompressed"/> — список encoding formats, в которых нужно искать precompressed sidecar files. Аргументы — упорядоченный список encoding formats для поиска предварительно сжатых [sidecar files](https://en.wikipedia.org/wiki/Sidecar_file). Поддерживаемые форматы: `gzip` (`.gz`), `zstd` (`.zst`) и `br` (`.br`). Если форматы опущены, по умолчанию используется `br zstd gzip` (именно в этом порядке).

  Все file lookups сначала проверяют существование несжатого файла. После его обнаружения Caddy ищет sidecar files с расширением файла для каждого включенного формата. Если precompressed sidecar file найден, Caddy ответит предварительно сжатым файлом, установив соответствующий response header `Content-Encoding`. Иначе Caddy ответит обычным несжатым файлом. Если включена [директива `encode`](encode), она может сжать ответ on-the-fly, если предварительно сжатой версии нет.

- **status** <span id="status"/> — необязательное переопределение status code, используемое при записи ответа. Особенно полезно при ответе на запрос [пользовательской страницей ошибки](handle_errors). Может быть 3-значным status code, например: `404`. Placeholders поддерживаются. По умолчанию записанный status code обычно будет `200` или `206` для partial content.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> отключает поведение по умолчанию с redirect (добавить завершающую косую черту, если path запроса является каталогом, или удалить завершающую косую черту, если path запроса является файлом). Обратите внимание, что по умолчанию canonicalization не выполняется, если последний элемент path запроса (имя файла) был изменен internal rewrite, чтобы не затереть явный rewrite неявным поведением.

- **pass_thru** <span id="pass_thru"/> включает режим pass-thru, который продолжает выполнение следующего HTTP handler в route, если запрошенный файл не найден, вместо генерации ошибки `404` (с вызовом routes [`handle_errors`](handle_errors)). На практике это полезно только внутри блока [`route`](route), где после `file_server` следуют другие handler directives, потому что эта директива фактически [упорядочена последней](/docs/caddyfile/directives#directive-order).


<a id="examples"></a>
## Примеры

Статический файловый сервер из текущего каталога:

```caddy-d
file_server
```

С включенными listings файлов:

```caddy-d
file_server browse
```

Обслуживать статические файлы только внутри папки `/static`:

```caddy-d
file_server /static/*
```

Директива `file_server` обычно используется вместе с [директивой `root`](root), чтобы задать root path, из которого будут обслуживаться файлы:

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Если вы запускаете Caddy как systemd service, чтение файлов из `/home` не будет работать, потому что пользователь `caddy` не имеет "executable" permission на каталог `/home` (необходимо для traversal). Рекомендуется вместо этого размещать файлы в `/srv` или `/var/www/html`.

</aside>


Скрыть все папки `.git` и их содержимое:

```caddy-d
file_server {
	hide .git
}
```

Если client поддерживает это (header `Accept-Encoding`), проверить наличие precompressed files рядом с запрошенным файлом. Поэтому если запрошен `/path/to/file`, проверяются `/path/to/file.br`, `/path/to/file.zst` и `/path/to/file.gz` в этом порядке, и отдается первый доступный файл с соответствующим `Content-Encoding`:

```caddy-d
file_server {
	precompressed
}
```
