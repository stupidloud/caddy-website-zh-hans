---
title: Как работает logging
---

Как работает logging
=================

У Caddy мощные и гибкие logging facilities, но они могут отличаться от привычных, особенно если вы пришли из более архаичного shared hosting или других legacy web servers.


<a id="overview"></a>
## Обзор

У logging есть два основных аспекта: emission и consumption.

**Emission** означает создание сообщений. Она состоит из трех шагов:

1. Сбор релевантной информации (context)
2. Построение полезного representation (encoding)
3. Отправка этого representation в output (writing)

Эта функциональность встроена в core Caddy, позволяя любой части code base Caddy или modules (plugins) emit logs.

**Consumption** — прием и обработка сообщений. Чтобы быть полезными, emitted logs должны быть consumed. Logs, которые просто записываются, но никогда не читаются, не имеют ценности. Consuming logs может быть таким простым, как чтение console output администратором, или таким advanced, как подключение log aggregation tool или cloud service для filtering, counting и indexing log messages.

<a id="caddys-role"></a>
### Роль Caddy

*Caddy — log emitter*. Он не consume logs, кроме минимальной обработки, необходимой для encoding и writing logs. Это важно, потому что core Caddy остается проще, что ведет к меньшему числу bugs и edge cases, а также снижает maintenance burden. В конечном счете log processing находится вне scope Caddy core.

Однако всегда есть возможность для Caddy app module, который consume logs. (Насколько нам известно, такого пока просто нет.)


<a id="structured-logs"></a>
## Structured logs

Как и у большинства современных applications, logs Caddy являются *structured*. Это означает, что информация в message — не просто opaque string или byte slice. Вместо этого data остается strongly typed и индексируется отдельными *field names* до момента encoding message и записи наружу.

Сравните traditional unstructured logs&mdash;например, архаичный Common Log Format (CLF)&mdash;обычно используемый traditional HTTP servers:

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Этот format "имеет structure", но не является "structured": его можно использовать только для logging HTTP requests. Нет (эффективного) способа encode его иначе, потому что это opaque string bytes. В нем также отсутствует много информации. Он даже не включает Host header запроса! Такой log format полезен только при hosting одного site и для получения самых базовых сведений о requests.

<aside class="tip">
	Отсутствие host information в CLF — причина, по которой такие logs обычно нужно писать в отдельные files при hosting более одного site: иначе невозможно узнать Host header из request!
</aside>

Теперь сравните эквивалентное structured log message из Caddy, encoded как JSON и красиво formatted для отображения:

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Видно, что structured log намного полезнее и содержит значительно больше информации. Обилие информации в этом log message не только полезно, но и практически не имеет performance overhead: logs Caddy zero-allocation. Structured logs не имеют ограничений по data types или context: их можно использовать в любом code path и включать любую информацию.

Поскольку logs structured и strongly-typed, их можно encode в любой format. Поэтому если вы не хотите работать с JSON, logs можно encode в любое другое representation. Caddy поддерживает другие варианты через [log encoder modules](/docs/json/logging/logs/encoder/), и можно добавить еще больше.

**Самое важное** в различии между structured logs и legacy formats: с performance penalty structured log [можно преобразовать в legacy Common Log Format <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), но не наоборот. Переход от CLF к structured formats нетривиален (или как минимум неэффективен) и невозможен с учетом отсутствующей информации.

По сути, эффективный structured logging обычно продвигает такие принципы:

- Слишком много logs лучше, чем слишком мало
- Filtering лучше, чем discarding
- Отложенный encoding дает большую flexibility и interoperability
 

<a id="emission"></a>
## Emission

В code emission log выглядит примерно так:

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Это реальная строка code из reverse proxy Caddy. Эта строка позволяет inspecting requests к настроенным upstreams при включенном debug logging. Это бесценные data при troubleshooting!
</aside>

Видно, что один function call содержит log level, message и несколько fields data. Все они strongly-typed, и Caddy использует zero-allocation logging library, поэтому log emissions быстрые и эффективные почти без overhead.

Variable `logger` — это `zap.Logger`, у которого может быть любой объем context, включая name и fields data. Это позволяет loggers красиво "inherit" из parent contexts, enabling advanced tracing и metrics.

Оттуда message отправляется через высокоэффективный processing pipeline, где он encoded и written.


<a id="logging-pipeline"></a>
## Logging pipeline

Как показано выше, messages emitted **loggers**. Затем messages отправляются в **logs** для processing.

Caddy позволяет [настраивать multiple logs](/docs/json/logging/logs/), которые могут process messages. Log состоит из encoder, writer, minimum level, sampling ratio и list loggers для include или exclude. В Caddy всегда есть default log с именем `default`. Его можно customize, указав log с key `"default"` в [этом object](/docs/json/logging/logs/) в config.

<aside class="tip">

Сейчас хороший момент [изучить docs Caddy по logging](/docs/json/logging/), чтобы познакомиться со structure и parameters, о которых идет речь.

</aside>


- **Encoder:** Format log. Преобразует in-memory data representation в byte slice. Encoders имеют доступ ко всем fields log message.
- **Writer:** Output log. Может быть любым log writer module, например file или network socket. Он просто writes bytes.
- **Level:** Logs имеют разные levels, от DEBUG до FATAL. Messages ниже указанного level игнорируются этим log.
- **Sampling:** Очень hot paths могут emit больше logs, чем можно эффективно process; enabling sampling снижает load, сохраняя representative sample messages.
- **Include/exclude:** Каждое message emitted logger, у которого есть name (обычно derived from module ID). Logs могут include или exclude messages от определенных loggers.

Когда log message emitted из Caddy:

- Name исходного logger проверяется по include/exclude list каждого log; если included (или not excluded), оно допускается в этот log.
- Если sampling включен, быстрый расчет определяет, сохранять ли log message.
- Message encoded с использованием настроенного encoder log.
- Encoded bytes затем written в настроенный writer log.

По умолчанию все messages идут во все настроенные logs. Это соответствует values structured logging, описанным выше. Можно ограничить, какие messages идут в какие logs, задав их include/exclude lists, но это в основном для filtering messages из разных modules; это не предназначено для использования как log aggregation service. Чтобы logging pipeline Caddy оставался streamlined и efficient, advanced processing log messages откладывается на consumption.

<a id="consumption"></a>
## Consumption

После отправки messages в output consumer прочитает их, parse и обработает соответственно.

Это совсем другая problem domain, чем emitting logs, и core Caddy не занимается consumption (хотя Caddy app module, безусловно, мог бы). Существует множество tools для processing streams JSON messages (или других formats) и viewing, filtering, indexing и querying logs. Можно даже написать или реализовать собственный.

Например, если вы запускаете legacy software, которому нужен CLF, разделенный по разным files на основе конкретного field (например, hostname), можно использовать или написать простой tool, который reads JSON, вызывает `sprintf()` для создания CLF string, затем writes его в file на основе value в field `request.host`.

Logging facilities Caddy также можно использовать для реализации metrics и tracing: metrics в основном count messages с определенными characteristics, а tracing links multiple messages на основе commonalities between them.

Есть бесчисленные possibilities того, что можно сделать, consuming logs Caddy!
