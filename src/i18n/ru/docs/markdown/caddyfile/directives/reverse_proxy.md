---
title: reverse_proxy (директива Caddyfile)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

Проксирует запросы к одному или нескольким backend с настраиваемым transport, балансировкой нагрузки, проверками работоспособности, изменением запросов и опциями буферизации.

- [Синтаксис](#syntax)
- [Upstream](#upstreams)
  - [Адреса upstream](#upstream-addresses)
  - [Динамические upstream](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Балансировка нагрузки](#load-balancing)
  - [Активные проверки работоспособности](#active-health-checks)
  - [Пассивные проверки работоспособности](#passive-health-checks)
  - [События](#events)
- [Streaming](#streaming)
- [Headers](#headers)
- [Rewrites](#rewrites)
- [Transports](#transports)
  - [Transport `http`](#the-http-transport)
  - [Transport `fastcgi`](#the-fastcgi-transport)
- [Перехват ответов](#intercepting-responses)
- [Примеры](#examples)



<a id="syntax"></a>
## Синтаксис

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# load balancing
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# active health checking
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive health checking
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# request/header manipulation
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# optionally intercept responses from upstream
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# special directives only available in handle_response
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



<a id="upstreams"></a>
## Upstream

- **&lt;upstreams...&gt;** — список upstream (backend), к которым нужно проксировать.
- **to** <span id="to"/> — альтернативный способ указать список upstream, по одному или нескольким на строку.
- **dynamic** <span id="dynamic"/> настраивает модуль *dynamic upstreams*. Это позволяет получать список upstream динамически для каждого запроса. Описание стандартных модулей dynamic upstream см. в разделе [динамические upstream](#dynamic-upstreams) ниже. Dynamic upstream извлекаются на каждой итерации цикла proxy, то есть потенциально несколько раз за запрос, если включены retry балансировки нагрузки, и имеют приоритет над статическими upstream. Если возникает ошибка, proxy возвращается к использованию любых статически настроенных upstream.


<a id="upstream-addresses"></a>
### Адреса upstream

Статические адреса upstream могут быть URL, содержащим только схему и host/port, или обычным [сетевым адресом Caddy](/docs/conventions#network-addresses). Допустимые примеры:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

По умолчанию подключения к upstream выполняются по незашифрованному HTTP. При использовании формы URL схема может служить сокращением для задания некоторых значений по умолчанию [`transport`](#transports).
- Схема `https://` использует [`http` transport](#the-http-transport) с включенным [`tls`](#tls).

  Дополнительно может понадобиться переопределить заголовок `Host`, чтобы он совпадал со значением TLS SNI, которое серверы используют для маршрутизации и выбора сертификата. Подробности см. в разделе [HTTPS](#https) ниже.

- Схема `h2c://` использует [`http` transport](#the-http-transport), где [версии HTTP](#versions) настроены так, чтобы разрешить cleartext-подключения HTTP/2.

- Схема `http://` идентична отсутствию схемы, поскольку HTTP уже используется по умолчанию. Этот синтаксис включен для симметрии с другими сокращениями схем.

Схемы нельзя смешивать, поскольку они изменяют общую конфигурацию transport: transport с TLS не может одновременно переносить HTTPS и незашифрованный HTTP. Любая явно заданная конфигурация transport не будет перезаписана, а отсутствие схемы или использование других портов не предполагает конкретный transport.

При использовании IPv6 с зоной, например link-local адресов с конкретным сетевым интерфейсом, схему **нельзя** использовать как сокращение, потому что `%` приведет к ошибке разбора URL; вместо этого настройте transport явно.

При использовании формы [сетевого адреса](/docs/conventions#network-addresses) тип сети задается как префикс адреса upstream. Это нельзя сочетать со схемой URL. В качестве особого случая `unix+h2c/` поддерживается как сокращение для сети `unix/` плюс те же эффекты, что у схемы `h2c://`. Диапазоны портов поддерживаются как сокращение, которое разворачивается в несколько upstream с тем же host.

Адреса upstream **не могут** содержать пути или query-строки, поскольку это означало бы одновременное переписывание запроса во время проксирования, а такое поведение не определено и не поддерживается. Если это нужно, используйте директиву [`rewrite`](/docs/caddyfile/directives/rewrite).

Если адрес не является URL, то есть не имеет схемы, можно использовать [placeholder](/docs/caddyfile/concepts#placeholders), но это делает upstream *динамически статическим*: потенциально много разных backend действуют как один статический upstream с точки зрения health checks и балансировки нагрузки. По возможности рекомендуем вместо этого использовать модуль [dynamic upstreams](#dynamic-upstreams). При использовании placeholder порт **обязательно** должен быть включен: либо через замену placeholder, либо как статический суффикс адреса.


<a id="dynamic-upstreams"></a>
### Динамические upstream

Reverse proxy Caddy поставляется со стандартными модулями dynamic upstream. Обратите внимание, что использование dynamic upstream влияет на балансировку нагрузки и health checks в зависимости от конкретной конфигурации policy: активные health checks не выполняются для dynamic upstream; а балансировка нагрузки и пассивные health checks работают лучше, если список upstream относительно стабилен и согласован, особенно с round-robin. В идеале модули dynamic upstream должны возвращать только здоровые, пригодные backend.


<a id="srv"></a>
#### SRV

Получает upstream из DNS-записей SRV.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** — полное доменное имя записи для поиска, то есть `_service._proto.name`.
- **service** — компонент service полного имени.
- **proto** — компонент protocol полного имени. Либо `tcp`, либо `udp`.
- **name** — компонент name. Либо, если `service` и `proto` пустые, полное доменное имя для запроса.
- **refresh** — как часто обновлять кэшированные результаты. По умолчанию: `1m`
- **resolvers** — список DNS resolvers, переопределяющий системные resolvers.
- **dial_timeout** — timeout для подключения при запросе.
- **dial_fallback_delay** — как долго ждать перед запуском соединения RFC 6555 Fast Fallback. По умолчанию: `300ms`



<a id="aaaaa"></a>
#### A/AAAA

Получает upstream из DNS-записей A/AAAA.

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** — доменное имя для запроса.
- **port** — порт, используемый для backend.
- **refresh** — как часто обновлять кэшированные результаты. По умолчанию: `1m`
- **resolvers** — список DNS resolvers, переопределяющий системные resolvers.
- **dial_timeout** — timeout для подключения при запросе.
- **dial_fallback_delay** — как долго ждать перед запуском соединения RFC 6555 Fast Fallback. По умолчанию: `300ms`
- **versions** — список версий IP для разрешения. По умолчанию: `ipv4 ipv6`, что соответствует записям A и AAAA соответственно.


<a id="multi"></a>
#### Multi

Добавляет результаты нескольких модулей dynamic upstream. Полезно, если нужны резервные источники upstream, например основной кластер SRV, подкрепленный вторичным кластером SRV.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** — имя модуля dynamic upstream, за которым следует его конфигурация. Можно указать больше одного.




<a id="load-balancing"></a>
## Балансировка нагрузки

Балансировка нагрузки обычно используется для распределения трафика между несколькими upstream. При включении retry ее также можно использовать с одним или несколькими upstream, чтобы удерживать запросы до выбора здорового upstream, например чтобы переждать и снизить число ошибок при перезагрузке или redeploy upstream.

Она включена по умолчанию с policy `random`. Retry по умолчанию отключены.

- **lb_policy** <span id="lb_policy"/> — имя policy балансировки нагрузки вместе с опциями. По умолчанию: `random`.

  Для policy, связанных с хэшированием, используется алгоритм [highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing), чтобы клиент или запрос с одним и тем же ключом хэша сопоставлялся с тем же upstream, даже если список upstream меняется.

  Некоторые policy поддерживают fallback как опцию, если это отмечено; в таком случае они принимают [блок](/docs/caddyfile/concepts#blocks) с `fallback <policy>`, где указывается другая policy балансировки нагрузки. Для таких policy fallback по умолчанию — `random`. Настройка fallback позволяет использовать вторичную policy, если основная ничего не выбрала, что дает мощные комбинации. При необходимости fallback можно вкладывать несколько раз.
  
  Например, `header` можно использовать как основную policy, чтобы разработчики могли выбирать конкретный upstream, с fallback `first` для всех остальных соединений, реализуя primary/secondary failover.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` случайно выбирает upstream

	- `random_choose <n>` случайно выбирает два или более upstream, затем выбирает один с наименьшей нагрузкой (`n` обычно равно 2)

	- `first` выбирает первый доступный upstream в порядке их определения в конфигурации, позволяя реализовать primary/secondary failover; не забудьте включить health checks вместе с этим, иначе failover не произойдет

	- `round_robin` последовательно перебирает каждый upstream

	- `weighted_round_robin <weights...>` последовательно перебирает каждый upstream с учетом заданных весов. Количество аргументов веса должно совпадать с количеством настроенных upstream. Веса должны быть неотрицательными целыми числами. Например, при двух upstream и весах `5 1` первый upstream будет выбран 5 раз подряд, прежде чем второй upstream будет выбран один раз; затем цикл повторится. Если в качестве веса используется ноль, это отключит выбор upstream для новых запросов.

	- `least_conn` выбирает upstream с наименьшим числом текущих запросов; если несколько host имеют одинаково минимальное число запросов, один из них выбирается случайно

	- `ip_hash` сопоставляет удаленный IP, то есть непосредственный peer, с sticky upstream

	- `client_ip_hash` сопоставляет IP клиента со sticky upstream; лучше всего сочетать это с [глобальной опцией `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies), которая включает разбор реального IP клиента, иначе поведение такое же, как у `ip_hash`

	- `uri_hash` сопоставляет URI запроса (path и query) со sticky upstream

	- `query [key]` сопоставляет query запроса со sticky upstream, хэшируя значение query; если указанный ключ отсутствует, для выбора upstream используется fallback policy (`random` по умолчанию)

	- `header [field]` сопоставляет заголовок запроса со sticky upstream, хэшируя значение заголовка; если указанное поле заголовка отсутствует, для выбора upstream используется fallback policy (`random` по умолчанию)

	- `cookie [<name> [<secret>]]` при первом запросе от клиента, когда cookie нет, для выбора upstream используется fallback policy (`random` по умолчанию), а в ответ добавляется заголовок `Set-Cookie` (имя cookie по умолчанию — `lb`, если не указано). Значение cookie — dial-адрес выбранного upstream, хэшированный с HMAC-SHA256 с использованием `<secret>` как общего секрета, либо пустой строки, если он не указан.
	
	  При последующих запросах, где cookie присутствует, значение cookie будет сопоставлено с тем же upstream, если он доступен; если он недоступен или не найден, новая upstream выбирается fallback policy, а cookie добавляется в ответ.

	  Если вы хотите использовать конкретный upstream для отладки, можно хэшировать адрес upstream с секретом и установить cookie в HTTP-клиенте, например в браузере. Например, с PHP можно выполнить следующее, чтобы вычислить значение cookie, где `10.1.0.10:8080` — адрес одного из upstream, а `secret` — настроенный секрет.
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  Можно установить cookie в браузере через Javascript-консоль, например чтобы установить cookie с именем `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> — сколько раз повторять выбор доступных backend для каждого запроса, если следующий доступный host недоступен. По умолчанию retry отключены (ноль).

  Если также настроен [`lb_try_duration`](#lb_try_duration), retry могут завершиться раньше при достижении длительности. Иными словами, длительность retry имеет приоритет над количеством retry.

- **lb_try_duration** <span id="lb_try_duration"/> — [значение длительности](/docs/conventions#durations), определяющее, как долго пытаться выбирать доступные backend для каждого запроса, если следующий доступный host недоступен. По умолчанию retry отключены (нулевая длительность).

  Клиенты будут ждать до этого времени, пока балансировщик нагрузки пытается найти доступный upstream host. Разумная начальная точка — `5s`, поскольку timeout подключения HTTP transport по умолчанию равен `3s`, и это должно позволить как минимум один retry, если первый выбранный upstream недоступен; но можно экспериментировать, чтобы найти баланс для вашего случая.

- **lb_try_interval** <span id="lb_try_interval"/> — [значение длительности](/docs/conventions#durations), определяющее, как долго ждать между выборами следующего host из пула. По умолчанию `250ms`. Имеет значение только когда запрос к upstream host завершается ошибкой. Учтите, что установка этого значения в `0` при ненулевом `lb_try_duration` может привести к busy loop CPU, если все backend недоступны, а latency очень мала.

- **lb_retry_match** <span id="lb_retry_match"/> ограничивает, для каких запросов разрешены retry. Запрос должен соответствовать этому условию, чтобы его можно было повторить, если подключение к upstream успешно установилось, но последующий round-trip завершился ошибкой. Если подключение к upstream не удалось, retry всегда разрешен. По умолчанию повторяются только запросы `GET`.

  Синтаксис этой опции такой же, как у [именованных request matcher](/docs/caddyfile/matchers#named-matchers), но без `@name`. Если нужен только один matcher, его можно настроить в той же строке. Для нескольких matcher требуется блок.



<a id="active-health-checks"></a>
### Активные проверки работоспособности

Активные health checks выполняют проверку работоспособности в фоне по таймеру. Чтобы включить их, требуется `health_uri` или `health_port`.

- **health_uri** <span id="health_uri"/> — URI path и необязательный query для активных health checks.

- **health_upstream** <span id="health_upstream"/> — ip:port, используемый для активных health checks, если он отличается от upstream. Его следует использовать вместе с `health_header` и `{http.reverse_proxy.active.target_upstream}`.

- **health_port** <span id="health_port"/> — порт для активных health checks, если он отличается от порта upstream. Игнорируется, если используется `health_upstream`.

- **health_interval** <span id="health_interval"/> — [значение длительности](/docs/conventions#durations), определяющее, как часто выполнять активные health checks. По умолчанию: `30s`.

- **health_passes** <span id="health_passes"/> — число последовательных успешных health checks, необходимых перед тем, как backend снова будет помечен здоровым. По умолчанию: `1`.

- **health_fails** <span id="health_fails"/> — число последовательных неуспешных health checks, необходимых перед тем, как backend будет помечен нездоровым. По умолчанию: `1`.

- **health_timeout** <span id="health_timeout"/> — [значение длительности](/docs/conventions#durations), определяющее, как долго ждать ответа перед тем, как пометить backend недоступным. По умолчанию: `5s`.

- **health_method** <span id="health_method"/> — HTTP-метод для активной health check. По умолчанию: `GET`.

- **health_status** <span id="health_status"/> — HTTP status code, ожидаемый от здорового backend. Может быть трехзначным status code или классом status code, заканчивающимся на `xx`. Например: `200` (по умолчанию) или `2xx`.

- **health_request_body** <span id="health_request_body"/> — строка, представляющая тело запроса, отправляемое с активной health check.

- **health_body** <span id="health_body"/> — substring или регулярное выражение для сопоставления с телом ответа активной health check. Если backend не возвращает совпадающее тело, он будет помечен как недоступный.

- **health_follow_redirects** <span id="health_follow_redirects"/> заставляет health check следовать redirects, предоставленным upstream. По умолчанию ответ redirect считается ошибкой health check.

- **health_headers** <span id="health_headers"/> позволяет указать headers для активных health check запросов. Это полезно, если нужно изменить заголовок `Host` или предоставить аутентификацию backend как часть health checks.



<a id="passive-health-checks"></a>
### Пассивные проверки работоспособности

Пассивные health checks происходят inline с реальными проксируемыми запросами. Чтобы включить их, требуется `fail_duration`.

- **fail_duration** <span id="fail_duration"/>  — [значение длительности](/docs/conventions#durations), определяющее, как долго помнить неуспешный запрос. Длительность > `0` включает пассивные health checks; по умолчанию `0` (отключено). Разумная начальная точка — `30s`, чтобы сбалансировать частоту ошибок и скорость возврата нездорового upstream в работу; но можно экспериментировать, чтобы найти баланс для вашего случая.

- **max_fails** <span id="max_fails"/> — максимальное число неуспешных запросов в пределах `fail_duration`, необходимое перед тем, как считать backend недоступным; должно быть >= `1`; по умолчанию `1`.

- **unhealthy_status** <span id="unhealthy_status"/> считает запрос неуспешным, если ответ возвращается с одним из этих status code. Может быть трехзначным status code или классом status code, заканчивающимся на `xx`, например `404` или `5xx`.

- **unhealthy_latency** <span id="unhealthy_latency"/> — [значение длительности](/docs/conventions#durations), при превышении которого запрос считается неуспешным.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> — допустимое число одновременных запросов к backend перед тем, как пометить его недоступным. Иными словами, если конкретный backend уже обрабатывает столько запросов, он считается "перегруженным", и предпочтение будет отдано другим backend.

  Это число должно быть достаточно большим; настройка этого параметра означает, что proxy будет иметь предел в `unhealthy_request_count × upstreams_count` одновременных запросов всего, а все запросы после этого будут завершаться ошибкой из-за отсутствия доступных upstream.


<a id="events"></a>
## События

Когда upstream переходит из здорового состояния в нездоровое или наоборот, генерируется [событие](/docs/caddyfile/options#event-options). Эти события можно использовать для запуска других действий, например отправки уведомления или записи сообщения в журнал. События:

- `healthy` генерируется, когда upstream помечается здоровым после того, как раньше был нездоровым
- `unhealthy` генерируется, когда upstream помечается нездоровым после того, как раньше был здоровым

В обоих случаях `host` включается в событие как metadata для идентификации upstream, состояние которого изменилось. Его можно использовать как placeholder `{event.data.host}`, например с обработчиком события `exec`.



<a id="streaming"></a>
## Streaming

По умолчанию proxy частично буферизует ответ для эффективности передачи по сети.

Proxy также поддерживает WebSocket-соединения: выполняет HTTP upgrade request, затем переводит соединение в двунаправленный tunnel.

<aside class="tip">

По умолчанию WebSocket-соединения принудительно закрываются с отправкой Close control message и клиенту, и upstream при reload конфигурации. Каждый запрос удерживает ссылку на конфигурацию, поэтому закрытие старых соединений необходимо, чтобы контролировать использование памяти. Это поведение закрытия можно настроить опциями [`stream_timeout`](#stream_timeout) и [`stream_close_delay`](#stream_close_delay).

</aside>

- **flush_interval** <span id="flush_interval"/> — [значение длительности](/docs/conventions#durations), которое настраивает, как часто Caddy должен сбрасывать буфер ответа клиенту. По умолчанию периодический flush не выполняется. Отрицательное значение, обычно -1, означает "режим низкой задержки": оно полностью отключает буферизацию ответа и выполняет flush сразу после каждой записи клиенту, а также не отменяет запрос к backend, даже если клиент отключился раньше. Эта опция игнорируется, и ответы немедленно сбрасываются клиенту, если для ответа выполняется одно из условий:
	- `Content-Type: text/event-stream`
	- `Content-Length` неизвестен
	- HTTP/2 с обеих сторон proxy, `Content-Length` неизвестен, а `Accept-Encoding` либо не задан, либо равен "identity"

- **request_buffers** <span id="request_buffers"/> заставляет proxy прочитать до `<size>` байтов из тела запроса в буфер перед отправкой upstream. Это очень неэффективно и должно использоваться только если upstream требует чтения тел запросов без задержки, что должно исправляться на стороне upstream-приложения. Принимаются все форматы размеров, поддерживаемые [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **response_buffers** <span id="response_buffers"/> заставляет proxy прочитать до `<size>` байтов из тела ответа в буфер перед возвратом клиенту. По возможности этого следует избегать по причинам производительности, но это может быть полезно, если у backend более жесткие ограничения памяти. Принимаются все форматы размеров, поддерживаемые [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **stream_timeout** <span id="stream_timeout"/> — [значение длительности](/docs/conventions#durations), после которого streaming-запросы, такие как WebSocket, будут принудительно закрыты по истечении timeout. По сути это отменяет соединения, если они остаются открытыми слишком долго. Разумная начальная точка — `24h`, чтобы отсекать соединения старше суток. По умолчанию: без timeout.

- **stream_close_delay** <span id="stream_close_delay"/> — [значение длительности](/docs/conventions#durations), которое откладывает принудительное закрытие streaming-запросов, таких как WebSocket, при выгрузке конфигурации; вместо этого stream останется открытым до завершения задержки. Иными словами, включение этой опции предотвращает немедленное закрытие streams при reload конфигурации Caddy. Это может быть хорошей идеей, чтобы избежать thundering herd переподключающихся клиентов, чьи соединения были закрыты предыдущей конфигурацией. Разумная начальная точка — например `5m`, чтобы дать пользователям 5 минут естественно покинуть страницу после reload конфигурации. По умолчанию: без задержки.



<a id="headers"></a>
## Headers

Proxy может **изменять headers** между собой и backend:

- **header_up** <span id="header_up"/> задает, добавляет (с префиксом `+`), удаляет (с префиксом `-`) или выполняет замену (с двумя аргументами: поиск и замена) в заголовке запроса, идущем upstream к backend.

- **header_down** <span id="header_down"/> задает, добавляет (с префиксом `+`), удаляет (с префиксом `-`) или выполняет замену (с двумя аргументами: поиск и замена) в заголовке ответа, идущем downstream от backend.

Например, чтобы задать заголовок запроса, перезаписав любые существующие значения:

```caddy-d
header_up Some-Header "the value"
```

Чтобы добавить заголовок ответа; учтите, что у поля заголовка может быть несколько значений:

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

Чтобы удалить заголовок запроса и не дать ему дойти до backend:

```caddy-d
header_up -Some-Header
```

Чтобы удалить все совпадающие заголовки запроса, используя suffix match:

```caddy-d
header_up -Some-*
```

Чтобы удалить *все* заголовки запроса и иметь возможность отдельно добавить нужные (не рекомендуется):

```caddy-d
header_up -*
```

Чтобы выполнить замену по регулярному выражению в заголовке запроса:

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

Используется язык регулярных выражений RE2, включенный в Go. См. [справочник синтаксиса RE2](https://github.com/google/re2/wiki/Syntax) и [обзор синтаксиса regexp в Go](https://pkg.go.dev/regexp/syntax). Строка замены [разворачивается](https://pkg.go.dev/regexp#Regexp.Expand), позволяя использовать захваченные значения, например `$1` как первую группу захвата.


<a id="defaults"></a>
### Defaults

По умолчанию Caddy пропускает входящие headers, включая `Host`, к backend без изменений, за тремя исключениями:

- Он задает или дополняет поле заголовка [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Он задает поле заголовка [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Он задает поле заголовка [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"/> Для этих заголовков `X-Forwarded-*` proxy по умолчанию игнорирует их значения из входящих запросов, чтобы предотвратить spoofing.

Если Caddy не первый сервер, к которому подключаются ваши клиенты, например когда перед Caddy стоит CDN, можно настроить `trusted_proxies` со списком IP-диапазонов (CIDR), от которых входящие запросы считаются доверенными и содержащими корректные значения этих заголовков.

Настоятельно рекомендуется настраивать это через [глобальную опцию `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies), а не внутри proxy, чтобы это применялось ко всем proxy handler на вашем сервере; дополнительно это включает разбор IP клиента.

<aside class="tip">

Если вы используете Cloudflare перед Caddy, учтите, что вы можете быть уязвимы к spoofing заголовка `X-Forwarded-For`. Наши друзья из [Authelia](https://www.authelia.com) задокументировали [обходной путь](https://www.authelia.com/integration/proxies/forwarded-headers/) для настройки Cloudflare так, чтобы он игнорировал входящие значения этого заголовка.

</aside>

Дополнительно при использовании [`http` transport](#the-http-transport) заголовок `Accept-Encoding: gzip` будет задан, если он отсутствует в запросе от клиента. Это позволяет upstream отдавать сжатый контент, если он может. Это поведение можно отключить с помощью [`compression off`](#compression) в transport.


<a id="https"></a>
### HTTPS

Поскольку большинство headers сохраняют исходное значение при проксировании, при проксировании к HTTPS часто необходимо переопределить заголовок `Host` настроенным адресом upstream, чтобы заголовок `Host` совпадал со значением TLS ServerName:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Начиная с Caddy v2.11.0, это выполняется автоматически, поэтому больше не нужно явно переопределять заголовок `Host` при проксировании к HTTPS. Если вы хотите отказаться от этого поведения, можно установить заголовок `Host` в его исходное значение, но это редко имеет смысл:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

Заголовок `X-Forwarded-Host` все еще передается [по умолчанию](#defaults), поэтому upstream может использовать его, если ему нужно знать исходное значение заголовка `Host`.

То же применимо при завершении TLS в caddy и проксировании через HTTP, будь то порт или unix socket. Действительно, сам caddy должен получить корректный Host, когда он является целью `reverse_proxy`. В случае unix socket `upstream_hostport` будет путем сокета, и Host нужно задать явно.



<a id="rewrites"></a>
## Rewrites

По умолчанию Caddy выполняет upstream-запрос с тем же HTTP-методом и URI, что и входящий запрос, если rewrite не был выполнен в цепочке middleware до достижения `reverse_proxy`.

Перед проксированием запрос клонируется; это гарантирует, что любые изменения запроса во время handler не протекут в другие handlers. Это полезно в ситуациях, где обработка должна продолжиться после proxy.

Помимо [изменения headers](#headers), метод и URI запроса можно изменить перед отправкой upstream:

- **method** <span id="method"/> изменяет HTTP-метод клонированного запроса. Если метод изменен на `GET` или `HEAD`, тело входящего запроса *не* будет отправлено upstream этим handler. Это полезно, если вы хотите позволить другому handler прочитать тело запроса.
- **rewrite** <span id="rewrite"/> изменяет URI (path и query) клонированного запроса. Это похоже на директиву [`rewrite`](/docs/caddyfile/directives/rewrite), за исключением того, что rewrite не сохраняется за пределами области этого handler.

Такие rewrites часто полезны для паттерна "предварительной проверки запросов", когда запрос отправляется другому серверу, чтобы помочь принять решение о дальнейшей обработке текущего запроса.

Например, запрос можно отправить authentication gateway, чтобы решить, пришел ли запрос от аутентифицированного пользователя (например, у запроса есть session cookie) и должен ли он продолжиться, или вместо этого его нужно перенаправить на страницу входа. Для этого паттерна Caddy предоставляет сокращенную директиву [`forward_auth`](/docs/caddyfile/directives/forward_auth), чтобы убрать большую часть шаблонной конфигурации.




<a id="transports"></a>
## Transports

Proxy **transport** в Caddy является подключаемым:

- **transport** <span id="transport"/> определяет, как взаимодействовать с backend. По умолчанию `http`.


<a id="the-http-transport"></a>
### Transport `http`

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> — размер буфера чтения в байтах. Принимает все форматы, поддерживаемые [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). По умолчанию: `4KiB`.

- **write_buffer** <span id="write_buffer"/> — размер буфера записи в байтах. Принимает все форматы, поддерживаемые [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). По умолчанию: `4KiB`.

- **max_response_header** <span id="max_response_header"/> — максимальное число байтов для чтения из headers ответа. Принимает все форматы, поддерживаемые [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). По умолчанию: `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> включает [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt), популяризированный HAProxy, на соединении к upstream, добавляя данные реального IP клиента. Лучше всего сочетать это с [глобальной опцией `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies), если Caddy находится за другим proxy. Поддерживаются версии `v1` и `v2`. Используйте это только если вы знаете, что upstream server способен разбирать PROXY protocol. По умолчанию отключено.

- **dial_timeout** <span id="dial_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания при подключении к upstream socket. По умолчанию: `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> — максимальная [длительность](/docs/conventions#durations) ожидания перед запуском соединения RFC 6555 Fast Fallback. Отрицательное значение отключает это. По умолчанию: `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания чтения headers ответа от upstream. По умолчанию: без timeout.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания первых headers ответа от upstream после полной записи headers запроса, если запрос содержит заголовок `Expect: 100-continue`. По умолчанию: без timeout.

- **read_timeout** <span id="read_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания следующего чтения от backend. По умолчанию: без timeout.

- **write_timeout** <span id="write_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания следующих записей к backend. По умолчанию: без timeout.

- **resolvers** <span id="resolvers"/> — список DNS resolvers, переопределяющий системные resolvers.

- **tls** <span id="tls"/> использует HTTPS с backend. Это будет включено автоматически, если backend указаны со схемой `https://` или если настроены любые из нижеперечисленных опций `tls_*`.

- **tls_client_auth** <span id="tls_client_auth"/> включает TLS client authentication одним из двух способов: (1) указанием доменного имени, для которого Caddy должен получить сертификат и поддерживать его обновленным, или (2) указанием файла сертификата и файла ключа, которые нужно предъявлять для TLS client authentication с backend.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> отключает проверку TLS handshake, делая соединение небезопасным и уязвимым к атакам man-in-the-middle. *Не используйте в production.*

- **tls_curves** <span id="tls_curves"/> — список эллиптических кривых для поддержки при upstream-соединении. Значения по умолчанию Caddy современны и безопасны, поэтому это нужно настраивать только при особых требованиях.

- **tls_timeout** <span id="tls_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания завершения TLS handshake. По умолчанию: без timeout.

- **tls_trust_pool** <span id="tls_trust_pool"/> настраивает источник доверенных центров сертификации аналогично [поддирективе `trust_pool`](/docs/caddyfile/directives/tls#trust_pool), описанной в документации директивы `tls`. Список источников trust pool, доступных в стандартной установке Caddy, доступен [здесь](/docs/caddyfile/directives/tls#trust-pool-providers).

- **tls_server_name** <span id="tls_server_name"/> задает имя сервера, используемое при проверке сертификата, полученного в TLS handshake. По умолчанию используется часть host из адреса upstream.

  Переопределять это нужно только если адрес upstream не соответствует сертификату, который, вероятно, использует upstream. Например, если адрес upstream — IP-адрес, нужно настроить это на hostname, обслуживаемый upstream server.

  Можно использовать request placeholder; в таком случае для каждого запроса будет использоваться клон конфигурации HTTP transport, что может привести к снижению производительности.

- **tls_renegotiation** <span id="tls_renegotiation"/> задает уровень TLS renegotiation. TLS renegotiation — это выполнение последующих handshakes после первого. Уровень может быть одним из:
  - `never` (по умолчанию) отключает renegotiation.
  - `once` позволяет удаленному серверу запросить renegotiation один раз на соединение.
  - `freely` позволяет удаленному серверу многократно запрашивать renegotiation.

- **tls_except_ports** <span id="tls_except_ports"/> когда TLS включен, если цель upstream использует один из заданных портов, TLS будет отключен для этих соединений. Это может быть полезно при настройке dynamic upstream, где одни upstream ожидают HTTP, а другие HTTPS-запросы.

- **keepalive** <span id="keepalive"/> — либо `off`, либо [значение длительности](/docs/conventions#durations), указывающее, как долго держать соединения открытыми (timeout). По умолчанию: `2m`.

  ⚠️ Запросы к upstream HTTP/1.1 могут завершаться ошибками "connection reset by peer", если длительность keepalive превышает keepalive timeout upstream server. Идемпотентные запросы будут повторены HTTP transport Go, но в остальных случаях Caddy ответит status code 502.

- **keepalive_interval** <span id="keepalive_interval"/> — [длительность](/docs/conventions#durations) между liveness probes. По умолчанию: `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> определяет максимальное число соединений, которые нужно держать живыми. По умолчанию: без ограничения.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> если не равно нулю, управляет максимальным числом idle (keep-alive) соединений на host. По умолчанию: `32`.

- **versions** <span id="versions"/> позволяет настроить, какие версии HTTP поддерживать.
  
  Допустимые опции: `1.1`, `2`, `h2c`, `3`. 

  По умолчанию: `1.1 2`; или, если [схема upstream](#upstream-addresses) — `h2c://`, по умолчанию `h2c 2`.

  `h2c` включает cleartext HTTP/2-соединения к upstream. Это нестандартная возможность, которая не использует HTTP transport Go по умолчанию, поэтому она несовместима с другими возможностями.

  `3` включает HTTP/3-соединения к upstream. ⚠️ Это экспериментальная возможность, и она может измениться.

- **compression** <span id="compression"/> можно использовать для отключения сжатия к backend, установив значение `off`.

- **max_conns_per_host** <span id="max_conns_per_host"/> необязательно ограничивает общее число соединений на host, включая соединения в состояниях dialing, active и idle. По умолчанию: без ограничения.

- **network_proxy** <span id="network_proxy"/> указывает имя модуля network proxy для запросов к upstream server. Если явно не настроено, Caddy учитывает proxy, настроенный через переменные окружения согласно [Go stdlib](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), то есть `HTTP_PROXY`, `HTTPS_PROXY` и `NO_PROXY`. Когда для этого параметра задано значение, запросы проходят через reverse proxy в следующем порядке: Client (users) → `reverse_proxy` → `network_proxy` → upstream. Встроенные модули:
	- `none`, который используется, чтобы игнорировать настройки окружения `HTTP_PROXY`, `HTTPS_PROXY` и `NO_PROXY`.
	- `url <url>`, который используется, чтобы указать один URL, переопределяющий конфигурацию окружения.

<a id="the-fastcgi-transport"></a>
### Transport `fastcgi`

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> — root сайта. По умолчанию: `{http.vars.root}` или текущая рабочая директория.

- **split** <span id="split"/> — место, где нужно разделить path, чтобы получить PATH_INFO в конце URI.

- **env** <span id="env"/> задает дополнительную переменную окружения указанному значению. Можно указывать несколько раз для нескольких переменных окружения.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> включает разрешение директории `root` в ее фактическое значение путем вычисления symbolic link, если он существует.

- **dial_timeout** <span id="dial_timeout"/> — как долго ждать при подключении к upstream socket. Принимает [значения длительности](/docs/conventions#durations). По умолчанию: `3s`.

- **read_timeout** <span id="read_timeout"/> — как долго ждать при чтении с FastCGI server. Принимает [значения длительности](/docs/conventions#durations). По умолчанию: без timeout.

- **write_timeout** <span id="write_timeout"/> — как долго ждать при отправке в FastCGI server. Принимает [значения длительности](/docs/conventions#durations). По умолчанию: без timeout.

- **capture_stderr** <span id="capture_stderr"/> включает захват и журналирование любых сообщений, отправленных upstream fastcgi server в `stderr`. По умолчанию журналирование выполняется на уровне `WARN`. Если ответ имеет status `4xx` или `5xx`, вместо этого будет использоваться уровень `ERROR`. По умолчанию `stderr` игнорируется.

<aside class="tip">

Если вы пытаетесь обслуживать современное PHP-приложение, возможно, вам нужна директива [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi), которая является сокращением для proxy с директивой `fastcgi` и необходимыми rewrites для использования `index.php` как routing entrypoint.

</aside>



<a id="intercepting-responses"></a>
## Перехват ответов

Reverse proxy можно настроить для перехвата ответов от backend. Для этого можно определить [response matchers](/docs/caddyfile/response-matchers), аналогично синтаксису request matchers, и будет вызван первый совпавший маршрут `handle_response`.

Когда response handler вызывается, ответ от backend не записывается клиенту; вместо этого выполняется настроенный маршрут `handle_response`, и именно этот маршрут должен записать ответ. Если маршрут *не* записывает ответ, обработка запроса продолжится любыми handlers, которые [упорядочены после](/docs/caddyfile/directives#directive-order) этого `reverse_proxy`.

- **@name** — имя [response matcher](/docs/caddyfile/response-matchers). Пока каждый response matcher имеет уникальное имя, можно определить несколько matchers. Ответ можно сопоставлять по status code и наличию или значению заголовка ответа.

- **replace_status** <span id="replace_status"/> просто изменяет status code ответа при совпадении с указанным matcher.

- **handle_response** <span id="handle_response"/> определяет маршрут, который нужно выполнить при совпадении с указанным matcher или, если matcher опущен, для всех ответов. Применяется первый совпавший блок. Внутри блока `handle_response` можно использовать любые другие [директивы](/docs/caddyfile/directives).

Дополнительно внутри `handle_response` можно использовать две специальные handler-директивы:

- **copy_response** <span id="copy_response"/> копирует тело ответа, полученное от backend, обратно клиенту. Необязательно позволяет при этом изменить status code ответа. Эта директива [упорядочена перед `respond`](/docs/caddyfile/directives#directive-order).

- **copy_response_headers** <span id="copy_response_headers"/> копирует headers ответа от backend клиенту, необязательно включая *ИЛИ* исключая список полей headers (нельзя указать одновременно `include` и `exclude`). Эта директива [упорядочена после `header`](/docs/caddyfile/directives#directive-order).

В маршрутах `handle_response` будут доступны три placeholder:

- `{rp.status_code}` Status code из ответа backend.

- `{rp.status_text}` Status text из ответа backend.

- `{rp.header.*}` Headers из ответа backend.

Хотя response handler reverse proxy может скопировать новый ответ, полученный от proxy, обратно клиенту, он не может передать этот новый ответ последующему reverse proxy. Каждое использование `reverse_proxy` получает тело из исходного запроса или измененное другим модулем.




<a id="examples"></a>
## Примеры

Reverse proxy всех запросов к локальному backend:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


[Балансировать нагрузку](#load-balancing) всех запросов [между 3 backend](#upstreams):

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


То же, но только для запросов внутри `/api`, и со sticky-поведением через [policy `cookie`](#lb_policy):

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


Использовать [активные health checks](#active-health-checks), чтобы определить, какие backend здоровы, и включить [retry](#lb_try_duration) при ошибках соединения, удерживая запрос до нахождения здорового backend:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Настроить некоторые [опции transport](#transports):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Reverse proxy к [HTTPS upstream](#https): начиная с v2.11.0, Caddy автоматически задает заголовок `Host` так, чтобы он совпадал с host upstream, поэтому делать это вручную больше не нужно:

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Reverse proxy к HTTPS upstream, но [⚠️ отключить TLS verification](#tls_insecure_skip_verify). Это НЕ РЕКОМЕНДУЕТСЯ, поскольку отключает все проверки безопасности, которые предлагает HTTPS; если возможно, предпочтительнее проксирование по HTTP в частных сетях, потому что оно избегает ложного ощущения безопасности:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


Вместо этого можно установить доверие к upstream, явно [доверяя сертификату upstream](#tls_trust_pool), и необязательно задав TLS-SNI так, чтобы он совпадал с hostname в сертификате upstream:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



[Убрать префикс path](handle_path) перед проксированием; но учитывайте [проблему subfolder <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575):

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


Заменить префикс path перед проксированием, используя [`rewrite`](/docs/caddyfile/directives/rewrite):

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


Поддержка `X-Accel-Redirect`, то есть обслуживание статических файлов по запросу, через [перехват ответа](#intercepting-responses):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Пользовательская страница ошибки для ошибок от upstream через [перехват ошибочных ответов](#intercepting-responses) по status code:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Получать backend [динамически](#dynamic-upstreams) из DNS-запросов к [записям `A`/`AAAA`](#aaaaa):

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Получать backend [динамически](#dynamic-upstreams) из DNS-запросов к [записям `SRV`](#srv):

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


Использование [активных health checks](#active-health-checks) и `health_upstream` может быть полезно при создании промежуточного сервиса для более тщательной health check. Затем `{http.reverse_proxy.active.target_upstream}` можно использовать как заголовок, чтобы передать исходный upstream сервису health check.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
