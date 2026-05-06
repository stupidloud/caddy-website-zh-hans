---
title: Request matchers (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

<a id="request-matchers"></a>
# Request Matchers

**Request matchers** можно использовать для filter (или classify) requests по разным criteria.

- [Синтаксис](#syntax)
	- [Примеры](#examples)
	- [Wildcard matchers](#wildcard-matchers)
	- [Path matchers](#path-matchers)
	- [Named matchers](#named-matchers)
- [Стандартные matchers](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


<a id="syntax"></a>
## Синтаксис

В Caddyfile **matcher token**, следующий сразу после directive, может ограничить scope этой directive. Matcher token может иметь одну из этих forms:

1. [**`*`**](#wildcard-matchers), чтобы match all requests (wildcard; default).
2. [**`/path`**](#path-matchers), начинается с forward slash, чтобы match request path.
3. [**`@name`**](#named-matchers), чтобы указать *named matcher*.

Если directive поддерживает matchers, в ее syntax documentation будет `[<matcher>]`. Matcher tokens [обычно optional](/docs/caddyfile/directives#syntax), что обозначается `[ ]`. Если matcher token omitted, это то же самое, что wildcard matcher (`*`).


<a id="examples"></a>
#### Примеры

Эта directive применяется ко [всем](#wildcard-matchers) HTTP requests:

```caddy-d
reverse_proxy localhost:9000
```

И это то же самое (`*` здесь не нужен):

```caddy-d
reverse_proxy * localhost:9000
```

Но эта directive применяется только к requests, у которых [path](#path-matchers) начинается с `/api/`:

```caddy-d
reverse_proxy /api/* localhost:9000
```

Чтобы match по чему-то кроме path, определите [named matcher](#named-matchers) и ссылайтесь на него через `@name`:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### Wildcard matchers

Wildcard (или "catch-all") matcher `*` match all requests и нужен только если matcher token required. Например, если first argument, который вы хотите передать directive, также является path, он будет выглядеть точно как path matcher! Поэтому можно использовать wildcard matcher для disambiguate, например:

```caddy-d
root * /home/www/mysite
```

Иначе этот matcher используется нечасто. В целом мы рекомендуем omit его, если syntax не требует.


<a id="path-matchers"></a>
### Path matchers

Matching by URI path — самый распространенный способ match requests, поэтому matcher можно inline так:

```caddy-d
redir /old.html /new.html
```

Path matcher tokens должны начинаться с forward slash `/`.

**[Path matching](#path) по умолчанию exact match, а не prefix match.** Для fast prefix match нужно append `*`. Обратите внимание, что `/foo*` match `/foo`, `/foo/` и `/foobar`; возможно, вам на самом деле нужен `/foo/*`.


<a id="named-matchers"></a>
### Named matchers

Все matchers, которые не являются path или wildcard matchers, должны быть named matchers. Это matcher, определенный вне конкретной directive, и его можно reuse.

Определение matcher с unique name дает больше flexibility, позволяя combine [любые доступные matchers](#standard-matchers) в set:

```caddy-d
@name {
	...
}
```

или, если в set только один matcher, можно записать его в одну строку:

```caddy-d
@name ...
```

Затем matcher можно использовать так, указав его first argument для directive:

```caddy-d
directive @name
```

Например, это проксирует HTTP/1.1 websocket requests к `localhost:6001`, а другие requests к `localhost:8080`. Оно match requests, у которых есть header field `Connection`, *containing* `Upgrade`, **и** другое field `Upgrade` со значением exactly `websocket`:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Если matcher set состоит только из одного matcher, one-liner syntax тоже работает:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

Как special case, matcher [`expression`](#expression) можно использовать без указания его name, если после matcher name идет один [quoted](/docs/caddyfile/concepts#tokens-and-quotes) argument (само CEL expression):

```caddy-d
@not-found `{err.status_code} == 404`
```

Как и directives, named matcher definitions должны находиться внутри [site blocks](/docs/caddyfile/concepts#structure), где они используются.

Named matcher definition образует *matcher set*. Matchers в set AND'ed together; то есть все должны match. Например, если в set есть matcher [`header`](#header) и [`path`](#path), оба должны match.

Несколько matchers одного type могут быть merged (например, multiple [`path`](#path) matchers in same set) с использованием boolean algebra (AND/OR), как описано в соответствующих разделах ниже.

Для более complex boolean matching logic рекомендуется использовать matcher [`expression`](#expression), чтобы написать CEL expression, поддерживающее **and** `&&`, **or** `||` и **parentheses** `( )`.





<a id="standard-matchers"></a>
## Стандартные matchers

Полную документацию matcher можно найти [в документации соответствующего matcher module](/docs/json/apps/http/servers/routes/match/).

Requests можно match следующими способами:



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

По client IP address. Принимает exact IPs или CIDR ranges. IPv6 zones поддерживаются.

Этот matcher лучше использовать, когда настроена global option [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies); иначе он ведет себя идентично matcher [`remote_ip`](#remote-ip). Только requests от trusted proxies будут иметь client IP parsed at start of request; untrusted requests будут использовать remote IP address immediate peer или address, set via [PROXY protocol](/docs/caddyfile/options#proxy-protocol).

Как shortcut, `private_ranges` можно использовать, чтобы match все private IPv4 и IPv6 ranges. Это то же самое, что указать все эти ranges: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

В одном named matcher может быть несколько `client_ip` matchers, и их ranges будут merged and OR'ed together.

#### Пример:

Match requests from private IPv4 addresses:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Этот matcher часто paired with matcher [`not`](#not), чтобы invert match. Например, чтобы abort all connections from *public* IPv4 и IPv6 addresses (то есть inverse всех private ranges):

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

В [CEL expression](#expression) это выглядело бы так:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

По любому [CEL (Common Expression Language)](https://github.com/google/cel-spec) expression, которое возвращает `true` или `false`.

Большинство других request matchers также можно использовать в expressions как functions, что дает больше flexibility для boolean logic, чем вне expressions. Смотрите documentation каждого matcher для supported syntax внутри CEL expressions.

Caddy [placeholders](/docs/conventions#placeholders) (или [Caddyfile shorthands](/docs/caddyfile/concepts#placeholders)) можно использовать в этих CEL expressions, поскольку они preprocessed и converted в обычные CEL function calls до interpretation CEL environment. Если placeholder нужно передать как string argument в matcher function, leading `{` следует escape backslash `\`, чтобы он не был preprocessed, например `file('\{path}.md')`.

Для удобства matcher name можно omit, если defined named matcher состоит только из CEL expression. CEL expression должно быть [quoted](/docs/caddyfile/concepts#tokens-and-quotes) (рекомендуются backticks или heredocs). Это читается довольно приятно:

```caddy-d
@mutable `{method}.startsWith("P")`
```

В этом случае предполагается CEL matcher.

#### Примеры:

Match requests, whose methods start with `P`, например `PUT` или `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

Match requests, где handler returned error status code `404`, используется вместе с directive [`handle_errors`](/docs/caddyfile/directives/handle_errors):

```caddy-d
@404 expression {err.status_code} == 404
```

Match requests, где path matches one of two different regular expressions; это можно написать только через expression, потому что matcher [`path_regexp`](#path-regexp) обычно может exist только once per named matcher:

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

Или то же самое, omitting matcher name и wrapping в [backticks](/docs/caddyfile/concepts#tokens-and-quotes), чтобы parsed as single token:

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

Можно использовать [heredoc syntax](/docs/caddyfile/concepts#heredocs), чтобы писать multi-line CEL expressions:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

По files.

- `root` определяет directory, где искать files. Default — текущий working directory или variable `root` [variable](/docs/modules/http.handlers.vars) (`{http.vars.root}`), если set (может быть set через directive [`root`](/docs/caddyfile/directives/root)).

- `try_files` checks files в своем list, которые match try_policy.

  Чтобы match directories, append trailing forward slash `/` к path. Все file paths relative to site [root](/docs/caddyfile/directives/root), а [glob patterns](https://pkg.go.dev/path/filepath#Match) будут expanded.

  Если `try_policy` — `first_exist` (default), последний item в list может быть number с prefix `=` (например, `=404`), который как fallback emit error с этим code; error можно catch and handle через [`handle_errors`](/docs/caddyfile/directives/handle_errors).



- `try_policy` указывает, как choose file. Default — `first_exist`.

	- `first_exist` checks for file existence. Выбирается первый existing file.

	- `first_exist_fallback` похож на `first_exist`, но assumes, что последний element в list всегда exists, чтобы avoid disk access.

	- `smallest_size` выбирает file с smallest size.

	- `largest_size` выбирает file с largest size.

	- `most_recently_modified` выбирает file, который был most recently modified.

- `split_path` causes path to be split at first delimiter in list, найденный в каждом filepath to try. Для каждого split value left-hand side split, including delimiter itself, будет filepath, который tried. Например, `/remote.php/dav/` с delimiter `.php` попробует file `/remote.php`. Каждый delimiter должен appear at end of URI path component, чтобы использоваться как split delimiter. Это niche setting и mostly used when serving PHP sites.

Поскольку `try_files` с policy `first_exist` очень common, для него есть one-line shortcut:

```caddy-d
file <files...>
```

Empty matcher `file` (без files после него) проверит, существует ли requested file, verbatim from URI, relative to [site root](/docs/caddyfile/directives/root). Фактически это то же самое, что `file {path}`.


<aside class="tip">

Поскольку rewriting based on existence of file on disk очень common, есть также directive [`try_files`](/docs/caddyfile/directives/try_files), которая является shortcut matcher `file` и handler [`rewrite`](/docs/caddyfile/directives/rewrite).

</aside>


При matching становятся доступны четыре новых placeholders:

- `{file_match.relative}` Root-relative path файла. Это часто полезно при rewriting requests.
- `{file_match.absolute}` Absolute path matched file, включая root.
- `{file_match.type}` Type file: `file` или `directory`.
- `{file_match.remainder}` Portion, remaining after splitting file path (если `split_path` configured)


#### Примеры:

Match requests, где path является existing file:

```caddy-d
@file file
```

Match requests, где path followed by `.html` является existing file, или если нет, где path является existing file:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

То же самое, но с one-line shortcut и fallback to emitting 404 error, если file не найден:

```caddy-d
@html-or-error file {path}.html {path} =404
```

Еще несколько examples с [CEL expressions](#expression). Помните, что placeholders preprocessed и converted в regular CEL function calls до interpretation CEL environment, поэтому здесь используется concatenation. Кроме того, long-form must be used при concatenating with placeholders из-за current parsing limitations:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

По request header fields.

- `<field>` — имя HTTP header field для проверки.
	- Если имеет prefix `!`, field must not exist to match (value arg omit).
- `<value>` — value, которое field must have to match. Можно указать one or more.
	- Если имеет prefix `*`, выполняет fast suffix match (appears at the end).
	- Если имеет suffix `*`, выполняет fast prefix match (appears at the start).
	- Если enclosed by `*`, выполняет fast substring match (appears anywhere).
	- Иначе это fast exact match.

Different header fields в одном set AND-ed. Multiple values per field OR'ed.

Обратите внимание, что header fields могут repeat и иметь different values. Backend applications ДОЛЖНЫ учитывать, что header field values являются arrays, а не singular values, и Caddy не interprets meaning в таких quandaries.

#### Пример:

Match requests с header `Connection`, containing `Upgrade`:

```caddy-d
@upgrade header Connection *Upgrade*
```

Match requests с header `Foo`, containing `bar` OR `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Match requests, у которых вообще нет header field `Foo`:

```caddy-d
@not_foo header !Foo
```

С [CEL expression](#expression), match WebSocket requests, проверяя header `Connection`, containing `Upgrade`, и header `Upgrade`, equal `websocket` (в HTTP/2 для этого есть header `:protocol`):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

Как [`header`](#header), но поддерживает regular expressions.

Используемый regular expression language — RE2, included in Go. Смотрите [RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) и [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax).

Начиная с v2.8.0, если `name` *не* provided, name будет taken from named matcher's name. Например, named matcher `@foo` приведет к тому, что этот matcher будет named `foo`. Главное advantage specifying name — если more than one regexp matcher (например, `header_regexp` и [`path_regexp`](#path-regexp), или несколько different header fields) используется в одном named matcher.

Capture groups доступны через [placeholder](/docs/caddyfile/concepts#placeholders) в directives after matching:
- `{re.<name>.<capture_group>}`, где:
  - `<name>` — name regular expression,
  - `<capture_group>` — name или number capture group в expression.

- `{re.<capture_group>}` без name тоже populated for convenience. Caveat: если several regexp matchers используются последовательно, placeholder values будут overwritten by next matcher.

Capture group `0` — full regexp match, `1` — first capture group, `2` — second capture group и так далее. Поэтому `{re.foo.1}` и `{re.1}` оба будут hold value first capture group.

Поддерживается только one regular expression per header field, поскольку regexp patterns cannot be merged; если нужно больше, consider using matcher [`expression`](#expression). Matches against multiple different header fields будут AND'ed.

#### Пример:

Match requests, где Cookie header содержит `login_`, followed by hex string, с capture group, доступной как `{re.login.1}` или `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Это можно simplify, omitted name, который будет inferred from named matcher:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

Или то же самое через [CEL expression](#expression):

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

Matches request по header field `Host` request.

Поскольку большинство site blocks уже указывают hosts в address site, этот matcher чаще используется в site blocks с wildcard hostname (см. [pattern wildcard certificates](/docs/caddyfile/patterns#wildcard-certificates)), где нужна hostname-specific logic.

Несколько matchers `host` будут OR'ed together.

#### Пример:

Matching one subdomain:

```caddy-d
@sub host sub.example.com
```

Matching apex domain и subdomain:

```caddy-d
@site host example.com www.example.com
```

Multiple subdomains через [CEL expression](#expression):

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

По method (verb) HTTP request. Verbs должны быть uppercase, например `POST`. Может match один или many methods.

Несколько matchers `method` будут OR'ed together.

#### Примеры:

Match requests с method `GET`:

```caddy-d
@get method GET
```

Match requests с methods `PUT` или `DELETE`:

```caddy-d
@put-delete method PUT DELETE
```

Match read-only methods через [CEL expression](#expression):

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

```caddy-d
not <matcher>
```

или, чтобы negate multiple matchers, which get AND'ed, откройте block:

```caddy-d
not {
	<matchers...>
}
```

Результаты enclosed matchers будут negated.

#### Примеры:

Match requests с paths, которые НЕ начинаются с `/css/` OR `/js/`.

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

Match requests WITH NEITHER:
- path prefix `/api/`, NOR
- request method `POST`

то есть для match не должно быть ни одного из этих условий:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

Match requests WITHOUT BOTH:
- path prefix `/api/`, AND
- request method `POST`

то есть для match должно отсутствовать оба условия или любое одно из них:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

Для этого matcher нет [CEL expression](#expression), потому что для negation можно использовать operator `!`. Например:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

Что эквивалентно этому, с parentheses:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

По request path (path component request URI). Path matches exact, но case-insensitive. Wildcards `*` можно использовать:

- Только в конце, для prefix match (`/prefix/*`)
- Только в начале, для suffix match (`*.suffix`)
- Только с обеих сторон, для substring match (`*/contains/*`)
- Только в середине, для globular match (`/accounts/*/info`)

Slashes значимы. Например, `/foo*` match `/foo`, `/foobar`, `/foo/` и `/foo/bar`, но `/foo/*` *не* match `/foo` или `/foobar`.

Request paths cleaned для resolve directory traversal dots before matching. Кроме того, multiple slashes merged, если match pattern не содержит multiple slashes. Иными словами, `/foo` match `/foo` и `//foo`, но `//foo` match только `//foo`.

Поскольку у любого URI есть multiple escaped forms, request path normalized (URL-decoded, unescaped), кроме escape sequences на positions, где escape sequences также present in match pattern. Например, `/foo/bar` match both `/foo/bar` и `/foo%2Fbar`, но `/foo%2Fbar` match только `/foo%2Fbar`, потому что escape sequence explicitly given in configuration.

Special wildcard escape `%*` также можно использовать вместо `*`, чтобы leave its matching span escaped. Например, `/bands/*/*` не match `/bands/AC%2FDC/T.N.T`, потому что path сравнивается in normalized space, где выглядит как `/bands/AC/DC/T.N.T`, что не match pattern; однако `/bands/%*/*` match `/bands/AC%2FDC/T.N.T`, потому что span, represented by `%*`, будет compared without decoding escape sequences.

Multiple paths будут OR'ed together.

#### Примеры:

Match multiple directories and their contents:

```caddy-d
@assets path /js/* /css/* /images/*
```

Match specific file:

```caddy-d
@favicon path /favicon.ico
```

Match file extensions:

```caddy-d
@extensions path *.js *.css
```

С [CEL expression](#expression):

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

Как [`path`](#path), но поддерживает regular expressions. Выполняется against URI-decoded/unescaped path.

Используемый regular expression language — RE2, included in Go. Смотрите [RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) и [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax).

Начиная с v2.8.0, если `name` *не* provided, name будет taken from named matcher's name. Например, named matcher `@foo` приведет к тому, что этот matcher будет named `foo`. Главное advantage specifying name — если more than one regexp matcher (например, `path_regexp` и [`header_regexp`](#header-regexp)) используется в одном named matcher.

Capture groups доступны через [placeholder](/docs/caddyfile/concepts#placeholders) в directives after matching:
- `{re.<name>.<capture_group>}`, где:
  - `<name>` — name regular expression,
  - `<capture_group>` — name или number capture group в expression.

- `{re.<capture_group>}` без name тоже populated for convenience. Caveat: если several regexp matchers используются последовательно, placeholder values будут overwritten by next matcher.

Capture group `0` — full regexp match, `1` — first capture group, `2` — second capture group и так далее. Поэтому `{re.foo.1}` и `{re.1}` оба будут hold value first capture group.

В одном named matcher может быть только один pattern `path_regexp`, поскольку этот matcher cannot be merged with itself; если нужно больше, consider using matcher [`expression`](#expression).

#### Пример:

Match requests, где path ends 6-character hex string, followed by `.css` или `.js` as file extension, with capture groups (parts enclosed in `( )`), доступные как `{re.static.1}` и `{re.static.2}` (или `{re.1}` и `{re.2}`), respectively:

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Это можно simplify, omitted name, который будет inferred from named matcher:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

Или то же самое через [CEL expression](#expression), также validating, что [`file`](#file) exists on disk:

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

По request protocol. Можно использовать broad protocol name, например `http`, `https` или `grpc`; или specific/minimum HTTP versions, такие как `http/1.1` или `http/2+`.

В одном named matcher может быть только один matcher `protocol`.

#### Пример:

Match requests, использующие HTTP/2:

```caddy-d
@http2 protocol http/2+
```

С [CEL expression](#expression):

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

По query string parameters. Должна быть sequence `key=value` pairs или empty string "". Keys matched exactly (case-sensitively), но также поддерживают `*` для match any value. Values могут использовать placeholders. Empty string matches HTTP requests with no query parameters.

В одном named matcher может быть несколько `query` matchers, и pairs с same keys будут OR'ed together. Different keys будут AND'ed together. То есть все keys в matcher должны иметь at least one matching value.

Illegal query strings (bad syntax, unescaped semicolons и т. д.) fail to parse и потому не match.

**NOTE:** Query string parameters are arrays, not singular values. Это потому, что repeated keys valid в query strings, и каждый может иметь different value. Этот matcher match key, если любое из configured values assigned в query string. Backend applications, using query strings, ДОЛЖНЫ учитывать, что query string values являются arrays и могут иметь multiple values.

#### Пример:

Match query parameter `q` с any value:

```caddy-d
@search query q=*
```

Match query parameter `sort` со значением `asc` или `desc`:

```caddy-d
@sorted query sort=asc sort=desc
```

Matching both `q` and `sort` через [CEL expression](#expression):

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

По remote IP address (то есть IP address immediate peer или address, set via [PROXY protocol](/docs/caddyfile/options#proxy-protocol)). Принимает exact IPs или CIDR ranges. IPv6 zones поддерживаются.

Как shortcut, `private_ranges` можно использовать, чтобы match все private IPv4 и IPv6 ranges. Это то же самое, что указать все эти ranges: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Если нужно match "real IP" client, parsed from HTTP headers, используйте вместо этого matcher [`client_ip`](#client-ip).

В одном named matcher может быть несколько `remote_ip` matchers, и их ranges будут merged and OR'ed together.

#### Пример:

Match requests from private IPv4 addresses:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Этот matcher часто paired with matcher [`not`](#not), чтобы invert match. Например, чтобы abort all connections from *public* IPv4 и IPv6 addresses (то есть inverse всех private ranges):

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

В [CEL expression](#expression) это выглядело бы так:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

По value variable в request context или value placeholder. Можно указать multiple values, чтобы match any of those possible values (OR'ed).

Argument **&lt;variable&gt;** может быть variable name или placeholder в curly braces `{ }`. (Placeholders не expanded в первом parameter.)

Этот matcher наиболее полезен в паре с directive [`map`](/docs/caddyfile/directives/map), которая sets outputs, с directive [`vars`](/docs/caddyfile/directives/vars) внутри routes, или с plugins, которые set некоторую information в request context.

#### Пример:

Match output directive [`map`](/docs/caddyfile/directives/map) named `magic_number` для values `3` или `5`:

```caddy-d
vars {magic_number} 3 5
```

Match arbitrary placeholder's value, то есть authenticated user's ID, либо `Bob`, либо `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Полный пример с directive [`vars`](/docs/caddyfile/directives/vars), которая set variable, и subsequent matching по ней через matcher [`vars`](#vars). Здесь мы combine два request headers в одну variable и match по этой variable:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

В [CEL expression](#expression) это выглядело бы так:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

Как [`vars`](#vars), но поддерживает regular expressions.

Используемый regular expression language — RE2, included in Go. Смотрите [RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) и [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax).

Начиная с v2.8.0, если `name` *не* provided, name будет taken from named matcher's name. Например, named matcher `@foo` приведет к тому, что этот matcher будет named `foo`. Главное advantage specifying name — если more than one regexp matcher (например, `vars_regexp` и [`header_regexp`](#header-regexp)) используется в одном named matcher.

Capture groups доступны через [placeholder](/docs/caddyfile/concepts#placeholders) в directives after matching:
- `{re.<name>.<capture_group>}`, где:
  - `<name>` — name regular expression,
  - `<capture_group>` — name или number capture group в expression.

- `{re.<capture_group>}` без name тоже populated for convenience. Caveat: если several regexp matchers используются последовательно, placeholder values будут overwritten by next matcher.

Capture group `0` — full regexp match, `1` — first capture group, `2` — second capture group и так далее. Поэтому `{re.foo.1}` и `{re.1}` оба будут hold value first capture group.

Поддерживается только one regular expression per variable name, поскольку regexp patterns cannot be merged; если нужно больше, consider using matcher [`expression`](#expression). Matches against multiple different variables будут AND'ed.

#### Пример:

Match output directive [`map`](/docs/caddyfile/directives/map) named `magic_number` для value, starting with `4`, capturing value in capture group, доступной как `{re.magic.1}` или `{re.1}`:

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Это можно simplify, omitted name, который будет inferred from named matcher:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

В [CEL expression](#expression) это выглядело бы так:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
