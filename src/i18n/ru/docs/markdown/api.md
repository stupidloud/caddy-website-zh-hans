---
title: "API"
---

# API

Caddy настраивается через administration endpoint, доступный по HTTP с помощью [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer) API. Этот endpoint можно [настроить](/docs/json/admin/) в config Caddy.

**Адрес по умолчанию: `localhost:2019`**

Адрес по умолчанию можно изменить, задав переменную окружения `CADDY_ADMIN`. Некоторые способы установки могут задавать другое значение. Адрес в config Caddy всегда имеет приоритет над значением по умолчанию.

<aside class="tip">
	Если вы запускаете на сервере недоверенный код (ужас 😬), обязательно защитите admin endpoint: изолируйте процессы, обновляйте уязвимые программы и настройте endpoint на привязку к permissioned unix socket.
</aside>

Последняя конфигурация будет сохранена на диск после любых изменений (если это не [отключено](/docs/json/admin/config/)). После перезапуска можно возобновить последнюю рабочую config через [`caddy run --resume`](/docs/command-line#caddy-run), что гарантирует долговечность config при отключении питания или похожем событии.

Чтобы начать работу с API, попробуйте наше [руководство по API](/docs/api-tutorial) или, если у вас есть только минута, [краткое руководство по API](/docs/quick-starts/api).

---

- **[POST /load](#post-load)**
  Задает или заменяет активную конфигурацию

- **[POST /stop](#post-stop)**
  Останавливает активную конфигурацию и завершает процесс

- **[GET /config/[path]](#get-configpath)**
  Экспортирует config по указанному path

- **[POST /config/[path]](#post-configpath)**
  Задает или заменяет object; добавляет в array
  
- **[PUT /config/[path]](#put-configpath)**
  Создает новый object; вставляет в array

- **[PATCH /config/[path]](#patch-configpath)**
  Заменяет существующий object или array element

- **[DELETE /config/[path]](#delete-configpath)**
  Удаляет значение по указанному path

- **[Using `@id` in JSON](#using-id-in-json)**
  Позволяет легко проходить внутрь структуры config

- **[Concurrent config changes](#concurrent-config-changes)**
  Помогает избегать collisions при несинхронизированных изменениях config

- **[POST /adapt](#post-adapt)**
  Адаптирует конфигурацию в JSON без запуска

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Возвращает информацию о конкретном CA [PKI app](/docs/json/apps/pki/)

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Возвращает certificate chain конкретного CA [PKI app](/docs/json/apps/pki/)

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Возвращает текущий статус настроенных proxy upstreams


<a id="post-load"></a>
## POST /load

Задает конфигурацию Caddy, переопределяя любую предыдущую конфигурацию. Блокируется до завершения или ошибки reload. Изменения конфигурации легковесны, эффективны и выполняются без простоя. Если новая config по какой-либо причине не сработает, старая config будет возвращена на место без простоя.

Этот endpoint поддерживает разные форматы config с помощью config adapters. Header Content-Type в request указывает формат config, используемый в request body. Обычно это должно быть `application/json`, что представляет собственный формат config Caddy. Для другого формата config укажите соответствующий Content-Type, чтобы значение после прямой косой черты / было именем используемого config adapter. Например, при отправке Caddyfile используйте значение вроде `text/caddyfile`; для JSON 5 — значение вроде `application/json5`; и так далее.

Если новая config совпадает с текущей, reload не произойдет. Чтобы принудительно выполнить reload, задайте `Cache-Control: must-revalidate` в request headers.

<a id="examples"></a>
### Примеры

Задать новую активную конфигурацию:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Примечание: флаг curl `-d` удаляет переносы строк, поэтому если ваш формат config чувствителен к line breaks (например, Caddyfile), используйте вместо него `--data-binary`:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="post-stop"></a>
## POST /stop

Плавно останавливает сервер и завершает процесс. Чтобы остановить только запущенную конфигурацию без завершения процесса, используйте [DELETE /config/](#delete-configpath).

<a id="example"></a>
### Пример

Остановить процесс:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


<a id="get-configpath"></a>
## GET /config/[path]

Экспортирует текущую конфигурацию Caddy по указанному path. Возвращает JSON body.

<a id="examples-1"></a>
### Примеры

Экспортировать весь config и красиво вывести:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

Экспортировать только listener addresses:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



<a id="post-configpath"></a>
## POST /config/[path]

Изменяет конфигурацию Caddy по указанному path на JSON body request. Если destination value является array, POST добавляет; если object — создает или заменяет.

Особый случай: в array можно добавить много элементов, если:

1. path заканчивается на `/...`
2. элемент path перед `/...` ссылается на array
3. payload является array

В этом случае элементы array из payload будут развернуты, и каждый будет добавлен в destination array. В терминах Go это имело бы тот же эффект, что:

```go
baseSlice = append(baseSlice, newElems...)
```

<a id="examples-2"></a>
### Примеры

Добавить listener address:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Добавить несколько listener addresses:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

<a id="put-configpath"></a>
## PUT /config/[path]

Изменяет конфигурацию Caddy по указанному path на JSON body request. Если destination value является position (index) в array, PUT вставляет; если object — строго создает новое значение.

<a id="example-1"></a>
### Пример

Добавить listener address в первый slot:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


<a id="patch-configpath"></a>
## PATCH /config/[path]

Изменяет конфигурацию Caddy по указанному path на JSON body request. PATCH строго заменяет существующее value или array element.

<a id="example-2"></a>
### Пример

Заменить listener addresses:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



<a id="delete-configpath"></a>
## DELETE /config/[path]

Удаляет конфигурацию Caddy по указанному path. DELETE удаляет target value.

<a id="examples-3"></a>
### Примеры

Чтобы выгрузить всю текущую конфигурацию, но оставить процесс запущенным:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Чтобы остановить только один из ваших HTTP servers:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## Использование `@id` в JSON

Можно встраивать IDs в JSON document, чтобы проще получать прямой доступ к этим частям JSON.

Просто добавьте поле `"@id"` в object и задайте ему уникальное имя. Например, если у вас есть handler reverse proxy, к которому нужно часто обращаться:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Чтобы использовать его, просто выполните request к API endpoint `/id/` так же, как к соответствующему endpoint `/config/`, но без всего path. ID сразу переносит request в этот scope config.

Например, чтобы получить доступ к upstreams reverse proxy без ID, path был бы примерно таким:

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

но с ID path становится таким:

```
/id/my_proxy/upstreams
```

что гораздо легче запомнить и написать вручную.

<a id="concurrent-config-changes"></a>
## Concurrent config changes

<aside class="tip">

Этот раздел относится ко всем endpoints `/config/`. Он experimental и может измениться.

</aside>


Config API Caddy предоставляет [ACID guarantees <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) для отдельных requests, но изменения, включающие больше одного request, подвержены collisions или data loss, если они не синхронизированы должным образом.

Например, два clients могут одновременно выполнить `GET /config/foo`, внести правку внутри этого scope (config path), затем одновременно вызвать `POST|PUT|PATCH|DELETE /config/foo/...`, чтобы применить изменения, что приведет к collision: либо один перезапишет другого, либо второй может оставить config в непреднамеренном состоянии, потому что он был применен к другой версии config, чем та, на основе которой готовился. Это происходит потому, что изменения не знают друг о друге.

API Caddy не поддерживает transactions, охватывающие несколько requests, а HTTP — stateless protocol. Однако можно использовать headers `Etag` и `If-Match`, чтобы обнаруживать и предотвращать collisions для любых изменений как форму optimistic concurrency control. Это полезно, если есть шанс, что вы используете endpoints `/config/...` Caddy конкурентно без синхронизации. Все responses на requests `GET /config/...` имеют HTTP header `Etag`, который содержит path и hash содержимого в этом scope (например, `Etag: "/config/apps/http/servers 65760b8e"`). Просто задайте header `If-Match` для mutative request равным header Etag из предыдущего request `GET`.

Базовый алгоритм такой:

1. Выполните request `GET` к любому scope `S` внутри config. Сохраните header `Etag` из response.
2. Внесите нужное изменение в возвращенную config.
3. Выполните request `POST|PUT|PATCH|DELETE` внутри scope `S`, задав request header `If-Match` сохраненным значением `Etag`.
4. Если response — HTTP 412 (Precondition Failed), повторите с шага 1 или откажитесь после слишком большого числа попыток.

Этот алгоритм безопасно позволяет выполнять несколько перекрывающихся изменений конфигурации Caddy без явной синхронизации. Он устроен так, что одновременные изменения разных частей config не требуют retry: только изменения, которые перекрывают один и тот же scope config, могут вызвать collision и потому потребовать retry.


<a id="post-adapt"></a>
## POST /adapt

Адаптирует конфигурацию в Caddy JSON без загрузки или запуска. Если успешно, итоговый JSON document возвращается в response body.

Header Content-Type используется для указания формата конфигурации так же, как работает [/load](#post-load). Например, чтобы адаптировать Caddyfile, задайте `Content-Type: text/caddyfile`.

Этот endpoint адаптирует любой формат конфигурации, если связанный [config adapter](/docs/config-adapters) подключен в вашу сборку Caddy.

<a id="examples-4"></a>
### Примеры

Адаптировать Caddyfile в JSON:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="get-pkicaltidgt"></a>
## GET /pki/ca/&lt;id&gt;

Возвращает информацию о конкретном CA [PKI app](/docs/json/apps/pki/) по его ID. Если запрошенный CA ID является default (`local`), CA будет provisioned, если еще не был. Другие CA IDs вернут error, если они не были previously provisioned.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


<a id="get-pkicaltidgtcertificates"></a>
## GET /pki/ca/&lt;id&gt;/certificates

Возвращает certificate chain конкретного CA [PKI app](/docs/json/apps/pki/) по его ID. Если запрошенный CA ID является default (`local`), CA будет provisioned, если еще не был. Другие CA IDs вернут error, если они не были previously provisioned.

Этот endpoint используется внутренне командой [`caddy trust`](/docs/command-line#caddy-trust), чтобы установить root certificate CA в trust store вашей системы.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

Возвращает текущий статус настроенных reverse proxy upstreams (backends) как JSON document.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Каждая запись в JSON array — это настроенный [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/), сохраненный в global upstream pool.

- **address** — dial address upstream.
- **num_requests** — количество active requests, которые сейчас обрабатывает upstream.
- **fails** — текущее число remembered failed requests, настроенное passive health checks.

Если ваша цель — определить доступность backend, нужно сопоставить релевантные свойства upstream с конфигурацией handler, которую вы используете. Например, если для ваших proxies включены [passive health checks](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/), нужно также учитывать значения `fails` и `num_requests`, чтобы определить, считается ли upstream доступным: проверьте, что число `fails` меньше настроенного максимального числа failures для вашего proxy (то есть [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)), и что `num_requests` меньше или равно настроенному максимальному числу requests на upstream (то есть [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) для всего proxy или [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) для отдельных upstreams).
