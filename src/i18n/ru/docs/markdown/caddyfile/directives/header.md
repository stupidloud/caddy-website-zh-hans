---
title: header (директива Caddyfile)
---

# header

Управляет полями HTTP response header. Может устанавливать, добавлять и удалять значения header, а также выполнять замены с помощью regular expressions.

По умолчанию операции с header выполняются немедленно, если только какие-либо headers не удаляются (prefix `-`) или не задается значение по умолчанию (prefix `?`). В этих случаях операции с header автоматически откладываются до момента записи клиенту.

Для управления HTTP request headers можно использовать директиву [`request_header`](request_header).


<a id="syntax"></a>
## Синтаксис

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# Add
	+<field> <value>

	# Set
	<field> <value>

	# Set with defer
	><field> <value>

	# Delete
	-<field>

	# Replace
	<field> <find> <replace>

	# Replace with defer
	><field> <find> <replace>

	# Default
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** — имя поля header.

  Без prefix поле устанавливается (перезаписывается).

  Prefix `+` добавляет поле вместо перезаписи (установки), если поле уже существует; поля header могут встречаться в ответе более одного раза.

  Prefix `-` удаляет поле. Поле может использовать wildcards `*` в prefix или suffix, чтобы удалить все совпадающие поля.

  Prefix `?` задает значение по умолчанию для поля. Поле записывается только если оно еще не существует.

  Prefix `>` задает поле и включает `defer` как сокращение.

- **&lt;value&gt;** — значение поля header при добавлении или установке поля.

- **&lt;find&gt;** — regular expression для поиска. Placeholders можно использовать как динамический ввод в search pattern. Используется язык regular expressions RE2, включенный в Go. См. [справочник по синтаксису RE2](https://github.com/google/re2/wiki/Syntax) и [обзор синтаксиса regexp в Go](https://pkg.go.dev/regexp/syntax).

- **&lt;replace&gt;** — replacement value; обязателен при выполнении search-and-replace. Используйте `$1`, `$2` и т. д., чтобы ссылаться на capture groups из search pattern. Если replacement value равно `""`, совпавший текст удаляется из значения. Подробности см. в [документации Go](https://golang.org/pkg/regexp/#Regexp.Expand).

- **defer** откладывает выполнение операций с header до момента отправки ответа клиенту. Эта опция автоматически включается при следующих условиях:
	- Когда какие-либо поля header удаляются с помощью `-`.
	- Когда значение по умолчанию задается с помощью `?`.
	- Когда prefix `>` используется в операции set или replace.
	- Когда присутствует одно или несколько условий `match`.

- **match** <span id="match"/> — inline [response matcher](/docs/caddyfile/response-matchers). Операции с header применяются только к ответам, которые удовлетворяют указанным условиям.

Для нескольких изменений header можно открыть блок и указать по одной операции в строке тем же способом.

При использовании prefix `?` для задания header value по умолчанию он автоматически выделяется в собственный handler `header`, если находился в блоке `header` с несколькими операциями header. [Под капотом](/docs/modules/http.handlers.headers#response/require) использование `?` настраивает [response matcher](/docs/caddyfile/response-matchers), который применяется ко всему handler директивы и применяет операции header (как `defer`) только если поле еще не установлено.


<a id="examples"></a>
## Примеры

Установить пользовательское поле header для всех ответов:

```caddy-d
header Custom-Header "My value"
```

Удалить поле header "Hidden":

```caddy-d
header -Hidden
```

Заменить `http://` на `https://` в любом header Location:

```caddy-d
header Location http:// https://
```

Установить security и privacy headers на всех страницах: (**WARNING:** используйте только если понимаете последствия!)

```caddy-d
header {
	# отключить FLoC tracking
	Permissions-Policy interest-cohort=()

	# включить HSTS
	Strict-Transport-Security max-age=31536000;

	# запретить clients определять media type по содержимому
	X-Content-Type-Options nosniff

	# защита от clickjacking
	X-Frame-Options DENY
}
```

Несколько директив header, которые должны быть взаимно исключающими:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Установить cache expiration по умолчанию, если upstream не определяет свой:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Пометить все успешные ответы на GET requests как кешируемые на срок до одного часа:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Предотвратить кеширование error responses при исключении на upstream server:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Пометить ответы light mode как кешируемые отдельно от ответов dark mode, если upstream server поддерживает client hints:
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Предотвратить чрезмерно разрешающие CORS headers, заменив wildcard values конкретным доменом:
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**Примечание**: в операциях replacement значение `<find>` интерпретируется как regular expression. Чтобы сопоставить символ `*`, его нужно экранировать обратной косой чертой, как показано в примере выше.

Альтернативно можно использовать [response matcher](/docs/caddyfile/response-matchers), чтобы сопоставить значение header буквально:
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Чтобы переопределить cache expiration, установленный proxy upstream, для paths, начинающихся с `/no-cache`; включение `defer` необходимо, чтобы гарантировать установку header *после* того, как proxy запишет свои headers:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Чтобы выполнить отложенное обновление header `Set-Cookie` и добавить `SameSite=None`; regexp capture используется, чтобы взять существующее значение, а `$1` повторно вставляет его в начало с добавленной опцией:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
