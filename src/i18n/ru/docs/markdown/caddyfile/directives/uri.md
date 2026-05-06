---
title: uri (директива Caddyfile)
---

# uri

Изменяет URI запроса. Может удалять path prefix/suffix или заменять substrings во всем URI.

Эта директива отличается от [`rewrite`](rewrite): `uri` *дифференциально* изменяет URI, а не сбрасывает его в полностью другое значение, как это делает `rewrite`. Если `rewrite` обрабатывается специально как internal redirect, то `uri` — просто еще один middleware.


<a id="syntax"></a>
## Синтаксис

Поддерживается несколько разных операций:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

Первый аргумент, не являющийся matcher, задает операцию:

- **strip_prefix** удаляет prefix из path.

- **strip_suffix** удаляет suffix из path.

- **replace** выполняет substring replacement по всему URI.

	- **&lt;target&gt;** — prefix, suffix или search string/regular expression. Если это prefix, ведущий forward slash можно опустить, поскольку paths всегда начинаются с forward slash.

	- **&lt;replacement&gt;** — replacement string. Поддерживает использование capture groups с синтаксисом `$name` или `${name}`, либо с числом для index, например `$1`. Подробности см. в [документации Go](https://golang.org/pkg/regexp/#Regexp.Expand). Если replacement value равно `""`, совпавший текст удаляется из значения.

	- **&lt;limit&gt;** — необязательный предел максимального числа replacements.

- **path_regexp** выполняет replacement по regular expression в части path URI.

	- **&lt;target&gt;** — prefix, suffix или search string/regular expression. Если это prefix, ведущий forward slash можно опустить, поскольку paths всегда начинаются с forward slash.

	- **&lt;replacement&gt;** — replacement string. Поддерживает использование capture groups с синтаксисом `$name` или `${name}`, либо с числом для index, например `$1`. Подробности см. в [документации Go](https://golang.org/pkg/regexp/#Regexp.Expand). Если replacement value равно `""`, совпавший текст удаляется из значения.

- **query** выполняет изменения URI query; режим зависит от prefix имени параметра или количества аргументов. Блок можно использовать, чтобы указать несколько операций сразу, сгруппированных и выполненных в таком порядке: rename 🡒 set 🡒 append 🡒 replace 🡒 delete.

	- Без prefix параметр устанавливается в query с заданным значением.
	
	  Например, `uri query foo bar` установит значение параметра `foo` в `bar`.

	- Prefix `-` удаляет параметр из query.
	
	  Например, `uri query -foo` удалит параметр `foo` из query.

	- Prefix `+` добавляет параметр в query с заданным значением. Это *не* перезапишет существующий параметр с тем же именем (опустите `+`, чтобы перезаписать).
	
	  Например, `uri query +foo bar` добавит `foo=bar` в query.

	- Param с `>` как infix переименует параметр в значение после `>`. 
	
	  Например, `uri query foo>bar` переименует параметр `foo` в `bar`.

	- При трех аргументах выполняется regular expression replacement значения query, где первый аргумент — имя query param, второй — search value, третий — replacement. Первый аргумент (param name) может быть `*`, чтобы выполнить replacement для всех query params.
	
	  Поддерживает использование capture groups с синтаксисом `$name` или `${name}`, либо с числом для index, например `$1`. Подробности см. в [документации Go](https://golang.org/pkg/regexp/#Regexp.Expand). Если replacement value равно `""`, совпавший текст удаляется из значения.
	
	  Например, `uri query foo ^(ba)r $1z` заменит значение параметра `foo`, если значение начиналось с `bar`, и результатом станет `baz`.

URI mutations выполняются на нормализованной или unescaped форме URI. Однако escape sequences можно использовать в prefix или suffix patterns, чтобы сопоставлять только эти literal escapes в этих позициях request path. Например, `uri strip_prefix /a/b` перепишет и `/a/b/c`, и `/a%2Fb/c` в `/c`; а `uri strip_prefix /a%2Fb` перепишет `/a%2Fb/c` в `/c`, но не совпадет с `/a/b/c`.

URI path очищается от directory traversal dots перед изменениями. Кроме того, multiple slashes (например, `//`) объединяются, если только `<target>` тоже не содержит multiple slashes.

<a id="similar-directives"></a>
## Похожие директивы

Некоторые другие директивы также могут изменять request URI.

- [`rewrite`](rewrite) изменяет весь path и query на новое значение вместо частичного изменения значения.

- [`handle_path`](handle_path) делает то же, что и [`handle`](handle), но удаляет prefix из запроса перед запуском своих handlers. Во многих случаях его можно использовать вместо `uri strip_prefix`, чтобы убрать одну лишнюю строку конфигурации.


<a id="examples"></a>
## Примеры

Удалить `/api` из начала всех request paths:

```caddy-d
uri strip_prefix /api
```

Удалить `.php` из конца всех request paths:

```caddy-d
uri strip_suffix .php
```

Заменить "/docs/" на "/v1/docs/" в любом request URI:

```caddy-d
uri replace /docs/ /v1/docs/
```

Свернуть все повторяющиеся slashes в request path (но не в request query) в один slash:

```caddy-d
uri path_regexp /{2,} /
```

Установить значение query parameter `foo` в `bar`:

```caddy-d
uri query foo bar
```

Удалить параметр `foo` из query:

```caddy-d
uri query -foo
```

Переименовать query parameter `foo` в `bar`:

```caddy-d
uri query foo>bar
```

Добавить параметр `bar` в query:

```caddy-d
uri query +foo bar
```

Заменить значение query parameter `foo`, где значение начинается с `bar`, на `baz`:

```caddy-d
uri query foo ^(ba)r $1z
```

Выполнить несколько query operations сразу:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
