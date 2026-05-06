---
title: Директивы Caddyfile
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

<a id="caddyfile-directives"></a>
# Директивы Caddyfile

Directives — это функциональные keywords, которые находятся внутри site [blocks](/docs/caddyfile/concepts#blocks). Иногда они могут открывать собственные blocks, содержащие *subdirectives*, но directives **нельзя** использовать внутри других directives, если это не указано явно. Например, нельзя использовать `basic_auth` внутри block `file_server`, потому что `file_server` не знает, как выполнять authentication. Однако некоторые directives *можно* использовать внутри специальных directive blocks, таких как `handle` и `route`, потому что они специально designed для группировки HTTP handler directives.

- [Синтаксис](#syntax)
- [Порядок директив](#directive-order)
- [Алгоритм сортировки](#sorting-algorithm)

Следующие directives входят в стандартную поставку Caddy и могут использоваться в HTTP Caddyfile:

<div id="directive-table">

Directive | Description
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Прерывает HTTP request
**[acme_server](/docs/caddyfile/directives/acme_server)** | Встроенный ACME server
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Принудительно применяет HTTP Basic Authentication
**[bind](/docs/caddyfile/directives/bind)** | Настраивает socket address server
**[encode](/docs/caddyfile/directives/encode)** | Encodes (обычно compresses) responses
**[error](/docs/caddyfile/directives/error)** | Trigger error
**[file_server](/docs/caddyfile/directives/file_server)** | Обслуживает files from disk
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Делегирует authentication внешнему service
**[fs](/docs/caddyfile/directives/fs)** | Задает file system для file I/O
**[handle](/docs/caddyfile/directives/handle)** | Mutually-exclusive group directives
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Определяет routes для обработки errors
**[handle_path](/docs/caddyfile/directives/handle_path)** | Как handle, но strips path prefix
**[header](/docs/caddyfile/directives/header)** | Sets или removes response headers
**[import](/docs/caddyfile/directives/import)** | Include snippets или files
**[intercept](/docs/caddyfile/directives/intercept)** | Intercept responses, written by other handlers
**[invoke](/docs/caddyfile/directives/invoke)** | Invoke named route
**[log](/docs/caddyfile/directives/log)** | Включает access/request logging
**[log_append](/docs/caddyfile/directives/log_append)** | Append field в access log
**[log_skip](/docs/caddyfile/directives/log_skip)** | Skip access logging для matched requests
**[log_name](/docs/caddyfile/directives/log_name)** | Override logger name(s), куда писать
**[map](/docs/caddyfile/directives/map)** | Maps input value к одному или нескольким outputs
**[method](/docs/caddyfile/directives/method)** | Внутренне изменяет HTTP method
**[metrics](/docs/caddyfile/directives/metrics)** | Настраивает Prometheus metrics exposition endpoint
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Обслуживает PHP sites через FastCGI
**[push](/docs/caddyfile/directives/push)** | Push content to client через HTTP/2 server push
**[redir](/docs/caddyfile/directives/redir)** | Выдает HTTP redirect клиенту
**[request_body](/docs/caddyfile/directives/request_body)** | Manipulates request body
**[request_header](/docs/caddyfile/directives/request_header)** | Manipulates request headers
**[respond](/docs/caddyfile/directives/respond)** | Writes hard-coded response to client
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Мощный и расширяемый reverse proxy
**[rewrite](/docs/caddyfile/directives/rewrite)** | Внутренне rewrites request
**[root](/docs/caddyfile/directives/root)** | Задает path к site root
**[route](/docs/caddyfile/directives/route)** | Group directives, treated literally as single unit
**[templates](/docs/caddyfile/directives/templates)** | Execute templates on response
**[tls](/docs/caddyfile/directives/tls)** | Настраивает TLS settings
**[tracing](/docs/caddyfile/directives/tracing)** | Integration with OpenTelemetry tracing
**[try_files](/docs/caddyfile/directives/try_files)** | Rewrite, зависящий от file existence
**[uri](/docs/caddyfile/directives/uri)** | Manipulate URI
**[vars](/docs/caddyfile/directives/vars)** | Задает arbitrary variables

</div>

<a id="syntax"></a>
## Синтаксис

Синтаксис каждой directive будет выглядеть примерно так:

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

`<carets>` обозначают tokens, которые заменяются actual values.

`[brackets]` обозначают optional parameters.

Многоточие `...` обозначает continuation, то есть один или несколько parameters или lines.

Subdirectives обычно optional, если не documented otherwise, даже если они не указаны в `[brackets]`.


<a id="matchers"></a>
### Matchers

Большинство, но не все directives принимают [matcher tokens](/docs/caddyfile/matchers#syntax), которые позволяют filter requests. Matcher tokens обычно optional. Directives поддерживают matchers, если в syntax directive вы видите:

```caddy-d
[<matcher>]
```

Поскольку matcher tokens работают одинаково, разные possibilities для matcher token не описываются на каждой странице, чтобы reduce duplication. Вместо этого смотрите [документацию matchers](/docs/caddyfile/matchers) для подробного объяснения syntax.


<a id="directive-order"></a>
## Порядок директив

Многие directives manipulate HTTP handler chain. Порядок, в котором эти directives evaluated, важен, поэтому default ordering hard-coded в Caddy.

Этот ordering можно override/customize с помощью [global option `order`](/docs/caddyfile/options#order) или directive [`route`](/docs/caddyfile/directives/route).

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # only in reverse_proxy's handle_response block
request_body

redir

# incoming request manipulation
method
rewrite
uri
try_files

# middleware handlers; some wrap responses
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# special routing & dispatching directives
invoke
handle
handle_path
route

# handlers that typically respond to requests
abort
error
copy_response # only in reverse_proxy's handle_response block
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## Алгоритм сортировки

Для удобства использования Caddyfile adapter сортирует directives по следующим rules:

- Directives с разными names сортируются по их position в [default order](#directive-order). Default order можно override через [global option `order`](/docs/caddyfile/options). Directives из plugins *не* имеют order, поэтому для задания order следует использовать global option [`order`](/docs/caddyfile/options) или directive [`route`](/docs/caddyfile/directives/route).

- Directives с одинаковыми names сортируются по их [matchers](/docs/caddyfile/matchers#syntax).

  - Highest priority имеет directive с single [path matcher](/docs/caddyfile/matchers#path-matchers).

    Path matchers сортируются по specificity, от most specific к least specific.
	
	В общем случае это выполняется сортировкой по length path matcher. Есть одно exception: если path заканчивается на `*`, а paths двух matchers в остальном одинаковы, matcher без `*` считается more specific и сортируется выше.

    Например:
    - `/foobar` more specific, чем `/foo`
    - `/foo` more specific, чем `/foo*`
    - `/foo/*` more specific, чем `/foo*`

  - Directive с любым другим matcher сортируется next, в порядке появления в Caddyfile.

    Сюда входят path matchers с multiple values и [named matchers](/docs/caddyfile/matchers#named-matchers).

  - Directive без matcher (то есть matching all requests) сортируется last.

- Directive [`vars`](/docs/caddyfile/directives/vars) имеет reversed ordering by matcher, потому что она sets values, которые могут overwrite друг друга, поэтому most specific matcher должен evaluated last.

- Содержимое directive [`route`](/docs/caddyfile/directives/route) ignores все rules выше и сохраняет order directives внутри.
