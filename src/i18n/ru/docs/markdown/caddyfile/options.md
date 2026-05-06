---
title: Глобальные параметры (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


<a id="global-options"></a>
# Глобальные параметры

Caddyfile позволяет задавать параметры, которые применяются глобально. Некоторые параметры действуют как значения по умолчанию; другие настраивают HTTP servers и не относятся только к одному конкретному site; третьи настраивают поведение Caddyfile [adapter](/docs/config-adapters).

Самый верх Caddyfile может быть **global options block**. Это block без keys:

```caddy
{
	...
}
```

Такой block может быть максимум один, и он должен быть первым block в Caddyfile.

Возможные options (нажмите на option, чтобы перейти к документации):

```caddy
{
	# General Options
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS Options
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Server Options
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# File Systems
	filesystem <name> <module> {
		<options...>
	}

	# PKI Options
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Event options
	events {
		on <event> <handler...>
	}
}
```


<a id="general-options"></a>
## General Options

##### `debug`
Включает debug mode, который устанавливает log level `DEBUG` для [default logger](#log). Это раскрывает больше деталей, полезных при troubleshooting (и очень verbose в production). Мы просим включать это перед обращением за помощью на [community forums](https://caddy.community). Например, в начале Caddyfile, если других global options нет:

```caddy
{
	debug
}
```


##### `http_port`
Порт, который server использует для HTTP.

**Только для внутреннего использования**; не изменяет HTTP port для clients. Обычно используется, если внутри вашей internal network нужно port forward `80` на другой port (например, `8080`) до того, как traffic достигнет Caddy, для целей routing.

Default: `80`


##### `https_port`
Порт, который server использует для HTTPS.

**Только для внутреннего использования**; не изменяет HTTPS port для clients. Обычно используется, если внутри вашей internal network нужно port forward `443` на другой port (например, `8443`) до того, как traffic достигнет Caddy, для целей routing.

Default: `443`


##### `default_bind`
Default bind address(es), используемые для всех sites, если в site не используется directive [`bind`](/docs/caddyfile/directives/bind). Default: empty, что означает bind ко всем interfaces.

<aside class="tip">

Имейте в виду, что это применяется только к servers, generated by Caddyfile; это означает, что HTTP server, созданный [Automatic HTTPS](/docs/automatic-https) для HTTP-to-HTTPS redirects, не inherited эти bind addresses. Чтобы обойти это, обязательно объявите site `http://` (он может быть empty, без directives), чтобы он существовал при адаптации Caddyfile и получил bind addresses.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
Назначает порядок HTTP handler directive(s). Поскольку HTTP handlers выполняются в sequential chain, важно, чтобы handlers выполнялись в правильном порядке. Standard directives имеют [предопределенный порядок](/docs/caddyfile/directives#directive-order), но если используются third-party HTTP handler modules, нужно явно определить порядок либо этой option, либо поместив directive в block [`route`](/docs/caddyfile/directives/route). Ordering может быть absolute (`first` или `last`) или relative (`before` или `after`) к другой directive.

Например, при использовании plugin [`replace-response`](https://github.com/caddyserver/replace-response), нужно убедиться, что его directive ordered after `encode`, чтобы он мог выполнить replacements до того, как response будет encoded (потому что responses идут вверх по handler chain, а не вниз):

```caddy
{
	order replace after encode
}
```


##### `storage`
Настраивает storage mechanism Caddy. Default — [`file_system`](/docs/json/storage/file_system/). Доступно много других [storage modules](/docs/json/storage/), предоставляемых как plugins.

Например, чтобы изменить storage location файловой системы:

```caddy
{
	storage file_system /path/to/custom/location
}
```

Customizing storage module обычно нужен при syncing storage Caddy между несколькими instances Caddy, чтобы все они использовали одни и те же certificates и keys. Подробнее смотрите [раздел Automatic HTTPS о storage](/docs/automatic-https#storage).


##### `storage_clean_interval`
Как часто scan storage units для старых или expired assets и удалять их. Эти scans создают много reads (и list operations) на storage module, поэтому для large deployments выбирайте longer interval. Принимает [duration values](/docs/conventions#durations).

Storage всегда очищается при первом startup процесса. Затем новая cleaning будет начата через этот duration после начала предыдущей cleaning, если предыдущая cleaning завершилась меньше чем за половину этого interval (иначе следующий start будет skipped).

Default: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
Настраивает [admin API endpoint](/docs/api). Принимает placeholders. Принимает [network addresses](/docs/conventions#network-addresses).

Default: `localhost:2019`, если не задана environment variable `CADDY_ADMIN`.

Если установить `off`, admin endpoint будет disabled. При disabled состоянии **config changes будут невозможны** без остановки и запуска server, потому что команда [`caddy reload`](/docs/command-line#caddy-reload) использует admin API для push новой config в running server.

Не забывайте использовать CLI flag `--address` с совместимыми [commands](/docs/command-line), чтобы указать текущий admin endpoint, если address running server изменен относительно default.

Также поддерживает эти sub-options:

- **origins** настраивает список [origins](https://developer.mozilla.org/en-US/docs/Glossary/Origin), которым разрешено подключаться к endpoint.

  Default выбирается intelligent:
  - если listen address является loopback (например, `localhost`, loopback IP или unix socket), allowed origins — `localhost`, `::1` и `127.0.0.1`, соединенные с port listen address (так что `localhost:2019` — valid origin).
  - если listen address не loopback, allowed origin совпадает с listen address.

  Если host listen address не является wildcard interface (wildcards include: empty string, `0.0.0.0` или `[::]`), выполняется enforcement header `Host`. Фактически это означает, что by default header `Host` validated against `origins`, поскольку interface — `localhost`. Но для address вроде `:2020` с wildcard interface validation header `Host` не выполняется.

- **enforce_origin** принудительно включает enforcement request header `Origin`. Это делается implicitly всякий раз, когда client отправляет CORS headers или если client explicitly disables CORS через `Sec-Fetch-Mode: no-cors`. Иначе эта option наиболее полезна, когда listen address — wildcard interface (так как `Host` не validated), а admin API exposed to public internet. Она включает CORS preflight checks и гарантирует, что header `Origin` validated against list `origins`. Используйте это только если запускаете Caddy на development machine и нужно обращаться к admin API из web browser.

Например, чтобы expose admin API на другом port, на всех interfaces — ⚠️ этот port **не должен быть публично exposed**, иначе любой сможет control ваш server; если он должен быть public, рассмотрите enabling origin enforcement:

```caddy
{
	admin :2020
}
```

Чтобы отключить admin API — ⚠️ это делает **config reloads невозможными** без остановки и запуска server:

```caddy
{
	admin off
}
```

Чтобы использовать [unix socket](/docs/conventions#network-addresses) для admin API, разрешая access control через file permissions:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Чтобы разрешить только requests с matching header `Origin`:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`

Управляет тем, должна ли текущая JSON config persisted в [configuration directory](/docs/conventions#configuration-directory), чтобы избежать потери config changes, выполненных через admin API. Сейчас поддерживается только option `off`. По умолчанию config persisted.

```caddy
{
	persist_config off
}
```



##### `log`
Настраивает named loggers.

Name можно передать, чтобы указать specific logger, поведение которого нужно customize. Если name не задано, изменяется behavior logger `default`. Подробнее о logger `default` и о том, [как logging работает в Caddy](/docs/logging), можно прочитать отдельно.

Несколько loggers с разными names можно настроить, используя `log` несколько раз.

Это отличается от directive [`log`](/docs/caddyfile/directives/log), которая настраивает только HTTP request logging (также known as access logs). Global option `log` разделяет структуру configuration с directive (кроме `include` и `exclude`), а полная documentation находится на странице directive.

- **output** настраивает, куда писать logs.

  Полную documentation смотрите в directive [`log`](/docs/caddyfile/directives/log#output-modules).

- **format** описывает, как encode или format logs.

  Полную documentation смотрите в directive [`log`](/docs/caddyfile/directives/log#format-modules).

- **level** — minimum entry level для log.

  Default: `INFO`.

  Возможные values: `DEBUG`, `INFO`, `WARN`, `ERROR` и очень редко `PANIC`, `FATAL`.

- **include** задает log names, включаемые в этот logger.

  By default этот list empty (то есть included все logs).

  Например, чтобы include только logs, emitted admin API, include `admin.api`.

- **exclude** задает log names, excluded from этого logger.

  By default этот list empty (то есть logs не excluded).

  Например, чтобы exclude только HTTP access logs, exclude `http.log.access`.

Logger names, которые принимают `include` и `exclude`, зависят от используемых modules, и проще всего discover их из previous logs.

Вот пример logging as json всех http access logs и admin logs в stdout:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
Определяет grace period для shutdown HTTP servers (то есть во время config changes или остановки Caddy).

Во время grace period новые connections не принимаются, idle connections закрываются, а active connections impatiently wait, пока завершат свои requests. Если clients не завершат requests в течение grace period, server будет forcefully terminated, чтобы reload мог завершиться и resources освободились. Принимает [duration values](/docs/conventions#durations).

По умолчанию grace period eternal, что означает, что connections никогда не закрываются forcefully.

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
Определяет [duration](/docs/conventions#durations)
*до* [grace period](#grace_period), в течение которого server, который будет stopped, продолжает работать normally, за исключением того, что placeholder `{http.shutting_down}` evaluates to `true`, а `{http.time_until_shutdown}` дает время до начала grace period.

Это вызывает delay, если какой-либо server shutting down как часть config change, и effectively schedules change на later time. Это полезно, чтобы announcement health checkers о impending doom этого server и дать time load balancer убрать его из rotation; например:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


<a id="tls-options"></a>
## TLS Options

##### `auto_https`
Настраивает [Automatic HTTPS](/docs/automatic-https), функцию, которая позволяет Caddy automate certificate management и HTTP-to-HTTPS redirects для ваших sites.

Есть несколько modes:

- `off`: отключает both certificate automation and HTTP-to-HTTPS redirects.

- `disable_redirects`: отключает только HTTP-to-HTTPS redirects.

- `disable_certs`: отключает только certificate automation.

- `ignore_loaded_certs`: автоматизирует certificates даже для names, которые появляются в manually-loaded certificates. Полезно, если вы указали certificate с directive [`tls`](/docs/caddyfile/directives/tls), содержащий names (или wildcards), которые вместо этого хотите manage automatically.

<aside class="tip">

Эта option не влияет на default protocol Caddy, который всегда HTTPS, если site address содержит valid domain name. Это означает, что `auto_https off` не заставит ваш site обслуживаться по HTTP; он только отключит automatic certificate management и redirects.

Это означает, что если вы хотите обслуживать site по HTTP, следует изменить [site address](/docs/caddyfile/concepts#addresses), добавив prefix `http://` или suffix `:80` (или option [`http_port`](#http_port)).

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
Ваш email address. В основном используется при создании ACME account у вашего CA и настоятельно рекомендуется на случай проблем с certificates.

<aside class="tip">

Имейте в виду, что Let's Encrypt может отправлять emails о приближении expiry вашего certificate, но это может be misleading, потому что Caddy мог выбрать другого issuer (например, ZeroSSL) при renewing. Проверьте logs и/или сам certificate (например, в browser), чтобы увидеть, какой issuer использовался и что его expiry все еще valid; если так, email от Let's Encrypt можно safely ignore.

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
Задает default TLS ServerName для случаев, когда clients не используют SNI в своем ClientHello.

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ <i>Experimental</i>

Если настроено, fallback становится TLS ServerName в ClientHello, если original ServerName не match никакие certificates в cache.

Use cases для этого очень niche; обычно если client является CDN и пропускает ServerName downstream handshake, но может accept certificate с hostname origin, тогда вы задаете это как hostname origin. Обратите внимание, что Caddy должен manage certificate для этого name.

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
Заставляет **все** certificates по умолчанию issued internally, а не через (public) ACME CA вроде Let's Encrypt. Это полезно как быстрый toggle в development environments.

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
Пропускает attempts установить root local CA в system trust store, а также в Java и Mozilla Firefox trust stores.

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
Указывает URL directory ACME CA. Для testing или development настоятельно рекомендуется задать staging endpoint Let's Encrypt [<img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/). Default: production endpoints ZeroSSL и Let's Encrypt.

Обратите внимание, что globally-configured ACME CA может применяться не ко всем sites; смотрите [hostname requirements](/docs/automatic-https#hostname-requirements) для использования default ACME issuer(s).

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
Указывает PEM file, содержащий trusted root certificate для ACME CA endpoints, если его нет в system trust store.

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
Указывает External Account Binding для всех ACME transactions.

Например, с mock ZeroSSL credentials:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
Настраивает provider [ACME DNS challenge](/docs/automatic-https#dns-challenge), используемый для всех ACME transactions.

Требуется custom build Caddy с plugin для вашего DNS provider.

Tokens после имени provider настраивают provider так же, как если бы он был указан в issuer [`acme` directive `tls`](/docs/caddyfile/directives/tls#acme).

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
Настраивает default DNS provider, используемый, когда никакой другой не указан локально в relevant context. Например, если ACME DNS challenge включен, но DNS provider не настроен, будет использован этот global default. Он также применяется для публикации Encrypted ClientHello (ECH) configs.

Чтобы это работало, binary Caddy должен быть compiled с указанным DNS provider module.

Пример с credentials из environment variable:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Требуется Caddy 2.10 beta 1 или новее.)


##### `ech`
Включает Encrypted ClientHello (ECH), используя указанные public domain name(s) как plaintext server name (SNI) в TLS handshakes. При правильных условиях ECH может помочь защитить domain names ваших sites on the wire во время connections. Caddy сгенерирует и опубликует один ECH config для каждого указанного public name. Publication — это то, как compatible clients (например, properly-configured modern browsers) узнают, что нужно использовать ECH для доступа к вашим sites.

Чтобы работать правильно, ECH config(s) должны быть опубликованы способом, который ожидают clients. Большинство browsers (с включенными DNS-over-HTTPS или DNS-over-TLS) ожидают ECH configs в HTTPS-type DNS records. Caddy выполняет такую publication автоматически, но нужно указать DNS provider либо через sub-option `dns`, либо globally через [global option `dns`](#dns), а binary Caddy должен быть built с указанным DNS provider module. (Custom builds доступны на нашей [странице загрузки](/download).)

**Privacy notices:**

- В общем случае рекомендуется **maximimize размер вашего [_anonymity set_](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction)**. Поэтому обычно мы рекомендуем большинству users настроить *только одно* public domain name для защиты всех sites.
- **Ваш server должен быть authoritative для указанных public domain name(s)** (то есть они должны указывать на ваш server), потому что Caddy получит certificates для них. Эти certificates жизненно важны, чтобы spec-conforming clients могли надежно и безопасно подключаться с ECH в некоторых cases. Они используются только для proper ECH handshake, а не для application data (ваших sites, если вы не определите site, совпадающий с public domain name).
- Обстоятельства могут различаться. Если ставки высоки, мы рекомендуем консультироваться с experts для **review вашего threat model**, поскольку ECH не является universal solution.

Пример с credentials из environment variable для publication на nameservers, parked at Cloudflare:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Это должно заставить compatible clients загружать все ваши sites с `ech.example.net`, а не с individual site names, exposed in plaintext.

Successful publication требует, чтобы domains вашего site были parked у настроенного DNS provider, а records можно было modify заданными credentials / provider configuration.

(Требуется Caddy 2.10 beta 1 или новее.)


##### `on_demand_tls`
Настраивает [On-Demand TLS](/docs/automatic-https#on-demand-tls) там, где он включен, но не включает его (для включения используйте [subdirective `on_demand` directive `tls`](/docs/caddyfile/directives/tls#syntax)). Обязательно для production environments, чтобы prevent abuse.

- **ask** заставляет Caddy выполнить HTTP request к заданному URL, спрашивая, разрешено ли выдавать certificate для domain.

  Request имеет query string `?domain=`, содержащую value domain name.

  Если endpoint возвращает status code `2xx`, Caddy будет authorized получить certificate для этого name. Любой другой status code приведет к отмене issuance certificate и error TLS handshake.

<aside class="tip">

Ask endpoint должен отвечать *как можно быстрее*, за несколько milliseconds, ideally. Обычно endpoint должен выполнять constant-time lookup в database с index by domain name; избегайте loops. Избегайте DNS queries или других network requests.

</aside>

- **permission** позволяет использовать custom modules, чтобы определить, должен ли certificate issued для конкретного name. Module должен implement interface [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission). Включен permission module `http`, который используется option `ask` и остается shortcut для backwards compatibility.

- ⚠️ Options rate limiting **interval** и **burst** были доступны, но НЕ рекомендуются. Удалите их из config, если они все еще есть.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
Указывает type key, генерируемого для TLS certificates; изменяйте это только при specific need customize.

Возможные values: `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
Определяет issuer (или source) TLS certificates.

Это позволяет настраивать issuers globally, а не per-site, как с subdirective [`issuer` directive `tls`](/docs/caddyfile/directives/tls#issuer).

Можно повторять, если нужно настроить несколько issuers для попытки. Они будут tried в порядке определения.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
Как часто scan all loaded, managed certificates на expiration и trigger renewal, если expired.

Default: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
Validity period, который нужно попросить CA issue для certificate.

Это value используется для вычисления field `notAfter` ACME order; поэтому system должна иметь reasonably synchronized clock. NOTE: не все CAs поддерживают это. Проверьте ACME documentation вашего CA, чтобы узнать, разрешено ли это и какие values можно использовать.

Default: `0` (CA выбирает lifetime, обычно 90 days)

⚠️ Это experimental feature. Может измениться или быть removed.

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
Как часто проверять, нужно ли обновлять [OCSP staples <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling).

Default: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
Можно задать `off`, чтобы отключить OCSP stapling. Полезно в environments, где responders недоступны из-за firewalls.

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
Ratio (между 0 и 1) lifetime certificate, который должен оставаться перед тем, как Caddy попытается renew certificate. Например, если certificate имеет lifetime 90 days, а ratio равен `0.3333` (default value), Caddy будет постоянно пытаться renew certificate, когда до expiration останется 30 days или меньше. Также можно задать per site с subdirective [`renewal_window_ratio` directive `tls`](/docs/caddyfile/directives/tls#renewal_window_ratio).

Обычно это менять не нужно, но это может быть полезно, чтобы renew позже в lifetime certificate, если ваш CA имеет очень long issuance time.

Имейте в виду, что это suggestion, поскольку ACME issuers могут implement [ARI extension](https://datatracker.ietf.org/doc/rfc9773/), где issuer диктует window, в котором ACME client (в данном случае Caddy) должен попытаться renewal, и это window может не совпадать с ratio.

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
Если ваш CA предоставляет multiple certificate chains, можно использовать эту option, чтобы указать, какую chain Caddy должен prefer. Задайте одну из следующих options:

- **smallest** скажет Caddy prefer chains с smallest amount of bytes.

- **root_common_name** — list одного или нескольких common names; Caddy выберет first chain, у которой root matches хотя бы одно из specified common names.

- **any_common_name** — list одного или нескольких common names; Caddy выберет first chain, у которой issuer matches хотя бы одно из specified common names.

Обратите внимание, что указание `preferred_chains` как global option повлияет на всех issuers, если нет [overriding issuer level config](/docs/caddyfile/directives/tls#acme).

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


<a id="server-options"></a>
## Server Options

Настраивает [HTTP servers](/docs/json/apps/http/servers/) с settings, которые потенциально охватывают multiple sites и потому не могут корректно настраиваться в site blocks. Эти options влияют на listener/socket или другие facilities ниже HTTP layer.

Можно указывать несколько раз с разными values `listener_address`, чтобы настраивать разные options per server. Например, `servers :443` применится только к server, bound to listener address `:443`. Если listener address опущен, options применятся к remaining server.

<aside class="tip">

Используйте команду [`caddy adapt`](/docs/command-line#caddy-adapt), чтобы найти listen address для servers в вашем Caddyfile.

</aside>


Например, чтобы настроить разные options для servers на ports `:80` и `:443`, нужно указать два blocks `servers`:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

При использовании `servers` это применится **только** к servers, которые **фактически появляются** в Caddyfile (то есть produced by site block). Помните, [Automatic HTTPS](/docs/automatic-https) создаст server, listening on port `80` (или option [`http_port`](#http_port)), чтобы обслуживать HTTP->HTTPS redirects и решать ACME HTTP challenge; это происходит at runtime, то есть *после* того, как Caddyfile adapter применит `servers`. Иными словами, `servers` **не применится** к `:80`, если вы явно не объявите site block вроде `http://` или `:80`.


<aside class="tip">

Если вы используете directive [`bind`](/docs/caddyfile/directives/bind) или global option [`default_bind`](/docs/caddyfile/options#default_bind), `listener_address` *ДОЛЖЕН* match bind address, combined with port of site block, иначе settings не будут applied. Например:

```caddy
{
	# This will NOT match the server, bind address missing
	servers :8080 {
		name private
	}

	# This will work because it's an exact match
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

Custom name, назначаемое этому server. Обычно полезно для идентификации server по name в logs и metrics. Если не задано, Caddy определит его dynamically по pattern `srvX`, где `X` начинается с `0` и increments based on number of servers in config.

Имейте в виду, что settings применяются только к servers, produced by site blocks in config. [Automatic HTTPS](/docs/automatic-https) создает server `:80` (или [`http_port`](#http_port)) at runtime, поэтому если вы хотите rename его, нужен как минимум empty site block `http://`.

Например:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

Позволяет настраивать [listener wrappers](/docs/json/apps/http/servers/listener_wrappers/), которые могут modify behaviour socket listener. Они применяются в заданном order.

###### `tls`

Listener wrapper `tls` — это no-op listener wrapper, который marks, где TLS listener должен находиться в chain listener wrappers. Его следует использовать только если другой listener wrapper должен быть placed in front of TLS handshake.

###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) предоставляет HTTP->HTTPS redirects для connections, которые приходят на TLS port как HTTP request, определяя по first few bytes, что это не TLS handshake, а HTTP request. Это наиболее полезно при serving HTTPS на non-standard port (не `443`), поскольку browsers будут пробовать HTTP, если scheme не указана. Он должен быть placed *before* listener wrapper `tls`. Пример:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

Listener wrapper [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) (до v2.7.0 был доступен только через plugin) включает parsing [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (популяризован HAProxy). Его нужно использовать *before* listener wrapper `tls`, поскольку он parses plaintext data в начале connection:

Учитывайте, что metadata из PROXY protocol может быть applied к connection до evaluation matchers или [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies). IP address immediate peer будет потерян для дальнейшей evaluation.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** задает maximum duration ожидания PROXY header. Defaults to `5s`.

- **allow** — list CIDR ranges trusted sources, от которых принимать PROXY headers. Unix sockets trusted by default и не входят в эту option.

- **deny** — list CIDR ranges trusted sources, от которых reject PROXY headers.

- **fallback_policy** — action, если PROXY header приходит с address, которого нет ни в allow, ни в deny list. Default fallback policy — `ignore`. Accepted values `fallback_policy`:
	- `ignore`: address from PROXY header, but accept connection
	- `use`: address from PROXY header
	- `reject`: connection when PROXY header is sent
	- `require`: connection to send PROXY header, reject if not present
	- `skip`: accepts a connection without requiring the PROXY header.


Например, для HTTPS server (нужен listener wrapper `tls`), который принимает PROXY headers от specific range IP addresses и rejects PROXY headers от другого range, с timeout 2 seconds:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body** — [duration value](/docs/conventions#durations), задающее, как долго allow read from client upload. Short non-zero value может mitigate slowloris attacks, но также может affect legitimately slow clients. Defaults to no timeout.

- **read_header** — [duration value](/docs/conventions#durations), задающее, как долго allow read from client's request headers. Defaults to no timeout.

- **write** — [duration value](/docs/conventions#durations), задающее, как долго allow write to client. Обратите внимание, что small value при serving large files может negatively affect legitimately slow clients. Defaults to no timeout.

- **idle** — [duration value](/docs/conventions#durations), задающее maximum time ожидания next request, когда keep-alives enabled. Defaults to 5 minutes, чтобы помочь avoid resource exhaustion.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

Interval, с которым TCP keepalive packets отправляются для поддержания connection alive на TCP layer, когда другие data не передаются. Defaults to `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

Duration, в течение которого connection должна быть idle перед отправкой TCP keepalive packets, когда другие data не передаются. Defaults to `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

Maximum number TCP keepalive packets, отправляемых перед тем, как считать connection dead. Defaults to `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

По умолчанию 0-RTT (early data) enabled для QUIC listeners (то есть HTTP/3), чтобы clients могли отправлять data в first round trip TLS handshake, что может improve performance для repeat connections.

Можно задать `off`, чтобы отключить 0-RTT для QUIC listeners. Одна причина отключить 0-RTT — использование matcher [`remote_ip`](/docs/caddyfile/matchers#remote-ip), который вводит dependency on remote address being verified, если routing happens before TLS handshake completes. В этом случае writes HTTP 425 response, но некоторые clients (browsers) могут misbehave и не выполнить retry, поэтому отключение 0-RTT может ensure, что users не увидят 425 responses, ценой потери performance benefits 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

Позволяет настраивать IP ranges (CIDRs) proxy servers, requests от которых должны быть trusted. По умолчанию proxies не trusted.

Включение этого causes trusted requests to have the *real* client IP parsed из HTTP headers (по умолчанию `X-Forwarded-For`; см. [`client_ip_headers`](#client-ip-headers), чтобы настроить другие headers). Если trusted, client IP добавляется в [access logs](/docs/caddyfile/directives/log), доступен как placeholder `{client_ip}` [placeholder](/docs/caddyfile/concepts#placeholders), и позволяет использовать matcher [`client_ip`](/docs/caddyfile/matchers#client-ip). Если request не от trusted proxy, client IP устанавливается в remote IP address прямого incoming connection или address, заданный [PROXY protocol](/docs/caddyfile/options#proxy-protocol), если он используется. По умолчанию IPs в headers parsed left-to-right. См. [`trusted_proxies_strict`](#trusted-proxies-strict), чтобы изменить это behaviour.

Некоторые matchers или handlers могут использовать trust status request для принятия decisions. Например, если trusted, handler [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) будет proxy и augment sensitive request headers `X-Forwarded-*`.

Сейчас в standard distribution Caddy включен только `static` [IP source module](/docs/json/apps/http/servers/trusted_proxies/), но это можно [extend](/docs/extending-caddy) plugins, чтобы поддерживать dynamic list IP ranges.


###### `static`

Принимает static (unchanging) list IP ranges (CIDRs), которым нужно trust.

Как shortcut, `private_ranges` можно использовать для match всех private IPv4 and IPv6 ranges. Это то же самое, что указать все эти ranges: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

Syntax:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

Полный пример, доверяющий example IPv4 range и IPv6 range:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

Когда [`trusted_proxies`](#trusted-proxies) enabled, IPs в headers (configured by [`client_ip_headers`](#client-ip-headers)) по умолчанию parsed left-to-right. First untrusted IP address found становится real client address. Начиная с v2.8, можно opt-in к right-to-left parsing этих headers через `trusted_proxies_strict`. По умолчанию эта option disabled для backwards compatibility.

Upstream proxies вроде HAProxy, CloudFlare, AWS ALB, CloudFront и т. д. append каждый новый connecting remote address справа от `X-Forwarded-For`. Рекомендуется включать `trusted_proxies_strict` при работе с ними, поскольку left-most IP address может быть spoofed client.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

Specifically в случае AWS ALB вы почти наверняка захотите включить эту option. [По их документации](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15), real client IP можно identify только задав XFF mode `append`. Этот IP будет appended справа от `X-Forwarded-For` и может быть safely extracted только через `trusted_proxies_strict`.

</aside>

##### `trusted_proxies_unix`

Option `trusted_proxies_unix` позволяет trust все connections, приходящие от Unix sockets, что полезно, когда Caddy находится за reverse proxy (возможно, другим instance Caddy), который подключается к нему через Unix socket (то есть directive [`bind`](/docs/caddyfile/directives/bind) set to unix socket). По умолчанию disabled.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

В паре с [`trusted_proxies`](#trusted-proxies) позволяет настраивать, какие headers использовать для определения IP address client. По умолчанию учитывается только `X-Forwarded-For`. Можно указать несколько header fields; в этом случае используется first non-empty header value.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

Включает сбор metrics; необходимо перед scraping metrics или pushing их через OTLP. Обратите внимание, что metrics reduce performance на really busy servers. (Наше community работает над улучшением этого. Please get involved!)

```caddy
{
	metrics
}
```

Можно добавить option `per_host`, чтобы label metrics host name metric.

```caddy
{
	metrics {
		per_host
	}
}
```

Из-за potential infinite cardinality при observing всех possible hosts, которые могут отправляться clients, Caddy будет record metrics только для configured hosts, а все остальные hosts (например, attacker.com) aggregated under label "_other". Чтобы force observation всех hosts, если potential infinite cardinality является acceptable risk, добавьте `observe_catchall_hosts`. Обратите внимание, что добавление `observe_catchall_hosts` не включит `per_host`. Однако это автоматически enabled для HTTPS servers (поскольку certificates дают некоторую protection against unbounded cardinality), но disabled для HTTP servers by default, чтобы prevent cardinality attacks from arbitrary Host headers.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Можно добавить option `otlp`, чтобы push те же metrics в OpenTelemetry Protocol (OTLP) endpoint. Exporter настраивается стандартными environment variables OpenTelemetry `OTEL_*`, такими как `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` и `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Например:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Подробнее смотрите [Monitoring Caddy with metrics](/docs/metrics).

##### `trace`

Log каждый individual handler, который invoked. Требует, чтобы log emit at level `DEBUG` (это можно сделать с [global option `debug`](#debug)).

NOTE: Это может log configuration ваших HTTP handler modules; не включайте это в insecure contexts, если в configuration есть sensitive data.

⚠️ Это experimental feature. Может измениться или быть removed.

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

Maximum size для parsing HTTP request headers client. Если limit exceeded, server ответит HTTP status `431 Request Header Fields Too Large`. Принимает все formats, поддерживаемые [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). По умолчанию limit `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

Включает full-duplex communication для HTTP/1 requests.

Для HTTP/1 requests Go HTTP server по умолчанию consumes любую unread portion request body перед началом write response, предотвращая concurrent reading from request и writing response в handlers. Включение этой option отключает такое behavior и разрешает handlers продолжать read from request, одновременно writing response.

Для HTTP/2+ requests Go HTTP server всегда разрешает concurrent reads and responses, поэтому эта option не имеет эффекта.

Thoroughly test с вашими HTTP clients, поскольку некоторые older clients могут не поддерживать full-duplex HTTP/1, что может привести к deadlock. Подробнее см. [golang/go#57786](https://github.com/golang/go/issues/57786).

⚠️ Это experimental feature. Может измениться или быть removed.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

По умолчанию access logs (enabled with directive [`log`](/docs/caddyfile/directives/log)) с headers, содержащими potentially sensitive information (`Cookie`, `Set-Cookie`, `Authorization` и `Proxy-Authorization`), будут logged как `REDACTED`.

Если вы хотите, чтобы эти headers *не* были redacted, включите option `log_credentials`.

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

Space-separated list HTTP protocols для support.

Default: `h1 h2 h3`

Accepted values:
- `h1` для HTTP/1.1
- `h2` для HTTP/2
- `h2c` для HTTP/2 over cleartext
- `h3` для HTTP/3

Сейчас enabling HTTP/2 (including H2C) necessarily implies enabling HTTP/1.1, потому что standard library Go не позволяет disable HTTP/1.1 при использовании HTTP server. Однако HTTP/1.1 или HTTP/3 можно enable independently.

Обратите внимание, что H2C ("Cleartext HTTP/2" или "H2 over TCP") и HTTP/3 не implemented by Go standard library, поэтому некоторые functionality или features могут быть limited. Мы не рекомендуем enabling H2C, если это не absolutely necessary для вашего application.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

Включение этого требует, чтобы header `Host` request совпадал со значением `ServerName`, отправленным TLS ClientHello client, что является necessary safeguard при использовании TLS client authentication. Если есть mismatch, client получает HTTP status `421 Misdirected Request`.

Эта option автоматически включается, если настроена [client authentication](/docs/caddyfile/directives/tls#client_auth). Это disallows TLS client auth bypass (domain fronting), который иначе можно exploit, отправив unprotected SNI value во время TLS handshake, а затем protected domain в Host header после establishing connection. Это behavior является safe default, но можно explicitly turn it off через `insecure_off`; например, при запуске proxy, где domain fronting desired и access не restricted based on hostname.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



<a id="file-systems"></a>
## File Systems

Global option `filesystem` позволяет объявлять одну или несколько file systems, которые можно использовать для file I/O.

Это может позволить подключиться к remote filesystem в cloud, database с file-like interface или даже читать files, embedded внутри binary Caddy.

File systems объявляются с name для identification. Это означает, что можно подключиться к more than one file system of the same type, если нужно.

По умолчанию Caddy не имеет file system modules, поэтому нужно build Caddy с plugin для file system, которую хотите использовать.

<a id="example"></a>
#### Пример

Используя imaginary module file system `custom`, можно объявить две file systems:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



<a id="pki-options"></a>
## PKI Options

App PKI (Public Key Infrastructure) — foundation для features [Local HTTPS](/docs/automatic-https#local-https) и [ACME server](/docs/caddyfile/directives/acme_server) Caddy. App определяет certificate authorities (CAs), которые способны signing certificates.

Default CA ID — `local`. Если ID omitted при configuration `ca`, предполагается `local`.

##### `name`
User-facing name certificate authority.

Default: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
Name, помещаемое в поле CommonName root certificate.

Default: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
Name, помещаемое в поле CommonName intermediate certificates.

Default: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
[Duration](/docs/conventions#durations), в течение которого intermediate certificates valid. Это value **должно** быть less than lifetime root cert (`3600d` или 10 years).

Default: `7d`. Менять это *не рекомендуется*, если нет absolute necessity.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
[Duration](/docs/conventions#durations), как часто проверять, нужно ли renewal intermediate (и root, когда applicable) certificates.

Default: `10m`. Менять это *не рекомендуется*, если нет absolute necessity.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
Ratio (между 0 и 1) lifetime certificate, который должен оставаться перед тем, как Caddy попытается renew certificates. Например, если certificate имеет lifetime 1 year, а ratio `0.2` (default value), Caddy будет continually attempt to renew certificate, когда до expiration останется 73 days или меньше.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
Key pair (certificate и private key), используемая как root для CA. Если не указана, будет generated and managed automatically.

- **format** — format, в котором предоставлены certificate и private key. Сейчас поддерживается только `pem_file`, это default, поэтому field optional.
- **cert** — certificate. При использовании format `pem_file` это должен быть path к PEM file.
- **key** — private key. При использовании format `pem_file` это должен быть path к PEM file.

##### `intermediate`
Key pair (certificate и private key), используемая как intermediate для CA. Если не указана, будет generated and managed automatically.

- **format** — format, в котором предоставлены certificate и private key. Сейчас поддерживается только `pem_file`, это default, поэтому field optional.
- **cert** — certificate. При использовании format `pem_file` это должен быть path к PEM file.
- **key** — private key. При использовании format `pem_file` это должен быть path к PEM file.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


<a id="event-options"></a>
## Event Options

Caddy modules emit events, когда происходят interesting things (или вот-вот произойдут).

Events обычно включают metadata payload. Лучший способ узнать об events и их payloads — documentation каждого module, но можно также увидеть events и их data payloads, включив [global option `debug`](#debug) и прочитав logs.

##### `on`

Связывает event handler с named event. Укажите name event handler module, затем его configuration.

Например, чтобы запустить command после получения certificate (требуется [third-party plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec)), с передачей части event payload в script через placeholder:

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

<a id="events"></a>
### Events

Эти standard events emitted by Caddy:

- [`tls` events <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [`reverse_proxy` events](/docs/caddyfile/directives/reverse_proxy#events)

Plugins также могут emit events, поэтому details смотрите в их documentation.
